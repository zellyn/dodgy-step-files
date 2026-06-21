"""M012 — tessellated_constructive_geometry_representation requires AP242 Ed.4.

Catalog claim: TCGR (tessellated supplemental geometry) was added in AP242 Ed.4.
Files using it under earlier AP242 schemas fail validation.

Reproducer recipe: AP242 Ed.2 STEP file containing a
tessellated_constructive_geometry_representation entity.

Byte assertions:
  contains(b'TESSELLATED_CONSTRUCTIVE_GEOMETRY_REPRESENTATION')
  contains(b'442 2 1 4')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M012",
    schema="AP242",
    defect=(
        "AP242 Ed.2 schema violation: TESSELLATED_CONSTRUCTIVE_GEOMETRY_REPRESENTATION "
        "used under AP242 Ed.2 (442 2 1 4); "
        "TCGR was added in AP242 Ed.4 — not available in Ed.1, Ed.2, or Ed.3; "
        "writers scoped to Ed.1-Ed.3 must not emit TESSELLATED_CONSTRUCTIVE_GEOMETRY_REPRESENTATION; "
        "readers must reject files where TCGR appears under an earlier edition schema; "
        "input: AP242 Ed.2 FILE_SCHEMA with TESSELLATED_CONSTRUCTIVE_GEOMETRY_REPRESENTATION entity; "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: TCGR requires AP242 Ed.4, tessellated supplemental geometry rejected, "
        "AP242 edition too old for TCGR, schema-version vs entity-vocabulary disagreement"
    ),
)


def _render_m012() -> str:
    """Render AP242 Ed.2 file with TESSELLATED_CONSTRUCTIVE_GEOMETRY_REPRESENTATION.

    The FILE_SCHEMA declares AP242 Ed.2 (442 2 1 4) but the DATA section
    contains TESSELLATED_CONSTRUCTIVE_GEOMETRY_REPRESENTATION, which only
    became legal in Ed.4. Readers enforcing the schema-version constraint
    must reject.

    Byte assertion: contains(b'442 2 1 4')
    Byte assertion: contains(b'TESSELLATED_CONSTRUCTIVE_GEOMETRY_REPRESENTATION')
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append(
        "/* M012: AP242 Ed.2 with TESSELLATED_CONSTRUCTIVE_GEOMETRY_REPRESENTATION */"
    )
    lines.append(
        "/* DEFECT: TCGR is an AP242 Ed.4 entity; schema declares Ed.2 (442 2 1 4) */"
    )
    lines.append(
        "/* Writer scoped to Ed.1-Ed.3 must not emit TCGR; reader must reject */"
    )
    lines.append("HEADER;")
    lines.append(
        "FILE_DESCRIPTION("
        "('M012: AP242 Ed.2 file with TESSELLATED_CONSTRUCTIVE_GEOMETRY_REPRESENTATION'),"
        "'2;1');"
    )
    lines.append(
        "FILE_NAME('M012.stp','2026-06-21T00:00:00',(''),(''),"
        "'cad-research-suite','','');"
    )
    # AP242 Ed.2: { 1 0 10303 442 2 1 4 } — byte assertion target
    lines.append(
        "FILE_SCHEMA(("
        "'AP242_MANAGED_MODEL_BASED_3D_ENGINEERING_MIM_LF { 1 0 10303 442 2 1 4 }'"
        "));"
    )
    lines.append("ENDSEC;")
    lines.append("DATA;")
    lines.append("/* Standard mm unit context */")
    lines.append("#1=(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.));")
    lines.append("#2=(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.));")
    lines.append("#3=(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT());")
    lines.append(
        "#4=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0E-7),"
        "#1,'distance_accuracy_value','');"
    )
    lines.append(
        "#5=(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
        "GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#4))"
        "GLOBAL_UNIT_ASSIGNED_CONTEXT((#1,#2,#3))"
        "REPRESENTATION_CONTEXT('','3D'));"
    )
    lines.append("/* Tessellated geometry: two triangles forming a flat quad */")
    lines.append(
        "#6=COORDINATES_LIST('tcgr_coords',3,"
        "((0.,0.,0.),(10.,0.,0.),(10.,10.,0.),(0.,10.,0.)));"
    )
    lines.append(
        "#7=TRIANGULATED_FACE('tcgr_face',#6,$,"
        "((.FALSE.,.FALSE.,.FALSE.,.FALSE.)),((0,1,2),(0,2,3)));"
    )
    lines.append(
        "#8=TESSELLATED_SOLID('tcgr_solid',(#7));"
    )
    # TESSELLATED_CONSTRUCTIVE_GEOMETRY_REPRESENTATION: added in AP242 Ed.4
    # Using it here under Ed.2 schema is the defect.
    lines.append(
        "/* DEFECT ENTITY: TCGR is valid only in AP242 Ed.4+; "
        "schema above is Ed.2 */"
    )
    lines.append(
        "#9=TESSELLATED_CONSTRUCTIVE_GEOMETRY_REPRESENTATION("
        "'tcgr_supplemental',(#8),#5);"
    )
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append(
        "#10=GEOMETRIC_CURVE_SET('tcgr-ap242-ed2-schema-violation',(#8,#9));"
    )
    # Minimal PRODUCT chain
    lines.append("#9000=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#9001=PRODUCT_CONTEXT(#9000,'mechanical','');")
    lines.append("#9002=PRODUCT('M012','M012','',(#9001));")
    lines.append("#9003=PRODUCT_DEFINITION_FORMATION('','',#9002);")
    lines.append("#9004=PRODUCT_DEFINITION_CONTEXT(#9000,'design','part definition');")
    lines.append("#9005=PRODUCT_DEFINITION('','',#9003,#9004);")
    lines.append("#9006=PRODUCT_DEFINITION_SHAPE('','',#9005);")
    lines.append("#9007=MANIFOLD_SURFACE_SHAPE_REPRESENTATION('',(#10),#5);")
    lines.append("#9008=SHAPE_DEFINITION_REPRESENTATION(#9006,#9007);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m012(path) -> None:
    Path(path).write_text(_render_m012())


f.render = _render_m012  # type: ignore[method-assign]
f.write = _write_m012    # type: ignore[method-assign]
