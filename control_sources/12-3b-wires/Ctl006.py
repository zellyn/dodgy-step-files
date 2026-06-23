"""Ctl006 — Clean square wire (negative control for §12-3b-wires).

A 1x1 square EDGE_LOOP on the XY plane wired into a GEOMETRICALLY_BOUNDED_WIREFRAME_SHAPE_REPRESENTATION.
No open endpoints, no dangling edges, no gap.

Expected: occt=shape(1)/shape(1)
"""
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
sys.path.insert(0, str(_HERE.parents[3] / "validation" / "src"))

from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ctl006",
    defect="NEGATIVE CONTROL: clean square wire, no wire defect",
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

# Wire as a GEOMETRICALLY_BOUNDED_WIREFRAME_SHAPE_REPRESENTATION
# Use add_product_chain via a shell-based surface model on a planar face
plc = f.axis2_placement_3d(p00, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
face = f.advanced_face([f.face_outer_bound(loop)], f.plane(plc))
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
