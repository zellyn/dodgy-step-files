"""Pmi029 — Datum system carries mixed Datum_System / Datum_Reference SELECT array.

Catalog claim: AP242 Datum_System_AP242.constituents is a SELECT array that
may contain both Datum_System and Datum_Reference items. Decoders that
assume a homogeneous array crash on multi-body files.

Reproducer recipe: AP242 file using DATUM_SYSTEM_AP242 whose constituents
list mixes DatumSystem and DatumReference.

Byte assertions:
  contains(b'DATUM_SYSTEM_AP242')
  contains(b'DATUM_REFERENCE')
  contains(b'DATUM_REFERENCE_ELEMENT')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi029",
    defect=(
        "DATUM_SYSTEM_AP242.constituents is a heterogeneous SELECT array mixing a "
        "DATUM_SYSTEM sub-item and a DATUM_REFERENCE item; decoders that assume a "
        "homogeneous array crash or silently drop entries on multi-body files; "
        "receivers must iterate and dispatch by entity type; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT

# Datum features.
asp_a = f._emit_raw("SHAPE_ASPECT('feature_A','',#9055,.T.)")
asp_b = f._emit_raw("SHAPE_ASPECT('feature_B','',#9055,.T.)")
asp_tol = f._emit_raw("SHAPE_ASPECT('tol_feature','',#9055,.T.)")

datum_a = f._emit_raw(f"DATUM('A','',#{asp_a.eid},.T.)")
datum_b = f._emit_raw(f"DATUM('B','',#{asp_b.eid},.T.)")

# A DATUM_REFERENCE_ELEMENT wrapping datum_a (AP242 modern form).
dre_a = f._emit_raw(f"DATUM_REFERENCE_ELEMENT(#{datum_a.eid},$,$,$,$)")

# An inner DATUM_SYSTEM used as a sub-constituent (modern SELECT item).
comp_inner = f._emit_raw(
    f"DATUM_REFERENCE_COMPARTMENT('primary',(#{dre_a.eid}))"
)
inner_sys = f._emit_raw(
    f"DATUM_SYSTEM('inner_sys',(#{comp_inner.eid}))"
)

# A legacy DATUM_REFERENCE (AP203/AP214) used as the second constituent.
# This is the "wrong" SELECT type mixed into the array — the defect.
datum_ref = f._emit_raw(f"DATUM_REFERENCE(1,#{datum_b.eid},$)")

# Defect: DATUM_SYSTEM_AP242.constituents mixes DATUM_SYSTEM and DATUM_REFERENCE.
f._emit_raw(
    f"DATUM_SYSTEM_AP242('mixed_drf',(#{inner_sys.eid},#{datum_ref.eid}))"
)

# Tolerance value.
tol_val = f._emit_raw("MEASURE_REPRESENTATION_ITEM('tol',LENGTH_MEASURE(0.15),#9056)")
