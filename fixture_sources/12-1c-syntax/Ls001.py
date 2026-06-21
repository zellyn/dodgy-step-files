"""Ls001 — REAL literal missing mandatory decimal point.

Catalog claim: ISO 10303-21 grammar requires every REAL to carry a decimal
point (1., 1.0, 0.5). Generators that print integer values into REAL slots
emit 1 where 1. is required (e.g. DIRECTION((1,0,0)) instead of (1.,0.,0.)).
stepcode warns and salvages; strict readers reject.

Reproducer recipe: #1=DIRECTION('',(1,0,0)); instead of (1.,0.,0.)

Byte assertions:
  matches(rb"DIRECTION\([^;]*,\(\s*1\s*,")
  contains(b'(1,0,0)') or matches(rb',\(1,\d')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ls001",
    defect=(
        "REAL literal missing mandatory decimal point; "
        "ISO 10303-21 §6.4 grammar requires every REAL to carry a decimal point: "
        "1. or 1.0 or 0.5; generators that print integer values into REAL slots "
        "emit 1 where 1. is required; "
        "defect: DIRECTION('',(1,0,0)) — integers in all three coordinate slots, "
        "no decimal point on any value; "
        "stepcode warns and salvages via istringstream >> double; "
        "strict readers must reject with decimal-point-required diagnostic; "
        "lenient mode may auto-promote INTEGER to REAL with a warning, never silently; "
        "implementors Issue 003 records the original disagreement: "
        "integers must not be followed by a dot, REALs must be; "
        "a primary cause of integer-vs-real type-coercion bugs; "
        "bug-reporter synonyms: REAL with no decimal point, integer where REAL required, "
        "1 written instead of 1., DIRECTION coords missing dots, "
        "STEP REAL missing trailing period; "
        "GEOMETRIC_CURVE_SET IS NOT used — DIRECTION entity is the defect carrier"
    ),
)

# Override render() to emit the defect: DIRECTION with bare integers, no dots.
_original_render = f.render


def _render_integer_reals() -> str:
    header = f._render_header()
    return (
        f"ISO-10303-21;\n"
        f"/* {f.catalog_id}: {f.defect} */\n"
        f"{header}\n"
        f"DATA;\n"
        f"/* Defect: integer values in REAL slots — no decimal point. */\n"
        f"/* ISO 10303-21 §6.4: every REAL must carry a decimal point. */\n"
        f"#1=DIRECTION('',(1,0,0));\n"
        f"#2=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        f"#3=VECTOR('v',#1,1.);\n"
        f"#4=LINE('l',#2,#3);\n"
        f"ENDSEC;\n"
        f"END-ISO-10303-21;\n"
    )


f.render = _render_integer_reals  # type: ignore[method-assign]
