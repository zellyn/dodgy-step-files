"""U042 — Specific-heat-capacity unit `J/(kg*K)` built from a derived-unit chain (`m^2 / (s^2 * K)`).

Catalog claim: Specific heat capacity J/(kg*K) is dimensionally m^2*s^(-2)*K^(-1) (the kg
cancels). A producer that emits the unit as a DERIVED_UNIT (length^+2, time^-2, temperature^-1)
confuses receivers that pattern-match on the kg-cancelled form vs the explicit J/kg/K form.
The underlying THERMODYNAMIC_TEMPERATURE_UNIT context for kelvin must be present.

Reproducer recipe: DERIVED_UNIT with three DERIVED_UNIT_ELEMENT entries: metre^+2, second^-2,
kelvin^-1; plus THERMODYNAMIC_TEMPERATURE_UNIT context.

Byte assertions:
  contains(b'DERIVED_UNIT_ELEMENT') and contains(b'DERIVED_UNIT(')
  contains(b'THERMODYNAMIC_TEMPERATURE_UNIT')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="U042",
    defect=(
        "Specific-heat-capacity unit J/(kg.K) as DERIVED_UNIT chain m^2*s^-2*K^-1; "
        "input: STEP file where specific heat capacity is emitted as a DERIVED_UNIT composed of "
        "three DERIVED_UNIT_ELEMENT entries: metre^+2, second^-2, kelvin^-1; "
        "the kg-cancelled dimensional form (J/(kg.K) = m^2*s^-2*K^-1) is spec-conformant "
        "but stresses receivers that pattern-match on named units or the un-cancelled J/kg/K form; "
        "the THERMODYNAMIC_TEMPERATURE_UNIT context for kelvin must be present; "
        "receivers that do not recognise THERMODYNAMIC_TEMPERATURE_UNIT in a DERIVED_UNIT chain "
        "silently drop the temperature factor and read the unit as m^2*s^-2 (=J/kg, not J/(kg.K)); "
        "receivers that pattern-match on the explicit J/kg/K form but not the kg-cancelled form "
        "also fail to bind the unit correctly; "
        "kernel must heal: detect dimensional signature m^2*s^-2*K^-1 for specific heat capacity "
        "regardless of whether the kg factor is present or cancelled; "
        "never drop the temperature component of a derived-unit chain; "
        "warn on dimensional mismatch when temperature exponent is unexpected; "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: STEP specific heat unit garbled, J/(kg.K) derived chain unrecognised, "
        "thermal property unit garbled, specific heat capacity unit dropped, "
        "STEP material thermal unit not bound, m^2 s^-2 K^-1 not bound as specific heat"
    ),
)


def _render_u042() -> str:
    """Render a Part-21 with DERIVED_UNIT for J/(kg*K) in kg-cancelled form: m^2*s^-2*K^-1."""
    return (
        "ISO-10303-21;\n"
        "/* U042: Specific heat capacity J/(kg*K) as DERIVED_UNIT m^2*s^-2*K^-1 (kg-cancelled form) */\n"
        "/* DEFECT: receivers that miss THERMODYNAMIC_TEMPERATURE_UNIT drop K^-1 factor */\n"
        "/* DEFECT: receivers pattern-matching named J/kg/K unit miss the kg-cancelled form */\n"
        "/* Kernel must detect m^2*s^-2*K^-1 dimensional signature and bind to J/(kg.K) */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('U042: J/(kg*K) DERIVED_UNIT chain m^2*s^-2*K^-1 with THERMODYNAMIC_TEMPERATURE_UNIT'),'2;1');\n"
        "FILE_NAME('U042.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
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
        "/* Base SI units for specific heat capacity DERIVED_UNIT chain */\n"
        "#20=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT($,.METRE.));\n"
        "#21=(NAMED_UNIT(*) SI_UNIT($,.SECOND.) TIME_UNIT());\n"
        "/* THERMODYNAMIC_TEMPERATURE_UNIT for kelvin — required by specific heat chain */\n"
        "/* DEFECT target: receivers that do not handle THERMODYNAMIC_TEMPERATURE_UNIT in */\n"
        "/*   a DERIVED_UNIT chain silently drop the K^-1 factor */\n"
        "#22=(NAMED_UNIT(*) SI_UNIT($,.KELVIN.) THERMODYNAMIC_TEMPERATURE_UNIT());\n"
        "/* DERIVED_UNIT for specific heat J/(kg*K) in kg-cancelled form: m^2*s^-2*K^-1 */\n"
        "#30=DERIVED_UNIT_ELEMENT(#20,2.);\n"
        "#31=DERIVED_UNIT_ELEMENT(#21,-2.);\n"
        "#32=DERIVED_UNIT_ELEMENT(#22,-1.);\n"
        "#33=DERIVED_UNIT((#30,#31,#32));\n"
        "/* Specific heat measure: 4182 J/(kg*K) (water) */\n"
        "/* Receiver that drops temperature factor reads m^2*s^-2 = J/kg — wrong unit */\n"
        "#40=MEASURE_REPRESENTATION_ITEM('specific_heat_capacity',LENGTH_MEASURE(4182.),#33);\n"
        "/* Model entity is GEOMETRIC_CURVE_SET — OCC returns empty shape */\n"
        "#50=GEOMETRIC_CURVE_SET('specific-heat-unit-derived-chain',(#1,#2,#3,#4,#5));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_u042(path) -> None:
    Path(path).write_text(_render_u042())


f.render = _render_u042  # type: ignore[method-assign]
f.write = _write_u042    # type: ignore[method-assign]
