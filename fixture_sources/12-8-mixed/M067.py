"""M067 — Transformation relation creation failed (zero-vector DIRECTION in ITEM_DEFINED_TRANSFORMATION).

Catalog claim: A child component's transformation reference
(ITEM_DEFINED_TRANSFORMATION) cannot be resolved to a valid 4x4 matrix
because the AXIS2_PLACEMENT_3D in transform_item_2 has zero-vector
DIRECTION ratios; the reader falls back to identity placement. The child
appears at the wrong location.

Reproducer recipe: An NAUO whose transformation references an
ITEM_DEFINED_TRANSFORMATION whose transform_item_2 axis directions are
zero vectors.

Byte assertions:
  contains(b'ITEM_DEFINED_TRANSFORMATION')
  matches(rb'DIRECTION\\'zero_vec\\',(0\\.0,0\\.0,0\\.0)\\)')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M067",
    defect=(
        "GEOMETRIC_CURVE_SET in file where ITEM_DEFINED_TRANSFORMATION has zero-vector "
        "DIRECTION in its transform_item_2 AXIS2_PLACEMENT_3D — transformation matrix "
        "cannot be resolved; reader falls back to identity placement, child appears at "
        "wrong location; "
        "input: AP242 STEP file where NAUO references an ITEM_DEFINED_TRANSFORMATION "
        "whose transform_item_2 is an AXIS2_PLACEMENT_3D with DIRECTION('zero_vec',(0.0,0.0,0.0)) "
        "as its axis (Z-direction) — a zero vector is geometrically degenerate; "
        "a 4x4 transformation matrix derived from a zero axis vector is undefined; "
        "OCCT silently substitutes the identity placement when the transformation reference "
        "cannot be resolved, leaving children at the origin without a diagnostic; "
        "kernel must reject the assembly placement as malformed and not silently use identity; "
        "synonyms: child at origin bug, STEP transformation creation failed, "
        "child placement wrong, ITEM_DEFINED_TRANSFORMATION fell back to identity, "
        "zero-vector DIRECTION in placement"
    ),
    schema="AP242",
)


def _render_m067() -> str:
    """Render AP242 file with ITEM_DEFINED_TRANSFORMATION containing zero-vector DIRECTION.

    Entity layout:
      #10  LENGTH_UNIT (complex)
      #11  PLANE_ANGLE_UNIT (complex)
      #12  SOLID_ANGLE_UNIT (complex)
      #13  UNCERTAINTY_MEASURE_WITH_UNIT
      #14  GEOMETRIC_REPRESENTATION_CONTEXT (full context)
      #20  Application context + product chain for parent
      #30  Application context + product chain for child
      #50  AXIS2_PLACEMENT_3D with zero-vector DIRECTION — the defect
      #51  ITEM_DEFINED_TRANSFORMATION referencing the bad placement
      #55  NAUO referencing the ITEM_DEFINED_TRANSFORMATION
      #60  GEOMETRIC_CURVE_SET model entity
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M067: ITEM_DEFINED_TRANSFORMATION with zero-vector DIRECTION in AXIS2_PLACEMENT_3D */")
    lines.append("/* DEFECT: zero-vector axis direction makes transformation matrix undefined */")
    lines.append("/* OCCT silently substitutes identity; kernel must reject */")
    lines.append("/* Byte assertion: contains(b'ITEM_DEFINED_TRANSFORMATION') */")
    lines.append("/* Byte assertion: matches(rb'DIRECTION\\'zero_vec\\',(0\\.0,0\\.0,0\\.0)\\)') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M067: ITEM_DEFINED_TRANSFORMATION with zero-vector DIRECTION'),'2;1');")
    lines.append("FILE_NAME('M067.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
    lines.append("FILE_SCHEMA(('AP242_MANAGED_MODEL_BASED_3D_ENGINEERING_MIM_LF { 1 0 10303 442 1 1 4 }'));")
    lines.append("ENDSEC;")
    lines.append("DATA;")
    lines.append("/* Standard unit context */")
    lines.append("#10=(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.));")
    lines.append("#11=(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.));")
    lines.append("#12=(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT());")
    lines.append("#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#10,")
    lines.append("  'distance_accuracy_value','maximum model space distance between geometric entities');")
    lines.append("#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3)")
    lines.append("  GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))")
    lines.append("  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12))")
    lines.append("  REPRESENTATION_CONTEXT('ctx','3D'));")
    lines.append("/* Application context */")
    lines.append("#20=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#21=PRODUCT_CONTEXT('',#20,'mechanical');")
    lines.append("/* Parent product */")
    lines.append("#22=PRODUCT('parent_001','Assembly','Top-level assembly',(#21));")
    lines.append("#23=PRODUCT_DEFINITION_FORMATION('','',#22);")
    lines.append("#24=PRODUCT_DEFINITION_CONTEXT(#20,'design');")
    lines.append("#25=PRODUCT_DEFINITION('','',#23,#24);")
    lines.append("#26=PRODUCT_DEFINITION_SHAPE('','',#25);")
    lines.append("/* Child product */")
    lines.append("#30=PRODUCT('child_001','Part','Child component',(#21));")
    lines.append("#31=PRODUCT_DEFINITION_FORMATION('','',#30);")
    lines.append("#32=PRODUCT_DEFINITION('','',#31,#24);")
    lines.append("#33=PRODUCT_DEFINITION_SHAPE('','',#32);")
    lines.append("/* Valid placement for transform_item_1 (parent origin) */")
    lines.append("#40=CARTESIAN_POINT('parent_origin',(0.,0.,0.));")
    lines.append("#41=DIRECTION('parent_z',(0.,0.,1.));")
    lines.append("#42=DIRECTION('parent_x',(1.,0.,0.));")
    lines.append("#43=AXIS2_PLACEMENT_3D('parent_placement',#40,#41,#42);")
    lines.append("/* DEFECT: zero-vector DIRECTION in child placement for transform_item_2 */")
    lines.append("/* A zero axis vector makes the transformation matrix geometrically undefined */")
    lines.append("#50=CARTESIAN_POINT('child_origin',(100.,0.,0.));")
    lines.append("/* Byte assertion: matches(rb'DIRECTION\\'zero_vec\\',(0\\.0,0\\.0,0\\.0)\\)') */")
    lines.append("#51=DIRECTION('zero_vec',(0.0,0.0,0.0));")
    lines.append("#52=DIRECTION('child_x',(1.,0.,0.));")
    lines.append("#53=AXIS2_PLACEMENT_3D('child_zero_placement',#50,#51,#52);")
    lines.append("/* Byte assertion: contains(b'ITEM_DEFINED_TRANSFORMATION') */")
    lines.append("/* ITEM_DEFINED_TRANSFORMATION references parent placement and bad child placement */")
    lines.append("#54=ITEM_DEFINED_TRANSFORMATION('xform','assembly transform',#43,#53);")
    lines.append("/* NAUO: parent uses ITEM_DEFINED_TRANSFORMATION to place child */")
    lines.append("#55=NEXT_ASSEMBLY_USAGE_OCCURRENCE('u1','','uses',#25,#32,$);")
    lines.append("#56=PRODUCT_DEFINITION_SHAPE('','',#55);")
    lines.append("#57=CONTEXT_DEPENDENT_SHAPE_REPRESENTATION(#58,#56);")
    lines.append("#58=SHAPE_REPRESENTATION_RELATIONSHIP('rel','',")
    lines.append("  SHAPE_REPRESENTATION('',(#43),#14),")
    lines.append("  SHAPE_REPRESENTATION('',(#53),#14));")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#60=GEOMETRIC_CURVE_SET('transformation-relation-creation-failed-zero-vec',")
    lines.append("  (#43,#53,#54,#55,#40,#50));")
    lines.append("#61=SHAPE_REPRESENTATION('',(#60),#14);")
    lines.append("#62=SHAPE_DEFINITION_REPRESENTATION(#26,#61);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m067(path) -> None:
    Path(path).write_text(_render_m067())


f.render = _render_m067  # type: ignore[method-assign]
f.write = _write_m067    # type: ignore[method-assign]
