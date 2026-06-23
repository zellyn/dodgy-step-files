"""Ctl009 — Clean MILLIMETRE-context fixture (negative control for §12-5-units).

A 10x10 mm square face with SI_UNIT(.MILLI.,.METRE.) in the
GLOBAL_UNIT_ASSIGNED_CONTEXT. The coordinates are in millimetres.
No unit ambiguity — this is the intended clean case where a reader
that correctly honours the MILLI prefix will see a 10mm x 10mm part.

Expected: occt=shape(1)/shape(1)
"""
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
sys.path.insert(0, str(_HERE.parents[3] / "validation" / "src"))

from step_corpus.step_builder import StepFile

# The step_builder's add_product_chain already emits SI_UNIT(.MILLI.,.METRE.)
# in its unit block, so we get a clean millimetre context for free.
f = StepFile(
    catalog_id="Ctl009",
    defect="NEGATIVE CONTROL: clean MILLIMETRE-context STEP, no unit defect",
)

# 10x10 mm square
p00 = f.cartesian_point((0.0,  0.0,  0.0))
p10 = f.cartesian_point((10.0, 0.0,  0.0))
p11 = f.cartesian_point((10.0, 10.0, 0.0))
p01 = f.cartesian_point((0.0,  10.0, 0.0))

v00 = f.vertex_point(p00); v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11); v01 = f.vertex_point(p01)

def ledge(va, vb, p, dvec, length):
    return f.edge_curve(va, vb, f.line(p, f.vector(f.direction(dvec), length)))

e0 = ledge(v00, v10, p00, (1.0, 0.0, 0.0), 10.0)
e1 = ledge(v10, v11, p10, (0.0, 1.0, 0.0), 10.0)
e2 = ledge(v11, v01, p11, (-1.0, 0.0, 0.0), 10.0)
e3 = ledge(v01, v00, p01, (0.0, -1.0, 0.0), 10.0)

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
f.add_product_chain(sbsm)  # emits LENGTH_UNIT NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.)
