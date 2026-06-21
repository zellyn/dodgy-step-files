"""N123 — BRepLib.UpdateEdgeTol with-edge-on-degenerate-surface

Edge on conical surface at apex (parametric u=0, degenerate parametric domain).
Sampling edge at parametric intervals produces zero-length derivatives on
degenerate patch; division-by-zero or normalization singularity.

Reproducer: cone apex at (0,0,10), three base edges radiating to (5,0,0),
(0,5,0), (-5,0,0). UpdateEdgeTol samples edges near apex where surface
derivatives vanish, triggering normalization singularity.

Byte assertions:
  contains(b'v_apex')
  contains(b'e_ab1')
  contains(b'apex')

Tier-3: load == "ok"
Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N123",
    defect=(
        "OPEN_SHELL with face from v_apex at (0,0,10) radiating via e_ab1, e_ab2, "
        "e_ab3 to base ring; UpdateEdgeTol samples edges near cone apex where "
        "parametric derivatives vanish — division-by-zero normalization singularity"
    ),
)

# Cone apex and base points
p_apex = f.cartesian_point((0.0, 0.0, 10.0))
p_b1 = f.cartesian_point((5.0, 0.0, 0.0))
p_b2 = f.cartesian_point((0.0, 5.0, 0.0))
p_b3 = f.cartesian_point((-5.0, 0.0, 0.0))

v_apex = f.vertex_point(p_apex, name="v_apex")
v_b1 = f.vertex_point(p_b1, name="v_b1")
v_b2 = f.vertex_point(p_b2, name="v_b2")
v_b3 = f.vertex_point(p_b3, name="v_b3")

# Lines from apex to each base vertex
d_ab1 = f.direction((5.0, 0.0, -10.0))
d_ab2 = f.direction((0.0, 5.0, -10.0))
d_ab3 = f.direction((-5.0, 0.0, -10.0))
vec_ab1 = f.vector(d_ab1, 1.0)
vec_ab2 = f.vector(d_ab2, 1.0)
vec_ab3 = f.vector(d_ab3, 1.0)

l_ab1 = f.line(p_apex, vec_ab1)
l_ab2 = f.line(p_apex, vec_ab2)
l_ab3 = f.line(p_apex, vec_ab3)

e_ab1 = f.edge_curve(v_apex, v_b1, l_ab1, name="e_ab1")
e_ab2 = f.edge_curve(v_apex, v_b2, l_ab2, name="e_ab2")
e_ab3 = f.edge_curve(v_apex, v_b3, l_ab3, name="e_ab3")

# Base ring segment: b1 → b2 → b3 → (close back to b1 via b3)
d_b12 = f.direction((-1.0, 1.0, 0.0))
d_b23 = f.direction((-1.0, -1.0, 0.0))
d_b31 = f.direction((1.0, 0.0, 0.0))
e_b12 = f.edge_curve(v_b1, v_b2, f.line(p_b1, f.vector(d_b12, 5.0)))
e_b23 = f.edge_curve(v_b2, v_b3, f.line(p_b2, f.vector(d_b23, 5.0)))
e_b31 = f.edge_curve(v_b3, v_b1, f.line(p_b3, f.vector(d_b31, 5.0)))

# Main face: apex → b1 → b2 → apex (triangle slice)
loop = f.edge_loop([
    f.oriented_edge(e_ab1, True),
    f.oriented_edge(e_b12, True),
    f.oriented_edge(e_ab2, False),
])
fob = f.face_outer_bound(loop)

# Plane approximation for the face surface
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(p_apex, zdir, xdir)
plane = f.plane(plc)
face = f.advanced_face([fob], plane)

shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N123.stp")
