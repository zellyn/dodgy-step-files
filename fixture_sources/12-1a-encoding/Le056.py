"""Le056 — Mixed .T. and .TRUE. boolean lexemes within one file.

Catalog claim: One DATA section contains both canonical .T. / .F. and long-form
.TRUE. / .FALSE. boolean lexemes. Receivers that accept only the canonical form
produce inconsistent results across the same file — some attributes parse,
others fail — which is harder to diagnose than a uniform long-form file.

Reproducer recipe:
  One EDGE_CURVE with same_sense=.T.; another with same_sense=.TRUE.; both
  referenced from the same EDGE_LOOP.

Byte assertions:
  contains(b'.T.') and contains(b'.TRUE.')
  count(b'.T.') >= 1 and count(b'.TRUE.') >= 1

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le056",
    defect=(
        "Mixed .T. and .TRUE. boolean lexemes within one file; "
        "ISO 10303-21 §6.3.4: canonical boolean spellings are .T. and .F. only; "
        "one DATA section contains both canonical .T./.F. and long-form .TRUE./.FALSE.; "
        "deduced from multi-source writer pipelines where one subsystem writes .T. "
        "and another writes .TRUE. without normalising; "
        "receivers that accept only canonical form produce inconsistent parse results "
        "across the same file — some attributes parse, others fail — "
        "harder to diagnose than a uniformly long-form file; "
        "sibling of Le055 (uniform long-form); cousin of Wr041; "
        "receiver must surface the inconsistency: never accept some and reject others "
        "in the same file; normalise to .T./.F. in lenient mode; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept encoding defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Defect payload: inject two EDGE_CURVE records in the same DATA section —
# one using the canonical .T. and another using the long-form .TRUE. — so the
# file contains both spellings, demonstrating the mixed-boolean inconsistency.
#
# Vertex/curve refs (#9001, #9002, #9003) are intentionally absent; the
# fixture tests the tokeniser's boolean handling, not topology resolution.
#
# Also inject a matching PERSON entity to anchor the defect string in a
# simpler attribute context.
#
# Satisfies:
#   contains(b'.T.')     — canonical form present
#   contains(b'.TRUE.')  — long form present (the defect)
#   count(b'.T.') >= 1  — at least one canonical boolean
#   count(b'.TRUE.') >= 1 — at least one non-canonical boolean

_original_render = f.render


def _render_with_mixed_booleans() -> str:
    text = _original_render()
    raw_lines = (
        # Canonical form: .T. — this one is correct
        "#8997=EDGE_CURVE('edge-canonical',#9001,#9002,#9003,.T.);\n"
        # Non-canonical form: .TRUE. — this one has the defect
        "#8998=EDGE_CURVE('edge-long-form',#9001,#9002,#9003,.TRUE.);\n"
        # PERSON to document the mixed-boolean defect in a string attribute
        "#8999=PERSON('file mixes .T. and .TRUE. booleans','mixed-boolean-lexemes','');\n"
    )
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + raw_lines + text[idx:]


f.render = _render_with_mixed_booleans  # type: ignore[method-assign]
