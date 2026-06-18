"""N089 — LimitTolerance recursion stops at WIRE.

Catalog claim: "ShapeFix_ShapeTolerance.LimitTolerance with mode=TopAbs_VERTEX
recursively applies limits to faces and wires but fails to descend into wire's
edge collection or edge's vertex endpoints. Shell with deeply nested geometry
(Face→Wire→Edge→Vertex) applies tolerance only to Face/Wire level; innermost
vertices unconstrained."

Demonstration: A face with a wire loop containing edges with vertices.
Set tolerance limits on the shell level, expecting LimitTolerance to recursively
constrain all vertices, but the implementation stops at the Wire level and
doesn't descend into edge endpoints.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="N089",
             defect="LimitTolerance recursion fails to descend into edge vertices")

# Simple rectangular face loop
p1 = f.cartesian_point((0.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 0.0, 0.0))
p3 = f.cartesian_point((1.0, 1.0, 0.0))
p4 = f.cartesian_point((0.0, 1.0, 0.0))

v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)
v4 = f.vertex_point(p4)

# Four edges forming the loop
d_x = f.direction((1.0, 0.0, 0.0))
d_y = f.direction((0.0, 1.0, 0.0))
d_nx = f.direction((-1.0, 0.0, 0.0))
d_ny = f.direction((0.0, -1.0, 0.0))

vec_1 = f.vector(d_x, 1.0)
vec_2 = f.vector(d_y, 1.0)
vec_3 = f.vector(d_nx, 1.0)
vec_4 = f.vector(d_ny, 1.0)

line1 = f.line(p1, vec_1)
line2 = f.line(p2, vec_2)
line3 = f.line(p3, vec_3)
line4 = f.line(p4, vec_4)

e1 = f.edge_curve(v1, v2, line1)
e2 = f.edge_curve(v2, v3, line2)
e3 = f.edge_curve(v3, v4, line3)
e4 = f.edge_curve(v4, v1, line4)

# Loop with edge collection
loop = f.edge_loop([
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
    f.oriented_edge(e4, True),
])

# Plane
ax_origin = f.cartesian_point((0.0, 0.0, 0.0))
z_dir = f.direction((0.0, 0.0, 1.0))
x_dir = f.direction((1.0, 0.0, 0.0))
placement = f.axis2_placement_3d(ax_origin, z_dir, x_dir)
plane = f.plane(placement)

face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm, mode="surface_shape")
