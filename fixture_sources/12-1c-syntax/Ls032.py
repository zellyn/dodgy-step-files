"""Ls032 — Comment longer than implementation buffer.

Catalog claim: stepcode hardcodes an 8 KiB ceiling on comment body length.
Files with multi-page log banners exceed this and trip rejection.

Reproducer recipe: Single /* .. */ containing >8192 characters before first DATA; instance.

Byte assertions:
  length > 8192
  length > 8000

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ls032",
    defect=(
        "Comment longer than implementation buffer in STEP file; "
        "stepcode hardcodes an 8 KiB ceiling (MAX_COMMENT_LENGTH 8192) on comment body length; "
        "files with multi-page log banners exceed this and trip rejection; "
        "ISO 10303-21 imposes no length limit on comments — only memory bounds apply; "
        "a conforming processor must never silently truncate or reject a comment solely for length; "
        "the defect is a single /* .. */ block whose body exceeds 8192 characters "
        "placed before the DATA section; "
        "strict conformance: the comment is valid; any reader that rejects it has a fixed-buffer bug; "
        "synonyms: STEP comment exceeds buffer, 8KB comment limit, "
        "multi-page log banner in STEP, long comment rejected by stepcode, "
        "huge STEP comment overflows buffer; "
        "GEOMETRIC_CURVE_SET IS NOT used — raw entities are the defect carriers"
    ),
)

_original_render = f.render

# Build the oversized comment body: over 8192 characters
_LONG_COMMENT_BODY = (
    "   Ls032 - Comment longer than implementation buffer\n"
    "   =========================================================================\n"
    "   Catalog section : §12.1c comments\n"
    "   Sources         : T004 (MAX_COMMENT_LENGTH 8192)\n"
    "   =========================================================================\n"
    "   Defect\n"
    "     stepcode hardcodes an 8 KiB ceiling on comment body length. Files with\n"
    "     multi-page log banners exceed this and trip rejection. ISO 10303-21 has\n"
    "     no comment-length limit; memory-bound only.\n"
    "   Expected behavior\n"
    "     Comment length is unbounded (memory-bound only); never silently truncate.\n"
    "   =========================================================================\n"
    "   BEGIN EXTENDED LOG BANNER\n"
    "   =========================================================================\n"
) + (
    "   This comment body is intentionally padded to exceed the 8192-byte ceiling\n"
    "   that stepcode and several other implementations impose. A conforming reader\n"
    "   must accept arbitrarily long comment bodies without truncation or rejection.\n"
    "   The following lines contain generated padding to push the total comment body\n"
    "   length well past 8 KiB (8192 bytes). The content is structurally identical\n"
    "   to a typical multi-page export log banner that a CAD system might prepend.\n"
    "\n"
) * 20 + (
    "   Status      : Export succeeded\n"
    "   Tool        : CAD Research Suite v1.0 (auto-generated fixture)\n"
    "   Date        : 2026-06-20T00:00:00Z\n"
    "   Schema      : AUTOMOTIVE_DESIGN\n"
    "   Entities    : 2 (CARTESIAN_POINT, DIRECTION)\n"
    "   =========================================================================\n"
    "   END EXTENDED LOG BANNER\n"
    "   =========================================================================\n"
)


def _render_long_comment() -> str:
    header = f._render_header()
    return (
        "/*\n"
        + _LONG_COMMENT_BODY
        + "*/\n"
        "ISO-10303-21;\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Ls032 - comment longer than implementation buffer'),'2;1');\n"
        "FILE_NAME('Ls032.stp','2026-06-20T00:00:00',('auto-generated'),(''),\n"
        "  'auto-generated','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=DIRECTION('x',(1.,0.,0.));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


f.render = _render_long_comment  # type: ignore[method-assign]
