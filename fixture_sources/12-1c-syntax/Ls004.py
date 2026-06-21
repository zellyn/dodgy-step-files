"""Ls004 — Fortran-style `D` exponent (`1.0D5`).

Catalog claim: Some legacy Fortran-fronted exporters (older I-DEAS, CADAM
converters) emit `1.0D5` instead of `1.0E5`. ISO 10303-21 only allows
`E`/`e`.

Reproducer recipe: #1=DIRECTION('',(1.0D5,0.,0.));

Byte assertions:
  matches(rb'\\d[Dd][+-]?\\d')
  contains(b'1.0D5') or contains(b'1.5D-3')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ls004",
    defect=(
        "Fortran-style D exponent in REAL literal; "
        "some legacy Fortran-fronted exporters (older I-DEAS, CADAM converters) "
        "emit 1.0D5 instead of 1.0E5; "
        "ISO 10303-21 only allows E or e as the exponent indicator; "
        "defect: DIRECTION('',(1.0D5,0.,0.)) — D-exponent REAL in the first coordinate; "
        "also VECTOR magnitude uses 1.5D-3 (a second D-exponent variant); "
        "strict readers must reject with diagnostic 'exponent must be E, got D'; "
        "lenient mode must not silently accept — emit a warning at minimum; "
        "legacy Fortran writer emits D exponent; I-DEAS D-exponent REAL; "
        "CADAM D-style exponent; "
        "synonyms: Fortran D exponent in STEP, 1.0D5 instead of 1.0E5, "
        "legacy Fortran writer emits D exponent, I-DEAS D-exponent REAL, "
        "CADAM D-style exponent; "
        "GEOMETRIC_CURVE_SET IS NOT used — DIRECTION entity is the defect carrier"
    ),
)

_original_render = f.render


def _render_d_exponent() -> str:
    header = f._render_header()
    return (
        f"ISO-10303-21;\n"
        f"/* {f.catalog_id}: {f.defect} */\n"
        f"{header}\n"
        f"DATA;\n"
        f"/* Defect: Fortran-style D exponent — 1.0D5 instead of 1.0E5. */\n"
        f"/* ISO 10303-21 §6.4: only E or e is permitted for the REAL exponent. */\n"
        f"/* Legacy Fortran-fronted exporters (I-DEAS, CADAM) emit D-exponent. */\n"
        f"#1=DIRECTION('',(1.0D5,0.,0.));\n"
        f"#2=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        f"#3=VECTOR('v',#1,1.5D-3);\n"
        f"#4=LINE('l',#2,#3);\n"
        f"ENDSEC;\n"
        f"END-ISO-10303-21;\n"
    )


f.render = _render_d_exponent  # type: ignore[method-assign]
