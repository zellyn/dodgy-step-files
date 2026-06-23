"""Ctl008 — Clean fixture with valid tolerance (negative control for §12-4-tolerance).

A 1x1 planar face with a properly-ordered uncertainty:
  UNCERTAINTY_MEASURE_WITH_UNIT = 1.0E-7 (standard STEP precision)
This is the normal, valid case — no inverted hierarchy.

Expected: occt=shape(1)/shape(1)
"""
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
sys.path.insert(0, str(_HERE.parents[3] / "validation" / "src"))

from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ctl008",
    defect="NEGATIVE CONTROL: clean tolerance 1.0E-7, no hierarchy inversion",
)

p00 = f.cartesian_point((0.0, 0.0, 0.0))
p10 = f.cartesian_point((1.0, 0.0, 0.0))
p11 = f.cartesian_point((1.0, 1.0, 0.0))
p01 = f.cartesian_point((0.0, 1.0, 0.0))

v00 = f.vertex_point(p00)
v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11)
v01 = f.vertex_point(p01)

def ledge(va, vb, p, dvec, length):
    return f.edge_curve(va, vb, f.line(p, f.vector(f.direction(dvec), length)))

e0 = ledge(v00, v10, p00, (1.0, 0.0, 0.0), 1.0)
e1 = ledge(v10, v11, p10, (0.0, 1.0, 0.0), 1.0)
e2 = ledge(v11, v01, p11, (-1.0, 0.0, 0.0), 1.0)
e3 = ledge(v01, v00, p01, (0.0, -1.0, 0.0), 1.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

plc = f.axis2_placement_3d(p00, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
face = f.advanced_face([f.face_outer_bound(loop)], f.plane(plc))
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
# Use the default uncertainty 1.0E-7 (standard, valid)
f.add_product_chain(sbsm, uncertainty=1.0e-7)
