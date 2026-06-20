"""Pmi025 — Datum reference frame contains identical datums.

Catalog claim: A datum_system lists the same datum letter in
primary/secondary/tertiary slots.

Reproducer recipe: datum_system for (A, A, B) — primary and secondary
slots both reference datum 'A'.

Byte assertions:
  count_entity_def(b'DATUM') == 2
  count_entity_def(b'DATUM_REFERENCE_COMPARTMENT') == 3
  contains(b'POSITION_TOLERANCE')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi025",
    defect=(
        "DATUM_SYSTEM DRF has three DATUM_REFERENCE_COMPARTMENTs but only two "
        "DATUM entities because 'A' appears in both primary and secondary slots; "
        "receivers must warn and repair by deduplication or reject as semantically "
        "invalid; GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT

# Two datum features that attach to the product shape.
asp_a = f._emit_raw("SHAPE_ASPECT('datum_feature_A','',#9055,.T.)")
asp_b = f._emit_raw("SHAPE_ASPECT('datum_feature_B','',#9055,.T.)")

# Datum A and Datum B.
datum_a = f._emit_raw(f"DATUM('A','',#{asp_a.eid},.T.)")
datum_b = f._emit_raw(f"DATUM('B','',#{asp_b.eid},.T.)")

# The tolerance target feature.
asp_tol = f._emit_raw("SHAPE_ASPECT('tol_feature','',#9055,.T.)")

# Tolerance value.
tol_val = f._emit_raw("MEASURE_REPRESENTATION_ITEM('tol',LENGTH_MEASURE(0.1),#9056)")

# Defect: three compartments but datum_a appears in both primary and secondary.
# DRF = (A, A, B) — duplicate datum in primary/secondary slots.
comp_primary = f._emit_raw(
    f"DATUM_REFERENCE_COMPARTMENT('primary',(#{datum_a.eid}))"
)
comp_secondary = f._emit_raw(
    f"DATUM_REFERENCE_COMPARTMENT('secondary',(#{datum_a.eid}))"
)
comp_tertiary = f._emit_raw(
    f"DATUM_REFERENCE_COMPARTMENT('tertiary',(#{datum_b.eid}))"
)

datum_sys = f._emit_raw(
    f"DATUM_SYSTEM('DRF',(#{comp_primary.eid},#{comp_secondary.eid},#{comp_tertiary.eid}))"
)

# POSITION_TOLERANCE referencing the datum system.
f._emit_raw(
    f"POSITION_TOLERANCE(#{asp_tol.eid},#{tol_val.eid},#{datum_sys.eid},$)"
)
