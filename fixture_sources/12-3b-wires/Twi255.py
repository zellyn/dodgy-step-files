"""Twi255 — ShapeAnalysis_Wire.CheckLoop.null-vertices

Catalog claim: Multi-edge wire with one edge having null V1 endpoint;
validates FAIL2 encoding. Without null check, segfault on
BRep_Tool::Tolerance().

Mechanism: GEOMETRIC_CURVE_SET containing an EDGE_LOOP where the defect
edge 'null_v1_e' has V1 = $ (null reference). When ShapeAnalysis_Wire::
CheckLoop builds the vertex map it calls BRep_Tool::Tolerance() on each
endpoint vertex; a null V1 causes a segfault before the FAIL2 status code
can be encoded. The null V1 IS the defect; a guard must check vertex
validity before any BRep_Tool call.

Byte assertions:
  - contains(b'null_v1_e')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi255",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with edges on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "null_v1_e: EDGE_CURVE $->V1 (null V1) IS null-vertex defect; "
        "CheckLoop calls BRep_Tool::Tolerance() on V1 before null guard; "
        "segfault on BRep_Tool::Tolerance() with null vertex IS defect; "
        "FAIL2 encoding unreachable without null guard IS defect; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP; never orphaned"
    ),
)

# PLANE: normal +Z
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# Rectangle vertices
PV0 = (0.0, 0.0, 0.0)
PV1 = (6.0, 0.0, 0.0)
PV2 = (6.0, 6.0, 0.0)
PV3 = (0.0, 6.0, 0.0)

vV0 = f.vertex_point(f.cartesian_point(PV0))
vV1 = f.vertex_point(f.cartesian_point(PV1))
vV2 = f.vertex_point(f.cartesian_point(PV2))
vV3 = f.vertex_point(f.cartesian_point(PV3))


def _line_sc(ps, pe, name=""):
    dx = pe[0] - ps[0]; dy = pe[1] - ps[1]; dz = pe[2] - ps[2]
    mag = _math.sqrt(dx*dx + dy*dy + dz*dz)
    ln3 = f.line(f.cartesian_point(ps),
                 f.vector(f.direction((dx/mag, dy/mag, dz/mag)), mag))
    uv_orig = f.cartesian_point((ps[0], ps[1]))
    uv_dir  = f.direction((dx/mag, dy/mag))
    uv_vec  = f.vector(uv_dir, mag)
    uv_ln   = f.line(uv_orig, uv_vec)
    drep    = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{uv_ln.eid}),#*)")
    pc      = f._emit_raw(f"PCURVE('',#{plane.eid},#{drep.eid})")
    sc      = f._emit_raw(f"SURFACE_CURVE('',#{ln3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return sc


# null_v1_e: V1 = $ (null) IS the defect
sc_nv1 = _line_sc(PV0, PV1)
ec_nv1 = f._emit_raw(
    f"EDGE_CURVE('null_v1_e',$,#{vV1.eid},#{sc_nv1.eid},.T.)"
)

# Remaining edges to close the loop (normal vertices)
sc_e1 = _line_sc(PV1, PV2)
ec_e1 = f._emit_raw(f"EDGE_CURVE('e1',#{vV1.eid},#{vV2.eid},#{sc_e1.eid},.T.)")

sc_e2 = _line_sc(PV2, PV3)
ec_e2 = f._emit_raw(f"EDGE_CURVE('e2',#{vV2.eid},#{vV3.eid},#{sc_e2.eid},.T.)")

sc_e3 = _line_sc(PV3, PV0)
ec_e3 = f._emit_raw(f"EDGE_CURVE('e3',#{vV3.eid},#{vV0.eid},#{sc_e3.eid},.T.)")

oe_nv1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_nv1.eid},.T.)")
oe_e1  = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e1.eid},.T.)")
oe_e2  = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e2.eid},.T.)")
oe_e3  = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e3.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_nv1.eid},#{oe_e1.eid},#{oe_e2.eid},#{oe_e3.eid}))"
)

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi255.stp")
