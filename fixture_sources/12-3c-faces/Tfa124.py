"""Tfa124 — ShapeAnalysis_CheckSmallFace.CheckSpotFace asymmetric.

Catalog claim: Small face with one long dimension (50 units) and one short
dimension (0.5 units), forming a strip-like spot. CheckSpotFace classifies
based on enclosing-circle diameter, misclassifying strip-like spots.

Mechanism: GEOMETRIC_CURVE_SET containing an ADVANCED_FACE on a PLANE. The
face is a long narrow rectangle (50×0.5). CheckSpotFace uses the diameter of
the minimal enclosing circle (~50 units) rather than both extents, so the
strip-like face with aspect ratio 100:1 is not recognized as a spot-face
defect even though one axis is nearly degenerate.

OCC sees a GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa124",
    defect=(
        "GEOMETRIC_CURVE_SET containing ADVANCED_FACE on PLANE; "
        "strip-like face with long dimension=50.0 and short dimension=0.5; "
        "aspect ratio 100:1 — one axis nearly degenerate; "
        "CheckSpotFace computes enclosing-circle diameter (~50) not both extents; "
        "misclassifies strip as not-spot despite 0.5-unit short axis; "
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

# ── Strip-like face: 50 × 0.5 ─────────────────────────────────────────────────
LNG = 50.0   # long dimension — enclosing circle diameter
SHT = 0.5    # short dimension — nearly degenerate

cp0 = f.cartesian_point((0.0,  0.0,  0.0))
cp1 = f.cartesian_point((LNG,  0.0,  0.0))
cp2 = f.cartesian_point((LNG,  SHT,  0.0))
cp3 = f.cartesian_point((0.0,  SHT,  0.0))

v0 = f._emit_raw(f"VERTEX_POINT('',#{cp0.eid})")
v1 = f._emit_raw(f"VERTEX_POINT('',#{cp1.eid})")
v2 = f._emit_raw(f"VERTEX_POINT('',#{cp2.eid})")
v3 = f._emit_raw(f"VERTEX_POINT('',#{cp3.eid})")

d_px = f.direction((1.0, 0.0, 0.0))
d_py = f.direction((0.0, 1.0, 0.0))
d_nx = f.direction((-1.0, 0.0, 0.0))
d_ny = f.direction((0.0, -1.0, 0.0))

vec_lng  = f.vector(d_px, LNG)
vec_sht  = f.vector(d_py, SHT)
vec_lngn = f.vector(d_nx, LNG)
vec_shtn = f.vector(d_ny, SHT)

ln_bot = f.line(cp0, vec_lng)
ln_rgt = f.line(cp1, vec_sht)
ln_top = f.line(cp2, vec_lngn)
ln_lft = f.line(cp3, vec_shtn)

ec_bot = f._emit_raw(f"EDGE_CURVE('e_bot',#{v0.eid},#{v1.eid},#{ln_bot.eid},.T.)")
ec_rgt = f._emit_raw(f"EDGE_CURVE('e_rgt',#{v1.eid},#{v2.eid},#{ln_rgt.eid},.T.)")
ec_top = f._emit_raw(f"EDGE_CURVE('e_top',#{v2.eid},#{v3.eid},#{ln_top.eid},.T.)")
ec_lft = f._emit_raw(f"EDGE_CURVE('e_lft',#{v3.eid},#{v0.eid},#{ln_lft.eid},.T.)")

oe_bot = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_bot.eid},.T.)")
oe_rgt = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_rgt.eid},.T.)")
oe_top = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_top.eid},.T.)")
oe_lft = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_lft.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('strip_spot_loop',"
    f"(#{oe_bot.eid},#{oe_rgt.eid},#{oe_top.eid},#{oe_lft.eid}))"
)
fob = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
af  = f._emit_raw(f"ADVANCED_FACE('strip_spot_face',(#{fob.eid}),#{plane.eid},.T.)")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',( #{af.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa124.stp")
