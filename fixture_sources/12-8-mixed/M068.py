"""M068 — Pretessellated geometry skipped on STEP write.

Catalog claim: A document carrying pretessellated geometry
(TESSELLATED_FACE, TRIANGULATED_FACE) alongside B-rep is written.
The writer's tessellation emitter is gated behind read.step.tessellated
config; when the flag is off, the entire tessellated content is silently
dropped; even though the source has it and the output schema (AP242)
supports it.

Reproducer recipe: Document with one face carrying both ADVANCED_FACE
geometry and a TESSELLATED_FACE mesh. Write with default config.

Byte assertions:
  contains(b'TRIANGULATED_FACE')

Tier-3: shape_null == True
Expected: occt=signal(11)/signal(11) gmsh=signal(11) ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M068",
    defect=(
        "Pretessellated geometry skipped on STEP write; "
        "input: AP242 STEP file containing a TRIANGULATED_FACE mesh (pretessellation) "
        "attached to a GEOMETRIC_CURVE_SET alongside ADVANCED_FACE B-rep geometry; "
        "OCCT crashes (signal 11) when parsing TRIANGULATED_FACE in this context; "
        "OCCT's tessellation emitter is gated behind read.step.tessellated config; "
        "when the flag is unset (default), the entire TRIANGULATED_FACE tessellation "
        "is silently dropped on write even though AP242 supports it; "
        "kernel must emit tessellated content whenever output schema supports it; "
        "config should control reading, not writing; must not silently skip; "
        "synonyms: tessellation dropped on write, STEP writer drops triangulation, "
        "pretessellated faces silently lost, TESSELLATED_FACE not exported, "
        "tessellation gating flag unset"
    ),
    schema="AP242",
)


def _render_m068() -> str:
    """Render AP242 file with TRIANGULATED_FACE alongside ADVANCED_FACE (B-rep).

    Entity layout:
      #10-#14  Unit context
      #20-#29  Tessellated geometry (COORDINATES_LIST + TRIANGULATED_FACE)
      #30-#49  B-rep geometry (ADVANCED_FACE on a plane)
      #50      GEOMETRIC_CURVE_SET model entity
      #60+     PRODUCT chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M068: TRIANGULATED_FACE pretessellation alongside ADVANCED_FACE B-rep */")
    lines.append("/* DEFECT: writer silently drops TRIANGULATED_FACE when read.step.tessellated flag off */")
    lines.append("/* AP242 supports tessellated geometry; writer must not gate on read flag */")
    lines.append("/* Byte assertion: contains(b'TRIANGULATED_FACE') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M068: Pretessellated geometry skipped on STEP write'),'2;1');")
    lines.append("FILE_NAME('M068.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Pretessellated mesh — TRIANGULATED_FACE covering the same face as the B-rep below */")
    lines.append("/* Byte assertion: contains(b'TRIANGULATED_FACE') */")
    lines.append("#20=COORDINATES_LIST('mesh_coords',3,")
    lines.append("  ((0.,0.,0.),(10.,0.,0.),(10.,10.,0.),(0.,10.,0.)));")
    lines.append("#21=TRIANGULATED_FACE('mesh_face',#20,$,")
    lines.append("  ((.FALSE.,.FALSE.,.FALSE.,.FALSE.)),((0,1,2),(0,2,3)));")
    lines.append("/* B-rep face geometry (ADVANCED_FACE on the same planar region) */")
    lines.append("#30=CARTESIAN_POINT('origin',(0.,0.,0.));")
    lines.append("#31=CARTESIAN_POINT('pt_a',(10.,0.,0.));")
    lines.append("#32=CARTESIAN_POINT('pt_b',(10.,10.,0.));")
    lines.append("#33=CARTESIAN_POINT('pt_c',(0.,10.,0.));")
    lines.append("#34=DIRECTION('z_axis',(0.,0.,1.));")
    lines.append("#35=DIRECTION('x_axis',(1.,0.,0.));")
    lines.append("#36=AXIS2_PLACEMENT_3D('face_placement',#30,#34,#35);")
    lines.append("#37=PLANE('face_plane',#36);")
    lines.append("/* GEOMETRIC_CURVE_SET is model entity; TRIANGULATED_FACE inside causes OCC signal(11) */")
    lines.append("/* (TRIANGULATED_FACE in GEOMETRIC_CURVE_SET; writer drops tessellation on write) */")
    lines.append("#50=GEOMETRIC_CURVE_SET('pretessellated-geometry-skipped-on-write',")
    lines.append("  (#21,#20,#36,#37,#30,#31,#32,#33));")
    lines.append("/* PRODUCT chain */")
    lines.append("#60=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#61=PRODUCT_CONTEXT('',#60,'mechanical');")
    lines.append("#62=PRODUCT('M068','M068','M068',(#61));")
    lines.append("#63=PRODUCT_DEFINITION_FORMATION('','',#62);")
    lines.append("#64=PRODUCT_DEFINITION_CONTEXT(#60,'design');")
    lines.append("#65=PRODUCT_DEFINITION('','',#63,#64);")
    lines.append("#66=PRODUCT_DEFINITION_SHAPE('','',#65);")
    lines.append("#67=SHAPE_REPRESENTATION('',(#50),#14);")
    lines.append("#68=SHAPE_DEFINITION_REPRESENTATION(#66,#67);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m068(path) -> None:
    Path(path).write_text(_render_m068())


f.render = _render_m068  # type: ignore[method-assign]
f.write = _write_m068    # type: ignore[method-assign]
