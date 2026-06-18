"""Tsh039 — Self-touching boundary cycle (figure-eight wire after triangulation).

Catalog claim: "A face whose boundary loop folds back on itself after
triangulation, or '4-manifold edge' (one shared edge has two pairs of triangles).
Tests healing via CGAL stitch_boundary_cycles or Manifold's DedupeEdges."

Demonstration: Build a single face with a boundary loop that pinches (self-touches)
at one point, forming a figure-eight or bow-tie topology. The loop traces
itself back on the same path.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tsh039",
             defect="Self-touching boundary loop (figure-eight wire)")

# Build a figure-eight (bow-tie) face:
# The loop starts at (0,0), goes right to (1,0), up to (1,1),
# back left to (0,0), then repeats the same path (or a similar pinch).
# This creates a self-intersection at the "waist."

# Pinch point and outer loop
p_pinch = f.cartesian_point((0.5, 0.5, 0.0))

# Top half loop: (0,0) → (1,0) → (1,1) → (0,1) → (0,0)
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))

v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)
v_pinch = f.vertex_point(p_pinch)

# Edges for top half
d = f.direction((1.0, 0.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(p0, vec)
e0 = f.edge_curve(v0, v1, ln)
d = f.direction((0.0, 1.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(p1, vec)
e1 = f.edge_curve(v1, v2, ln)
d = f.direction((-1.0, 0.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(p2, vec)
e2 = f.edge_curve(v2, v3, ln)
d = f.direction((0.0, -1.0, 0.0)); vec = f.vector(d, 1.0); ln = f.line(p3, vec)
e3 = f.edge_curve(v3, v0, ln)

# Bottom half loop: same boundary retraced (creates pinch)
# This forces a self-touching point in the middle of the loop
# In STEP, we represent this as the loop starting at pinch, going around,
# and coming back to pinch (a figure-eight).

# Simplified: just use the outer rectangle but with a "internal" edge
# that makes the loop self-touch. We'll create a loop that goes:
# (0,0) → (1,0) → (1,1) → (0.5,0.5) → (1,1) → (0,1) → (0,0)
# This causes a self-intersection at (0.5, 0.5).

# Edge from p2 to pinch
# Direction from (1,1,0) to (0.5, 0.5, 0)
d_vec = (-0.5, -0.5, 0.0)
d_norm = (0.5**2 + 0.5**2)**0.5
d_normalized = (-0.5/d_norm, -0.5/d_norm, 0.0)
d = f.direction(d_normalized)
vec = f.vector(d, d_norm)
ln = f.line(p2, vec)
e_to_pinch = f.edge_curve(v2, v_pinch, ln)

# Edge from pinch back up to p2 (retracing)
d_vec = (0.5, 0.5, 0.0)
d_norm = (0.5**2 + 0.5**2)**0.5
d_normalized = (0.5/d_norm, 0.5/d_norm, 0.0)
d = f.direction(d_normalized)
vec = f.vector(d, d_norm)
ln = f.line(p_pinch, vec)
e_from_pinch = f.edge_curve(v_pinch, v2, ln)

# Self-touching loop: creates figure-eight
loop_self_touch = f.edge_loop([
    f.oriented_edge(e0, True),     # p0 → p1
    f.oriented_edge(e1, True),     # p1 → p2
    f.oriented_edge(e_to_pinch, True),     # p2 → pinch
    f.oriented_edge(e_from_pinch, True),   # pinch → p2 (retraces!)
    f.oriented_edge(e2, True),     # p2 → p3
    f.oriented_edge(e3, True),     # p3 → p0
])

# Plane for the face
ax_orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(ax_orig, zdir, xdir)
plane = f.plane(plc)

face = f.advanced_face([f.face_outer_bound(loop_self_touch)], plane)

# Open shell containing the self-touching face
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
