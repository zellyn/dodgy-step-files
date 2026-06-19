"""M190 — Compound with free VERTEX ignored on STEP export.

Catalog claim: a compound shape containing a free vertex (a VERTEX_POINT
not part of any edge, wire, face, or solid) is silently dropped during
STEP export. The compound on round-trip has one fewer sub-shape than the
in-memory original.

Source: pattern-matched from OCCT bugs/step/bug33053, which exercises
WriteStep on a compound where a free vertex is dropped. We synthesize
the *intended* fixture: a compound carrying both a solid face and a
free vertex, claiming the latter is canonically representable but
producer-dependent in survival.

LGPL-clean: pattern-matched, no bytes copied from OCCT's test data.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="M190",
             defect="compound with free VERTEX_POINT not in any face/edge/shell")

# Build a small face (so the compound has a solid sub-shape).
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))
v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple)
    vec = f.vector(d, length)
    ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

e0 = line_edge(p0, (1.0, 0.0, 0.0), 1.0, v0, v1)
e1 = line_edge(p1, (0.0, 1.0, 0.0), 1.0, v1, v2)
e2 = line_edge(p2, (-1.0, 0.0, 0.0), 1.0, v2, v3)
e3 = line_edge(p3, (0.0, -1.0, 0.0), 1.0, v3, v0)

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)
loop = f.edge_loop([
    f.oriented_edge(e0, True), f.oriented_edge(e1, True),
    f.oriented_edge(e2, True), f.oriented_edge(e3, True),
])
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])

# Free vertex at (5, 5, 5) — not part of any edge/face/shell above.
# The defect: many STEP writers omit free vertices from the compound's
# items list, so the round-trip loses this entity.
free_pt = f.cartesian_point((5.0, 5.0, 5.0))
free_vertex = f.vertex_point(free_pt)

# Geometric compound (GEOMETRIC_REPRESENTATION_ITEM list) carrying both.
# Most viewers and consumers preserve the SBSM but drop the loose vertex.
sbsm = f.shell_based_surface_model([shell])
f._emit_raw(
    f"GEOMETRIC_SET('compound_with_free_vertex',"
    f"(#{sbsm.eid},#{free_vertex.eid}))"
)
f.add_product_chain(sbsm)
