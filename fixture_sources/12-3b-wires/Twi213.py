"""Twi213 — ShapeAnalysis_Wire.CheckGap3d using-pcurve-distance.

Catalog claim: Adjacent edges have valid 3D positional continuity but invalid
pcurve geometry (gap in parametric space). CheckGap3d defaults to 3D distance
check and misses the pcurve discontinuity.

Mechanism: GEOMETRIC_CURVE_SET containing one EDGE_LOOP with 3 edges on a
PLANE. Edge 'pcurve_gap_e0' has a pcurve ending at parameter point (5, 0) in
UV space; edge 'pcurve_gap_e1' (adjacent) has its pcurve starting at (7, 0)
in UV space — a parametric gap of 2 units — but both edges share the same 3D
junction vertex at (5, 0, 0). CheckGap3d checks only 3D vertex proximity and
finds no gap; the pcurve discontinuity of 2 UV units IS the defect that goes
undetected.

Byte assertions:
  - contains(b'pcurve_gap_e0')
  - contains(b'pcurve_gap_e1')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi213",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 3 edges on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "pcurve_gap_e0: LINE V0(0,0,0)->V1(5,0,0), pcurve LINE in UV "
        "from (0,0) direction (1,0) — pcurve ends at UV=(5,0); "
        "pcurve_gap_e1: LINE V1(5,0,0)->V2(10,0,0), pcurve LINE in UV "
        "STARTS at (7,0) instead of (5,0) — UV gap of 2 units IS the defect; "
        "both edges share 3D junction vertex V1=(5,0,0) — 3D continuity valid; "
        "CheckGap3d 3D-only check misses the UV pcurve gap IS the mechanism; "
        "close_e2: V2(10,0,0)->V0(0,0,0) closes the wire; "
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

# 3D vertices
PV0 = (0.0,  0.0, 0.0)
PV1 = (5.0,  0.0, 0.0)   # junction with valid 3D continuity
PV2 = (10.0, 0.0, 0.0)

vV0 = f.vertex_point(f.cartesian_point(PV0))
vV1 = f.vertex_point(f.cartesian_point(PV1))
vV2 = f.vertex_point(f.cartesian_point(PV2))


def _line_sc_with_uv(v_s, v_e, ps, pe, uv_s, uv_e, name=""):
    """LINE edge with explicit UV pcurve endpoints (allows pcurve gap)."""
    dx = pe[0] - ps[0]; dy = pe[1] - ps[1]; dz = pe[2] - ps[2]
    mag3 = _math.sqrt(dx*dx + dy*dy + dz*dz)
    ln3 = f.line(f.cartesian_point(ps),
                 f.vector(f.direction((dx/mag3, dy/mag3, dz/mag3)), mag3))
    # Build UV pcurve with explicit start point (may differ from 3D projection)
    du = uv_e[0] - uv_s[0]; dv = uv_e[1] - uv_s[1]
    mag_uv = _math.sqrt(du*du + dv*dv)
    uv_orig = f.cartesian_point(uv_s)
    uv_dir  = f.direction((du/mag_uv, dv/mag_uv))
    uv_vec  = f.vector(uv_dir, mag_uv)
    uv_ln   = f.line(uv_orig, uv_vec)
    drep    = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{uv_ln.eid}),#*)")
    pc      = f._emit_raw(f"PCURVE('',#{plane.eid},#{drep.eid})")
    sc      = f._emit_raw(f"SURFACE_CURVE('',#{ln3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('{name}',#{v_s.eid},#{v_e.eid},#{sc.eid},.T.)")


def _line_sc(v_s, v_e, ps, pe, name=""):
    """LINE edge with UV pcurve matching 3D XY projection."""
    return _line_sc_with_uv(v_s, v_e, ps, pe, (ps[0], ps[1]), (pe[0], pe[1]), name=name)


# pcurve_gap_e0: V0(0,0,0)->V1(5,0,0), pcurve from UV=(0,0) to UV=(5,0) — normal
ec0 = _line_sc_with_uv(vV0, vV1, PV0, PV1, (0.0, 0.0), (5.0, 0.0), name="pcurve_gap_e0")
oe0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec0.eid},.T.)")

# pcurve_gap_e1: V1(5,0,0)->V2(10,0,0), pcurve STARTS at UV=(7,0) not UV=(5,0)
# 3D is continuous (same V1 vertex) but UV start is at u=7 — gap of 2 IS defect
ec1 = _line_sc_with_uv(vV1, vV2, PV1, PV2, (7.0, 0.0), (12.0, 0.0), name="pcurve_gap_e1")
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec1.eid},.T.)")

# close_e2: V2(10,0,0)->V0(0,0,0), normal closing edge
ec2 = _line_sc(vV2, vV0, PV2, PV0, name="close_e2")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec2.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe0.eid},#{oe1.eid},#{oe2.eid}))"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi213.stp")
