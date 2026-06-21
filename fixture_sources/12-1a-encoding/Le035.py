"""Le035 — Encoding directives emitted in Ed.3 UTF-8 file unnecessarily.

Catalog claim: An Ed.3 producer that retains Ed.2 codepaths emits
\\S\\/\\P\\/\\X\\ even though the body is UTF-8 by default. Strict Ed.3
readers that assume raw multi-byte UTF-8 may then double-decode
(interpret \\X\\C3 \\X\\A9 and the byte sequence 0xC3 0xA9 as two different
characters when both were intended as é).

Reproducer recipe:
  file with implementation_level='4' (Ed.3) containing 'caf\\X\\E9';
  or 'caf\\PA\\\\S\\i'.

Byte assertions:
  contains(b'\\\\X\\\\') and matches(rb"'[^']*[\\xc0-\\xff][\\x80-\\xbf]")

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
import re as _re

from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le035",
    defect=(
        "Ed.2 encoding directives emitted in an Ed.3 UTF-8 file unnecessarily; "
        "ISO 10303-21 Ed.3 §6.4: the file body is UTF-8 by default when "
        "implementation_level is '4' or higher; "
        "Ed.3 producers that retain Ed.2 codepaths emit \\X\\E9 or \\PA\\\\S\\i "
        "even though the body is already UTF-8 — causing double-decode; "
        "strict Ed.3 reader interprets raw 0xC3 0xA9 as é AND also decodes "
        "\\X\\E9 as é, producing a doubled or corrupted glyph; "
        "heal and accept: receivers must not assume the file edition matches its header; "
        "defect 1: 'caf\\X\\E9' — \\X\\E9 is the Ed.2 escape for é (latin-1 0xE9) "
        "but also raw UTF-8 byte 0xE9 appears because the body is UTF-8; "
        "defect 2: 'caf\\PA\\\\S\\i' — \\PA\\ selects ISO-8859-1 then \\S\\i is 0xE9=é, "
        "again redundant in an Ed.3 UTF-8 body; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Defect payload: override render() to:
#   1. Change FILE_DESCRIPTION implementation_level to '4' (Ed.3 UTF-8 body).
#   2. Inject PERSON entities with Ed.2 \\X\\ and \\PA\\\\S\\ directives that
#      are redundant/harmful in an Ed.3 body that also carries raw UTF-8.
#
# PERSON #8998: name='caf\X\E9' — \\X\\E9 is the Ed.2 single-byte escape for
#   é (ISO 8859-1 code point 0xE9), but the file body is declared Ed.3 UTF-8.
#   The file also has the raw UTF-8 bytes 0xC3 0xA9 (é) elsewhere, creating
#   the conditions for double-decode by strict Ed.3-only readers.
#
# PERSON #8999: name='caf\PA\\S\i' — \\PA\\ selects ISO-8859-1 (page A) then
#   \\S\\i where 'i' is 0x69 shifted by 0x80 = 0xE9 = é; again pointless in
#   an Ed.3 UTF-8 body.
#
# The raw UTF-8 continuation bytes 0xC3 0xA9 appear in #8997 to satisfy the
# byte assertion: matches(rb"'[^']*[\xc0-\xff][\x80-\xbf]")
#
# Satisfies:
#   contains(b'\\X\\')                              — PERSON #8998 name
#   matches(rb"'[^']*[\xc0-\xff][\x80-\xbf]")      — PERSON #8997 raw UTF-8

_original_render = f.render


def _render_with_ed3_redundant_directives() -> str:
    text = _original_render()

    # Step 1: change implementation_level to '4' (Ed.3) in FILE_DESCRIPTION.
    text = _re.sub(
        r"FILE_DESCRIPTION\((\([^)]*\))\s*,\s*'[^']*'\)",
        r"FILE_DESCRIPTION(\1,'4')",
        text,
        count=1,
    )

    # Step 2: inject PERSON entities with Ed.2 directives in an Ed.3 UTF-8 body.
    person_lines = (
        # Raw UTF-8 bytes for é (0xC3 0xA9) — satisfies the [\xc0-\xff][\x80-\xbf] assertion
        "#8997=PERSON('caf\xc3\xa9','raw-utf8-e-acute','');\n"
        # Ed.2 \\X\\E9 escape for é — unnecessary and misleading in Ed.3 body
        "#8998=PERSON('caf\\X\\E9','ed2-x-escape-in-ed3','');\n"
        # Ed.2 \\PA\\\\S\\ page-select + shifted-byte — redundant in Ed.3 UTF-8 body
        "#8999=PERSON('caf\\PA\\\\S\\i','ed2-pa-s-in-ed3','');\n"
    )
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + person_lines + text[idx:]


f.render = _render_with_ed3_redundant_directives  # type: ignore[method-assign]
