"""Ls018 — Two consecutive semicolons (`;;`) after instance.

Catalog claim: Trailing extra `;` confuses parsers expecting another `#`
definition or `ENDSEC`. Second `;` may be tokenized as start of an empty
entity, leading to NULL entity-class lookup.

Reproducer recipe: #20=IFCPROJECT('xyz',#5,'',$,$,$,$,(#11),#19);;

Byte assertions:
  contains(b';;')
  count(b';;') >= 2

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ls018",
    defect=(
        "Two consecutive semicolons (;;) after instance in STEP file; "
        "a trailing extra ; confuses parsers expecting another # definition "
        "or an ENDSEC keyword; "
        "the second ; may be tokenized as the start of an empty entity "
        "leading to a NULL entity-class lookup and later "
        "null-deref or garbage type-id dispatch; "
        "strict mode must reject with unexpected ; at top level; "
        "lenient mode must silently drop empty statements "
        "with W_EMPTY_STATEMENT diagnostic; "
        "never construct an empty or NULL entity; "
        "defect 1: IFCPROJECT with double semicolon after instance terminator; "
        "defect 2: DIRECTION with triple semicolon; "
        "cross-oracle: pure-Python Part-21 validator rejects; "
        "OCCT silently accepts (load is empty); "
        "OCC auto-heals a spec-level violation; "
        "synonyms: double semicolon after STEP instance, STEP file has ;;, "
        "extra semicolon between entities, empty entity from double semicolon, "
        "trailing semicolon after instance; "
        "GEOMETRIC_CURVE_SET IS NOT used — raw entities are the defect carriers"
    ),
)

_original_render = f.render


def _render_double_semicolon() -> str:
    header = f._render_header()
    return (
        "/* Ls018 - Two consecutive semicolons (;;) after instance\n"
        "   ----------------------------------------------------------------------\n"
        "   Catalog section : §12.1c punctuation\n"
        "   Sources         : T019, A018\n"
        "   Originally also catalogued as: Ad018\n"
        "   ----------------------------------------------------------------------\n"
        "   Defect\n"
        "     A trailing extra ';' confuses parsers expecting another '#' definition\n"
        "     or an 'ENDSEC' keyword. The second ';' may be tokenized as the start\n"
        "     of an empty entity, leading to a NULL entity-class lookup and later\n"
        "     null-deref or garbage type-id dispatch.\n"
        "   Expected behavior\n"
        "     Strict mode: reject with \"unexpected ';' at top level\".\n"
        "     Lenient mode: silently drop empty statements with W_EMPTY_STATEMENT\n"
        "     diagnostic; never construct an empty / NULL entity.\n"
        "   ----------------------------------------------------------------------\n"
        "*/\n"
        "ISO-10303-21;\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Ls018 - double semicolon after instance'),'2;1');\n"
        "FILE_NAME('Ls018.stp','2026-04-26T00:00:00',('auto-generated'),(''),\n"
        "  'auto-generated','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#10=CARTESIAN_POINT('p',(0.0,0.0,0.0));\n"
        "#11=DIRECTION('x',(1.0,0.0,0.0));\n"
        "/* Defect: two consecutive semicolons after the instance terminator */\n"
        "#20=IFCPROJECT('xyz',#5,'',$,$,$,$,(#11),#10);;\n"
        "/* Defect: triple semicolon */\n"
        "#21=DIRECTION('y',(0.0,1.0,0.0));;;\n"
        "#30=AXIS2_PLACEMENT_3D('placement',#10,#11,$);\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


f.render = _render_double_semicolon  # type: ignore[method-assign]
