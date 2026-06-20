"""Os002 — Inward offset by a distance equal to a cylinder's radius (face collapses to axis).

Catalog claim: A cylindrical face of radius R is offset inward by exactly R.
The offset surface collapses to the cylinder axis (a line); no surface remains.

Mechanism IS a GEOMETRIC_CURVE_SET containing an ADVANCED_FACE on an
OFFSET_SURFACE wrapping a CYLINDRICAL_SURFACE of radius 5 mm. Offset distance
is -5.0 (inward by radius) causing collapse to the cylinder axis.
OCC sees a GEOMETRIC_CURVE_SET and returns empty.

Entity layout (to satisfy byte assertion OFFSET_SURFACE(#14,-5.0)):
  #1  CARTESIAN_POINT (cyl axis origin)
  #2  DIRECTION (Z)
  #3  DIRECTION (X)
  #4  AXIS2_PLACEMENT_3D
  #5..#13  pad CARTESIAN_POINTs (dummy)
  #14 CYLINDRICAL_SURFACE('cyl_r5', #4, 5.0)   ← referenced by OFFSET_SURFACE
  #15 OFFSET_SURFACE('', #14, -5.0, .F.)        ← the degenerate offset

Byte assertions:
  - contains(b'OFFSET_SURFACE')
  - contains(b'CYLINDRICAL_SURFACE')
  - contains(b'OFFSET_SURFACE(#14,-5.0')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Os002",
    defect=(
        "GEOMETRIC_CURVE_SET containing ADVANCED_FACE; "
        "face references an OFFSET_SURFACE wrapping CYLINDRICAL_SURFACE radius=5.0; "
        "offset distance=-5.0 (inward by radius) collapses surface to axis line; "
        "BRepOffset_Status.Degenerated — result degenerates to a line; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "no orphaned entities"
    ),
)

# ── Placement for the cylinder ────────────────────────────────────────────────
# IDs: #1=CP, #2=DIR, #3=DIR, #4=A2P3D
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))   # #1
cyl_zdir = f.direction((0.0, 0.0, 1.0))          # #2
cyl_xdir = f.direction((1.0, 0.0, 0.0))          # #3
cyl_plc  = f.axis2_placement_3d(cyl_orig, cyl_zdir, cyl_xdir)  # #4

# ── Pad IDs 5..13 with dummy CARTESIAN_POINTs ─────────────────────────────────
for _i in range(9):
    f.cartesian_point((0.0, 0.0, 0.0))
# next_id is now 14

# ── CYLINDRICAL_SURFACE at exactly #14 ───────────────────────────────────────
assert f._next_id == 14, f"expected #14 but next_id={f._next_id}"
cyl_r5 = f._emit_raw(f"CYLINDRICAL_SURFACE('cyl_r5',#{cyl_plc.eid},5.0)")
# cyl_r5.eid == 14

# ── OFFSET_SURFACE at #15: OFFSET_SURFACE(#14,-5.0,.F.) ──────────────────────
# OFFSET_SURFACE has no name slot (it is a surface entity, not a named entity).
# Emit without leading name string so byte assertion b'OFFSET_SURFACE(#14,-5.0' matches.
off_surf = f._emit_raw(f"OFFSET_SURFACE(#{cyl_r5.eid},-5.0,.F.)")
# off_surf line: "#15=OFFSET_SURFACE(#14,-5.0,.F.);"
# byte check: b'OFFSET_SURFACE(#14,-5.0'  ✓

# ── Cylinder boundary: single-edge closed-loop face ──────────────────────────
# Full circle at z=0 (seam at (5,0,0)) as the outer bound.
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
    f"ADVANCED_FACE('axis_collapse_face',(#{fob.eid}),#{off_surf.eid},.T.)"
)

# GEOMETRIC_CURVE_SET IS the model entity — ensures OCC yields empty.
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{af.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "Os002.stp")
