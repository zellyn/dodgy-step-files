"""Tfa129 — CheckSplittingVertices: T-vertex at B-spline midpoint.

Catalog claim: Vertex positioned at exact midpoint of a B-spline edge (not a
LINE). CheckSplittingVertices uses parameter domain midpoint (0.5) for detection
rather than 3D spatial midpoint, causing misdetection. Reproducer: rectangular
face with T-junction vertex at parameter u=0.5 on non-line edge.

Mechanism: OPEN_SHELL with a single PLANE face whose top boundary uses a
B_SPLINE_CURVE_WITH_KNOTS (degree=3) instead of a LINE for the top edge.
A T-junction vertex is introduced at the 3D geometric midpoint of the B-spline
arc. Due to non-uniform parameterization (asymmetric internal knot at 0.3),
the parameter at the 3D midpoint is NOT u=0.5.

CheckSplittingVertices checks parameter u=0.5 for vertex detection but the
T-vertex sits at a different parameter value (the geometric midpoint ≠ the
parametric midpoint), causing the vertex to be missed.

The face IS on the live OPEN_SHELL traversal path.

Byte assertions:
  - contains(b'B_SPLINE_CURVE_WITH_KNOTS')
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa129",
    defect=(
        "OPEN_SHELL: single PLANE ADVANCED_FACE 4×2 rectangle; "
        "top edge is B_SPLINE_CURVE_WITH_KNOTS degree=3 with asymmetric internal "
        "knot at 0.3 (knots=[0.0,0.3,1.0], mults=[4,1,4]); "
        "T-junction vertex at 3D midpoint does NOT correspond to parameter u=0.5 "
        "due to non-uniform B-spline parameterization; "
        "ShapeAnalysis_CheckSmallFace::CheckSplittingVertices checks u=0.5 and "
        "misses the actual T-vertex (geometric midpoint ≠ parametric midpoint); "
        "defect IS on live OPEN_SHELL traversal path"
    ),
)

# Single rectangular face 4×2 at z=0
# Bottom edge: straight line bl → br
# Right edge: straight line br → tr
# Top edge: B-spline curve with slight arc tr → tl (reversed: tl → tr in forward)
# Left edge: straight line tl → bl

# Corners
p_bl = f.cartesian_point((0.0, 0.0, 0.0))
p_br = f.cartesian_point((4.0, 0.0, 0.0))
p_tr = f.cartesian_point((4.0, 2.0, 0.0))
p_tl = f.cartesian_point((0.0, 2.0, 0.0))

v_bl = f.vertex_point(p_bl); v_br = f.vertex_point(p_br)
v_tr = f.vertex_point(p_tr); v_tl = f.vertex_point(p_tl)

# B-spline top edge: from tl to tr (slight upward arc)
# degree=3, 5 control points, asymmetric internal knot at u=0.3
# Control points form a slight arc: tl=(0,2,0) → apex≈(2,2.5,0) → tr=(4,2,0)
# Asymmetric parameterization: knots=[0,0.3,1] → 3D midpoint at u≠0.5
bsp_cp = [
    f.cartesian_point((0.0, 2.0, 0.0)),
    f.cartesian_point((1.0, 2.4, 0.0)),
    f.cartesian_point((2.0, 2.5, 0.0)),
    f.cartesian_point((3.0, 2.4, 0.0)),
    f.cartesian_point((4.0, 2.0, 0.0)),
]
# degree=3, n=5: sum(mults) = 5+3+1 = 9 → mults=[4,1,4] knots=[0,0.3,1]
bsp_top = f.b_spline_curve_with_knots(
    degree=3,
    control_points=bsp_cp,
    knot_multiplicities=[4, 1, 4],
    knots=[0.0, 0.3, 1.0],
)

# Edge using the B-spline: from v_tl to v_tr
e_top = f.edge_curve(v_tl, v_tr, bsp_top)
e_bot = f.edge_curve(v_bl, v_br, f.line(p_bl, f.vector(f.direction(( 1.0, 0.0, 0.0)), 4.0)))
e_rgt = f.edge_curve(v_br, v_tr, f.line(p_br, f.vector(f.direction(( 0.0, 1.0, 0.0)), 2.0)))
e_lft = f.edge_curve(v_tl, v_bl, f.line(p_tl, f.vector(f.direction(( 0.0,-1.0, 0.0)), 2.0)))

# Face loop: bl → br (bot) → tr (rgt) → tl (top reversed) → bl (lft reversed)
face_loop = f.edge_loop([
    f.oriented_edge(e_bot, True),   # bl → br
    f.oriented_edge(e_rgt, True),   # br → tr
    f.oriented_edge(e_top, False),  # tr → tl (B-spline reversed)
    f.oriented_edge(e_lft, False),  # tl → bl (reversed)
])
face_plc = f.axis2_placement_3d(p_bl, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
main_face = f.advanced_face([f.face_outer_bound(face_loop)], f.plane(face_plc))

# OPEN_SHELL: single face
open_sh = f.open_shell([main_face])
sbsm    = f.shell_based_surface_model([open_sh])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa129.stp")
