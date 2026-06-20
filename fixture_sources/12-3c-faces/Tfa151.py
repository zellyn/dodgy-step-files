"""Tfa151 — ShapeFix_Face.FixLoopWire one-inner-touches-outer.

Catalog claim: Inner wire has a vertex that coincides with the outer wire.
FixLoopWire's nested-loop assumption that inner loops never touch outer geometry
fails, causing incorrect topology repair.

Mechanism: CLOSED_SHELL box (10×10×1 mm). The top face (z=1) has a standard
10×10 outer loop and an inner FACE_BOUND wire (square hole) where one corner
vertex of the inner wire coincides exactly with a corner vertex of the outer wire.
Specifically: outer wire corners at (0,0,1),(10,0,1),(10,10,1),(0,10,1) and the
inner wire's bottom-left corner is at (0,0,1) — identical to the outer corner.
FixLoopWire assumes inner loops are strictly contained (no shared vertices with
outer); this shared-vertex case causes incorrect topology repair.
Defect IS on live CLOSED_SHELL traversal path.

Byte assertions:
  - contains(b'ADVANCED_FACE')
  - contains(b'FACE_BOUND')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa151",
    defect=(
        "CLOSED_SHELL: 10×10×1 mm box; "
        "top face (z=1) outer loop corners at (0,0,1)(10,0,1)(10,10,1)(0,10,1) "
        "plus inner FACE_BOUND wire with bottom-left corner coincident at (0,0,1) "
        "(same XYZ as outer wire corner); "
        "FixLoopWire nested-loop assumption: inner loops never touch outer geometry; "
        "shared vertex (0,0,1) violates assumption — algorithm generates incorrect "
        "topology repair for the touching vertex; "
        "defect IS on live CLOSED_SHELL traversal path"
    ),
)

L = 10.0
W = 10.0
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

# Bottom edges
eAB = f.edge_curve(vA, vB, f.line(p_A, f.vector(f.direction(( 1.0, 0.0, 0.0)), L)))
eBC = f.edge_curve(vB, vC, f.line(p_B, f.vector(f.direction(( 0.0, 1.0, 0.0)), W)))
eCD = f.edge_curve(vC, vD, f.line(p_C, f.vector(f.direction((-1.0, 0.0, 0.0)), L)))
eDA = f.edge_curve(vD, vA, f.line(p_D, f.vector(f.direction(( 0.0,-1.0, 0.0)), W)))

# Top edges
eEF = f.edge_curve(vE, vF, f.line(p_E, f.vector(f.direction(( 1.0, 0.0, 0.0)), L)))
eFG = f.edge_curve(vF, vG, f.line(p_F, f.vector(f.direction(( 0.0, 1.0, 0.0)), W)))
eGH = f.edge_curve(vG, vH, f.line(p_G, f.vector(f.direction((-1.0, 0.0, 0.0)), L)))
eHE = f.edge_curve(vH, vE, f.line(p_pH, f.vector(f.direction(( 0.0,-1.0, 0.0)), W)))

# Vertical edges
eAE = f.edge_curve(vA, vE, f.line(p_A, f.vector(f.direction((0.0, 0.0, 1.0)), H)))
eBF = f.edge_curve(vB, vF, f.line(p_B, f.vector(f.direction((0.0, 0.0, 1.0)), H)))
eCG = f.edge_curve(vC, vG, f.line(p_C, f.vector(f.direction((0.0, 0.0, 1.0)), H)))
eDH = f.edge_curve(vD, vH, f.line(p_D, f.vector(f.direction((0.0, 0.0, 1.0)), H)))

# ── Bottom face ──────────────────────────────────────────────────────────────
bot_loop = f.edge_loop([
    f.oriented_edge(eAB, True), f.oriented_edge(eBC, True),
    f.oriented_edge(eCD, True), f.oriented_edge(eDA, True),
])
ax_bot = f.axis2_placement_3d(p_A, f.direction((0.0, 0.0, -1.0)), f.direction((1.0, 0.0, 0.0)))
face_bot = f.advanced_face([f.face_outer_bound(bot_loop)], f.plane(ax_bot))

# ── Top face: outer loop + inner wire touching outer at (0,0,H) — THE DEFECT ─
top_outer_loop = f.edge_loop([
    f.oriented_edge(eEF, True), f.oriented_edge(eFG, True),
    f.oriented_edge(eGH, True), f.oriented_edge(eHE, True),
])
# Inner wire: 3×3 square with bottom-left at (0,0,H) — touches outer corner vE
# Inner corners: (0,0,H)=vE (shared!), (3,0,H), (3,3,H), (0,3,H)
IW = 3.0
# Reuse vE for the shared corner — the defect
p_i1 = f.cartesian_point((IW,  0.0, H))
p_i2 = f.cartesian_point((IW,  IW,  H))
p_i3 = f.cartesian_point((0.0, IW,  H))
vi1 = f.vertex_point(p_i1)
vi2 = f.vertex_point(p_i2)
vi3 = f.vertex_point(p_i3)
# Edges of inner wire
ei01 = f.edge_curve(vE,  vi1, f.line(p_E,  f.vector(f.direction(( 1.0, 0.0, 0.0)), IW)))
ei12 = f.edge_curve(vi1, vi2, f.line(p_i1, f.vector(f.direction(( 0.0, 1.0, 0.0)), IW)))
ei23 = f.edge_curve(vi2, vi3, f.line(p_i2, f.vector(f.direction((-1.0, 0.0, 0.0)), IW)))
ei30 = f.edge_curve(vi3, vE,  f.line(p_i3, f.vector(f.direction(( 0.0,-1.0, 0.0)), IW)))
inner_loop = f.edge_loop([
    f.oriented_edge(ei01, True), f.oriented_edge(ei12, True),
    f.oriented_edge(ei23, True), f.oriented_edge(ei30, True),
])
ax_top = f.axis2_placement_3d(p_E, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
face_top = f.advanced_face([
    f.face_outer_bound(top_outer_loop),
    f.face_bound(inner_loop),  # inner touches outer at vE — THE DEFECT
], f.plane(ax_top))

# ── Side faces ───────────────────────────────────────────────────────────────
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
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa151.stp")
