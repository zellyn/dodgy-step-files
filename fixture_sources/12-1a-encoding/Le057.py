"""Le057 — Records terminated with ;\\n plus extra blank lines between records.

Catalog claim: ISO 10303-21 §6.2 allows arbitrary whitespace (including
newlines) between records; the record terminator is the ';'. A producer
that emits records with trailing blank lines (;\\n\\n) is technically
conformant but stresses streaming tokenisers that special-case ;\\n as
"next record starts here". Mixing ;\\n, ;\\n\\n, and ; followed immediately
by the next record on the same line is non-canonical.

Reproducer recipe:
  A DATA section where some records end with ;\\n (immediate next record),
  others end with ;\\n\\n (blank line between), and one record runs ;
  followed by another record on the same line.

Byte assertions:
  matches(rb';\\n\\n') or matches(rb';\\n#')
  count(b';\\n\\n') >= 1 or count(b';\\n') >= 3

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le057",
    defect=(
        "Records terminated with ;\\n plus extra blank lines between records; "
        "ISO 10303-21 §6.2: record terminator is ';'; "
        "arbitrary whitespace (including newlines) between records is allowed; "
        "producers that emit ;\\n\\n (blank line after each record) are technically conformant "
        "but stress streaming tokenisers that special-case ;\\n as a record boundary; "
        "defect: DATA section mixes three EOR styles within one file — "
        ";\\n (no separator), ;\\n\\n (blank line), and ; on same line as next record; "
        "non-canonical mixing is the defect — inconsistency harder to diagnose than "
        "a uniformly long-form or uniformly compact file; "
        "receiver must tokenise on ';' alone and treat all inter-record whitespace "
        "(including blank lines) as ignorable; never reject for EOR whitespace variation; "
        "sibling of Le056; see also Le054, Le058; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Defect payload: override render() to insert PERSON entities with three
# different EOR whitespace styles in the same DATA section:
#
#   Style A: ;\\n  — record ends, next begins immediately on next line
#   Style B: ;\\n\\n — blank line between records
#   Style C: ; followed by next entity on the SAME line (no newline at all)
#
# All three styles are spec-conformant per §6.2; the inconsistency within
# one file is the defect. A tokeniser that relies on line-based scanning
# instead of ';'-based tokenising may mis-frame one or more styles.
#
# Satisfies:
#   matches(rb';\\n\\n')    — at least one blank line between records (Style B)
#   count(b';\\n\\n') >= 1  — at least one blank-line separator
#   count(b';\\n') >= 3    — multiple ;\\n sequences present

_original_render = f.render


def _render_with_mixed_eor_whitespace() -> str:
    text = _original_render()
    # Style A: ;\\n  — standard, immediate next record on next line
    # Style B: ;\\n\\n — blank line between (the non-canonical defect)
    # Style C: ; followed by next on same line (no separator newline)
    #
    # We inject three PERSON entities demonstrating the three styles.
    # The blank line after #8997 is Style B; #8998 and #8999 are on one line
    # (Style C between them); #8999 ends with ;\\n (Style A back to normal).
    mixed_lines = (
        "#8997=PERSON('style-a-immediate','no-blank-line','');\n"
        "\n"  # blank line = Style B (;\\n\\n pattern — the blank is HERE)
        "#8998=PERSON('style-b-blank-line','blank-line-before','');"
        "#8999=PERSON('style-c-same-line','next-on-same-line','');\n"
    )
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + mixed_lines + text[idx:]


f.render = _render_with_mixed_eor_whitespace  # type: ignore[method-assign]
