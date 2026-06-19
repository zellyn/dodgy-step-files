"""Pmi061 — DATUM → ADVANCED_FACE chain not resolved for some link patterns.

Catalog claim: NIST PMI test cases ctc_01.stc_10 — DATUM →
ADVANCED_FACE chain not resolved.

Previous fixture used empty-EDGE_LOOP placeholders. Regen: one face +
DATUM chain that links to the face indirectly via SHAPE_ASPECT.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Pmi061",
             defect="DATUM → SHAPE_ASPECT → ADVANCED_FACE indirect chain")

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

# Indirect DATUM chain.
shape_aspect = f._emit_raw(
    f"SHAPE_ASPECT('datum_aspect','indirect link to face',#9005,.T.)"
)
f._emit_raw(
    f"DATUM_FEATURE('df_indirect','indirect via SHAPE_ASPECT','',#{shape_aspect.eid})"
)
f._emit_raw(
    f"DATUM('A','primary datum','',#{shape_aspect.eid},'A')"
)
# GEOMETRIC_ITEM_SPECIFIC_USAGE pointing the shape_aspect at the face.
f._emit_raw(
    f"GEOMETRIC_ITEM_SPECIFIC_USAGE('gisu_datum','',#{shape_aspect.eid},"
    f"#9005,#{face.eid})"
)
