"""Gs181 — ShapeConstruct_Surface.ConvertCurveToSurface invalid-basis bypass.

Catalog claim: "PLANE-based RECTANGULAR_TRIMMED_SURFACE with inverted axis
orientation. ConvertCurveToSurface fails to validate basis surface axis
consistency before curve-lifting, causing parameter mismatch."

Demonstration: A PLANE with a reversed Z-axis (negative scale) is trimmed as
the basis for a rectangular surface. When conversion from 2D edge curve to 3D
surface curve is attempted, the inverted basis axis bypasses the axis-direction
guard, leading to incorrect surface parameter inference.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gs181",
             defect="RECTANGULAR_TRIMMED_SURFACE with inverted plane basis; ConvertCurveToSurface skips axis validation")

# -----------------------------------------------------------------------
# Base: PLANE with inverted Z-axis (negative axis direction)
# -----------------------------------------------------------------------
origin = f.cartesian_point((0.0, 0.0, 0.0))
x_dir = f.direction((1.0, 0.0, 0.0))
z_dir = f.direction((0.0, 0.0, -1.0))  # Inverted (negative Z)
axis2_placement = f.axis2_placement_3d(origin, z_dir, x_dir)

# Create a plane with inverted normal
plane = f.plane(axis2_placement)

# Trim the inverted plane
rts = f.rectangular_trimmed_surface(plane, -1.0, 1.0, -1.0, 1.0)

# Face boundary (still in XY plane despite inverted normal)
p0 = f.cartesian_point((-1.0, -1.0, 0.0))
p1 = f.cartesian_point((1.0, -1.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((-1.0, 1.0, 0.0))

v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

d_x = f.direction((1.0, 0.0, 0.0))
d_y = f.direction((0.0, 1.0, 0.0))

line1 = f.line(p0, f.vector(d_x, 2.0))
line2 = f.line(p1, f.vector(d_y, 2.0))
line3 = f.line(p2, f.vector(d_x, -2.0))
line4 = f.line(p3, f.vector(d_y, -2.0))

e1 = f.edge_curve(v0, v1, line1)
e2 = f.edge_curve(v1, v2, line2)
e3 = f.edge_curve(v2, v3, line3)
e4 = f.edge_curve(v3, v0, line4)

loop = f.edge_loop([
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
    f.oriented_edge(e4, True)
])
fob = f.face_outer_bound(loop)
face = f.advanced_face([fob], rts)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm, mode="surface_shape")
