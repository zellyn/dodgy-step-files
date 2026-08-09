"""Ctl016 — Clean 9-arg B_SPLINE_CURVE_WITH_KNOTS edge (negative control for §12-2b-nurbs).

A planar square face where one side is carried by a degree-3 B-spline whose
four poles lie exactly on the straight side (a Bezier segment of the line),
with the CORRECT 9-attribute form. The defective siblings of this file
(10-arg curves) crash 96% of the time; the correct arity must load and must
not be flagged by any argument-count checker.

Expected: occt=shape(1)/shape(1)
"""
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
sys.path.insert(0, str(_HERE.parents[3] / "validation" / "src"))

from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ctl016",
    defect="NEGATIVE CONTROL: correct 9-arg B-spline curve edge, no defect",
)

p00 = f.cartesian_point((0.0, 0.0, 0.0))
p20 = f.cartesian_point((2.0, 0.0, 0.0))
p22 = f.cartesian_point((2.0, 2.0, 0.0))
p02 = f.cartesian_point((0.0, 2.0, 0.0))

# Bezier form of the bottom side: poles on the segment (0,0,0)->(2,0,0).
b1 = f.cartesian_point((2.0 / 3.0, 0.0, 0.0))
b2 = f.cartesian_point((4.0 / 3.0, 0.0, 0.0))
bez = f.b_spline_curve_with_knots(3, [p00, b1, b2, p20], [4, 4], [0.0, 1.0])

v00 = f.vertex_point(p00)
v20 = f.vertex_point(p20)
v22 = f.vertex_point(p22)
v02 = f.vertex_point(p02)

def ledge(va, vb, p, dvec):
    return f.edge_curve(va, vb, f.line(p, f.vector(f.direction(dvec), 2.0)))

e0 = f.edge_curve(v00, v20, bez)
e1 = ledge(v20, v22, p20, (0.0, 1.0, 0.0))
e2 = ledge(v22, v02, p22, (-1.0, 0.0, 0.0))
e3 = ledge(v02, v00, p02, (0.0, -1.0, 0.0))

loop = f.edge_loop([f.oriented_edge(e, True) for e in (e0, e1, e2, e3)])
plc = f.axis2_placement_3d(p00, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
face = f.advanced_face([f.face_outer_bound(loop)], f.plane(plc), True)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
