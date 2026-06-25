"""pymeshfix oracle: cross-kernel mesh validation via the MeshFix C++ port.

pymeshfix wraps the MeshFix algorithm — a C++ mesh repair toolkit by
Marco Attene — and is install-optional via `pip install pymeshfix`.

Unlike _brlcad_oracle / _solvespace_oracle which wrap binaries via
subprocess, pymeshfix is a Python package, so the install check is
`try: import pymeshfix` rather than `which pymeshfix`. The oracle
reads `.mesh.json` files directly (vertices + triangles arrays) and
runs the standard repair pipeline, reporting the count delta and
the number of boundary loops detected.

Usage:
    uv run python -m step_corpus._pymeshfix_oracle <fixture.mesh.json> [--json]
    uv run python -m step_corpus._pymeshfix_oracle --check-install

When pymeshfix isn't installed, every call returns
`{status: "not_installed", ...}` so the corpus continues to validate
cleanly without it.

Install:
    uv pip install pymeshfix    # MIT license, ~1.3 MiB wheel, pure pip

Output JSON record (matches cross-kernel schema):
    {
      "kernel": "pymeshfix",
      "status": "loaded" | "rejected" | "error" | "not_installed",
      "n_vertices_in": int | null,
      "n_triangles_in": int | null,
      "n_vertices_out": int | null,
      "n_triangles_out": int | null,
      "n_boundaries": int | null,
      "stderr_tail": str,
      "duration_ms": float
    }
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path


try:
    import pymeshfix as _PMF  # type: ignore
    _PYMESHFIX_INSTALLED = True
    _PMF_VERSION = getattr(_PMF, "__version__", "unknown")
except ImportError:
    _PMF = None
    _PYMESHFIX_INSTALLED = False
    _PMF_VERSION = None


def check_install() -> dict:
    """Probe whether pymeshfix is importable."""
    if not _PYMESHFIX_INSTALLED:
        return {
            "installed": False,
            "binary": None,
            "version": None,
            "reason": "pymeshfix not importable; install with `uv pip install pymeshfix`",
        }
    return {
        "installed": True,
        "binary": "pymeshfix (Python package)",
        "version": _PMF_VERSION,
    }


def _empty_result(extra: dict | None = None) -> dict:
    base = {
        "kernel": "pymeshfix",
        "status": "not_installed",
        "n_vertices_in": None,
        "n_triangles_in": None,
        "n_vertices_out": None,
        "n_triangles_out": None,
        "n_boundaries": None,
        "stderr_tail": "",
        "duration_ms": 0.0,
    }
    if extra:
        base.update(extra)
    return base


def run_pymeshfix(fixture: Path) -> dict:
    """Run pymeshfix on a .mesh.json fixture and classify the outcome."""
    if not _PYMESHFIX_INSTALLED:
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
    n_v_in = len(verts)
    n_t_in = len(tris)

    if n_v_in == 0 or n_t_in == 0:
        return _empty_result({
            "status": "rejected",
            "n_vertices_in": n_v_in,
            "n_triangles_in": n_t_in,
            "stderr_tail": "empty vertices or triangles array",
        })

    try:
        import numpy as np
        t0 = time.perf_counter()
        v_arr = np.asarray(verts, dtype=float)
        f_arr = np.asarray(tris, dtype=np.int32)
        mfix = _PMF.MeshFix(v_arr, f_arr)
        # n_boundaries is a property on the pre-repair mesh; capture before
        # repair() mutates the geometry.
        try:
            n_boundaries = int(mfix.n_boundaries)
        except Exception:
            n_boundaries = None
        mfix.repair()
        duration_ms = (time.perf_counter() - t0) * 1000.0
        # After repair, mfix.points / mfix.faces are numpy arrays.
        n_v_out = int(len(mfix.points))
        n_t_out = int(len(mfix.faces))
        return {
            "kernel": "pymeshfix",
            "status": "loaded",
            "n_vertices_in": n_v_in,
            "n_triangles_in": n_t_in,
            "n_vertices_out": n_v_out,
            "n_triangles_out": n_t_out,
            "n_boundaries": n_boundaries,
            "stderr_tail": "",
            "duration_ms": duration_ms,
        }
    except Exception as e:
        return _empty_result({
            "status": "error",
            "n_vertices_in": n_v_in,
            "n_triangles_in": n_t_in,
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

    result = run_pymeshfix(fixture)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"{result['kernel']}: {result['status']}")
        if result["n_vertices_in"] is not None:
            print(f"  in: {result['n_vertices_in']} verts × {result['n_triangles_in']} tris")
        if result["n_vertices_out"] is not None:
            print(f"  out: {result['n_vertices_out']} verts × {result['n_triangles_out']} tris (boundaries={result['n_boundaries']}, {result['duration_ms']:.1f} ms)")
        if result["stderr_tail"]:
            print(f"  stderr: {result['stderr_tail']}")
    return 0 if result["status"] in ("loaded", "rejected", "not_installed") else 1


if __name__ == "__main__":
    sys.exit(main())
