"""Ls030 — Apostrophe inside `/* .. */` comment misread as string delimiter.

Catalog claim: A `/* .. */` comment containing an apostrophe is rejected because the
comment-skip routine and a separate string-literal recognizer share a regex/scanner that
mis-pairs the in-comment apostrophe with the next apostrophe in the file.

Reproducer recipe: `/* plane angle is 'degree' as non-SI unit */` placed between header
and DATA.

Byte assertions:
  matches(rb"/\\*[^*]*'[^*]*\\*/")
  matches(rb"/\\*[^*]*'")

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ls030",
    defect=(
        "Apostrophe inside /* .. */ comment misread as string delimiter in STEP file; "
        "a comment containing an apostrophe is rejected because "
        "the comment-skip routine and a separate string-literal recognizer "
        "share a regex/scanner that mis-pairs the in-comment apostrophe "
        "with the next apostrophe in the file; "
        "ISO 10303-21 §5.3: comments are scanned to the next */ independently of string state; "
        "an apostrophe inside a comment is opaque and must not be matched "
        "as an opening string delimiter; "
        "expected kernel behavior: heal and accept — "
        "comments scanned to next */ independent of any string state; "
        "apostrophe inside comment is opaque; "
        "OCCT silently accepts (load is empty); "
        "OCC auto-heals a spec-level violation; "
        "synonyms: apostrophe inside STEP comment misread, "
        "comment containing single quote breaks parser, "
        "comment apostrophe paired with later quote, "
        "STEP comment quote desyncs scanner, in-comment apostrophe confuses lexer; "
        "GEOMETRIC_CURVE_SET IS NOT used — raw entities are the defect carriers"
    ),
)

_original_render = f.render


def _render_apostrophe_in_comment() -> str:
    header = f._render_header()
    return (
        "/* Ls030 - Apostrophe inside comment misread as string delimiter\n"
        "   ----------------------------------------------------------------------\n"
        "   Catalog section : §12.1c comments\n"
        "   Sources         : T002\n"
        "   Fixture kind    : conformance-probe\n"
        "   ----------------------------------------------------------------------\n"
        "   Defect\n"
        "     A comment containing an apostrophe is rejected because the comment-skip\n"
        "     routine and a separate string-literal recognizer share a regex/scanner\n"
        "     that mis-pairs the in-comment apostrophe with the next apostrophe in\n"
        "     the file.\n"
        "   Expected behavior\n"
        "     Heal and accept: comments scanned to next */ independent of any string\n"
        "     state; apostrophe inside comment is opaque.\n"
        "   ----------------------------------------------------------------------\n"
        "*/\n"
        "ISO-10303-21;\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Ls030 - apostrophe in comment misread as string delimiter'),'2;1');\n"
        "FILE_NAME('Ls030.stp','2026-06-20T00:00:00',('auto-generated'),(''),\n"
        "  'auto-generated','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "/* Defect: apostrophe inside this comment -- scanner must NOT treat it as a string open */\n"
        "/* plane angle is 'degree' as non-SI unit; the apostrophes here are inside the comment */\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=DIRECTION('x',(1.,0.,0.));\n"
        "/* another comment with apostrophe: it's fine inside here */\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


f.render = _render_apostrophe_in_comment  # type: ignore[method-assign]
