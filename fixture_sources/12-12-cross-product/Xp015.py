"""Xp015 — Self-intersecting wire on cylindrical (periodic) face × seam-edge missing."""
from step_corpus.step_builder import StepFile
import math

f = StepFile(catalog_id="Xp015",
             defect='Self-intersecting wire on cylindrical face x seam-edge missing x UV crossover')

# CYLINDRICAL_SURFACE: radius=1, axis=Z
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
cyl  = f.cylindrical_surface(plc, 1.0)

# Wire that self-intersects near the seam (u=0/2pi):
# 4 edges whose UV projections cross each other near u=2*pi.
# The seam edge is absent — no explicit edge at u=0 or u=2*pi.
# We map UV crossover to 3D: the wire wraps more than 2*pi.
import math as _math
R = 1.0

def pt_on_cyl(theta, z):
    """Point on cylinder of radius 1."""
    return f.cartesian_point((_math.cos(theta), _math.sin(theta), z))

# 4 points with theta crossing past 2*pi — self-intersecting in UV
t0 = 0.1;   t1 = _math.pi * 1.9;  t2 = _math.pi * 0.1;  t3 = _math.pi * 2.1
p0 = pt_on_cyl(t0, 0.0)
p1 = pt_on_cyl(t1, 0.0)
p2 = pt_on_cyl(t2, 0.5)
p3 = pt_on_cyl(t3, 0.5)

v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)

def line_edge(pa, pb, va, vb):
    dx = pb.args[1][0] - pa.args[1][0]
    dy = pb.args[1][1] - pa.args[1][1]
    dz = pb.args[1][2] - pa.args[1][2]
    length = max((dx**2 + dy**2 + dz**2) ** 0.5, 1e-15)
    d = f.direction((dx/length, dy/length, dz/length))
    vec = f.vector(d, length)
    ln = f.line(pa, vec)
    return f.edge_curve(va, vb, ln)

e0 = line_edge(p0, p1, v0, v1)  # crosses seam in UV
e1 = line_edge(p1, p2, v1, v2)
e2 = line_edge(p2, p3, v2, v3)  # self-intersection with e0 in UV
e3 = line_edge(p3, p0, v3, v0)

loop = f.edge_loop([
    f.oriented_edge(e0, True), f.oriented_edge(e1, True),
    f.oriented_edge(e2, True), f.oriented_edge(e3, True),
])
# No seam edge — the wire spans across u=2*pi without an explicit seam edge
face = f.advanced_face([f.face_outer_bound(loop)], cyl)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

f._emit_raw(
    "/* xp015 defect: wire self-intersects in UV near seam (u=2*pi); "
    "seam edge absent; pcurves absent */"
)
