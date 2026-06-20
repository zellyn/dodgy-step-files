"""Tsh026 — Coincident / duplicate ADVANCED_FACE instances in CLOSED_SHELL.

Catalog claim: A CLOSED_SHELL contains two ADVANCED_FACE instances that are
geometrically coincident; the same face appears twice on the same supporting
PLANE with identical EDGE_LOOP geometry, producing a coincident layered face.
Typical signature: a shell with N+1 faces where the cube/box should have N, the
duplicated face being a flat cap stored under two different ADVANCED_FACE IDs.

Mechanism IS the shell structure: a 7-face CLOSED_SHELL is built where the
bottom face (z=0) is duplicated — two distinct ADVANCED_FACE entities (different
entity IDs) on the same PLANE with geometrically identical EDGE_LOOPs. Both are
attached to the same CLOSED_SHELL. The duplicate IS wired directly into the
shell/face topology. OCCT silently accepts; strict receivers must detect
coincidence and drop one.

Byte assertions:
  - (no specific byte assertions in catalog for this entry)

Tier-3 assertions:
  - n_edges_total >= 28
  - face[0].surface_type == "plane"
  - face[5].surface_type == "plane"

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh026",
    defect=(
        "7-face CLOSED_SHELL: bottom face (z=0) appears twice as two distinct "
        "ADVANCED_FACE entities on the same PLANE with identical EDGE_LOOP geometry; "
        "duplicate face IS wired into shell/face topology; OCCT silently accepts; "
        "strict receivers must detect coincidence and drop one"
    ),
)

# ── Unit cube: 6 faces + 1 duplicate bottom ───────────────────────────────────
def pt(x, y, z):
    return f.cartesian_point((float(x), float(y), float(z)))

def mk_edge(va, vb, pstart, dx, dy, dz):
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

# Bottom z=0 — primary copy
e_b0 = mk_edge(v000, v010, p000,  0, 1, 0)
e_b1 = mk_edge(v010, v110, p010,  1, 0, 0)
e_b2 = mk_edge(v110, v100, p110,  0,-1, 0)
e_b3 = mk_edge(v100, v000, p100, -1, 0, 0)
lp_bot = f.edge_loop([f.oriented_edge(e_b0,True), f.oriented_edge(e_b1,True),
                      f.oriented_edge(e_b2,True), f.oriented_edge(e_b3,True)])
ax_bot = f.axis2_placement_3d(p000, f.direction((0,0,-1)), f.direction((1,0,0)))
face_bot = f.advanced_face([f.face_outer_bound(lp_bot)], f.plane(ax_bot))

# Top z=1
e_t0 = mk_edge(v001, v101, p001,  1, 0, 0)
e_t1 = mk_edge(v101, v111, p101,  0, 1, 0)
e_t2 = mk_edge(v111, v011, p111, -1, 0, 0)
e_t3 = mk_edge(v011, v001, p011,  0,-1, 0)
lp_top = f.edge_loop([f.oriented_edge(e_t0,True), f.oriented_edge(e_t1,True),
                      f.oriented_edge(e_t2,True), f.oriented_edge(e_t3,True)])
ax_top = f.axis2_placement_3d(p001, f.direction((0,0,1)), f.direction((1,0,0)))
face_top = f.advanced_face([f.face_outer_bound(lp_top)], f.plane(ax_top))

# Front y=0
e_f0 = mk_edge(v000, v100, p000,  1, 0, 0)
e_f1 = mk_edge(v100, v101, p100,  0, 0, 1)
e_f2 = mk_edge(v101, v001, p101, -1, 0, 0)
e_f3 = mk_edge(v001, v000, p001,  0, 0,-1)
lp_frt = f.edge_loop([f.oriented_edge(e_f0,True), f.oriented_edge(e_f1,True),
                      f.oriented_edge(e_f2,True), f.oriented_edge(e_f3,True)])
ax_frt = f.axis2_placement_3d(p000, f.direction((0,-1,0)), f.direction((1,0,0)))
face_frt = f.advanced_face([f.face_outer_bound(lp_frt)], f.plane(ax_frt))

# Back y=1
e_bk0 = mk_edge(v010, v011, p010,  0, 0, 1)
e_bk1 = mk_edge(v011, v111, p011,  1, 0, 0)
e_bk2 = mk_edge(v111, v110, p111,  0, 0,-1)
e_bk3 = mk_edge(v110, v010, p110, -1, 0, 0)
lp_bk = f.edge_loop([f.oriented_edge(e_bk0,True), f.oriented_edge(e_bk1,True),
                     f.oriented_edge(e_bk2,True), f.oriented_edge(e_bk3,True)])
ax_bk = f.axis2_placement_3d(p010, f.direction((0,1,0)), f.direction((1,0,0)))
face_bk = f.advanced_face([f.face_outer_bound(lp_bk)], f.plane(ax_bk))

# Left x=0
e_l0 = mk_edge(v000, v001, p000,  0, 0, 1)
e_l1 = mk_edge(v001, v011, p001,  0, 1, 0)
e_l2 = mk_edge(v011, v010, p011,  0, 0,-1)
e_l3 = mk_edge(v010, v000, p010,  0,-1, 0)
lp_lft = f.edge_loop([f.oriented_edge(e_l0,True), f.oriented_edge(e_l1,True),
                      f.oriented_edge(e_l2,True), f.oriented_edge(e_l3,True)])
ax_lft = f.axis2_placement_3d(p000, f.direction((-1,0,0)), f.direction((0,1,0)))
face_lft = f.advanced_face([f.face_outer_bound(lp_lft)], f.plane(ax_lft))

# Right x=1
e_r0 = mk_edge(v100, v110, p100,  0, 1, 0)
e_r1 = mk_edge(v110, v111, p110,  0, 0, 1)
e_r2 = mk_edge(v111, v101, p111,  0,-1, 0)
e_r3 = mk_edge(v101, v100, p101,  0, 0,-1)
lp_rgt = f.edge_loop([f.oriented_edge(e_r0,True), f.oriented_edge(e_r1,True),
                      f.oriented_edge(e_r2,True), f.oriented_edge(e_r3,True)])
ax_rgt = f.axis2_placement_3d(p100, f.direction((1,0,0)), f.direction((0,1,0)))
face_rgt = f.advanced_face([f.face_outer_bound(lp_rgt)], f.plane(ax_rgt))

# ── DEFECT: duplicate bottom face (z=0) with fresh entity IDs ─────────────────
# Same PLANE, same geometry as face_bot but distinct entity IDs.
# Separate points, edges, loop, placement, plane entity objects → distinct IDs.
dp000 = pt(0,0,0); dp100 = pt(1,0,0); dp110 = pt(1,1,0); dp010 = pt(0,1,0)
dv000 = f.vertex_point(dp000); dv100 = f.vertex_point(dp100)
dv110 = f.vertex_point(dp110); dv010 = f.vertex_point(dp010)
de_b0 = mk_edge(dv000, dv010, dp000,  0, 1, 0)
de_b1 = mk_edge(dv010, dv110, dp010,  1, 0, 0)
de_b2 = mk_edge(dv110, dv100, dp110,  0,-1, 0)
de_b3 = mk_edge(dv100, dv000, dp100, -1, 0, 0)
dlp_bot = f.edge_loop([f.oriented_edge(de_b0,True), f.oriented_edge(de_b1,True),
                       f.oriented_edge(de_b2,True), f.oriented_edge(de_b3,True)])
dax_bot = f.axis2_placement_3d(dp000, f.direction((0,0,-1)), f.direction((1,0,0)))
face_bot_dup = f.advanced_face([f.face_outer_bound(dlp_bot)], f.plane(dax_bot))

# ── 7-face CLOSED_SHELL: 6 normal + 1 duplicate bottom IS the mechanism ───────
closed_sh = f.closed_shell([face_bot, face_top, face_frt, face_bk, face_lft, face_rgt,
                             face_bot_dup])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb)
