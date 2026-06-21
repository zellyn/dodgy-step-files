"""Le020 — String literal exceeds Ed.3 32769-octet limit.

Catalog claim: Ed.3 caps a single STRING literal at 32 769 octets.
Tools embedding base64 thumbnails or long descriptions exceed this silently,
and naive parsers overflow fixed-size string buffers.

Byte assertions: max_string_literal_length > 32768, length > 32768,
                 matches(rb"PERSON\\(\\s*'p1','A{1000,}")
Tier-3: load != "ok"
Expected: occt=reject/reject gmsh=reject ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le020",
    defect=(
        "String literal exceeds Ed.3 32769-octet limit: "
        "PERSON entity carries a string attribute of length 50000 'A' characters; "
        "naive parsers overflow fixed-size string buffers; "
        "spec rejects beyond the limit; tolerant readers may accept and warn but must "
        "guard against integer-overflow in length fields; "
        "the 50000-A string IS the mechanism — file is > 32768 bytes"
    ),
)

# Anchor geometry
p0 = f.cartesian_point((0.0, 0.0, 0.0))
zd = f.direction((0.0, 0.0, 1.0))
xd = f.direction((1.0, 0.0, 0.0))
f.axis2_placement_3d(p0, zd, xd)

_original_render = f.render


def _render_with_long_string():
    text = _original_render()
    # Inject a PERSON entity with a 50000-character string attribute
    long_string = "A" * 50000
    person_line = f"#8999=PERSON('p1','{long_string}','');\n"
    marker = "\nENDSEC;\nEND-ISO-10303-21;\n"
    idx = text.index(marker)
    return text[:idx] + "\n" + person_line + text[idx:]


f.render = _render_with_long_string  # type: ignore[method-assign]
