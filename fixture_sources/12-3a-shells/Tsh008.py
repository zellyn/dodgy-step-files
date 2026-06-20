"""Tsh008 — Mis-oriented faces in shell (Möbius-detect).

Catalog claim: Faces are oriented inconsistently within a closed shell — every
other face is flipped — so adjacent faces' outward normals do not agree along
their shared edges.  The inside/outside classification of the solid is broken;
rendering shows alternating inside-out shading.

Mechanism IS the shell structure: a 6-face CLOSED_SHELL / MANIFOLD_SOLID_BREP
unit-cube is built with alternating faces flipped via same_sense=False on
ADVANCED_FACE, so neighbour normals point opposite directions across every
shared edge boundary.  The orientation inconsistency IS wired into the
shell/face topology — correct-sense and flipped faces alternate in the entity
list.

Byte assertions:
  - contains(b'CLOSED_SHELL')
  - contains(b'MANIFOLD_SOLID_BREP')
  - count_entity_def(b'ADVANCED_FACE') == 6

Tier-3 assertion: n_faces_total == 6
live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh008",
    defect=(
        "MANIFOLD_SOLID_BREP 6-face cube: every other ADVANCED_FACE has same_sense=False "
        "(flipped), so alternating faces point inward; neighbour normals conflict across "
        "shared edge boundaries; Möbius-style orientation inconsistency IS wired into "
        "shell/face topology; strict receivers must flood-fill or reject"
    ),
)

# ── Unit-cube: 6 faces, alternating same_sense to create Möbius-like mismatch ──
# Faces at even positions: same_sense=True (normal outward as built)
# Faces at odd positions: same_sense=False (normal flipped inward) — the defect
# The plane normal directions are all correct geometrically; same_sense inversion
# IS the mechanism that makes adjacent normals conflict.

def pt(x, y, z):
    return f.cartesian_point((float(x), float(y), float(z)))

def line_edge(va, vb, pstart, dx, dy, dz):
    d = f.direction((float(dx), float(dy), float(dz)))
    vec = f.vector(d, 1.0)
    ln = f.line(pstart, vec)
    return f.edge_curve(va, vb, ln)

p000 = pt(0,0,0); p100 = pt(1,0,0); p110 = pt(1,1,0); p010 = pt(0,1,0)
p001 = pt(0,0,1); p101 = pt(1,0,1); p111 = pt(1,1,1); p011 = pt(0,1,1)
v000 = f.vertex_point(p000); v100 = f.vertex_point(p100)
v110 = f.vertex_point(p110); v010 = f.vertex_point(p010)
v001 = f.vertex_point(p001); v101 = f.vertex_point(p101)
v111 = f.vertex_point(p111); v011 = f.vertex_point(p011)

# Bottom z=0, plane normal (0,0,-1) — face 0 (even): same_sense=True (correct)
e_b0 = line_edge(v000, v010, p000,  0, 1, 0)
e_b1 = line_edge(v010, v110, p010,  1, 0, 0)
e_b2 = line_edge(v110, v100, p110,  0,-1, 0)
e_b3 = line_edge(v100, v000, p100, -1, 0, 0)
lp_bot = f.edge_loop([f.oriented_edge(e_b0,True), f.oriented_edge(e_b1,True),
                      f.oriented_edge(e_b2,True), f.oriented_edge(e_b3,True)])
ax_bot = f.axis2_placement_3d(p000, f.direction((0,0,-1)), f.direction((1,0,0)))
# face 0: same_sense=True — outward normal (0,0,-1)
face_bot = f.advanced_face([f.face_outer_bound(lp_bot)], f.plane(ax_bot), same_sense=True)

# Top z=1, plane normal (0,0,1) — face 1 (odd): DEFECT same_sense=False (flipped inward)
e_t0 = line_edge(v001, v101, p001,  1, 0, 0)
e_t1 = line_edge(v101, v111, p101,  0, 1, 0)
e_t2 = line_edge(v111, v011, p111, -1, 0, 0)
e_t3 = line_edge(v011, v001, p011,  0,-1, 0)
lp_top = f.edge_loop([f.oriented_edge(e_t0,True), f.oriented_edge(e_t1,True),
                      f.oriented_edge(e_t2,True), f.oriented_edge(e_t3,True)])
ax_top = f.axis2_placement_3d(p001, f.direction((0,0,1)), f.direction((1,0,0)))
# face 1: same_sense=False — DEFECT: effective normal becomes (0,0,-1), points down (inward)
face_top = f.advanced_face([f.face_outer_bound(lp_top)], f.plane(ax_top), same_sense=False)

# Front y=0, plane normal (0,-1,0) — face 2 (even): same_sense=True (correct)
e_f0 = line_edge(v000, v100, p000,  1, 0, 0)
e_f1 = line_edge(v100, v101, p100,  0, 0, 1)
e_f2 = line_edge(v101, v001, p101, -1, 0, 0)
e_f3 = line_edge(v001, v000, p001,  0, 0,-1)
lp_frt = f.edge_loop([f.oriented_edge(e_f0,True), f.oriented_edge(e_f1,True),
                      f.oriented_edge(e_f2,True), f.oriented_edge(e_f3,True)])
ax_frt = f.axis2_placement_3d(p000, f.direction((0,-1,0)), f.direction((1,0,0)))
# face 2: same_sense=True — outward normal (0,-1,0)
face_frt = f.advanced_face([f.face_outer_bound(lp_frt)], f.plane(ax_frt), same_sense=True)

# Back y=1, plane normal (0,1,0) — face 3 (odd): DEFECT same_sense=False
e_bk0 = line_edge(v010, v011, p010,  0, 0, 1)
e_bk1 = line_edge(v011, v111, p011,  1, 0, 0)
e_bk2 = line_edge(v111, v110, p111,  0, 0,-1)
e_bk3 = line_edge(v110, v010, p110, -1, 0, 0)
lp_bk = f.edge_loop([f.oriented_edge(e_bk0,True), f.oriented_edge(e_bk1,True),
                     f.oriented_edge(e_bk2,True), f.oriented_edge(e_bk3,True)])
ax_bk = f.axis2_placement_3d(p010, f.direction((0,1,0)), f.direction((1,0,0)))
# face 3: same_sense=False — DEFECT: effective normal becomes (0,-1,0), points inward
face_bk = f.advanced_face([f.face_outer_bound(lp_bk)], f.plane(ax_bk), same_sense=False)

# Left x=0, plane normal (-1,0,0) — face 4 (even): same_sense=True (correct)
e_l0 = line_edge(v000, v001, p000,  0, 0, 1)
e_l1 = line_edge(v001, v011, p001,  0, 1, 0)
e_l2 = line_edge(v011, v010, p011,  0, 0,-1)
e_l3 = line_edge(v010, v000, p010,  0,-1, 0)
lp_lft = f.edge_loop([f.oriented_edge(e_l0,True), f.oriented_edge(e_l1,True),
                      f.oriented_edge(e_l2,True), f.oriented_edge(e_l3,True)])
ax_lft = f.axis2_placement_3d(p000, f.direction((-1,0,0)), f.direction((0,1,0)))
# face 4: same_sense=True — outward normal (-1,0,0)
face_lft = f.advanced_face([f.face_outer_bound(lp_lft)], f.plane(ax_lft), same_sense=True)

# Right x=1, plane normal (1,0,0) — face 5 (odd): DEFECT same_sense=False
e_r0 = line_edge(v100, v110, p100,  0, 1, 0)
e_r1 = line_edge(v110, v111, p110,  0, 0, 1)
e_r2 = line_edge(v111, v101, p111,  0,-1, 0)
e_r3 = line_edge(v101, v100, p101,  0, 0,-1)
lp_rgt = f.edge_loop([f.oriented_edge(e_r0,True), f.oriented_edge(e_r1,True),
                      f.oriented_edge(e_r2,True), f.oriented_edge(e_r3,True)])
ax_rgt = f.axis2_placement_3d(p100, f.direction((1,0,0)), f.direction((0,1,0)))
# face 5: same_sense=False — DEFECT: effective normal becomes (-1,0,0), points inward
face_rgt = f.advanced_face([f.face_outer_bound(lp_rgt)], f.plane(ax_rgt), same_sense=False)

# ── DEFECT: alternating same_sense flips ARE wired into the CLOSED_SHELL ──────
# Even faces (bot, frt, lft) point outward; odd faces (top, bk, rgt) point
# inward.  The alternation IS the Möbius-like orientation inconsistency.
closed_sh = f.closed_shell([face_bot, face_top, face_frt, face_bk, face_lft, face_rgt])
msb = f.manifold_solid_brep(closed_sh)

f.add_product_chain(msb)
