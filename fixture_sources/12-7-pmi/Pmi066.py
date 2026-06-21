"""Pmi066 — Compound-feature semantics (HTC counterbore) per Hole RP.

Catalog claim: Compound holes (counterbore, countersink, counter-drill) must
be modeled as semantic features per the draft Hole Information Recommended
Practices. Files emitting each segment as an independent DIMENSIONAL_SIZE and
no compound-hole entity lose the compound-feature link.

Reproducer recipe: HTC-style model with one counterbore; each segment emitted
as an independent DIMENSIONAL_SIZE; no compound-hole feature entity linking
them.

Byte assertions:
  count_entity_def(b'DIMENSIONAL_SIZE') == 4
  count_entity_def(b'SHAPE_ASPECT') == 4
  contains(b'PLUS_MINUS_TOLERANCE')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi066",
    defect=(
        "Counterbore hole compound feature represented as four independent "
        "DIMENSIONAL_SIZE entities (bore_diameter, bore_depth, cbore_diameter, "
        "cbore_depth) without a compound-hole entity linking them; the Hole "
        "Information Recommended Practices require a compound-hole feature "
        "entity to preserve the counterbore semantic relationship; receivers "
        "must reconstruct or repair compound features by name and proximity; "
        "silently accepting disconnected dimensions as a compound hole is forbidden; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT

# ── Four SHAPE_ASPECTs (one per dimension segment) ───────────────────────────
asp_bore_diam = f._emit_raw("SHAPE_ASPECT('bore_diameter','',#9055,.T.)")
asp_bore_depth = f._emit_raw("SHAPE_ASPECT('bore_depth','',#9055,.T.)")
asp_cbore_diam = f._emit_raw("SHAPE_ASPECT('cbore_diameter','',#9055,.T.)")
asp_cbore_depth = f._emit_raw("SHAPE_ASPECT('cbore_depth','',#9055,.T.)")

# ── Four independent DIMENSIONAL_SIZEs (defect: no compound-hole linking) ─────
ds_bore_diam = f._emit_raw(
    f"DIMENSIONAL_SIZE(#{asp_bore_diam.eid},'bore_diameter')"
)
ds_bore_depth = f._emit_raw(
    f"DIMENSIONAL_SIZE(#{asp_bore_depth.eid},'bore_depth')"
)
ds_cbore_diam = f._emit_raw(
    f"DIMENSIONAL_SIZE(#{asp_cbore_diam.eid},'cbore_diameter')"
)
ds_cbore_depth = f._emit_raw(
    f"DIMENSIONAL_SIZE(#{asp_cbore_depth.eid},'cbore_depth')"
)

# ── PLUS_MINUS_TOLERANCE on bore_diameter (byte assertion) ───────────────────
mri_nom = f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('nominal',LENGTH_MEASURE(8.0),#9056)"
)
mri_upper = f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('upper',LENGTH_MEASURE(0.05),#9056)"
)
mri_lower = f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('lower',LENGTH_MEASURE(0.05),#9056)"
)
tol_val = f._emit_raw(
    f"TOLERANCE_VALUE(#{mri_upper.eid},#{mri_lower.eid})"
)
f._emit_raw(
    f"PLUS_MINUS_TOLERANCE(#{tol_val.eid},#{ds_bore_diam.eid})"
)
