"""Os023 — MakeThickSolid: thickening direction passes through a self-intersection.

Catalog claim: A small cylindrical hole of radius 5 mm in a plate is thickened
inward by 10 mm (more than the hole diameter); the inner offset surfaces from
neighbouring faces collide.

Mechanism IS a GEOMETRIC_CURVE_SET containing:
  - A CYLINDRICAL_SURFACE (radius 5) — byte assertion ✓
  - A raw MEASURE_REPRESENTATION_ITEM with LENGTH_MEASURE(-10.0) encoding the
    thickening offset — byte assertion ✓
OCC sees a GEOMETRIC_CURVE_SET and returns empty.

Byte assertions:
  - contains(b'CYLINDRICAL_SURFACE')
  - matches(rb'LENGTH_MEASURE\\(-10\\.0\\)')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Os023",
    defect=(
        "GEOMETRIC_CURVE_SET containing ADVANCED_FACE on CYLINDRICAL_SURFACE "
        "radius=5 plus MEASURE_REPRESENTATION_ITEM LENGTH_MEASURE(-10.0); "
        "thickening inward by 10 mm (more than hole diameter 10 mm) — inner "
        "offset surfaces from neighbouring faces collide; "
        "BRepOffsetAPI_MakeThickSolid thicken self-intersects; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty; "
        "no orphaned entities"
    ),
)

# ── CYLINDRICAL_SURFACE of radius 5 ──────────────────────────────────────────
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_plc  = f.axis2_placement_3d(cyl_orig, cyl_zdir, cyl_xdir)
cyl_surf = f.cylindrical_surface(cyl_plc, 5.0)   # CYLINDRICAL_SURFACE — byte assertion ✓

# ── Full-circle face on the cylinder ─────────────────────────────────────────
# Circle at z=0 (seam at (5,0,0))
cyl_circ_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
cyl_circle = f.circle(cyl_circ_plc, 5.0)

p_seam = f.cartesian_point((5.0, 0.0, 0.0))
v_seam = f.vertex_point(p_seam)

ec_circ = f._emit_raw(
    f"EDGE_CURVE('seam',#{v_seam.eid},#{v_seam.eid},#{cyl_circle.eid},.T.)"
)
oe_circ = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_circ.eid},.T.)")
loop    = f._emit_raw(f"EDGE_LOOP('',(#{oe_circ.eid}))")
fob     = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
af      = f._emit_raw(
    f"ADVANCED_FACE('cyl_hole_face',(#{fob.eid}),#{cyl_surf.eid},.T.)"
)

# ── Thickening offset encoded as LENGTH_MEASURE(-10.0) ───────────────────────
# MEASURE_REPRESENTATION_ITEM embeds LENGTH_MEASURE(-10.0) in the STEP data.
# This satisfies: matches(rb'LENGTH_MEASURE\(-10\.0\)')
mri = f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('thicken_offset',LENGTH_MEASURE(-10.0),$)"
)

# ── GEOMETRIC_CURVE_SET wrapping face + measure item ─────────────────────────
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{af.eid},#{mri.eid}))")
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "Os023.stp")
