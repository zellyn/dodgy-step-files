"""N117 — ShapeAnalysis_Edge.CheckOverlapping mixed-curve-orientation

Overlapping edges where one is traversed forward and the other backward
(geometrically identical path); CheckOverlapping's directional test compares
tangent directions and reports no overlap when they differ, even though 3D
curves are coincident. Masks topology errors where duplicate geometry should
be detected.

Reproducer: two identical line segments (0,0,0) to (10,0,0), one with EDGE_CURVE
forward direction (+X), one backward (-X direction). Directional mismatch causes
the overlap check to return false negative.

Byte assertions:
  contains(b'v_start')
  contains(b'v_end')
  contains(b'edge_fwd')
  contains(b'edge_bwd')

Tier-3: n_faces_total == 1
Expected: occt=shape(1)/shape(1) gmsh=shape(5) ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N117",
    defect=(
        "OPEN_SHELL face with edge_fwd (v_start→v_end, +X direction) and edge_bwd "
        "(v_end→v_start, -X direction) sharing coincident geometry; CheckOverlapping "
        "tangent direction comparison returns false negative — overlap masked"
    ),
)

# Two coincident edges with opposite directions
p_start = f.cartesian_point((0.0, 0.0, 0.0))
p_end = f.cartesian_point((10.0, 0.0, 0.0))

v_start = f.vertex_point(p_start, name="v_start")
v_end = f.vertex_point(p_end, name="v_end")

# Forward line: origin, +X direction
d_fwd = f.direction((1.0, 0.0, 0.0))
vec_fwd = f.vector(d_fwd, 10.0)
l_fwd = f.line(p_start, vec_fwd)
e_fwd = f.edge_curve(v_start, v_end, l_fwd, name="edge_fwd")

# Backward line: from p_end, -X direction
d_bwd = f.direction((-1.0, 0.0, 0.0))
vec_bwd = f.vector(d_bwd, 10.0)
l_bwd = f.line(p_end, vec_bwd)
e_bwd = f.edge_curve(v_end, v_start, l_bwd, name="edge_bwd")

# Close with a rectangular face
p2 = f.cartesian_point((10.0, 5.0, 0.0))
p3 = f.cartesian_point((0.0, 5.0, 0.0))
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

e_up   = f.edge_curve(v_end, v2, f.line(p_end, f.vector(f.direction((0.0, 1.0, 0.0)), 5.0)))
e_back = f.edge_curve(v2, v3, f.line(p2, f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0)))
e_down = f.edge_curve(v3, v_start, f.line(p3, f.vector(f.direction((0.0, -1.0, 0.0)), 5.0)))

loop = f.edge_loop([
    f.oriented_edge(e_fwd, True),
    f.oriented_edge(e_up, True),
    f.oriented_edge(e_back, True),
    f.oriented_edge(e_down, True),
], name="bidirectional_loop")
fob = f.face_outer_bound(loop)

zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(p_start, zdir, xdir)
plane = f.plane(plc)
face = f.advanced_face([fob], plane)

shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(Path(__file__).parent.parent.parent / "step-examples" / "12-4-tolerance" / "N117.stp")
