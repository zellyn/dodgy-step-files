"""Ls017 — Trailing comma at end of aggregate.

Catalog claim: Aggregates do not permit trailing commas. JS/Python-influenced
generators emit `(1.,2.,3.,)`. Recursive-descent grammars that accept it
append a default-constructed element, mismatching schema-declared count.

Reproducer recipe: #1=DIRECTION('',(1.,0.,0.,));

Byte assertions:
  matches(rb',\\s*\\)')
  count(b',)') >= 1

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ls017",
    defect=(
        "Trailing comma at end of aggregate in STEP file; "
        "ISO 10303-21 does not permit trailing commas in aggregates; "
        "JS- or Python-influenced generators routinely emit (1.,2.,3.,); "
        "recursive-descent grammars that silently accept the trailing comma "
        "may append a default-constructed element "
        "mismatching the schema-declared element count "
        "and propagating uninitialised data downstream; "
        "strict reject required; "
        "lenient mode must strip and warn; "
        "never expand the trailing comma into an extra element; "
        "defect 1: DIRECTION('x',(1.0,0.0,0.0,)) trailing comma after last coordinate; "
        "defect 2: DIRECTION('z',(0.0,0.0,1.0),) trailing comma after last attribute; "
        "defect 3: POLYLINE with trailing comma in reference list (#10,#20,#30,); "
        "OCC silently accepts with diagnostic but loads empty result; "
        "synonyms: trailing comma in STEP aggregate, (1.,2.,3.,) extra comma, "
        "JS-style trailing comma in STEP, extra comma at end of list, "
        "aggregate ends with comma; "
        "GEOMETRIC_CURVE_SET IS NOT used — raw entities are the defect carriers"
    ),
)

_original_render = f.render


def _render_trailing_comma() -> str:
    header = f._render_header()
    return (
        "/* Ls017 - Trailing comma at end of aggregate\n"
        "   ----------------------------------------------------------------------\n"
        "   Catalog section : §12.1c punctuation\n"
        "   Sources         : A017, N051\n"
        "   Originally also catalogued as: Ad017\n"
        "   ----------------------------------------------------------------------\n"
        "   Defect\n"
        "     Aggregates do not permit trailing commas in ISO 10303-21. JS- or\n"
        "     Python-influenced generators routinely emit (1.,2.,3.,). Recursive-\n"
        "     descent grammars that silently accept the trailing comma may append\n"
        "     a default-constructed element, mismatching the schema-declared\n"
        "     element count and propagating uninitialised data downstream.\n"
        "   Expected behavior\n"
        "     Strict reject; lenient mode strip and warn. Never expand the trailing\n"
        "     comma into an extra element.\n"
        "   ----------------------------------------------------------------------\n"
        "*/\n"
        "ISO-10303-21;\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Ls017 - trailing comma at end of aggregate'),'2;1');\n"
        "FILE_NAME('Ls017.stp','2026-04-26T00:00:00',('auto-generated'),(''),\n"
        "  'auto-generated','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#10=CARTESIAN_POINT('origin',(0.0,0.0,0.0));\n"
        "/* Defect: trailing comma after the last element of the coordinate list */\n"
        "#20=DIRECTION('x',(1.0,0.0,0.0,));\n"
        "/* Defect: trailing comma after the last attribute of the entity record */\n"
        "#30=DIRECTION('z',(0.0,0.0,1.0),);\n"
        "/* Defect: trailing comma in a reference list */\n"
        "#31=POLYLINE('seq',(#10,#20,#30,));\n"
        "#40=AXIS2_PLACEMENT_3D('placement',#10,#20,$);\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


f.render = _render_trailing_comma  # type: ignore[method-assign]
