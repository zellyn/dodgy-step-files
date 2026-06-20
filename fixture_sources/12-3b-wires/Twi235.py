"""Twi235 — ShapeAnalysis_Wire.CheckTail B-spline-tangent-mismatch.

Catalog claim: Wire's tail edge has tangent at start that doesn't match the
previous edge's tangent at end, forming a sharp corner. CheckTail's
smooth-only assumption misses this case when B-splines are involved.

Mechanism: GEOMETRIC_CURVE_SET containing one EDGE_LOOP representing a
rectangular base loop with a B-spline tail edge 'bspl_tail' appended. The
tail's B-spline curve has a starting tangent pointing in a direction
perpendicular to the line edge it meets, creating a sharp corner at the
junction. CheckTail's smooth-tail detection assumes G1 continuity and skips
the tail when the junction has a sharp tangent break IS the defect.

Byte assertions:
  - contains(b'bspl_tail')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi235",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with rectangular base loop and "
        "B-spline tail edge on PLANE; PLANE: normal +Z, origin (0,0,0); "
        "Base rectangle: V0(0,0,0)->V1(8,0,0)->V2(8,6,0)->V3(0,6,0)->V0; "
        "branch vertex V1(8,0,0) IS where B-spline tail starts; "
        "bspl_tail: degree-3 B-spline from V1(8,0,0) to Vtip(8,-3,0) then doubles back; "
        "tail start tangent: pointing in +Y direction (perpendicular to line e0 +X tangent); "
        "sharp corner at junction V1 IS the tangent mismatch defect; "
        "CheckTail smooth-only assumption misses tail at sharp corner IS mechanism; "
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
PV0   = (0.0, 0.0,  0.0)
PV1   = (8.0, 0.0,  0.0)   # branch for tail — line e0 arrives with +X tangent
PV2   = (8.0, 6.0,  0.0)
PV3   = (0.0, 6.0,  0.0)
PVtip = (8.0, -3.0, 0.0)   # tail tip

vV0   = f.vertex_point(f.cartesian_point(PV0))
vV1   = f.vertex_point(f.cartesian_point(PV1))
vV2   = f.vertex_point(f.cartesian_point(PV2))
vV3   = f.vertex_point(f.cartesian_point(PV3))
vVtip = f.vertex_point(f.cartesian_point(PVtip))


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


# Base rectangle edges: V0->V1->V2->V3->V0
ec_e0 = _line_sc(vV0, vV1, PV0, PV1, name="e0")   # arrives at V1 with +X tangent
ec_e1 = _line_sc(vV1, vV2, PV1, PV2, name="e1")
ec_e2 = _line_sc(vV2, vV3, PV2, PV3, name="e2")
ec_e3 = _line_sc(vV3, vV0, PV3, PV0, name="e3")

oe_e0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e0.eid},.T.)")
oe_e1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e1.eid},.T.)")
oe_e2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e2.eid},.T.)")
oe_e3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e3.eid},.T.)")

# B-spline tail: starts at V1(8,0,0), initial tangent in -Y direction
# (perpendicular to +X arrival tangent of e0 IS the sharp corner)
# Control points designed so tangent at t=0 is -Y direction:
#   CP[0] = V1 = (8, 0, 0)
#   CP[1] = (8, -2, 0) → tangent direction = CP1-CP0 = (0,-2,0) → -Y direction
#   CP[2] = (8, -3, 0) → heading to tip
#   CP[3] = Vtip = (8, -3, 0) same as tip — effectively stopped
# Use degree 3, 4 control points → knot sum = 4+3+1 = 8, multiplicities [4,4]
cp_t0 = f.cartesian_point(( 8.0,  0.0, 0.0))  # start V1
cp_t1 = f.cartesian_point(( 8.0, -2.0, 0.0))  # tangent control: -Y IS mismatch with +X
cp_t2 = f.cartesian_point(( 8.0, -3.5, 0.0))
cp_t3 = f.cartesian_point(( 8.0, -3.0, 0.0))  # tip end

bspl_tail = f.b_spline_curve_with_knots(
    degree=3,
    control_points=[cp_t0, cp_t1, cp_t2, cp_t3],
    knot_multiplicities=[4, 4],
    knots=[0.0, 1.0],
    curve_form="UNSPECIFIED",
    closed=False,
    self_intersect=False,
    knot_spec="UNSPECIFIED",
    name="bspl_tail_3d",
)

# Pcurve for tail: straight line in UV from V1 to Vtip
uv_t_s = (8.0, 0.0)
uv_t_e = (8.0, -3.0)
du_t = uv_t_e[0] - uv_t_s[0]; dv_t = uv_t_e[1] - uv_t_s[1]
mag_t = _math.sqrt(du_t*du_t + dv_t*dv_t)
pc_t_orig = f.cartesian_point(uv_t_s)
pc_t_dir  = f.direction((du_t/mag_t, dv_t/mag_t))
pc_t_vec  = f.vector(pc_t_dir, mag_t)
pc_t_ln   = f.line(pc_t_orig, pc_t_vec)
drep_t    = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{pc_t_ln.eid}),#*)")
pc_t      = f._emit_raw(f"PCURVE('',#{plane.eid},#{drep_t.eid})")
sc_t      = f._emit_raw(f"SURFACE_CURVE('',#{bspl_tail.eid},(#{pc_t.eid}),.PCURVE_S1.)")
ec_tail   = f._emit_raw(f"EDGE_CURVE('bspl_tail',#{vV1.eid},#{vVtip.eid},#{sc_t.eid},.T.)")

oe_tail_in = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_tail.eid},.T.)")
oe_tail_rt = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_tail.eid},.F.)")

# Wire: e0 arrives at V1, then tail goes out and back (oe_tail_in + oe_tail_rt),
# then continue around rectangle
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_e0.eid},#{oe_tail_in.eid},#{oe_tail_rt.eid},"
    f"#{oe_e1.eid},#{oe_e2.eid},#{oe_e3.eid}))"
)

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi235.stp")
