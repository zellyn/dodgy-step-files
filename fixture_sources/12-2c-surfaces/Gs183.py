"""Gs183 — ShapeAnalysis_Surface.ComputeSingularities edge-proximity cache-invalidation.

Catalog claim: "CYLINDRICAL_SURFACE trimmed by RECTANGULAR_TRIMMED_SURFACE with
edge extremely close to (but not exactly at) the cylinder axis singularity
(v=0). ComputeSingularities cache remains valid even though edge proximity
triggers tolerance-dependent singularity detection."

Demonstration: A cylinder with its axis along Z is trimmed with bounds placing
one edge within a small distance (0.001 units) of the singularity at v=0 (the
axis). The singularity computation caches results without considering edge
proximity to cached singularity regions, causing closure checks to miss the
near-singular geometry.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gs183",
             defect="RECTANGULAR_TRIMMED_SURFACE on CYLINDRICAL_SURFACE near axis singularity; ComputeSingularities cache-invalidation omitted")

# -----------------------------------------------------------------------
# Base: CYLINDRICAL_SURFACE with axis along Z
# -----------------------------------------------------------------------
origin = f.cartesian_point((0.0, 0.0, 0.0))
z_dir = f.direction((0.0, 0.0, 1.0))
x_dir = f.direction((1.0, 0.0, 0.0))
axis2_placement = f.axis2_placement_3d(origin, z_dir, x_dir)

# Cylinder with radius 1.0, axis at origin
cylinder = f.cylindrical_surface(axis2_placement, radius=1.0)

# Trim very close to the singularity (v=0 is the axis)
# u ∈ [0, 2π], v ∈ [0.001, 1.0] — places lower edge near singularity
rts = f.rectangular_trimmed_surface(cylinder, 0.0, 6.283, 0.001, 1.0)

# Face boundary (approximating the cylindrical trim with 8 corner points)
theta_0 = 0.0
theta_1 = 1.5708
theta_2 = 3.1416
theta_3 = 4.7124

# Four corners of trim boundary
p0 = f.cartesian_point((1.0, 0.0, 0.001))       # (θ=0, v=0.001)
p1 = f.cartesian_point((0.0, 1.0, 0.001))       # (θ=π/2, v=0.001)
p2 = f.cartesian_point((-1.0, 0.0, 0.001))      # (θ=π, v=0.001)
p3 = f.cartesian_point((0.0, -1.0, 0.001))      # (θ=3π/2, v=0.001)
p4 = f.cartesian_point((1.0, 0.0, 1.0))         # (θ=0, v=1.0)
p5 = f.cartesian_point((0.0, 1.0, 1.0))         # (θ=π/2, v=1.0)
p6 = f.cartesian_point((-1.0, 0.0, 1.0))        # (θ=π, v=1.0)
p7 = f.cartesian_point((0.0, -1.0, 1.0))        # (θ=3π/2, v=1.0)

v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)
v4 = f.vertex_point(p4)
v5 = f.vertex_point(p5)
v6 = f.vertex_point(p6)
v7 = f.vertex_point(p7)

# Build edges for the rectangular trim boundary
# Lower edge (near singularity): p0→p1→p2→p3→p0 (circular arc at v=0.001)
d_lower_1 = f.direction((0.0, 1.0, 0.0))
line_lower_1 = f.line(p0, f.vector(d_lower_1, 1.0))
e_lower_1 = f.edge_curve(v0, v1, line_lower_1)

d_lower_2 = f.direction((-1.0, 0.0, 0.0))
line_lower_2 = f.line(p1, f.vector(d_lower_2, 1.0))
e_lower_2 = f.edge_curve(v1, v2, line_lower_2)

d_lower_3 = f.direction((0.0, -1.0, 0.0))
line_lower_3 = f.line(p2, f.vector(d_lower_3, 1.0))
e_lower_3 = f.edge_curve(v2, v3, line_lower_3)

d_lower_4 = f.direction((1.0, 0.0, 0.0))
line_lower_4 = f.line(p3, f.vector(d_lower_4, 1.0))
e_lower_4 = f.edge_curve(v3, v0, line_lower_4)

# Upper edge: p4→p5→p6→p7→p4 (circular arc at v=1.0)
d_upper_1 = f.direction((0.0, 1.0, 0.0))
line_upper_1 = f.line(p4, f.vector(d_upper_1, 1.0))
e_upper_1 = f.edge_curve(v4, v5, line_upper_1)

d_upper_2 = f.direction((-1.0, 0.0, 0.0))
line_upper_2 = f.line(p5, f.vector(d_upper_2, 1.0))
e_upper_2 = f.edge_curve(v5, v6, line_upper_2)

d_upper_3 = f.direction((0.0, -1.0, 0.0))
line_upper_3 = f.line(p6, f.vector(d_upper_3, 1.0))
e_upper_3 = f.edge_curve(v6, v7, line_upper_3)

d_upper_4 = f.direction((1.0, 0.0, 0.0))
line_upper_4 = f.line(p7, f.vector(d_upper_4, 1.0))
e_upper_4 = f.edge_curve(v7, v4, line_upper_4)

# Vertical edges: p0↔p4, p1↔p5, p2↔p6, p3↔p7
d_vert = f.direction((0.0, 0.0, 1.0))
line_vert_0 = f.line(p0, f.vector(d_vert, 0.999))
e_vert_0 = f.edge_curve(v0, v4, line_vert_0)

line_vert_1 = f.line(p1, f.vector(d_vert, 0.999))
e_vert_1 = f.edge_curve(v1, v5, line_vert_1)

line_vert_2 = f.line(p2, f.vector(d_vert, 0.999))
e_vert_2 = f.edge_curve(v2, v6, line_vert_2)

line_vert_3 = f.line(p3, f.vector(d_vert, 0.999))
e_vert_3 = f.edge_curve(v3, v7, line_vert_3)

# Lower loop
lower_loop = f.edge_loop([
    f.oriented_edge(e_lower_1, True),
    f.oriented_edge(e_lower_2, True),
    f.oriented_edge(e_lower_3, True),
    f.oriented_edge(e_lower_4, True)
])

# Upper loop
upper_loop = f.edge_loop([
    f.oriented_edge(e_upper_1, False),
    f.oriented_edge(e_vert_3, True),
    f.oriented_edge(e_upper_4, False),
    f.oriented_edge(e_vert_2, False)
])

# Face with one outer and one inner bound
fob_lower = f.face_outer_bound(lower_loop)
fib_upper = f.face_bound(upper_loop, orientation=False)
face = f.advanced_face([fob_lower, fib_upper], rts)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm, mode="surface_shape")
