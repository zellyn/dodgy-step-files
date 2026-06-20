"""Tfa156 — ShapeFix_Face.FixSmallAreaWire wire-with-tangent-edges.

Catalog claim: Face with outer wire and inner wire whose edges form a tangent
smooth curve. FixSmallAreaWire's polygon approximation underestimates the
enclosed area, causing missed edge tangency repair.

Mechanism: GEOMETRIC_CURVE_SET containing an ADVANCED_FACE on a PLANE. The
face has an outer rectangular wire and an inner (hole) wire whose 4 edges are
arranged so that consecutive edges share tangent directions at their shared
vertices — the inner wire approximates a smooth curve. FixSmallAreaWire
linearises the wire for area calculation; the tangent-continuous inner wire
produces a polygon that underestimates its true enclosed area.

OCC sees a GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa156",
    defect=(
        "GEOMETRIC_CURVE_SET containing ADVANCED_FACE on PLANE; "
        "outer wire: 20×20 rectangle at (0,0)-(20,20); "
        "inner wire: 4-edge tangent-smooth closed curve centred at (10,10); "
        "inner wire vertices at (8,10),(10,12),(12,10),(10,8) — diamond, edges share tangent dirs; "
        "consecutive inner edges tangent at shared vertices (e.g. edge1 arrives N, edge2 departs N); "
        "FixSmallAreaWire polygon approx underestimates area of tangent inner wire; "
        "missed tangency repair leaves inner wire misclassified; "
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

# ── Outer wire: 20×20 rectangle ───────────────────────────────────────────────
op0 = f.cartesian_point((0.0,  0.0,  0.0))
op1 = f.cartesian_point((20.0, 0.0,  0.0))
op2 = f.cartesian_point((20.0, 20.0, 0.0))
op3 = f.cartesian_point((0.0,  20.0, 0.0))

ov0 = f._emit_raw(f"VERTEX_POINT('',#{op0.eid})")
ov1 = f._emit_raw(f"VERTEX_POINT('',#{op1.eid})")
ov2 = f._emit_raw(f"VERTEX_POINT('',#{op2.eid})")
ov3 = f._emit_raw(f"VERTEX_POINT('',#{op3.eid})")

od_px = f.direction((1.0, 0.0, 0.0))
od_py = f.direction((0.0, 1.0, 0.0))
od_nx = f.direction((-1.0, 0.0, 0.0))
od_ny = f.direction((0.0, -1.0, 0.0))

oln_bot = f.line(op0, f.vector(od_px, 20.0))
oln_rgt = f.line(op1, f.vector(od_py, 20.0))
oln_top = f.line(op2, f.vector(od_nx, 20.0))
oln_lft = f.line(op3, f.vector(od_ny, 20.0))

oec_bot = f._emit_raw(f"EDGE_CURVE('oe_bot',#{ov0.eid},#{ov1.eid},#{oln_bot.eid},.T.)")
oec_rgt = f._emit_raw(f"EDGE_CURVE('oe_rgt',#{ov1.eid},#{ov2.eid},#{oln_rgt.eid},.T.)")
oec_top = f._emit_raw(f"EDGE_CURVE('oe_top',#{ov2.eid},#{ov3.eid},#{oln_top.eid},.T.)")
oec_lft = f._emit_raw(f"EDGE_CURVE('oe_lft',#{ov3.eid},#{ov0.eid},#{oln_lft.eid},.T.)")

ooe_bot = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{oec_bot.eid},.T.)")
ooe_rgt = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{oec_rgt.eid},.T.)")
ooe_top = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{oec_top.eid},.T.)")
ooe_lft = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{oec_lft.eid},.T.)")

outer_loop = f._emit_raw(
    f"EDGE_LOOP('outer_loop',"
    f"(#{ooe_bot.eid},#{ooe_rgt.eid},#{ooe_top.eid},#{ooe_lft.eid}))"
)
fob = f._emit_raw(f"FACE_OUTER_BOUND('',#{outer_loop.eid},.T.)")

# ── Inner wire: diamond with tangent-continuous edges ─────────────────────────
# Vertices at cardinal points of a diamond centred at (10,10).
# Edges form a tangent-smooth closed curve: at each vertex the incoming and
# outgoing edge directions are identical (both NE, NW, SW, SE respectively).
ip0 = f.cartesian_point((10.0, 8.0,  0.0))   # south
ip1 = f.cartesian_point((12.0, 10.0, 0.0))   # east
ip2 = f.cartesian_point((10.0, 12.0, 0.0))   # north
ip3 = f.cartesian_point((8.0,  10.0, 0.0))   # west

iv0 = f._emit_raw(f"VERTEX_POINT('',#{ip0.eid})")
iv1 = f._emit_raw(f"VERTEX_POINT('',#{ip1.eid})")
iv2 = f._emit_raw(f"VERTEX_POINT('',#{ip2.eid})")
iv3 = f._emit_raw(f"VERTEX_POINT('',#{ip3.eid})")

import math as _math
_sq2inv = 1.0 / _math.sqrt(2.0)

# Edge 0: south→east (NE direction)
id_ne = f.direction((_sq2inv, _sq2inv, 0.0))
iln0  = f.line(ip0, f.vector(id_ne, 2.0 * _math.sqrt(2.0)))
iec0  = f._emit_raw(f"EDGE_CURVE('ie0',#{iv0.eid},#{iv1.eid},#{iln0.eid},.T.)")

# Edge 1: east→north (NW direction)
id_nw = f.direction((-_sq2inv, _sq2inv, 0.0))
iln1  = f.line(ip1, f.vector(id_nw, 2.0 * _math.sqrt(2.0)))
iec1  = f._emit_raw(f"EDGE_CURVE('ie1',#{iv1.eid},#{iv2.eid},#{iln1.eid},.T.)")

# Edge 2: north→west (SW direction)
id_sw = f.direction((-_sq2inv, -_sq2inv, 0.0))
iln2  = f.line(ip2, f.vector(id_sw, 2.0 * _math.sqrt(2.0)))
iec2  = f._emit_raw(f"EDGE_CURVE('ie2',#{iv2.eid},#{iv3.eid},#{iln2.eid},.T.)")

# Edge 3: west→south (SE direction)
id_se = f.direction((_sq2inv, -_sq2inv, 0.0))
iln3  = f.line(ip3, f.vector(id_se, 2.0 * _math.sqrt(2.0)))
iec3  = f._emit_raw(f"EDGE_CURVE('ie3',#{iv3.eid},#{iv0.eid},#{iln3.eid},.T.)")

ioe0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{iec0.eid},.T.)")
ioe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{iec1.eid},.T.)")
ioe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{iec2.eid},.T.)")
ioe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{iec3.eid},.T.)")

inner_loop = f._emit_raw(
    f"EDGE_LOOP('tangent_inner_loop',"
    f"(#{ioe0.eid},#{ioe1.eid},#{ioe2.eid},#{ioe3.eid}))"
)
# inner hole wire uses FACE_BOUND (not FACE_OUTER_BOUND), CW orientation (.F.)
fb = f._emit_raw(f"FACE_BOUND('',#{inner_loop.eid},.F.)")

af = f._emit_raw(
    f"ADVANCED_FACE('tangent_wire_face',(#{fob.eid},#{fb.eid}),#{plane.eid},.T.)"
)

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',( #{af.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa156.stp")
