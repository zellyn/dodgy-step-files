"""U028 — Two GEOMETRIC_REPRESENTATION_CONTEXT instances with different LENGTH_UNIT (mm BRep vs metre PMI/CGR).

Catalog claim: A single STEP file carries two GEOMETRIC_REPRESENTATION_CONTEXT instances with
different LENGTH_UNITs — one named 'mm_brep' in millimetres and another 'm_pmi' in metres —
where a SHAPE_REPRESENTATION (B-rep) uses the mm context and a CONSTRUCTIVE_GEOMETRY_REPRESENTATION
(CGR) or DRAUGHTING_MODEL (PMI) uses the metre context.

Reproducer recipe: part with two GRCs — one in mm for the BREP, another in m for the CGR;
PMI references supplemental elements from the second CGR.

Byte assertions:
  contains(b'.MILLI.') and matches(rb'SI_UNIT\\(\\$\\s*,\\s*\\.METRE\\.\\)')
  count_entity_def(b'GEOMETRIC_REPRESENTATION_CONTEXT') >= 2 or
    count(b'GEOMETRIC_REPRESENTATION_CONTEXT') >= 2

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="U028",
    defect=(
        "Two GEOMETRIC_REPRESENTATION_CONTEXT instances with different LENGTH_UNIT: "
        "mm BRep context vs metre PMI/CGR context in the same STEP file; "
        "input: STEP file with two GEOMETRIC_REPRESENTATION_CONTEXT complexes where "
        "the BRep SHAPE_REPRESENTATION references a mm-based GRC named 'mm_brep' "
        "and a CONSTRUCTIVE_GEOMETRY_REPRESENTATION (CGR) references a metre-based GRC "
        "named 'm_pmi'; per PMI v4.1 §9.4.2 and Supplemental Geometry §5.4, "
        "part shape, supplemental geometry CGR, and PMI draughting models are required "
        "to share the same GEOMETRIC_REPRESENTATION_CONTEXT; "
        "when they don't, units, uncertainty, and coordinate space differ between "
        "sub-representations; receivers see Cartesian points apparently in mixed scale; "
        "OCCT-based readers default to mm and silently mis-scale the non-mm ones "
        "(metre coordinates appear 1000x smaller than intended); "
        "kernel must reject or propagate units consistently: resolve the full unit-conversion "
        "chain to a single SI scale factor per sub-representation; "
        "refuse to silently default to mm when contexts differ; "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: two GEOMETRIC_REPRESENTATION_CONTEXT different units, "
        "mm BRep with metre PMI in same STEP, shape_representation and CGR units differ, "
        "PMI and BRep on different unit contexts, multiple GRC unit conflict"
    ),
)


def _render_u028() -> str:
    """Render a Part-21 with two GRCs using different length units (mm BRep, metre CGR)."""
    return (
        "ISO-10303-21;\n"
        "/* U028: Two GEOMETRIC_REPRESENTATION_CONTEXT with different LENGTH_UNIT */\n"
        "/* BRep uses mm context; CGR/PMI uses metre context */\n"
        "/* PMI v4.1 §9.4.2: all sub-representations must share the same GRC */\n"
        "/* OCCT defaults to mm and silently mis-scales the metre-based CGR coordinates */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('U028: mm BRep vs metre PMI/CGR in separate GRC contexts'),'2;1');\n"
        "FILE_NAME('U028.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* BRep geometry: 50x50x25 mm cube (values in mm) */\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner-x',(50.0,0.,0.));\n"
        "#3=CARTESIAN_POINT('corner-y',(0.,50.0,0.));\n"
        "#4=CARTESIAN_POINT('corner-z',(0.,0.,25.0));\n"
        "#5=CARTESIAN_POINT('corner-xyz',(50.0,50.0,25.0));\n"
        "/* BRep context: mm (MILLI METRE) */\n"
        "#10=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.));\n"
        "#11=(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.));\n"
        "#12=(NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT());\n"
        "#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#10,\n"
        "  'distance_accuracy_value','maximum model space distance between geometric entities');\n"
        "/* DEFECT: BRep GRC in mm */\n"
        "#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))\n"
        "  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12)) REPRESENTATION_CONTEXT('mm_brep','3D'));\n"
        "/* CGR/PMI geometry: same cube but expressed in METRES (values: 0.05, 0.025) */\n"
        "#51=CARTESIAN_POINT('pmi-origin',(0.,0.,0.));\n"
        "#52=CARTESIAN_POINT('pmi-corner-x',(0.05,0.,0.));\n"
        "#53=CARTESIAN_POINT('pmi-corner-y',(0.,0.05,0.));\n"
        "#54=CARTESIAN_POINT('pmi-corner-z',(0.,0.,0.025));\n"
        "#55=CARTESIAN_POINT('pmi-corner-xyz',(0.05,0.05,0.025));\n"
        "/* DEFECT: CGR/PMI context in metres (no prefix: SI_UNIT($,.METRE.)) */\n"
        "#60=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT($,.METRE.));\n"
        "#61=(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.));\n"
        "#62=(NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT());\n"
        "#63=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-6),#60,\n"
        "  'distance_accuracy_value','maximum model space distance between geometric entities');\n"
        "/* DEFECT: Second GRC in metres — conflicts with BRep GRC in mm */\n"
        "#64=(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#63))\n"
        "  GLOBAL_UNIT_ASSIGNED_CONTEXT((#60,#61,#62)) REPRESENTATION_CONTEXT('m_pmi','3D'));\n"
        "/* BRep model entity uses mm GRC */\n"
        "#70=GEOMETRIC_CURVE_SET('brep-mm-context',(#1,#2,#3,#4,#5));\n"
        "/* CGR model entity uses metre GRC — same physical shape but mis-scaled when read */\n"
        "#71=GEOMETRIC_CURVE_SET('cgr-metre-context',(#51,#52,#53,#54,#55));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_u028(path) -> None:
    Path(path).write_text(_render_u028())


f.render = _render_u028  # type: ignore[method-assign]
f.write = _write_u028    # type: ignore[method-assign]
