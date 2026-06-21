"""U018 — Tessellated annotation coordinates with no global unit context (silent 25.4x).

Catalog claim: coordinates_list.position_coords are bare REALs, not length_measure.
If a tessellated annotation or tessellated shape sits under a representation_context that
is not a global_unit_assigned_context, coordinates have no resolvable unit. Common breakage:
tessellated PMI extracted out of context appears 25.4x the correct size.

Reproducer recipe: STEP file with one tessellated_annotation_occurrence whose
tessellated_geometric_set references a coordinates_list; place that occurrence's
tessellated_shape_representation under a generic representation_context lacking
global_unit_assigned_context.

Byte assertions:
  contains(b'TESSELLATED_SHAPE_REPRESENTATION')
  contains(b'TESSELLATED_ANNOTATION_OCCURRENCE') or contains(b'TESSELLATED_GEOMETRIC_SET')
    or contains(b'TESSELLATED_SHAPE_REPRESENTATION')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="U018",
    defect=(
        "Tessellated annotation coordinates with no global unit context (silent 25.4x); "
        "input: STEP file with tessellated PMI annotation whose tessellated_shape_representation "
        "is placed under a generic REPRESENTATION_CONTEXT lacking GLOBAL_UNIT_ASSIGNED_CONTEXT; "
        "coordinates_list.position_coords are bare REAL values without a length_measure wrapper; "
        "when the tessellated annotation is extracted out of unit context the coordinates have "
        "no resolvable unit — tessellated PMI appears 25.4x too large (inch/mm confusion); "
        "the TESSELLATED_SHAPE_REPRESENTATION must be placed under a "
        "GLOBAL_UNIT_ASSIGNED_CONTEXT for its coordinates to be unambiguously interpretable; "
        "kernel must reject or warn on tessellated representations not anchored in a "
        "global_unit_assigned_context; "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: tessellated annotation no global unit context, PMI tessellation 25.4x wrong, "
        "tessellated coords without unit anchor, annotation outside global_unit_assigned_context, "
        "tessellated PMI silent unit drop"
    ),
)


def _render_u018() -> str:
    """Render a Part-21 with TESSELLATED_SHAPE_REPRESENTATION under a bare REPRESENTATION_CONTEXT."""
    return (
        "ISO-10303-21;\n"
        "/* U018: Tessellated annotation coords with no global_unit_assigned_context */\n"
        "/* TESSELLATED_SHAPE_REPRESENTATION placed under bare REPRESENTATION_CONTEXT */\n"
        "/* coordinates_list uses bare REAL values with no resolvable unit */\n"
        "/* PMI tessellation appears 25.4x wrong size due to missing unit anchor */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('U018: Tessellated PMI with no global_unit_assigned_context'),'2;1');\n"
        "FILE_NAME('U018.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Main geometry context — properly unit-assigned */\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner-x',(50.0,0.,0.));\n"
        "#3=CARTESIAN_POINT('corner-y',(0.,50.0,0.));\n"
        "#4=CARTESIAN_POINT('corner-z',(0.,0.,25.0));\n"
        "#5=CARTESIAN_POINT('corner-xyz',(50.0,50.0,25.0));\n"
        "/* Proper unit context for main geometry */\n"
        "#10=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.));\n"
        "#11=(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.));\n"
        "#12=(NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT());\n"
        "#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#10,\n"
        "  'distance_accuracy_value','maximum model space distance between geometric entities');\n"
        "#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))\n"
        "  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12)) REPRESENTATION_CONTEXT('main-ctx','3D'));\n"
        "/* Main model entity */\n"
        "#20=GEOMETRIC_CURVE_SET('main-geometry',(#1,#2,#3,#4,#5));\n"
        "/* DEFECT: tessellated PMI placed under bare REPRESENTATION_CONTEXT */\n"
        "/* No GLOBAL_UNIT_ASSIGNED_CONTEXT => coordinates have no resolvable unit */\n"
        "#50=COORDINATES_LIST('annot-pts',3,(\n"
        "  (0.0,0.0,0.0),(50.0,0.0,0.0),(50.0,50.0,0.0),(0.0,50.0,0.0),\n"
        "  (0.0,0.0,0.0)));\n"
        "#51=TESSELLATED_GEOMETRIC_SET('tess-outline',(#50));\n"
        "#52=TESSELLATED_ANNOTATION_OCCURRENCE('dim-label',(),(#51));\n"
        "/* DEFECT: bare REPRESENTATION_CONTEXT — no GLOBAL_UNIT_ASSIGNED_CONTEXT */\n"
        "#60=REPRESENTATION_CONTEXT('tess-pmi-ctx','3D');\n"
        "#61=TESSELLATED_SHAPE_REPRESENTATION('tess-pmi-rep',(#52),#60);\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_u018(path) -> None:
    Path(path).write_text(_render_u018())


f.render = _render_u018  # type: ignore[method-assign]
f.write = _write_u018    # type: ignore[method-assign]
