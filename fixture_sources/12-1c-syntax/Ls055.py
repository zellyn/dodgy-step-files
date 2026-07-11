"""Ls055 — Unterminated block comment (no closing star-slash) swallows the file.

Catalog claim: ISO 10303-21 §6.3 block comments are delimited by an opening
slash-star and a closing star-slash. ruststep's `combinator.rs::comment`
(`tag("/*") ... tag("*/")`) FAILS if the closer is missing. An unterminated
comment consumes every byte to end-of-file, silently swallowing the section
terminators (ENDSEC / END-ISO-10303-21;). A conformant reader must reject
with an unterminated-comment diagnostic; it must not hang or silently drop
the tail of the file.

Reproducer recipe: a valid entity followed by `/* note ...` with no closing
star-slash before EOF.

Byte assertions:
  count(b'/*') > count(b'*/')
  not_contains(b'END-ISO-10303-21;')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a

Pattern-mined from ricosjp/ruststep combinator.rs::comment (Apache-2.0/MIT
— pattern only, no bytes copied).
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ls055",
    defect=(
        "unterminated block comment consumes the rest of the file; "
        "ISO 10303-21 6.3 block comments open with slash-star and close with "
        "star-slash; the fixture opens a comment in the DATA section and never "
        "closes it, so every byte to end-of-file is consumed as comment text, "
        "silently swallowing the ENDSEC and END-ISO-10303-21 section terminators; "
        "expected kernel behavior: reject with an unterminated-comment "
        "diagnostic; the reader must not hang or silently drop the file tail; "
        "synonyms: unterminated comment, missing star-slash closer, comment "
        "runs to EOF, STEP comment never closed, dangling slash-star; "
        "the unterminated comment is the defect carrier"
    ),
)


def _render_unterminated_comment() -> str:
    header = f._render_header()
    return (
        "ISO-10303-21;\n"
        f"/* {f.catalog_id}: {f.defect} */\n"
        f"{header}\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "/* Defect: this comment is opened but NEVER closed. A conformant reader\n"
        "   must reject with an unterminated-comment diagnostic (ISO 10303-21 6.3).\n"
        "   From the opening slash-star to end of file everything is consumed as\n"
        "   comment text, including what should have been the section terminators.\n"
        "#2=DIRECTION('never-parsed',(1.,0.,0.));\n"
    )


f.render = _render_unterminated_comment  # type: ignore[method-assign]
