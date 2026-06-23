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

    def assert_triangles_do_not_intersect(self, ta: int, tb: int) -> None:
        """Catalog triangles ``ta`` and ``tb`` as geometrically
        non-intersecting — the MeshFix ``intersects`` predicate should
        return false for this pair. Covers branches that fast-reject:
        full vertex coincidence (Branch 2), shared edge (Branches 3–5),
        shared single vertex with no edge crossing (Branch 6), bounding-box
        separation (Branches 7–12), and orientation separation (Branches 13–14).
        """
        self.assertions.append({
            "kind": "triangles_do_not_intersect",
            "triangles": [int(ta), int(tb)],
        })

    def assert_isolated_vertex(self, v: int) -> None:
        """Catalog vertex ``v`` as not referenced by any triangle
        (isolated-vertex defect)."""
        self.assertions.append({
            "kind": "isolated_vertex",
            "vertex": int(v),
        })

    def assert_duplicate_triangle_pair(self, ta: int, tb: int) -> None:
        """Catalog triangles ``ta`` and ``tb`` as having identical
        vertex-index sets (duplicate-triangle defect). The oracle compares
        sorted vertex triples so rotation/reflection are also caught."""
        self.assertions.append({
            "kind": "duplicate_triangle_pair",
            "triangles": [int(ta), int(tb)],
        })

    def assert_duplicate_polygon_group(self, triangles: list[int], n: int) -> None:
        """Catalog ``n`` triangles in ``triangles`` as all sharing an identical
        canonical vertex-index set (merge_duplicate_polygons group defect).
        The oracle checks that len(triangles)==n and that every triangle in
        the group maps to the same sorted triple.

        Source: CGAL PMP.merge_duplicate_polygons_in_polygon_soup —
        *duplicate_collection* branch (line 971)."""
        self.assertions.append({
            "kind": "duplicate_polygon_group",
            "triangles": [int(t) for t in triangles],
            "n": int(n),
        })

    def assert_reversed_polygon_pair(self, ta: int, tb: int) -> None:
        """Catalog triangles ``ta`` and ``tb`` as having identical vertex-index
        sets but in *opposite* winding order (orientation-reversed duplicate).
        The oracle checks that sorted(t_a) == sorted(t_b) but the raw triples
        have opposite handedness.

        Source: CGAL PMP.merge_duplicate_polygons_in_polygon_soup —
        *orientation_requirement* branch (line 955)."""
        self.assertions.append({
            "kind": "reversed_polygon_pair",
            "triangles": [int(ta), int(tb)],
        })

    def assert_triangle_normal_z_negative(self, idx: int) -> None:
        """Catalog triangle ``idx`` as having a normal whose Z component is
        negative — evidence of CW (inward) winding for faces in the XY plane
        (inverted-normals defect)."""
        self.assertions.append({
            "kind": "triangle_normal_z_negative",
            "triangle": int(idx),
        })

    def assert_vertex_on_edge(self, v: int, a: int, b: int) -> None:
        """Catalog vertex ``v`` as lying exactly on the line segment between
        vertices ``a`` and ``b`` (T-junction defect). The oracle checks that
        the cross product (v-a)×(b-a) is zero and v is between a and b."""
        self.assertions.append({
            "kind": "vertex_on_edge",
            "vertex": int(v),
            "edge": [int(a), int(b)],
        })

    def assert_triangle_aspect_ratio_gt(self, idx: int, gt: float) -> None:
        """Catalog triangle ``idx`` as having aspect ratio (longest edge /
        shortest altitude) greater than ``gt`` (needle/sliver defect)."""
        self.assertions.append({
            "kind": "triangle_aspect_ratio_gt",
            "triangle": int(idx),
            "gt": float(gt),
        })

    def assert_vertex_fan_disconnected(self, v: int) -> None:
        """Catalog vertex ``v`` as having a disconnected triangle fan —
        i.e. the triangles incident on ``v`` form two or more groups with
        no shared edge between groups (non-manifold-vertex / bowtie defect)."""
        self.assertions.append({
            "kind": "vertex_fan_disconnected",
            "vertex": int(v),
        })

    def assert_adjacent_triangles_inconsistent_winding(self, ta: int, tb: int) -> None:
        """Catalog triangles ``ta`` and ``tb`` as sharing an edge but having
        antiparallel normals (inconsistent-face-orientation defect). The
        oracle computes both normals and checks that their dot product is
        negative."""
        self.assertions.append({
            "kind": "adjacent_triangles_inconsistent_winding",
            "triangles": [int(ta), int(tb)],
        })

    def assert_triangle_not_reachable_from(self, target: int, source: int) -> None:
        """Catalog triangle ``target`` as unreachable from ``source`` by
        walking shared edges (disconnected-component defect). The oracle does
        a BFS/DFS from ``source`` and verifies ``target`` is never visited."""
        self.assertions.append({
            "kind": "triangle_not_reachable_from",
            "target": int(target),
            "source": int(source),
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

    def render_obj(self) -> str:
        """Render as Wavefront OBJ (interop). Defect metadata is lost;
        consumers without our JSON format can still load the geometry.

        Degenerate triangles (e.g. `f a b a`) and triangles indexing
        near-coincident-but-distinct vertices are preserved verbatim —
        OBJ doesn't dedupe vertices for us. Self-intersection and
        non-manifold-edge are present in the raw triangle list."""
        lines = [f"# {self.catalog_id}: {self.title}",
                 f"# defect_class: {self.defect_class}"]
        for x, y, z in self.vertices:
            lines.append(f"v {x:.12g} {y:.12g} {z:.12g}")
        # OBJ uses 1-based vertex indices.
        for i0, i1, i2 in self.triangles:
            lines.append(f"f {i0 + 1} {i1 + 1} {i2 + 1}")
        return "\n".join(lines) + "\n"

    def render_ply(self) -> str:
        """Render as ASCII PLY (interop). Same caveat as OBJ — defect
        metadata isn't preserved, but the actual defective geometry is."""
        header = [
            "ply",
            "format ascii 1.0",
            f"comment {self.catalog_id}: {self.title}",
            f"comment defect_class: {self.defect_class}",
            f"element vertex {len(self.vertices)}",
            "property float x",
            "property float y",
            "property float z",
            f"element face {len(self.triangles)}",
            "property list uchar int vertex_indices",
            "end_header",
        ]
        body = []
        for x, y, z in self.vertices:
            body.append(f"{x:.12g} {y:.12g} {z:.12g}")
        for i0, i1, i2 in self.triangles:
            body.append(f"3 {i0} {i1} {i2}")
        return "\n".join(header + body) + "\n"


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
        print("                                                      [--co-emit]")
        print("  --write    write <id>.mesh.json to mesh-examples/<section>/")
        print("  --co-emit  also write <id>.obj and <id>.ply (interop formats)")
        raise SystemExit(2)
    source = Path(sys.argv[1])
    mesh, out_path = _run_source(source)
    rendered = mesh.render()
    if "--write" in sys.argv:
        out_path.write_text(rendered)
        print(f"wrote {out_path}")
        if "--co-emit" in sys.argv:
            obj_path = out_path.with_suffix("").with_suffix(".obj")
            ply_path = out_path.with_suffix("").with_suffix(".ply")
            obj_path.write_text(mesh.render_obj())
            ply_path.write_text(mesh.render_ply())
            print(f"wrote {obj_path}")
            print(f"wrote {ply_path}")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
