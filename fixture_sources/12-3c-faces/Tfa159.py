"""Tfa159 — ShapeAnalysis_CheckSmallFace.CheckStripFace cylindrical-strip.

Catalog claim: Strip face on cylindrical surface (narrow angular band, full
height). CheckStripFace's aspect ratio uses parametric domain (0–2π, bounded
v), which doesn't reflect true 3D strip geometry in 3D arc length.

Mechanism: GEOMETRIC_CURVE_SET containing an ADVANCED_FACE on a
CYLINDRICAL_SURFACE. The face spans a narrow angular band (5° = 0.0873 rad)
but the full height of the cylinder (50mm). In parametric space the u-extent
is 0.0873 and v-extent is 50, so parametric aspect ratio is 50/0.0873 ≈ 573.
The true 3D arc length of the narrow strip is radius × angle = 10 × 0.0873
≈ 0.873mm, giving a 3D aspect ratio of 50/0.873 ≈ 57. CheckStripFace uses
the parametric width (0.0873) not the 3D arc length (0.873), so it
miscomputes the aspect ratio.

OCC sees a GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'ADVANCED_FACE')
  - contains(b'CYLINDRICAL_SURFACE')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa159",
    defect=(
        "GEOMETRIC_CURVE_SET containing ADVANCED_FACE on CYLINDRICAL_SURFACE; "
        "narrow angular strip: 5 degrees (0.0873 rad) wide, 50mm tall; "
        "radius=10mm so 3D arc width=0.873mm; "
        "CheckStripFace uses parametric width (0.0873) not 3D arc length (0.873); "
        "aspect ratio miscomputed in parametric domain vs true 3D geometry; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "no orphaned entities"
    ),
)

import math as _math

RADIUS = 10.0
HEIGHT = 50.0
ANGLE  = 5.0 * _math.pi / 180.0   # 5 degrees in radians

# ── Cylindrical surface ────────────────────────────────────────────────────────
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_plc  = f.axis2_placement_3d(cyl_orig, cyl_zdir, cyl_xdir)
cyl      = f.cylindrical_surface(cyl_plc, RADIUS)

# ── Four corners of the strip in 3D ───────────────────────────────────────────
# u=0 edge (left): x=R, y=0
# u=ANGLE edge (right): x=R*cos(ANGLE), y=R*sin(ANGLE)
x0, y0 = RADIUS, 0.0
x1, y1 = RADIUS * _math.cos(ANGLE), RADIUS * _math.sin(ANGLE)

cp_bl = f.cartesian_point((x0, y0, 0.0))       # bottom-left
cp_br = f.cartesian_point((x1, y1, 0.0))       # bottom-right
cp_tr = f.cartesian_point((x1, y1, HEIGHT))    # top-right
cp_tl = f.cartesian_point((x0, y0, HEIGHT))    # top-left

vbl = f._emit_raw(f"VERTEX_POINT('',#{cp_bl.eid})")
vbr = f._emit_raw(f"VERTEX_POINT('',#{cp_br.eid})")
vtr = f._emit_raw(f"VERTEX_POINT('',#{cp_tr.eid})")
vtl = f._emit_raw(f"VERTEX_POINT('',#{cp_tl.eid})")

# ── Bottom edge: arc from bl to br at z=0 ─────────────────────────────────────
arc_bot_orig = f.cartesian_point((0.0, 0.0, 0.0))
arc_bot_zdir = f.direction((0.0, 0.0, -1.0))   # .T. orientation = CW = rightward at bottom
arc_bot_xdir = f.direction((1.0, 0.0, 0.0))
arc_bot_plc  = f.axis2_placement_3d(arc_bot_orig, arc_bot_zdir, arc_bot_xdir)
arc_bot      = f.circle(arc_bot_plc, RADIUS)
ec_bot = f._emit_raw(f"EDGE_CURVE('e_bot',#{vbl.eid},#{vbr.eid},#{arc_bot.eid},.T.)")

# ── Right edge: vertical line from br to tr ────────────────────────────────────
d_up   = f.direction((0.0, 0.0, 1.0))
ln_rgt = f.line(cp_br, f.vector(d_up, HEIGHT))
ec_rgt = f._emit_raw(f"EDGE_CURVE('e_rgt',#{vbr.eid},#{vtr.eid},#{ln_rgt.eid},.T.)")

# ── Top edge: arc from tr to tl at z=HEIGHT ───────────────────────────────────
arc_top_orig = f.cartesian_point((0.0, 0.0, HEIGHT))
arc_top_zdir = f.direction((0.0, 0.0, 1.0))    # .T. orientation = CCW = leftward at top
arc_top_xdir = f.direction((1.0, 0.0, 0.0))
arc_top_plc  = f.axis2_placement_3d(arc_top_orig, arc_top_zdir, arc_top_xdir)
arc_top      = f.circle(arc_top_plc, RADIUS)
ec_top = f._emit_raw(f"EDGE_CURVE('e_top',#{vtr.eid},#{vtl.eid},#{arc_top.eid},.T.)")

# ── Left edge: vertical line from tl to bl ────────────────────────────────────
d_dn   = f.direction((0.0, 0.0, -1.0))
ln_lft = f.line(cp_tl, f.vector(d_dn, HEIGHT))
ec_lft = f._emit_raw(f"EDGE_CURVE('e_lft',#{vtl.eid},#{vbl.eid},#{ln_lft.eid},.T.)")

oe_bot = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_bot.eid},.T.)")
oe_rgt = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_rgt.eid},.T.)")
oe_top = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_top.eid},.T.)")
oe_lft = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_lft.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('strip_loop',"
    f"(#{oe_bot.eid},#{oe_rgt.eid},#{oe_top.eid},#{oe_lft.eid}))"
)
fob = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
af  = f._emit_raw(f"ADVANCED_FACE('cyl_strip_face',(#{fob.eid}),#{cyl.eid},.T.)")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',( #{af.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa159.stp")
