"""U026 — `derived_unit` / non-SI unit handling incomplete (BRL-CAD step-g).

Catalog claim: `derived_unit` (e.g. kg·m/s²) and unusual conversion bases are not normalized;
unit lookup falls through and the kernel uses the value as identity (scale = 1).

Reproducer recipe: file with DERIVED_UNIT((DERIVED_UNIT_ELEMENT(#k,1.0))) referenced from a
geometric quantity (force/density).

Byte assertions:
  contains(b'DERIVED_UNIT')
  contains(b'DERIVED_UNIT_ELEMENT') or contains(b'DERIVED_UNIT')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="U026",
    defect=(
        "derived_unit treated as identity scale by BRL-CAD step-g: non-SI unit lookup falls through; "
        "input: STEP file with DERIVED_UNIT referencing DERIVED_UNIT_ELEMENT entries for "
        "composite units such as kg*m/s^2 (Newton) or kg/m^3 (density); "
        "BRL-CAD step-g GlobalUnitAssignedContext.cpp:184 has a TODO: derived_unit comment "
        "indicating that derived units are not yet handled; "
        "the kernel falls through the derived_unit case and applies identity scale (scale = 1) "
        "silently, with no diagnostic emitted; "
        "a force of 9.81 N stored as a DERIVED_UNIT quantity gets treated as dimensionless 9.81; "
        "kernel must walk the derived_unit_element list and compute the SI scale factor "
        "by multiplying each base si_unit's prefix factor raised to its exponent; "
        "never silently treat an unrecognized DERIVED_UNIT as identity (scale = 1); "
        "this fixture defines a Newton (kg*m/s^2) as a DERIVED_UNIT and references it from "
        "a force measure; also includes a density unit (kg/m^3) as second DERIVED_UNIT; "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: derived_unit treated as identity scale, BRL-CAD step-g derived unit TODO, "
        "kg.m/s^2 derived unit unsupported, DERIVED_UNIT lookup falls through, "
        "non-SI derived unit identity-scale bug"
    ),
)


def _render_u026() -> str:
    """Render a Part-21 with DERIVED_UNIT for Newton and density; kernel must not use identity."""
    return (
        "ISO-10303-21;\n"
        "/* U026: DERIVED_UNIT entities (Newton, density) cause identity-scale fallthrough */\n"
        "/* BRL-CAD step-g silently treats unresolved DERIVED_UNIT as scale=1 */\n"
        "/* Kernel must walk DERIVED_UNIT_ELEMENT list and compute SI scale factor */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('U026: DERIVED_UNIT treated as identity scale in BRL-CAD step-g'),'2;1');\n"
        "FILE_NAME('U026.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Geometry: simple part with mm coordinates */\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner-x',(50.0,0.,0.));\n"
        "#3=CARTESIAN_POINT('corner-y',(0.,50.0,0.));\n"
        "#4=CARTESIAN_POINT('corner-z',(0.,0.,25.0));\n"
        "#5=CARTESIAN_POINT('corner-xyz',(50.0,50.0,25.0));\n"
        "/* Standard SI units for geometry context */\n"
        "#10=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.));\n"
        "#11=(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.));\n"
        "#12=(NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT());\n"
        "#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#10,\n"
        "  'distance_accuracy_value','maximum model space distance between geometric entities');\n"
        "#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))\n"
        "  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12)) REPRESENTATION_CONTEXT('ctx','3D'));\n"
        "/* Base SI units needed for DERIVED_UNIT elements */\n"
        "#20=(MASS_UNIT() NAMED_UNIT(*) SI_UNIT(.KILO.,.GRAM.));\n"
        "#21=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT($,.METRE.));\n"
        "#22=(NAMED_UNIT(*) SI_UNIT($,.SECOND.) TIME_UNIT());\n"
        "/* DEFECT: DERIVED_UNIT for Newton (kg*m*s^-2) */\n"
        "/* BRL-CAD step-g does not resolve this; falls through to identity scale */\n"
        "#30=DERIVED_UNIT_ELEMENT(#20,1.);\n"
        "#31=DERIVED_UNIT_ELEMENT(#21,1.);\n"
        "#32=DERIVED_UNIT_ELEMENT(#22,-2.);\n"
        "#33=(FORCE_UNIT() NAMED_UNIT(*) DERIVED_UNIT((#30,#31,#32)));\n"
        "/* DEFECT: DERIVED_UNIT for density (kg*m^-3) */\n"
        "#40=DERIVED_UNIT_ELEMENT(#20,1.);\n"
        "#41=DERIVED_UNIT_ELEMENT(#21,-3.);\n"
        "#42=DERIVED_UNIT((#40,#41));\n"
        "/* Force measure using the DERIVED_UNIT Newton */\n"
        "#50=MEASURE_REPRESENTATION_ITEM('applied_force',LENGTH_MEASURE(9.81),#33);\n"
        "/* Density measure using the DERIVED_UNIT density */\n"
        "#51=MEASURE_REPRESENTATION_ITEM('material_density',LENGTH_MEASURE(7850.),#42);\n"
        "/* Model entity is GEOMETRIC_CURVE_SET — OCC returns empty shape */\n"
        "#60=GEOMETRIC_CURVE_SET('derived-unit-identity-fallthrough',(#1,#2,#3,#4,#5));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_u026(path) -> None:
    Path(path).write_text(_render_u026())


f.render = _render_u026  # type: ignore[method-assign]
f.write = _write_u026    # type: ignore[method-assign]
