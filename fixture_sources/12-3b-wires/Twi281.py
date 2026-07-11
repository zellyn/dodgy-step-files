"""Twi281 — `VERTEX_LOOP` point-loop used as the SOLE `FACE_OUTER_BOUND` of an
`ADVANCED_FACE` on a non-singular `PLANE` (loop-degeneracy flag vs flat geometry).

Catalog claim (input pattern): a face's outer boundary is expressed as a
`FACE_OUTER_BOUND` wrapping a `VERTEX_LOOP` — a loop that collapses to a single
`VERTEX_POINT`. In openNURBS's validity ontology (`ON_BrepLoop` type
`ptonsrf` / singular loop) a point-loop is only valid where the underlying
surface has a genuine singularity (cone apex / sphere pole). Here the surface is
a flat `PLANE`, which has NO singular point anywhere, so the loop's
"this-face-is-a-single-point" degeneracy flag contradicts the flat geometry.

Distinct from:
  - Twi041 / Pf025 — `VERTEX_LOOP` as an INNER `FACE_BOUND` alongside a real
    outer bound (here it is the SOLE / OUTER bound).
  - Tfe writer-drop cluster (sphere cap `VERTEX_LOOP`) — that is a SPHERE, which
    HAS pole singularities; a PLANE does not.

Reproducer recipe: `PLANE` + `VERTEX_POINT` at (0,0,0) + `VERTEX_LOOP` +
`FACE_OUTER_BOUND` + `ADVANCED_FACE` on the plane, wrapped in an
`OPEN_SHELL` / `SHELL_BASED_SURFACE_MODEL` so the face is transferred.

Live oracle (accept-live-oracle): OCCT builds a face on the plane bounded only
by the degenerate vertex loop — `shape(1)` with n_edges_total==0,
n_vertices_total==0 (a clean quad face has 4 edges) and an empty mesh; gmsh
yields `shape(1)` (a clean planar quad meshes to `shape(9)`).

Byte assertions:
  - contains(b'VERTEX_LOOP(')
  - contains(b'point_loop_on_flat_plane')
  - contains(b'PLANE(')

Tier-3 assertions: shape_null == False; n_faces_total == 1;
  n_edges_total == 0; n_vertices_total == 0; face[0].surface_type == "plane"

Expected: occt=shape(1)/shape(1) gmsh=shape(1) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi281",
    defect=(
        "VERTEX_LOOP 'point_loop_on_flat_plane' wrapping a single VERTEX_POINT at "
        "(0,0,0) used as the SOLE FACE_OUTER_BOUND of an ADVANCED_FACE on a flat PLANE; "
        "a point-loop (openNURBS ON_BrepLoop ptonsrf / singular loop type) is only valid "
        "at a genuine surface singularity (cone apex / sphere pole) — a PLANE has none; "
        "loop-degeneracy flag contradicts the flat surface geometry; "
        "face IS transferred via SHELL_BASED_SURFACE_MODEL — no orphaned entities"
    ),
)

# ── PLANE at origin, +Z normal (non-singular surface) ────────────────────────
p_orig = f.cartesian_point((0.0, 0.0, 0.0))
p_zdir = f.direction((0.0, 0.0, 1.0))
p_xdir = f.direction((1.0, 0.0, 0.0))
p_plc  = f.axis2_placement_3d(p_orig, p_zdir, p_xdir)
plane  = f.plane(p_plc)

# ── VERTEX_LOOP: a point-loop collapsing to one VERTEX_POINT ──────────────────
v_pt   = f.cartesian_point((0.0, 0.0, 0.0))
v      = f.vertex_point(v_pt)
vloop  = f._emit_raw(f"VERTEX_LOOP('point_loop_on_flat_plane',#{v.eid})")

# ── FACE_OUTER_BOUND wrapping the point-loop is the face's SOLE boundary ──────
fob    = f._emit_raw(f"FACE_OUTER_BOUND('',#{vloop.eid},.T.)")
face   = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{plane.eid},.T.)")
shell  = f._emit_raw(f"OPEN_SHELL('',(#{face.eid}))")
sbsm   = f._emit_raw(f"SHELL_BASED_SURFACE_MODEL('',(#{shell.eid}))")

f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi281.stp")
