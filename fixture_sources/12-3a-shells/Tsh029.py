"""Tsh029 — Naked / dangling edge in shell (free edges, LOTAR integrity defect).

Catalog claim: An edge that belongs to fewer than two faces inside a shell
intended to be closed (a "naked" edge). Acceptable for an open shell, fatal
for a solid. LOTAR explicitly classifies this as an integrity defect preventing
reliable archive retrieval.

Mechanism IS the shell structure: a CLOSED_SHELL is built from 5 faces instead
of the required 6 — one cap (the top face, z=1) is intentionally omitted from
a unit cube. This leaves 4 edges along the top perimeter each referenced by
only one face (one edge each from the four side faces) — those are the naked
edges. The nakedness IS wired directly into the shell/face topology via the
missing face in the CLOSED_SHELL. OCCT silently accepts; strict receivers must
stitch or reject.

Byte assertions:
  - (no specific byte assertions in catalog for this entry)

Tier-3 assertions:
  - n_edges_total >= 20
  - face[0].surface_type == "plane"
  - face[4].surface_type == "plane"

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh029",
    defect=(
        "CLOSED_SHELL with 5 faces (top z=1 face intentionally omitted from a unit cube); "
        "4 top-perimeter edges each referenced by exactly one face — naked/free edges; "
        "missing face IS wired into shell/face topology as the nakedness; "
        "LOTAR integrity defect; strict receivers must stitch or reject as non-watertight"
    ),
)

# ── Unit cube with top face (z=1) intentionally omitted ───────────────────────
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

# Bottom edges (z=0)
e_b0 = mk_edge(v000, v010, p000,  0, 1, 0)
e_b1 = mk_edge(v010, v110, p010,  1, 0, 0)
e_b2 = mk_edge(v110, v100, p110,  0,-1, 0)
e_b3 = mk_edge(v100, v000, p100, -1, 0, 0)

# Vertical edges (z direction)
e_v00 = mk_edge(v000, v001, p000, 0, 0, 1)
e_v10 = mk_edge(v100, v101, p100, 0, 0, 1)
e_v11 = mk_edge(v110, v111, p110, 0, 0, 1)
e_v01 = mk_edge(v010, v011, p010, 0, 0, 1)

# Top edges (z=1) — these will be NAKED: each referenced by only one side face
e_t0 = mk_edge(v001, v101, p001,  1, 0, 0)   # naked: only Rfront uses it
e_t1 = mk_edge(v101, v111, p101,  0, 1, 0)   # naked: only Rright uses it
e_t2 = mk_edge(v111, v011, p111, -1, 0, 0)   # naked: only Rback uses it
e_t3 = mk_edge(v011, v001, p011,  0,-1, 0)   # naked: only Rleft uses it

# ── Face 1: Bottom z=0, outward normal (0,0,-1) ───────────────────────────────
lp_bot = f.edge_loop([f.oriented_edge(e_b0,True), f.oriented_edge(e_b1,True),
                      f.oriented_edge(e_b2,True), f.oriented_edge(e_b3,True)])
ax_bot = f.axis2_placement_3d(p000, f.direction((0,0,-1)), f.direction((1,0,0)))
face_bot = f.advanced_face([f.face_outer_bound(lp_bot)], f.plane(ax_bot))

# ── Face 2: Front y=0, outward normal (0,-1,0) ────────────────────────────────
lp_frt = f.edge_loop([f.oriented_edge(e_b3,False), f.oriented_edge(e_v10,True),
                      f.oriented_edge(e_t0,True),   f.oriented_edge(e_v00,False)])
ax_frt = f.axis2_placement_3d(p000, f.direction((0,-1,0)), f.direction((1,0,0)))
face_frt = f.advanced_face([f.face_outer_bound(lp_frt)], f.plane(ax_frt))

# ── Face 3: Right x=1, outward normal (1,0,0) ─────────────────────────────────
lp_rgt = f.edge_loop([f.oriented_edge(e_b2,False), f.oriented_edge(e_v11,True),
                      f.oriented_edge(e_t1,True),   f.oriented_edge(e_v10,False)])
ax_rgt = f.axis2_placement_3d(p100, f.direction((1,0,0)), f.direction((0,1,0)))
face_rgt = f.advanced_face([f.face_outer_bound(lp_rgt)], f.plane(ax_rgt))

# ── Face 4: Back y=1, outward normal (0,1,0) ──────────────────────────────────
lp_bk = f.edge_loop([f.oriented_edge(e_b1,False), f.oriented_edge(e_v01,True),
                     f.oriented_edge(e_t2,True),   f.oriented_edge(e_v11,False)])
ax_bk = f.axis2_placement_3d(p010, f.direction((0,1,0)), f.direction((1,0,0)))
face_bk = f.advanced_face([f.face_outer_bound(lp_bk)], f.plane(ax_bk))

# ── Face 5: Left x=0, outward normal (-1,0,0) ─────────────────────────────────
lp_lft = f.edge_loop([f.oriented_edge(e_b0,False), f.oriented_edge(e_v00,True),
                      f.oriented_edge(e_t3,True),   f.oriented_edge(e_v01,False)])
ax_lft = f.axis2_placement_3d(p000, f.direction((-1,0,0)), f.direction((0,1,0)))
face_lft = f.advanced_face([f.face_outer_bound(lp_lft)], f.plane(ax_lft))

# ── DEFECT: 5-face CLOSED_SHELL — top face (z=1) is OMITTED ──────────────────
# Edges e_t0, e_t1, e_t2, e_t3 are each referenced by exactly one face.
# Placing these in a CLOSED_SHELL IS the mechanism: the spec requires every
# edge in a closed shell to be shared by exactly 2 faces. The top perimeter
# edges are naked/free — an integrity defect per LOTAR EN 9300-110.
closed_sh = f.closed_shell([face_bot, face_frt, face_rgt, face_bk, face_lft])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb)
