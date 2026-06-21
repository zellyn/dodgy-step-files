"""M072 — AP238 toolpath_curve open chain claimed as closed contour.

Catalog claim: A TRAJECTORY references a COMPOSITE_CURVE whose
self_intersect = .F. and which is consumed as a closed contouring pass,
but the underlying COMPOSITE_CURVE_SEGMENT chain does not actually close
in 3D (the last segment's endpoint != the first segment's startpoint).
Bug-reporter language: "toolpath should close but doesn't", "contour pass
leaves a gap", "STEP-NC malformed toolpath_curve".

Reproducer recipe: A COMPOSITE_CURVE listing two COMPOSITE_CURVE_SEGMENTs
that form an "L" (e.g. line p1->p2, line p2->p3), referenced by a
TRAJECTORY as if it were a closed loop.

Byte assertions:
  contains(b'AP238_STEP_NC_MIM')
  contains(b'COMPOSITE_CURVE')
  contains(b'TRAJECTORY')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M072",
    defect=(
        "GEOMETRIC_CURVE_SET in AP238 STEP-NC file where TRAJECTORY references a "
        "COMPOSITE_CURVE that does not close in 3D — open chain claimed as closed contour; "
        "input: AP238 STEP-NC file where TRAJECTORY references a COMPOSITE_CURVE with "
        "self_intersect=.F. consumed as a closed contouring pass; "
        "the COMPOSITE_CURVE_SEGMENT chain forms an 'L' shape (p1->p2, p2->p3) "
        "where the last endpoint p3 != first startpoint p1, leaving a gap; "
        "AP238 §6.2 trajectory and basiccurve invariants require closure validation; "
        "kernel must validate continuity/closure before treating as closed contour; "
        "must emit synthesized closing segment, reject as malformed, or treat as open pass; "
        "synonyms: non-closed toolpath, trajectory doesn't loop, "
        "AP238 contour pass not closed, open toolpath claimed as closed"
    ),
    schema="AP242",
)


def _render_m072() -> str:
    """Render AP238 STEP-NC file with open COMPOSITE_CURVE referenced as closed TRAJECTORY.

    The COMPOSITE_CURVE_SEGMENTs form an L: p1(0,0,0)->p2(10,0,0)->p3(10,10,0).
    The chain does not close (p3 != p1), but TRAJECTORY consumes it as a closed loop.

    Entity layout:
      #10-#14   Unit context
      #20-#29   Points and lines for the L-shaped open chain
      #30       COMPOSITE_CURVE_SEGMENT #1 (line p1->p2)
      #31       COMPOSITE_CURVE_SEGMENT #2 (line p2->p3)
      #32       COMPOSITE_CURVE (L-shaped, open — self_intersect=.F.)
      #40       TRAJECTORY referencing the open COMPOSITE_CURVE as closed
      #50       WORKPLAN
      #60       GEOMETRIC_CURVE_SET model entity
      #70+      Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M072: AP238 TRAJECTORY references open COMPOSITE_CURVE as closed contour */")
    lines.append("/* DEFECT: L-shaped chain (p1->p2->p3) does not close; p3 != p1 */")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("/* Byte assertion: contains(b'COMPOSITE_CURVE') */")
    lines.append("/* Byte assertion: contains(b'TRAJECTORY') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M072: AP238 toolpath_curve open chain claimed as closed contour'),'2;1');")
    lines.append("FILE_NAME('M072.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
    lines.append("/* Byte assertion: contains(b'AP238_STEP_NC_MIM') */")
    lines.append("FILE_SCHEMA(('AP238_STEP_NC_MIM { 1 0 10303 238 3 1 1 1 }'));")
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
    lines.append("/* L-shaped open chain: p1(0,0,0) -> p2(10,0,0) -> p3(10,10,0) */")
    lines.append("/* The chain does NOT close: p3(10,10,0) != p1(0,0,0) */")
    lines.append("#20=CARTESIAN_POINT('p1',(0.,0.,0.));")
    lines.append("#21=CARTESIAN_POINT('p2',(10.,0.,0.));")
    lines.append("#22=CARTESIAN_POINT('p3',(10.,10.,0.));")
    lines.append("/* Line seg 1: p1 -> p2 (along X axis) */")
    lines.append("#23=DIRECTION('dir_x',(1.,0.,0.));")
    lines.append("#24=VECTOR(#23,10.);")
    lines.append("#25=LINE('seg1_line',#20,#24);")
    lines.append("/* Line seg 2: p2 -> p3 (along Y axis) */")
    lines.append("#26=DIRECTION('dir_y',(0.,1.,0.));")
    lines.append("#27=VECTOR(#26,10.);")
    lines.append("#28=LINE('seg2_line',#21,#27);")
    lines.append("/* COMPOSITE_CURVE_SEGMENTs forming the L shape */")
    lines.append("#30=COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,#25);")
    lines.append("#31=COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,#28);")
    lines.append("/* Byte assertion: contains(b'COMPOSITE_CURVE') */")
    lines.append("/* COMPOSITE_CURVE: self_intersect=.F., open chain claimed as closed by TRAJECTORY */")
    lines.append("#32=COMPOSITE_CURVE('l_shaped_toolpath',(#30,#31),.F.);")
    lines.append("/* Byte assertion: contains(b'TRAJECTORY') */")
    lines.append("/* TRAJECTORY references the open composite curve as a closed contour */")
    lines.append("#40=TRAJECTORY('contour_pass','closed contouring trajectory',(),(),#32,$);")
    lines.append("/* WORKPLAN wrapping the trajectory */")
    lines.append("#50=WORKPLAN('main_program','AP238 STEP-NC workplan',(),$,());")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#60=GEOMETRIC_CURVE_SET('ap238-toolpath-open-chain-claimed-closed',")
    lines.append("  (#32,#40,#20,#21,#22,#25,#28));")
    lines.append("/* Product chain */")
    lines.append("#70=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#71=PRODUCT_CONTEXT('',#70,'mechanical');")
    lines.append("#72=PRODUCT('M072','M072','M072',(#71));")
    lines.append("#73=PRODUCT_DEFINITION_FORMATION('','',#72);")
    lines.append("#74=PRODUCT_DEFINITION_CONTEXT(#70,'design');")
    lines.append("#75=PRODUCT_DEFINITION('','',#73,#74);")
    lines.append("#76=PRODUCT_DEFINITION_SHAPE('','',#75);")
    lines.append("#77=SHAPE_REPRESENTATION('',(#60),#14);")
    lines.append("#78=SHAPE_DEFINITION_REPRESENTATION(#76,#77);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m072(path) -> None:
    Path(path).write_text(_render_m072())


f.render = _render_m072  # type: ignore[method-assign]
f.write = _write_m072    # type: ignore[method-assign]
