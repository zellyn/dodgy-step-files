"""A100 — STEP importer routes Assembly-module assemblies into Part containers.

Catalog claim: STEP file with KINEMATIC_TOPOLOGY_STRUCTURE / MECHANISM
referencing geometry sub-shapes is silently dropped.

Previous fixture used empty-EDGE_LOOP placeholders. Regen: 2
ADVANCED_FACEs + a stub MECHANISM/KINEMATIC_JOINT chain that
references them.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="A100",
             defect="2 sub-shapes + stub MECHANISM/KINEMATIC_JOINT references")

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

# Stub MECHANISM / KINEMATIC_JOINT graph — what the importer drops.
# These reference the faces as the kinematic sub-shapes.
f._emit_raw(
    f"KINEMATIC_TOPOLOGY_STRUCTURE('joint_graph',(#{faces[0].eid},#{faces[1].eid}))"
)
f._emit_raw(
    f"MECHANISM('mech_joint_1',(#{faces[0].eid},#{faces[1].eid}))"
)
