"""Pmi090 — Persistent UUID lost on round-trip (PMI association breaks).

Catalog claim: receivers regenerate UUIDs on import rather than honouring
the producer-emitted APPLIED_IDENTIFICATION_ASSIGNMENT('uuid', ..).

Previous fixture used empty-EDGE_LOOP placeholders. Regen: face +
SHAPE_ASPECT + APPLIED_IDENTIFICATION_ASSIGNMENT carrying a UUID.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Pmi090",
             defect="APPLIED_IDENTIFICATION_ASSIGNMENT('uuid', ..) on PMI feature")

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

# DIMENSIONAL_SIZE on a SHAPE_ASPECT for the feature.
shape_aspect = f._emit_raw(f"SHAPE_ASPECT('uuid_feature','',#9055,.T.)")
f._emit_raw(
    f"DIMENSIONAL_SIZE(#{shape_aspect.eid},'diameter','10.0 mm')"
)

# IDENTIFICATION_ROLE + APPLIED_IDENTIFICATION_ASSIGNMENT
# carrying a UUID — the persistent-id the receiver is supposed to honour.
ident_role = f._emit_raw(
    f"IDENTIFICATION_ROLE('uuid','persistent UUID')"
)
f._emit_raw(
    f"APPLIED_IDENTIFICATION_ASSIGNMENT("
    f"'550e8400-e29b-41d4-a716-446655440000',"
    f"#{ident_role.eid},(#{shape_aspect.eid}))"
)

# DATUM_FEATURE — required by byte assertion.
f._emit_raw(
    f"DATUM_FEATURE('df_uuid','datum feature for UUID test','',"
    f"#{shape_aspect.eid})"
)
