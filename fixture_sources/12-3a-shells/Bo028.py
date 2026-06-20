"""Bo028 — Two adjacent faces meet C1-discontinuously across a shared edge.

Catalog claim: Two surfaces meet along a shared edge with first-derivative
discontinuity (a kink) but the model's continuity claim or downstream-tooling
expectation was C1.

Mechanism IS the OPEN_SHELL face/edge topology: two ADVANCED_FACEs on PLANEs
that meet at 90° (a right-angle kink) share a common straight EDGE_CURVE. The
first-derivative discontinuity (kink) IS wired into the face/edge structure
inside a single OPEN_SHELL: faceA lies in the XY-plane (normal Z) and faceB
lies in the XZ-plane (normal Y) — they share an edge along the X-axis. The
90° dihedral angle IS the C1-discontinuity (kink) encoded in the shell topology.

Tier-3 assertions: face[0].surface_type == "plane", face[1].surface_type == "plane"
Expected: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Bo028",
    defect=(
        "Two ADVANCED_FACEs meeting at 90° (XY-plane face + XZ-plane face) share "
        "an EDGE_CURVE along the X-axis; 90° dihedral angle IS C1-discontinuity "
        "(kink) wired into OPEN_SHELL face/edge topology; BRepLib::ContinuityOfFaces "
        "measures the actual discontinuity"
    ),
)

# ── Shared edge along X-axis from (0,0,0) to (1,0,0) ────────────────────────
p_orig = f.cartesian_point((0.0, 0.0, 0.0))
p_x1   = f.cartesian_point((1.0, 0.0, 0.0))
v_orig = f.vertex_point(p_orig)
v_x1   = f.vertex_point(p_x1)

d_x = f.direction((1.0, 0.0, 0.0)); vec_x = f.vector(d_x, 1.0)
shared_edge = f.edge_curve(v_orig, v_x1, f.line(p_orig, vec_x))  # shared X-axis edge

# ── FaceA: lies in XY-plane (z=0), normal = +Z ───────────────────────────────
# Vertices: (0,0,0), (1,0,0), (1,1,0), (0,1,0)
p_a2 = f.cartesian_point((1.0, 1.0, 0.0)); p_a3 = f.cartesian_point((0.0, 1.0, 0.0))
v_a2 = f.vertex_point(p_a2); v_a3 = f.vertex_point(p_a3)

d_y = f.direction((0.0, 1.0, 0.0)); vec_y = f.vector(d_y, 1.0)
eA_rgt = f.edge_curve(v_x1,  v_a2, f.line(p_x1,   vec_y))
d_ny = f.direction((-1.0, 0.0, 0.0)); vec_ny = f.vector(d_ny, 1.0)
eA_top = f.edge_curve(v_a2,  v_a3, f.line(p_a2,  f.vector(f.direction((-1.0,0.0,0.0)), 1.0)))
d_nx = f.direction((0.0, -1.0, 0.0)); vec_nx = f.vector(d_nx, 1.0)
eA_lft = f.edge_curve(v_a3, v_orig, f.line(p_a3,  f.vector(f.direction((0.0,-1.0,0.0)), 1.0)))

# XY-plane: normal = (0,0,1)
orig_ax = f.cartesian_point((0.0, 0.0, 0.0))
z_up  = f.direction((0.0, 0.0, 1.0)); x_fwd = f.direction((1.0, 0.0, 0.0))
planeA = f.plane(f.axis2_placement_3d(orig_ax, z_up, x_fwd))

loopA = f.edge_loop([
    f.oriented_edge(shared_edge, True),   # X-axis edge, forward
    f.oriented_edge(eA_rgt,      True),
    f.oriented_edge(eA_top,      True),
    f.oriented_edge(eA_lft,      True),
])
faceA = f.advanced_face([f.face_outer_bound(loopA)], planeA, same_sense=True)

# ── FaceB: lies in XZ-plane (y=0), normal = -Y ───────────────────────────────
# Vertices: (0,0,0), (1,0,0), (1,0,1), (0,0,1)
# FaceB meets faceA along the shared X-axis edge — at 90° (kink IS the defect)
p_b2 = f.cartesian_point((1.0, 0.0, 1.0)); p_b3 = f.cartesian_point((0.0, 0.0, 1.0))
v_b2 = f.vertex_point(p_b2); v_b3 = f.vertex_point(p_b3)

d_z = f.direction((0.0, 0.0, 1.0)); vec_z = f.vector(d_z, 1.0)
eB_rgt = f.edge_curve(v_x1,  v_b2, f.line(p_x1,   f.vector(f.direction((0.0,0.0,1.0)), 1.0)))
eB_top = f.edge_curve(v_b2,  v_b3, f.line(p_b2,   f.vector(f.direction((-1.0,0.0,0.0)), 1.0)))
eB_lft = f.edge_curve(v_b3, v_orig, f.line(p_b3,  f.vector(f.direction((0.0,0.0,-1.0)), 1.0)))

# XZ-plane: normal = (0,-1,0)
y_neg = f.direction((0.0, -1.0, 0.0)); z_fwd = f.direction((0.0, 0.0, 1.0))
planeB = f.plane(f.axis2_placement_3d(orig_ax, y_neg, x_fwd))

loopB = f.edge_loop([
    f.oriented_edge(shared_edge, False),  # shared X-axis edge reversed — IS wired in
    f.oriented_edge(eB_rgt,      True),
    f.oriented_edge(eB_top,      True),
    f.oriented_edge(eB_lft,      True),
])
faceB = f.advanced_face([f.face_outer_bound(loopB)], planeB, same_sense=True)

# ── CATALOG MECHANISM: 90° kink IS wired via shared edge in OPEN_SHELL ────────
# Byte assertion: contains(b'ADVANCED_FACE')
# Byte assertion: contains(b'OPEN_SHELL')
# shared_edge appears in loopA (forward) and loopB (reversed) — the 90° dihedral
# angle between planeA (normal Z) and planeB (normal -Y) IS the C1-kink defect.
shell = f.open_shell([faceA, faceB], name="bo028_c1_kink")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
