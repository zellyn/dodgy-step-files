"""Pmi013 — Counterbore/countersink emitted as separate dimensions with no compound link.

Catalog claim: AP242 Ed.1 lacks compound-feature semantics. Workaround: emit
counterbore as two unrelated dimensions; countersink adds a third (angle). No
relationship ties them as one feature, so compound holes become plain holes on
round-trip.

Reproducer recipe: Three DIMENSIONAL_SIZE instances (bore diameter, cbore
diameter, cbore depth) and three SHAPE_ASPECTs with no
geometric_tolerance_relationship tying them.

Byte assertions:
  count_entity_def(b'DIMENSIONAL_SIZE') == 3
  count_entity_def(b'SHAPE_ASPECT') == 3
  contains(b'PLUS_MINUS_TOLERANCE')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi013",
    defect=(
        "counterbore hole emitted as three unrelated DIMENSIONAL_SIZE entities "
        "(bore diam, cbore diam, cbore depth) with three SHAPE_ASPECTs and no "
        "compound-feature relationship; SolidWorks Hole Wizard / Onshape thread "
        "features become plain holes on round-trip; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT

# Three shape aspects: one per constituent dimension of the counterbore.
asp_bore = f._emit_raw("SHAPE_ASPECT('through_bore','',#9055,.T.)")
asp_cbore_diam = f._emit_raw("SHAPE_ASPECT('cbore_diameter','',#9055,.T.)")
asp_cbore_depth = f._emit_raw("SHAPE_ASPECT('cbore_depth','',#9055,.T.)")

# ── Through-bore diameter: Ø6.0 ± 0.05 mm ────────────────────────────────────
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

# ── Counterbore diameter: Ø10.0 mm ───────────────────────────────────────────
ds_cbore_diam = f._emit_raw(
    f"DIMENSIONAL_SIZE(#{asp_cbore_diam.eid},'cbore_diameter')"
)
mri_cbore_diam = f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('nominal',LENGTH_MEASURE(10.0),#9056)"
)

# ── Counterbore depth: 4.0 mm ────────────────────────────────────────────────
ds_cbore_depth = f._emit_raw(
    f"DIMENSIONAL_SIZE(#{asp_cbore_depth.eid},'cbore_depth')"
)
mri_cbore_depth = f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('nominal',LENGTH_MEASURE(4.0),#9056)"
)

# Intentionally no GEOMETRIC_TOLERANCE_RELATIONSHIP or compound-hole entity
# linking the three DIMENSIONAL_SIZE instances — that is the defect.
