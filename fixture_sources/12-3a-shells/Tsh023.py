"""Tsh023 — Empty EDGE_LOOP / empty face list on shells.

Catalog claim: "STEP file with empty EDGE_LOOP(..,()) crashes reader.
Similarly: empty EDGE_BASED_WIREFRAME_MODEL with empty boundary or
empty connected_edge_set; FACE_BASED_SURFACE_MODEL with empty face list."

Demonstration: Build an OPEN_SHELL containing one normal face and one
ADVANCED_FACE with an empty EDGE_LOOP. The empty loop should trigger
the crash or parse failure the catalog warns about.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tsh023",
             defect="Empty EDGE_LOOP crashes reader")

# Valid face: rectangle at z=0
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))

v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

# Edges for valid face
d = f.direction((1.0, 0.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(p0, vec)
e0 = f.edge_curve(v0, v1, ln)
d = f.direction((0.0, 1.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(p1, vec)
e1 = f.edge_curve(v1, v2, ln)
d = f.direction((-1.0, 0.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(p2, vec)
e2 = f.edge_curve(v2, v3, ln)
d = f.direction((0.0, -1.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(p3, vec)
e3 = f.edge_curve(v3, v0, ln)

loop_normal = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# Plane for both faces
ax_orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(ax_orig, zdir, xdir)
plane = f.plane(plc)

# Valid face
face_good = f.advanced_face([f.face_outer_bound(loop_normal)], plane)

# EMPTY EDGE_LOOP: no edges in the list
empty_loop = f.edge_loop([])

# Face with empty loop (the defect)
face_bad = f.advanced_face([f.face_outer_bound(empty_loop)], plane)

# Shell containing both faces; the empty loop is the crash trigger
shell = f.open_shell([face_good, face_bad])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
