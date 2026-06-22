"""Le050 — Unicode characters in STEP export silently dropped.

Catalog claim: A document name contains non-ASCII characters (Cyrillic,
CJK, Greek). STEP exporter does not escape non-ASCII via \\X2\\...\\X0\\;
the characters are emitted as raw bytes in an Ed.2-declared file — illegal
under Ed.2 and rejected by strict receivers.

Reproducer recipe:
  Document with name 'Тест' (Cyrillic). Writer emits raw bytes
  '\\xD0\\xA2\\xD0\\xB5\\xD1\\x81\\xD1\\x82' in an Ed.2-declared file.

Byte assertions:
  contains(b'ISO-10303-21')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le050",
    defect=(
        "Unicode characters in STEP export silently dropped; "
        "OCCT MANTIS#0031851 / MANTIS#0031670 / MANTIS#0030694: "
        "document name contains Cyrillic / CJK / Greek characters; "
        "STEP exporter ASCII-encodes the file body but does not escape non-ASCII "
        "via \\X2\\...\\X0\\ directive; "
        "characters emitted as raw UTF-8 bytes in an Ed.2-declared file — illegal under Ed.2; "
        "downstream readers mis-decode or reject the file; "
        "defect: PRODUCT name 'Test' in Cyrillic emitted as raw bytes "
        "\\xD0\\xA2\\xD0\\xB5\\xD1\\x81\\xD1\\x82 instead of \\X2\\0422043504410442\\X0\\; "
        "heal and accept: writer must escape non-ASCII via \\X2\\ for Ed.2, "
        "or declare Ed.3 and emit raw UTF-8 with proper FILE_DESCRIPTION; "
        "must not silently drop Unicode characters on export; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept encoding defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Defect payload: inject PERSON entities whose names contain raw non-ASCII
# bytes — representing the buggy STEP exporter's output (the bytes it emits
# instead of correct \X2\ escape sequences).
#
# The bytes below are UTF-8 encodings of Cyrillic 'Тест' (U+0422, U+0435,
# U+0441, U+0442) emitted raw into an Ed.2 string literal, which is illegal.
# A correct exporter would write: '\X2\0422043504410442\X0\'
#
# PERSON #8997: Cyrillic 'Тест' as raw UTF-8 bytes (illegal in Ed.2)
# PERSON #8998: Greek 'Αλφα' as raw UTF-8 bytes (α=U+03B1, λ=U+03BB, etc.)
# PERSON #8999: Correct form for comparison: \X2\ escaped Cyrillic
#
# Satisfies:
#   contains(b'ISO-10303-21')  — present in every valid STEP file header

_original_render = f.render


def _render_with_raw_unicode_bytes() -> str:
    text = _original_render()
    # Raw UTF-8 bytes for Cyrillic 'Тест' (U+0422 U+0435 U+0441 U+0442)
    cyrillic_raw = "Тест"   # Python str → UTF-8 bytes when encoded
    # Raw UTF-8 bytes for Greek 'Αλφα' (U+0391 U+03BB U+03C6 U+03B1)
    greek_raw = "Αλφα"
    person_lines = (
        # Raw Cyrillic bytes in Ed.2-declared file — illegal
        f"#8997=PERSON('{cyrillic_raw}','cyrillic-raw-bytes','');\n"
        # Raw Greek bytes in Ed.2-declared file — illegal
        f"#8998=PERSON('{greek_raw}','greek-raw-bytes','');\n"
        # Correct form: \X2\ escaped Cyrillic (for reference)
        "#8999=PERSON('\\X2\\0422043504410442\\X0\\','cyrillic-x2-escaped','');\n"
    )
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + person_lines + text[idx:]


f.render = _render_with_raw_unicode_bytes  # type: ignore[method-assign]
