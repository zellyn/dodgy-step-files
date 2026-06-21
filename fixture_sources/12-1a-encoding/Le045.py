"""Le045 — String literal at the Edition-3 length limit (32768 characters).

Catalog claim: Edition-3 raises the maximum string-literal length to 32768
characters. A reader that statically allocates a 256-char buffer truncates
silently or faults; a reader that checks against an off-by-one threshold may
reject one too many or too few. The boundary character itself becomes load-bearing.

Byte assertions: max_string_literal_length >= 32768, max_string_literal_length >= 32700
Tier-3: load != "ok"
Expected: occt=reject/reject gmsh=reject ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le045",
    defect=(
        "String literal at exactly 32768 characters (Ed.3 maximum); "
        "readers that statically allocate 256-char buffers truncate or fault; "
        "readers with off-by-one threshold reject one too many or too few; "
        "the boundary character at position 32768 IS the mechanism; "
        "PRODUCT.name carries exactly 32768 'A' characters"
    ),
)

# Anchor geometry
p0 = f.cartesian_point((0.0, 0.0, 0.0))
zd = f.direction((0.0, 0.0, 1.0))
xd = f.direction((1.0, 0.0, 0.0))
f.axis2_placement_3d(p0, zd, xd)

_original_render = f.render


def _render_with_max_string():
    text = _original_render()
    # Inject a PRODUCT entity with a string of exactly 32768 'A' characters
    boundary_string = "A" * 32768
    product_line = f"#8998=PRODUCT('{boundary_string}','boundary','',());\n"
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + product_line + text[idx:]


f.render = _render_with_max_string  # type: ignore[method-assign]
