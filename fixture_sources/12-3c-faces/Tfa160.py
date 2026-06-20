"""Tfa160 — ShapeFix_Face.FixWiresTwoCoincEdges loop-inside-loop.

Catalog claim: Face with inner wire (hole) fully inside outer wire; inner
wire's bottom edge is geometrically coincident with outer wire's bottom edge.
FixWiresTwoCoincEdges detects the coincidence but cannot resolve ownership.

Mechanism: GEOMETRIC_CURVE_SET containing an ADVANCED_FACE on a PLANE. The
outer wire is a 10×10 rectangle at (0,0)-(10,10). The inner wire is a 4×4
rectangle at (3,0)-(7,4), so its bottom edge at y=0 is geometrically
coincident with the outer wire's bottom edge (both lie on y=0 between x=3
and x=7). FixWiresTwoCoincEdges detects this coincident-edge situation but
cannot resolve which wire should own the shared geometry.

OCC sees a GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa160",
    defect=(
        "GEOMETRIC_CURVE_SET containing ADVANCED_FACE on PLANE; "
        "outer wire: 10×10 rectangle (0,0)-(10,10); "
        "inner wire: 4×4 rectangle (3,0)-(7,4); "
        "inner wire bottom edge at y=0 is geometrically coincident with outer wire bottom edge segment; "
        "FixWiresTwoCoincEdges detects coincidence but cannot resolve wire ownership; "
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

# ── Outer wire: 10×10 rectangle (0,0)-(10,10) ────────────────────────────────
op0 = f.cartesian_point((0.0,  0.0,  0.0))
op1 = f.cartesian_point((10.0, 0.0,  0.0))
op2 = f.cartesian_point((10.0, 10.0, 0.0))
op3 = f.cartesian_point((0.0,  10.0, 0.0))

ov0 = f._emit_raw(f"VERTEX_POINT('',#{op0.eid})")
ov1 = f._emit_raw(f"VERTEX_POINT('',#{op1.eid})")
ov2 = f._emit_raw(f"VERTEX_POINT('',#{op2.eid})")
ov3 = f._emit_raw(f"VERTEX_POINT('',#{op3.eid})")

od_px = f.direction((1.0,  0.0, 0.0))
od_py = f.direction((0.0,  1.0, 0.0))
od_nx = f.direction((-1.0, 0.0, 0.0))
od_ny = f.direction((0.0, -1.0, 0.0))

oln_b = f.line(op0, f.vector(od_px, 10.0))
oln_r = f.line(op1, f.vector(od_py, 10.0))
oln_t = f.line(op2, f.vector(od_nx, 10.0))
oln_l = f.line(op3, f.vector(od_ny, 10.0))

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

# ── Inner wire: 4×4 at (3,0)-(7,4) ──────────────────────────────────────────
# Bottom edge at y=0 is coincident with outer wire's bottom edge (y=0, x=3..7)
ip0 = f.cartesian_point((3.0, 0.0, 0.0))
ip1 = f.cartesian_point((7.0, 0.0, 0.0))
ip2 = f.cartesian_point((7.0, 4.0, 0.0))
ip3 = f.cartesian_point((3.0, 4.0, 0.0))

iv0 = f._emit_raw(f"VERTEX_POINT('',#{ip0.eid})")
iv1 = f._emit_raw(f"VERTEX_POINT('',#{ip1.eid})")
iv2 = f._emit_raw(f"VERTEX_POINT('',#{ip2.eid})")
iv3 = f._emit_raw(f"VERTEX_POINT('',#{ip3.eid})")

# inner bottom edge at y=0 — coincident with outer bottom edge
iln_b = f.line(ip0, f.vector(od_px, 4.0))
iln_r = f.line(ip1, f.vector(od_py, 4.0))
iln_t = f.line(ip2, f.vector(od_nx, 4.0))
iln_l = f.line(ip3, f.vector(od_ny, 4.0))

iec_b = f._emit_raw(f"EDGE_CURVE('ie_b',#{iv0.eid},#{iv1.eid},#{iln_b.eid},.T.)")
iec_r = f._emit_raw(f"EDGE_CURVE('ie_r',#{iv1.eid},#{iv2.eid},#{iln_r.eid},.T.)")
iec_t = f._emit_raw(f"EDGE_CURVE('ie_t',#{iv2.eid},#{iv3.eid},#{iln_t.eid},.T.)")
iec_l = f._emit_raw(f"EDGE_CURVE('ie_l',#{iv3.eid},#{iv0.eid},#{iln_l.eid},.T.)")

ioe_b = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{iec_b.eid},.T.)")
ioe_r = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{iec_r.eid},.T.)")
ioe_t = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{iec_t.eid},.T.)")
ioe_l = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{iec_l.eid},.T.)")

inner_loop = f._emit_raw(
    f"EDGE_LOOP('inner_coinc_loop',"
    f"(#{ioe_b.eid},#{ioe_r.eid},#{ioe_t.eid},#{ioe_l.eid}))"
)
# Inner hole: .F. = CW traversal (correct for a hole)
fb = f._emit_raw(f"FACE_BOUND('',#{inner_loop.eid},.F.)")

af = f._emit_raw(
    f"ADVANCED_FACE('coinc_edge_face',(#{fob.eid},#{fb.eid}),#{plane.eid},.T.)"
)

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',( #{af.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa160.stp")
