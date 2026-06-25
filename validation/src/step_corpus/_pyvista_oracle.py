"""pyvista oracle: mesh orientation + shape-quality cross-kernel oracle.

Audit #479 (pymeshfix-unchanged sweep) flagged that pymeshfix has no
window into orientation repair or shape-quality (needle / cap)
defects, leaving ~30 mesh fixtures invisible to mesh-layer cross-oracle
diff. pyvista (already a pymeshfix runtime dep) wraps VTK and gives us
both signals cheaply:

- `is_manifold` — boolean property: every edge incident on exactly
  2 faces (or 1 if boundary)
- `compute_normals(auto_orient_normals=True)` — runs VTK's
  vtkPolyDataNormals consistent-orientation pass; we flag fixtures
  where this changes triangle winding
- `cell_quality(quality_measure='aspect_ratio')` — per-triangle aspect
  ratio (longest-edge / shortest-altitude); high values indicate
  needles, low indicate near-equilateral

Output JSON record:
    {
      "kernel": "pyvista",
      "status": "loaded" | "rejected" | "error" | "not_installed",
      "is_manifold": bool | null,
      "n_vertices": int | null,
      "n_triangles": int | null,
      "n_orientation_flipped": int | null,
      "max_aspect_ratio": float | null,
      "stderr_tail": str,
      "duration_ms": float
    }

Install:
    pyvista is already pulled in by pymeshfix; no extra install needed.

Usage:
    uv run python -m step_corpus._pyvista_oracle <fixture.mesh.json> [--json]
    uv run python -m step_corpus._pyvista_oracle --check-install
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path


try:
    import numpy as np
    import pyvista as _PV  # type: ignore
    _PYVISTA_INSTALLED = True
    _PV_VERSION = getattr(_PV, "__version__", "unknown")
except ImportError:
    _PV = None
    _PYVISTA_INSTALLED = False
    _PV_VERSION = None


def check_install() -> dict:
    if not _PYVISTA_INSTALLED:
        return {
            "installed": False,
            "binary": None,
            "version": None,
            "reason": "pyvista not importable; install with `uv pip install pyvista`",
        }
    return {
        "installed": True,
        "binary": "pyvista (Python package, VTK wrapper)",
        "version": _PV_VERSION,
    }


def _empty_result(extra: dict | None = None) -> dict:
    base = {
        "kernel": "pyvista",
        "status": "not_installed",
        "is_manifold": None,
        "n_vertices": None,
        "n_triangles": None,
        "n_orientation_flipped": None,
        "max_aspect_ratio": None,
        "stderr_tail": "",
        "duration_ms": 0.0,
    }
    if extra:
        base.update(extra)
    return base


def _build_polydata(verts: list, tris: list):
    """Convert vertices + triangles to a pyvista PolyData."""
    points = np.asarray(verts, dtype=float)
    # PolyData faces format: flat array (n_pts_per_face, *idx)
    faces_flat = np.zeros((len(tris), 4), dtype=np.int64)
    faces_flat[:, 0] = 3
    faces_flat[:, 1:] = np.asarray(tris, dtype=np.int64)
    return _PV.PolyData(points, faces_flat.flatten())


def run_pyvista(fixture: Path) -> dict:
    if not _PYVISTA_INSTALLED:
        return _empty_result()

    try:
        data = json.loads(fixture.read_text())
    except Exception as e:
        return _empty_result({
            "status": "rejected",
            "stderr_tail": f"could not parse mesh.json: {e}"[-200:],
        })

    verts = data.get("vertices", [])
    tris = data.get("triangles", [])
    if not verts or not tris:
        return _empty_result({
            "status": "rejected",
            "n_vertices": len(verts),
            "n_triangles": len(tris),
            "stderr_tail": "empty vertices or triangles array",
        })

    try:
        t0 = time.perf_counter()
        pd = _build_polydata(verts, tris)
        n_v = pd.n_points
        n_t = pd.n_cells
        try:
            is_manifold = bool(pd.is_manifold)
        except Exception:
            is_manifold = None

        # Auto-orient: counts how many triangles got their winding
        # flipped by VTK's consistent-orientation pass.
        try:
            oriented = pd.compute_normals(
                consistent_normals=True,
                auto_orient_normals=True,
                flip_normals=False,
            )
            # Compare original vs oriented face windings — count mismatches.
            orig_faces = pd.regular_faces  # shape (n_tris, 3)
            new_faces = oriented.regular_faces
            # A flip is detected when the cyclic order changes.
            flips = 0
            for a, b in zip(orig_faces, new_faces):
                # Same set of vertices; different cyclic direction = flip
                if set(a) == set(b) and list(a) != list(b):
                    # Check cyclic equality (a==b rotated)
                    rot = list(a)
                    rotations = [rot, [rot[1], rot[2], rot[0]],
                                 [rot[2], rot[0], rot[1]]]
                    if list(b) not in rotations:
                        flips += 1
            n_flipped = int(flips)
        except Exception:
            n_flipped = None

        # Cell aspect ratio
        try:
            q = pd.cell_quality(quality_measure="aspect_ratio")
            arr = q["CellQuality"]
            max_aspect = float(np.max(arr)) if len(arr) > 0 else None
        except Exception:
            max_aspect = None

        duration_ms = (time.perf_counter() - t0) * 1000.0
        return {
            "kernel": "pyvista",
            "status": "loaded",
            "is_manifold": is_manifold,
            "n_vertices": int(n_v),
            "n_triangles": int(n_t),
            "n_orientation_flipped": n_flipped,
            "max_aspect_ratio": max_aspect,
            "stderr_tail": "",
            "duration_ms": duration_ms,
        }
    except Exception as e:
        return _empty_result({
            "status": "error",
            "n_vertices": len(verts),
            "n_triangles": len(tris),
            "stderr_tail": f"{type(e).__name__}: {e}"[-200:],
        })


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("fixture", nargs="?")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--check-install", action="store_true")
    args = ap.parse_args()

    if args.check_install:
        info = check_install()
        print(json.dumps(info, indent=2) if args.json else info)
        return 0 if info["installed"] else 1

    if not args.fixture:
        ap.error("fixture path required (or use --check-install)")

    fixture = Path(args.fixture)
    if not fixture.is_file():
        print(f"fixture not found: {fixture}", file=sys.stderr)
        return 2

    result = run_pyvista(fixture)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"{result['kernel']}: {result['status']}")
        if result["n_vertices"] is not None:
            print(f"  {result['n_vertices']}v × {result['n_triangles']}t, "
                  f"manifold={result['is_manifold']}, "
                  f"flipped={result['n_orientation_flipped']}, "
                  f"max_aspect={result['max_aspect_ratio']}, "
                  f"{result['duration_ms']:.1f} ms")
        if result["stderr_tail"]:
            print(f"  stderr: {result['stderr_tail']}")
    return 0 if result["status"] in ("loaded", "rejected", "not_installed") else 1


if __name__ == "__main__":
    sys.exit(main())
