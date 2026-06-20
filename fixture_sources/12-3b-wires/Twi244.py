"""Twi244 — ShapeAnalysis_Wire.CheckSmall degenerate zero-length edge.

Catalog claim: Degenerate zero-length edge in closed loop. EDGE_LOOP contains
edge 'degen_e' with magnitude 0.00001 (far below tolerance), linking same
vertex. CheckSmall flags sub-tolerance edges; FixSmall removes them.

Mechanism: GEOMETRIC_CURVE_SET containing one EDGE_LOOP representing a
rectangular wire with a degenerate 'degen_e' edge of length 0.00001 inserted
between V1 and a duplicate vertex VD at the same location. The sub-tolerance
edge magnitude is the defect; CheckSmall's length test flags it and FixSmall
should remove it from the wire.

Byte assertions:
  - contains(b'degen_e')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi244",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP with 4 line edges on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "Rectangle: V0(0,0,0)->V1(6,0,0)->V2(6,6,0)->V3(0,6,0)->V0; "
        "degen_e: EDGE_CURVE from V1(6,0,0) to VD(6.00001,0,0) magnitude=0.00001; "
        "magnitude 0.00001 is far below tolerance IS degenerate sub-tolerance edge; "
        "CheckSmall flags degen_e magnitude < tolerance IS defect; "
        "FixSmall must identify and suppress degen_e from wire IS repair mechanism; "
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

# Main rectangle vertices
PV0 = (0.0, 0.0, 0.0)
PV1 = (6.0, 0.0, 0.0)
PV2 = (6.0, 6.0, 0.0)
PV3 = (0.0, 6.0, 0.0)
# Degenerate duplicate vertex — 0.00001 from V1
PVD = (6.00001, 0.0, 0.0)

vV0 = f.vertex_point(f.cartesian_point(PV0))
vV1 = f.vertex_point(f.cartesian_point(PV1))
vV2 = f.vertex_point(f.cartesian_point(PV2))
vV3 = f.vertex_point(f.cartesian_point(PV3))
vVD = f.vertex_point(f.cartesian_point(PVD))   # near-duplicate


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


# Rectangle edges (V0->V1->V2->V3->V0), with degenerate edge inserted at V1
ec_e0    = _line_sc(vV0, vV1, PV0, PV1, name="e0")
# Degenerate sub-tolerance edge: V1 -> VD, magnitude=0.00001 IS the defect
ec_degen = _line_sc(vV1, vVD, PV1, PVD, name="degen_e")
ec_e1    = _line_sc(vVD, vV2, PVD, PV2, name="e1")
ec_e2    = _line_sc(vV2, vV3, PV2, PV3, name="e2")
ec_e3    = _line_sc(vV3, vV0, PV3, PV0, name="e3")

oe_e0    = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e0.eid},.T.)")
oe_degen = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_degen.eid},.T.)")
oe_e1    = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e1.eid},.T.)")
oe_e2    = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e2.eid},.T.)")
oe_e3    = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_e3.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_e0.eid},#{oe_degen.eid},#{oe_e1.eid},"
    f"#{oe_e2.eid},#{oe_e3.eid}))"
)

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi244.stp")
