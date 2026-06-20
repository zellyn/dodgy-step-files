"""Twi249 — ShapeFix_IntersectionTool CutEdge range too small.

Catalog claim: Cut range below tolerance threshold. Condition
std::abs(cut - pend) < 10*Precision::PConfusion() triggers at line 200.
Trimmed edge range becomes invalid or degenerate.

Mechanism: GEOMETRIC_CURVE_SET containing an EDGE_LOOP with a 'cut_e' edge
whose parametric extent is extremely small (1e-7 — well below the
10*Precision::PConfusion() threshold of ~1e-6). When ShapeFix_IntersectionTool
attempts CutEdge on this edge the range-too-small condition triggers and the
trimmed edge range becomes degenerate. The sub-threshold range IS the defect;
no diagnostic is emitted on the range-too-small branch.

Byte assertions:
  - contains(b'cut_e')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi249",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with edges on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "cut_e: EDGE_CURVE from V0(0,0,0) to VE(1e-7,0,0) magnitude=1e-7; "
        "parametric extent 1e-7 is below 10*PConfusion threshold IS range-too-small defect; "
        "CutEdge condition abs(cut-pend)<10*PConfusion triggers on cut_e IS defect branch; "
        "trimmed edge range becomes invalid or degenerate after CutEdge IS model impact; "
        "no diagnostic emitted from range-too-small branch IS silent failure; "
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

# cut_e: sub-threshold extent 1e-7
PV0 = (0.0,   0.0, 0.0)
PVE = (1e-7,  0.0, 0.0)   # 1e-7 magnitude IS range-too-small defect

# Surrounding rectangle to make a closed loop
PV1 = (6.0,  0.0, 0.0)
PV2 = (6.0,  6.0, 0.0)
PV3 = (0.0,  6.0, 0.0)

vV0 = f.vertex_point(f.cartesian_point(PV0))
vVE = f.vertex_point(f.cartesian_point(PVE))
vV1 = f.vertex_point(f.cartesian_point(PV1))
vV2 = f.vertex_point(f.cartesian_point(PV2))
vV3 = f.vertex_point(f.cartesian_point(PV3))


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


# cut_e: sub-threshold magnitude IS the defect
ec_cut = _line_sc(vV0, vVE, PV0, PVE, name="cut_e")

# Remaining edges to close the loop (starting from VE ≈ V0)
ec_e1 = _line_sc(vVE, vV1, PVE, PV1, name="e1")
ec_e2 = _line_sc(vV1, vV2, PV1, PV2, name="e2")
ec_e3 = _line_sc(vV2, vV3, PV2, PV3, name="e3")
ec_e4 = _line_sc(vV3, vV0, PV3, PV0, name="e4")

oe_cut = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_cut.eid},.T.)")
oe_e1  = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e1.eid},.T.)")
oe_e2  = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e2.eid},.T.)")
oe_e3  = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e3.eid},.T.)")
oe_e4  = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e4.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_cut.eid},#{oe_e1.eid},#{oe_e2.eid},"
    f"#{oe_e3.eid},#{oe_e4.eid}))"
)

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi249.stp")
