"""Tsh035 — DEGENERATE_TOROIDAL_SURFACE with negative minor radius and reused edge.

Catalog claim: "A DEGENERATE_TOROIDAL_SURFACE whose minor radius is negative
leads OCCT to invert the surface normal. An EDGE_LOOP on the degenerate torus
seam reuses the same EDGE_CURVE twice with opposite ORIENTED_EDGE senses,
making orientation ambiguous."

Demonstration: Build a degenerate toroidal surface with negative minor radius,
and construct the seam using the same EDGE_CURVE with opposite orientations.
This tests orientation ambiguity resolution.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tsh035",
             defect="Degenerate torus with negative minor radius and ambiguous edge reuse")

# Build a degenerate torus seam loop that reuses one edge with opposite senses.
# The torus has major_radius=1.0, minor_radius=-0.3 (negative, triggers inversion).

# Seam edge endpoints
p_seam_start = f.cartesian_point((1.0, 0.0, 0.0))
p_seam_end = f.cartesian_point((0.7, 0.0, 0.0))

v_seam_start = f.vertex_point(p_seam_start)
v_seam_end = f.vertex_point(p_seam_end)

# Seam edge (a straight line from major to minor radius)
d = f.direction((-1.0, 0.0, 0.0)); vec = f.vector(d, 0.3); ln = f.line(p_seam_start, vec)
seam_edge = f.edge_curve(v_seam_start, v_seam_end, ln)

# Loop that reuses the seam edge twice with opposite orientations (ambiguous!)
loop_seam = f.edge_loop([
    f.oriented_edge(seam_edge, True),   # Forward
    f.oriented_edge(seam_edge, False),  # Reversed (same edge, opposite sense)
])

# Degenerate torus placement (axis along Z at origin)
torus_origin = f.cartesian_point((0.0, 0.0, 0.0))
z_dir = f.direction((0.0, 0.0, 1.0))
x_dir = f.direction((1.0, 0.0, 0.0))
torus_plc = f.axis2_placement_3d(torus_origin, z_dir, x_dir)

# DEGENERATE_TOROIDAL_SURFACE with negative minor_radius (major=1.0, minor=-0.3)
# This is the key defect: negative minor radius inverts normal
degen_torus = f._emit("DEGENERATE_TOROIDAL_SURFACE", torus_plc, 1.0, -0.3)

# Face on the degenerate torus using the ambiguous seam loop
face = f.advanced_face([f.face_outer_bound(loop_seam)], degen_torus)

# Open shell containing the degenerate torus face
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
