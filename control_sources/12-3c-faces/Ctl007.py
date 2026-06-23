"""Ctl007 — Clean planar ADVANCED_FACE (negative control for §12-3c-faces).

A 3x3 square ADVANCED_FACE on the XY plane. Exactly one FACE_OUTER_BOUND,
one EDGE_LOOP with 4 ORIENTED_EDGEs.  PLANE placement is consistent with
the face normal (0,0,1).  same_sense=True.

Expected: occt=shape(1)/shape(1)
"""
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
sys.path.insert(0, str(_HERE.parents[3] / "validation" / "src"))

from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ctl007",
    defect="NEGATIVE CONTROL: clean planar ADVANCED_FACE with one FACE_OUTER_BOUND",
)

p00 = f.cartesian_point((0.0, 0.0, 0.0))
p30 = f.cartesian_point((3.0, 0.0, 0.0))
p33 = f.cartesian_point((3.0, 3.0, 0.0))
p03 = f.cartesian_point((0.0, 3.0, 0.0))

v00 = f.vertex_point(p00)
v30 = f.vertex_point(p30)
v33 = f.vertex_point(p33)
v03 = f.vertex_point(p03)

def ledge(va, vb, p, dvec, length):
    return f.edge_curve(va, vb, f.line(p, f.vector(f.direction(dvec), length)))

e0 = ledge(v00, v30, p00, (1.0, 0.0, 0.0), 3.0)
e1 = ledge(v30, v33, p30, (0.0, 1.0, 0.0), 3.0)
e2 = ledge(v33, v03, p33, (-1.0, 0.0, 0.0), 3.0)
e3 = ledge(v03, v00, p03, (0.0, -1.0, 0.0), 3.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

plc = f.axis2_placement_3d(p00, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
plane = f.plane(plc)
face = f.advanced_face([f.face_outer_bound(loop)], plane, True)

shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
