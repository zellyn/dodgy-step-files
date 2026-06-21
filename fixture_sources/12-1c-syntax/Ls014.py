"""Ls014 — Untyped (`*`) attribute used where derived not declared / `$` confused with `*`.

Catalog claim: `*` denotes derived/inherited attribute; `$` denotes null
OPTIONAL value. Generators substitute one for the other. Inside aggregate
elements only `$` is permitted as a "no value" placeholder; `*` is an
attribute-level marker only.

Reproducer recipe:
  #1=SI_ENERGY_UNIT((#2),*,$,.JOULE.);
  #1=POLYLINE('',(*,#10,#11));

Byte assertions:
  matches(rb',\\s*\\*\\s*[,)]')
  count(b'*') >= 2

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ls014",
    defect=(
        "Untyped (*) attribute used where derived not declared or $ confused with *; "
        "* denotes a derived or inherited attribute; "
        "$ denotes a null OPTIONAL value; "
        "generators substitute one for the other; "
        "inside aggregate elements only $ is permitted as a no-value placeholder; "
        "* is an attribute-level marker only; "
        "some senders also emit a real value for a derived slot instead of *; "
        "schema-aware kernel must cross-check * / $ against the attribute kind "
        "in the EXPRESS schema; "
        "reject * inside list elements; "
        "emit expected * (derived) rather than a generic type error "
        "when the position is a derived attribute carrying a value; "
        "defect 1: * put in slot 3 where $ (null OPTIONAL) is expected; "
        "defect 2: * inside an aggregate element (only $ may placeholder there); "
        "defect 3: a value supplied where the derived attribute should be *; "
        "defect 4: $ placed in a derived attribute position (should be *); "
        "OCC silently accepts with no diagnostic and loads empty result; "
        "synonyms: dollar versus star in STEP attribute, * used where $ expected, "
        "$ used in derived slot, untyped parameter confusion, "
        "STEP null vs derived marker; "
        "GEOMETRIC_CURVE_SET IS NOT used — raw entities are the defect carriers"
    ),
)

_original_render = f.render


def _render_star_dollar_confusion() -> str:
    header = f._render_header()
    return (
        "/* Ls014 - Untyped (*) attribute used where derived not declared,\n"
        "            or '$' confused with '*'\n"
        "   ----------------------------------------------------------------------\n"
        "   Catalog section : §12.1c parameter tokens\n"
        "   Sources         : T024, Q087, N022, N046\n"
        "   Originally also catalogued as: Ad069\n"
        "   ----------------------------------------------------------------------\n"
        "   Defect\n"
        "     '*' denotes a derived/inherited attribute; '$' denotes a null\n"
        "     OPTIONAL value. Generators substitute one for the other. Inside\n"
        "     aggregate elements only '$' is permitted as a \"no value\" placeholder;\n"
        "     '*' is an attribute-level marker only. Some senders also emit a real\n"
        "     value for a derived slot instead of '*'.\n"
        "   Expected behavior\n"
        "     Schema-aware kernel cross-checks '*' / '$' against the attribute\n"
        "     kind in the EXPRESS schema; reject '*' inside list elements; emit\n"
        "     \"expected '*' (derived)\" rather than a generic type error when the\n"
        "     position is a derived attribute carrying a value.\n"
        "   ----------------------------------------------------------------------\n"
        "*/\n"
        "ISO-10303-21;\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Ls014 - star/dollar misuse in attribute slots'),'2;1');\n"
        "FILE_NAME('Ls014.stp','2026-04-26T00:00:00',('auto-generated'),(''),\n"
        "  'auto-generated','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#10=CARTESIAN_POINT('p',(0.0,0.0,0.0));\n"
        "#11=CARTESIAN_POINT('q',(1.0,0.0,0.0));\n"
        "/* Defect: '*' put in slot 3 where '$' (null OPTIONAL) is expected */\n"
        "#20=SI_ENERGY_UNIT((#10),*,$,.JOULE.);\n"
        "/* Defect: '*' inside an aggregate element (only '$' may placeholder there) */\n"
        "#30=POLYLINE('',(*,#10,#11));\n"
        "/* Defect: a value supplied where the derived attribute should be '*' */\n"
        "#40=DIMENSIONAL_EXPONENTS(0.0,0.0,0.0,0.0,0.0,0.0,42.0);\n"
        "/* Defect: '$' placed in a derived attribute position (should be '*') */\n"
        "#41=NAMED_UNIT($);\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


f.render = _render_star_dollar_confusion  # type: ignore[method-assign]
