"""Pmi055 — AP242 hole feature missing required attribute / inconsistent dims.

Catalog claim: round_hole / counterbore / countersink is missing depth /
diameter / tip_angle, OR counterbore/countersink diameter <= drill diameter,
OR counterbore depth >= drill depth.

Reproducer recipe: counterbore with counterbore_diameter < drill_diameter.

Byte assertions:
  count_entity_def(b'DIMENSIONAL_SIZE') == 4
  count_entity_def(b'SHAPE_ASPECT') == 3
  contains(b'PLUS_MINUS_TOLERANCE')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi055",
    defect=(
        "counterbore hole feature has inconsistent dimensions: counterbore_diameter "
        "< drill_diameter (4.0 < 6.0); AP242 requires counterbore diameter to exceed "
        "drill diameter; receivers must reject or warn; "
        "silently accepting geometrically impossible hole dimensions is forbidden; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT

# Three shape aspects: bore, cbore_diameter, cbore_depth.
asp_bore = f._emit_raw("SHAPE_ASPECT('through_bore','',#9055,.T.)")
asp_cbore_diam = f._emit_raw("SHAPE_ASPECT('cbore_diameter','',#9055,.T.)")
asp_cbore_depth = f._emit_raw("SHAPE_ASPECT('cbore_depth','',#9055,.T.)")

# ── Through-bore diameter: Ø6.0 ± 0.05 mm ─────────────────────────────────
ds_bore = f._emit_raw(f"DIMENSIONAL_SIZE(#{asp_bore.eid},'bore_diameter')")
mri_bore = f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('nominal',LENGTH_MEASURE(6.0),#9056)"
)
upper_bore = f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('upper',LENGTH_MEASURE(0.05),#9056)"
)
lower_bore = f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('lower',LENGTH_MEASURE(0.05),#9056)"
)
tol_bore = f._emit_raw(
    f"TOLERANCE_VALUE(#{upper_bore.eid},#{lower_bore.eid})"
)
f._emit_raw(f"PLUS_MINUS_TOLERANCE(#{tol_bore.eid},#{ds_bore.eid})")

# ── Counterbore diameter: Ø4.0 mm — DEFECT: 4.0 < 6.0 (drill diameter) ────
# AP242 requires cbore_diameter > drill_diameter; this fixture violates it.
ds_cbore_diam = f._emit_raw(
    f"DIMENSIONAL_SIZE(#{asp_cbore_diam.eid},'cbore_diameter')"
)
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('nominal',LENGTH_MEASURE(4.0),#9056)"
)

# ── Counterbore depth: 3.0 mm ───────────────────────────────────────────────
ds_cbore_depth = f._emit_raw(
    f"DIMENSIONAL_SIZE(#{asp_cbore_depth.eid},'cbore_depth')"
)
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('nominal',LENGTH_MEASURE(3.0),#9056)"
)

# Fourth DIMENSIONAL_SIZE: bore depth (satisfies count_entity_def == 4).
ds_bore_depth = f._emit_raw(
    f"DIMENSIONAL_SIZE(#{asp_bore.eid},'bore_depth')"
)
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('nominal',LENGTH_MEASURE(15.0),#9056)"
)
