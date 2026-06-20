"""Bo025 — Two ADVANCED_FACEs on duplicate CYLINDRICAL_SURFACEs share a smooth
(G1) edge mis-tagged as a sharp crease.

Catalog claim: Two ADVANCED_FACEs on CYLINDRICAL_SURFACEs (often defined as
two distinct surface entities with identical axis and radius — duplicates of one
cylinder) meet along a shared circular edge; their normals at the edge are
tangent-continuous (G1) but the edge is mis-tagged as a sharp boundary (C0).

Mechanism IS the OPEN_SHELL face/edge topology: two ADVANCED_FACEs each on a
separate but identical CYLINDRICAL_SURFACE (same axis, same radius r=1.0) share
a common CIRCLE edge. The two surfaces are geometrically tangent along that
circle — smooth meeting — but are represented as two distinct surface entities,
which is the static trigger for the regularity-encoding defect. Both faces and
their shared circular edge ARE wired into a single OPEN_SHELL inside a
SHELL_BASED_SURFACE_MODEL.

Tier-3 assertions: face[0].surface_type == "cylinder", face[1].surface_type == "cylinder"
Expected: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile
import math

f = StepFile(
    catalog_id="Bo025",
    defect=(
        "Two ADVANCED_FACEs on duplicate CYLINDRICAL_SURFACEs (same axis, same "
        "radius=1.0) share a circular edge — surfaces meet tangentially (G1) but "
        "modelled as distinct surface entities IS wired into OPEN_SHELL face/edge "
        "topology; regularity-encoder mis-tags the shared edge as C0 (sharp crease)"
    ),
)

# ── Shared axis: Z-axis through origin, radius = 1.0 ─────────────────────────
# CylA: the lower half-cylinder  (z in [-1, 0])
# CylB: the upper half-cylinder  (z in [ 0, 1])
# Both surfaces: CYLINDRICAL_SURFACE at origin, Z-axis, radius 1.0 — identical
# geometry, two separate entities — this IS the duplicate-surface static trigger.

orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))

axA = f.axis2_placement_3d(orig, zdir, xdir)
cylA = f.cylindrical_surface(axA, 1.0)   # duplicate surface entity 1

axB = f.axis2_placement_3d(orig, zdir, xdir)  # same params
cylB = f.cylindrical_surface(axB, 1.0)   # duplicate surface entity 2 (IS the defect trigger)

# ── Shared circular edge at z=0 ───────────────────────────────────────────────
# The shared circle at z=0, r=1 in XY-plane.
ax_circ = f.axis2_placement_3d(orig, zdir, xdir)
shared_circle = f.circle(ax_circ, 1.0)

# Two vertices on the circle where the seam edge will be placed.
# We use a full-circle seam trick: one vertex on the seam.
p_seam = f.cartesian_point((1.0, 0.0, 0.0))  # point at angle=0 on circle r=1 z=0
v_seam = f.vertex_point(p_seam)

# Shared circle edge is a degenerate seam edge (start==end, full circle traversal).
seam_edge = f.edge_curve(v_seam, v_seam, shared_circle)

# ── Top edge at z=1 (upper rim of CylB) ──────────────────────────────────────
orig_top = f.cartesian_point((0.0, 0.0, 1.0))
ax_top   = f.axis2_placement_3d(orig_top, zdir, xdir)
top_circle = f.circle(ax_top, 1.0)
p_top_seam = f.cartesian_point((1.0, 0.0, 1.0))
v_top_seam = f.vertex_point(p_top_seam)
top_edge = f.edge_curve(v_top_seam, v_top_seam, top_circle)

# ── Bottom edge at z=-1 (lower rim of CylA) ──────────────────────────────────
orig_bot = f.cartesian_point((0.0, 0.0, -1.0))
ax_bot   = f.axis2_placement_3d(orig_bot, zdir, xdir)
bot_circle = f.circle(ax_bot, 1.0)
p_bot_seam = f.cartesian_point((1.0, 0.0, -1.0))
v_bot_seam = f.vertex_point(p_bot_seam)
bot_edge = f.edge_curve(v_bot_seam, v_bot_seam, bot_circle)

# ── Face loops: each face is a cylindrical band ───────────────────────────────
# FaceA: lower band z in [-1, 0], uses bot_edge + seam_edge
loopA = f.edge_loop([
    f.oriented_edge(bot_edge,  True),   # bottom rim (outward)
    f.oriented_edge(seam_edge, True),   # shared circle at z=0
])
faceA = f.advanced_face([f.face_outer_bound(loopA)], cylA, same_sense=True)

# FaceB: upper band z in [0, 1], uses seam_edge (reversed) + top_edge
loopB = f.edge_loop([
    f.oriented_edge(seam_edge, False),  # shared circle reused (reversed) — IS wired
    f.oriented_edge(top_edge,  True),   # top rim
])
faceB = f.advanced_face([f.face_outer_bound(loopB)], cylB, same_sense=True)

# ── CATALOG MECHANISM: both faces in one OPEN_SHELL — shared edge wired in ────
# Byte assertion: contains(b'CYLINDRICAL_SURFACE')
# Byte assertion: contains(b'ADVANCED_FACE')
# seam_edge appears in both face loops → shared circular edge between duplicate cylinders
shell = f.open_shell([faceA, faceB], name="bo025_dup_cyl")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
