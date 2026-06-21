"""Le014 — Apostrophe inside a \\X2\\...\\X0\\ block decoded as string close.

Catalog claim: Scanner that counts apostrophe parity but does not first
identify hex-escape blocks may treat hex digits like 27 (which is the ASCII
apostrophe code point) as a closing quote.  The recogniser must consume
\\X\\ (exactly two hex digits), \\X2\\...\\X0\\, etc. before applying
apostrophe parity.

Reproducer recipe: 'pre\\X\\27post'

Byte assertions:
  contains(b'\\X\\27')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le014",
    defect=(
        "Apostrophe inside \\X\\27 hex-escape block decoded as string close; "
        "ISO 10303-21 §12.1a: \\X\\HH directive consumes exactly two hex digits "
        "and the byte value they encode is NOT an apostrophe delimiter; "
        "hex pair 27 is U+0027, the apostrophe code point; "
        "a scanner that applies apostrophe parity before consuming \\X\\-escape blocks "
        "reads \\X\\27 as: literal '\\', 'X', '\\', closing apostrophe (27 ignored as next token); "
        "the string 'pre\\X\\27post' must parse to the 8-char string pre'post; "
        "receiver must scan control directives before counting apostrophe parity; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Defect payload: inject a PERSON entity whose name contains \\X\\27 (the
# \\X\\ single-byte escape for U+0027, the apostrophe).  A buggy scanner
# that counts apostrophe parity without first resolving \\X\\ directives
# will stop at the '27' and misparse the token stream.
#
# Satisfies: contains(b'\\X\\27')

_original_render = f.render


def _render_with_x27_escape():
    text = _original_render()
    # PERSON name: 'pre\X\27post'
    # In the STEP byte stream the characters are:
    #   apostrophe  p r e  \X\27  p o s t  apostrophe
    # The \X\27 directive encodes U+0027 (apostrophe); a conforming parser
    # MUST NOT treat the code-point value 27 as a string terminator.
    person_line = "#8999=PERSON('pre\\X\\27post','apostrophe-in-x-escape','');\n"
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + person_line + text[idx:]


f.render = _render_with_x27_escape  # type: ignore[method-assign]
