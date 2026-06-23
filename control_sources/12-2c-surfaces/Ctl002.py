"""Ctl002 — Clean planar ADVANCED_FACE (negative control for §12-2c-surfaces).

A single 2x2 square ADVANCED_FACE on the XY plane.  No surface defects:
the PLANE placement is consistent with the face normal, same_sense=True,
one FACE_OUTER_BOUND, four edges forming a valid closed loop.

Expected: occt=shape(1)/shape(1)
"""
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
sys.path.insert(0, str(_HERE.parents[3] / "validation" / "src"))

from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ctl002",
    defect="NEGATIVE CONTROL: clean planar ADVANCED_FACE, no surface defect",
)

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

plc = f.axis2_placement_3d(p00, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
face = f.advanced_face([f.face_outer_bound(loop)], f.plane(plc), True)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
