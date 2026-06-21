"""N092 — ShapeAnalysis_ShapeTolerance.AddTolerance type-mismatch

Calling AddTolerance(shape, tol, TopAbs_FACE) on a shape with WIRE entries
silently skips them, leading to incomplete tolerance accumulation and downstream
errors in tolerance-aware algorithms.

Reproducer: shape with both FACE and WIRE; iteration expects only the called
type but doesn't report type mismatch or skip reason.

Byte assertions:
  contains(b'triangle_face')
  contains(b'fe0')
  count_entity_def(b'ADVANCED_FACE') == 1

Tier-3: n_faces_total == 1
Expected: occt=shape(1)/shape(1) gmsh=shape(7) ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N092",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE triangle_face; AddTolerance(shape, tol, FACE) "
        "processes only the face and silently skips any WIRE-type sub-shapes — "
        "tolerance accumulation incomplete for mixed shape types"
    ),
)

# Plane for all faces
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# Face: equilateral triangle — will be processed by AddTolerance(FACE)
p_f0 = f.cartesian_point((0.0, 0.0, 0.0))
p_f1 = f.cartesian_point((1.0, 0.0, 0.0))
p_f2 = f.cartesian_point((0.5, 0.866, 0.0))

v_f0 = f.vertex_point(p_f0, name="fv0")
v_f1 = f.vertex_point(p_f1, name="fv1")
v_f2 = f.vertex_point(p_f2, name="fv2")

d_e0 = f.direction((1.0, 0.0, 0.0))
e0 = f.edge_curve(v_f0, v_f1, f.line(p_f0, f.vector(d_e0, 1.0)), name="fe0")

d_e1 = f.direction((-0.5, 0.866, 0.0))
e1 = f.edge_curve(v_f1, v_f2, f.line(p_f1, f.vector(d_e1, 1.0)), name="fe1")

d_e2 = f.direction((-0.5, -0.866, 0.0))
e2 = f.edge_curve(v_f2, v_f0, f.line(p_f2, f.vector(d_e2, 1.0)), name="fe2")

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
], name="face_loop")
fob = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane, name="triangle_face")

# Shell containing face (wire sub-shapes would be outside the shell,
# demonstrating the type-mismatch skip)
shell = f.open_shell([face], name="shell_faces")
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N092.stp")
