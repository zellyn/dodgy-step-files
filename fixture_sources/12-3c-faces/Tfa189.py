"""Tfa189 — ShapeAnalysis_CheckSmallFace.CheckTwisted face-on-sphere-with-pole

Catalog claim: "CheckTwisted compares normals at face boundary points. On
sphere including both poles, normal singularities cause comparison to fail
(undefined direction)."

Demonstration: SPHERICAL_SURFACE (radius 5) with ADVANCED_FACE boundary loop
spanning south pole → equator → north pole → equator → south. Normal
vectors are undefined at poles.
"""
from step_corpus.step_builder import StepFile
import math

f = StepFile(catalog_id="Tfa189",
             defect="CheckTwisted on spherical face spanning both poles")

# Create sphere placement
ax_origin = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(ax_origin, zdir, xdir)
sphere = f.spherical_surface(plc, radius=5.0)

# Face boundary path on sphere that includes both poles:
# Start near south pole → equator → near north pole → equator → back to south
# Points in 3D on a radius-5 sphere

pts_boundary = [
    # Near south pole (0, 0, -5)
    f.cartesian_point((0.1, 0.0, -4.99)),
    # Move to equator, positive x
    f.cartesian_point((5.0, 0.0, 0.0)),
    # Near north pole (0, 0, 5)
    f.cartesian_point((0.1, 0.0, 4.99)),
    # Move back to equator, negative x
    f.cartesian_point((-5.0, 0.0, 0.0)),
]

loop = f.closed_polyline_loop(pts_boundary)
face = f.advanced_face([f.face_outer_bound(loop)], sphere)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
