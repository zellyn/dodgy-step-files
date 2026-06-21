"""Ls013 — Empty parameter list `()` versus typed empty parameter.

Catalog claim: Two distinct empty-list forms exist: a zero-attribute entity
`#1=ABSTRACT_PT()` and an empty typed parameter `IFCMEASURE(())`. Lexical
layer accepts `#1=PRODUCT();` but the schema expects N attributes.

Reproducer recipe:
  #1=BOUNDED_SURFACE();
  #2=IFCMEASURE(IFCLENGTHMEASURE());

Byte assertions:
  contains(b'PRODUCT();') or contains(b'IFCMEASURE(IFCLENGTHMEASURE())')
  matches(rb'PRODUCT\\(\\s*\\)') or contains(b'IFCMEASURE(')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ls013",
    defect=(
        "Empty parameter list () versus typed empty parameter; "
        "two distinct empty-list forms exist: "
        "a zero-attribute entity record: #1=BOUNDED_SURFACE(); "
        "and an empty typed parameter: IFCMEASURE(IFCLENGTHMEASURE()); "
        "the lexical layer accepts #1=PRODUCT(); but the schema expects N attributes "
        "so the semantic layer must reject; "
        "generators emit zero-argument forms when default-construction logic "
        "produces empty slots; "
        "lex layer accepts () as zero-argument record; "
        "semantic layer must reject if schema requires N>0 attributes "
        "with diagnostic 0 attributes expected N; "
        "reject zero-argument typed parameters unless the schema explicitly permits them; "
        "defect: BOUNDED_SURFACE() zero-argument entity where schema requires attributes; "
        "defect: IFCMEASURE(IFCLENGTHMEASURE()) empty typed parameter; "
        "defect: PRODUCT() zero-argument (schema-illegal); "
        "defect: PROPERTY_LIST with nested empty typed parameter; "
        "OCC silently accepts with no diagnostic and loads empty result; "
        "synonyms: empty parameter list versus null, PRODUCT() with no attributes, "
        "zero-attribute STEP entity, schema expects attributes but none provided, "
        "empty parens for typed parameter; "
        "GEOMETRIC_CURVE_SET IS NOT used — raw entities are the defect carriers"
    ),
)

_original_render = f.render


def _render_empty_param_list() -> str:
    header = f._render_header()
    return (
        "/* Ls013 - Empty parameter list () versus typed empty parameter\n"
        "   ----------------------------------------------------------------------\n"
        "   Catalog section : §12.1c parameter syntax\n"
        "   Sources         : T026, N054\n"
        "   See also        : Ad015\n"
        "   ----------------------------------------------------------------------\n"
        "   Defect\n"
        "     Two distinct empty-list forms exist:\n"
        "       - a zero-attribute entity record  : #1=BOUNDED_SURFACE();\n"
        "       - an empty typed parameter        : IFCMEASURE(())\n"
        "     The lexical layer accepts #1=PRODUCT();, but the schema expects N\n"
        "     attributes, so the semantic layer must reject. Generators emit zero-\n"
        "     argument forms when default-construction logic produces empty slots.\n"
        "   Expected behavior\n"
        "     Lex layer accepts () as zero-argument record. Semantic layer must\n"
        "     reject if the schema requires N>0 attributes with the diagnostic\n"
        "     \"0 attributes, expected N\". Reject zero-argument typed parameters\n"
        "     unless the schema explicitly permits them.\n"
        "   ----------------------------------------------------------------------\n"
        "*/\n"
        "ISO-10303-21;\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Ls013 - empty parameter list versus typed empty parameter'),'2;1');\n"
        "FILE_NAME('Ls013.stp','2026-04-26T00:00:00',('auto-generated'),(''),\n"
        "  'auto-generated','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Defect: zero-argument entity record where schema requires N attributes */\n"
        "#10=BOUNDED_SURFACE();\n"
        "/* Defect: empty typed parameter where the schema expects a value */\n"
        "#20=IFCMEASURE(IFCLENGTHMEASURE());\n"
        "/* Defect: zero-argument PRODUCT (schema-illegal) */\n"
        "#30=PRODUCT();\n"
        "/* Defect: nested empty typed parameter inside an aggregate */\n"
        "#40=PROPERTY_LIST((IFCMEASURE(IFCLENGTHMEASURE())));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


f.render = _render_empty_param_list  # type: ignore[method-assign]
