"""Le041 — \\Q\\ encoding a code point in the UTF-16 surrogate range (U+D800-U+DFFF).

Catalog claim: \\Q\\NNN\\Q\\ accepts decimal Unicode scalars, but values
55296-57343 (the UTF-16 surrogate halves U+D800-U+DFFF) are not legal
Unicode scalars. A kernel that decodes \\Q\\55296\\Q\\ into a UTF-8 stream
produces an ill-formed sequence (CESU-8 / WTF-8) that downstream tooling
may reject.

Reproducer recipe:
  PRODUCT.name='lone=\\Q\\55296\\Q\\' — value 55296 is U+D800, a high-surrogate half.

Byte assertions:
  contains(b'\\\\Q\\\\55296\\\\Q\\\\')
  contains(b'55296')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=process_signal
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le041",
    defect=(
        "\\Q\\ encoding a code point in the UTF-16 surrogate range U+D800-U+DFFF; "
        "ISO 10303-21 Ed.3 §6.4.3: \\Q\\NNN\\Q\\ accepts decimal Unicode scalars; "
        "values 55296-57343 are UTF-16 surrogate halves, not legal Unicode scalars; "
        "defect string: 'lone=\\Q\\55296\\Q\\' — decimal 55296 = U+D800, high-surrogate half; "
        "a kernel decoding this into UTF-8 produces an ill-formed CESU-8 / WTF-8 sequence; "
        "the producer may have re-encoded a Java/JavaScript string that allowed lone surrogates "
        "internally, or failed to emit the surrogate pair for a supplementary-plane character; "
        "receiver must reject \\Q\\ payloads in the surrogate range 55296-57343 "
        "with a precise diagnostic; a tolerant mode may pass them through with a warning "
        "but must not emit conforming Unicode output containing lone surrogates; "
        "ifcopenshell observed to terminate via process signal on \\Q\\..\\Q\\ payloads; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept encoding defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Defect payload: inject PERSON entities with surrogate-half \\Q\\ payloads.
#
# PERSON #8998: name = 'lone=\Q\55296\Q\'
#   Decimal 55296 = U+D800, the first high-surrogate half.
#   Any attempt to produce UTF-8 from this scalar yields ill-formed bytes.
#
# PERSON #8999: name = 'low=\Q\57343\Q\'
#   Decimal 57343 = U+DFFF, the last low-surrogate half.
#   Covers the upper boundary of the surrogate range.
#
# Satisfies:
#   contains(b'\\Q\\55296\\Q\\')   — primary byte assertion (U+D800)
#   contains(b'55296')            — secondary byte assertion

_original_render = f.render


def _render_with_q_surrogate_payload() -> str:
    text = _original_render()
    person_lines = (
        # \\Q\\55296\\Q\\: U+D800 — first high-surrogate half (not a legal scalar)
        "#8998=PERSON('lone=\\Q\\55296\\Q\\','q-ref-surrogate-U+D800','');\n"
        # \\Q\\57343\\Q\\: U+DFFF — last low-surrogate half (also not a legal scalar)
        "#8999=PERSON('low=\\Q\\57343\\Q\\','q-ref-surrogate-U+DFFF','');\n"
    )
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + person_lines + text[idx:]


f.render = _render_with_q_surrogate_payload  # type: ignore[method-assign]
