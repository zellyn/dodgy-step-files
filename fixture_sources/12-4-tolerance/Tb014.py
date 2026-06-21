"""Tb014 — Sliver triangle whose smallest internal angle is at the hardcoded trigger.

Catalog claim: A planar triangular face has internal angles of 89.9999°,
89.9999°, and 0.0002°. The 0.0002° angle = 3.49e-6 rad. Many sliver
detectors trigger at "internal angle < 1e-5 rad"; some at "1e-7 rad"; some
at "1e-3 rad". The triangle is alive in one regime and dead in another.

Reproducer recipe: Triangle with vertices at (0,0,0), (1,0,0), (1, 3.49e-6, 0).
Angle at vertex (0,0,0) is 3.49e-6 rad. Wrap in PRODUCT chain.

Tier-3: face[0].area < 1e-3, n_edges_total >= 3, face[0].surface_type == "plane",
        n_vertices_total >= 6
Expected: occt=shape(1)/shape(1) gmsh=shape(7) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
import math

# Triangle vertices matching the catalog recipe
# v0 = (0,0,0), v1 = (1,0,0), v2 = (1, 3.49e-6, 0)
# Angle at v0: tan(angle) ≈ 3.49e-6/1 → angle ≈ 3.49e-6 rad = 0.0002°
TINY_Y = 3.49e-6

f = StepFile(
    catalog_id="Tb014",
    defect=(
        f"triangular ADVANCED_FACE with vertices (0,0,0),(1,0,0),(1,{TINY_Y},0); "
        f"angle at (0,0,0) ≈ 3.49e-6 rad = 0.0002°; "
        "sliver detector triggers at 1e-5 rad (triangle dead) or 1e-7 rad (alive); "
        "policy-dependent rejection; silent drop is unacceptable"
    ),
)

# Three vertices of the sliver triangle
p0 = f.cartesian_point((0.0, 0.0,    0.0), name="v0_sharp_angle")
p1 = f.cartesian_point((1.0, 0.0,    0.0), name="v1_base")
p2 = f.cartesian_point((1.0, TINY_Y, 0.0), name="v2_sliver_tip")

v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)

# Edge e01: v0 → v1 (along x-axis, length = 1.0)
d01 = f.direction((1.0, 0.0, 0.0))
l01 = f.line(p0, f.vector(d01, 1.0))
e01 = f.edge_curve(v0, v1, l01, name="e01_base")

# Edge e12: v1 → v2 (along y-axis, length = TINY_Y)
d12 = f.direction((0.0, 1.0, 0.0))
l12 = f.line(p1, f.vector(d12, TINY_Y))
e12 = f.edge_curve(v1, v2, l12, name="e12_sliver_side")

# Edge e20: v2 → v0 (hypotenuse, length ≈ 1.0)
dx = -1.0
dy = -TINY_Y
hyp = math.sqrt(dx**2 + dy**2)
d20 = f.direction((dx / hyp, dy / hyp, 0.0))
l20 = f.line(p2, f.vector(d20, hyp))
e20 = f.edge_curve(v2, v0, l20, name="e20_hypotenuse")

loop = f.edge_loop([
    f.oriented_edge(e01, True),
    f.oriented_edge(e12, True),
    f.oriented_edge(e20, True),
])

# Plane for the triangle (z=0, normal +z)
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
surf = f.plane(plc)

face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
