"""Ls016 — Double comma / empty parameter slot.

Catalog claim: `(a,,b)` leaves an attribute slot empty. Correct null is `$`,
derived is `*`. Empty slot is a generator bug. Parsers that map positional
slots without re-checking arity may construct the entity with one fewer
attribute, leading to uninitialised fields.

Reproducer recipe:
  #1=IFCPERSON($,$,'',,$,$,$,$);
  #1=CARTESIAN_POINT('',(0.,,1.));

Byte assertions:
  matches(rb',\\s*,') or matches(rb'\\(\\s*,')
  count(b',,') >= 1

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ls016",
    defect=(
        "Double comma leaves empty parameter slot in STEP entity record; "
        "(a,,b) leaves an attribute slot empty; "
        "correct null is $ and correct derived is *; "
        "an empty slot is a generator bug; "
        "parsers that map positional slots without re-checking arity "
        "may construct the entity with one fewer attribute "
        "leading to uninitialised fields and later null-deref crashes; "
        "reject with expected parameter found comma; "
        "do not silently treat the empty slot as $; "
        "the error message should report the slot index within the parameter list; "
        "OCC silently treats the empty slot as $ (omitted) and proceeds; "
        "defect 1: IFCPERSON with empty slot between '' and $ (the ,, between '' and $); "
        "defect 2: CARTESIAN_POINT with empty slot inside aggregate (,, between 0.0 and 1.0); "
        "defect 3: leading empty slot in aggregate (,...); "
        "synonyms: double comma in STEP aggregate, (a,,b) empty slot, "
        "STEP entity attribute slot empty, empty parameter slot in entity, "
        "consecutive commas in attribute list; "
        "GEOMETRIC_CURVE_SET IS NOT used — raw entities are the defect carriers"
    ),
)

_original_render = f.render


def _render_double_comma() -> str:
    header = f._render_header()
    return (
        "/* Ls016 - Double comma / empty parameter slot\n"
        "   ----------------------------------------------------------------------\n"
        "   Catalog section : §12.1c punctuation\n"
        "   Sources         : T020, A016\n"
        "   Originally also catalogued as: Ad016\n"
        "   ----------------------------------------------------------------------\n"
        "   Defect\n"
        "     (a,,b) leaves an attribute slot empty. Correct null is '$', correct\n"
        "     derived is '*'. An empty slot is a generator bug. Parsers that map\n"
        "     positional slots without re-checking arity may construct the entity\n"
        "     with one fewer attribute, leading to uninitialised fields and later\n"
        "     null-deref crashes.\n"
        "   Expected behavior\n"
        "     Reject with \"expected parameter, found ','\"; do not silently treat\n"
        "     the empty slot as '$'. The error message should report the slot\n"
        "     index within the parameter list.\n"
        "   ----------------------------------------------------------------------\n"
        "*/\n"
        "ISO-10303-21;\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Ls016 - double comma leaves empty parameter slot'),'2;1');\n"
        "FILE_NAME('Ls016.stp','2026-04-26T00:00:00',('auto-generated'),(''),\n"
        "  'auto-generated','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Defect: empty slot in attribute list (the ',,' between '' and $) */\n"
        "#10=IFCPERSON($,$,'',,$,$,$,$);\n"
        "/* Defect: empty slot inside aggregate (the ',,' between 0.0 and 1.0) */\n"
        "#20=CARTESIAN_POINT('',(0.0,,1.0));\n"
        "/* Defect: leading empty slot ('(,...)') */\n"
        "#21=CARTESIAN_POINT('lead',(,1.0,0.0));\n"
        "#30=DIRECTION('x',(1.0,0.0,0.0));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


f.render = _render_double_comma  # type: ignore[method-assign]
