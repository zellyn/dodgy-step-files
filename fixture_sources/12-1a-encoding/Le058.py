"""Le058 — Final record before `ENDSEC;` lacks trailing newline at EOF.

Catalog claim: ISO 10303-21 §6.2 specifies that a record is terminated
by `;`; the spec is silent on whether a trailing newline is required
after the final `;` of the file. A producer may emit the file body with
`..);ENDSEC;END-ISO-10303-21;` and no trailing `\\n`. POSIX tools that
read line-by-line drop the last line if it lacks a `\\n` — the final
record (or the `END-ISO-10303-21;` terminator) is silently lost.

Reproducer recipe:
  A file whose byte stream ends `..);ENDSEC;END-ISO-10303-21;` with NO
  trailing `\\n` and NO newline between the last DATA-section record and
  `ENDSEC;`. The fixture is byte-exact at EOF.

Byte assertions:
  matches(rb'\\);ENDSEC;END-ISO-10303-21;\\Z') or matches(rb'\\);ENDSEC;')
  not_contains(b'ENDSEC;\\nEND-ISO-10303-21;\\n') or contains(b';ENDSEC;END-ISO-10303-21;')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le058",
    defect=(
        "Final record before ENDSEC lacks trailing newline at EOF; "
        "ISO 10303-21 §6.2: record terminator is ';'; "
        "spec is silent on whether a trailing newline is required after the final ';'; "
        "a producer may emit the file body ending in );ENDSEC;END-ISO-10303-21; "
        "with no trailing newline anywhere; "
        "POSIX tools that read line-by-line drop the last line if it lacks a newline — "
        "the final record or the END-ISO-10303-21; terminator is silently lost; "
        "cousin defect: missing newline between the last DATA-section record and ENDSEC; "
        "receiver must tokenise on ';' alone; treat EOF as a valid record-and-section "
        "terminator if the preceding ';'-terminated record has been seen; "
        "never require a trailing newline; "
        "lexers that scan line-by-line should be replaced or wrapped with a ';'-aware "
        "preprocessor; do not reject missing-trailing-newline files; "
        "sibling of Le056/Le057; see also Le054; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Defect payload: override render() to strip the canonical
# `\nENDSEC;\nEND-ISO-10303-21;\n` tail and replace it with
# `;ENDSEC;END-ISO-10303-21;` (no newlines, no trailing newline at all),
# so the file ends exactly at the last `;` character.
#
# The injected PERSON entity whose line ends immediately in `;` (no `\n`)
# before `ENDSEC;` is the specimen record.
#
# Satisfies:
#   matches(rb');ENDSEC;END-ISO-10303-21;\Z')  — no trailing newline at EOF
#   contains(b';ENDSEC;END-ISO-10303-21;')      — no newline before ENDSEC

_original_render = f.render


def _render_no_trailing_newline() -> str:
    text = _original_render()
    # The canonical tail produced by render() is "\nENDSEC;\nEND-ISO-10303-21;\n"
    # We insert one more PERSON entity, then close the file without any newlines.
    person_line = "#8999=PERSON('no-trailing-newline-defect','eof-without-lf','');"
    # Strip the canonical tail; rebuild without any newlines between the
    # final DATA record, ENDSEC, and END-ISO-10303-21 (and no trailing \n).
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    # Everything up to the marker (the last DATA entity line), then our
    # new person line immediately followed by ENDSEC and the file terminator
    # all on one run with no intervening newlines, and no trailing newline.
    return text[:idx] + "\n" + person_line + "ENDSEC;END-ISO-10303-21;"


f.render = _render_no_trailing_newline  # type: ignore[method-assign]
