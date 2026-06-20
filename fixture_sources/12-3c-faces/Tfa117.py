"""Tfa117 — ShapeAnalysis_CheckSmallFace.CheckSplittingVertices vertex-on-degenerate-edge.

Catalog claim: Face vertex sits on midpoint of degenerate (zero-length) edge
from adjacent face; CheckSplittingVertices fails to classify the T-vertex.
Without degenerate-edge tolerance context, CheckSplittingVertices cannot
identify vertices sitting on zero-length edges as splitting vertices.

Mechanism: OPEN_SHELL with two planar faces sharing a vertex:
  - Face 1: rectangle [0,2]×[0,1] at z=0 with a degenerate (zero-length) edge
    at (1,0,0). The zero-length edge is a T-vertex candidate.
  - Face 2: rectangle [0,2]×[0,1] at z=1 with normal edges through (1,0,1).
    The vertex at (1,0,1) corresponds to the T-vertex location on face 2.

CheckSplittingVertices inspects face 2's normal edges and tries to classify
whether any vertex sits on a midpoint of a degenerate edge from face 1.
Without tolerance context for zero-length edges, the classification fails.

Both faces are on the live OPEN_SHELL traversal path.

Byte assertions:
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: n_faces_total == 2

Expected: occt=shape(1)/shape(1) gmsh=shape(2) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa117",
    defect=(
        "OPEN_SHELL: two planar ADVANCED_FACE entities; "
        "face[0] at z=0 has degenerate zero-length edge at vertex (1,0,0) "
        "breaking the bottom edge of the 2×1 rectangle; "
        "face[1] at z=1 is a normal 2×1 rectangle with vertex at (1,0,1); "
        "ShapeAnalysis_CheckSmallFace::CheckSplittingVertices cannot classify "
        "the T-vertex at (1,0,0) because the zero-length edge has no meaningful "
        "parameter domain for midpoint detection; defect IS on live OPEN_SHELL traversal path"
    ),
)

# Face 1: 2×1 rectangle at z=0 with degenerate zero-length edge at (1,0,0)
# Corners: (0,0,0), (1,0,0), (2,0,0), (2,1,0), (0,1,0)
# The bottom edge is split at (1,0,0) with a zero-length edge at that point

p_f1_00 = f.cartesian_point((0.0, 0.0, 0.0))
p_f1_10 = f.cartesian_point((1.0, 0.0, 0.0))   # T-vertex location
p_f1_10b = f.cartesian_point((1.0, 0.0, 0.0))  # twin for degenerate edge
p_f1_20 = f.cartesian_point((2.0, 0.0, 0.0))
p_f1_21 = f.cartesian_point((2.0, 1.0, 0.0))
p_f1_01 = f.cartesian_point((0.0, 1.0, 0.0))

vf1_00  = f.vertex_point(p_f1_00)
vf1_10  = f.vertex_point(p_f1_10)
vf1_10b = f.vertex_point(p_f1_10b)  # degenerate endpoint
vf1_20  = f.vertex_point(p_f1_20)
vf1_21  = f.vertex_point(p_f1_21)
vf1_01  = f.vertex_point(p_f1_01)

# Degenerate edge: zero-length at (1,0,0)
e_degen = f.edge_curve(
    vf1_10, vf1_10b,
    f.line(p_f1_10, f.vector(f.direction((1.0, 0.0, 0.0)), 0.0))
)

# Normal edges for face 1
ef1_b0  = f.edge_curve(vf1_00,  vf1_10,  f.line(p_f1_00,  f.vector(f.direction((1.0,  0.0, 0.0)), 1.0)))
ef1_b1  = f.edge_curve(vf1_10b, vf1_20,  f.line(p_f1_10b, f.vector(f.direction((1.0,  0.0, 0.0)), 1.0)))
ef1_r   = f.edge_curve(vf1_20,  vf1_21,  f.line(p_f1_20,  f.vector(f.direction((0.0,  1.0, 0.0)), 1.0)))
ef1_t   = f.edge_curve(vf1_21,  vf1_01,  f.line(p_f1_21,  f.vector(f.direction((-1.0, 0.0, 0.0)), 2.0)))
ef1_l   = f.edge_curve(vf1_01,  vf1_00,  f.line(p_f1_01,  f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)))

f1_loop = f.edge_loop([
    f.oriented_edge(ef1_b0,  True),
    f.oriented_edge(e_degen, True),   # THE DEFECT: zero-length T-vertex edge
    f.oriented_edge(ef1_b1,  True),
    f.oriented_edge(ef1_r,   True),
    f.oriented_edge(ef1_t,   True),
    f.oriented_edge(ef1_l,   True),
])
f1_plc  = f.axis2_placement_3d(p_f1_00, f.direction((0.0, 0.0, -1.0)), f.direction((1.0, 0.0, 0.0)))
face1   = f.advanced_face([f.face_outer_bound(f1_loop)], f.plane(f1_plc))

# Face 2: normal 2×1 rectangle at z=1 (no degenerate edges)
p_f2_00 = f.cartesian_point((0.0, 0.0, 1.0))
p_f2_20 = f.cartesian_point((2.0, 0.0, 1.0))
p_f2_21 = f.cartesian_point((2.0, 1.0, 1.0))
p_f2_01 = f.cartesian_point((0.0, 1.0, 1.0))

vf2_00  = f.vertex_point(p_f2_00)
vf2_20  = f.vertex_point(p_f2_20)
vf2_21  = f.vertex_point(p_f2_21)
vf2_01  = f.vertex_point(p_f2_01)

ef2_b   = f.edge_curve(vf2_00, vf2_20, f.line(p_f2_00, f.vector(f.direction((1.0,  0.0, 0.0)), 2.0)))
ef2_r   = f.edge_curve(vf2_20, vf2_21, f.line(p_f2_20, f.vector(f.direction((0.0,  1.0, 0.0)), 1.0)))
ef2_t   = f.edge_curve(vf2_21, vf2_01, f.line(p_f2_21, f.vector(f.direction((-1.0, 0.0, 0.0)), 2.0)))
ef2_l   = f.edge_curve(vf2_01, vf2_00, f.line(p_f2_01, f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)))

f2_loop = f.edge_loop([
    f.oriented_edge(ef2_b, True), f.oriented_edge(ef2_r, True),
    f.oriented_edge(ef2_t, True), f.oriented_edge(ef2_l, True),
])
f2_plc  = f.axis2_placement_3d(p_f2_00, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
face2   = f.advanced_face([f.face_outer_bound(f2_loop)], f.plane(f2_plc))

# OPEN_SHELL: two faces
open_sh = f.open_shell([face1, face2])
sbsm    = f.shell_based_surface_model([open_sh])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa117.stp")
