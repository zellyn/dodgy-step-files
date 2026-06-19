"""A087 — STEP exporter loses shapes after import-export cycle.

Catalog claim: final document has fewer shapes than original — some
sub-shapes were not reachable through the export's traversal.

Previous fixture used empty-EDGE_LOOP placeholders. Regen: 4 distinct
ADVANCED_FACEs in one shell, plus an additional 'orphaned' face
reachable only via a separate GEOMETRIC_SET (not via the SBSM chain) —
the writer's traversal walks SBSM only, so the orphaned face is lost.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A087",
             defect="orphaned ADVANCED_FACE in GEOMETRIC_SET (writer drops on round-trip)")

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

def line_edge(p, dir_tuple, length, va, vb):
    d = f.direction(dir_tuple); vec = f.vector(d, length); ln = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

faces = []
for k in range(4):
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

# Main shell contains 4 faces.
shell = f.open_shell(faces)
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# Orphaned 5th face — reachable only via a separate GEOMETRIC_SET.
# Writers traversing the SBSM chain don't see this; round-trip loses it.
p0 = f.cartesian_point((100.0, 0.0, 0.0))
p1 = f.cartesian_point((101.0, 0.0, 0.0))
p2 = f.cartesian_point((101.0, 1.0, 0.0))
p3 = f.cartesian_point((100.0, 1.0, 0.0))
v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)
e0 = line_edge(p0, (1.0, 0.0, 0.0), 1.0, v0, v1)
e1 = line_edge(p1, (0.0, 1.0, 0.0), 1.0, v1, v2)
e2 = line_edge(p2, (-1.0, 0.0, 0.0), 1.0, v2, v3)
e3 = line_edge(p3, (0.0, -1.0, 0.0), 1.0, v3, v0)
loop_orphan = f.edge_loop([
    f.oriented_edge(e0, True), f.oriented_edge(e1, True),
    f.oriented_edge(e2, True), f.oriented_edge(e3, True),
])
orphan_face = f.advanced_face([f.face_outer_bound(loop_orphan)], plane)
f._emit_raw(
    f"GEOMETRIC_SET('orphaned_face_carrier',(#{orphan_face.eid}))"
)
