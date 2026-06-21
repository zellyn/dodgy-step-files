"""M101 — AP238 two5d_milling_operation applied to a 3D-only feature.

Catalog claim: A TWO5D_MILLING_OPERATION (Z-constant, X-Y contour pass)
references a feature whose toolpath topology is intrinsically 3D; e.g. a
FREEFORM_FEATURE on a sculpted surface. The 2.5D Z-step semantics cannot
represent the surface; consumers either silently approximate (gouging the
surface or leaving stock) or fail to plan motion.

Reproducer recipe: A TWO5D_MILLING_OPERATION whose its_feature
attribute references a freeform-surface feature.

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'TWO5D_MILLING_OPERATION')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M101",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP238 TWO5D_MILLING_OPERATION referencing a 3D "
        "freeform feature — 2.5D Z-step semantics cannot represent a sculpted surface; "
        "input: AP238 STEP-NC file where a TWO5D_MILLING_OPERATION('contour_2p5d') "
        "references its_feature pointing to a FREEFORM_FEATURE on a sculpted surface; "
        "per ISO 10303-238 §5.8 two5d_milling_operation applicability constraints "
        "the operation is restricted to features whose toolpath topology is Z-constant; "
        "a FREEFORM_FEATURE on a sculpted surface is intrinsically 3D — the surface "
        "curvature requires simultaneous X, Y and Z motion to follow it correctly; "
        "a 2.5D Z-step pass on a 3D freeform feature either gouges the surface "
        "(removing material below the intended surface) or leaves excess stock; "
        "kernel must validate operation-feature dimensionality match; reject or warn "
        "that operation is geometrically inadequate for the referenced feature; "
        "synonyms: 2.5D vs 3D mismatch, AP238 operation feature dimensionality, "
        "Z-step on freeform, AP238 2.5D op on 3D feature, STEP-NC contour can't follow surface, "
        "wrong operation type for feature"
    ),
    schema="AP242",
)


def _render_m101() -> str:
    """Render AP238 file with TWO5D_MILLING_OPERATION on a FREEFORM_FEATURE.

    Uses AP238_STEP_NC_MIM schema. Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #50       FREEFORM_FEATURE 'sculpted_surface' — a 3D-only feature (DEFECT target)
      #60       MACHINING_TOOL 'ballmill_6mm'
      #70       TWO5D_MILLING_OPERATION referencing #50 (3D feature) — DEFECT
      #80       MACHINING_WORKINGSTEP wrapping #70
      #90       WORKPLAN referencing the workingstep
      #300      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M101: AP238 TWO5D_MILLING_OPERATION applied to a 3D-only feature */")
    lines.append("/* DEFECT: TWO5D_MILLING_OPERATION references FREEFORM_FEATURE (sculpted surface) */")
    lines.append("/* 2.5D Z-step semantics cannot follow intrinsically 3D surface curvature */")
    lines.append("/* Violates ISO 10303-238 §5.8 two5d_milling_operation applicability constraints */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'TWO5D_MILLING_OPERATION') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M101: AP238 TWO5D_MILLING_OPERATION on 3D freeform feature'),'2;1');")
    lines.append("FILE_NAME('M101.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("FILE_SCHEMA(('AP238_STEP_NC_MIM { 1 0 10303 238 1 0 0 }'));")
    lines.append("ENDSEC;")
    lines.append("DATA;")
    lines.append("#1=APPLICATION_CONTEXT('step_nc_mim');")
    lines.append("#2=APPLICATION_PROTOCOL_DEFINITION('international standard',")
    lines.append("  'ap238_step_nc_mim',2007,#1);")
    lines.append("/* Standard unit context — mm */")
    lines.append("#10=(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.));")
    lines.append("#11=(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.));")
    lines.append("#12=(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT());")
    lines.append("#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#10,")
    lines.append("  'distance_accuracy_value','maximum model space distance between geometric entities');")
    lines.append("#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3)")
    lines.append("  GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))")
    lines.append("  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12))")
    lines.append("  REPRESENTATION_CONTEXT('nc','3D'));")
    lines.append("/* DEFECT target: FREEFORM_FEATURE is an intrinsically 3D feature */")
    lines.append("/* Sculpted surfaces require simultaneous X, Y, Z motion — incompatible with 2.5D */")
    lines.append("#50=FREEFORM_FEATURE('sculpted_surface',$,$,$,$,$);")
    lines.append("/* Ball-end mill for the (incorrectly typed) operation */")
    lines.append("#60=MACHINING_TOOL('ballmill_6mm',$,$,$);")
    lines.append("/* Byte assertion: contains(b'TWO5D_MILLING_OPERATION') */")
    lines.append("/* DEFECT: TWO5D_MILLING_OPERATION references its_feature=#50 (FREEFORM_FEATURE) */")
    lines.append("/* A 2.5D operation cannot represent 3D surface curvature — gouge or stock remains */")
    lines.append("#70=TWO5D_MILLING_OPERATION('contour_2p5d',#60,$,$,$,$,$,$,#50,$,$);")
    lines.append("/* Workingstep and workplan */")
    lines.append("#80=MACHINING_WORKINGSTEP('contour_step',#50,#70,$);")
    lines.append("#90=WORKPLAN('main',(#80),$,$,$);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#300=GEOMETRIC_CURVE_SET('ap238-two5d-milling-op-on-3d-freeform-feature',")
    lines.append("  (#50,#60,#70,#80,#90));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M101','M101','M101',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#300),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m101(path) -> None:
    Path(path).write_text(_render_m101())


f.render = _render_m101  # type: ignore[method-assign]
f.write = _write_m101    # type: ignore[method-assign]
