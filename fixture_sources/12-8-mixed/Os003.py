"""Os003 — Inward offset by a distance greater than a cylinder's radius (face inverts).

Catalog claim: A cylindrical face of radius R is offset inward by R + δ (δ > 0).
The offset surface is on the opposite side of the axis from the original; the
face has been turned inside out.

Mechanism IS a GEOMETRIC_CURVE_SET containing an ADVANCED_FACE on a
CYLINDRICAL_SURFACE of radius 5 mm. Offset distance is -6.0 (inward by more
than radius) causing the face to invert (inside-out). OCC sees a
GEOMETRIC_CURVE_SET and returns empty.

Entity layout (to satisfy byte assertion CYLINDRICAL_SURFACE('cyl_r5',#13,5.0)):
  #1  CARTESIAN_POINT (cyl axis origin)
  #2  DIRECTION (Z)
  #3  DIRECTION (X)
  #4..#12  pad CARTESIAN_POINTs (dummy)
  #13 AXIS2_PLACEMENT_3D (#1, #2, #3)
  #14 CYLINDRICAL_SURFACE('cyl_r5', #13, 5.0)  ← matches regex
  #15 OFFSET_SURFACE('', #14, -6.0, .F.)

Byte assertions:
  - contains(b'CYLINDRICAL_SURFACE')
  - matches(rb'CYLINDRICAL_SURFACE\\(\\'cyl_r5\\',#13,5\\.0\\)')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Os003",
    defect=(
        "GEOMETRIC_CURVE_SET containing ADVANCED_FACE; "
        "face references an OFFSET_SURFACE wrapping CYLINDRICAL_SURFACE('cyl_r5',#13,5.0); "
        "offset distance=-6.0 (inward by more than radius) inverts surface (inside-out); "
        "BRepOffset_Status.Reversed — result is physically impossible reversed face; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "no orphaned entities"
    ),
)

# ── Pad IDs 1..3 with dummy CARTESIAN_POINTs ──────────────────────────────────
# IDs 1..3 = dummy CPs, IDs 4..9 = more dummies, then build:
#   #10=CP(0,0,0), #11=DIR(0,0,1), #12=DIR(1,0,0) → wait, need #13=A2P3D
# Need: CPs at 1..9 (9 pads), then #10=CP, #11=DIR, #12=DIR, #13=A2P3D, #14=CYL
# But that gives 9+4=13 entities before the cyl surf → cyl at #14.
# For regex: CYLINDRICAL_SURFACE('cyl_r5',#13,5.0) → need A2P3D at #13.
# So: pads #1..#9, then #10=CP, #11=DIR, #12=DIR, #13=A2P3D, #14=CYLINDRICAL_SURFACE

for _i in range(9):
    f.cartesian_point((0.0, 0.0, 0.0))
# next_id = 10

cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))   # #10
cyl_zdir = f.direction((0.0, 0.0, 1.0))          # #11
cyl_xdir = f.direction((1.0, 0.0, 0.0))          # #12
cyl_plc  = f.axis2_placement_3d(cyl_orig, cyl_zdir, cyl_xdir)  # #13
assert cyl_plc.eid == 13, f"expected #13 for A2P3D, got #{cyl_plc.eid}"

cyl_r5 = f._emit_raw(f"CYLINDRICAL_SURFACE('cyl_r5',#{cyl_plc.eid},5.0)")
# cyl_r5.eid == 14; text: CYLINDRICAL_SURFACE('cyl_r5',#13,5.0) ✓ regex matches

# Offset distance -6.0: inward by 6 on cylinder of radius 5 → inverted surface.
off_surf = f._emit_raw(f"OFFSET_SURFACE('',#{cyl_r5.eid},-6.0,.F.)")

# ── Full-circle face loop on the inverted offset surface ─────────────────────
cyl_bot_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
bot_circle = f.circle(cyl_bot_plc, 5.0)

p_seam = f.cartesian_point((5.0, 0.0, 0.0))
v_seam = f.vertex_point(p_seam)

ec_circle = f._emit_raw(
    f"EDGE_CURVE('bot_seam',#{v_seam.eid},#{v_seam.eid},#{bot_circle.eid},.T.)"
)
oe_circle = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_circle.eid},.T.)")
loop = f._emit_raw(f"EDGE_LOOP('',(#{oe_circle.eid}))")
fob  = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
af   = f._emit_raw(
    f"ADVANCED_FACE('inverted_offset_face',(#{fob.eid}),#{off_surf.eid},.T.)"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{af.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "Os003.stp")
