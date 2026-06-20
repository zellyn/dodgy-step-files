"""Tfa166 — ShapeFix_Face.FixSmallAreaWire negative-area-from-orientation.

Catalog claim: Wire with incorrect traversal direction producing negative
signed area. Inner hole traversed counter-clockwise instead of clockwise;
FixSmallAreaWire uses absolute value during area check but fails to correct
wire orientation before returning, leaving the face with an incorrectly-
oriented inner bound.

Mechanism: GEOMETRIC_CURVE_SET containing an ADVANCED_FACE on a PLANE. The
outer wire is a 20×20 rectangle traversed CCW (correct). The inner hole wire
is a 6×6 rectangle traversed CCW instead of CW — producing a negative signed
area relative to the face normal. FixSmallAreaWire's |area| check passes but
the wrong orientation is not corrected. FACE_BOUND has .T. (CCW) instead of
.F. (CW) for the inner hole.

OCC sees a GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa166",
    defect=(
        "GEOMETRIC_CURVE_SET containing ADVANCED_FACE on PLANE; "
        "outer wire: 20×20 rectangle at (0,0)-(20,20) traversed CCW (correct); "
        "inner hole wire: 6×6 rectangle at (7,7)-(13,13) traversed CCW (wrong for hole); "
        "CCW inner wire produces negative signed area relative to face normal; "
        "FACE_BOUND uses .T. (CCW) not .F. (CW) — incorrect orientation; "
        "FixSmallAreaWire uses |area| so passes check without correcting orientation; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "no orphaned entities"
    ),
)

# ── Plane surface ─────────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# ── Outer wire: 20×20 rectangle, CCW ─────────────────────────────────────────
op0 = f.cartesian_point((0.0,  0.0,  0.0))
op1 = f.cartesian_point((20.0, 0.0,  0.0))
op2 = f.cartesian_point((20.0, 20.0, 0.0))
op3 = f.cartesian_point((0.0,  20.0, 0.0))

ov0 = f._emit_raw(f"VERTEX_POINT('',#{op0.eid})")
ov1 = f._emit_raw(f"VERTEX_POINT('',#{op1.eid})")
ov2 = f._emit_raw(f"VERTEX_POINT('',#{op2.eid})")
ov3 = f._emit_raw(f"VERTEX_POINT('',#{op3.eid})")

od_px = f.direction((1.0,  0.0, 0.0))
od_py = f.direction((0.0,  1.0, 0.0))
od_nx = f.direction((-1.0, 0.0, 0.0))
od_ny = f.direction((0.0, -1.0, 0.0))

oln_b = f.line(op0, f.vector(od_px, 20.0))
oln_r = f.line(op1, f.vector(od_py, 20.0))
oln_t = f.line(op2, f.vector(od_nx, 20.0))
oln_l = f.line(op3, f.vector(od_ny, 20.0))

oec_b = f._emit_raw(f"EDGE_CURVE('oe_b',#{ov0.eid},#{ov1.eid},#{oln_b.eid},.T.)")
oec_r = f._emit_raw(f"EDGE_CURVE('oe_r',#{ov1.eid},#{ov2.eid},#{oln_r.eid},.T.)")
oec_t = f._emit_raw(f"EDGE_CURVE('oe_t',#{ov2.eid},#{ov3.eid},#{oln_t.eid},.T.)")
oec_l = f._emit_raw(f"EDGE_CURVE('oe_l',#{ov3.eid},#{ov0.eid},#{oln_l.eid},.T.)")

ooe_b = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{oec_b.eid},.T.)")
ooe_r = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{oec_r.eid},.T.)")
ooe_t = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{oec_t.eid},.T.)")
ooe_l = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{oec_l.eid},.T.)")

outer_loop = f._emit_raw(
    f"EDGE_LOOP('outer_loop',"
    f"(#{ooe_b.eid},#{ooe_r.eid},#{ooe_t.eid},#{ooe_l.eid}))"
)
fob = f._emit_raw(f"FACE_OUTER_BOUND('',#{outer_loop.eid},.T.)")

# ── Inner wire: 6×6 at (7,7)-(13,13), traversed CCW (WRONG for hole) ─────────
# CCW traversal: bottom→right→top→left (same as outer), yields negative area for hole
ip0 = f.cartesian_point((7.0,  7.0,  0.0))
ip1 = f.cartesian_point((13.0, 7.0,  0.0))
ip2 = f.cartesian_point((13.0, 13.0, 0.0))
ip3 = f.cartesian_point((7.0,  13.0, 0.0))

iv0 = f._emit_raw(f"VERTEX_POINT('',#{ip0.eid})")
iv1 = f._emit_raw(f"VERTEX_POINT('',#{ip1.eid})")
iv2 = f._emit_raw(f"VERTEX_POINT('',#{ip2.eid})")
iv3 = f._emit_raw(f"VERTEX_POINT('',#{ip3.eid})")

# CCW order: (7,7)→(13,7)→(13,13)→(7,13)→back — same winding as outer (WRONG for hole)
iln_b = f.line(ip0, f.vector(od_px, 6.0))
iln_r = f.line(ip1, f.vector(od_py, 6.0))
iln_t = f.line(ip2, f.vector(od_nx, 6.0))
iln_l = f.line(ip3, f.vector(od_ny, 6.0))

iec_b = f._emit_raw(f"EDGE_CURVE('ie_b',#{iv0.eid},#{iv1.eid},#{iln_b.eid},.T.)")
iec_r = f._emit_raw(f"EDGE_CURVE('ie_r',#{iv1.eid},#{iv2.eid},#{iln_r.eid},.T.)")
iec_t = f._emit_raw(f"EDGE_CURVE('ie_t',#{iv2.eid},#{iv3.eid},#{iln_t.eid},.T.)")
iec_l = f._emit_raw(f"EDGE_CURVE('ie_l',#{iv3.eid},#{iv0.eid},#{iln_l.eid},.T.)")

ioe_b = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{iec_b.eid},.T.)")
ioe_r = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{iec_r.eid},.T.)")
ioe_t = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{iec_t.eid},.T.)")
ioe_l = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{iec_l.eid},.T.)")

inner_loop = f._emit_raw(
    f"EDGE_LOOP('wrong_orient_inner',"
    f"(#{ioe_b.eid},#{ioe_r.eid},#{ioe_t.eid},#{ioe_l.eid}))"
)
# .T. = CCW traversal for inner wire (WRONG — produces negative signed area)
fb = f._emit_raw(f"FACE_BOUND('',#{inner_loop.eid},.T.)")

af = f._emit_raw(
    f"ADVANCED_FACE('neg_area_inner_face',(#{fob.eid},#{fb.eid}),#{plane.eid},.T.)"
)

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',( #{af.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa166.stp")
