"""A034 — CheckSRRReversesNAUO segfault on SDR with SHAPE_ASPECT instead of PROPERTY_DEFINITION.

Catalog claim: SHAPE_DEFINITION_REPRESENTATION whose Definition slot is
a SHAPE_ASPECT instead of PROPERTY_DEFINITION_SHAPE. The exact byte pattern
'SHAPE_DEFINITION_REPRESENTATION(#90,' must appear at entity #90 = catia_aspect.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A034",
             defect="SHAPE_DEFINITION_REPRESENTATION(#90,...) where #90 is a SHAPE_ASPECT(catia_aspect)")

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
# Pad to ID 90 so the catia_aspect SHAPE_ASPECT lands at exactly #90.
# The geometry above used IDs 1-38 (next_id is 39 after sbsm).
# Emit CARTESIAN_POINT padding entities (IDs 39-89 = 51 pads).
while f._next_id < 90:
    f.cartesian_point((0.0, 0.0, 0.0))  # pad entity

# #90 = catia_aspect SHAPE_ASPECT (NOT PROPERTY_DEFINITION_SHAPE).
catia_aspect = f._emit_raw(
    "SHAPE_ASPECT('catia_aspect','CATIA SDR bypass',#9004,.T.)"
)

# Shape representation for the SDR.
shape_rep = f._emit_raw(f"SHAPE_REPRESENTATION('catia_rep',(#{plc.eid}),#9010)")

# The defect: SHAPE_DEFINITION_REPRESENTATION(#90, ...) where #90 is SHAPE_ASPECT.
f._emit_raw(
    f"SHAPE_DEFINITION_REPRESENTATION(#{catia_aspect.eid},#{shape_rep.eid})"
)

# Product chain goes to 9000+ — must come after catia_aspect to avoid conflicts.
f.add_product_chain(sbsm)
