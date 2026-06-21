"""N070 — ShapeFix_ShapeTolerance.LimitTolerance zero lower-bound as no-op marker

LimitTolerance(shape, 0, 0.01) treats lower=0 as "skip lower check" AND skips
upper check entirely; shape with 0.5mm tolerance receives no enforcement of
0.01mm upper limit. Root cause: conditional uses single if(lower>0) gate for
entire tolerance-clamping logic.

Fixture: triangle face with 0.5mm tolerance; LimitTolerance(..., 0, 0.01)
leaves tolerance at 0.5mm instead of clamping to 0.01mm.

Byte assertions:
  count_entity_def(b'EDGE_CURVE') == 3
  count_entity_def(b'ADVANCED_FACE') == 1

Tier-3: n_faces_total == 1
Expected: occt=shape(1)/shape(1) gmsh=shape(7) ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N070",
    defect=(
        "CLOSED_SHELL triangle face with declared tolerance 0.5mm; "
        "LimitTolerance(shape, lower=0, upper=0.01) skips entire clamping "
        "logic due to if(lower>0) gate — 0.5mm tolerance unchanged"
    ),
)

# Simple triangle face with loose tolerance (0.5 mm, well above desired 0.01)
p0 = f.cartesian_point((0.0, 0.0, 0.0), name="p0")
p1 = f.cartesian_point((1.0, 0.0, 0.0), name="p1")
p2 = f.cartesian_point((0.5, 1.0, 0.0), name="p2")

v0 = f.vertex_point(p0, name="v0")
v1 = f.vertex_point(p1, name="v1")
v2 = f.vertex_point(p2, name="v2")

d0 = f.direction((1.0, 0.0, 0.0), name="d0")
vec0 = f.vector(d0, 1.0, name="vec0")
l0 = f.line(p0, vec0, name="line0")
e0 = f.edge_curve(v0, v1, l0, name="e0")

d1 = f.direction((-0.5, 1.0, 0.0), name="d1")
vec1 = f.vector(d1, 1.118, name="vec1")
l1 = f.line(p1, vec1, name="line1")
e1 = f.edge_curve(v1, v2, l1, name="e1")

d2 = f.direction((-0.5, -1.0, 0.0), name="d2")
vec2 = f.vector(d2, 1.118, name="vec2")
l2 = f.line(p2, vec2, name="line2")
e2 = f.edge_curve(v2, v0, l2, name="e2")

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
])
fob = f.face_outer_bound(loop)

d_z = f.direction((0.0, 0.0, 1.0), name="zdir")
d_x = f.direction((1.0, 0.0, 0.0), name="xdir")
plc = f.axis2_placement_3d(p0, d_z, d_x, name="ax3")
plane = f.plane(plc, name="plane")
face = f.advanced_face([fob], plane, name="face")
shell = f.closed_shell([face], name="shell")

# Units and loose tolerance (0.5 mm)
lu = f._emit_raw("(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.))")
pau = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
sau = f._emit_raw("(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT())")
unc = f._emit_raw(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(5.0E-1),#{lu.eid},'distance_accuracy_value','')")
_geom_ctx = f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_CONTEXT(3)"
    f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{unc.eid}))"
    f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{lu.eid},#{pau.eid},#{sau.eid}))"
    f"REPRESENTATION_CONTEXT('','3D'))"
)

sbsm = f.shell_based_surface_model([shell], name="sbsm")
f.add_product_chain(sbsm)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N070.stp")
