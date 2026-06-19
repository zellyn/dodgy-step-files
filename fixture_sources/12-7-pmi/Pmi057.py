"""Pmi057 — PMI semantic vs presentation associativity lost on round-trip.

Catalog claim: a semantic GEOMETRIC_TOLERANCE loses its associativity
with the toleranced ADVANCED_FACE after translation.

Previous fixture used empty-EDGE_LOOP placeholders. Regen: 2 faces +
GEOMETRIC_TOLERANCE referencing one face + DRAUGHTING_ANNOTATION_
OCCURRENCE for the graphical presentation.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Pmi057",
             defect="GEOMETRIC_TOLERANCE + ANNOTATION_OCCURRENCE on toleranced face")

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple); vec = f.vector(d, length); ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

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

# Toleranced shape aspect on face 0.
shape_aspect = f._emit_raw(
    f"SHAPE_ASPECT('toleranced_aspect','',#9005,.T.)"
)
# Semantic GEOMETRIC_TOLERANCE (perpendicularity).
f._emit_raw(
    f"PERPENDICULARITY_TOLERANCE('perpendicularity',"
    f"'0.05 mm perpendicularity',#9009,#{shape_aspect.eid})"
)
# Graphical presentation that drifts off the part on round-trip.
f._emit_raw(
    f"ANNOTATION_PLANE('perp_plane',(),#{plc.eid},(#{faces[0].eid}))"
)
