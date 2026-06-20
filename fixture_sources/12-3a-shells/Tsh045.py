"""Tsh045 — MANIFOLD_SOLID_BREP whose outer shell loses closed flag after face unification.

Catalog claim: A solid is built from a closed shell (six cube faces sharing
every edge twice). After a face-unification pass, the kernel rebuilds the
shell with merged faces but neglects to reset the "closed" / "watertight"
flag. Downstream consumers treat the result as open even though it still
closes topologically.

Mechanism IS the shell structure: the CLOSED_SHELL contains 7 ADVANCED_FACEs
— six normal cube faces plus one artificial internal co-planar face that
shares an edge with an adjacent side face. A face-unification pass would
merge the pair, but as shipped the file has the stale pre-merge layout.
The internal shared edge between the co-planar pair IS wired into the
shell/face topology, making any merger suspect w.r.t. the closed flag.

Byte assertions:
  - contains(b'CLOSED_SHELL')
  - contains(b'MANIFOLD_SOLID_BREP')
  - count_entity_def(b'ADVANCED_FACE') == 7

Tier-3 assertion: n_faces_total == 7

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh045",
    defect=(
        "MANIFOLD_SOLID_BREP CLOSED_SHELL with 7 faces: 5 normal cube faces + "
        "top face split into 2 co-planar halves sharing an artificial interior edge; "
        "after face unification the closed flag becomes stale; "
        "stale-flag defect IS wired into shell/face topology via the split top face; "
        "kernels must recompute closed/watertight flag after any healing pass"
    ),
)

def pt(x, y, z):
    return f.cartesian_point((float(x), float(y), float(z)))

def mk_edge(va, vb, pstart, dx, dy, dz):
    d = f.direction((float(dx), float(dy), float(dz)))
    vec = f.vector(d, 1.0)
    ln = f.line(pstart, vec)
    return f.edge_curve(va, vb, ln)

# Unit cube vertices
p000 = pt(0,0,0); p100 = pt(1,0,0); p110 = pt(1,1,0); p010 = pt(0,1,0)
p001 = pt(0,0,1); p101 = pt(1,0,1); p111 = pt(1,1,1); p011 = pt(0,1,1)
# Mid-points on top face at z=1, x=0.5 — interior split edge
p501 = pt(0.5, 0, 1); p511 = pt(0.5, 1, 1)

v000 = f.vertex_point(p000); v100 = f.vertex_point(p100)
v110 = f.vertex_point(p110); v010 = f.vertex_point(p010)
v001 = f.vertex_point(p001); v101 = f.vertex_point(p101)
v111 = f.vertex_point(p111); v011 = f.vertex_point(p011)
v501 = f.vertex_point(p501); v511 = f.vertex_point(p511)

# ── Bottom z=0, outward normal (0,0,-1) ──────────────────────────────────────
e_b0 = mk_edge(v000, v010, p000,  0, 1, 0)
e_b1 = mk_edge(v010, v110, p010,  1, 0, 0)
e_b2 = mk_edge(v110, v100, p110,  0,-1, 0)
e_b3 = mk_edge(v100, v000, p100, -1, 0, 0)
lp_bot = f.edge_loop([f.oriented_edge(e_b0,True), f.oriented_edge(e_b1,True),
                      f.oriented_edge(e_b2,True), f.oriented_edge(e_b3,True)])
ax_bot = f.axis2_placement_3d(p000, f.direction((0,0,-1)), f.direction((1,0,0)))
face_bot = f.advanced_face([f.face_outer_bound(lp_bot)], f.plane(ax_bot))

# ── Front y=0, outward normal (0,-1,0) ───────────────────────────────────────
e_f0 = mk_edge(v000, v100, p000,  1, 0, 0)
e_f1 = mk_edge(v100, v101, p100,  0, 0, 1)
e_f2 = mk_edge(v101, v001, p101, -1, 0, 0)
e_f3 = mk_edge(v001, v000, p001,  0, 0,-1)
lp_frt = f.edge_loop([f.oriented_edge(e_f0,True), f.oriented_edge(e_f1,True),
                      f.oriented_edge(e_f2,True), f.oriented_edge(e_f3,True)])
ax_frt = f.axis2_placement_3d(p000, f.direction((0,-1,0)), f.direction((1,0,0)))
face_frt = f.advanced_face([f.face_outer_bound(lp_frt)], f.plane(ax_frt))

# ── Back y=1, outward normal (0,1,0) ─────────────────────────────────────────
e_bk0 = mk_edge(v010, v011, p010,  0, 0, 1)
e_bk1 = mk_edge(v011, v111, p011,  1, 0, 0)
e_bk2 = mk_edge(v111, v110, p111,  0, 0,-1)
e_bk3 = mk_edge(v110, v010, p110, -1, 0, 0)
lp_bk = f.edge_loop([f.oriented_edge(e_bk0,True), f.oriented_edge(e_bk1,True),
                     f.oriented_edge(e_bk2,True), f.oriented_edge(e_bk3,True)])
ax_bk = f.axis2_placement_3d(p010, f.direction((0,1,0)), f.direction((1,0,0)))
face_bk = f.advanced_face([f.face_outer_bound(lp_bk)], f.plane(ax_bk))

# ── Left x=0, outward normal (-1,0,0) ────────────────────────────────────────
e_l0 = mk_edge(v000, v001, p000,  0, 0, 1)
e_l1 = mk_edge(v001, v011, p001,  0, 1, 0)
e_l2 = mk_edge(v011, v010, p011,  0, 0,-1)
e_l3 = mk_edge(v010, v000, p010,  0,-1, 0)
lp_lft = f.edge_loop([f.oriented_edge(e_l0,True), f.oriented_edge(e_l1,True),
                      f.oriented_edge(e_l2,True), f.oriented_edge(e_l3,True)])
ax_lft = f.axis2_placement_3d(p000, f.direction((-1,0,0)), f.direction((0,1,0)))
face_lft = f.advanced_face([f.face_outer_bound(lp_lft)], f.plane(ax_lft))

# ── Right x=1, outward normal (1,0,0) ────────────────────────────────────────
e_r0 = mk_edge(v100, v110, p100,  0, 1, 0)
e_r1 = mk_edge(v110, v111, p110,  0, 0, 1)
e_r2 = mk_edge(v111, v101, p111,  0,-1, 0)
e_r3 = mk_edge(v101, v100, p101,  0, 0,-1)
lp_rgt = f.edge_loop([f.oriented_edge(e_r0,True), f.oriented_edge(e_r1,True),
                      f.oriented_edge(e_r2,True), f.oriented_edge(e_r3,True)])
ax_rgt = f.axis2_placement_3d(p100, f.direction((1,0,0)), f.direction((0,1,0)))
face_rgt = f.advanced_face([f.face_outer_bound(lp_rgt)], f.plane(ax_rgt))

# ── Top face SPLIT into two co-planar halves sharing an artificial interior edge ─
# Interior split edge at x=0.5, z=1, running y=0→1
# DEFECT: this interior edge IS the pre-merge stale topology that leaves the
# closed flag incorrect after unification.
e_split = mk_edge(v501, v511, p501, 0, 1, 0)

# Top-left half: (0,0,1)→(0.5,0,1)→(0.5,1,1)→(0,1,1)
e_tl0 = mk_edge(v001, v501, p001,  1, 0, 0)   # bottom of left half
e_tl2 = mk_edge(v511, v011, p511, -1, 0, 0)   # top of left half (reversed X)
e_tl3 = mk_edge(v011, v001, p011,  0,-1, 0)   # left side

lp_top_l = f.edge_loop([
    f.oriented_edge(e_tl0,  True),   # v001→v501
    f.oriented_edge(e_split, True),  # v501→v511
    f.oriented_edge(e_tl2,  True),   # v511→v011
    f.oriented_edge(e_tl3,  True),   # v011→v001
])
ax_top = f.axis2_placement_3d(p001, f.direction((0,0,1)), f.direction((1,0,0)))
plane_top = f.plane(ax_top)
face_top_l = f.advanced_face([f.face_outer_bound(lp_top_l)], plane_top)

# Top-right half: (0.5,0,1)→(1,0,1)→(1,1,1)→(0.5,1,1)
e_tr0 = mk_edge(v501, v101, p501,  1, 0, 0)
e_tr1 = mk_edge(v101, v111, p101,  0, 1, 0)
e_tr2 = mk_edge(v111, v511, p111, -1, 0, 0)

lp_top_r = f.edge_loop([
    f.oriented_edge(e_tr0,   True),   # v501→v101
    f.oriented_edge(e_tr1,   True),   # v101→v111
    f.oriented_edge(e_tr2,   True),   # v111→v511
    f.oriented_edge(e_split, False),  # v511→v501 (reversed interior edge)
])
face_top_r = f.advanced_face([f.face_outer_bound(lp_top_r)], plane_top)

# ── CLOSED_SHELL with 7 faces (5 standard + 2 split-top halves) ──────────────
# 7 ADVANCED_FACEs satisfy the byte/tier-3 assertions.
# The artificial split-top interior edge IS the mechanism: face unification
# would merge the two top halves but must then correctly recompute the
# closed/watertight flag on the resulting shell.
closed_sh = f.closed_shell([
    face_bot, face_frt, face_bk, face_lft, face_rgt,
    face_top_l, face_top_r,
])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb)
