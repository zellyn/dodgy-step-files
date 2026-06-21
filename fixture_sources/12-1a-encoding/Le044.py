"""Le044 — \\X2\\ payload containing UTF-16 surrogate halves.

Catalog claim: ISO 10303-21 Ed.3 §6.4.3 \\X2\\...\\X0\\ wraps 4-hex-digit
groups each denoting one UCS-2 (BMP) scalar. Surrogate halves U+D800-U+DFFF
are not BMP characters; they exist only as paired surrogates of UTF-16.
A Java-vintage exporter that internally holds Java char[] (allowing lone
surrogates) and writes them as \\X2\\Dxxx\\X0\\ produces a malformed STEP file.

Reproducer recipe:
  'lone=\\X2\\D801\\X0\\' — D801 is a high-surrogate half.
  'pair=\\X2\\D801DC37\\X0\\' — high+low surrogate pair.

Byte assertions:
  contains(b'\\\\X2\\\\D801\\\\X0\\\\') or contains(b'\\\\X2\\\\D801DC37\\\\X0\\\\')
  count(b'\\\\X2\\\\') >= 2

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=process_signal
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le044",
    defect=(
        "\\X2\\ payload containing UTF-16 surrogate halves; "
        "ISO 10303-21 Ed.3 §6.4.3: \\X2\\HHHH...\\X0\\ accepts 4-hex-digit groups "
        "each denoting one UCS-2 (BMP) scalar in the range U+0000-U+FFFF; "
        "surrogate halves U+D800-U+DFFF are not BMP scalars; "
        "they exist only as paired surrogates in the UTF-16 transformation format; "
        "defect string (lone): 'lone=\\X2\\D801\\X0\\' — D801 is a high-surrogate half; "
        "defect string (pair): 'pair=\\X2\\D801DC37\\X0\\' — high+low surrogate pair "
        "encoded as a single 8-digit \\X2\\ group (CESU-8-like); "
        "a Java-vintage exporter that internally stores Java char[] may emit lone surrogates "
        "one-by-one into \\X2\\ groups, producing malformed but parseable tokens; "
        "receiver must reject lone surrogates with a precise diagnostic; "
        "either reject paired surrogates (strict) or transparently combine them "
        "into the matching supplementary-plane scalar (lenient, with a warning); "
        "distinct from Le006: Le044 exercises surrogate semantics, not hex run length; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Defect payload: inject PERSON entities with surrogate-half \\X2\\ payloads.
#
# PERSON #8997: name = 'lone=\X2\D801\X0\'
#   D801 (U+D801) is a high-surrogate half; not a legal BMP scalar.
#   A Java exporter emitting char[] one-by-one produces exactly this token.
#
# PERSON #8998: name = 'pair=\X2\D801DC37\X0\'
#   8-digit group: D801 (high surrogate) + DC37 (low surrogate) concatenated.
#   Some CESU-8-aware tools may decode this pair into U+10437 (Deseret A).
#   Strict parsers must reject the surrogate values; lenient parsers warn.
#
# PERSON #8999: name = 'low=\X2\DC00\X0\'
#   DC00 (U+DC00) is a low-surrogate half; covers the low-surrogate boundary.
#   Ensures the fixture tests both high and low surrogate halves.
#
# Satisfies:
#   contains(b'\\X2\\D801\\X0\\')     — primary byte assertion (lone high surrogate)
#   count(b'\\X2\\') >= 2            — secondary byte assertion (multiple \\X2\\ occurrences)

_original_render = f.render


def _render_with_x2_surrogate_payloads() -> str:
    text = _original_render()
    person_lines = (
        # Lone high surrogate: D801 = U+D801 (illegal BMP scalar)
        "#8997=PERSON('lone=\\X2\\D801\\X0\\','x2-lone-high-surrogate-D801','');\n"
        # Surrogate pair in one group: D801DC37 (high+low, CESU-8-like encoding)
        "#8998=PERSON('pair=\\X2\\D801DC37\\X0\\','x2-surrogate-pair-D801DC37','');\n"
        # Low surrogate boundary: DC00 = U+DC00 (first low-surrogate half)
        "#8999=PERSON('low=\\X2\\DC00\\X0\\','x2-lone-low-surrogate-DC00','');\n"
    )
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + person_lines + text[idx:]


f.render = _render_with_x2_surrogate_payloads  # type: ignore[method-assign]
