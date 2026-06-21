"""Pmi073 — Compound feature with self-referential pattern membership.

Catalog claim: AP242 Edition 4 COMPOUND_FEATURE groups feature definitions as
a PMI target. A programmatic exporter that forgets a recursion guard can emit
a cycle: the compound feature is 'part_of' itself.

Reproducer recipe: SHAPE_ASPECT 'compound_pattern' linked via
SHAPE_ASPECT_RELATIONSHIP 'part_of' to itself; alongside two member features
'hole1' and 'hole2' linked to the same pattern.

Byte assertions:
  count_entity_def(b'SHAPE_ASPECT') == 3
  count_entity_def(b'SHAPE_ASPECT_RELATIONSHIP') == 3

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi073",
    schema="AP242",
    defect=(
        "COMPOUND_FEATURE compound_pattern has a SHAPE_ASPECT_RELATIONSHIP 'part_of' "
        "linking it to itself (self-loop); a recursive descent traversal of the "
        "part-of graph never terminates; receivers must detect cycles in the "
        "pattern-membership graph and reject, or treat the self-loop as a no-op "
        "with a warning; silently accepting a self-referential pattern is forbidden; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT

# ── Three SHAPE_ASPECTs (byte assertion: count == 3) ─────────────────────────
# compound_pattern: the feature group that refers to itself.
compound_pattern = f._emit_raw(
    "SHAPE_ASPECT('compound_pattern','hole pattern',#9055,.T.)"
)
# Two member hole features.
hole1 = f._emit_raw("SHAPE_ASPECT('hole1','first hole',#9055,.T.)")
hole2 = f._emit_raw("SHAPE_ASPECT('hole2','second hole',#9055,.T.)")

# ── Three SHAPE_ASPECT_RELATIONSHIPs (byte assertion: count == 3) ─────────────
# Defect: compound_pattern is 'part_of' itself (self-loop).
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('part_of','self-loop',"
    f"#{compound_pattern.eid},#{compound_pattern.eid})"
)
# Legitimate: hole1 and hole2 are members of the pattern.
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('part_of','hole1 member',"
    f"#{hole1.eid},#{compound_pattern.eid})"
)
f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('part_of','hole2 member',"
    f"#{hole2.eid},#{compound_pattern.eid})"
)
