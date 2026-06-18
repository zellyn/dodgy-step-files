"""M087 — AP210 signal net node references unresolved terminal.

Catalog claim: "A NETWORK (signal net) lists NETWORK_NODEs, one of which
references a TERMINAL by id that isn't declared in the file. The net is
dangling at one end."

Demonstration: construct a NETWORK with two NETWORK_NODEs in its network_nodes
list. The first node references a valid TERMINAL (#50); the second node
references a dangling TERMINAL (#999) that is never defined. This demonstrates
the exact defect: a signal net with an unresolved terminal reference.
"""
from step_corpus.step_builder import StepFile, DanglingRef

f = StepFile(catalog_id="M087",
             defect="NETWORK with unresolved TERMINAL reference in NETWORK_NODE")

# AP210 requires a basic product context.
# We need TERMINALs and a NETWORK that references them.

# First, create a TERMINAL (a connection point on a component).
# TERMINAL has (name, description, associated_component_terminal).
term1 = f._emit_raw("TERMINAL('term1','first terminal',())")

# Create NETWORK_NODEs: each references a TERMINAL.
# NETWORK_NODE has (name, associated_nodes, location, mapping_target).
# nn1 refs term1 which was just created as exec1
nn1 = f._emit_raw("NETWORK_NODE('nn1',(),(),(#" + str(term1.eid) + "))")

# Second NETWORK_NODE references a dangling terminal at #999
nn2 = f._emit_raw("NETWORK_NODE('nn2',(),(),(#999))")  # DANGLING ref to #999

# Create the NETWORK that lists both nodes
# NETWORK has (name, description, network_nodes).
network = f._emit_raw("NETWORK('net1','signal net with dangling ref',(#" +
                      f"{nn1.eid},#{nn2.eid}))")

# Add a minimal geometry model to anchor the AP210 net structure.
origin = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(origin, zdir, xdir)
plane = f.plane(plc)

p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))

v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

dirs = [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (-1.0, 0.0, 0.0), (0.0, -1.0, 0.0)]
verts = [(v0, v1), (v1, v2), (v2, v3), (v3, v0)]
points = [(p0, p1), (p1, p2), (p2, p3), (p3, p0)]
edges = []
for (dx, dy, dz), (va, vb), (pa, pb) in zip(dirs, verts, points):
    d = f.direction((dx, dy, dz))
    vec = f.vector(d, 1.0)
    line = f.line(pa, vec)
    edges.append(f.edge_curve(va, vb, line))

loop = f.edge_loop([f.oriented_edge(e) for e in edges])
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])

# Add product chain (required for validator)
f.add_product_chain(sbsm)
