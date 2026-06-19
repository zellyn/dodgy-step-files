"""A022 — PRESENTATION_LAYER_ASSIGNMENT collisions / namespace abuse.

Catalog claim: two PRESENTATION_LAYER_ASSIGNMENT instances with
identical names but different visibility flags collide. Or empty PLA.

Previous fixture used empty-EDGE_LOOP placeholders. Regen: 2 faces +
2 PRESENTATION_LAYER_ASSIGNMENTs with the same name 'Copper' but
different visibility flags ('meshable' vs 'invisible').
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A022",
             defect="2 PLA records with same name 'Copper' but different visibility")

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple); vec = f.vector(d, length); ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

# Build two faces.
faces = []
for k in range(2):
    x = k * 2.0
    p0 = f.cartesian_point((x, 0.0, 0.0))
    p1 = f.cartesian_point((x + 1.0, 0.0, 0.0))
    p2 = f.cartesian_point((x + 1.0, 1.0, 0.0))
    p3 = f.cartesian_point((x, 1.0, 0.0))
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
    faces.append(f.advanced_face([f.face_outer_bound(loop)], plane))

shell = f.open_shell(faces)
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# Two PRESENTATION_LAYER_ASSIGNMENT records with the IDENTICAL name
# 'Copper' but DIFFERENT visibility flags. This is the collision.
f._emit_raw(
    f"PRESENTATION_LAYER_ASSIGNMENT('Copper','meshable',(#{faces[0].eid}))"
)
f._emit_raw(
    f"PRESENTATION_LAYER_ASSIGNMENT('Copper','invisible',(#{faces[1].eid}))"
)
