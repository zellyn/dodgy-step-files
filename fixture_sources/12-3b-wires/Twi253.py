"""Twi253 — ShapeAnalysis_Wire.CheckConnected.NULL_EDGE_VERTICES

Catalog claim: EDGE_CURVE with null V2 endpoint; validates null-vertex
detection. Without null check, segfault on IsSame() dereference.

Mechanism: GEOMETRIC_CURVE_SET containing an EDGE_LOOP where the defect
edge 'null_v2_e' has V2 = $ (null reference). When ShapeAnalysis_Wire::
CheckConnected accesses the endpoint vertices to test connectivity the V2
null dereference reaches IsSame() without a null guard IS the defect. The
remaining edges use normal vertices to close the loop around the null-V2 edge.

Byte assertions:
  - contains(b'null_v2_e')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi253",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with edges on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "null_v2_e: EDGE_CURVE V0->$ (null V2) IS null-vertex defect; "
        "CheckConnected accesses V2 endpoint for IsSame() test; "
        "without null check on V2, segfault on IsSame() dereference IS defect; "
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


def _line_sc(v_s, v_e_ref, ps, pe, name="", null_v2=False):
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
    if null_v2:
        # V2 = $ (null) IS the defect
        return f._emit_raw(f"EDGE_CURVE('{name}',#{v_s.eid},$,#{sc.eid},.T.)")
    return f._emit_raw(f"EDGE_CURVE('{name}',#{v_s.eid},#{v_e_ref.eid},#{sc.eid},.T.)")


# null_v2_e: defect edge with V2 = $ (null)
ec_nv2 = _line_sc(vV0, None, PV0, PV1, name="null_v2_e", null_v2=True)

# Remaining edges to close the loop
ec_e1 = _line_sc(vV1, vV2, PV1, PV2, name="e1")
ec_e2 = _line_sc(vV2, vV3, PV2, PV3, name="e2")
ec_e3 = _line_sc(vV3, vV0, PV3, PV0, name="e3")

oe_nv2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_nv2.eid},.T.)")
oe_e1  = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e1.eid},.T.)")
oe_e2  = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e2.eid},.T.)")
oe_e3  = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e3.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_nv2.eid},#{oe_e1.eid},#{oe_e2.eid},#{oe_e3.eid}))"
)

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi253.stp")
