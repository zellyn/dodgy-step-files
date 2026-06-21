"""Ad090 — Lower-case `End-ISO-10303-21` token rejected.

Catalog claim: a STEP file ends with `end-iso-10303-21;` (lower-case) rather
than the spec's `END-ISO-10303-21;`. ISO 10303-21 keywords are conventionally
upper-case, but tolerant readers should accept case-folded forms. Strict reader
rejects the entire file at the trailing token.

Reproducer recipe: otherwise-valid STEP file whose last line is
`end-iso-10303-21;` (lower-case).

Byte assertions:
  bytes_ends_with(b'end-iso-10303-21;') or contains(b'end-iso-10303-21;')
  bytes_ends_with(b'end-iso-10303-21;')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad090",
    defect=(
        "lower-case end-iso-10303-21; token at end of file; "
        "ISO 10303-21 keywords should be case-insensitive; "
        "strict reader rejects entire file at trailing lower-case token; "
        "cross-oracle: pure-Python Part-21 validator rejects (E_CLOSE_CASE); "
        "OCCT silently accepts with no diagnostic; "
        "OCCT MANTIS#0031000; See also Le027; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Monkey-patch render() to emit lower-case END-ISO-10303-21 token.
# Satisfies: bytes_ends_with(b'end-iso-10303-21;')
_orig_render = f.render.__func__


def _render_lowercase(self) -> str:
    text = _orig_render(self)
    # Replace upper-case trailer with lower-case version.
    return text.replace("END-ISO-10303-21;\n", "end-iso-10303-21;\n")


import types
f.render = types.MethodType(_render_lowercase, f)
