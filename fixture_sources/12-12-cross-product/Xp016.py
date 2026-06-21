"""Xp016 — Forward reference × cyclic reference × invalid axis-placement."""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Xp016",
             defect='Forward reference x cyclic reference x zero-magnitude direction')

# Normal geometry for EDGE_CURVE/ADVANCED_FACE byte assertion (not present in
# Xp016's catalog assertions, but load == "ok" tier-3 requires geometry)
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

def line_edge(pa, pb, va, vb):
    dx = pb.args[1][0] - pa.args[1][0]
    dy = pb.args[1][1] - pa.args[1][1]
    dz = pb.args[1][2] - pa.args[1][2]
    length = (dx**2 + dy**2 + dz**2) ** 0.5
    d = f.direction((dx/length, dy/length, dz/length))
    vec = f.vector(d, length)
    ln = f.line(pa, vec)
    return f.edge_curve(va, vb, ln)

p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))
v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)
e0 = line_edge(p0, p1, v0, v1)
e1 = line_edge(p1, p2, v1, v2)
e2 = line_edge(p2, p3, v2, v3)
e3 = line_edge(p3, p0, v3, v0)
loop = f.edge_loop([
    f.oriented_edge(e0, True), f.oriented_edge(e1, True),
    f.oriented_edge(e2, True), f.oriented_edge(e3, True),
])
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# Defect 1: DIRECTION with zero-magnitude (0,0,0) — degenerate placement
zero_dir = f._emit_raw("DIRECTION('',(0.,0.,0.))")

# Defect 2 + 3: cyclic reference between two AXIS2_PLACEMENT_3D entities
# #A references #B's id as origin, and #B references #A as origin.
# We use _emit_raw to create the entities with intentional IDs.
# Reserve two IDs just past current _next_id
id_A = f._next_id
id_B = f._next_id + 1
f._next_id += 2

# #id_A references #id_B as origin (forward reference)
# #id_B references #id_A as origin (cycle)
from step_corpus.step_builder import Entity
ent_A = Entity(id_A, "__RAW__", [])
ent_A._raw_body = f"AXIS2_PLACEMENT_3D('',#{id_B},#{zero_dir.eid},#{zero_dir.eid})"
ent_B = Entity(id_B, "__RAW__", [])
ent_B._raw_body = f"AXIS2_PLACEMENT_3D('',#{id_A},#{zero_dir.eid},#{zero_dir.eid})"
f.entities.append(ent_A)
f.entities.append(ent_B)
