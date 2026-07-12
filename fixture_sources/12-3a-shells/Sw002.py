"""Sw002 — Sliver face silently dropped by sewing.

Catalog claim: A face whose area is below the squared sewing tolerance is
removed entirely by the sewer with no diagnostic. Reproducer recipe (per
catalog): an ADVANCED_FACE whose underlying PLANE references
CARTESIAN_POINTs covering only a sub-micron sliver region (e.g.,
(0,0,0), (1e-6,0,0), (1e-6,1e-6,0), (0,1e-6,0)) -- a face whose extent is
below typical tolerance.

Previously this fixture built a full 1x1 unit square (NOT a sliver) --
byte-verified rejection from the OCCT exchange-layer coverage audit
(occt-coverage/exchange/, sew-tiny-edge-face-culling). Fixed here to use
the exact sub-micron sliver footprint the catalog's own reproducer
recipe specifies, so the face genuinely sits below sewing-tolerance
squared area.

Byte assertion: count_entity_def(b'ADVANCED_FACE') == 1
Byte assertion: contains(b'sliver')
Tier-3: n_faces_total == 1, n_edges_total == 4, n_vertices_total == 8
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Sw002", defect="sub-micron sliver face for sewing-loss")

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple); vec = f.vector(d, length); ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

# Sub-micron sliver: 1e-6 x 1e-6 square -- exactly the catalog's own
# reproducer-recipe example coordinates.
S = 1.0e-6
p0 = f.cartesian_point((0.0, 0.0, 0.0)); p1 = f.cartesian_point((S, 0.0, 0.0))
p2 = f.cartesian_point((S, S, 0.0)); p3 = f.cartesian_point((0.0, S, 0.0))
v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)
e0 = line_edge(p0, (1.0, 0.0, 0.0), S, v0, v1)
e1 = line_edge(p1, (0.0, 1.0, 0.0), S, v1, v2)
e2 = line_edge(p2, (-1.0, 0.0, 0.0), S, v2, v3)
e3 = line_edge(p3, (0.0, -1.0, 0.0), S, v3, v0)
loop = f.edge_loop([f.oriented_edge(e0, True), f.oriented_edge(e1, True),
                   f.oriented_edge(e2, True), f.oriented_edge(e3, True)])
face = f.advanced_face([f.face_outer_bound(loop)], plane)

all_faces = [face]

shell = f.open_shell(all_faces)
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

