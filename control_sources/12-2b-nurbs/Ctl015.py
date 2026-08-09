"""Ctl015 — Clean B_SPLINE_SURFACE_WITH_KNOTS face (negative control for §12-2b-nurbs).

A bilinear B-spline patch (degree 1x1, 2x2 control net) with the CORRECT
13-attribute form, bounded by four line edges. This is the positive-control
geometry that isolated crash site B: the correct arity LOADS, so any
argument-count or slot-type checker must report nothing here.

Expected: occt=shape(1)/shape(1)
"""
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
sys.path.insert(0, str(_HERE.parents[3] / "validation" / "src"))

from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ctl015",
    defect="NEGATIVE CONTROL: correct 13-arg B-spline surface, no defect",
)

p00 = f.cartesian_point((0.0, 0.0, 0.0))
p10 = f.cartesian_point((10.0, 0.0, 0.0))
p01 = f.cartesian_point((0.0, 10.0, 0.0))
p11 = f.cartesian_point((10.0, 10.0, 0.0))

surf = f.b_spline_surface_with_knots(
    1, 1, [[p00, p10], [p01, p11]],
    [2, 2], [2, 2], [0.0, 1.0], [0.0, 1.0],
)

v00 = f.vertex_point(p00)
v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11)
v01 = f.vertex_point(p01)

def ledge(va, vb, p, dvec):
    return f.edge_curve(va, vb, f.line(p, f.vector(f.direction(dvec), 10.0)))

e0 = ledge(v00, v10, p00, (1.0, 0.0, 0.0))
e1 = ledge(v10, v11, p10, (0.0, 1.0, 0.0))
e2 = ledge(v11, v01, p11, (-1.0, 0.0, 0.0))
e3 = ledge(v01, v00, p01, (0.0, -1.0, 0.0))

loop = f.edge_loop([f.oriented_edge(e, True) for e in (e0, e1, e2, e3)])
face = f.advanced_face([f.face_outer_bound(loop)], surf, True)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
