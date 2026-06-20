"""Pmi032 — Datum target dimension equals zero.

Catalog claim: A placed_datum_target_feature carries a target diameter / target
length of 0. Receivers must emit a warning diagnostic; no degenerate target
should be silently emitted.

Reproducer recipe: placed_datum_target_feature with
target_diameter = LENGTH_MEASURE(0.0).

Byte assertions:
  contains(b'PLACED_DATUM_TARGET_FEATURE')
  contains(b'DATUM')
  contains(b'MEASURE_REPRESENTATION_ITEM')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi032",
    defect=(
        "PLACED_DATUM_TARGET_FEATURE has target_diameter encoded as "
        "LENGTH_MEASURE(0.0) via MEASURE_REPRESENTATION_ITEM; a zero-size datum "
        "target is degenerate — receivers must warn; silently accepting and emitting "
        "a degenerate target is forbidden; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT

# The datum feature shape aspect.
asp_datum = f._emit_raw("SHAPE_ASPECT('datum_feature_A','',#9055,.T.)")

# Datum entity linking the shape aspect.
datum = f._emit_raw(f"DATUM('A','',#{asp_datum.eid},.T.)")

# Defect: target_diameter = LENGTH_MEASURE(0.0) — zero-size datum target.
# MEASURE_REPRESENTATION_ITEM carries the dimension value.
zero_diam = f._emit_raw(
    f"MEASURE_REPRESENTATION_ITEM('target diameter',LENGTH_MEASURE(0.0),#9056)"
)

# PLACED_DATUM_TARGET_FEATURE referencing the datum and the zero-diameter measure.
# Arguments: name, description, of_shape, product_definitional, target_id, target_label
f._emit_raw(
    f"PLACED_DATUM_TARGET_FEATURE('A1','circle',#{asp_datum.eid},.T.,'1','A')"
)

# Attach the zero-diameter representation item to the feature via
# PROPERTY_DEFINITION / PROPERTY_DEFINITION_REPRESENTATION so that the
# MEASURE_REPRESENTATION_ITEM is reachable.
prop_def = f._emit_raw(
    f"PROPERTY_DEFINITION('target diameter','',#{asp_datum.eid})"
)
rep = f._emit_raw(
    f"REPRESENTATION('',(#{zero_diam.eid}),$)"
)
f._emit_raw(
    f"PROPERTY_DEFINITION_REPRESENTATION(#{prop_def.eid},#{rep.eid})"
)
