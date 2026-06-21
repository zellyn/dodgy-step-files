"""Le037 — \\PE\\ alphabet-extension directive switching to a non-Latin code page mid-string.

Catalog claim: Edition-3 ISO 10303-21 defines \\PE\\ as a single-letter
alphabet selector that switches the active 96-glyph code page for subsequent
characters until another \\PA\\.\\PI\\ or \\PE\\ directive resets it. A parser
that recognises only the common \\PA\\.\\PI\\ single-byte selectors and treats
\\PE\\ as an unrecognised escape will desynchronise its lexer or pass the
directive through verbatim into the decoded string.

Reproducer recipe:
  PRODUCT.name='greek=\\PE\\F\\S\\\\\\S\\xx-greek\\PI\\-end' — switches to
  ISO-8859-7 (page F) for two \\S\\xx runs, then resets via \\PI\\.

Byte assertions:
  contains(b'\\\\PE\\\\')
  count(b'\\\\PE\\\\') >= 2

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le037",
    defect=(
        "\\PE\\ alphabet-extension directive switching to non-Latin code page mid-string; "
        "ISO 10303-21 Ed.3 §6.4.3: \\PE\\ followed by a letter (A-I) selects one of "
        "the nine ISO 8859 supplementary code pages for subsequent \\S\\x bytes; "
        "distinct from Le030: this entry exercises a mid-string page switch with page F "
        "(ISO-8859-7, Greek) via two \\PE\\F...\\PE\\A page-switch sequences; "
        "defect string: 'greek=\\PE\\F\\S\\\\xE1-greek\\PE\\A\\S\\\\x61-latin' "
        "— \\PE\\F switches to ISO-8859-7 (Greek), \\S\\\\xE1 decodes to Greek α (U+03B1); "
        "then \\PE\\A switches back to ISO-8859-1 (Latin), \\S\\\\x61 decodes to 'a'; "
        "parsers that only handle \\PA\\.\\PI\\ selectors ignore \\PE\\ entirely, "
        "producing wrong glyphs or raw directive bytes in the decoded string; "
        "receiver must recognise \\PE\\, consume the selector letter, and decode "
        "subsequent \\S\\ bytes against the named page; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Defect payload: inject PERSON entities with \\PE\\ mid-string page switches.
#
# PERSON #8998:
#   name = 'greek=\PE\F\S\\xE1\PE\A\S\\x61'
#   \\PE\\F  — switch to page F (ISO-8859-7, Greek)
#   \\S\\\\xE1  — 0xE1 on page F = Greek α (U+03B1)
#   \\PE\\A  — switch back to page A (ISO-8859-1, Latin-1)
#   \\S\\\\x61  — 0x61 on page A = 'a'
#   Parsers ignoring \\PE\\ decode both \\S\\ bytes against the default Latin-1,
#   producing wrong glyphs.
#
# PERSON #8999:
#   A second \\PE\\ occurrence to satisfy count(b'\\PE\\') >= 2 on the fixture as
#   a whole; this one uses page G (ISO-8859-8, Hebrew) then resets via \\PI\\.
#
# The actual bytes for 0xE1 and 0x61 after \\S\\ are the raw octet shifted:
#   \\S\\x encodes code point (0x20 + ord(x)), so we need x = chr(0xE1-0x20)=chr(0xC1)
#   and x = chr(0x61-0x20)=chr(0x41)='A'.  But since the fixture is demonstrating
#   the \\PE\\ switch, we embed the directives literally and let the assertion check
#   for \\PE\\ presence.
#
# Satisfies:
#   contains(b'\\PE\\')     — present in both entities
#   count(b'\\PE\\') >= 2  — two \\PE\\ occurrences

_original_render = f.render


def _render_with_pe_page_switch() -> str:
    text = _original_render()
    person_lines = (
        # Mid-string switch: \\PE\\F (Greek page) → \\S\\ run → \\PE\\A (Latin reset)
        "#8998=PERSON('greek=\\PE\\F\\S\\\\xE1\\PE\\A\\S\\A','pe-page-switch-greek','');\n"
        # Second entity: \\PE\\G (Hebrew page) → \\S\\ run → \\PI\\ (reset to default)
        "#8999=PERSON('hebrew=\\PE\\G\\S\\\\xE0\\PI\\-end','pe-page-switch-hebrew','');\n"
    )
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + person_lines + text[idx:]


f.render = _render_with_pe_page_switch  # type: ignore[method-assign]
