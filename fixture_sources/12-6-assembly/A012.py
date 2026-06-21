"""A012 — Self-reference / cyclic external file reference.

Catalog claim: APPLIED_EXTERNAL_IDENTIFICATION_ASSIGNMENT whose target
path resolves to the main file itself (self_ref). Reader loops forever
on self-referential path. The bytes 'APPLIED_EXTERNAL_IDENTIFICATION_ASSIGNMENT'
and 'self_ref' must both be present.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A012",
             defect="APPLIED_EXTERNAL_IDENTIFICATION_ASSIGNMENT pointing at self_ref (cyclic external)")

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

# External file reference infrastructure.
ext_source = f._emit_raw(
    "EXTERNAL_SOURCE(IDENTIFICATION_ITEM('self_ref','A012.stp'))"
)
ext_id = f._emit_raw(
    f"EXTERNAL_IDENTIFICATION_ASSIGNMENT('self_ref','self-reference',#{ext_source.eid})"
)
# The self-referencing assignment — points at the SHAPE_DEFINITION_REPRESENTATION
# of the current file, which is entity #9004 (root product def).
f._emit_raw(
    f"APPLIED_EXTERNAL_IDENTIFICATION_ASSIGNMENT(#{ext_id.eid},(APPLIED_SHAPE_ASPECT_ROLE($)))"
)
