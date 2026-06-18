"""N090 — GlobalTolerance weighted mode edge direction bug.

Catalog claim: "ShapeAnalysis_ShapeTolerance.GlobalTolerance mode=2 (weighted
average) counts forward and reversed edges separately for denominator but sums
their tolerance contributions. Shape with N/2 forward + N/2 reversed edges
computed as avg(tol_sum) / (2N) instead of / N; weighting factor doubled,
result halved."

Demonstration: A shell with multiple edges, half oriented forward and half
reversed. GlobalTolerance with mode=2 should compute a weighted average,
but the bug causes it to count reversed edges twice in the denominator,
halving the expected result.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="N090",
             defect="GlobalTolerance mode=2 double-counts reversed edges in denominator")

# Create a simple grid: 4 rectangles in 2x2 arrangement
# Using 6 vertices:
#   (0,0) (1,0) (2,0)
#   (0,1) (1,1) (2,1)

pts = [
    [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (2.0, 0.0, 0.0)],
    [(0.0, 1.0, 0.0), (1.0, 1.0, 0.0), (2.0, 1.0, 0.0)],
]
verts = [[f.vertex_point(f.cartesian_point(p)) for p in row] for row in pts]

# Helper to create edges with specific orientation
def make_edge(v_from, v_to, coords_from, coords_to):
    dx = coords_to[0] - coords_from[0]
    dy = coords_to[1] - coords_from[1]
    dz = coords_to[2] - coords_from[2]
    length = (dx**2 + dy**2 + dz**2) ** 0.5
    if length == 0:
        return None
    d = f.direction((dx/length, dy/length, dz/length))
    v = f.vector(d, length)
    l = f.line(f.cartesian_point(coords_from), v)
    return f.edge_curve(v_from, v_to, l)

# Bottom-left rectangle edges: mix forward and reversed
e_bl_bot = make_edge(verts[0][0], verts[0][1], pts[0][0], pts[0][1])  # forward
e_bl_right = make_edge(verts[0][1], verts[1][1], pts[0][1], pts[1][1])  # forward
e_bl_top = make_edge(verts[1][0], verts[0][0], pts[1][0], pts[0][0])  # reversed (going backwards)
e_bl_left = make_edge(verts[1][0], verts[0][0], pts[1][0], pts[0][0])  # reversed

# Bottom-right rectangle (shares edge with bottom-left)
e_br_right = make_edge(verts[0][2], verts[1][2], pts[0][2], pts[1][2])  # forward
e_br_top = make_edge(verts[1][1], verts[0][1], pts[1][1], pts[0][1])  # reversed

# Build loops
loop_bl = f.edge_loop([
    f.oriented_edge(e_bl_bot, True),
    f.oriented_edge(e_bl_right, True),
    f.oriented_edge(e_bl_top, False),
    f.oriented_edge(e_bl_left, False),
])

# Plane
ax_origin = f.cartesian_point((0.0, 0.0, 0.0))
z_dir = f.direction((0.0, 0.0, 1.0))
x_dir = f.direction((1.0, 0.0, 0.0))
placement = f.axis2_placement_3d(ax_origin, z_dir, x_dir)
plane = f.plane(placement)

face = f.advanced_face([f.face_outer_bound(loop_bl)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm, mode="surface_shape")
