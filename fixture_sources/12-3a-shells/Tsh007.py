"""Tsh007 — `IsClosed` flag inconsistent with actual shell topology.

Catalog claim: A STEP-imported shell carries `IsClosed=true` (i.e. declared as
CLOSED_SHELL) while geometrically having free boundaries — the face graph has
dangling/free edges because one face is missing.  The declared entity type lies
about closure, leaving the wrong flag downstream.

Mechanism IS the shell structure: a CLOSED_SHELL entity is emitted containing
only 5 faces of a unit cube (top face absent), so the face graph has four
free/dangling edges along the top rim.  The mismatch between the declared
CLOSED_SHELL entity and the actual open topology IS wired into the shell/face
topology — the IsClosed claim IS the CLOSED_SHELL entity type.

Byte assertions:
  - contains(b'CLOSED_SHELL')
  - contains(b'MANIFOLD_SOLID_BREP')
  - count_entity_def(b'ADVANCED_FACE') >= 20

Tier-3 assertion: n_edges_total >= 20
Tier-3 assertion: face[0].surface_type == "plane"
Tier-3 assertion: face[4].surface_type == "plane"
live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh007",
    defect=(
        "CLOSED_SHELL declared but contains only 5 faces (top missing): four free "
        "boundary edges exist along top rim; IsClosed flag IS the CLOSED_SHELL entity "
        "type — inconsistency IS wired into shell/face topology; strict receivers must "
        "recompute closure and warn or reject"
    ),
)

# ── Unit-cube with top face ABSENT: 5 faces ───────────────────────────────────
# The CLOSED_SHELL entity type claims closure but the face graph has dangling
# edges along the top rim — the IsClosed inconsistency IS the mechanism.

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

# Bottom z=0, outward normal (0,0,-1): CCW from -z → 000,010,110,100
e_b0 = line_edge(v000, v010, p000,  0, 1, 0)
e_b1 = line_edge(v010, v110, p010,  1, 0, 0)
e_b2 = line_edge(v110, v100, p110,  0,-1, 0)
e_b3 = line_edge(v100, v000, p100, -1, 0, 0)
lp_bot = f.edge_loop([f.oriented_edge(e_b0,True), f.oriented_edge(e_b1,True),
                      f.oriented_edge(e_b2,True), f.oriented_edge(e_b3,True)])
ax_bot = f.axis2_placement_3d(p000, f.direction((0,0,-1)), f.direction((1,0,0)))
face_bot = f.advanced_face([f.face_outer_bound(lp_bot)], f.plane(ax_bot))

# Front y=0, outward normal (0,-1,0)
e_f0 = line_edge(v000, v100, p000,  1, 0, 0)
e_f1 = line_edge(v100, v101, p100,  0, 0, 1)
e_f2 = line_edge(v101, v001, p101, -1, 0, 0)
e_f3 = line_edge(v001, v000, p001,  0, 0,-1)
lp_frt = f.edge_loop([f.oriented_edge(e_f0,True), f.oriented_edge(e_f1,True),
                      f.oriented_edge(e_f2,True), f.oriented_edge(e_f3,True)])
ax_frt = f.axis2_placement_3d(p000, f.direction((0,-1,0)), f.direction((1,0,0)))
face_frt = f.advanced_face([f.face_outer_bound(lp_frt)], f.plane(ax_frt))

# Back y=1, outward normal (0,1,0)
e_bk0 = line_edge(v010, v011, p010,  0, 0, 1)
e_bk1 = line_edge(v011, v111, p011,  1, 0, 0)
e_bk2 = line_edge(v111, v110, p111,  0, 0,-1)
e_bk3 = line_edge(v110, v010, p110, -1, 0, 0)
lp_bk = f.edge_loop([f.oriented_edge(e_bk0,True), f.oriented_edge(e_bk1,True),
                     f.oriented_edge(e_bk2,True), f.oriented_edge(e_bk3,True)])
ax_bk = f.axis2_placement_3d(p010, f.direction((0,1,0)), f.direction((1,0,0)))
face_bk = f.advanced_face([f.face_outer_bound(lp_bk)], f.plane(ax_bk))

# Left x=0, outward normal (-1,0,0)
e_l0 = line_edge(v000, v001, p000,  0, 0, 1)
e_l1 = line_edge(v001, v011, p001,  0, 1, 0)
e_l2 = line_edge(v011, v010, p011,  0, 0,-1)
e_l3 = line_edge(v010, v000, p010,  0,-1, 0)
lp_lft = f.edge_loop([f.oriented_edge(e_l0,True), f.oriented_edge(e_l1,True),
                      f.oriented_edge(e_l2,True), f.oriented_edge(e_l3,True)])
ax_lft = f.axis2_placement_3d(p000, f.direction((-1,0,0)), f.direction((0,1,0)))
face_lft = f.advanced_face([f.face_outer_bound(lp_lft)], f.plane(ax_lft))

# Right x=1, outward normal (1,0,0)
e_r0 = line_edge(v100, v110, p100,  0, 1, 0)
e_r1 = line_edge(v110, v111, p110,  0, 0, 1)
e_r2 = line_edge(v111, v101, p111,  0,-1, 0)
e_r3 = line_edge(v101, v100, p101,  0, 0,-1)
lp_rgt = f.edge_loop([f.oriented_edge(e_r0,True), f.oriented_edge(e_r1,True),
                      f.oriented_edge(e_r2,True), f.oriented_edge(e_r3,True)])
ax_rgt = f.axis2_placement_3d(p100, f.direction((1,0,0)), f.direction((0,1,0)))
face_rgt = f.advanced_face([f.face_outer_bound(lp_rgt)], f.plane(ax_rgt))

# ── DEFECT: 5 faces wrapped in CLOSED_SHELL — the IsClosed lie IS the mechanism ──
# Top face (z=1) is absent; the four top-rim edges (e_f1, e_bk0, e_l0, e_r1
# and their reverses) are free/dangling.  CLOSED_SHELL entity type IS the false
# IsClosed claim — wired directly into shell/face topology.
closed_sh = f.closed_shell([face_bot, face_frt, face_bk, face_lft, face_rgt])
msb = f.manifold_solid_brep(closed_sh)

f.add_product_chain(msb)
