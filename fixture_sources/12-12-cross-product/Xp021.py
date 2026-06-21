"""Xp021 — Disconnected EDGE_LOOP × pcurve missing × wire bypassing seam."""
from step_corpus.step_builder import StepFile
import math as _math

f = StepFile(catalog_id="Xp021",
             defect='Disconnected EDGE_LOOP x pcurve missing x wire bypassing seam')

# Cylinder: radius=1, axis=Z
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
cyl  = f.cylindrical_surface(plc, 1.0)

def pt_on_cyl(theta, z):
    return f.cartesian_point((_math.cos(theta), _math.sin(theta), z))

# 3 edges with gaps (edge[1].end != edge[2].start)
# The wire also spans > 2*pi in U (wraps more than one period)
t0 = 0.0;   t1 = _math.pi;   t2 = t1 + 0.5  # GAP: start of edge2 is 0.5 away from end of edge1
t3 = 3.2 * _math.pi              # wire covers > 2*pi total U extent

p0 = pt_on_cyl(t0, 0.0)
p1 = pt_on_cyl(t1, 0.5)    # end of edge1
p2 = pt_on_cyl(t2, 0.5)    # start of edge2 — GAP of 0.5 in UV from p1
p3 = pt_on_cyl(t3, 1.0)

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

e0 = line_edge(p0, p1, v0, v1)
e1 = line_edge(p2, p3, v2, v3)  # gap: does not connect to e0.end (p1 != p2)
e2 = line_edge(p3, p0, v3, v0)  # wrap back to start

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
])
# No pcurves — pcurves absent from all EDGE_CURVEs
face = f.advanced_face([f.face_outer_bound(loop)], cyl)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

f._emit_raw(
    "/* xp021 defect: edge_loop disconnected (gap 0.5 in 3D); "
    "no pcurves; wire U-extent > 2*pi */"
)
