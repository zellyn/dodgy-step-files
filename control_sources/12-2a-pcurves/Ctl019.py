"""Ctl019 — Clean SURFACE_CURVE edge with a real PCURVE (§12-2a-pcurves control).

A planar square face where the bottom edge's geometry is a SURFACE_CURVE
whose associated_geometry holds one genuine PCURVE (2D line in the plane's
parameter space, via a DEFINITIONAL_REPRESENTATION). The non-empty
aggregate and the well-typed pcurve chain are the point: the defective
siblings of this construct (empty associated_geometry) crash in the
reference-graph walk, and the clean form must not be flagged.

Expected: occt=shape(1)/shape(1)
"""
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
sys.path.insert(0, str(_HERE.parents[3] / "validation" / "src"))

from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ctl019",
    defect="NEGATIVE CONTROL: valid SURFACE_CURVE with real PCURVE, no defect",
)

p00 = f.cartesian_point((0.0, 0.0, 0.0))
p20 = f.cartesian_point((2.0, 0.0, 0.0))
p22 = f.cartesian_point((2.0, 2.0, 0.0))
p02 = f.cartesian_point((0.0, 2.0, 0.0))

plc = f.axis2_placement_3d(p00, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
plane = f.plane(plc)

# 3D line for the bottom edge, plus its 2D image in the plane's (u,v) space.
l3d = f.line(p00, f.vector(f.direction((1.0, 0.0, 0.0)), 2.0))
uv0 = f._emit_raw("CARTESIAN_POINT('',(0.0,0.0))")
uvd = f._emit_raw("DIRECTION('',(1.0,0.0))")
uvv = f._emit_raw(f"VECTOR('',#{uvd.eid},2.0)")
l2d = f._emit_raw(f"LINE('',#{uv0.eid},#{uvv.eid})")
ctx2 = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('2D','parameter space'))")
defrep = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{l2d.eid}),#{ctx2.eid})")
pcv = f._emit_raw(f"PCURVE('',#{plane.eid},#{defrep.eid})")
scv = f._emit_raw(f"SURFACE_CURVE('',#{l3d.eid},(#{pcv.eid}),.PCURVE_S1.)")

v00 = f.vertex_point(p00)
v20 = f.vertex_point(p20)
v22 = f.vertex_point(p22)
v02 = f.vertex_point(p02)

def ledge(va, vb, p, dvec):
    return f.edge_curve(va, vb, f.line(p, f.vector(f.direction(dvec), 2.0)))

e0 = f.edge_curve(v00, v20, scv)
e1 = ledge(v20, v22, p20, (0.0, 1.0, 0.0))
e2 = ledge(v22, v02, p22, (-1.0, 0.0, 0.0))
e3 = ledge(v02, v00, p02, (0.0, -1.0, 0.0))

loop = f.edge_loop([f.oriented_edge(e, True) for e in (e0, e1, e2, e3)])
face = f.advanced_face([f.face_outer_bound(loop)], plane, True)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
