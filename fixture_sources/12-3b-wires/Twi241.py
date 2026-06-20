"""Twi241 — ShapeFix_Wire.FixNotchedEdges notch-at-multi-edge-junction.

Catalog claim: Edges form a notch pattern at a junction vertex where multiple
curves meet at shallow angles or with tangency that creates local concavity.
FixNotchedEdges splits the offending curve at the notch point to eliminate
the discontinuity and restore smooth wire traversal.

Mechanism: GEOMETRIC_CURVE_SET containing one EDGE_LOOP representing a
rectangular wire with a notch spike. Four edges form a base rectangle; a
fifth edge 'notch_e' is a short segment that juts inward from vertex V1 to
a notch tip vertex, then a sixth edge 'notch_ret' returns from the tip back
to V1. The notch spike at V1 makes edges on both sides (e0 arriving and e1
departing) meet the notch at shallow angles, creating a concave fold.
FixNotchedEdges tangent-vector analysis must detect this concavity at the
notch junction and split the offending edge IS the mechanism.

Byte assertions:
  - contains(b'notch_e')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi241",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 6 line edges on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "Base rectangle: V0(0,0,0)->V1(8,0,0)->V2(8,6,0)->V3(0,6,0)->V0; "
        "notch_e: spike from V1(8,0,0) to VNotch(8,1.0,0) — juts inward 1 unit upward; "
        "notch_ret: returns from VNotch(8,1.0,0) back to V1(8,0,0); "
        "notch spike creates acute concavity at V1 — arriving e0 +X meets notch +Y at 90°; "
        "departing e1 +Y meets notch_ret -Y at 0° (antiparallel) IS tangent discontinuity; "
        "FixNotchedEdges tangent-vector analysis must split at notch point IS mechanism; "
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
PV0     = (0.0, 0.0, 0.0)
PV1     = (8.0, 0.0, 0.0)   # notch junction
PV2     = (8.0, 6.0, 0.0)
PV3     = (0.0, 6.0, 0.0)
PVNotch = (8.0, 1.0, 0.0)   # notch tip — 1 unit inward from V1

vV0     = f.vertex_point(f.cartesian_point(PV0))
vV1     = f.vertex_point(f.cartesian_point(PV1))
vV2     = f.vertex_point(f.cartesian_point(PV2))
vV3     = f.vertex_point(f.cartesian_point(PV3))
vVNotch = f.vertex_point(f.cartesian_point(PVNotch))


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


# Base rectangle edges
ec_e0 = _line_sc(vV0, vV1, PV0, PV1, name="e0")   # arrives at V1 with +X tangent
ec_e1 = _line_sc(vV1, vV2, PV1, PV2, name="e1")   # departs V1 with +Y tangent
ec_e2 = _line_sc(vV2, vV3, PV2, PV3, name="e2")
ec_e3 = _line_sc(vV3, vV0, PV3, PV0, name="e3")

# Notch spike at V1: in then back out
ec_notch = _line_sc(vV1, vVNotch, PV1, PVNotch, name="notch_e")   # V1 -> tip +Y
ec_notch_ret = _line_sc(vVNotch, vV1, PVNotch, PV1, name="notch_ret")  # tip -> V1 -Y

oe_e0        = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e0.eid},.T.)")
oe_notch     = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_notch.eid},.T.)")
oe_notch_ret = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_notch_ret.eid},.T.)")
oe_e1        = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e1.eid},.T.)")
oe_e2        = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e2.eid},.T.)")
oe_e3        = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e3.eid},.T.)")

# Wire: e0 arrives at V1, notch spike goes in+out, then continue around rectangle
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_e0.eid},#{oe_notch.eid},#{oe_notch_ret.eid},"
    f"#{oe_e1.eid},#{oe_e2.eid},#{oe_e3.eid}))"
)

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi241.stp")
