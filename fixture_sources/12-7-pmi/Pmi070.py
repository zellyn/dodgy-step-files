"""Pmi070 — GEOMETRIC_TOLERANCE_RELATIONSHIP cycle (A→B→C→A).

Catalog claim: AP242 GEOMETRIC_TOLERANCE_RELATIONSHIP allows one tolerance to
be derived/refined from another. A cycle A→B, B→C, C→A causes infinite
recursion or a stack guard hit in any receiver that walks the relationship
graph to evaluate a tolerance.

Reproducer recipe: three GEOMETRIC_TOLERANCE entities A, B, C; three
GEOMETRIC_TOLERANCE_RELATIONSHIP entities forming the cycle A refines B,
B refines C, C refines A.

Byte assertions:
  count_entity_def(b'GEOMETRIC_TOLERANCE') == 3
  count_entity_def(b'GEOMETRIC_TOLERANCE_RELATIONSHIP') == 3
  count_entity_def(b'SHAPE_ASPECT') == 3

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi070",
    schema="AP242",
    defect=(
        "GEOMETRIC_TOLERANCE_RELATIONSHIP forms a cycle A→B→C→A across three "
        "GEOMETRIC_TOLERANCE entities; any receiver that walks the refinement "
        "graph to evaluate a tolerance recurses infinitely or hits a stack guard; "
        "receivers must detect cycles in the tolerance-relationship graph at load "
        "time and reject with a diagnostic naming the cycle members; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT

# ── Three SHAPE_ASPECTs (byte assertion: count == 3) ─────────────────────────
asp_a = f._emit_raw("SHAPE_ASPECT('feature_A','',#9055,.T.)")
asp_b = f._emit_raw("SHAPE_ASPECT('feature_B','',#9055,.T.)")
asp_c = f._emit_raw("SHAPE_ASPECT('feature_C','',#9055,.T.)")

# Tolerance value (shared — the cycle is the defect, not the values).
tol_val = f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('tol',LENGTH_MEASURE(0.05),#9056)"
)

# ── Three GEOMETRIC_TOLERANCE entities (byte assertion: count == 3) ───────────
# Using GEOMETRIC_TOLERANCE directly so count_entity_def(b'GEOMETRIC_TOLERANCE')
# == 3 is satisfied by exact name match.
gt_a = f._emit_raw(
    f"GEOMETRIC_TOLERANCE('gt_A','tolerance A',#{tol_val.eid},#{asp_a.eid})"
)
gt_b = f._emit_raw(
    f"GEOMETRIC_TOLERANCE('gt_B','tolerance B',#{tol_val.eid},#{asp_b.eid})"
)
gt_c = f._emit_raw(
    f"GEOMETRIC_TOLERANCE('gt_C','tolerance C',#{tol_val.eid},#{asp_c.eid})"
)

# ── Three GEOMETRIC_TOLERANCE_RELATIONSHIP forming a cycle A→B→C→A ───────────
# Defect: the three relationships form a directed cycle; receivers that walk
# this graph to evaluate refinement recurse infinitely.
f._emit_raw(
    f"GEOMETRIC_TOLERANCE_RELATIONSHIP('refines','A refines B',#{gt_a.eid},#{gt_b.eid})"
)
f._emit_raw(
    f"GEOMETRIC_TOLERANCE_RELATIONSHIP('refines','B refines C',#{gt_b.eid},#{gt_c.eid})"
)
f._emit_raw(
    f"GEOMETRIC_TOLERANCE_RELATIONSHIP('refines','C refines A',#{gt_c.eid},#{gt_a.eid})"
)
