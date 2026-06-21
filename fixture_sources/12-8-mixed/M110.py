"""M110 — AP209 ply orientation vector not normalized.

Catalog claim: A composite ply's fiber orientation DIRECTION ratios sum
to a magnitude of e.g. 2.0 (vector (2.0, 0.0, 0.0)) instead of unit
length. STEP DIRECTION is supposed to be unit-normalized; consumers that
use the ratios directly (e.g. for stiffness-matrix transformation) compute
doubled effective fiber-angle weight.

Reproducer recipe: DIRECTION('ply_0deg', (2.0, 0.0, 0.0)) referenced
as a ply orientation in a LAMINATE_TABLE.

Byte assertions:
  contains(b'STRUCTURAL_ANALYSIS_DESIGN')
  contains(b'DIRECTION')
  contains(b'(2.0,0.0,0.0)')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M110",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP209 composite ply with an unnormalized fiber "
        "orientation DIRECTION whose ratios have magnitude 2.0 instead of 1.0; "
        "input: AP209 STEP file where a DIRECTION entity 'ply_0deg' carries ratios "
        "(2.0,0.0,0.0) — magnitude sqrt(4+0+0) = 2.0, not the required unit length 1.0; "
        "this DIRECTION is referenced as the fiber orientation in a LAMINATE_TABLE ply entry; "
        "per ISO 10303-42 direction normalization convention and AP209 §8 composite ply "
        "orientation, DIRECTION ratios must form a unit vector (magnitude exactly 1.0); "
        "consumers that use the direction ratios directly in stiffness-matrix coordinate "
        "transformations compute a doubled effective fiber-angle contribution, producing "
        "a laminate stiffness matrix that is wrong by a factor of 2 in the fiber direction; "
        "this causes composite structural analysis to overpredict in-plane stiffness; "
        "kernel must normalize direction silently and warn; or reject the ply specification "
        "as malformed and require the CAD/CAM tool to resubmit with a unit-length vector; "
        "synonyms: AP209 unnormalized direction, ply orientation magnitude wrong, "
        "fiber DIRECTION not unit length, STEP DIRECTION ratios sum >1, "
        "AP209 ply direction not unit, fiber angle vector wrong magnitude, "
        "composite stiffness 2x off"
    ),
    schema="AP242",
)


def _render_m110() -> str:
    """Render AP209 file with ply DIRECTION having magnitude 2.0 instead of 1.0.

    Uses STRUCTURAL_ANALYSIS_DESIGN schema. Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #50       DIRECTION('ply_0deg', (2.0,0.0,0.0)) — DEFECT: magnitude 2.0 not 1.0
      #60       AXIS2_PLACEMENT_3D using defective direction #50 as orientation axis
      #70       PLY_LAMINATE_DEFINITION referencing the unnormalized ply direction
      #80       LAMINATE_TABLE holding the defective ply orientation
      #300      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M110: AP209 ply orientation vector not normalized */")
    lines.append("/* DEFECT: DIRECTION('ply_0deg',(2.0,0.0,0.0)) — magnitude=2.0, not unit length */")
    lines.append("/* Consumers computing stiffness-matrix transforms get 2x effective fiber weight */")
    lines.append("/* Violates ISO 10303-42 direction normalization and AP209 §8 ply orientation */")
    lines.append("/* Byte assertion: contains(b'STRUCTURAL_ANALYSIS_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'DIRECTION') */")
    lines.append("/* Byte assertion: contains(b'(2.0,0.0,0.0)') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M110: AP209 ply orientation DIRECTION not unit normalized'),'2;1');")
    lines.append("FILE_NAME('M110.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
    lines.append("/* Byte assertion: contains(b'STRUCTURAL_ANALYSIS_DESIGN') */")
    lines.append("FILE_SCHEMA(('STRUCTURAL_ANALYSIS_DESIGN { 1 0 10303 209 1 0 0 }'));")
    lines.append("ENDSEC;")
    lines.append("DATA;")
    lines.append("#1=APPLICATION_CONTEXT('structural_analysis_design');")
    lines.append("#2=APPLICATION_PROTOCOL_DEFINITION('international standard',")
    lines.append("  'structural_analysis_design',2001,#1);")
    lines.append("/* Standard unit context */")
    lines.append("#10=(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.));")
    lines.append("#11=(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.));")
    lines.append("#12=(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT());")
    lines.append("#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#10,")
    lines.append("  'distance_accuracy_value','maximum model space distance between geometric entities');")
    lines.append("#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3)")
    lines.append("  GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))")
    lines.append("  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12))")
    lines.append("  REPRESENTATION_CONTEXT('fea','3D'));")
    lines.append("/* Byte assertion: contains(b'DIRECTION') */")
    lines.append("/* Byte assertion: contains(b'(2.0,0.0,0.0)') */")
    lines.append("/* DEFECT: ply_0deg direction has magnitude 2.0 — should be (1.0,0.0,0.0) */")
    lines.append("/* CAM tool stored raw vector without normalisation; magnitude = sqrt(4) = 2.0 */")
    lines.append("#50=DIRECTION('ply_0deg',(2.0,0.0,0.0));")
    lines.append("/* Normal to ply plane — correctly unit-normalised (0 deg layup on XY plane) */")
    lines.append("#51=DIRECTION('ply_normal',(0.0,0.0,1.0));")
    lines.append("/* Origin for ply axis placement */")
    lines.append("#52=CARTESIAN_POINT('ply_origin',(0.0,0.0,0.0));")
    lines.append("/* AXIS2_PLACEMENT_3D using the defective unnormalized direction as ref direction *)  */")
    lines.append("#60=AXIS2_PLACEMENT_3D('ply_axis',#52,#51,#50);")
    lines.append("/* PLY_LAMINATE_DEFINITION referencing the unnormalized ply orientation axis */")
    lines.append("#70=PLY_LAMINATE_DEFINITION('ply_0',#60,$,$,$);")
    lines.append("/* LAMINATE_TABLE holding the defective ply entry *)  */")
    lines.append("#80=LAMINATE_TABLE('layup_A',(#70),$);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#300=GEOMETRIC_CURVE_SET('ap209-ply-orientation-direction-not-unit-normalized',")
    lines.append("  (#50,#51,#52,#60,#70,#80));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M110','M110','M110',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#300),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m110(path) -> None:
    Path(path).write_text(_render_m110())


f.render = _render_m110  # type: ignore[method-assign]
f.write = _write_m110    # type: ignore[method-assign]
