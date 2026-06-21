"""Pmi069 — DIMENSIONAL_LOCATION_WITH_PATH whose path connects unrelated shape aspects.

Catalog claim: AP242 DIMENSIONAL_LOCATION_WITH_PATH carries an extra 'path'
attribute (a SHAPE_ASPECT_RELATIONSHIP chain) describing the route through the
model along which a dimension is to be measured. When the path endpoints are
unrelated shape aspects on disconnected components, the dimension's
interpretation is ambiguous.

Reproducer recipe: two SHAPE_ASPECTs 'feature_on_A' and 'feature_on_B' on
disjoint topology; SHAPE_ASPECT_RELATIONSHIP between them named 'no path';
DIMENSIONAL_LOCATION_WITH_PATH referencing both.

Byte assertions:
  contains(b'DIMENSIONAL_LOCATION_WITH_PATH')
  contains(b'SHAPE_ASPECT_RELATIONSHIP')
  count_entity_def(b'SHAPE_ASPECT') == 2

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi069",
    schema="AP242",
    defect=(
        "DIMENSIONAL_LOCATION_WITH_PATH path connects 'feature_on_A' and "
        "'feature_on_B' which are on disconnected (disjoint) topology; "
        "the SHAPE_ASPECT_RELATIONSHIP named 'no path' does not form a connected "
        "chain through the model; receivers must validate that the path is a "
        "connected sequence of shape_aspects and reject or warn when endpoints "
        "are unrelated; silently accepting a disconnected path is forbidden; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT

# ── Two SHAPE_ASPECTs on disjoint topology (count_entity_def == 2) ────────────
asp_a = f._emit_raw("SHAPE_ASPECT('feature_on_A','',#9055,.T.)")
asp_b = f._emit_raw("SHAPE_ASPECT('feature_on_B','',#9055,.T.)")

# ── SHAPE_ASPECT_RELATIONSHIP between the unrelated aspects ──────────────────
# Defect: the path connects aspects from disconnected components — no shared
# topology between A and B.
sar = f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('no path','unrelated disconnected path',"
    f"#{asp_a.eid},#{asp_b.eid})"
)

# ── DIMENSIONAL_LOCATION_WITH_PATH ────────────────────────────────────────────
# measuring_length=10.0 mm between the two unrelated aspects via the bad path.
f._emit_raw(
    f"DIMENSIONAL_LOCATION_WITH_PATH(#{asp_a.eid},#{asp_b.eid},'distance',#{sar.eid})"
)
