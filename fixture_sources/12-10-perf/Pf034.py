"""Pf034 — Shape-divide pass raises end-of-iteration on large shape.

Catalog claim: compound of ~200 cubes (~1,200 faces). Shape-divide hits
an internal hard-coded collection limit and raises NoMoreObject.

Previous fixture used 30 empty-EDGE_LOOP placeholders. Regen: 50 real
single-face MANIFOLD_SOLID_BREPs in a compound. Each is a minimal cube
face. Scaled-down from production 200 cubes but representative of the
many-solid pattern.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Pf034",
             defect="50-cube compound exercising shape-divide collection limit")

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

NUM_BREPS = 50

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple); vec = f.vector(d, length); ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

# First MSSR via add_product_chain — provides root product context.
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))
v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)
e0 = line_edge(p0, (1.0, 0.0, 0.0), 1.0, v0, v1)
e1 = line_edge(p1, (0.0, 1.0, 0.0), 1.0, v1, v2)
e2 = line_edge(p2, (-1.0, 0.0, 0.0), 1.0, v2, v3)
e3 = line_edge(p3, (0.0, -1.0, 0.0), 1.0, v3, v0)
loop = f.edge_loop([
    f.oriented_edge(e0, True), f.oriented_edge(e1, True),
    f.oriented_edge(e2, True), f.oriented_edge(e3, True),
])
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell0 = f.open_shell([face])
sbsm0 = f.shell_based_surface_model([shell0])
f.add_product_chain(sbsm0)

# Now emit NUM_BREPS additional MANIFOLD_SOLID_BREPs to exercise the
# shape-divide collection limit. Each brep wraps a single CLOSED_SHELL
# containing one ADVANCED_FACE (with proper geometry).
for k in range(NUM_BREPS):
    x = (k % 10) * 2.0
    y = (k // 10) * 2.0
    z = 0.0

    pk0 = f.cartesian_point((x, y, z))
    pk1 = f.cartesian_point((x + 1.0, y, z))
    pk2 = f.cartesian_point((x + 1.0, y + 1.0, z))
    pk3 = f.cartesian_point((x, y + 1.0, z))
    vk0 = f.vertex_point(pk0); vk1 = f.vertex_point(pk1)
    vk2 = f.vertex_point(pk2); vk3 = f.vertex_point(pk3)
    ek0 = line_edge(pk0, (1.0, 0.0, 0.0), 1.0, vk0, vk1)
    ek1 = line_edge(pk1, (0.0, 1.0, 0.0), 1.0, vk1, vk2)
    ek2 = line_edge(pk2, (-1.0, 0.0, 0.0), 1.0, vk2, vk3)
    ek3 = line_edge(pk3, (0.0, -1.0, 0.0), 1.0, vk3, vk0)
    loopk = f.edge_loop([
        f.oriented_edge(ek0, True), f.oriented_edge(ek1, True),
        f.oriented_edge(ek2, True), f.oriented_edge(ek3, True),
    ])
    facek = f.advanced_face([f.face_outer_bound(loopk)], plane)
    shellk = f._emit_raw(f"CLOSED_SHELL('cube_{k}',(#{facek.eid}))")
    f._emit_raw(f"MANIFOLD_SOLID_BREP('cube_brep_{k}',#{shellk.eid})")
