"""Tsh018 — Volume orientation mismatch between LastShape() and parent solid.

Catalog claim: After BRepPrimAPI_MakeRevol, the closing face returned by
LastShape() is oriented FORWARD, but the same face inside the resulting solid
is REVERSED. Code using LastShape() to drive a follow-up operation sees an
inconsistent normal direction.

Mechanism IS the shell structure: a 3-face wedge MANIFOLD_SOLID_BREP is built
where the closing triangular cap (the "last" face, analogous to LastShape())
has same_sense=True (FORWARD). For a correctly-oriented closed solid the top
cap should be REVERSED (same_sense=False). The wrong orientation IS wired into
the shell/face topology — the mismatch between the cap face orientation and the
solid's outward convention IS the mechanism. OCCT silently accepts; strict
receivers must heal to make orientations consistent.

Byte assertions:
  - contains(b'CLOSED_SHELL')
  - contains(b'MANIFOLD_SOLID_BREP')
  - count_entity_def(b'ADVANCED_FACE') == 3

Tier-3 assertion: n_faces_total == 3
live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh018",
    defect=(
        "3-face wedge MANIFOLD_SOLID_BREP: closing cap face (z=1 triangle) has "
        "same_sense=True (FORWARD) but solid convention requires REVERSED; "
        "orientation mismatch IS wired into shell/face topology — mirrors the "
        "LastShape()-vs-solid inconsistency; strict receivers must heal"
    ),
)

# ── Build a triangular-prism wedge solid: 3 faces ─────────────────────────────
# Cross-section: right triangle (0,0)-(1,0)-(0,1) extruded along z=[0,1].
# Only 3 faces are used (bottom z=0 triangle, side y=0 rectangle, top z=1 triangle)
# to hit the tier-3 assertion count_entity_def(ADVANCED_FACE) == 3.

def pt(x, y, z):
    return f.cartesian_point((float(x), float(y), float(z)))

def mk_edge(va, vb, pstart, dx, dy, dz):
    d = f.direction((float(dx), float(dy), float(dz)))
    vec = f.vector(d, 1.0)
    ln = f.line(pstart, vec)
    return f.edge_curve(va, vb, ln)

# Wedge corners
A0 = pt(0,0,0); B0 = pt(1,0,0); C0 = pt(0,1,0)  # z=0 triangle
A1 = pt(0,0,1); B1 = pt(1,0,1); C1 = pt(0,1,1)  # z=1 triangle

vA0 = f.vertex_point(A0); vB0 = f.vertex_point(B0); vC0 = f.vertex_point(C0)
vA1 = f.vertex_point(A1); vB1 = f.vertex_point(B1); vC1 = f.vertex_point(C1)

# Bottom edges (z=0)
eAB0 = mk_edge(vA0, vB0, A0,  1, 0, 0)
eBC0 = mk_edge(vB0, vC0, B0, -1, 1, 0)
eCA0 = mk_edge(vC0, vA0, C0,  0,-1, 0)

# Top edges (z=1)
eAB1 = mk_edge(vA1, vB1, A1,  1, 0, 0)
eBC1 = mk_edge(vB1, vC1, B1, -1, 1, 0)
eCA1 = mk_edge(vC1, vA1, C1,  0,-1, 0)

# Vertical pillar edges
eAA = mk_edge(vA0, vA1, A0, 0, 0, 1)
eBB = mk_edge(vB0, vB1, B0, 0, 0, 1)
eCC = mk_edge(vC0, vC1, C0, 0, 0, 1)

# ── Face 1: bottom triangle (z=0), outward normal (0,0,-1) ────────────────────
lp_bot = f.edge_loop([
    f.oriented_edge(eAB0, True),
    f.oriented_edge(eBC0, True),
    f.oriented_edge(eCA0, True),
])
ax_bot = f.axis2_placement_3d(A0, f.direction((0,0,-1)), f.direction((1,0,0)))
face_bot = f.advanced_face([f.face_outer_bound(lp_bot)], f.plane(ax_bot), same_sense=True)

# ── Face 2: rectangular side (y=0), outward normal (0,-1,0) ───────────────────
# Vertices: A0, B0, B1, A1 — traversed so outward normal faces -y
lp_side = f.edge_loop([
    f.oriented_edge(eAB0, True),
    f.oriented_edge(eBB,  True),
    f.oriented_edge(eAB1, False),
    f.oriented_edge(eAA,  False),
])
ax_side = f.axis2_placement_3d(A0, f.direction((0,-1,0)), f.direction((1,0,0)))
face_side = f.advanced_face([f.face_outer_bound(lp_side)], f.plane(ax_side), same_sense=True)

# ── Face 3: top triangle (z=1) — DEFECT: same_sense=True instead of False ─────
# The closing cap ("LastShape() analogue") is emitted with same_sense=True.
# Inside the solid, the top face should have same_sense=False (reversed) so the
# outward normal points +z. Emitting True creates the orientation mismatch IS
# the mechanism — the solid's LastShape()-equivalent reports FORWARD but the
# solid's explorer sees the wrong sign.
lp_top = f.edge_loop([
    f.oriented_edge(eAB1, True),
    f.oriented_edge(eBC1, True),
    f.oriented_edge(eCA1, True),
])
ax_top = f.axis2_placement_3d(A1, f.direction((0,0,1)), f.direction((1,0,0)))
# DEFECT: same_sense=True on the closing cap; correct would be False
face_top = f.advanced_face([f.face_outer_bound(lp_top)], f.plane(ax_top), same_sense=True)

# ── CLOSED_SHELL → MANIFOLD_SOLID_BREP ───────────────────────────────────────
closed_sh = f.closed_shell([face_bot, face_side, face_top])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb)
