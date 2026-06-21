"""Ls034 — Enumeration value missing dotted delimiters or with bad casing.

Catalog claim: ISO 10303-21 enum literals are `.IDENT.` where IDENT is an
EXPRESS-conformant identifier (uppercase letters and digits only). Defects:
missing closing dot, lower-case body, quoted body, missing leading dot.

Reproducer recipe: #1=DIRECTION_FLAG(.true.); #2=DIRECTION_FLAG(TRUE);
  and IFCSIUNIT with missing closing dot after LENGTHUNIT.

Byte assertions:
  contains(b'.LENGTHUNIT,') or contains(b'.true.') or contains(b'(TRUE)') or contains(b'."LEFT".')
  matches(rb'\.[a-z]+\.|\bTRUE\b|\bLEFT\.')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ls034",
    defect=(
        "Enumeration value missing dotted delimiters or with bad casing; "
        "ISO 10303-21 enum literals must be .IDENT. where IDENT is an "
        "EXPRESS-conformant identifier using uppercase letters and digits only; "
        "defect 1: lowercase enum body — .true. instead of .T. (or .TRUE.); "
        "defect 2: unquoted bare identifier without dots — TRUE instead of .TRUE.; "
        "defect 3: missing closing dot — .LENGTHUNIT, instead of .LENGTHUNIT.,; "
        "defect 4: quoted body — .\"LEFT\". instead of .LEFT.; "
        "strict reject: lenient mode may case-fold the identifier "
        "but the surrounding dots are non-negotiable; "
        "the dots are part of the grammar production for ENUMERATION_LITERAL; "
        "see also: Ls035; "
        "synonyms: STEP enum missing dotted delimiters, lowercase enum body, "
        "missing leading dot on STEP enum, quoted enum value, STEP enum value malformed; "
        "GEOMETRIC_CURVE_SET IS NOT used — raw entities are the defect carriers"
    ),
)

_original_render = f.render


def _render_bad_enums() -> str:
    header = f._render_header()
    return (
        "/* Ls034 - Enumeration value missing dotted delimiters or with bad casing\n"
        "   ----------------------------------------------------------------------\n"
        "   Catalog section : §12.1c enumeration token form\n"
        "   Sources         : T035, N021\n"
        "   See also        : Ls035\n"
        "   ----------------------------------------------------------------------\n"
        "   Defect\n"
        "     ISO 10303-21 enum literals are .IDENT. (uppercase, no quotes).\n"
        "     Defect 1: .true. -- lowercase body\n"
        "     Defect 2: TRUE   -- bare identifier without dotted delimiters\n"
        "     Defect 3: .LENGTHUNIT, -- missing closing dot (comma closes slot)\n"
        "     Defect 4: .\"LEFT\". -- quoted body inside the dots\n"
        "   Expected behavior\n"
        "     Strict reject; lenient mode may case-fold but dots are non-negotiable.\n"
        "   ----------------------------------------------------------------------\n"
        "*/\n"
        "ISO-10303-21;\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Ls034 - malformed enumeration literals'),'2;1');\n"
        "FILE_NAME('Ls034.stp','2026-06-20T00:00:00',('auto-generated'),(''),\n"
        "  'auto-generated','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Defect 1: lowercase enum body -- .true. instead of .T. */\n"
        "#1=DIRECTION_FLAG('flag-lc',.true.);\n"
        "/* Defect 2: bare unquoted identifier without dots -- TRUE */\n"
        "#2=DIRECTION_FLAG('flag-bare',TRUE);\n"
        "/* Defect 3: SIUNIT with missing closing dot after LENGTHUNIT */\n"
        "/* .LENGTHUNIT, has comma immediately after identifier — no closing dot */\n"
        "#3=NAMED_UNIT(*,.LENGTHUNIT,$);\n"
        "/* Defect 4: quoted body inside dots -- .\"LEFT\". */\n"
        "#4=CARTESIAN_POINT('pt',(1.,0.,0.));\n"
        "#5=DIRECTION('dir-quoted',(0.,1.,0.));\n"
        "#6=PLACEMENT_FLAG('pf',#4,#5,.\"LEFT\".);\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


f.render = _render_bad_enums  # type: ignore[method-assign]
