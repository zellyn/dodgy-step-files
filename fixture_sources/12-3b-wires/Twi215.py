"""Twi215 — ShapeAnalysis_Wire.CheckTail multi-tail-detection.

Catalog claim: Wire with multiple potential tail candidates. CheckTail picks
the first and reports it as definitive but should enumerate all.

Mechanism: GEOMETRIC_CURVE_SET containing one EDGE_LOOP representing a
rectangular loop with two small spike tails appended. Spike 'tail_a' doubles
back from (5,0,0)→(5,-2,0)→(5,0,0). Spike 'tail_b' doubles back from
(10,5,0)→(12,5,0)→(10,5,0). CheckTail finds 'tail_a' first and returns it
as the definitive tail without detecting 'tail_b' IS the multi-tail-detection
defect.

Byte assertions:
  - contains(b'tail_a')
  - contains(b'tail_b')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi215",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with rectangular loop plus "
        "two spike tails on PLANE; PLANE: normal +Z, origin (0,0,0); "
        "Rectangle: V0(0,0,0)->V1(5,0,0)->V2(10,0,0)->V3(10,5,0)->V4(0,5,0)->V0; "
        "tail_a: spike V1(5,0,0)->Vta(5,-2,0)->V1, doubles back IS first tail; "
        "tail_b: spike V3(10,5,0)->Vtb(12,5,0)->V3, doubles back IS second tail; "
        "CheckTail finds tail_a first and reports it as definitive IS defect; "
        "tail_b goes undetected — multi-tail enumeration IS the mechanism; "
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

# 3D vertex coordinates
PV0  = (0.0,  0.0, 0.0)
PV1  = (5.0,  0.0, 0.0)   # branch point for tail_a
PV2  = (10.0, 0.0, 0.0)
PV3  = (10.0, 5.0, 0.0)   # branch point for tail_b
PV4  = (0.0,  5.0, 0.0)
PVta = (5.0,  -2.0, 0.0)  # tail_a tip
PVtb = (12.0, 5.0, 0.0)   # tail_b tip

vV0  = f.vertex_point(f.cartesian_point(PV0))
vV1  = f.vertex_point(f.cartesian_point(PV1))
vV2  = f.vertex_point(f.cartesian_point(PV2))
vV3  = f.vertex_point(f.cartesian_point(PV3))
vV4  = f.vertex_point(f.cartesian_point(PV4))
vVta = f.vertex_point(f.cartesian_point(PVta))
vVtb = f.vertex_point(f.cartesian_point(PVtb))


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


# Wire order: V0->V1, then tail_a spike (V1->Vta->V1), then V1->V2->V3,
# then tail_b spike (V3->Vtb->V3), then V3->V4->V0
ec_e0    = _line_sc(vV0,  vV1,  PV0,  PV1,  name="e0")
oe_e0    = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e0.eid},.T.)")

ec_ta_in = _line_sc(vV1,  vVta, PV1,  PVta, name="tail_a")
oe_ta_in = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_ta_in.eid},.T.)")

# tail_a return: Vta->V1 (reverse of tail_a edge)
oe_ta_rt = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_ta_in.eid},.F.)")

ec_e1    = _line_sc(vV1,  vV2,  PV1,  PV2,  name="e1")
oe_e1    = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e1.eid},.T.)")

ec_e2    = _line_sc(vV2,  vV3,  PV2,  PV3,  name="e2")
oe_e2    = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e2.eid},.T.)")

ec_tb_in = _line_sc(vV3,  vVtb, PV3,  PVtb, name="tail_b")
oe_tb_in = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_tb_in.eid},.T.)")

# tail_b return: Vtb->V3
oe_tb_rt = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_tb_in.eid},.F.)")

ec_e3    = _line_sc(vV3,  vV4,  PV3,  PV4,  name="e3")
oe_e3    = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e3.eid},.T.)")

ec_e4    = _line_sc(vV4,  vV0,  PV4,  PV0,  name="e4")
oe_e4    = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e4.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_e0.eid},#{oe_ta_in.eid},#{oe_ta_rt.eid},"
    f"#{oe_e1.eid},#{oe_e2.eid},#{oe_tb_in.eid},#{oe_tb_rt.eid},"
    f"#{oe_e3.eid},#{oe_e4.eid}))"
)

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi215.stp")
