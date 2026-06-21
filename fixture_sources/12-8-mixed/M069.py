"""M069 — TRIANGULATED_FACE emitted without pnval indices.

Catalog claim: A TRIANGULATED_FACE is supposed to reference vertex indices
via pnval (parametric values). When the tessellation was built from a
non-parametric source (mesh-only), pnval is empty; AP242 readers expect
at least one entry and reject the entity, dropping the face.

Reproducer recipe: TRIANGULATED_FACE with pnval = () (empty list).

Byte assertions:
  contains(b'TRIANGULATED_FACE')
  contains(b'no_pnval')
  contains(b"TRIANGULATED_FACE('no_pnval','',(#100),(),(),(),'',$)")

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M069",
    defect=(
        "GEOMETRIC_CURVE_SET in file containing TRIANGULATED_FACE with empty pnval — "
        "AP242 readers reject face with missing parametric indices, dropping the face; "
        "input: AP242 STEP file where TRIANGULATED_FACE('no_pnval','',(#100),(),(),(),'',$) "
        "has an empty pnval list () — the parametric-value index list is absent; "
        "when tessellation was built from a non-parametric mesh-only source, pnval is empty; "
        "AP242 readers that require at least one pnval entry reject the entity and drop the face; "
        "kernel must heal and accept: empty pnval is legal; fall back to 3D vertex indices "
        "for parameterless meshes; emit synthetic UV when downstream consumers require it; "
        "synonyms: TRIANGULATED_FACE missing pnval, AP242 reader rejects empty pnval, "
        "tessellated face has no parametric indices, mesh-only triangulation lacks UV indices"
    ),
    schema="AP242",
)


def _render_m069() -> str:
    """Render AP242 file with TRIANGULATED_FACE having empty pnval.

    Entity layout:
      #10-#14  Unit context
      #100     COORDINATES_LIST (vertex coords)
      #101     TRIANGULATED_FACE with pnval=() — the defect
                 form: TRIANGULATED_FACE('no_pnval','',(#100),(),(),(),'',$)
      #110     GEOMETRIC_CURVE_SET model entity
      #120+    PRODUCT chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M069: TRIANGULATED_FACE emitted without pnval indices */")
    lines.append("/* DEFECT: empty pnval () causes AP242 readers to reject and drop the face */")
    lines.append("/* Kernel must heal: empty pnval is valid for non-parametric mesh sources */")
    lines.append("/* Byte assertion: contains(b'TRIANGULATED_FACE') */")
    lines.append("/* Byte assertion: contains(b'no_pnval') */")
    lines.append("/* Byte assertion: contains(b\"TRIANGULATED_FACE('no_pnval','',(#100),(),(),(),'',\$)\") */")
    lines.append("HEADER;")
    # Note: \$ in the comment above renders as \$ in the file (cosmetic only);
    # the actual entity line below uses a plain $ which satisfies the byte assertion.
    lines.append("FILE_DESCRIPTION(('M069: TRIANGULATED_FACE emitted without pnval indices'),'2;1');")
    lines.append("FILE_NAME('M069.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* COORDINATES_LIST for the tessellated face vertices */")
    lines.append("#100=COORDINATES_LIST('mesh_verts',3,")
    lines.append("  ((0.,0.,0.),(5.,0.,0.),(5.,5.,0.),(0.,5.,0.)));")
    lines.append("/* TRIANGULATED_FACE with empty pnval () — the defect */")
    lines.append("/* AP242 TRIANGULATED_FACE attributes: name, description, coordinates,")
    lines.append("   pnindex, normals, pnval, geometry_link, face_shape_representation */")
    lines.append("/* Byte assertion: contains(b'no_pnval') */")
    # Build entity using string concatenation so $ is a plain literal character
    null_attr = "$"
    lines.append(
        "#101=TRIANGULATED_FACE('no_pnval','',(#100),(),(),(),''" + "," + null_attr + ");"
    )
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#110=GEOMETRIC_CURVE_SET('triangulated-face-missing-pnval-indices',")
    lines.append("  (#100,#101));")
    lines.append("/* PRODUCT chain */")
    lines.append("#120=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#121=PRODUCT_CONTEXT('',#120,'mechanical');")
    lines.append("#122=PRODUCT('M069','M069','M069',(#121));")
    lines.append("#123=PRODUCT_DEFINITION_FORMATION('','',#122);")
    lines.append("#124=PRODUCT_DEFINITION_CONTEXT(#120,'design');")
    lines.append("#125=PRODUCT_DEFINITION('','',#123,#124);")
    lines.append("#126=PRODUCT_DEFINITION_SHAPE('','',#125);")
    lines.append("#127=SHAPE_REPRESENTATION('',(#110),#14);")
    lines.append("#128=SHAPE_DEFINITION_REPRESENTATION(#126,#127);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m069(path) -> None:
    Path(path).write_text(_render_m069())


f.render = _render_m069  # type: ignore[method-assign]
f.write = _write_m069    # type: ignore[method-assign]
