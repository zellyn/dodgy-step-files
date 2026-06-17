"""Tfa098 — ShapeFix_Face.FixSplitFace null-line.

Catalog claim: "Face split by a LINE edge whose geometry has been
internally replaced with null. FixSplitFace doesn't validate the
splitter, causing null-deref or silent corruption."

Demonstration: a 10×10 face whose outer-loop fourth edge references a
DanglingRef — entity #99 that is never defined. Schema-strict parser
rejects (E_UNRESOLVED_REFS); OCCT may auto-heal or crash.
"""
from step_corpus.step_builder import StepFile, DanglingRef

f = StepFile(catalog_id="Tfa098",
             defect="FixSplitFace given a face with an edge referencing undefined LINE geometry")

# 10x10 rectangle on z=0
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((10.0, 0.0, 0.0))
p2 = f.cartesian_point((10.0, 10.0, 0.0))
p3 = f.cartesian_point((0.0, 10.0, 0.0))
v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

# First three edges are properly constructed
dirs = [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (-1.0, 0.0, 0.0)]
verts = [(v0, v1), (v1, v2), (v2, v3)]
points = [(p0, p1), (p1, p2), (p2, p3)]
edges = []
for (dx, dy, dz), (va, vb), (pa, pb) in zip(dirs, verts, points):
    d = f.direction((dx, dy, dz))
    vec = f.vector(d, 10.0)
    line = f.line(pa, vec)
    edges.append(f.edge_curve(va, vb, line))

# Fourth edge: references DANGLING #99 instead of a real LINE geometry
# This is the intentional defect.
dangling_line = DanglingRef(99)
edge_with_null_geom = f.edge_curve(v3, v0, dangling_line)
edges.append(edge_with_null_geom)

loop = f.edge_loop([f.oriented_edge(e) for e in edges])
ax_origin = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(ax_origin, zdir, xdir)
plane = f.plane(plc)
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
