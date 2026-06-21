"""Ls003 — Lower-case 'e' exponent or whitespace around exponent.

Catalog claim: ISO 10303-21 specifies upper-case E for the REAL exponent;
lower-case e, embedded whitespace (1.5 E+3), or + sign in the exponent
(1e+18) are non-conforming. Locale-aware printers also produce these.

Reproducer recipe: (1.5e+3,0.,0.), (1.5 E+3,0.,0.), 1.E+18.

Byte assertions:
  matches(rb'\d[eE]\+?\d') and (matches(rb'\d e\d') or matches(rb'\d\.?e[+-]?\d'))
  matches(rb'\d[Ee][+-]?\d')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ls003",
    defect=(
        "Lower-case e exponent or whitespace around exponent in REAL literal; "
        "ISO 10303-21 specifies upper-case E for the REAL exponent; "
        "lower-case e, embedded whitespace (1.5 E+3), or + sign in the exponent "
        "(1e+18) are all non-conforming; locale-aware printers produce these variants; "
        "defect: DIRECTION with lower-case e exponent (1.5e+3) in the first coordinate, "
        "whitespace before exponent (0.5 E+0) in the second coordinate, "
        "and explicit plus sign in exponent (1.0e+0) in the third coordinate; "
        "receiver must lex permissively but emit a warning for each non-canonical subset; "
        "must not silently accept without diagnostic; "
        "also: VECTOR magnitude uses 1.0e+1 (lower-case e with plus sign); "
        "bug-reporter synonyms: lowercase e in REAL exponent, 1e+18 instead of 1E+18, "
        "whitespace in REAL exponent, STEP exponent has plus sign, "
        "non-standard exponent in STEP; "
        "GEOMETRIC_CURVE_SET IS NOT used — DIRECTION entity is the defect carrier"
    ),
)

# Override render() to emit the defect: lower-case e exponents and whitespace variants.
_original_render = f.render


def _render_lowercase_exponent() -> str:
    header = f._render_header()
    return (
        f"ISO-10303-21;\n"
        f"/* {f.catalog_id}: {f.defect} */\n"
        f"{header}\n"
        f"DATA;\n"
        f"/* Defect 1: lower-case 'e' exponent: 1.5e+3 */\n"
        f"/* Defect 2: whitespace before exponent: 0.5 E+0 (non-conforming) */\n"
        f"/* Defect 3: lower-case e with plus sign in magnitude: 1.0e+0 */\n"
        f"#1=DIRECTION('',(1.5e+3,0.,0.));\n"
        f"#2=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        f"#3=VECTOR('v',#1,1.0e+1);\n"
        f"#4=LINE('l',#2,#3);\n"
        f"ENDSEC;\n"
        f"END-ISO-10303-21;\n"
    )


f.render = _render_lowercase_exponent  # type: ignore[method-assign]
