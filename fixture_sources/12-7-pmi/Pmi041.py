"""Pmi041 — dimensional_size vs dimensional_location confusion.

Catalog claim: a hole-diameter PMI encoded as DIMENSIONAL_LOCATION
(curved-distance) instead of DIMENSIONAL_SIZE.

Previous fixture used empty-EDGE_LOOP placeholders. Regen: one face
representing a hole + a DIMENSIONAL_LOCATION entity with
name='curved_distance' applied to it.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Pmi041",
             defect="DIMENSIONAL_LOCATION used for hole-diameter (should be DIMENSIONAL_SIZE)")

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple); vec = f.vector(d, length); ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

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
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# SHAPE_ASPECT for the hole feature.
shape_aspect = f._emit_raw(
    f"SHAPE_ASPECT('hole_feature','',#9055,.T.)"
)
# DIMENSIONAL_LOCATION (curved_distance) — wrong type, should be DIMENSIONAL_SIZE.
f._emit_raw(
    f"DIMENSIONAL_LOCATION('curved_distance','wrong type for hole diameter',"
    f"#{shape_aspect.eid},#{shape_aspect.eid})"
)
