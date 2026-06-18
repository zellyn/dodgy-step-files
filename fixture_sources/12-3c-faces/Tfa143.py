"""Tfa143 — ShapeFix_Face.FixAddNaturalBound cone-with-apex-in-domain

Catalog claim: "CONICAL_SURFACE with apex at origin (0,0,0) and half-angle
0.52 radians. Face has single partial boundary wire at height z=5.0 spanning
v-direction (theta 0 to π/2), leaving uncovered parametric region.
FixAddNaturalBound attempts to add natural bounds via isNeedAddNaturalBound
predicate, but boundary construction includes apex-region edges where pcurve
is singular (radius=0). Apex makes pcurve-evaluation undefined; test triggers
FAN-001/FAN-003 path failures."

Demonstration: construct a cone with apex at origin and a circular wire at
height z=5.0, spanning only v in [0, π/2] (quarter circle). The wire doesn't
close the domain, and the cone's apex singularity at the base causes issues
when computing natural bounds.
"""
from step_corpus.step_builder import StepFile
import math

f = StepFile(catalog_id="Tfa143",
             defect="Cone with apex in parametric domain and partial boundary wire")

# Cone parameters
# apex at (0, 0, 0)
# half-angle: 0.52 radians (~30°)
# axis along +Z
# At height z, radius = z * tan(half-angle)
half_angle = 0.52
z_height = 5.0
radius_at_z = z_height * math.tan(half_angle)  # ~= 5.0 * 0.547 ~= 2.735

# Create conical surface
# CONICAL_SURFACE takes (name, placement, radius, semi_angle)
# The placement's origin should be at the apex.
ax_origin = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(ax_origin, zdir, xdir)
cone = f.conical_surface(plc, radius=0.0, semi_angle=half_angle)

# Create a quarter-circle wire on the cone at height z=5.0
# v-parameter ranges from 0 to π/2 (quarter circle around the axis)
# u-parameter is the height along the axis (but on a cone we use v for theta, u for z typically)
# Actually, on a cone, typically:
#   u = height (distance along axis from apex)
#   v = angular position (0 to 2π)
# We create points at quarter-circle (v: 0 to π/2) at fixed height (u ≈ distance from apex)

# At height z=5.0, we have 4 points: quarter-circle from v=0 to v=π/2
angles = [0.0, math.pi/6, math.pi/3, math.pi/2]
pts = []
for theta in angles:
    x = radius_at_z * math.cos(theta)
    y = radius_at_z * math.sin(theta)
    z = z_height
    pts.append(f.cartesian_point((x, y, z)))

# Build an open polyline (not closed, since it's only a quarter circle)
# We use the edge-building manually:
verts = [f.vertex_point(p) for p in pts]
oriented_edges = []
for i in range(len(pts) - 1):
    v1 = verts[i]
    v2 = verts[i + 1]
    p1 = pts[i]
    p2 = pts[i + 1]
    dx = p2.args[1][0] - p1.args[1][0]
    dy = p2.args[1][1] - p1.args[1][1]
    dz = p2.args[1][2] - p1.args[1][2]
    length = (dx**2 + dy**2 + dz**2) ** 0.5
    if length > 0:
        dir_ent = f.direction((dx/length, dy/length, dz/length))
        vec_ent = f.vector(dir_ent, length)
        line_ent = f.line(p1, vec_ent)
        edge_curve = f.edge_curve(v1, v2, line_ent)
        oriented_edges.append(f.oriented_edge(edge_curve))

loop = f.edge_loop(oriented_edges)

# Create the face on the cone surface
# The face is bounded by the partial wire (not closed, so only partially bounding)
face = f.advanced_face([f.face_outer_bound(loop)], cone)

# Wrap in shell and surface model
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
