"""Tsh021 — Non-manifold vertex (bowtie / hourglass).

Catalog claim: "A vertex whose 1-ring is not a single fan; touching cones,
bowtie meshes (two fans glued at a single point). Common when two solids
touch at exactly one vertex (hourglass)."

Demonstration: two triangular faces that share exactly one VERTEX_POINT
(no shared edge). The shared vertex's 1-ring is two disjoint fans.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tsh021",
             defect="Bowtie: two triangles sharing a single vertex (non-manifold 1-ring)")

# Shared vertex at origin.
p_shared = f.cartesian_point((0.0, 0.0, 0.0), name="bowtie_center")
v_shared = f.vertex_point(p_shared)

# Triangle 1: shared at origin, extends into +x/+y quadrant
p1a = f.cartesian_point((1.0, 0.0, 0.0))
p1b = f.cartesian_point((0.0, 1.0, 0.0))
v1a = f.vertex_point(p1a)
v1b = f.vertex_point(p1b)

# Edges of triangle 1
def _edge(p_from, p_to, v_from, v_to):
    dx = p_to.args[1][0] - p_from.args[1][0]
    dy = p_to.args[1][1] - p_from.args[1][1]
    dz = p_to.args[1][2] - p_from.args[1][2]
    length = (dx*dx + dy*dy + dz*dz) ** 0.5
    d = f.direction((dx/length, dy/length, dz/length))
    vec = f.vector(d, length)
    line = f.line(p_from, vec)
    return f.edge_curve(v_from, v_to, line)

e1_a = _edge(p_shared, p1a, v_shared, v1a)
e1_b = _edge(p1a, p1b, v1a, v1b)
e1_c = _edge(p1b, p_shared, v1b, v_shared)
loop1 = f.edge_loop([
    f.oriented_edge(e1_a, True),
    f.oriented_edge(e1_b, True),
    f.oriented_edge(e1_c, True),
])

# Triangle 2: shared at origin, extends into -x/-y quadrant (the other "fan")
p2a = f.cartesian_point((-1.0, 0.0, 0.0))
p2b = f.cartesian_point((0.0, -1.0, 0.0))
v2a = f.vertex_point(p2a)
v2b = f.vertex_point(p2b)

e2_a = _edge(p_shared, p2a, v_shared, v2a)
e2_b = _edge(p2a, p2b, v2a, v2b)
e2_c = _edge(p2b, p_shared, v2b, v_shared)
loop2 = f.edge_loop([
    f.oriented_edge(e2_a, True),
    f.oriented_edge(e2_b, True),
    f.oriented_edge(e2_c, True),
])

# The shared vertex v_shared is in both loops; touching at one point only,
# no shared edges. Classic bowtie.

ax_origin = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(ax_origin, zdir, xdir)
plane = f.plane(plc)
face1 = f.advanced_face([f.face_outer_bound(loop1)], plane)
face2 = f.advanced_face([f.face_outer_bound(loop2)], plane)

shell = f.open_shell([face1, face2])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
