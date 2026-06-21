"""Le013 — Apostrophe-doubling escape '' confused with string terminator.

Catalog claim: ISO 10303-21 escapes a literal apostrophe inside a string by
doubling it: 'It''s' decodes to It's. State machines that do not treat the
doubled quote as escape mistake mid-string '' for end-of-string + start-of-next,
leading to a misaligned token stream and (in worst cases) heap corruption when
a later write uses the wrong length. Parity matters when an even number of
consecutive apostrophes appears.

Reproducer recipe:
  #1=PERSON('O''Brien','x');   ('O''Brien' is correct STEP; parser must not split it)
  'a''b' decodes to a'b
  '''' decodes to two literal apostrophes
  'O'Brien' — broken producer forgot to double the apostrophe

Byte assertions:
  contains(b"O''Brien") or contains(b"a''b") or contains(b"''''")
  count(b"''") >= 3

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le013",
    defect=(
        "Apostrophe-doubling escape '' confused with string terminator; "
        "ISO 10303-21 §6.4.3.1: a literal apostrophe inside a string is escaped by "
        "doubling it — 'It''s' decodes to the 4-char string It's; "
        "defect 1: 'O''Brien' — parser must NOT split at the doubled quote; "
        "defect 2: '''' — four consecutive apostrophes encode two literal apostrophes; "
        "defect 3: 'a''b' — doubled apostrophe mid-string; "
        "a parser that treats '' as end-of-string + start-of-next desynchronizes the "
        "token stream; subsequent attributes shift by one position; "
        "downstream entity construction fails type-check or builds wrong sub-tree; "
        "receiver must track parity of consecutive apostrophes; "
        "only an odd count terminates the string; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Defect payload: three PERSON entities via render() override, all using
# correctly-doubled apostrophes in the STEP byte stream.
#
# In Python string literals below, '' in the STEP sense must be written as
# the two characters apostrophe-apostrophe; Python raw strings help avoid
# confusion with Python's own escape rules.
#
# PERSON #8997: name = 'O''Brien'   — the canonical example; two apostrophes
#   in sequence represent a single literal apostrophe in the decoded string.
#   A buggy parser splits this at the '' and reads two strings: 'O' and 'Brien'.
#
# PERSON #8998: name = 'a''b'  — minimal doubled-apostrophe mid-string; also
#   exercises the parity counter.
#
# PERSON #8999: name = '''''  — four consecutive apostrophes followed by one
#   to close the string; the four in the middle decode to two literal apostrophes.
#   Written in full STEP: '''' is the name field value (start-quote, '', end-quote
#   gives the empty-apostrophe-string); use ''''' to encode two literal apostrophes.
#
# Satisfies:
#   contains(b"O''Brien")  — #8997
#   contains(b"a''b")      — #8998
#   contains(b"''''")      — #8999 (part of ''''')
#   count(b"''") >= 3      — #8997 has 1, #8998 has 1, #8999 has 2 → total = 4

_original_render = f.render


def _render_with_doubled_apostrophe():
    text = _original_render()
    # Note: in the Python source below, the content inside the outer Python double-quotes
    # is written verbatim as STEP bytes. The STEP string delimiter is the apostrophe.
    #   "PERSON('O''Brien','x','')" — Python string containing STEP with O''Brien
    person_lines = (
        # O''Brien: two apostrophes in sequence are the STEP escape for one literal apostrophe
        '#8997=PERSON(\'O\'\'Brien\',\'x\',\'\');\n'
        # a''b: doubled apostrophe mid-string
        '#8998=PERSON(\'a\'\'b\',\'doubled-mid-string\',\'\');\n'
        # ''''': start-quote + '''' (two doubled apostrophes = two literal apostrophes) + end-quote
        '#8999=PERSON(\'\'\'\'\'\',\'four-consecutive-apostrophes\',\'\');\n'
    )
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + person_lines + text[idx:]


f.render = _render_with_doubled_apostrophe  # type: ignore[method-assign]
