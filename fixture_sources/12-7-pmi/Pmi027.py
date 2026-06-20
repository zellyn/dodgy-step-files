"""Pmi027 — datum_reference (legacy) used instead of datum_system in AP242.

Catalog claim: AP242 file uses the AP203/AP214-style datum_reference to
attach datums directly to a tolerance, when it should use a datum_system
containing datum_reference_compartments.

Reproducer recipe: geometric_tolerance with datum_reference chain (legacy)
inside an AP242 file.

Byte assertions:
  count_entity_def(b'DATUM_REFERENCE') == 3
  contains(b'POSITION_TOLERANCE_WITH_DATUM_REFERENCE')
  count_entity_def(b'DATUM_SYSTEM') == 0

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi027",
    defect=(
        "AP242 file uses legacy DATUM_REFERENCE chain (AP203/AP214 style) inside "
        "POSITION_TOLERANCE_WITH_DATUM_REFERENCE instead of the AP242-required "
        "DATUM_SYSTEM / DATUM_REFERENCE_COMPARTMENT structure; receivers must warn "
        "and coerce to the equivalent datum_system form on import; "
        "no DATUM_SYSTEM present; GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT

# Three datum features.
asp_a = f._emit_raw("SHAPE_ASPECT('feature_A','',#9055,.T.)")
asp_b = f._emit_raw("SHAPE_ASPECT('feature_B','',#9055,.T.)")
asp_c = f._emit_raw("SHAPE_ASPECT('feature_C','',#9055,.T.)")
asp_tol = f._emit_raw("SHAPE_ASPECT('tol_feature','',#9055,.T.)")

# Three datums (one per feature).
datum_a = f._emit_raw(f"DATUM('A','',#{asp_a.eid},.T.)")
datum_b = f._emit_raw(f"DATUM('B','',#{asp_b.eid},.T.)")
datum_c = f._emit_raw(f"DATUM('C','',#{asp_c.eid},.T.)")

# Defect: legacy DATUM_REFERENCE chain used directly, no DATUM_SYSTEM.
# AP203/AP214 pattern: each DATUM_REFERENCE holds one datum + a next-ref pointer.
# Three DATUM_REFERENCE entities forming a precedence chain: A → B → C.
dr_c = f._emit_raw(f"DATUM_REFERENCE(3,#{datum_c.eid},$)")
dr_b = f._emit_raw(f"DATUM_REFERENCE(2,#{datum_b.eid},#{dr_c.eid})")
dr_a = f._emit_raw(f"DATUM_REFERENCE(1,#{datum_a.eid},#{dr_b.eid})")

# Tolerance value.
tol_val = f._emit_raw("MEASURE_REPRESENTATION_ITEM('tol',LENGTH_MEASURE(0.1),#9056)")

# POSITION_TOLERANCE_WITH_DATUM_REFERENCE: references datum_reference chain directly
# (legacy AP203/AP214 approach, not AP242 datum_system approach).
f._emit_raw(
    f"POSITION_TOLERANCE_WITH_DATUM_REFERENCE(#{asp_tol.eid},#{tol_val.eid},"
    f"#{dr_a.eid})"
)
# Intentionally zero DATUM_SYSTEM entities — that is the defect.
