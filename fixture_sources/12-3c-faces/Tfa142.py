"""Tfa142 — ShapeAnalysis_CheckSmallFace.CheckSmallArea torus-patch

Catalog claim: "Small face on TOROIDAL_SURFACE with major radius 5.0 and
minor radius 1.0. CheckSmallArea computes area via parametric (u,v)-domain
projection as planar polygon, ignoring torus surface curvature. Actual 3D
area differs significantly from projection; parametric bounds [0.0, 0.2] ×
[0.0, 0.3] yield false positives or negatives in small-area classification
depending on projection method. Defect exposes curvature-unawareness in area
approximation."

Demonstration: construct a small parametric face on a torus (major radius 5.0,
minor radius 1.0) with u-bounds [0.0, 0.2] and v-bounds [0.0, 0.3].
The parametric area is tiny, but the 3D area on the curved torus surface
is larger than a flat projection would suggest.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tfa142",
             defect="Small parametric face on torus with area-computation mismatch")

# Create a toroidal surface centered at origin
# Major radius 5.0, minor radius 1.0
ax_origin = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(ax_origin, zdir, xdir)
torus = f.toroidal_surface(plc, major_radius=5.0, minor_radius=1.0)

# Create a small rectangular wire on the torus surface.
# Parametric bounds: u in [0.0, 0.2], v in [0.0, 0.3]
# These are parametric (angle-like) coordinates on the torus.
# On the torus, these map to 3D points as follows:
# x = (major_r + minor_r * cos(v)) * cos(u)
# y = (major_r + minor_r * cos(v)) * sin(u)
# z = minor_r * sin(v)
# with u,v typically in [0, 2π].

# For the parametric bounds [0.0, 0.2] × [0.0, 0.3], approximate 3D corners:
# (u=0, v=0): (5+1, 0, 0) = (6, 0, 0)
# (u=0.2, v=0): (5+1)*cos(0.2), (5+1)*sin(0.2), 0) ≈ (5.88, 1.19, 0)
# (u=0.2, v=0.3): (5+cos(0.3))*cos(0.2), (5+cos(0.3))*sin(0.2), sin(0.3)) ≈ (5.84, 1.18, 0.296)
# (u=0, v=0.3): (5+cos(0.3), 0, sin(0.3)) ≈ (5.955, 0, 0.296)

import math

u_corners = [0.0, 0.2, 0.2, 0.0]
v_corners = [0.0, 0.0, 0.3, 0.3]
major_r = 5.0
minor_r = 1.0

pts = []
for u, v in zip(u_corners, v_corners):
    x = (major_r + minor_r * math.cos(v)) * math.cos(u)
    y = (major_r + minor_r * math.cos(v)) * math.sin(u)
    z = minor_r * math.sin(v)
    pts.append(f.cartesian_point((x, y, z)))

# Build the rectangular wire using closed_polyline_loop
loop = f.closed_polyline_loop(pts)

# Create the face on the torus surface
face = f.advanced_face([f.face_outer_bound(loop)], torus)

# Wrap in shell and surface model
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
