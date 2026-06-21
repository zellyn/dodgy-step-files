"""Le010 — \\F\\ font-shift directive consumed wrongly.

Catalog claim: \\F\\ introduces a single-character alternate-font selector (used
for CJK font shifts); exactly one letter follows. Tools sometimes embed
multi-character font tags as if it were an HTML tag (\\F\\bold\\F\\).

Reproducer recipe:
  'mix\\F\\katakana hello'  (illegal multi-letter tag after \\F\\)

Byte assertions:
  contains(b'\\\\F\\\\')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le010",
    defect=(
        "\\F\\ font-shift directive consumed wrongly: multi-character tag after \\F\\; "
        "\\F\\ introduces a single-character alternate-font selector for CJK font shifts; "
        "exactly one letter follows — the selector is always a single byte; "
        "defect: 'mix\\F\\katakana hello' treats \\F\\ like an HTML tag and embeds "
        "multi-character text after it before any closing marker; "
        "a parser that over-consumes eats trailing characters of the string; "
        "the attribute records a truncated or wrong value; "
        "receiver must reject with diagnostic; ignoring the directive is safer "
        "than over-consuming text; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Defect payload: a PERSON entity with a multi-character \\F\\ tag via
# render() override. The string 'mix\\F\\katakana hello' embeds an illegal
# multi-letter token after \\F\\ — the spec allows only a single character.
# A parser treating \\F\\ as an HTML-style open tag over-consumes the input
# and the attribute value ends up truncated.
#
# Satisfies: contains(b'\\F\\')

_original_render = f.render


def _render_with_bad_font_directive():
    text = _original_render()
    # PERSON with multi-character \\F\\ tag: 'katakana' is not a single-char font selector.
    person_line = "#8999=PERSON('mix\\F\\katakana hello','multi-char-font-directive','');\n"
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + person_line + text[idx:]


f.render = _render_with_bad_font_directive  # type: ignore[method-assign]
