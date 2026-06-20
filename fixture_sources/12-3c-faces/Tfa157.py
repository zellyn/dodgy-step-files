"""Tfa157 — ShapeAnalysis_CheckSmallFace.CheckPin extreme-axis-pin.

Catalog claim: Pin face with 1000x aspect ratio (1000mm × 1mm). CheckPin's
threshold calculation overflows when processing extreme aspect ratios on thin
axis pins.

Mechanism: GEOMETRIC_CURVE_SET containing an ADVANCED_FACE on a PLANE. The
face is a thin rectangle 1000mm × 1mm — aspect ratio 1000:1. CheckPin
computes width threshold using floating-point arithmetic that overflows (or
produces NaN/Inf) at this extreme aspect ratio, causing incorrect
classification of the pin face.

OCC sees a GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa157",
    defect=(
        "GEOMETRIC_CURVE_SET containing ADVANCED_FACE on PLANE; "
        "extreme aspect-ratio pin face: 1000mm × 1mm (ratio 1000:1); "
        "CheckPin threshold calculation overflows at extreme aspect ratio; "
        "width=1.0mm, length=1000.0mm — arithmetic overflow or NaN produced; "
        "face misclassified (not detected as pin) by CheckPin; "
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

# ── Extreme-ratio pin rectangle: 1000 × 1 ─────────────────────────────────────
LEN = 1000.0   # long axis (mm)
WID = 1.0      # thin axis (mm) — aspect ratio 1000:1

cp0 = f.cartesian_point((0.0,  0.0,  0.0))
cp1 = f.cartesian_point((LEN,  0.0,  0.0))
cp2 = f.cartesian_point((LEN,  WID,  0.0))
cp3 = f.cartesian_point((0.0,  WID,  0.0))

v0 = f._emit_raw(f"VERTEX_POINT('',#{cp0.eid})")
v1 = f._emit_raw(f"VERTEX_POINT('',#{cp1.eid})")
v2 = f._emit_raw(f"VERTEX_POINT('',#{cp2.eid})")
v3 = f._emit_raw(f"VERTEX_POINT('',#{cp3.eid})")

d_px = f.direction((1.0, 0.0, 0.0))
d_py = f.direction((0.0, 1.0, 0.0))
d_nx = f.direction((-1.0, 0.0, 0.0))
d_ny = f.direction((0.0, -1.0, 0.0))

ln_bot = f.line(cp0, f.vector(d_px, LEN))
ln_rgt = f.line(cp1, f.vector(d_py, WID))
ln_top = f.line(cp2, f.vector(d_nx, LEN))
ln_lft = f.line(cp3, f.vector(d_ny, WID))

ec_bot = f._emit_raw(f"EDGE_CURVE('e_bot',#{v0.eid},#{v1.eid},#{ln_bot.eid},.T.)")
ec_rgt = f._emit_raw(f"EDGE_CURVE('e_rgt',#{v1.eid},#{v2.eid},#{ln_rgt.eid},.T.)")
ec_top = f._emit_raw(f"EDGE_CURVE('e_top',#{v2.eid},#{v3.eid},#{ln_top.eid},.T.)")
ec_lft = f._emit_raw(f"EDGE_CURVE('e_lft',#{v3.eid},#{v0.eid},#{ln_lft.eid},.T.)")

oe_bot = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_bot.eid},.T.)")
oe_rgt = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_rgt.eid},.T.)")
oe_top = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_top.eid},.T.)")
oe_lft = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_lft.eid},.T.)")

loop = f._emit_raw(
    f"EDGE_LOOP('extreme_pin_loop',"
    f"(#{oe_bot.eid},#{oe_rgt.eid},#{oe_top.eid},#{oe_lft.eid}))"
)
fob = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
af  = f._emit_raw(f"ADVANCED_FACE('extreme_pin_face',(#{fob.eid}),#{plane.eid},.T.)")

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',( #{af.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa157.stp")
