"""Twi247 — BRepLib::SameParameter exception silent skip.

Catalog claim: Edge with inconsistent 3D curve and parametric curves;
BRepLib::SameParameter throws Standard_Failure. Catch block executes continue
without diagnostic output. Operation appears successful to caller.

Mechanism: GEOMETRIC_CURVE_SET containing an EDGE_LOOP with one 'incon_e' edge
whose SURFACE_CURVE has a 3D LINE pointing in +X but whose PCURVE definitional
representation has a 2D LINE pointing in +Y. The direction mismatch between the
3D curve and the parametric curve creates a same-parameter inconsistency. When
BRepLib::SameParameter processes this edge the inconsistency triggers
Standard_Failure; the catch block silently continues instead of reporting the
failure IS the defect.

Byte assertions:
  - contains(b'incon_e')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi247",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 4 line edges on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "Rectangle: V0(0,0,0)->V1(6,0,0)->V2(6,6,0)->V3(0,6,0)->V0; "
        "incon_e: EDGE_CURVE V0->V1; 3D LINE dir +X but PCURVE 2D dir +Y IS mismatch; "
        "3D curve and parametric curve directions are inconsistent IS same-parameter defect; "
        "BRepLib::SameParameter throws Standard_Failure on incon_e inconsistency; "
        "catch block executes continue without diagnostic — silent skip IS defect; "
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

# Vertices
PV0 = (0.0, 0.0, 0.0)
PV1 = (6.0, 0.0, 0.0)
PV2 = (6.0, 6.0, 0.0)
PV3 = (0.0, 6.0, 0.0)

vV0 = f.vertex_point(f.cartesian_point(PV0))
vV1 = f.vertex_point(f.cartesian_point(PV1))
vV2 = f.vertex_point(f.cartesian_point(PV2))
vV3 = f.vertex_point(f.cartesian_point(PV3))

# incon_e: 3D curve is +X direction, but pcurve is +Y direction — inconsistency IS defect
ln3_incon  = f.line(f.cartesian_point(PV0),
                    f.vector(f.direction((1.0, 0.0, 0.0)), 6.0))   # 3D: +X
uv_orig_ic = f.cartesian_point((PV0[0], PV0[1]))
uv_dir_ic  = f.direction((0.0, 1.0))                               # 2D: +Y IS mismatch
uv_vec_ic  = f.vector(uv_dir_ic, 6.0)
uv_ln_ic   = f.line(uv_orig_ic, uv_vec_ic)
drep_ic    = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{uv_ln_ic.eid}),#*)")
pc_ic      = f._emit_raw(f"PCURVE('',#{plane.eid},#{drep_ic.eid})")
sc_ic      = f._emit_raw(f"SURFACE_CURVE('',#{ln3_incon.eid},(#{pc_ic.eid}),.PCURVE_S1.)")
ec_incon   = f._emit_raw(
    f"EDGE_CURVE('incon_e',#{vV0.eid},#{vV1.eid},#{sc_ic.eid},.T.)"
)


def _line_sc(v_s, v_e, ps, pe, name=""):
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
    return f._emit_raw(f"EDGE_CURVE('{name}',#{v_s.eid},#{v_e.eid},#{sc.eid},.T.)")


# Remaining rectangle edges
ec_e1 = _line_sc(vV1, vV2, PV1, PV2, name="e1")
ec_e2 = _line_sc(vV2, vV3, PV2, PV3, name="e2")
ec_e3 = _line_sc(vV3, vV0, PV3, PV0, name="e3")

oe_incon = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_incon.eid},.T.)")
oe_e1    = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e1.eid},.T.)")
oe_e2    = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e2.eid},.T.)")
oe_e3    = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e3.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_incon.eid},#{oe_e1.eid},#{oe_e2.eid},#{oe_e3.eid}))"
)

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi247.stp")
