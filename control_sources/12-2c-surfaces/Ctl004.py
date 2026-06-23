"""Ctl004 — Clean B-spline (NURBS) surface patch (negative control for §12-2c-surfaces).

A flat 2x2 bilinear B-spline surface of degree 1x1 with 4 control points
(2x2 grid) and unit weights — equivalent to a planar patch.  All NURBS
invariants are satisfied: knot-mult sums match, weights positive.

Expected: occt=shape(1)/shape(1)
"""
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
sys.path.insert(0, str(_HERE.parents[3] / "validation" / "src"))

from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ctl004",
    defect="NEGATIVE CONTROL: clean B-spline surface patch, no NURBS defect",
)

# Control point grid: 2x2, flat in XY at z=0
# Row 0: y=0; Row 1: y=2
cp = [
    [f.cartesian_point((0.0, 0.0, 0.0)), f.cartesian_point((2.0, 0.0, 0.0))],
    [f.cartesian_point((0.0, 2.0, 0.0)), f.cartesian_point((2.0, 2.0, 0.0))],
]

# Degree-1 in both directions, 2 control pts → knot mults [2,2], knots [0,1]
surf = f.rational_b_spline_surface_with_knots(
    u_degree=1, v_degree=1,
    control_points_grid=cp,
    weights_grid=[[1.0, 1.0], [1.0, 1.0]],
    u_multiplicities=[2, 2],
    v_multiplicities=[2, 2],
    u_knots=[0.0, 1.0],
    v_knots=[0.0, 1.0],
    surface_form="UNSPECIFIED",
    name="clean_bspline_patch",
)

# Wire a boundary loop around the perimeter
p00 = f.cartesian_point((0.0, 0.0, 0.0))
p20 = f.cartesian_point((2.0, 0.0, 0.0))
p22 = f.cartesian_point((2.0, 2.0, 0.0))
p02 = f.cartesian_point((0.0, 2.0, 0.0))

v00 = f.vertex_point(p00)
v20 = f.vertex_point(p20)
v22 = f.vertex_point(p22)
v02 = f.vertex_point(p02)

def ledge(va, vb, p, dvec, length):
    return f.edge_curve(va, vb, f.line(p, f.vector(f.direction(dvec), length)))

e0 = ledge(v00, v20, p00, (1.0, 0.0, 0.0), 2.0)
e1 = ledge(v20, v22, p20, (0.0, 1.0, 0.0), 2.0)
e2 = ledge(v22, v02, p22, (-1.0, 0.0, 0.0), 2.0)
e3 = ledge(v02, v00, p02, (0.0, -1.0, 0.0), 2.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

face = f.advanced_face([f.face_outer_bound(loop)], surf, True)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
