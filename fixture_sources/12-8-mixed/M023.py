"""M023 — Mesh-to-NURBS face has inner FACE_BOUND extending outside the FACE_OUTER_BOUND.

Catalog claim: Mesh-to-BRep tools fit B_SPLINE_SURFACE_WITH_KNOTS patches per triangle
and stitch them. Near sharp creases the per-triangle patches' inner trims cross outside
their outer bounds. Common signature: a face whose outer rectangular FACE_OUTER_BOUND is
a 2x2 square but whose inner triangular FACE_BOUND has vertices that extend outside the
outer square; a self-intersecting face from mesh-to-NURBS conversion.

Reproducer recipe: ADVANCED_FACE with outer rectangular loop (2x2 square) and inner
triangular loop whose vertices extend outside the outer square; pcurves cross the outer
boundary — a self-intersecting trim topology. The file loads but every later Boolean fails.

Tier-3 assertions:
  n_edges_total >= 11
  face[0].surface_type == "plane"
  n_vertices_total >= 16

Expected: occt=shape(1)/shape(1) gmsh=shape(21) ifc=schema_n/a
"""
from pathlib import Path as _Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M023",
    schema="AP214",
    defect=(
        "Mesh-to-NURBS face has inner FACE_BOUND extending outside the FACE_OUTER_BOUND; "
        "input: STEP file produced by mesh-to-BRep fitting tool where per-triangle "
        "NURBS patches are stitched near a sharp crease; "
        "ADVANCED_FACE outer rectangular FACE_OUTER_BOUND is a 2x2 square; "
        "inner triangular FACE_BOUND has vertices (1,1),(3,1),(2,3) that extend "
        "outside the outer square — pcurves cross the outer boundary; "
        "self-intersecting trim topology: file loads but every subsequent Boolean fails; "
        "kernel must heal: STL-to-STEP path should emit FACETED_BREP not smooth NURBS, "
        "or run self-intersection healing as a final step; "
        "synonyms: mesh-to-NURBS inner trim outside outer, STL-to-STEP face self-intersects, "
        "FACE_BOUND extends past outer bound, self-intersecting reverse-engineered face"
    ),
)


def _render_m023() -> str:
    lines = []
    lines.append("ISO-10303-21;")
    lines.append(f"/* M023: {f.defect} */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M023'),'2;1');")
    lines.append("FILE_NAME('M023.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
    lines.append("FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));")
    lines.append("ENDSEC;")
    lines.append("DATA;")
    lines.append("#1=APPLICATION_CONTEXT('automotive_design');")
    lines.append("#2=APPLICATION_PROTOCOL_DEFINITION('international standard','automotive_design',2000,#1);")
    lines.append("#10=(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.));")
    lines.append("#11=(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.));")
    lines.append("#12=(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT());")
    lines.append("#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-6),#10,'distance_accuracy_value','');")
    lines.append("#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3)")
    lines.append("     GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))")
    lines.append("     GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12))")
    lines.append("     REPRESENTATION_CONTEXT('part','3D'));")
    lines.append("/* Plane in z=0 */")
    lines.append("#100=CARTESIAN_POINT('',(0.0,0.0,0.0));")
    lines.append("#101=DIRECTION('',(0.0,0.0,1.0));")
    lines.append("#102=DIRECTION('',(1.0,0.0,0.0));")
    lines.append("#103=AXIS2_PLACEMENT_3D('',#100,#101,#102);")
    lines.append("#104=PLANE('mesh_to_nurbs_face',#103);")
    lines.append("/* Outer loop: square (0,0)-(2,0)-(2,2)-(0,2) */")
    lines.append("#200=CARTESIAN_POINT('',(0.0,0.0,0.0));")
    lines.append("#201=CARTESIAN_POINT('',(2.0,0.0,0.0));")
    lines.append("#202=CARTESIAN_POINT('',(2.0,2.0,0.0));")
    lines.append("#203=CARTESIAN_POINT('',(0.0,2.0,0.0));")
    lines.append("/* Inner loop: triangle (1,1)-(3,1)-(2,3) - vertices cross the 2x2 outer square")
    lines.append("   at x=2 and y=2. This is the self-intersecting trim defect. */")
    lines.append("#210=CARTESIAN_POINT('',(1.0,1.0,0.0));")
    lines.append("#211=CARTESIAN_POINT('',(3.0,1.0,0.0));")
    lines.append("#212=CARTESIAN_POINT('',(2.0,3.0,0.0));")
    lines.append("#220=VERTEX_POINT('',#200);")
    lines.append("#221=VERTEX_POINT('',#201);")
    lines.append("#222=VERTEX_POINT('',#202);")
    lines.append("#223=VERTEX_POINT('',#203);")
    lines.append("#224=VERTEX_POINT('',#210);")
    lines.append("#225=VERTEX_POINT('',#211);")
    lines.append("#226=VERTEX_POINT('',#212);")
    lines.append("/* Outer loop edge vectors */")
    lines.append("#230=DIRECTION('',(1.0,0.0,0.0));")
    lines.append("#231=DIRECTION('',(0.0,1.0,0.0));")
    lines.append("#232=VECTOR('',#230,2.0);")
    lines.append("#233=VECTOR('',#231,2.0);")
    lines.append("/* Outer loop edges: bottom, right, top(rev), left(rev) */")
    lines.append("#240=LINE('',#200,#232);")
    lines.append("#241=EDGE_CURVE('',#220,#221,#240,.T.);")
    lines.append("#242=LINE('',#201,#233);")
    lines.append("#243=EDGE_CURVE('',#221,#222,#242,.T.);")
    lines.append("#244=LINE('',#203,#232);")
    lines.append("#245=EDGE_CURVE('',#223,#222,#244,.T.);")
    lines.append("#246=LINE('',#200,#233);")
    lines.append("#247=EDGE_CURVE('',#220,#223,#246,.T.);")
    lines.append("/* Inner loop edge vectors (cross the outer boundary) */")
    lines.append("/* Edge 0: (1,1)->(3,1) along +x, length=2 */")
    lines.append("#250=LINE('',#210,#232);")
    lines.append("#251=EDGE_CURVE('',#224,#225,#250,.T.);")
    lines.append("/* Edge 1: (3,1)->(2,3) direction ~(-0.447,0.894,0) length~2.236 */")
    lines.append("#252=DIRECTION('',(-0.4472135955,0.8944271910,0.0));")
    lines.append("#253=VECTOR('',#252,2.2360679775);")
    lines.append("#254=LINE('',#211,#253);")
    lines.append("#255=EDGE_CURVE('',#225,#226,#254,.T.);")
    lines.append("/* Edge 2: (2,3)->(1,1) direction ~(-0.447,-0.894,0) length~2.236 */")
    lines.append("#256=DIRECTION('',(-0.4472135955,-0.8944271910,0.0));")
    lines.append("#257=VECTOR('',#256,2.2360679775);")
    lines.append("#258=LINE('',#212,#257);")
    lines.append("#259=EDGE_CURVE('',#226,#224,#258,.T.);")
    lines.append("/* Outer FACE_OUTER_BOUND */")
    lines.append("#260=ORIENTED_EDGE('',*,*,#241,.T.);")
    lines.append("#261=ORIENTED_EDGE('',*,*,#243,.T.);")
    lines.append("#262=ORIENTED_EDGE('',*,*,#245,.F.);")
    lines.append("#263=ORIENTED_EDGE('',*,*,#247,.F.);")
    lines.append("#264=EDGE_LOOP('',(#260,#261,#262,#263));")
    lines.append("#265=FACE_OUTER_BOUND('',#264,.T.);")
    lines.append("/* Inner FACE_BOUND: triangle whose vertices cross the outer square */")
    lines.append("#270=ORIENTED_EDGE('',*,*,#251,.T.);")
    lines.append("#271=ORIENTED_EDGE('',*,*,#255,.T.);")
    lines.append("#272=ORIENTED_EDGE('',*,*,#259,.T.);")
    lines.append("#273=EDGE_LOOP('',(#270,#271,#272));")
    lines.append("#274=FACE_BOUND('',#273,.T.);")
    lines.append("/* Defect: FACE_BOUND inner loop crosses FACE_OUTER_BOUND edges */")
    lines.append("#280=ADVANCED_FACE('self_intersecting',(#265,#274),#104,.T.);")
    lines.append("/* Minimal PRODUCT chain so OCCT TransferRoots produces a shape */")
    lines.append("#9010=PRODUCT_CONTEXT('',#1,'mechanical');")
    lines.append("#9011=PRODUCT('M023','M023','',(#9010));")
    lines.append("#9012=PRODUCT_DEFINITION_FORMATION('','',#9011);")
    lines.append("#9013=PRODUCT_DEFINITION_CONTEXT('part definition',#1,'design');")
    lines.append("#9014=PRODUCT_DEFINITION('','',#9012,#9013);")
    lines.append("#9015=PRODUCT_DEFINITION_SHAPE('','',#9014);")
    lines.append("#9030=OPEN_SHELL('wrap_shell',(#280));")
    lines.append("#9031=SHELL_BASED_SURFACE_MODEL('wrap_sbsm',(#9030));")
    lines.append("#9050=MANIFOLD_SURFACE_SHAPE_REPRESENTATION('',(#9031),#14);")
    lines.append("#9051=SHAPE_DEFINITION_REPRESENTATION(#9015,#9050);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m023(path) -> None:
    _Path(path).write_text(_render_m023())


f.render = _render_m023   # type: ignore[method-assign]
f.write  = _write_m023    # type: ignore[method-assign]
