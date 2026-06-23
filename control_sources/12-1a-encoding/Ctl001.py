"""Ctl001 — Clean STEP file: UTF-8 encoding, no BOM, no high-bit bytes.

Negative control for §12-1a-encoding. A minimal valid STEP with:
  - ISO-10303-21 bookends present
  - UTF-8 encoding, no BOM
  - No NUL, CRLF, or high-bit bytes
  - Standard ASCII content only
  - Correct FILE_DESCRIPTION / FILE_NAME / FILE_SCHEMA header
  - A simple planar face wired into the product chain

Expected: occt=shape(1)/shape(1)  (no encoding defect → clean load)
"""
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
sys.path.insert(0, str(_HERE.parents[3] / "validation" / "src"))

from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ctl001",
    defect="NEGATIVE CONTROL: clean UTF-8 STEP with no encoding defects",
)

# Simple 1x1 square on the XY plane
p00 = f.cartesian_point((0.0, 0.0, 0.0))
p10 = f.cartesian_point((1.0, 0.0, 0.0))
p11 = f.cartesian_point((1.0, 1.0, 0.0))
p01 = f.cartesian_point((0.0, 1.0, 0.0))

v00 = f.vertex_point(p00)
v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11)
v01 = f.vertex_point(p01)

def ledge(va, vb, p, dvec, length):
    d = f.direction(dvec)
    vec = f.vector(d, length)
    ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

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
plane = f.plane(plc)
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
