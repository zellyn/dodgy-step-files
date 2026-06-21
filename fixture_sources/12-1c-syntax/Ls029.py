"""Ls029 — Comment terminator absent — runs through EOF.

Catalog claim: `/* .. ` opens a comment that is never closed; lexer scans past EOF if
loop only terminates on `*/`. One-byte read past mmap'd file boundary; weaponizable
for info leak.

Reproducer recipe: `ISO-10303-21; HEADER; .. ENDSEC; DATA; /* unterminated`

Byte assertions:
  bytes_ends_with(b'closing it') or matches(rb'(?s)/\\*[^*]+$')
  matches(rb'(?s)/\\*[^*]*$')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ls029",
    defect=(
        "Comment terminator absent in STEP file — unterminated comment runs through EOF; "
        "/* opens a comment that is never closed; "
        "lexer scans past EOF if loop only terminates on */; "
        "one-byte read past mmap'd file boundary is weaponizable for information leak; "
        "ISO 10303-21 §5.3 requires every /* to be matched by a closing */; "
        "strict reader must reject with E_UNTERMINATED_COMMENT; "
        "lexer must check pos < end on every advance and emit the diagnostic at EOF; "
        "cross-oracle: pure-Python Part-21 validator rejects (E_NO_CLOSE); "
        "OCCT silently accepts (load is empty); "
        "OCC auto-heals a spec-level violation; "
        "synonyms: unclosed STEP comment runs through EOF, "
        "comment without closing star-slash, STEP lexer reads past file end, "
        "/* without */ in STEP, comment terminator missing; "
        "GEOMETRIC_CURVE_SET IS NOT used — raw entities are the defect carriers"
    ),
)

_original_render = f.render


def _render_unterminated_comment() -> str:
    header = f._render_header()
    return (
        "/* Ls029 - Comment terminator absent -- runs through EOF\n"
        "   ----------------------------------------------------------------------\n"
        "   Catalog section : §12.1c comments\n"
        "   Sources         : A007, N028\n"
        "   See also        : Le015\n"
        "   ----------------------------------------------------------------------\n"
        "   Defect\n"
        "     /* .. opens a comment that is never closed; lexer scans past EOF if\n"
        "     the loop only terminates on */. One-byte read past mmap'd file boundary;\n"
        "     weaponizable for info leak.\n"
        "   Expected behavior\n"
        "     Reject with E_UNTERMINATED_COMMENT: lexer must check pos < end on every\n"
        "     advance and emit the diagnostic at EOF.\n"
        "   ----------------------------------------------------------------------\n"
        "*/\n"
        "ISO-10303-21;\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Ls029 - unterminated comment runs through EOF'),'2;1');\n"
        "FILE_NAME('Ls029.stp','2026-06-20T00:00:00',('auto-generated'),(''),\n"
        "  'auto-generated','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=DIRECTION('x',(1.,0.,0.));\n"
        "/* Defect: this comment is never closed; lexer must detect EOF while scanning for closing it"
    )


f.render = _render_unterminated_comment  # type: ignore[method-assign]
