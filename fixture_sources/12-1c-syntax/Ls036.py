"""Ls036 — Binary literal `"…"` malformed (bit-count nibble or hex case).

Catalog claim: ISO 10303-21 BINARY syntax is `"<n><hex>*"` where `<n>` is
0–3 indicating unused bits in the final hex digit; hex digits are uppercase,
even-count is required. Defects: lower-case hex, wrong leading nibble,
missing leading nibble, odd hex-digit count.

Reproducer recipe: attributes with "0dead", "4DEAD", "FF", "3DEAD" binary literals.

Byte assertions:
  contains(b'"0dead"') or contains(b'"4DEAD"') or contains(b'"FF"') or contains(b'"3DEAD"')
  count(b'"') >= 4

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ls036",
    defect=(
        "Binary literal malformed: bit-count nibble or hex case defects; "
        "ISO 10303-21 BINARY syntax is \"<n><hex>*\" "
        "where <n> is 0-3 indicating the number of unused bits in the final hex digit; "
        "hex digits must be uppercase and even-count pairs are required; "
        "defect 1: lowercase hex -- \"0dead\" instead of \"0DEAD\"; "
        "defect 2: wrong leading nibble -- \"4DEAD\" (nibble must be 0, 1, 2, or 3); "
        "defect 3: missing leading nibble altogether -- \"FF\" has no nibble prefix; "
        "defect 4: odd hex-digit count -- \"3DEAD\" has 4 hex digits after the nibble "
        "which is correct count (4 is even), "
        "but \"3DAD\" would have an odd count (3 hex digits is wrong); "
        "strict processors must reject all malformed forms; "
        "lenient mode may accept lowercase but must warn; "
        "synonyms: malformed BINARY literal in STEP, binary literal lowercase hex, "
        "wrong leading nibble on BINARY, odd hex-digit count in STEP binary, "
        "BINARY missing leading nibble; "
        "GEOMETRIC_CURVE_SET IS NOT used — raw entities are the defect carriers"
    ),
)

_original_render = f.render


def _render_bad_binary() -> str:
    header = f._render_header()
    return (
        "/* Ls036 - Binary literal malformed (bit-count nibble or hex case)\n"
        "   ----------------------------------------------------------------------\n"
        "   Catalog section : §12.1c binary-literal grammar\n"
        "   Sources         : T036, A024, N020\n"
        "   ----------------------------------------------------------------------\n"
        "   Defect\n"
        "     ISO 10303-21 BINARY syntax: \"<n><HEX>*\" where n in {0,1,2,3}.\n"
        "     Defect 1: \"0dead\" -- lowercase hex digits (must be uppercase)\n"
        "     Defect 2: \"4DEAD\" -- leading nibble 4 is out of range {0,1,2,3}\n"
        "     Defect 3: \"FF\"   -- missing leading nibble entirely\n"
        "     Defect 4: \"3DAD\" -- odd hex-digit count after nibble (must be even)\n"
        "   Expected behavior\n"
        "     Strict reject all four forms; lenient may accept lowercase with warning.\n"
        "   ----------------------------------------------------------------------\n"
        "*/\n"
        "ISO-10303-21;\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Ls036 - malformed BINARY literals'),'2;1');\n"
        "FILE_NAME('Ls036.stp','2026-06-20T00:00:00',('auto-generated'),(''),\n"
        "  'auto-generated','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Defect 1: lowercase hex digits in binary literal -- \"0dead\" */\n"
        "#1=BINARY_ATTR('lc-hex',\"0dead\");\n"
        "/* Defect 2: leading nibble out of range -- \"4DEAD\" (nibble must be 0-3) */\n"
        "#2=BINARY_ATTR('bad-nibble',\"4DEAD\");\n"
        "/* Defect 3: missing leading nibble entirely -- \"FF\" */\n"
        "#3=BINARY_ATTR('no-nibble',\"FF\");\n"
        "/* Defect 4: odd hex-digit count after nibble -- \"3DAD\" (3 hex digits, not even) */\n"
        "#4=BINARY_ATTR('odd-count',\"3DAD\");\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


f.render = _render_bad_binary  # type: ignore[method-assign]
