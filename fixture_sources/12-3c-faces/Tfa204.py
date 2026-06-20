"""Tfa204 — FixLoopWire closed topology reordering

Planar square face with properly closed edge loop (v4->v1 closure). Tests
closed-wire reordering branch via FixReorder vs open-wire appending path.

Mechanism: CLOSED_SHELL with ONE ADVANCED_FACE on a PLANE. The face boundary is
a square loop where the final edge explicitly closes back to the starting vertex
(v4->v1). This closed-topology loop triggers the FixReorder dispatch branch at
OCCT ShapeFix_Face line 2534 rather than the open-wire appending path. The
closure vertex v4->v1 is the same entity as the start vertex, making the wire
topologically closed from the STEP reader's perspective. FixLoopWire must
choose FixReorder (not append) for closed wires; the defect is the ambiguous
closed/open dispatch in the presence of a properly-closed seam edge.

Byte assertions:
  - contains(b'ADVANCED_FACE')
  - contains(b'FACE_OUTER_BOUND')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa204",
    defect=(
        "CLOSED_SHELL: single ADVANCED_FACE on PLANE; "
        "outer boundary: 1×1 square loop where last edge closes v4->v1 "
        "(same vertex entity as loop start — topologically closed); "
        "FixLoopWire line 2534: closed-wire dispatch to FixReorder; "
        "defect: ambiguous closed/open dispatch — closed wires must use "
        "FixReorder branch, not open-wire edge-appending path; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

# ── PLANE surface at origin, normal +Z ───────────────────────────────────────
plane = f.plane(f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
))

# ── Square vertices (CCW) ────────────────────────────────────────────────────
p_ll = f.cartesian_point((0.0, 0.0, 0.0))
p_lr = f.cartesian_point((1.0, 0.0, 0.0))
p_ur = f.cartesian_point((1.0, 1.0, 0.0))
p_ul = f.cartesian_point((0.0, 1.0, 0.0))

v_ll = f.vertex_point(p_ll)
v_lr = f.vertex_point(p_lr)
v_ur = f.vertex_point(p_ur)
v_ul = f.vertex_point(p_ul)

# ── Edges: final edge closes v_ul -> v_ll (same entity as start) ─────────────
e_bot = f.edge_curve(v_ll, v_lr, f.line(p_ll, f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)))
e_rgt = f.edge_curve(v_lr, v_ur, f.line(p_lr, f.vector(f.direction((0.0, 1.0, 0.0)), 1.0)))
e_top = f.edge_curve(v_ur, v_ul, f.line(p_ur, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)))
# Closing edge: v_ul -> v_ll — v_ll is the same vertex entity as the loop start
e_lft = f.edge_curve(v_ul, v_ll, f.line(p_ul, f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)))

face_loop = f.edge_loop([
    f.oriented_edge(e_bot, True),
    f.oriented_edge(e_rgt, True),
    f.oriented_edge(e_top, True),
    f.oriented_edge(e_lft, True),   # closes back to v_ll
])
face = f.advanced_face([f.face_outer_bound(face_loop)], plane)

closed_sh = f.closed_shell([face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa204.stp")
