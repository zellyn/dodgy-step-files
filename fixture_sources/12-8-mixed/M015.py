"""M015 — Tessellated PMI placement: third coordinate must be 0 in tessellated_geometric_set
(repositioned form preferred).

Catalog claim: For efficiency, tessellated annotation sets should be combined with
repositioned_tessellated_item so that the coordinates_list entries have z=0
(annotation lies in its own 2D plane) and the placement axis carries the 3D
position. Writers that omit the repositioned form emit absolute 3D coordinates
with z≈10 throughout; readers that require z=0 reject.

Reproducer recipe: Tessellated annotation in plane at z=10. Either emit absolute
3D coords (z≈10 throughout), or use repositioned_tessellated_item with z=0 in
coords plus an axis at z=10.

Byte assertions:
  contains(b'TESSELLATED_GEOMETRIC_SET')
  contains(b'10.0)')
  contains(b'annot_coords_absolute')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M015",
    schema="AP242",
    defect=(
        "GEOMETRIC_CURVE_SET containing TESSELLATED_GEOMETRIC_SET with absolute 3D "
        "coordinates at z=10 throughout; "
        "non-repositioned form: PMI annotation emits absolute coords with z≈10.0 "
        "instead of using REPOSITIONED_TESSELLATED_ITEM with z=0 in coord list; "
        "PMI v4.1 §8.2 prefers the repositioned form: coordinates_list z=0 + axis at z=10; "
        "readers requiring z=0 in tessellated_geometric_set reject the absolute form; "
        "kernel must heal: accept both absolute and repositioned forms; "
        "writers must prefer the repositioned form; "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: tessellated PMI z != 0, annotation third coordinate nonzero, "
        "tessellated_geometric_set placement wrong, repositioned tessellated form preferred"
    ),
)

# ── Annotation at z=10: absolute coordinates, third coordinate nonzero ────────
# The defect: annotation coords have z=10.0 instead of z=0.0 (non-repositioned form).
# Byte assertion: contains(b'annot_coords_absolute')
# The name 'annot_coords_absolute' makes the byte assertion explicit.
# Byte assertion: contains(b'10.0)') — from coordinate entries ending in 10.0)
annot_coords = f._emit_raw(
    "COORDINATES_LIST('annot_coords_absolute',3,"
    "((0.,0.,10.0),(5.,0.,10.0),(5.,3.,10.0),(0.,3.,10.0)))"
)

# TESSELLATED_CURVE_SET for the annotation outline (a rectangular bounding box)
# Two line strips forming the rectangle at z=10
annot_curve = f._emit_raw(
    f"TESSELLATED_CURVE_SET('annot_outline',#{annot_coords.eid},"
    f"((0,1,2,3,0)))"
)

# TESSELLATED_GEOMETRIC_SET wraps the tessellated curve set
# Byte assertion: contains(b'TESSELLATED_GEOMETRIC_SET')
tgs = f._emit_raw(
    f"TESSELLATED_GEOMETRIC_SET('annotation_tgs',(#{annot_curve.eid}))"
)

# ── What the conformant repositioned form would look like (contrast) ──────────
# Conformant: COORDINATES_LIST with z=0, plus REPOSITIONED_TESSELLATED_ITEM
# with an axis at z=10 carrying the 3D placement.
# Here we emit it but mark it as the correct alternative — not the defect.
axis_orig = f.cartesian_point((0.0, 0.0, 10.0))
axis_zdir = f.direction((0.0, 0.0, 1.0))
axis_xdir = f.direction((1.0, 0.0, 0.0))
axis_plc  = f.axis2_placement_3d(axis_orig, axis_zdir, axis_xdir)

conformant_coords = f._emit_raw(
    "COORDINATES_LIST('annot_coords_repositioned',3,"
    "((0.,0.,0.),(5.,0.,0.),(5.,3.,0.),(0.,3.,0.)))"
)
conformant_curve = f._emit_raw(
    f"TESSELLATED_CURVE_SET('annot_outline_z0',#{conformant_coords.eid},"
    f"((0,1,2,3,0)))"
)
# REPOSITIONED_TESSELLATED_ITEM: wraps conformant_curve with axis at z=10
repositioned = f._emit_raw(
    f"REPOSITIONED_TESSELLATED_ITEM('',#{conformant_curve.eid},#{axis_plc.eid})"
)

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty ───────────────
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('tess-pmi-z-nonzero-absolute',"
    f"(#{tgs.eid},#{repositioned.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M015.stp")
