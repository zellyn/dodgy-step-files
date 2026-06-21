"""Pmi085 — Dimension names dropped on round-trip.

Catalog claim: a PMI dimension's name attribute (an identifier used by
downstream design-of-experiments tools) is read but never written back on
export. Round-trip files have anonymous dimensions.

Reproducer recipe: PMI dimension with name = "OD_critical". Read, export.
Output dimension has empty name.

Byte assertions:
  contains(b'DIMENSIONAL_LOCATION')
  count_entity_def(b'SHAPE_ASPECT') == 2

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi085",
    schema="AP242",
    defect=(
        "DIMENSIONAL_LOCATION named 'OD_critical' connects two SHAPE_ASPECTs "
        "representing the measured feature endpoints; the dimension name "
        "'OD_critical' is used by downstream design-of-experiments tools to "
        "identify specific tolerances; a writer that routes attribute emission "
        "only for shapes with non-trivial geometry silently drops the name "
        "attribute on round-trip, producing an anonymous dimension; receivers "
        "must preserve the name attribute of every named DIMENSIONAL_LOCATION "
        "and DIMENSIONAL_SIZE regardless of the associated geometry; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE

# ── Two SHAPE_ASPECTs (byte assertion: count == 2) ────────────────────────────
# 'asp_from' and 'asp_to' are the two endpoints of the named OD dimension.
asp_from = f._emit_raw(
    "SHAPE_ASPECT('OD_from','outer diameter start',#9055,.T.)"
)
asp_to = f._emit_raw(
    "SHAPE_ASPECT('OD_to','outer diameter end',#9055,.T.)"
)

# ── DIMENSIONAL_LOCATION (byte assertion: contains) ───────────────────────────
# DEFECT: the name 'OD_critical' is written by the producer but silently
# dropped by the writer on round-trip, leaving '' in the output file.
# Downstream design-of-experiments tools that look up 'OD_critical' by name
# cannot find the dimension in the round-tripped file.
f._emit_raw(
    f"DIMENSIONAL_LOCATION('OD_critical','named outer diameter dimension',"
    f"#{asp_from.eid},#{asp_to.eid})"
)
