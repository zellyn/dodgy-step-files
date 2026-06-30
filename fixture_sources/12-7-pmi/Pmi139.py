"""Pmi139 — Orphan DRAUGHTING_ANNOTATION_OCCURRENCE with broken STEP syntax.

Catalog claim: a STEP AP242 file (modeled on HOOPS Exchange SDHE-36465 defect)
where a DRAUGHTING_ANNOTATION_OCCURRENCE entity is emitted in the DATA section
with no reference from any DRAUGHTING_MODEL or
MECHANICAL_DESIGN_GEOMETRIC_PRESENTATION_REPRESENTATION.  Additionally, the
entity record has an attribute-count mismatch (wrong number of arguments).

The combination of:
  1. no parent reference (orphan — not reachable from the model shape tree), AND
  2. attribute-count mismatch (extra trailing $)
causes downstream parsers to report a syntax error.  The pre-fix HOOPS Exchange
writer (pre-SDHE-36465) emitted exactly this pattern.  Correct behavior: a
parser should skip the malformed orphan with a diagnostic rather than crashing.

The fixture wires a valid DRAUGHTING_MODEL with a PRESENTATION_SET and a correctly
formed annotation, then appends the orphan entity to demonstrate the contrast.

Source: https://docs.techsoft3d.com/exchange/2024/fixed_bugs.html (SDHE-36465)

Byte assertions:
  count_entity_def(b'DRAUGHTING_ANNOTATION_OCCURRENCE') == 2
  contains(b'DRAUGHTING_MODEL')
  contains(b'orphan_annotation')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi139",
    schema="AP242",
    defect=(
        "two DRAUGHTING_ANNOTATION_OCCURRENCE entities: one correctly wired into "
        "a DRAUGHTING_MODEL, one orphan with no parent reference AND an attribute "
        "count mismatch (extra trailing $); parsers must skip the malformed orphan "
        "with a diagnostic rather than crashing; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: GCS so OCC yields empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain reserves #9000+:
#   #9055 = PRODUCT_DEFINITION_SHAPE
#   #9060 = GEOMETRIC_REPRESENTATION_CONTEXT complex

# ── Shared presentation style ─────────────────────────────────────────────────
psa = f._emit_raw("PRESENTATION_STYLE_ASSIGNMENT($)")

# ── Valid annotation: correctly wired DRAUGHTING_ANNOTATION_OCCURRENCE ─────────
# A POLYLINE leader for a well-formed dimension annotation.
pt_a = f._emit_raw("CARTESIAN_POINT('',(0.0,0.0,0.0))")
pt_b = f._emit_raw("CARTESIAN_POINT('',(10.0,0.0,0.0))")
poly1 = f._emit_raw(f"POLYLINE('',(#{pt_a.eid},#{pt_b.eid}))")
# Correct attribute signature: (name, styles, item)
dao_valid = f._emit_raw(
    f"DRAUGHTING_ANNOTATION_OCCURRENCE('valid_annotation',(#{psa.eid}),#{poly1.eid})"
)

# ── DRAUGHTING_MODEL that references only the valid annotation ─────────────────
# This entity anchors the valid annotation to the model shape tree.
f._emit_raw(
    f"DRAUGHTING_MODEL('pmi_view',(#{dao_valid.eid}),#9060)"
)

# ── Orphan DRAUGHTING_ANNOTATION_OCCURRENCE with broken syntax ─────────────────
# DEFECT (SDHE-36465): entity exists in the DATA section but is not referenced
# from any DRAUGHTING_MODEL or MDGPR.  Additionally the attribute list has one
# extra trailing $ (attribute count mismatch — 4 args instead of the expected 3).
# A pre-fix writer emitted annotations that lost their parent reference but kept
# a spurious extra attribute from the incomplete write pass.
pt_c = f._emit_raw("CARTESIAN_POINT('',(20.0,0.0,0.0))")
pt_d = f._emit_raw("CARTESIAN_POINT('',(30.0,0.0,0.0))")
poly2 = f._emit_raw(f"POLYLINE('',(#{pt_c.eid},#{pt_d.eid}))")
# Extra trailing $ makes the arg count 4 instead of 3 — the syntax error.
# Byte assertion: contains(b'orphan_annotation')
f._emit_raw(
    f"DRAUGHTING_ANNOTATION_OCCURRENCE('orphan_annotation',(#{psa.eid}),#{poly2.eid},$)"
)
# Note: no DRAUGHTING_MODEL references this entity — it is an orphan.
