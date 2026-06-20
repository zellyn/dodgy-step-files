"""Pmi043 — Lower-case relation names where RP requires lower-case keywords.

Catalog claim: Relation name values (e.g. on geometric_tolerance_relationship)
use upper or mixed case where RP requires lower-case keywords ('composite',
'all around', etc.).

Reproducer recipe: geometric_tolerance_relationship('Composite', t1, t2)
with capital C.

Byte assertions:
  count_entity_def(b'POSITION_TOLERANCE') == 2
  count_entity_def(b'GEOMETRIC_TOLERANCE_RELATIONSHIP') == 2
  contains(b'DATUM_SYSTEM')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi043",
    defect=(
        "GEOMETRIC_TOLERANCE_RELATIONSHIP name values use wrong capitalisation: "
        "'Composite' and 'All Around' instead of the AP242 RP-required lowercase "
        "'composite' and 'all around'; receivers must case-insensitive-normalize on "
        "read and warn on case mismatch; silently accepting mixed-case is forbidden; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT

# Datum feature for the datum system (satisfies byte assertion).
asp_datum = f._emit_raw("SHAPE_ASPECT('datum_feature_A','',#9055,.T.)")
datum_a = f._emit_raw(f"DATUM('A','',#{asp_datum.eid},.T.)")
dre = f._emit_raw(f"DATUM_REFERENCE_ELEMENT(#{datum_a.eid},$,$,$,$)")
comp = f._emit_raw(f"DATUM_REFERENCE_COMPARTMENT('primary',(#{dre.eid}))")
datum_sys = f._emit_raw(f"DATUM_SYSTEM('DRF',(#{comp.eid}))")

# Two tolerance target features.
asp_tol1 = f._emit_raw("SHAPE_ASPECT('surface_A','',#9055,.T.)")
asp_tol2 = f._emit_raw("SHAPE_ASPECT('surface_B','',#9055,.T.)")
tol_val = f._emit_raw("MEASURE_REPRESENTATION_ITEM('tol',LENGTH_MEASURE(0.05),#9056)")

# Two POSITION_TOLERANCE entities (byte assertion: count == 2).
pos_tol1 = f._emit_raw(
    f"POSITION_TOLERANCE(#{asp_tol1.eid},#{tol_val.eid},#{datum_sys.eid},$)"
)
pos_tol2 = f._emit_raw(
    f"POSITION_TOLERANCE(#{asp_tol2.eid},#{tol_val.eid},#{datum_sys.eid},$)"
)

# Defect: two GEOMETRIC_TOLERANCE_RELATIONSHIP entities with wrong-case names.
# RP requires lowercase 'composite' and 'all around'; using 'Composite' and
# 'All Around' (mixed/title case) is the defect being demonstrated.
f._emit_raw(
    f"GEOMETRIC_TOLERANCE_RELATIONSHIP('Composite','',#{pos_tol1.eid},#{pos_tol2.eid})"
)
f._emit_raw(
    f"GEOMETRIC_TOLERANCE_RELATIONSHIP('All Around','',#{pos_tol1.eid},#{pos_tol2.eid})"
)
