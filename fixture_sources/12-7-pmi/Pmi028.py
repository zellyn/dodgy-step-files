"""Pmi028 — common_datum vs common_datum_list (multi-feature datum).

Catalog claim: For ASME multiple-feature datums or ISO common datums, RP
requires datum_reference_element with common_datum_list; some senders use
the older common_datum instead.

Reproducer recipe: A multi-feature datum encoded with common_datum(d1, d2)
rather than common_datum_list((d1, d2)).

Byte assertions:
  contains(b'COMMON_DATUM')
  count_entity_def(b'DATUM') == 2
  contains(b'DATUM_SYSTEM')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi028",
    defect=(
        "multi-feature datum encoded with COMMON_DATUM(d1, d2) instead of the "
        "AP242 RP-required COMMON_DATUM_LIST((d1, d2)) inside a "
        "DATUM_REFERENCE_ELEMENT; receivers must warn and coerce the two forms to "
        "equivalent; GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT

# Two datum features for the multi-feature datum.
asp_a = f._emit_raw("SHAPE_ASPECT('feature_A','',#9055,.T.)")
asp_b = f._emit_raw("SHAPE_ASPECT('feature_B','',#9055,.T.)")
asp_tol = f._emit_raw("SHAPE_ASPECT('tol_feature','',#9055,.T.)")

# Two DATUM entities (count_entity_def == 2).
datum_a = f._emit_raw(f"DATUM('A','',#{asp_a.eid},.T.)")
datum_b = f._emit_raw(f"DATUM('B','',#{asp_b.eid},.T.)")

# Defect: COMMON_DATUM (older entity) used instead of COMMON_DATUM_LIST.
# COMMON_DATUM groups two datums as a single multi-feature reference (ASME-Y14.5
# / ISO common datum). The RP requires COMMON_DATUM_LIST inside
# DATUM_REFERENCE_ELEMENT; using COMMON_DATUM directly is the legacy misuse.
common_dat = f._emit_raw(
    f"COMMON_DATUM(#{datum_a.eid},#{datum_b.eid})"
)

# DATUM_REFERENCE_ELEMENT carries the common_datum (wrong form).
dre = f._emit_raw(f"DATUM_REFERENCE_ELEMENT(#{common_dat.eid},$,$,$,$)")

# Wrap in a DATUM_SYSTEM (satisfies byte assertion; structure is otherwise valid).
comp = f._emit_raw(f"DATUM_REFERENCE_COMPARTMENT('primary',(#{dre.eid}))")
datum_sys = f._emit_raw(f"DATUM_SYSTEM('DRF',(#{comp.eid}))")

# Tolerance value and position tolerance to complete the PMI annotation.
tol_val = f._emit_raw("MEASURE_REPRESENTATION_ITEM('tol',LENGTH_MEASURE(0.2),#9056)")
f._emit_raw(
    f"POSITION_TOLERANCE(#{asp_tol.eid},#{tol_val.eid},#{datum_sys.eid},$)"
)
