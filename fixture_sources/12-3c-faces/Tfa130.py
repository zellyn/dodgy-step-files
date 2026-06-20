"""Tfa130 — FixSmallAreaWire: mixed-size-wires.

Catalog claim: Face declares two outer-wire candidates: one large (20×20)
and one tiny (0.2×0.2) with no nesting relationship.
FixSmallAreaWire's outer-vs-inner detection heuristic selects tiny wire as
outer because it processes area-sorted list incorrectly. Reproducer: single
plane face with two disjoint FACE_OUTER_BOUND entries of vastly different
scales.

Mechanism: CLOSED_SHELL wrapping a box. The top face (z=1) carries two
FACE_OUTER_BOUND loops — a large 20×20 loop and a tiny 0.2×0.2 loop
placed disjoint from it. FixSmallAreaWire's heuristic mis-selects the tiny
loop as the outer boundary because it sorts by area ascending and takes the
first entry. The defect is live on the CLOSED_SHELL traversal path.

Byte assertions:
  - contains(b'ADVANCED_FACE')
  - contains(b'FACE_OUTER_BOUND')

Tier-3 assertion: n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(17) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa130",
    defect=(
        "CLOSED_SHELL: top face (z=1) carries two FACE_OUTER_BOUND loops — "
        "a large 20×20 loop (area=400) and a tiny 0.2×0.2 loop (area=0.04) "
        "placed disjoint from the large loop; "
        "FixSmallAreaWire area-sorted-list heuristic processes ascending order "
        "and incorrectly selects the tiny loop as the outer boundary; "
        "defect IS on live CLOSED_SHELL traversal path"
    ),
)

# Box: 20×20×1 mm — large face so the area disparity is extreme
L = 20.0
W = 20.0
H = 1.0

# Bottom corners z=0
p_A = f.cartesian_point((0.0, 0.0, 0.0))
p_B = f.cartesian_point(( L,   0.0, 0.0))
p_C = f.cartesian_point(( L,   W,   0.0))
p_D = f.cartesian_point((0.0,  W,   0.0))
# Top corners z=H
p_E = f.cartesian_point((0.0, 0.0, H))
p_F = f.cartesian_point(( L,   0.0, H))
p_G = f.cartesian_point(( L,   W,   H))
p_pH = f.cartesian_point((0.0,  W,   H))

vA = f.vertex_point(p_A); vB = f.vertex_point(p_B)
vC = f.vertex_point(p_C); vD = f.vertex_point(p_D)
vE = f.vertex_point(p_E); vF = f.vertex_point(p_F)
vG = f.vertex_point(p_G); vH = f.vertex_point(p_pH)

# Bottom edges (z=0)
eAB = f.edge_curve(vA, vB, f.line(p_A, f.vector(f.direction(( 1.0, 0.0, 0.0)), L)))
eBC = f.edge_curve(vB, vC, f.line(p_B, f.vector(f.direction(( 0.0, 1.0, 0.0)), W)))
eCD = f.edge_curve(vC, vD, f.line(p_C, f.vector(f.direction((-1.0, 0.0, 0.0)), L)))
eDA = f.edge_curve(vD, vA, f.line(p_D, f.vector(f.direction(( 0.0,-1.0, 0.0)), W)))

# Top edges (z=H)
eEF = f.edge_curve(vE, vF, f.line(p_E, f.vector(f.direction(( 1.0, 0.0, 0.0)), L)))
eFG = f.edge_curve(vF, vG, f.line(p_F, f.vector(f.direction(( 0.0, 1.0, 0.0)), W)))
eGH = f.edge_curve(vG, vH, f.line(p_G, f.vector(f.direction((-1.0, 0.0, 0.0)), L)))
eHE = f.edge_curve(vH, vE, f.line(p_pH, f.vector(f.direction((0.0, -1.0, 0.0)), W)))

# Vertical edges
eAE = f.edge_curve(vA, vE, f.line(p_A, f.vector(f.direction((0.0, 0.0, 1.0)), H)))
eBF = f.edge_curve(vB, vF, f.line(p_B, f.vector(f.direction((0.0, 0.0, 1.0)), H)))
eCG = f.edge_curve(vC, vG, f.line(p_C, f.vector(f.direction((0.0, 0.0, 1.0)), H)))
eDH = f.edge_curve(vD, vH, f.line(p_D, f.vector(f.direction((0.0, 0.0, 1.0)), H)))

# Bottom face (z=0, normal -Z)
bot_loop = f.edge_loop([
    f.oriented_edge(eAB, True), f.oriented_edge(eBC, True),
    f.oriented_edge(eCD, True), f.oriented_edge(eDA, True),
])
ax_bot = f.axis2_placement_3d(p_A, f.direction((0.0, 0.0, -1.0)), f.direction((1.0, 0.0, 0.0)))
face_bot = f.advanced_face([f.face_outer_bound(bot_loop)], f.plane(ax_bot))

# Top face (z=H, normal +Z): THE DEFECT — two FACE_OUTER_BOUNDs
# Large outer loop 20×20
top_large_loop = f.edge_loop([
    f.oriented_edge(eEF, True), f.oriented_edge(eFG, True),
    f.oriented_edge(eGH, True), f.oriented_edge(eHE, True),
])
# Tiny disjoint loop 0.2×0.2 at (25, 25, H) — far outside the main face
p_t0 = f.cartesian_point((25.0,  25.0,  H))
p_t1 = f.cartesian_point((25.2,  25.0,  H))
p_t2 = f.cartesian_point((25.2,  25.2,  H))
p_t3 = f.cartesian_point((25.0,  25.2,  H))
vt0 = f.vertex_point(p_t0); vt1 = f.vertex_point(p_t1)
vt2 = f.vertex_point(p_t2); vt3 = f.vertex_point(p_t3)
et01 = f.edge_curve(vt0, vt1, f.line(p_t0, f.vector(f.direction((1.0, 0.0, 0.0)), 0.2)))
et12 = f.edge_curve(vt1, vt2, f.line(p_t1, f.vector(f.direction((0.0, 1.0, 0.0)), 0.2)))
et23 = f.edge_curve(vt2, vt3, f.line(p_t2, f.vector(f.direction((-1.0, 0.0, 0.0)), 0.2)))
et30 = f.edge_curve(vt3, vt0, f.line(p_t3, f.vector(f.direction((0.0, -1.0, 0.0)), 0.2)))
top_tiny_loop = f.edge_loop([
    f.oriented_edge(et01, True), f.oriented_edge(et12, True),
    f.oriented_edge(et23, True), f.oriented_edge(et30, True),
])
ax_top = f.axis2_placement_3d(p_E, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
# Two FACE_OUTER_BOUNDs — the defect: tiny loop listed first (area=0.04), large loop second (area=400)
face_top = f.advanced_face([
    f.face_outer_bound(top_tiny_loop),
    f.face_outer_bound(top_large_loop),
], f.plane(ax_top))

# Side faces
frt_loop = f.edge_loop([
    f.oriented_edge(eAB, True),  f.oriented_edge(eBF, True),
    f.oriented_edge(eEF, False), f.oriented_edge(eAE, False),
])
ax_frt = f.axis2_placement_3d(p_A, f.direction((0.0, -1.0, 0.0)), f.direction((1.0, 0.0, 0.0)))
face_frt = f.advanced_face([f.face_outer_bound(frt_loop)], f.plane(ax_frt))

bk_loop = f.edge_loop([
    f.oriented_edge(eDH, True),  f.oriented_edge(eGH, False),
    f.oriented_edge(eCG, False), f.oriented_edge(eCD, False),
])
ax_bk = f.axis2_placement_3d(p_D, f.direction((0.0, 1.0, 0.0)), f.direction((1.0, 0.0, 0.0)))
face_bk = f.advanced_face([f.face_outer_bound(bk_loop)], f.plane(ax_bk))

lft_loop = f.edge_loop([
    f.oriented_edge(eAE, True),  f.oriented_edge(eHE, False),
    f.oriented_edge(eDH, False), f.oriented_edge(eDA, False),
])
ax_lft = f.axis2_placement_3d(p_A, f.direction((-1.0, 0.0, 0.0)), f.direction((0.0, 1.0, 0.0)))
face_lft = f.advanced_face([f.face_outer_bound(lft_loop)], f.plane(ax_lft))

rgt_loop = f.edge_loop([
    f.oriented_edge(eBC, True),  f.oriented_edge(eCG, True),
    f.oriented_edge(eFG, False), f.oriented_edge(eBF, False),
])
ax_rgt = f.axis2_placement_3d(p_B, f.direction((1.0, 0.0, 0.0)), f.direction((0.0, 1.0, 0.0)))
face_rgt = f.advanced_face([f.face_outer_bound(rgt_loop)], f.plane(ax_rgt))

closed_sh = f.closed_shell([face_bot, face_top, face_frt, face_bk, face_lft, face_rgt])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa130.stp")
