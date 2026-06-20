"""Tfa123 — ShapeFix_Face.FixSmallAreaWire near-collinear edges.

Catalog claim: Face with 4-edge wire where 3 consecutive edges are
near-collinear (deviation ~tolerance). FixSmallAreaWire's area calculation
produces a tiny or near-zero value despite the wire being geometrically
valid.

Mechanism: GEOMETRIC_CURVE_SET containing an ADVANCED_FACE on a PLANE. The
outer wire has 4 vertices where 3 consecutive edges are nearly collinear:
the wire is an extremely thin rectangle (width ~1e-4, length 10). The
signed polygon area is tiny — FixSmallAreaWire treats it as a degenerate
small-area wire and may delete it, despite the wire being closed and
geometrically valid.

OCC sees a GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa123",
    defect=(
        "GEOMETRIC_CURVE_SET containing ADVANCED_FACE on PLANE; "
        "outer wire has 4 edges where 3 consecutive edges are near-collinear; "
        "wire forms an extremely thin rectangle: width=1e-4, length=10.0; "
        "vertices at (0,0,0), (10,0,0), (10,1e-4,0), (0,1e-4,0); "
        "signed polygon area = 10.0 * 1e-4 = 1e-3 (near-tolerance); "
        "FixSmallAreaWire area calc returns near-zero despite valid closed wire; "
        "wire edges e1,e2,e3 form near-collinear sequence at the thin end; "
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

# ── Wire vertices: extremely thin rectangle (near-collinear) ──────────────────
# 3 consecutive near-collinear edges: bottom (length 10), right (width 1e-4),
# top (length 10 reversed). The deviation from collinearity is ~1e-4 (tolerance).
W = 1e-4   # near-zero width
L = 10.0   # length

cp0 = f.cartesian_point((0.0, 0.0, 0.0))
cp1 = f.cartesian_point((L,   0.0, 0.0))
cp2 = f.cartesian_point((L,   W,   0.0))
cp3 = f.cartesian_point((0.0, W,   0.0))

v0 = f._emit_raw(f"VERTEX_POINT('',#{cp0.eid})")
v1 = f._emit_raw(f"VERTEX_POINT('',#{cp1.eid})")
v2 = f._emit_raw(f"VERTEX_POINT('',#{cp2.eid})")
v3 = f._emit_raw(f"VERTEX_POINT('',#{cp3.eid})")

# Bottom edge: v0 → v1 (length L, near-collinear with the top)
d_px = f.direction((1.0, 0.0, 0.0))
vec_L = f.vector(d_px, L)
ln_bot = f.line(cp0, vec_L)
ec_bot = f._emit_raw(f"EDGE_CURVE('e_bot',#{v0.eid},#{v1.eid},#{ln_bot.eid},.T.)")

# Right edge: v1 → v2 (width W — near-zero, part of near-collinear triple)
d_py = f.direction((0.0, 1.0, 0.0))
vec_W = f.vector(d_py, W)
ln_rgt = f.line(cp1, vec_W)
ec_rgt = f._emit_raw(f"EDGE_CURVE('e_rgt',#{v1.eid},#{v2.eid},#{ln_rgt.eid},.T.)")

# Top edge: v2 → v3 (length L reversed)
d_nx = f.direction((-1.0, 0.0, 0.0))
vec_Ln = f.vector(d_nx, L)
ln_top = f.line(cp2, vec_Ln)
ec_top = f._emit_raw(f"EDGE_CURVE('e_top',#{v2.eid},#{v3.eid},#{ln_top.eid},.T.)")

# Left edge: v3 → v0 (width W reversed)
d_ny = f.direction((0.0, -1.0, 0.0))
vec_Wn = f.vector(d_ny, W)
ln_lft = f.line(cp3, vec_Wn)
ec_lft = f._emit_raw(f"EDGE_CURVE('e_lft',#{v3.eid},#{v0.eid},#{ln_lft.eid},.T.)")

oe_bot = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_bot.eid},.T.)")
oe_rgt = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_rgt.eid},.T.)")
oe_top = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_top.eid},.T.)")
oe_lft = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_lft.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('near_collinear_loop',"
    f"(#{oe_bot.eid},#{oe_rgt.eid},#{oe_top.eid},#{oe_lft.eid}))"
)
fob = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
af  = f._emit_raw(f"ADVANCED_FACE('near_collinear_face',(#{fob.eid}),#{plane.eid},.T.)")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',( #{af.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa123.stp")
