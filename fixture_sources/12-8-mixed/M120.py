"""M120 — AP209 symmetry plane not perpendicular to a coordinate axis.

Catalog claim: A symmetry boundary condition is encoded with a plane normal of
(0.5, 0.5, 0.707) (non-axis-aligned). The constraint pattern restricts only
U_x (X-DOF) without rotating to the plane frame. On a curved shell the global-X
encoding wraps around and applies the wrong physics.

Reproducer recipe: A SINGLE_POINT_CONSTRAINT interpreted as symmetry with a
normal direction (0.5,0.5,0.707), paired with a constraint pattern restricting
only U_x (X-DOF), without rotating the constraint basis to the symmetry frame.

Byte assertions:
  contains(b'STRUCTURAL_ANALYSIS_DESIGN')
  contains(b'SINGLE_POINT_CONSTRAINT')
  contains(b'(0.5,0.5,0.707)')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M120",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP209 SINGLE_POINT_CONSTRAINT encoding a "
        "symmetry boundary condition with a non-axis-aligned plane normal (0.5,0.5,0.707) "
        "but restricting only the X-DOF (U_x=0) without rotating to the symmetry frame; "
        "input: AP209 STEP file where a SINGLE_POINT_CONSTRAINT is annotated as a "
        "symmetry boundary condition with symmetry-plane normal direction (0.5,0.5,0.707) "
        "but the DOF restriction pattern encodes only U_x = 0 as if the plane were "
        "perpendicular to the global X-axis; "
        "per ISO 10303-209 §7 symmetry_plane DOF-restriction semantics, a symmetry "
        "condition requires restricting displacement normal to the plane and rotation "
        "about all in-plane axes; for an axis-aligned plane the constraint reduces to "
        "a single scalar DOF; for a non-axis-aligned plane (0.5,0.5,0.707) the solver "
        "must transform the constraint to a rotated frame; encoding only U_x=0 applies "
        "the constraint in the wrong direction; "
        "actual physics: the skew normal means the structural model is not symmetric "
        "about any coordinate plane; applying U_x=0 over-constrains some DOFs and "
        "under-constrains others; results are non-conservative; "
        "kernel must reject if the symmetry plane normal is non-axis-aligned, or "
        "transform the constraint into the symmetry-plane frame; "
        "synonyms: AP209 skew symmetry, non-axis symmetry plane, symmetry plane not "
        "aligned with coordinate axis, FEM symmetry boundary off-axis, symmetry "
        "constraint can't reduce to scalar BCs, AP209 symmetry plane not aligned, "
        "FEM symmetry BC at angle, skew symmetry applied as axis-aligned"
    ),
    schema="AP242",
)


def _render_m120() -> str:
    """Render AP209 file with SINGLE_POINT_CONSTRAINT for skew symmetry plane.

    Uses STRUCTURAL_ANALYSIS_DESIGN schema. Entity layout:
      #1-#2      APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14    Unit context (mm)
      #100       CARTESIAN_POINT at constrained node
      #101       DIRECTION representing the skew symmetry-plane normal (0.5,0.5,0.707)
      #102       AXIS2_PLACEMENT_3D for the symmetry plane orientation
      #110       NODE entity
      #200       SINGLE_POINT_CONSTRAINT with skew normal, DOF restricted = U_x only — DEFECT
      #300       NODE_GROUP
      #310       FEA_MODEL
      #500       GEOMETRIC_CURVE_SET model entity
      #600+      Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M120: AP209 symmetry plane not perpendicular to a coordinate axis */")
    lines.append("/* DEFECT: SINGLE_POINT_CONSTRAINT symmetry-plane normal = (0.5,0.5,0.707) */")
    lines.append("/* Constraint restricts only U_x=0 without rotating to the symmetry frame */")
    lines.append("/* Skew normal means no coordinate plane corresponds to the symmetry surface */")
    lines.append("/* Per AP209 §7, non-axis-aligned symmetry requires frame transformation */")
    lines.append("/* Byte assertion: contains(b'STRUCTURAL_ANALYSIS_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'SINGLE_POINT_CONSTRAINT') */")
    lines.append("/* Byte assertion: contains(b'(0.5,0.5,0.707)') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M120: AP209 symmetry plane not perpendicular to coordinate axis'),'2;1');")
    lines.append("FILE_NAME('M120.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
    lines.append("/* Byte assertion: contains(b'STRUCTURAL_ANALYSIS_DESIGN') */")
    lines.append("FILE_SCHEMA(('STRUCTURAL_ANALYSIS_DESIGN { 1 0 10303 209 1 0 0 }'));")
    lines.append("ENDSEC;")
    lines.append("DATA;")
    lines.append("#1=APPLICATION_CONTEXT('structural_analysis_design');")
    lines.append("#2=APPLICATION_PROTOCOL_DEFINITION('international standard',")
    lines.append("  'structural_analysis_design',2001,#1);")
    lines.append("/* Standard unit context (mm) */")
    lines.append("#10=(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.));")
    lines.append("#11=(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.));")
    lines.append("#12=(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT());")
    lines.append("#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#10,")
    lines.append("  'distance_accuracy_value','maximum model space distance between geometric entities');")
    lines.append("#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3)")
    lines.append("  GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))")
    lines.append("  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12))")
    lines.append("  REPRESENTATION_CONTEXT('fea','3D'));")
    lines.append("/* Node on the symmetry plane */")
    lines.append("#100=CARTESIAN_POINT('sym_node',(5.0,5.0,7.07));")
    lines.append("/* Byte assertion: contains(b'(0.5,0.5,0.707)') */")
    lines.append("/* DEFECT: symmetry-plane normal is (0.5,0.5,0.707) — non-axis-aligned */")
    lines.append("/* A valid axis-aligned normal would be e.g. (1.0,0.0,0.0) for YZ plane */")
    lines.append("#101=DIRECTION('skew_sym_normal',(0.5,0.5,0.707));")
    lines.append("#102=AXIS2_PLACEMENT_3D('skew_sym_plane',#100,#101,$);")
    lines.append("#110=NODE('sym_boundary_node',(#100),$);")
    lines.append("/* Byte assertion: contains(b'SINGLE_POINT_CONSTRAINT') */")
    lines.append("/* DEFECT: constraint applied as U_x=0 using axis-aligned convention */")
    lines.append("/* For a skew normal (0.5,0.5,0.707) the correct constraint requires frame rotation */")
    lines.append("/* Encoding only DOF_1 (U_x=0.0) is incorrect — missing U_y and U_z contributions */")
    lines.append("#200=SINGLE_POINT_CONSTRAINT('skew_symmetry_bc','symmetry',")
    lines.append("  #110,#102,(1),(0.0,$,$,$,$,$));")
    lines.append("#300=NODE_GROUP('sym_nodes',(#110),$);")
    lines.append("#310=FEA_MODEL('skew_symmetry_model',$,'',(#300),(),());")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#500=GEOMETRIC_CURVE_SET('ap209-symmetry-plane-not-perpendicular-to-axis',")
    lines.append("  (#100,#101,#102,#110,#200,#310));")
    lines.append("/* Product chain */")
    lines.append("#600=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#601=PRODUCT_CONTEXT('',#600,'mechanical');")
    lines.append("#602=PRODUCT('M120','M120','M120',(#601));")
    lines.append("#603=PRODUCT_DEFINITION_FORMATION('','',#602);")
    lines.append("#604=PRODUCT_DEFINITION_CONTEXT(#600,'design');")
    lines.append("#605=PRODUCT_DEFINITION('','',#603,#604);")
    lines.append("#606=PRODUCT_DEFINITION_SHAPE('','',#605);")
    lines.append("#607=SHAPE_REPRESENTATION('',(#500),#14);")
    lines.append("#608=SHAPE_DEFINITION_REPRESENTATION(#606,#607);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m120(path) -> None:
    Path(path).write_text(_render_m120())


f.render = _render_m120  # type: ignore[method-assign]
f.write = _write_m120    # type: ignore[method-assign]
