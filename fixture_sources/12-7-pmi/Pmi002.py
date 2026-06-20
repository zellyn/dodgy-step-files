"""Pmi002 — Blank/hidden dimensions exported as semantic dimensions.

Catalog claim: a CAD user hides a dimension's value (keeps only extension
lines as visual aids). The writer emits both the real and the blank dimension
as full DIMENSIONAL_SIZE instances, inflating semantic-PMI counts and
producing phantom semantic content with no real toleranced value.

Byte assertions:
  count_entity_def(b'DIMENSIONAL_SIZE') == 2
  contains(b'blanked-width')
  count_entity_def(b'SHAPE_DIMENSION_REPRESENTATION') == 2

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi002",
    defect=(
        "blank dimension emitted as DIMENSIONAL_SIZE; "
        "two DIMENSIONAL_SIZE + two SHAPE_DIMENSION_REPRESENTATION instances; "
        "one is real, one is blank (blanked-width) — inflates semantic-PMI count; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in a GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
sdr = f.add_product_chain(gcs)
# After add_product_chain IDs are:
#   #9000 APPLICATION_CONTEXT
#   #9055 PRODUCT_DEFINITION_SHAPE
#   #9056 LENGTH_UNIT complex
#   #9060 GEOMETRIC_REPRESENTATION_CONTEXT complex

shape_asp = f._emit_raw(
    "SHAPE_ASPECT('width','external width',#9055,.T.)"
)

# Real dimensional_size with its SDR.
ds_real = f._emit_raw(f"DIMENSIONAL_SIZE(#{shape_asp.eid},'width')")
mri_real = f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('nominal',LENGTH_MEASURE(50.0),#9056)"
)
f._emit_raw(
    f"SHAPE_DIMENSION_REPRESENTATION('width_rep',(#{mri_real.eid}),#9060)"
)

# Defect: blank dimension still emitted as semantic DIMENSIONAL_SIZE.
# Writers must omit this; only extension lines belong in graphic presentation.
ds_blank = f._emit_raw(f"DIMENSIONAL_SIZE(#{shape_asp.eid},'blanked-width')")
mri_blank = f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('nominal',LENGTH_MEASURE(50.0),#9056)"
)
f._emit_raw(
    f"SHAPE_DIMENSION_REPRESENTATION('blank_rep',(#{mri_blank.eid}),#9060)"
)
