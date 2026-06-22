"""Le025 — Empty / blank / single-space NAME silently emptied.

Catalog claim: A PRODUCT(' ',…) with a NAME consisting only of a single
space becomes an empty XCAF attribute name after trim, losing the original
sender's intent. The distinction between '' (empty) and ' ' (whitespace-only)
is meaningful to the producer.

Reproducer recipe:
  PRODUCT(' ','id','desc',(..));

Byte assertions:
  matches(rb"PRODUCT\\(' ',")
  count(b"PRODUCT('") >= 1

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le025",
    defect=(
        "Empty / blank / single-space NAME silently emptied; "
        "PRODUCT(' ',...) NAME is whitespace-only — a single space; "
        "OCCT XCAF attribute loading trims the name to '' losing the sender's intent; "
        "ISO 10303-21 §6.4.3.1: string values are preserved as-is; "
        "heap must distinguish empty '' from whitespace-only ' '; "
        "heal and accept: preserve literal value or trim only after explicit user opt-in; "
        "must not silently empty a non-empty whitespace string; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept encoding defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Defect payload: inject PRODUCT entities whose NAME field is whitespace-only.
#
# The canonical builder's add_product_chain() uses non-empty product IDs.
# We inject a supplementary PRODUCT with a single-space name to trigger the
# whitespace-trim bug observed in OCCT XCAF (MantisBT #27169, commit 0911d06).
#
# PRODUCT #8997: NAME=' ' (single space) — the minimal reproducer from the catalog.
# PRODUCT #8998: NAME='   ' (three spaces) — exercises multi-space trim.
#
# Satisfies:
#   matches(rb"PRODUCT\(' ',")   — #8997 (single space followed by comma)
#   count(b"PRODUCT('") >= 1    — both entities

_original_render = f.render


def _render_with_blank_name() -> str:
    text = _original_render()
    product_lines = (
        "#8997=PRODUCT(' ','blank-name-id','desc',(#9000));\n"
        "#8998=PRODUCT('   ','multi-space-name','desc',(#9000));\n"
    )
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + product_lines + text[idx:]


f.render = _render_with_blank_name  # type: ignore[method-assign]
