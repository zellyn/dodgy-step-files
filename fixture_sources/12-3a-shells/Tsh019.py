"""Tsh019 — Non-manifold edge (>=3 incident faces) in shell or solid.

Catalog claim: An edge shared by three or more faces; surface is not locally
homeomorphic to a disk along the edge. Two cubes sharing one common edge (4
faces meet at one edge) emitted as one MANIFOLD_SOLID_BREP is the canonical
case. Many translators silently smash these into one CLOSED_SHELL.

Mechanism IS the shell structure: two unit-cube CLOSED_SHELLs are merged into
one MANIFOLD_SOLID_BREP. The shared edge between them (the common edge along
x=1,y=0 to x=1,y=0,z=1) appears in 4 FACE_BOUND chains — two from the right
face of the left cube and two from the left face of the right cube. The
non-manifold edge referencing is IS wired directly into the shell/face topology
via the merged CLOSED_SHELL's edge references. OCCT silently accepts; strict
receivers must reject or reclassify as non_manifold_surface_shape_representation.

Byte assertions:
  - (no specific byte assertions in catalog)

Tier-3 assertions:
  - n_edges_total >= 12
  - face[0].surface_type == "plane"
  - face[2].surface_type == "plane"

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh019",
    defect=(
        "MANIFOLD_SOLID_BREP whose CLOSED_SHELL contains an EDGE_CURVE shared by "
        "4 FACE_BOUND chains (two cubes joined at a common edge); non-manifold edge "
        "IS wired into shell/face topology; OCCT silently accepts; strict receivers "
        "must reject or reclassify"
    ),
)

# ── Build two cubes sharing one common edge ───────────────────────────────────
# Left cube:  [0,1] x [0,1] x [0,1]   — right edge: x=1, from (1,0,0)→(1,0,1)
# Right cube: [1,2] x [0,1] x [0,1]   — left edge:  x=1, from (1,0,0)→(1,0,1)
# The shared edge (at y=0, x=1) appears in:
#   left cube's  front face  (y=0): one of its 4 edges
#   left cube's  right face  (x=1): one of its 4 edges
#   right cube's front face  (y=0): one of its 4 edges
#   right cube's left face   (x=1): one of its 4 edges
# → 4 incident face edges on one EDGE_CURVE → non-manifold.

def pt(x, y, z):
    return f.cartesian_point((float(x), float(y), float(z)))

def mk_edge(va, vb, pstart, dx, dy, dz):
    d = f.direction((float(dx), float(dy), float(dz)))
    vec = f.vector(d, 1.0)
    ln = f.line(pstart, vec)
    return f.edge_curve(va, vb, ln)

# ── Shared edge vertices (at x=1, y=0) ────────────────────────────────────────
p_s0 = pt(1, 0, 0)
p_s1 = pt(1, 0, 1)
v_s0 = f.vertex_point(p_s0)
v_s1 = f.vertex_point(p_s1)
# The shared EDGE_CURVE — referenced by 4 face loops below
ec_shared = mk_edge(v_s0, v_s1, p_s0, 0, 0, 1)

# ── Left cube [0,1]x[0,1]x[0,1] ─────────────────────────────────────────────
# Vertices (excluding the shared edge which uses v_s0/v_s1)
Lp000 = pt(0,0,0); Lp010 = pt(0,1,0); Lp110 = pt(1,1,0); Lp100 = p_s0
Lp001 = pt(0,0,1); Lp011 = pt(0,1,1); Lp111 = pt(1,1,1); Lp101 = p_s1
Lv000 = f.vertex_point(Lp000); Lv010 = f.vertex_point(Lp010)
Lv110 = f.vertex_point(Lp110); Lv001 = f.vertex_point(Lp001)
Lv011 = f.vertex_point(Lp011); Lv111 = f.vertex_point(Lp111)

# Bottom (z=0): 000→010→110→100
Le_b0 = mk_edge(Lv000, Lv010, Lp000,  0, 1, 0)
Le_b1 = mk_edge(Lv010, Lv110, Lp010,  1, 0, 0)
Le_b2 = mk_edge(Lv110, v_s0,  Lp110,  0,-1, 0)
Le_b3 = mk_edge(v_s0,  Lv000, p_s0,  -1, 0, 0)
lp_Lbot = f.edge_loop([f.oriented_edge(Le_b0,True), f.oriented_edge(Le_b1,True),
                       f.oriented_edge(Le_b2,True), f.oriented_edge(Le_b3,True)])
ax = f.axis2_placement_3d(Lp000, f.direction((0,0,-1)), f.direction((1,0,0)))
Lface_bot = f.advanced_face([f.face_outer_bound(lp_Lbot)], f.plane(ax))

# Top (z=1): 001→101→111→011
Le_t0 = mk_edge(Lv001, v_s1,  Lp001,  1, 0, 0)
Le_t1 = mk_edge(v_s1,  Lv111, p_s1,   0, 1, 0)
Le_t2 = mk_edge(Lv111, Lv011, Lp111, -1, 0, 0)
Le_t3 = mk_edge(Lv011, Lv001, Lp011,  0,-1, 0)
lp_Ltop = f.edge_loop([f.oriented_edge(Le_t0,True), f.oriented_edge(Le_t1,True),
                       f.oriented_edge(Le_t2,True), f.oriented_edge(Le_t3,True)])
ax = f.axis2_placement_3d(Lp001, f.direction((0,0,1)), f.direction((1,0,0)))
Lface_top = f.advanced_face([f.face_outer_bound(lp_Ltop)], f.plane(ax))

# Front y=0: 000→100→101→001  (uses ec_shared at 100→101)
Le_f0 = mk_edge(Lv000, v_s0, Lp000,  1, 0, 0)
Le_f2 = mk_edge(v_s1,  Lv001, p_s1, -1, 0, 0)
Le_f3 = mk_edge(Lv001, Lv000, Lp001,  0, 0,-1)
lp_Lfrt = f.edge_loop([f.oriented_edge(Le_f0,True), f.oriented_edge(ec_shared,True),
                       f.oriented_edge(Le_f2,True), f.oriented_edge(Le_f3,True)])
ax = f.axis2_placement_3d(Lp000, f.direction((0,-1,0)), f.direction((1,0,0)))
Lface_frt = f.advanced_face([f.face_outer_bound(lp_Lfrt)], f.plane(ax))

# Back y=1: 010→011→111→110
Le_bk0 = mk_edge(Lv010, Lv011, Lp010,  0, 0, 1)
Le_bk1 = mk_edge(Lv011, Lv111, Lp011,  1, 0, 0)
Le_bk2 = mk_edge(Lv111, Lv110, Lp111,  0, 0,-1)
Le_bk3 = mk_edge(Lv110, Lv010, Lp110, -1, 0, 0)
lp_Lbk = f.edge_loop([f.oriented_edge(Le_bk0,True), f.oriented_edge(Le_bk1,True),
                      f.oriented_edge(Le_bk2,True), f.oriented_edge(Le_bk3,True)])
ax = f.axis2_placement_3d(Lp010, f.direction((0,1,0)), f.direction((1,0,0)))
Lface_bk = f.advanced_face([f.face_outer_bound(lp_Lbk)], f.plane(ax))

# Left x=0: 000→001→011→010
Le_l0 = mk_edge(Lv000, Lv001, Lp000,  0, 0, 1)
Le_l1 = mk_edge(Lv001, Lv011, Lp001,  0, 1, 0)
Le_l2 = mk_edge(Lv011, Lv010, Lp011,  0, 0,-1)
Le_l3 = mk_edge(Lv010, Lv000, Lp010,  0,-1, 0)
lp_Llft = f.edge_loop([f.oriented_edge(Le_l0,True), f.oriented_edge(Le_l1,True),
                       f.oriented_edge(Le_l2,True), f.oriented_edge(Le_l3,True)])
ax = f.axis2_placement_3d(Lp000, f.direction((-1,0,0)), f.direction((0,1,0)))
Lface_lft = f.advanced_face([f.face_outer_bound(lp_Llft)], f.plane(ax))

# Right x=1: 100→110→111→101  (uses ec_shared at 100→101 — 2nd incident face on right side)
Le_r0 = mk_edge(v_s0,  Lv110, p_s0,   0, 1, 0)
Le_r1 = mk_edge(Lv110, Lv111, Lp110,  0, 0, 1)
Le_r2 = mk_edge(Lv111, v_s1,  Lp111,  0,-1, 0)
lp_Lrgt = f.edge_loop([f.oriented_edge(Le_r0,True), f.oriented_edge(Le_r1,True),
                       f.oriented_edge(Le_r2,True), f.oriented_edge(ec_shared,False)])
ax = f.axis2_placement_3d(p_s0, f.direction((1,0,0)), f.direction((0,1,0)))
Lface_rgt = f.advanced_face([f.face_outer_bound(lp_Lrgt)], f.plane(ax))

# ── Right cube [1,2]x[0,1]x[0,1] ────────────────────────────────────────────
Rp200 = pt(2,0,0); Rp210 = pt(2,1,0)
Rp110 = pt(1,1,0); Rp201 = pt(2,0,1); Rp211 = pt(2,1,1); Rp111 = pt(1,1,1)
Rv200 = f.vertex_point(Rp200); Rv210 = f.vertex_point(Rp210)
Rv110 = f.vertex_point(Rp110); Rv201 = f.vertex_point(Rp201)
Rv211 = f.vertex_point(Rp211); Rv111 = f.vertex_point(Rp111)

# Bottom z=0: s0→200→210→110
Re_b0 = mk_edge(v_s0,  Rv200, p_s0,   1, 0, 0)
Re_b1 = mk_edge(Rv200, Rv210, Rp200,  0, 1, 0)
Re_b2 = mk_edge(Rv210, Rv110, Rp210, -1, 0, 0)
Re_b3 = mk_edge(Rv110, v_s0,  Rp110,  0,-1, 0)
lp_Rbot = f.edge_loop([f.oriented_edge(Re_b0,True), f.oriented_edge(Re_b1,True),
                       f.oriented_edge(Re_b2,True), f.oriented_edge(Re_b3,True)])
ax = f.axis2_placement_3d(p_s0, f.direction((0,0,-1)), f.direction((1,0,0)))
Rface_bot = f.advanced_face([f.face_outer_bound(lp_Rbot)], f.plane(ax))

# Top z=1: s1→201→211→111
Re_t0 = mk_edge(v_s1,  Rv201, p_s1,   1, 0, 0)
Re_t1 = mk_edge(Rv201, Rv211, Rp201,  0, 1, 0)
Re_t2 = mk_edge(Rv211, Rv111, Rp211, -1, 0, 0)
Re_t3 = mk_edge(Rv111, v_s1,  Rp111,  0,-1, 0)
lp_Rtop = f.edge_loop([f.oriented_edge(Re_t0,True), f.oriented_edge(Re_t1,True),
                       f.oriented_edge(Re_t2,True), f.oriented_edge(Re_t3,True)])
ax = f.axis2_placement_3d(p_s1, f.direction((0,0,1)), f.direction((1,0,0)))
Rface_top = f.advanced_face([f.face_outer_bound(lp_Rtop)], f.plane(ax))

# Front y=0: s0→200→201→s1  (3rd incident use of ec_shared!)
Re_f0 = mk_edge(v_s0,  Rv200, p_s0,   1, 0, 0)
Re_f1 = mk_edge(Rv200, Rv201, Rp200,  0, 0, 1)
Re_f2 = mk_edge(Rv201, v_s1,  Rp201, -1, 0, 0)
lp_Rfrt = f.edge_loop([f.oriented_edge(Re_f0,True), f.oriented_edge(Re_f1,True),
                       f.oriented_edge(Re_f2,True), f.oriented_edge(ec_shared,False)])
ax = f.axis2_placement_3d(p_s0, f.direction((0,-1,0)), f.direction((1,0,0)))
Rface_frt = f.advanced_face([f.face_outer_bound(lp_Rfrt)], f.plane(ax))

# Back y=1: 110→111→211→210
Re_bk0 = mk_edge(Rv110, Rv111, Rp110,  0, 0, 1)
Re_bk1 = mk_edge(Rv111, Rv211, Rp111,  1, 0, 0)
Re_bk2 = mk_edge(Rv211, Rv210, Rp211,  0, 0,-1)
Re_bk3 = mk_edge(Rv210, Rv110, Rp210, -1, 0, 0)
lp_Rbk = f.edge_loop([f.oriented_edge(Re_bk0,True), f.oriented_edge(Re_bk1,True),
                      f.oriented_edge(Re_bk2,True), f.oriented_edge(Re_bk3,True)])
ax = f.axis2_placement_3d(Rp110, f.direction((0,1,0)), f.direction((1,0,0)))
Rface_bk = f.advanced_face([f.face_outer_bound(lp_Rbk)], f.plane(ax))

# Left x=1: s0→s1→111→110  (4th incident use of ec_shared!)
Re_l1 = mk_edge(v_s1,  Rv111, p_s1,   0, 1, 0)
Re_l2 = mk_edge(Rv111, Rv110, Rp111,  0, 0,-1)
Re_l3 = mk_edge(Rv110, v_s0,  Rp110,  0,-1, 0)
lp_Rlft = f.edge_loop([f.oriented_edge(ec_shared,True), f.oriented_edge(Re_l1,True),
                       f.oriented_edge(Re_l2,True), f.oriented_edge(Re_l3,True)])
ax = f.axis2_placement_3d(p_s0, f.direction((-1,0,0)), f.direction((0,1,0)))
Rface_lft = f.advanced_face([f.face_outer_bound(lp_Rlft)], f.plane(ax))

# Right x=2: 200→210→211→201
Re_r0 = mk_edge(Rv200, Rv210, Rp200,  0, 1, 0)
Re_r1 = mk_edge(Rv210, Rv211, Rp210,  0, 0, 1)
Re_r2 = mk_edge(Rv211, Rv201, Rp211,  0,-1, 0)
Re_r3 = mk_edge(Rv201, Rv200, Rp201,  0, 0,-1)
lp_Rrgt = f.edge_loop([f.oriented_edge(Re_r0,True), f.oriented_edge(Re_r1,True),
                       f.oriented_edge(Re_r2,True), f.oriented_edge(Re_r3,True)])
ax = f.axis2_placement_3d(Rp200, f.direction((1,0,0)), f.direction((0,1,0)))
Rface_rgt = f.advanced_face([f.face_outer_bound(lp_Rrgt)], f.plane(ax))

# ── DEFECT: merge both cubes' faces into a single CLOSED_SHELL ────────────────
# ec_shared is referenced by 4 face loops: Lface_frt, Lface_rgt, Rface_frt, Rface_lft
# → non-manifold T-junction edge IS wired into the shell/face topology
all_faces = [
    Lface_bot, Lface_top, Lface_frt, Lface_bk, Lface_lft, Lface_rgt,
    Rface_bot, Rface_top, Rface_frt, Rface_bk, Rface_lft, Rface_rgt,
]
merged_shell = f.closed_shell(all_faces)
msb = f.manifold_solid_brep(merged_shell)
f.add_product_chain(msb)
