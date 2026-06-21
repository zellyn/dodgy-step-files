"""Xp017 — Empty geometric-set × extreme coordinates × NaN component."""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Xp017",
             defect='Empty geometric-set x extreme coordinates (1e308) x NaN component')

# Minimal geometry for tier-3 load == "ok" assertion
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

def line_edge(pa, pb, va, vb):
    dx = pb.args[1][0] - pa.args[1][0]
    dy = pb.args[1][1] - pa.args[1][1]
    dz = pb.args[1][2] - pa.args[1][2]
    length = (dx**2 + dy**2 + dz**2) ** 0.5
    d = f.direction((dx/length, dy/length, dz/length))
    vec = f.vector(d, length)
    ln = f.line(pa, vec)
    return f.edge_curve(va, vb, ln)

p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))
v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)
e0 = line_edge(p0, p1, v0, v1)
e1 = line_edge(p1, p2, v1, v2)
e2 = line_edge(p2, p3, v2, v3)
e3 = line_edge(p3, p0, v3, v0)
loop = f.edge_loop([
    f.oriented_edge(e0, True), f.oriented_edge(e1, True),
    f.oriented_edge(e2, True), f.oriented_edge(e3, True),
])
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# Defect 1: empty GEOMETRIC_SET
f._emit_raw("GEOMETRIC_SET('xp017_empty',())")

# Defect 2: extreme coordinate — 1e308 (near float max)
f._emit_raw("CARTESIAN_POINT('xp017_extreme',(1.0E308,0.,0.))")

# Defect 3: NaN coordinate — textual NaN literal, non-conforming for ISO-10303-21 REAL
f._emit_raw("CARTESIAN_POINT('xp017_nan',(NaN,0.,0.))")
