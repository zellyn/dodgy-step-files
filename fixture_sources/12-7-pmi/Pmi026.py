"""Pmi026 — Datum letters not unique within product.

Catalog claim: Two datum.identification letters are equal within the same
product_definition_shape.

Reproducer recipe: Three datum entities; two of them both carry
identification='A' in the same part.

Byte assertions:
  count_entity_def(b'DATUM') == 3
  contains(b'DATUM_SYSTEM')
  contains(b'POSITION_TOLERANCE')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi026",
    defect=(
        "two DATUM entities both carry identification='A' within the same "
        "PRODUCT_DEFINITION_SHAPE; AP242 requires datum letters to be unique per "
        "product; receivers must reject as semantically invalid; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT

# Three shape aspects within the same PRODUCT_DEFINITION_SHAPE.
asp1 = f._emit_raw("SHAPE_ASPECT('feature_1','',#9055,.T.)")
asp2 = f._emit_raw("SHAPE_ASPECT('feature_2','',#9055,.T.)")
asp3 = f._emit_raw("SHAPE_ASPECT('tol_feature','',#9055,.T.)")

# Defect: two DATUM entities both have identification='A'.
datum_a1 = f._emit_raw(f"DATUM('A','datum on face 1',#{asp1.eid},.T.)")
datum_a2 = f._emit_raw(f"DATUM('A','datum on face 2',#{asp2.eid},.T.)")
datum_b  = f._emit_raw(f"DATUM('B','datum on face 3',#{asp3.eid},.T.)")

# One compartment references datum_a1; the datum_system is still valid in
# structure but the duplicate 'A' identification makes it semantically invalid.
comp_a = f._emit_raw(
    f"DATUM_REFERENCE_COMPARTMENT('primary',(#{datum_a1.eid}))"
)
comp_b = f._emit_raw(
    f"DATUM_REFERENCE_COMPARTMENT('secondary',(#{datum_b.eid}))"
)
datum_sys = f._emit_raw(
    f"DATUM_SYSTEM('DRF',(#{comp_a.eid},#{comp_b.eid}))"
)

# Tolerance value.
tol_val = f._emit_raw("MEASURE_REPRESENTATION_ITEM('tol',LENGTH_MEASURE(0.05),#9056)")

# POSITION_TOLERANCE to satisfy the byte assertion.
asp_tol = f._emit_raw("SHAPE_ASPECT('pos_tol_feature','',#9055,.T.)")
f._emit_raw(
    f"POSITION_TOLERANCE(#{asp_tol.eid},#{tol_val.eid},#{datum_sys.eid},$)"
)
