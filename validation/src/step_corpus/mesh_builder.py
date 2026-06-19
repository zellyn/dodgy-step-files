"""Minimal Python builder for mesh-defect fixtures.

Parallel to ``step_builder.py``: each mesh fixture source lives at
``mesh_sources/<section>/<ID>.py`` and constructs a ``MeshFile`` object
via the convenience methods below. The CLI (``python -m
step_corpus.mesh_builder <source.py>``) runs the source and writes the
corresponding ``mesh-examples/<section>/<ID>.mesh.json``.

The fixture carries the **actual defective geometry** — three triangles
literally sharing an edge for non-manifold, zero-area triangles for
degenerate, distinct-but-sub-tolerance vertex entries for near-
coincident, etc. A healer that reads the file must confront the defect
in the data structure; there's no prose helping it.

The ``metadata.assertions`` list is the mesh equivalent of STEP tier-3
assertions: machine-checkable pointers that confirm the defect is where
the catalog says it is (e.g. ``{edge: [0, 2], shared_by_n_triangles: 3}``
for non-manifold-edge fixtures).

Schema (v0)::

    {
      "vertices": [[x, y, z], ...],
      "triangles": [[i0, i1, i2], ...],
      "metadata": {
        "id": "Me001",
        "schema_version": 0,
        "defect_class": "non_manifold_edge" | "degenerate_triangle"
                      | "near_coincident_vertex" | "hole_in_hull"
                      | "self_intersection" | "inverted_normal"
                      | "duplicate_triangle" | "isolated_vertex",
        "title": "<one-line claim>",
        "assertions": [
          {"kind": "edge_shared_by_n_triangles", "edge": [i0, i1], "n": 3},
          {"kind": "triangle_area_lt", "triangle": idx, "lt": 1e-9},
          {"kind": "vertex_pair_distance_lt", "pair": [i, j], "lt": 1e-7},
          ...
        ]
      }
    }

The schema is intentionally open-ended on the assertion kind — new
mesh defects will pull on new assertion types as needed. v0 is just
the first cut.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import json
import sys
from typing import Any


@dataclass
class MeshFile:
    """In-memory mesh model. Emit to JSON via ``render()``."""
    catalog_id: str
    title: str = ""
    defect_class: str = "unknown"
    schema_version: int = 0
    vertices: list[list[float]] = field(default_factory=list)
    triangles: list[list[int]] = field(default_factory=list)
    assertions: list[dict[str, Any]] = field(default_factory=list)

    # ----- Geometry construction -----

    def vertex(self, x: float, y: float, z: float) -> int:
        """Append a vertex; return its index. No deduplication —
        near-coincident-vertex fixtures rely on distinct entries at
        sub-tolerance positions."""
        self.vertices.append([float(x), float(y), float(z)])
        return len(self.vertices) - 1

    def triangle(self, i0: int, i1: int, i2: int) -> int:
        """Append a triangle by vertex indices; return its index.
        No validation — degenerate (e.g. i0 == i1) and zero-area
        triangles are valid defect demonstrations."""
        self.triangles.append([int(i0), int(i1), int(i2)])
        return len(self.triangles) - 1

    # ----- Assertion shortcuts -----

    def assert_edge_shared(self, i0: int, i1: int, n: int) -> None:
        """Catalog this edge as shared by exactly ``n`` triangles
        (non-manifold when n > 2 or n == 0 on a closed surface).
        Edge is stored with min vertex index first for canonical form."""
        a, b = sorted((int(i0), int(i1)))
        self.assertions.append({
            "kind": "edge_shared_by_n_triangles",
            "edge": [a, b],
            "n": int(n),
        })

    def assert_triangle_area_lt(self, idx: int, lt: float) -> None:
        """Catalog triangle ``idx`` as having area below ``lt``
        (degenerate-triangle defect)."""
        self.assertions.append({
            "kind": "triangle_area_lt",
            "triangle": int(idx),
            "lt": float(lt),
        })

    def assert_vertex_pair_distance_lt(self, i: int, j: int, lt: float) -> None:
        """Catalog vertex pair (i, j) as separated by less than ``lt``
        (near-coincident-vertex defect)."""
        self.assertions.append({
            "kind": "vertex_pair_distance_lt",
            "pair": [int(i), int(j)],
            "lt": float(lt),
        })

    def assert_hole_boundary(self, vertex_loop: list[int]) -> None:
        """Catalog a vertex loop as the boundary of an unfilled hole
        (hole-in-hull defect). Loop is ordered; first == last is
        implicit closure."""
        self.assertions.append({
            "kind": "hole_boundary",
            "loop": [int(v) for v in vertex_loop],
        })

    def assert_triangles_self_intersect(self, ta: int, tb: int) -> None:
        """Catalog triangles ``ta`` and ``tb`` as geometrically
        crossing each other (self-intersection defect)."""
        self.assertions.append({
            "kind": "triangles_self_intersect",
            "triangles": [int(ta), int(tb)],
        })

    def assert_isolated_vertex(self, v: int) -> None:
        """Catalog vertex ``v`` as not referenced by any triangle
        (isolated-vertex defect)."""
        self.assertions.append({
            "kind": "isolated_vertex",
            "vertex": int(v),
        })

    # ----- Serialization -----

    def to_dict(self) -> dict[str, Any]:
        return {
            "vertices": self.vertices,
            "triangles": self.triangles,
            "metadata": {
                "id": self.catalog_id,
                "schema_version": self.schema_version,
                "defect_class": self.defect_class,
                "title": self.title,
                "assertions": self.assertions,
            },
        }

    def render(self) -> str:
        """Render as JSON. Stable key order; 2-space indent for
        readability and diff-friendliness."""
        return json.dumps(self.to_dict(), indent=2, sort_keys=False) + "\n"


# ----- CLI entry point -----

def _run_source(source_path: Path) -> tuple[MeshFile, Path]:
    """Execute a mesh source file and return its MeshFile + output path."""
    import runpy
    ns = runpy.run_path(str(source_path))
    mesh = None
    # Match by class name to survive the python -m __main__ vs
    # step_corpus.mesh_builder dual-class case (isinstance would fail).
    for v in ns.values():
        if type(v).__name__ == "MeshFile" and hasattr(v, "render"):
            mesh = v
            break
    if mesh is None:
        raise SystemExit(f"no MeshFile object in {source_path}")
    # Output path: mesh-examples/<section>/<ID>.mesh.json
    section = source_path.parent.name
    out_dir = source_path.parents[2] / "mesh-examples" / section
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{mesh.catalog_id}.mesh.json"
    return mesh, out_path


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: python -m step_corpus.mesh_builder <source.py> [--write]")
        raise SystemExit(2)
    source = Path(sys.argv[1])
    mesh, out_path = _run_source(source)
    rendered = mesh.render()
    if "--write" in sys.argv:
        out_path.write_text(rendered)
        print(f"wrote {out_path}")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
