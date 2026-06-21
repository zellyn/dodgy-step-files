"""Ls002 — REAL literal with no digit before the decimal point.

Catalog claim: ISO 10303-21 grammar requires at least one digit before the
decimal dot. .5 is not legal; 0.5 is. C/Python %g formatters frequently
emit bare .5.

Reproducer recipe: #1=DIRECTION('',(.0,.0,1.0));

Byte assertions:
  matches(rb"\(\s*\.\d")
  contains(b'.5') and matches(rb'\(\.\d')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ls002",
    defect=(
        "REAL literal with no digit before the decimal point; "
        "ISO 10303-21 grammar requires at least one digit before the dot: "
        ".5 is not legal; 0.5 is; "
        "C and Python percent-g formatters frequently emit bare .5 for values < 1; "
        "defect: DIRECTION('',(.0,.0,.5)) — leading-dot REAL literals in all three "
        "coordinate slots: .0, .0, .5; no digit before any decimal point; "
        "strict readers must reject with digit-required-before-decimal diagnostic; "
        "lenient readers commonly accept implicit zero; "
        "bug-reporter synonyms: REAL with no digit before decimal, .5 instead of 0.5 in STEP, "
        "leading-dot REAL literal, percent-g formatter emits .5, missing zero before decimal; "
        "GEOMETRIC_CURVE_SET IS NOT used — DIRECTION entity is the defect carrier"
    ),
)

# Override render() to emit the defect: DIRECTION with leading-dot REAL literals.
_original_render = f.render


def _render_leading_dot_reals() -> str:
    header = f._render_header()
    return (
        f"ISO-10303-21;\n"
        f"/* {f.catalog_id}: {f.defect} */\n"
        f"{header}\n"
        f"DATA;\n"
        f"/* Defect: leading-dot REAL literals — no digit before the decimal point. */\n"
        f"/* ISO 10303-21: grammar requires at least one digit before the dot. */\n"
        f"/* C/Python %g formatter emits .5 instead of 0.5 for values < 1. */\n"
        f"#1=DIRECTION('',(.0,.0,.5));\n"
        f"#2=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        f"#3=VECTOR('v',#1,1.);\n"
        f"#4=LINE('l',#2,#3);\n"
        f"ENDSEC;\n"
        f"END-ISO-10303-21;\n"
    )


f.render = _render_leading_dot_reals  # type: ignore[method-assign]
