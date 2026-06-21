"""Le046 — String literal containing every legal printable ASCII character.

Catalog claim: A kernel that does not handle every printable-ASCII byte
(0x20..0x7E) correctly inside a single string literal will mis-parse one
of: embedded apostrophe (must be doubled as ''), backslash (legal literal
in Ed.2 but begins a directive in Ed.3), '=' / '#' / ';' (token boundary
characters at outer scope but legal in strings).

Reproducer recipe:
  PRODUCT.name=' !"#$%&''()*+,-./0123456789:;<=>?@ABC...XYZ[\\]^_'`abc...'
  — exactly one occurrence of each printable ASCII byte.

Byte assertions:
  matches(rb"'[^']* !\"#")
  contains(b"#$%&")

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le046",
    defect=(
        "String literal containing every legal printable ASCII character (0x20..0x7E); "
        "ISO 10303-21 Ed.3 §6.4.4: all printable ASCII bytes are legal inside string literals; "
        "embedded apostrophe must be doubled (''); "
        "embedded backslash is a literal in Ed.2 but begins a directive in Ed.3; "
        "token-boundary characters '=' '#' ';' are legal inside string context but "
        "mishandled by parsers that do not track string state; "
        "defect: kernel that does not handle every printable-ASCII byte correctly "
        "will mis-parse one of: '' apostrophe, backslash, '=' '#' ';'; "
        "round-trip every printable ASCII byte through encode/decode/storage byte-for-byte; "
        "heal and accept; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Defect payload: inject a PERSON entity whose name string spans the full
# printable ASCII range (0x20..0x7E) in order.
#
# Per ISO 10303-21 §6.4.4 the apostrophe (0x27) must be doubled ('') inside
# a string literal. All other printable ASCII bytes — including '#', '=', ';',
# and '\\' — appear once each in their natural positions.
#
# The resulting STEP string body (between the outer apostrophes) is:
#   [SP]!"#$%&''()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~
#
# Satisfies:
#   matches(rb"'[^']* !\"#")   — space, !, ", # at the start of the literal
#   contains(b"#$%&")           — hash, dollar, percent, ampersand

_original_render = f.render


def _render_with_full_printable_ascii() -> str:
    text = _original_render()
    # Build the printable-ASCII string body:
    # 0x20..0x26 = space through &  (no apostrophe yet)
    # 0x27 = apostrophe — doubled as '' in STEP
    # 0x28..0x7E = ( through ~
    printable = (
        " !\"#$%&''"           # 0x20-0x27, apostrophe doubled
        "()*+,-./"             # 0x28-0x2F
        "0123456789"           # 0x30-0x39
        ":;<=>?@"              # 0x3A-0x40
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"  # 0x41-0x5A
        "[\\]^_`"              # 0x5B-0x60
        "abcdefghijklmnopqrstuvwxyz"  # 0x61-0x7A
        "{|}~"                 # 0x7B-0x7E
    )
    person_line = f"#8999=PERSON('{printable}','all-printable-ascii','');\n"
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + person_line + text[idx:]


f.render = _render_with_full_printable_ascii  # type: ignore[method-assign]
