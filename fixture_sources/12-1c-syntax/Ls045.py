"""Ls045 — Print/control directives appearing outside string-literal context.

Catalog claim: Control directives like `\\X\\`, `\\S\\`, `\\F\\`, `\\N\\` are valid only
inside `'..'` string literals. Tools that pre-process content textually sometimes leave
directives in BINARY values, ENUMERATION names, or between top-level tokens.

Reproducer recipe: `#1=DIRECTION('',(1.\\X\\09,0.,0.));`

Byte assertions:
  matches(rb"\\(\\s*\\d+\\.\\\\X\\\\")
  matches(rb"\\\\X\\\\09")

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ls045",
    defect=(
        "Print/control directives appearing outside string-literal context; "
        "control directives like \\X\\, \\S\\, \\F\\, \\N\\ are valid only inside '..' string literals; "
        "tools that pre-process content textually sometimes leave directives "
        "in BINARY values, ENUMERATION names, or between top-level tokens; "
        "defect 1: \\X\\09 escape sequence appears in a numeric coordinate slot "
        "of a DIRECTION entity — between the opening paren and the first real number; "
        "the coordinate list (1.\\X\\09,0.,0.) embeds a control directive "
        "between the REAL value and the separator comma; "
        "ISO 10303-21 §5.2: print control directives are only valid inside string literals; "
        "expected kernel behavior: strict reject; lenient mode may strip the directive and warn; "
        "synonyms: X escape outside string literal, STEP control directive in BINARY, "
        "directive in enumeration name, backslash X in non-string slot, "
        "control directive between top-level tokens; "
        "GEOMETRIC_CURVE_SET IS NOT used — raw entities are the defect carriers"
    ),
)

_original_render = f.render


def _render_directive_outside_string() -> str:
    header = f._render_header()
    return (
        "/* Ls045 - Print/control directives appearing outside string-literal context\n"
        "   ----------------------------------------------------------------------\n"
        "   Catalog section : §12.1c lexical / directive scope\n"
        "   Sources         : N047\n"
        "   ----------------------------------------------------------------------\n"
        "   Defect\n"
        "     Control directives (\\X\\, \\S\\, \\F\\, \\N\\) are valid only inside\n"
        "     '..' string literals. Tools that pre-process content textually\n"
        "     sometimes leave directives in BINARY values, ENUMERATION names,\n"
        "     or between top-level tokens.\n"
        "   Expected behavior\n"
        "     Strict reject; lenient mode may strip and warn.\n"
        "   ----------------------------------------------------------------------\n"
        "*/\n"
        "ISO-10303-21;\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Ls045 - control directives outside string context'),'2;1');\n"
        "FILE_NAME('Ls045.stp','2026-06-20T00:00:00',('auto-generated'),(''),\n"
        "  'auto-generated','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Defect 1: \\X\\09 (horizontal tab escape) embedded in a coordinate list */\n"
        "/* The directive appears after the real number 1. outside any string literal */\n"
        "#1=DIRECTION('',(1.\\X\\09,0.,0.));\n"
        "/* Defect 2: \\N\\ (newline directive) embedded between entity tokens */\n"
        "#2=CARTESIAN_POINT(''\\N\\,(0.,0.,0.));\n"
        "/* Defect 3: \\S\\ (shift directive) left inside an ENUMERATION slot */\n"
        "#3=FACE_SURFACE('',(),$,\\S\\.T.);\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


f.render = _render_directive_outside_string  # type: ignore[method-assign]
