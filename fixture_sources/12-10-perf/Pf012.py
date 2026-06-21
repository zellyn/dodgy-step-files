"""Pf012 — Stack overflow via deeply nested aggregate parens.

Catalog claim: recursive-descent parser for Part-21 LIST/SET/BAG aggregates
without depth ceiling crashes when an attacker supplies thousands of nested
parentheses inside a single attribute. Pattern: GEOMETRIC_SET with deeply
nested parens causes stack overflow / depth-exceeded rejection.

Byte assertion: count_entity_def(b'CARTESIAN_POINT') >= 3
Tier-3: load != "ok"
Expected: occt=reject/reject gmsh=reject ifc=schema_n/a E_AGGREGATE_TOO_DEEP
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pf012",
    defect=(
        "GEOMETRIC_SET with deeply nested aggregate parens (25–30 levels deep) "
        "inside a single attribute; recursive-descent parser without depth ceiling "
        "crashes via stack overflow; compliant readers must enforce a depth ceiling "
        "(e.g. 64) and emit E_AGGREGATE_TOO_DEEP; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields reject"
    ),
)

# Three anchor CARTESIAN_POINTs to satisfy byte assertion
p1 = f.cartesian_point((0.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 0.0, 0.0))
p3 = f.cartesian_point((2.0, 0.0, 0.0))
p4 = f.cartesian_point((3.0, 0.0, 0.0))


def _render_with_deep_nesting():
    text = f._original_render_pf012()
    # Inject GEOMETRIC_SET entities with deeply nested aggregate parens.
    # Each GEOMETRIC_SET attribute value has N levels of parens around #p1.
    # depth 25: 25 levels of nested parens
    d25 = "(" * 25 + f" #{p1.eid} " + ")" * 25
    d22 = "(" * 22 + f" #{p1.eid} " + ")" * 22
    d27 = "(" * 27 + f" #{p1.eid} " + ")" * 27
    d30 = "(" * 30 + f" #{p1.eid} " + ")" * 30
    injection = (
        "/* depth 25 */\n"
        f"#10=GEOMETRIC_SET('deep-25',\n{d25});\n"
        "/* Pf012-B variant: nested LIST inside a single attribute's value\n"
        "   (some readers special-case nested LISTs at any depth). */\n"
        "/* depth 22 */\n"
        f"#20=GEOMETRIC_SET('deep-22',\n{d22});\n"
        "/* Pf012-C variant: doubly-nested chains in one file - some healers\n"
        "   recover after the first then crash on the second. */\n"
        "/* depth 27 */\n"
        f"#30=GEOMETRIC_SET('deep-27',\n{d27});\n"
        "/* depth 30 - exceeds many default ceilings */\n"
        f"#40=GEOMETRIC_SET('deep-30',\n{d30});\n"
    )
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + injection + text[idx:]


# Stash the original render and replace
f._original_render_pf012 = f.render  # type: ignore[attr-defined]
f.render = _render_with_deep_nesting  # type: ignore[method-assign]

# Add a minimal GEOMETRIC_CURVE_SET as the product entity
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{p1.eid}))")
f.add_product_chain(gcs)
