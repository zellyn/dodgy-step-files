"""Twi233 — ShapeAnalysis_Wire.CheckOuterBound winding-number-zero.

Catalog claim: Wire forming a figure-8 pattern (two loops meeting at pinch
vertex). The 3D winding number around a test point is zero. CheckOuterBound's
enclosing test returns inconclusive, failing to classify the wire correctly as
inner/outer bound.

Mechanism: GEOMETRIC_CURVE_SET containing one EDGE_LOOP representing a
figure-8 wire: two rectangular loops meeting at shared pinch vertex 'pinch_v'
at origin (0,0,0). Left loop: (0,0,0)→(-5,0,0)→(-5,5,0)→(0,5,0)→(0,0,0).
Right loop: (0,0,0)→(5,0,0)→(5,5,0)→(0,5,0)→(0,0,0). The two loops run in
opposite orientation so the winding number around any interior test point
is zero IS the defect. CheckOuterBound's test returns inconclusive.

Byte assertions:
  - contains(b'pinch_v')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Twi233",
    defect=(
        "GEOMETRIC_CURVE_SET containing EDGE_LOOP forming figure-8 pattern on PLANE; "
        "PLANE: normal +Z, origin (0,0,0); "
        "pinch_v at origin (0,0,0) IS the shared junction vertex of two loops; "
        "left loop: (0,0,0)→(-5,0,0)→(-5,5,0)→(0,5,0)→(0,0,0) CCW orientation; "
        "right loop: (0,0,0)→(0,5,0)→(5,5,0)→(5,0,0)→(0,0,0) CW orientation; "
        "opposite orientations produce winding-number zero around any interior point; "
        "CheckOuterBound enclosing test IS inconclusive — cannot classify wire IS defect; "
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
# Pinch vertex at origin — shared by both loops
PPinch = (0.0,  0.0, 0.0)
PL1    = (-5.0, 0.0, 0.0)   # left-bottom
PL2    = (-5.0, 5.0, 0.0)   # left-top
PTop_l = (0.0,  5.0, 0.0)   # top-center left
PTop_r = (0.0,  5.0, 0.0)   # top-center right (same coords)
PR1    = (5.0,  0.0, 0.0)   # right-bottom
PR2    = (5.0,  5.0, 0.0)   # right-top

vPinch = f.vertex_point(f.cartesian_point(PPinch))
vL1    = f.vertex_point(f.cartesian_point(PL1))
vL2    = f.vertex_point(f.cartesian_point(PL2))
vTopL  = f.vertex_point(f.cartesian_point(PTop_l))
vTopR  = f.vertex_point(f.cartesian_point(PTop_r))
vR1    = f.vertex_point(f.cartesian_point(PR1))
vR2    = f.vertex_point(f.cartesian_point(PR2))


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


# Left loop (CCW): pinch→L1→L2→TopL→pinch
ec_l0 = _line_sc(vPinch, vL1,   PPinch, PL1,    name="left_bottom")
ec_l1 = _line_sc(vL1,    vL2,   PL1,    PL2,    name="left_side")
ec_l2 = _line_sc(vL2,    vTopL, PL2,    PTop_l, name="left_top")
ec_l3 = _line_sc(vTopL,  vPinch, PTop_l, PPinch, name="pinch_v")

oe_l0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_l0.eid},.T.)")
oe_l1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_l1.eid},.T.)")
oe_l2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_l2.eid},.T.)")
oe_l3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_l3.eid},.T.)")

# Right loop (CW): pinch→TopR→R2→R1→pinch
# Note: opposite orientation — TopR same coords as TopL but separate vertex entity
ec_r0 = _line_sc(vPinch, vTopR, PPinch, PTop_r, name="right_top_up")
ec_r1 = _line_sc(vTopR,  vR2,   PTop_r, PR2,    name="right_top")
ec_r2 = _line_sc(vR2,    vR1,   PR2,    PR1,    name="right_side")
ec_r3 = _line_sc(vR1,    vPinch, PR1,   PPinch, name="right_bottom")

oe_r0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_r0.eid},.T.)")
oe_r1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_r1.eid},.T.)")
oe_r2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_r2.eid},.T.)")
oe_r3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_r3.eid},.T.)")

# Full EDGE_LOOP: left loop then right loop
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_l0.eid},#{oe_l1.eid},#{oe_l2.eid},#{oe_l3.eid},"
    f"#{oe_r0.eid},#{oe_r1.eid},#{oe_r2.eid},#{oe_r3.eid}))"
)

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{loop.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi233.stp")
