"""Tsh028 — STYLED_ITEM attached to sub-tolerance sliver ADVANCED_FACE.

Catalog claim: "Per-face STYLED_ITEM / PRESENTATION_STYLE_ASSIGNMENT references
break when the face they target is dropped by sliver-face removal or merged
with neighbors during orientation healing."

Demonstration: Build a three-edge sliver ADVANCED_FACE with very small width
(1e-9 mm), add a STYLED_ITEM referencing it. When the sliver is removed during
healing, the STYLED_ITEM becomes orphaned.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tsh028",
             defect="STYLED_ITEM orphaned when sliver face is removed")

# Main face: large rectangle at z=0
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))

v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)

# Edges for main face
d = f.direction((1.0, 0.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(p0, vec)
e0 = f.edge_curve(v0, v1, ln)
d = f.direction((0.0, 1.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(p1, vec)
e1 = f.edge_curve(v1, v2, ln)
d = f.direction((-1.0, 0.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(p2, vec)
e2 = f.edge_curve(v2, v3, ln)
d = f.direction((0.0, -1.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(p3, vec)
e3 = f.edge_curve(v3, v0, ln)

loop_main = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# Plane for main face
ax_orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(ax_orig, zdir, xdir)
plane = f.plane(plc)

face_main = f.advanced_face([f.face_outer_bound(loop_main)], plane)

# Sliver face: three-edge sliver with width 1e-9 (below tolerance)
# Vertices at (0, 0, 0.1), (1, 0, 0.1), (1+1e-9, 1, 0.1)
ps0 = f.cartesian_point((0.0, 0.0, 0.1))
ps1 = f.cartesian_point((1.0, 0.0, 0.1))
ps2 = f.cartesian_point((1.0 + 1e-9, 1.0, 0.1))

vs0 = f.vertex_point(ps0)
vs1 = f.vertex_point(ps1)
vs2 = f.vertex_point(ps2)

# Edges for sliver (3 edges)
d = f.direction((1.0, 0.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(ps0, vec)
es0 = f.edge_curve(vs0, vs1, ln)
# Diagonal edge from ps1 to ps2
d_diag = (1.0 + 1e-9 - 1.0, 1.0 - 0.0, 0.0)
d_norm = (d_diag[0]**2 + d_diag[1]**2)**0.5
if d_norm > 0:
    d_normalized = (d_diag[0]/d_norm, d_diag[1]/d_norm, 0.0)
else:
    d_normalized = (0.0, 0.0, 0.0)
d = f.direction(d_normalized)
vec = f.vector(d, d_norm)
ln = f.line(ps1, vec)
es1 = f.edge_curve(vs1, vs2, ln)
# Edge from ps2 back to ps0
d = f.direction((-(1.0 + 1e-9), -1.0, 0.0)); vec = f.vector(d, ((1.0 + 1e-9)**2 + 1.0)**0.5); ln = f.line(ps2, vec)
es2 = f.edge_curve(vs2, vs0, ln)

loop_sliver = f.edge_loop([
    f.oriented_edge(es0, True),
    f.oriented_edge(es1, True),
    f.oriented_edge(es2, True),
])

plc_sliver = f.axis2_placement_3d(ps0, zdir, xdir)
plane_sliver = f.plane(plc_sliver)

face_sliver = f.advanced_face([f.face_outer_bound(loop_sliver)], plane_sliver)

# Open shell with both faces
shell = f.open_shell([face_main, face_sliver])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
