"""Pmi042 — Empty semantic-text string in PMI.

Catalog claim: A semantic_text validation property carries an empty string ''.
Provides no information yet inflates PMI counts.

Reproducer recipe: descriptive_representation_item('semantic text', '')
attached to a tolerance.

Byte assertions:
  contains(b'PERPENDICULARITY_TOLERANCE')
  contains(b'DESCRIPTIVE_REPRESENTATION_ITEM')
  contains(b'DATUM_SYSTEM')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi042",
    defect=(
        "DESCRIPTIVE_REPRESENTATION_ITEM with name='semantic text' carries an empty "
        "string value ''; semantic_text validation property must carry non-empty text; "
        "receivers must emit a warning diagnostic and ignore the offending attribute; "
        "silently accepting blank semantic text is forbidden; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT

# Datum feature and datum for DATUM_SYSTEM.
asp_datum = f._emit_raw("SHAPE_ASPECT('datum_feature_A','',#9055,.T.)")
datum_a = f._emit_raw(f"DATUM('A','',#{asp_datum.eid},.T.)")
dre = f._emit_raw(f"DATUM_REFERENCE_ELEMENT(#{datum_a.eid},$,$,$,$)")
comp = f._emit_raw(f"DATUM_REFERENCE_COMPARTMENT('primary',(#{dre.eid}))")
datum_sys = f._emit_raw(f"DATUM_SYSTEM('DRF',(#{comp.eid}))")

# Tolerance target feature and value.
asp_tol = f._emit_raw("SHAPE_ASPECT('tol_feature','',#9055,.T.)")
tol_val = f._emit_raw("MEASURE_REPRESENTATION_ITEM('tol',LENGTH_MEASURE(0.05),#9056)")

# PERPENDICULARITY_TOLERANCE referencing the datum system.
perp_tol = f._emit_raw(
    f"PERPENDICULARITY_TOLERANCE(#{asp_tol.eid},#{tol_val.eid},#{datum_sys.eid},$)"
)

# Defect: DESCRIPTIVE_REPRESENTATION_ITEM with an empty string value.
# This is the semantic_text validation property attached to the tolerance.
empty_text = f._emit_raw("DESCRIPTIVE_REPRESENTATION_ITEM('semantic text','')")

# Representation holding the tolerance and the offending empty text item.
rep_ctx = f._emit_raw("REPRESENTATION_CONTEXT('pmi','3D')")
f._emit_raw(
    f"REPRESENTATION('pmi_rep',(#{perp_tol.eid},#{empty_text.eid}),#{rep_ctx.eid})"
)
