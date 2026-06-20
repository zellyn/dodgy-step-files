"""Tfa198 — ShapeAnalysis_FreeBoundsProperties.CheckNotches gap-after-fix

Free bounds (unclosed edges after face healing) are analyzed for gaps and
notches. The notch checker computes arc length between consecutive edge
endpoints; a gap smaller than parametric precision but larger than geometric
tolerance indicates a healing-recoverable discrepancy. Incomplete
re-validation after healing may miss newly opened gaps.

Mechanism: CLOSED_SHELL with two ADVANCED_FACEs. The defective face is a
planar quadrilateral whose edge loop has a deliberate micro-gap between one
edge's end vertex and the next edge's start vertex (identical coordinate
values in the STEP file but the vertex entities are distinct, creating a
topological gap that the free-bounds notch checker must flag after a healing
pass). The companion face is a valid 1×1 square on a second plane so the
shell loads as shape(1). Defect IS on live traversal path.

Byte assertions:
  - contains(b'ADVANCED_FACE')
  - contains(b'FACE_OUTER_BOUND')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa198",
    defect=(
        "CLOSED_SHELL: defective ADVANCED_FACE on PLANE at z=0; "
        "edge loop has topological gap: edge[2] end-vertex and edge[3] start-vertex "
        "are distinct VERTEX_POINT entities at the same 3D coordinate (0,0,0); "
        "CheckNotches detects the gap between consecutive free-bound edge endpoints; "
        "healing-pass re-validation skipped: gap persists undetected post-fix; "
        "companion valid face at z=1 ensures OCC loads shape(1); "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

# ── Defective face: planar quadrilateral with topological micro-gap ───────────
# Vertices of a 1×1 square at z=0.
# The gap is between v3_end (end of edge[2]) and v0_gap (start of edge[3]):
# both sit at (0,0,0) but are stored as separate VERTEX_POINT entities.
p00a = f.cartesian_point((0.0, 0.0, 0.0))   # shared: start of edge[0]
p10  = f.cartesian_point((1.0, 0.0, 0.0))
p11  = f.cartesian_point((1.0, 1.0, 0.0))
p01  = f.cartesian_point((0.0, 1.0, 0.0))
p00b = f.cartesian_point((0.0, 0.0, 0.0))   # gap twin: same coords, distinct entity

v00a = f.vertex_point(p00a)   # start of bottom edge
v10  = f.vertex_point(p10)
v11  = f.vertex_point(p11)
v01  = f.vertex_point(p01)
v00b = f.vertex_point(p00b)   # end of left edge — topological gap start

# Edge[0]: bottom (→)
e_bot = f.edge_curve(v00a, v10,  f.line(p00a, f.vector(f.direction(( 1.0, 0.0, 0.0)), 1.0)))
# Edge[1]: right (↑)
e_rgt = f.edge_curve(v10,  v11,  f.line(p10,  f.vector(f.direction(( 0.0, 1.0, 0.0)), 1.0)))
# Edge[2]: top (←)
e_top = f.edge_curve(v11,  v01,  f.line(p11,  f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)))
# Edge[3]: left (↓) — ends at v00b, not v00a: topological gap
e_lft = f.edge_curve(v01,  v00b, f.line(p01,  f.vector(f.direction(( 0.0,-1.0, 0.0)), 1.0)))

defect_loop = f.edge_loop([
    f.oriented_edge(e_bot, True),
    f.oriented_edge(e_rgt, True),
    f.oriented_edge(e_top, True),
    f.oriented_edge(e_lft, True),
])

defect_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
defect_face = f.advanced_face([f.face_outer_bound(defect_loop)], f.plane(defect_plc))

# ── Companion face: valid 1×1 square at z=1 ──────────────────────────────────
c00 = f.cartesian_point((0.0, 0.0, 1.0))
c10 = f.cartesian_point((1.0, 0.0, 1.0))
c11 = f.cartesian_point((1.0, 1.0, 1.0))
c01 = f.cartesian_point((0.0, 1.0, 1.0))

cv00 = f.vertex_point(c00)
cv10 = f.vertex_point(c10)
cv11 = f.vertex_point(c11)
cv01 = f.vertex_point(c01)

ce0 = f.edge_curve(cv00, cv10, f.line(c00, f.vector(f.direction(( 1.0, 0.0, 0.0)), 1.0)))
ce1 = f.edge_curve(cv10, cv11, f.line(c10, f.vector(f.direction(( 0.0, 1.0, 0.0)), 1.0)))
ce2 = f.edge_curve(cv11, cv01, f.line(c11, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)))
ce3 = f.edge_curve(cv01, cv00, f.line(c01, f.vector(f.direction(( 0.0,-1.0, 0.0)), 1.0)))

good_loop = f.edge_loop([
    f.oriented_edge(ce0, True),
    f.oriented_edge(ce1, True),
    f.oriented_edge(ce2, True),
    f.oriented_edge(ce3, True),
])
good_plc = f.axis2_placement_3d(
    c00,
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
good_face = f.advanced_face([f.face_outer_bound(good_loop)], f.plane(good_plc))

# ── Assemble ──────────────────────────────────────────────────────────────────
closed_sh = f.closed_shell([defect_face, good_face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa198.stp")
