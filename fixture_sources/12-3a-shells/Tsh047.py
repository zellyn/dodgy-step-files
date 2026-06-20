"""Tsh047 — Same-domain face unification crosses cylinder seam, producing non-manifold result.

Catalog claim: A cylindrical face with a closed seam has been emitted as two
half-cylinder faces sharing a seam edge. The kernel's face-unification step
recognises both carry the same underlying CYLINDRICAL_SURFACE and merges them;
but in doing so reuses the seam edge as an interior edge, producing a
non-manifold result (the seam edge belongs to one merged face but is referenced
twice).

Mechanism IS the shell structure: an OPEN_SHELL contains two ADVANCED_FACEs
on the SAME CYLINDRICAL_SURFACE (radius 1, axis Z). Face A covers U=[0,π],
Face B covers U=[π,2π]. They share two vertical EDGE_CURVEs at U=0 (seam)
and U=π. The shared seam edges ARE wired into the shell/face/edge topology
with opposite ORIENTED_EDGE senses. A unifier must NOT merge across the
periodic seam; if it does, the seam edge is listed twice in the merged
face's outer wire — a non-manifold defect.

Byte assertions:
  - contains(b'OPEN_SHELL')
  - contains(b'CYLINDRICAL_SURFACE')
  - count_entity_def(b'ADVANCED_FACE') == 2

Tier-3 assertion: n_faces_total == 2

live oracle: occt=shape(1)/shape(1)
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh047",
    defect=(
        "OPEN_SHELL with 2 ADVANCED_FACEs on same CYLINDRICAL_SURFACE (R=1, axis Z), "
        "split at U=0 and U=pi into two half-cylinders; "
        "shared seam edges at U=0 and U=pi are wired with opposite orientations; "
        "face unifier must NOT merge across periodic seam; "
        "seam edges ARE the mechanism in shell/face/edge topology"
    ),
)

# Cylinder radius=1, height=1, axis=Z.
# Two seam lines: U=0 (x=1, y=0) and U=pi (x=-1, y=0).
# Heights: z=0 (bottom), z=1 (top).

R = 1.0
H = 1.0

# Four corner points on the cylinder surface
# At U=0 (x=1,y=0):   p0_bot, p0_top
# At U=pi (x=-1,y=0): p_pi_bot, p_pi_top
p0_bot   = f.cartesian_point(( R,  0.0, 0.0))
p0_top   = f.cartesian_point(( R,  0.0, H))
p_pi_bot = f.cartesian_point((-R,  0.0, 0.0))
p_pi_top = f.cartesian_point((-R,  0.0, H))

v0_bot   = f.vertex_point(p0_bot)
v0_top   = f.vertex_point(p0_top)
v_pi_bot = f.vertex_point(p_pi_bot)
v_pi_top = f.vertex_point(p_pi_top)

# Two vertical seam edges (LINE geometry, running z=0→z=1)
def vert_edge(va, vb, px, py):
    pst = f.cartesian_point((px, py, 0.0))
    d   = f.direction((0.0, 0.0, 1.0))
    vec = f.vector(d, H)
    ln  = f.line(pst, vec)
    return f.edge_curve(va, vb, ln)

seam_u0  = vert_edge(v0_bot,   v0_top,   R,  0.0)  # at U=0
seam_upi = vert_edge(v_pi_bot, v_pi_top, -R, 0.0)  # at U=pi

# Two circular arcs for bottom and top:
# Bottom arc A: U=0→pi (x=1,y=0 → x=-1,y=0) CCW in XY, z=0
# Bottom arc B: U=pi→2pi (x=-1,y=0 → x=1,y=0) CCW, z=0
# Top arcs: same but at z=H

cyl_axis_pt  = f.cartesian_point((0.0, 0.0, 0.0))
cyl_axis_top = f.cartesian_point((0.0, 0.0, H))
cyl_z    = f.direction((0.0, 0.0, 1.0))
cyl_x    = f.direction((1.0, 0.0, 0.0))

def circle_edge(va, vb, center_pt, normal_dir, ref_dir, arc_label):
    """Build an EDGE_CURVE backed by a CIRCLE (half-circle arc)."""
    plc = f.axis2_placement_3d(center_pt, normal_dir, ref_dir)
    circ = f.circle(plc, R)
    return f.edge_curve(va, vb, circ)

# Bottom arcs
arc_bot_A = circle_edge(v0_bot,   v_pi_bot, cyl_axis_pt,  cyl_z, cyl_x, "botA")
arc_bot_B = circle_edge(v_pi_bot, v0_bot,   cyl_axis_pt,  cyl_z, cyl_x, "botB")

# Top arcs (center at z=H, axis = -Z so CCW when viewed from above going the same way)
cyl_z_neg = f.direction((0.0, 0.0, -1.0))
arc_top_A = circle_edge(v_pi_top, v0_top,   cyl_axis_top, cyl_z_neg, cyl_x, "topA")
arc_top_B = circle_edge(v0_top,   v_pi_top, cyl_axis_top, cyl_z_neg, cyl_x, "topB")

# ── CYLINDRICAL_SURFACE (shared by both faces) ────────────────────────────────
cyl_plc_pt = f.cartesian_point((0.0, 0.0, 0.0))
cyl_plc    = f.axis2_placement_3d(cyl_plc_pt, cyl_z, cyl_x)
cyl_surf   = f.cylindrical_surface(cyl_plc, R)

# ── Face A: U=[0,pi], front half ──────────────────────────────────────────────
# Loop: seam_u0(up, fwd) → arc_top_A(fwd, pi→0 at top reversed) → seam_upi(down, rev) → arc_bot_A(fwd, 0→pi)
loopA = f.edge_loop([
    f.oriented_edge(seam_u0,  True),    # v0_bot → v0_top (up at U=0)
    f.oriented_edge(arc_top_A, True),   # v_pi_top → v0_top (reversed: top going 0←pi)
    f.oriented_edge(seam_upi, False),   # v_pi_top → v_pi_bot (down at U=pi, reversed)
    f.oriented_edge(arc_bot_A, True),   # v0_bot → v_pi_bot ... wait, need head-to-tail

])

# Re-think loop order for head-to-tail traversal on Face A:
# Start at v0_bot:
#   seam_u0 fwd:   v0_bot  → v0_top
#   arc_top_A fwd: v_pi_top→ v0_top  -- WRONG (head mismatch)
# Correct traversal:
#   seam_u0 fwd:    v0_bot   → v0_top
#   arc_top_A rev:  v0_top   → v_pi_top  (arc_top_A is v_pi_top→v0_top, reversed gives v0_top→v_pi_top)
#   seam_upi rev:   v_pi_top → v_pi_bot  (seam_upi is v_pi_bot→v_pi_top, reversed gives v_pi_top→v_pi_bot)
#   arc_bot_A rev:  v_pi_bot → v0_bot    (arc_bot_A is v0_bot→v_pi_bot, reversed gives v_pi_bot→v0_bot)

loopA = f.edge_loop([
    f.oriented_edge(seam_u0,   True),    # v0_bot   → v0_top
    f.oriented_edge(arc_top_A, False),   # v0_top   → v_pi_top
    f.oriented_edge(seam_upi,  False),   # v_pi_top → v_pi_bot
    f.oriented_edge(arc_bot_A, False),   # v_pi_bot → v0_bot
])
faceA = f.advanced_face([f.face_outer_bound(loopA)], cyl_surf)

# ── Face B: U=[pi,2pi], back half ─────────────────────────────────────────────
# Start at v_pi_bot:
#   seam_upi fwd:   v_pi_bot → v_pi_top
#   arc_top_B fwd:  v0_top   → v_pi_top  -- WRONG
# Correct:
#   seam_upi fwd:   v_pi_bot → v_pi_top
#   arc_top_B rev:  v_pi_top → v0_top    (arc_top_B is v0_top→v_pi_top, reversed → v_pi_top→v0_top)
#   seam_u0 rev:    v0_top   → v0_bot    (seam_u0 is v0_bot→v0_top, reversed → v0_top→v0_bot)
#   arc_bot_B fwd:  v0_bot   → v_pi_bot  -- wait arc_bot_B is v_pi_bot→v0_bot; reversed → v0_bot→v_pi_bot -- correct!
# Actually arc_bot_B: v_pi_bot → v0_bot (as defined above)
# arc_bot_B rev: v0_bot → v_pi_bot  ← that's what we need to close loop

loopB = f.edge_loop([
    f.oriented_edge(seam_upi,  True),    # v_pi_bot → v_pi_top
    f.oriented_edge(arc_top_B, False),   # v_pi_top → v0_top  (arc_top_B = v0_top→v_pi_top, rev)
    f.oriented_edge(seam_u0,   False),   # v0_top   → v0_bot
    f.oriented_edge(arc_bot_B, False),   # v0_bot   → v_pi_bot (arc_bot_B = v_pi_bot→v0_bot, rev)
])
faceB = f.advanced_face([f.face_outer_bound(loopB)], cyl_surf)

# ── OPEN_SHELL: seam edges ARE wired into shell/face topology ─────────────────
# seam_u0 is used by both faces (fwd in A, rev in B) — the seam IS the mechanism.
# A unifier seeing both faces on the same CYLINDRICAL_SURFACE must NOT merge them
# because crossing the seam would list seam_u0 twice in the outer wire.
shell = f.open_shell([faceA, faceB])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
