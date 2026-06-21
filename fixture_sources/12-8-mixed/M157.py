"""M157 — AP210 solder mask covers a pad that should be exposed

Catalog claim: A solder-mask layer outline (a PLY_BOUNDARY_REPRESENTATION
with a LAMINATE_OR_PLY_DEFINITION of a solder-mask material) encloses
a pad that the placement record requires to be exposed for soldering.
The fabricated board has the pad masked — the component cannot be
reflowed onto it.

Reproducer recipe: LAMINATE_OR_PLY_DEFINITION('solder_mask_top',
..,green_LPI,..) with PLY_BOUNDARY_REPRESENTATION polygon
enclosing a TERMINAL that requires reflow.

Byte assertions:
  contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN')
  contains(b'solder_mask')
  contains(b'PLY_BOUNDARY_REPRESENTATION')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M157",
    defect=(
        "GEOMETRIC_CURVE_SET in AP210 ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN "
        "file where a PLY_BOUNDARY_REPRESENTATION for the solder_mask_top layer encloses "
        "a TERMINAL pad that requires reflow exposure; "
        "input: AP210 STEP file containing a LAMINATE_OR_PLY_DEFINITION 'solder_mask_top' "
        "with material green_LPI representing the solder-mask opening layer; "
        "a PLY_BOUNDARY_REPRESENTATION polygon for the solder mask covers coordinates "
        "(0.0,0.0) to (5.0,5.0) — a 5mm x 5mm rectangle; "
        "TERMINAL 'PAD_U1_1' at (2.5, 2.5, 0.0) lies inside the solder-mask polygon; "
        "the pad requires reflow soldering per its PROPERTY_DEFINITION 'reflow_required'; "
        "the solder-mask polygon should have a pad-clearance cutout at PAD_U1_1 position; "
        "because the cutout is missing the mask covers the pad — it cannot be reflowed; "
        "the ECAD exporter emitted solder-mask outlines before pad-clearance subtraction; "
        "per ISO 10303-210 §5 pads required for reflow must be exposed in the solder mask; "
        "kernel must validate pads required for reflow are not covered by solder mask; "
        "synonyms: AP210 solder mask error, PCB pad blocked, ECAD reflow obstruction, "
        "AP210 solder mask over pad, PCB pad masked, ECAD reflow blocked"
    ),
    schema="AP242",
)


def _render_m157() -> str:
    """Render AP210 file with solder-mask polygon covering a reflow pad.

    Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #50       TERMINAL 'PAD_U1_1' — pad requiring reflow at (2.5, 2.5, 0.0)
      #51       CARTESIAN_POINT for PAD_U1_1 location
      #52       PROPERTY_DEFINITION 'reflow_required' on PAD_U1_1
      #53       DESCRIPTIVE_REPRESENTATION_ITEM 'reflow_required' = 'true'
      #54       REPRESENTATION for reflow property
      #55       PROPERTY_DEFINITION_REPRESENTATION
      #60       LAMINATE_OR_PLY_DEFINITION 'solder_mask_top' — green LPI material
      #70       PLY_BOUNDARY_REPRESENTATION — mask outline enclosing PAD_U1_1 (DEFECT)
      #200      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M157: AP210 solder mask covers a pad that should be exposed */")
    lines.append("/* DEFECT: PLY_BOUNDARY_REPRESENTATION for solder_mask_top encloses PAD_U1_1 */")
    lines.append("/* PAD_U1_1 has reflow_required=true but the mask has no clearance cutout */")
    lines.append("/* The solder-mask polygon was emitted before pad-clearance subtraction */")
    lines.append("/* Per ISO 10303-210 §5 reflow pads must be exposed in the solder mask layer */")
    lines.append("/* Byte assertion: contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'solder_mask') */")
    lines.append("/* Byte assertion: contains(b'PLY_BOUNDARY_REPRESENTATION') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M157: AP210 solder mask covers reflow pad PAD_U1_1'),'2;1');")
    lines.append("FILE_NAME('M157.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* TERMINAL PAD_U1_1: pad at (2.5, 2.5, 0.0) — lies inside the mask polygon */")
    lines.append("#51=CARTESIAN_POINT('PAD_U1_1_loc',(2.5,2.5,0.0));")
    lines.append("#50=TERMINAL('PAD_U1_1',#51);")
    lines.append("/* PROPERTY_DEFINITION 'reflow_required' on PAD_U1_1 — this pad must be exposed */")
    lines.append("#52=PROPERTY_DEFINITION('reflow_required','Pad requires reflow soldering',#50);")
    lines.append("#53=DESCRIPTIVE_REPRESENTATION_ITEM('reflow_required','true');")
    lines.append("#54=REPRESENTATION('pad_props',(#53),#14);")
    lines.append("#55=PROPERTY_DEFINITION_REPRESENTATION(#52,#54);")
    lines.append("/* Byte assertion: contains(b'solder_mask') */")
    lines.append("/* LAMINATE_OR_PLY_DEFINITION 'solder_mask_top' — top solder mask layer */")
    lines.append("#60=LAMINATE_OR_PLY_DEFINITION('solder_mask_top','Top solder mask green LPI',$);")
    lines.append("/* Byte assertion: contains(b'PLY_BOUNDARY_REPRESENTATION') */")
    lines.append("/* DEFECT: PLY_BOUNDARY_REPRESENTATION covers (0,0) to (5,5) — PAD_U1_1 at (2.5,2.5) */")
    lines.append("/* The pad is inside this polygon; no clearance cutout was subtracted *)");
    lines.append("#70=PLY_BOUNDARY_REPRESENTATION('solder_mask_top_outline',#60,")
    lines.append("  (CARTESIAN_POINT('corner_0',(0.0,0.0,0.0)),")
    lines.append("   CARTESIAN_POINT('corner_1',(5.0,0.0,0.0)),")
    lines.append("   CARTESIAN_POINT('corner_2',(5.0,5.0,0.0)),")
    lines.append("   CARTESIAN_POINT('corner_3',(0.0,5.0,0.0))));")
    lines.append("/* PAD_U1_1 at (2.5,2.5) is enclosed by the 0-5 mm mask rectangle — covered */")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#200=GEOMETRIC_CURVE_SET('ap210-solder-mask-covers-reflow-pad-ply-boundary-representation',")
    lines.append("  (#50,#51,#52,#53,#54,#55,#60,#70));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M157','M157','M157',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#200),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m157(path) -> None:
    Path(path).write_text(_render_m157())


f.render = _render_m157  # type: ignore[method-assign]
f.write = _write_m157    # type: ignore[method-assign]
