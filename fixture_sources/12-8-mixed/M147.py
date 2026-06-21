"""M147 — AP210 surface-mount component oriented on wrong board side

Catalog claim: A component placement transform on the bottom side
(origin at z=0, normal = -Z) is applied to a part declared as a
top-only SMD package (e.g. BGA). The footprint resolves below the
board surface; the BGA balls face away from the PCB.

Reproducer recipe: AXIS2_PLACEMENT_3D with DIRECTION(0.0,0.0,-1.0)
placed at z=0; component PRODUCT carries
DESCRIPTIVE_REPRESENTATION_ITEM('mount_constraint','TOP_ONLY').

Byte assertions:
  contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN')
  contains(b'AXIS2_PLACEMENT_3D')
  contains(b'TOP_ONLY')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M147",
    defect=(
        "GEOMETRIC_CURVE_SET in AP210 ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN "
        "file where a component placement transform on the bottom side of the PCB is applied "
        "to a PRODUCT declared as a TOP_ONLY surface-mount package; "
        "input: AP210 STEP file containing a PRODUCT 'BGA256' representing a 256-ball BGA "
        "package; a PROPERTY_DEFINITION 'mount_constraint' attached to BGA256 is represented "
        "by DESCRIPTIVE_REPRESENTATION_ITEM with value 'TOP_ONLY' — the package may only be "
        "placed on the top face of the PCB; "
        "the placement AXIS2_PLACEMENT_3D #201 uses a z-axis DIRECTION of (0.0, 0.0, -1.0) "
        "pointing downward (into the board bottom) with origin at CARTESIAN_POINT(15.0, 20.0, 0.0); "
        "the -Z normal indicates a bottom-side placement; the footprint resolves below the "
        "board surface; the BGA solder balls face away from the PCB copper pads; "
        "the component cannot be soldered — the placement is fundamentally invalid; "
        "per ISO 10303-210 §6 the placement axis must agree with the mount_constraint; "
        "kernel must validate placement orientation against mount_constraint and reject or warn; "
        "synonyms: AP210 SMD wrong side, PCB BGA on bottom, ECAD top-only part placed bottom, "
        "AP210 wrong-side placement, BGA on bottom, PCB SMD orientation error, "
        "AP210 mount-side violation, PCB component wrong side"
    ),
    schema="AP242",
)


def _render_m147() -> str:
    """Render AP210 file with TOP_ONLY BGA component placed on bottom side.

    Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #100      PRODUCT 'BGA256' — the top-only SMD package
      #110      PROPERTY_DEFINITION 'mount_constraint' attached to BGA256
      #111      DESCRIPTIVE_REPRESENTATION_ITEM 'mount_constraint' = 'TOP_ONLY'
      #112      REPRESENTATION holding mount_constraint item
      #113      PROPERTY_DEFINITION_REPRESENTATION
      #200      CARTESIAN_POINT for placement origin at (15.0, 20.0, 0.0)
      #202      DIRECTION (0.0, 0.0, -1.0) — bottom-side placement
      #201      AXIS2_PLACEMENT_3D — DEFECT: -Z normal means bottom-side placement
      #300      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M147: AP210 surface-mount component oriented on wrong board side */")
    lines.append("/* DEFECT: BGA256 declared TOP_ONLY but placement uses -Z normal (bottom side) */")
    lines.append("/* BGA solder balls face away from the PCB — component cannot be soldered */")
    lines.append("/* Per ISO 10303-210 §6 placement axis must agree with mount_constraint */")
    lines.append("/* Byte assertion: contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'AXIS2_PLACEMENT_3D') */")
    lines.append("/* Byte assertion: contains(b'TOP_ONLY') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M147: AP210 TOP_ONLY SMD component placed on bottom side'),'2;1');")
    lines.append("FILE_NAME('M147.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
    lines.append("/* Byte assertion: contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN') */")
    lines.append("FILE_SCHEMA(('ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN { 1 0 10303 210 3 1 0 }'));")
    lines.append("ENDSEC;")
    lines.append("DATA;")
    lines.append("#1=APPLICATION_CONTEXT('electronic_assembly_interconnect_and_packaging_design');")
    lines.append("#2=APPLICATION_PROTOCOL_DEFINITION('international standard',")
    lines.append("  'electronic_assembly_interconnect_and_packaging_design',2014,#1);")
    lines.append("/* Standard unit context (mm) */")
    lines.append("#10=(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.));")
    lines.append("#11=(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.));")
    lines.append("#12=(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT());")
    lines.append("#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#10,")
    lines.append("  'distance_accuracy_value','maximum model space distance between geometric entities');")
    lines.append("#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3)")
    lines.append("  GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))")
    lines.append("  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12))")
    lines.append("  REPRESENTATION_CONTEXT('pcb','3D'));")
    lines.append("/* BGA256 component product — 256-ball BGA surface-mount package */")
    lines.append("#100=PRODUCT('BGA256','BGA256','256-ball BGA package',(#1));")
    lines.append("/* Byte assertion: contains(b'TOP_ONLY') */")
    lines.append("/* mount_constraint property declares BGA256 is a top-side-only package */")
    lines.append("#110=PROPERTY_DEFINITION('mount_constraint','Placement side constraint',#100);")
    lines.append("#111=DESCRIPTIVE_REPRESENTATION_ITEM('mount_constraint','TOP_ONLY');")
    lines.append("#112=REPRESENTATION('mount',(#111),#14);")
    lines.append("#113=PROPERTY_DEFINITION_REPRESENTATION(#110,#112);")
    lines.append("/* Byte assertion: contains(b'AXIS2_PLACEMENT_3D') */")
    lines.append("/* Placement origin on the PCB at position (15.0, 20.0, 0.0) */")
    lines.append("#200=CARTESIAN_POINT('bga_origin',(15.0,20.0,0.0));")
    lines.append("/* DEFECT: z-axis direction (0,0,-1) = -Z normal = bottom-side placement */")
    lines.append("/* A TOP_ONLY package requires +Z normal (0,0,1) for top-side placement */")
    lines.append("#202=DIRECTION('bottom_normal',(0.0,0.0,-1.0));")
    lines.append("#201=AXIS2_PLACEMENT_3D('bga_placement',#200,#202,$);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#300=GEOMETRIC_CURVE_SET('ap210-smd-component-oriented-on-wrong-board-side',")
    lines.append("  (#100,#110,#111,#112,#113,#200,#202,#201));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M147','M147','M147',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#300),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m147(path) -> None:
    Path(path).write_text(_render_m147())


f.render = _render_m147  # type: ignore[method-assign]
f.write = _write_m147    # type: ignore[method-assign]
