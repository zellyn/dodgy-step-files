"""Le001 — UTF-8 BOM at start of ISO-10303-21;.

Catalog claim: a leading EF BB BF byte sequence appears before the literal
ISO-10303-21; start token. Strict parsers fail on the first non-ASCII byte.
In Ed.3 a leading BOM is harmless data but still not part of the magic.

Byte assertions: bytes_starts_with(b'\\xef\\xbb\\xbf'), matches(rb'\\xef\\xbb\\xbf')
Tier-3: load != "ok"
Expected: occt=reject/reject gmsh=reject ifc=reject
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Le001",
    defect=(
        "UTF-8 BOM (EF BB BF) at start of file before ISO-10303-21; magic line; "
        "spec framing grammar requires ISO-10303-21; as first non-whitespace token; "
        "strict parsers fail on first non-ASCII byte; "
        "heal: strip single leading UTF-8 BOM at offset 0 with warning; "
        "reject UTF-16/UTF-32 BOMs with E_UNEXPECTED_BOM; "
        "the three BOM bytes ARE the first bytes of the rendered file"
    ),
)

# Minimal geometry anchor
origin = f.cartesian_point((0.0, 0.0, 0.0))
zdir   = f.direction((0.0, 0.0, 1.0))
xdir   = f.direction((1.0, 0.0, 0.0))
f._emit_raw(f"AXIS2_PLACEMENT_3D('placement',#{origin.eid},#{zdir.eid},#{xdir.eid})")


_original_render = f.render


def _render_with_utf8_bom():
    text = _original_render()
    # Prepend the UTF-8 BOM (EF BB BF) as the very first bytes of the file.
    # The comment and ISO-10303-21; header follow immediately after.
    bom = "﻿"  # Python str representation of UTF-8 BOM
    return bom + text


f.render = _render_with_utf8_bom  # type: ignore[method-assign]
