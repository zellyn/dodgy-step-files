"""M161 — Reader does not validate cross-references; dangling references silently accepted

Catalog claim: "A STEP file has EDGE_CURVE referencing entity ID #999 where
#999 is not defined anywhere in the file. The reader's deserialiser walks the
data section once, then resolves references on demand; an unresolved reference
is silently treated as null."

Demonstration: Valid STEP file with a simple geometry (10×10 square face) where
one EDGE_CURVE in the loop references a non-existent LINE entity via DanglingRef.
The reader imports without diagnostic; the resulting edge has no underlying curve.
"""
from step_corpus.step_builder import StepFile, DanglingRef

f = StepFile(catalog_id="M161",
             defect="EDGE_CURVE references non-existent LINE entity")

# Create a 10×10 rectangle on z=0
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((10.0, 0.0, 0.0))
p2 = f.cartesian_point((10.0, 10.0, 0.0))
p3 = f.cartesian_point((0.0, 10.0, 0.0))

v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

# Helper to build edges
def _edge(pa, pb, va, vb):
    dx = pb.args[1][0] - pa.args[1][0]
    dy = pb.args[1][1] - pa.args[1][1]
    dz = pb.args[1][2] - pa.args[1][2]
    length = (dx*dx + dy*dy + dz*dz) ** 0.5
    d = f.direction((dx/length, dy/length, dz/length))
    vec = f.vector(d, length)
    line = f.line(pa, vec)
    return f.edge_curve(va, vb, line)

# First three edges are valid
edges = [
    _edge(p0, p1, v0, v1),
    _edge(p1, p2, v1, v2),
    _edge(p2, p3, v2, v3),
]

# Fourth edge: references a dangling LINE (#9999 that doesn't exist)
dangling_line = DanglingRef(9999)
edge_with_dangling_line = f.edge_curve(v3, v0, dangling_line)
edges.append(edge_with_dangling_line)

loop = f.edge_loop([f.oriented_edge(e) for e in edges])

# Create plane
ax_origin = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(ax_origin, zdir, xdir)
plane = f.plane(plc)

face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
