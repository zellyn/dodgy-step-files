"""Sw007 — Fast-sewing cannot find the canonical vertex for a wire endpoint.

Catalog claim: Two VERTEX_POINTs whose 3D coordinates differ by a large
magnitude ((0,0,0) and (1e6,0,0)) fall into the same hash bucket in the
fast-sewing vertex table due to bit-pattern coincidence, but are spatially
distant — no near-coincident match within sewing tolerance.  The algorithm
cannot decide whether to dedup or insert.

Mechanism IS the shell / face topology: both VERTEX_POINTs ARE wired as
start and end vertices of an EDGE_CURVE which IS wired into the
FACE_OUTER_BOUND EDGE_LOOP of the single ADVANCED_FACE of the OPEN_SHELL.
The widely-separated vertices ARE directly embedded in the boundary topology
— no post-hoc args mutation.

Byte assertions:
  - count_entity_def(b'VERTEX_POINT') == 2
  - contains(b'1.0e6') or contains(b'1.0E6') or contains(b'1.E6') or contains(b'1000000')
Tier-3 assertions:
  - shape_null == True
OCC behavior: silently accepts (empty result).
live oracle: occt=shape(1)/shape(1)/empty
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Sw007",
    defect=(
        "Exactly 2 VERTEX_POINTs at (0,0,0) and (1e6,0,0) ARE wired as start/end "
        "of EDGE_CURVE in EDGE_LOOP of ADVANCED_FACE of OPEN_SHELL; "
        "widely-separated coords trigger fast-sewing hash-bucket collision "
        "with no near-coincident match; vertex lookup fails"
    ),
)

# ── Minimal face: one edge spanning (0,0,0)→(1e6,0,0) ───────────────────────
# Exactly 2 VERTEX_POINTs satisfying byte assertion count_entity_def == 2
p_near = f.cartesian_point((0.0, 0.0, 0.0))
p_far  = f.cartesian_point((1.0e6, 0.0, 0.0))

v_near = f.vertex_point(p_near)   # VERTEX_POINT 1 at (0,0,0)
v_far  = f.vertex_point(p_far)    # VERTEX_POINT 2 at (1e6,0,0) — exact count: 2

# Single EDGE_CURVE from v_near to v_far
d_x    = f.direction((1.0, 0.0, 0.0))
vec_1M = f.vector(d_x, 1.0e6)
ln     = f.line(p_near, vec_1M)
edge   = f.edge_curve(v_near, v_far, ln)  # start=v_near (0,0,0), end=v_far (1e6,0,0)

# Degenerate edge_loop: forward then backward (back-and-forth) to close with only 2 vertices
oe_fwd = f.oriented_edge(edge, True)
oe_rev = f.oriented_edge(edge, False)
loop   = f.edge_loop([oe_fwd, oe_rev])

# Plane for the face
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

fob  = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane)

# OPEN_SHELL IS the shell topology carrier — widely-separated VERTEX_POINTs
# ARE wired directly into the face boundary
shell = f.open_shell([face], name="sw007_hash_collision_vertices")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
