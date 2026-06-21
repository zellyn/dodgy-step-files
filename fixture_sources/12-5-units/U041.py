"""U041 — Dynamic-viscosity unit `Pa*s` built from a derived-unit chain (`kg / (m * s)`).

Catalog claim: Dynamic viscosity Pa*s is kg*m^(-1)*s^(-1). A producer emitting viscosity as a
multi-element DERIVED_UNIT exposes exponent defects — some receivers flatten the time exponent
and read the unit as Pa instead of Pa*s.

Reproducer recipe: DERIVED_UNIT with three DERIVED_UNIT_ELEMENT entries: kilogram^+1, metre^-1,
second^-1.

Byte assertions:
  contains(b'DERIVED_UNIT_ELEMENT') and contains(b'DERIVED_UNIT(')
  count(b'DERIVED_UNIT_ELEMENT') >= 3

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="U041",
    defect=(
        "Dynamic-viscosity unit Pa.s built from DERIVED_UNIT chain kg*m^-1*s^-1; "
        "input: STEP file where dynamic viscosity is emitted as a DERIVED_UNIT composed of "
        "three DERIVED_UNIT_ELEMENT entries: kilogram^+1, metre^-1, second^-1; "
        "dimensional signature is mass^1 length^-1 time^-1 = Pa.s (dynamic viscosity); "
        "some receivers flatten the time-exponent dictionary lookup: "
        "they match mass^1 length^-1 and treat the remaining time^-1 as pressure Pa "
        "instead of correctly resolving to Pa.s (Pa times second); "
        "other receivers that pattern-match a named unit do not recognise this DERIVED_UNIT chain; "
        "kernel must detect the dimensional signature of dynamic viscosity (mass^1 length^-1 time^-1) "
        "and bind to a Pa.s context; never silently flatten the time exponent to produce Pa; "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: STEP viscosity unit not recognised, Pa.s read as Pa, "
        "dynamic viscosity derived chain unsupported, STEP material viscosity wrong unit, "
        "viscosity flattened to pressure, kg.m^-1.s^-1 not bound as Pa.s"
    ),
)


def _render_u041() -> str:
    """Render a Part-21 with DERIVED_UNIT for Pa*s (dynamic viscosity): kg*m^-1*s^-1."""
    return (
        "ISO-10303-21;\n"
        "/* U041: Dynamic viscosity Pa*s as DERIVED_UNIT: kg*m^-1*s^-1 */\n"
        "/* DEFECT: receivers may flatten time exponent and read as Pa instead of Pa*s */\n"
        "/* Kernel must resolve dimensional signature mass^1 length^-1 time^-1 to Pa.s */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('U041: Pa.s dynamic viscosity DERIVED_UNIT chain kg*m^-1*s^-1'),'2;1');\n"
        "FILE_NAME('U041.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Geometry: part with mm coordinates */\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner-x',(50.0,0.,0.));\n"
        "#3=CARTESIAN_POINT('corner-y',(0.,50.0,0.));\n"
        "#4=CARTESIAN_POINT('corner-z',(0.,0.,25.0));\n"
        "#5=CARTESIAN_POINT('corner-xyz',(50.0,50.0,25.0));\n"
        "/* Standard mm geometry context */\n"
        "#10=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.));\n"
        "#11=(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.));\n"
        "#12=(NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT());\n"
        "#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#10,\n"
        "  'distance_accuracy_value','maximum model space distance between geometric entities');\n"
        "#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))\n"
        "  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12)) REPRESENTATION_CONTEXT('ctx','3D'));\n"
        "/* Base SI units for dynamic viscosity DERIVED_UNIT chain */\n"
        "#20=(MASS_UNIT() NAMED_UNIT(*) SI_UNIT(.KILO.,.GRAM.));\n"
        "#21=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT($,.METRE.));\n"
        "#22=(NAMED_UNIT(*) SI_UNIT($,.SECOND.) TIME_UNIT());\n"
        "/* DERIVED_UNIT for dynamic viscosity Pa*s: mass^+1, length^-1, time^-1 */\n"
        "/* Correct dimensional signature: kg*m^-1*s^-1 = Pa.s */\n"
        "/* DEFECT: receivers that flatten time exponent read this as Pa (not Pa.s) */\n"
        "#30=DERIVED_UNIT_ELEMENT(#20,1.);\n"
        "#31=DERIVED_UNIT_ELEMENT(#21,-1.);\n"
        "#32=DERIVED_UNIT_ELEMENT(#22,-1.);\n"
        "#33=DERIVED_UNIT((#30,#31,#32));\n"
        "/* Viscosity measure: 0.001 Pa*s (water at 20 deg C) */\n"
        "/* Receiver that reads Pa instead of Pa*s gets wrong material property */\n"
        "#40=MEASURE_REPRESENTATION_ITEM('dynamic_viscosity',LENGTH_MEASURE(0.001),#33);\n"
        "/* Model entity is GEOMETRIC_CURVE_SET — OCC returns empty shape */\n"
        "#50=GEOMETRIC_CURVE_SET('viscosity-unit-pas-derived-chain',(#1,#2,#3,#4,#5));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_u041(path) -> None:
    Path(path).write_text(_render_u041())


f.render = _render_u041  # type: ignore[method-assign]
f.write = _write_u041    # type: ignore[method-assign]
