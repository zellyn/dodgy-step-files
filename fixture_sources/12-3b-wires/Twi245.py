"""Twi245 — ShapeAnalysis_Wire closure gap.

Catalog claim: EDGE_LOOP topology declares closed but 3D geometry has gap at
closure point. EDGE_LOOP has 4 edges; last edge ends at (0.0, 0.05, 0.0)
while first edge starts at (0.0, 0.0, 0.0) — 0.05 mm gap violates geometric
closure despite topological closure claim.

Mechanism: GEOMETRIC_CURVE_SET containing one EDGE_LOOP with 4 edges. The
wire topologically claims to be closed (EDGE_LOOP) but the start point of
edge 'gap_e0' at (0,0,0) does not match the end point of 'gap_e3' at
(0,0.05,0) — a 0.05 mm geometric gap. Wire validation detects this geometric
gap; FixSeam or FixConnected must insert a bridge or adjust the endpoint.

Byte assertions:
  - contains(b'gap_e0')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi245",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 4 line edges on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "gap_e0: (0,0,0)->(6,0,0); gap_e1: (6,0,0)->(6,6,0); "
        "gap_e2: (6,6,0)->(0,6,0); gap_e3: (0,6,0)->(0,0.05,0); "
        "gap_e3 ends at (0,0.05,0) but gap_e0 starts at (0,0,0) — 0.05 mm gap IS defect; "
        "EDGE_LOOP topologically claims closure but geometry does not close IS inconsistency; "
        "FixSeam or FixConnected must bridge the 0.05 mm gap at closure IS repair; "
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

# Vertices — last edge ends at (0, 0.05, 0) not (0, 0, 0) IS the closure gap
PV0  = (0.0,  0.0,  0.0)   # first edge start
PV1  = (6.0,  0.0,  0.0)
PV2  = (6.0,  6.0,  0.0)
PV3  = (0.0,  6.0,  0.0)
PV3e = (0.0,  0.05, 0.0)   # last edge end — gap of 0.05 mm from PV0

vV0  = f.vertex_point(f.cartesian_point(PV0))
vV1  = f.vertex_point(f.cartesian_point(PV1))
vV2  = f.vertex_point(f.cartesian_point(PV2))
vV3  = f.vertex_point(f.cartesian_point(PV3))
vV3e = f.vertex_point(f.cartesian_point(PV3e))


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


# 4 edges; last ends at (0, 0.05, 0) — gap from first start at (0, 0, 0)
ec_e0 = _line_sc(vV0,  vV1,  PV0,  PV1,  name="gap_e0")
ec_e1 = _line_sc(vV1,  vV2,  PV1,  PV2,  name="gap_e1")
ec_e2 = _line_sc(vV2,  vV3,  PV2,  PV3,  name="gap_e2")
ec_e3 = _line_sc(vV3,  vV3e, PV3,  PV3e, name="gap_e3")   # ends 0.05 from V0

oe_e0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e0.eid},.T.)")
oe_e1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e1.eid},.T.)")
oe_e2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e2.eid},.T.)")
oe_e3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e3.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_e0.eid},#{oe_e1.eid},#{oe_e2.eid},#{oe_e3.eid}))"
)

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi245.stp")
