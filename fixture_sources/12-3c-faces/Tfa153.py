"""Tfa153 — ShapeFix_Face.FixSmallAreaWire computational-overflow.

Catalog claim: Face with very large vertex coordinates (1e15). FixSmallAreaWire's
area calculation overflows float precision when scaling by coordinates near
machine limits.

Mechanism: CLOSED_SHELL box at large offset (1e15 mm). The entire box is placed
far from the origin: corners at 1e15 + small offsets. The top face (z = 1e15+1)
has a standard outer loop plus an inner FACE_BOUND wire (small rectangle).
FixSmallAreaWire computes cross-products of vertex coordinate vectors; when
coordinates are ~1e15, the cross-product magnitudes ~(1e15)^2 = 1e30, overflowing
IEEE 754 double (max ~1.8e308 but losing mantissa precision past 1e15 in sums).
The area calculation loses significance and produces incorrect result.
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
    catalog_id="Tfa153",
    defect=(
        "CLOSED_SHELL: 10×10×1 mm box with all coordinates offset by 1e15; "
        "top face outer loop plus inner FACE_BOUND wire (small 2×2 rectangle); "
        "FixSmallAreaWire cross-product area calculation: vertex magnitudes ~1e15 "
        "cause cross-product ~1e30; float precision at 1e15 loses ~15 significant "
        "digits so small area differences vanish in rounding; "
        "area calculation overflows meaningful precision and returns wrong result; "
        "defect IS on live CLOSED_SHELL traversal path"
    ),
)

O = 1.0e15  # large coordinate offset
L = 10.0
W = 10.0
H = 1.0

# Bottom corners at z=O
p_A = f.cartesian_point((O,     O,     O))
p_B = f.cartesian_point((O + L, O,     O))
p_C = f.cartesian_point((O + L, O + W, O))
p_D = f.cartesian_point((O,     O + W, O))
# Top corners at z=O+H
p_E  = f.cartesian_point((O,     O,     O + H))
p_F  = f.cartesian_point((O + L, O,     O + H))
p_G  = f.cartesian_point((O + L, O + W, O + H))
p_pH = f.cartesian_point((O,     O + W, O + H))

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
eEF = f.edge_curve(vE, vF, f.line(p_E,  f.vector(f.direction(( 1.0, 0.0, 0.0)), L)))
eFG = f.edge_curve(vF, vG, f.line(p_F,  f.vector(f.direction(( 0.0, 1.0, 0.0)), W)))
eGH = f.edge_curve(vG, vH, f.line(p_G,  f.vector(f.direction((-1.0, 0.0, 0.0)), L)))
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

# ── Top face: outer loop + small inner wire at large offset — THE DEFECT ─────
top_outer_loop = f.edge_loop([
    f.oriented_edge(eEF, True), f.oriented_edge(eFG, True),
    f.oriented_edge(eGH, True), f.oriented_edge(eHE, True),
])
# Inner wire: 2×2 mm rectangle at (O+1, O+1, O+H)
IW = 2.0
p_i0 = f.cartesian_point((O + 1.0,        O + 1.0,        O + H))
p_i1 = f.cartesian_point((O + 1.0 + IW,   O + 1.0,        O + H))
p_i2 = f.cartesian_point((O + 1.0 + IW,   O + 1.0 + IW,   O + H))
p_i3 = f.cartesian_point((O + 1.0,        O + 1.0 + IW,   O + H))
vi0 = f.vertex_point(p_i0); vi1 = f.vertex_point(p_i1)
vi2 = f.vertex_point(p_i2); vi3 = f.vertex_point(p_i3)
ei01 = f.edge_curve(vi0, vi1, f.line(p_i0, f.vector(f.direction(( 1.0, 0.0, 0.0)), IW)))
ei12 = f.edge_curve(vi1, vi2, f.line(p_i1, f.vector(f.direction(( 0.0, 1.0, 0.0)), IW)))
ei23 = f.edge_curve(vi2, vi3, f.line(p_i2, f.vector(f.direction((-1.0, 0.0, 0.0)), IW)))
ei30 = f.edge_curve(vi3, vi0, f.line(p_i3, f.vector(f.direction(( 0.0,-1.0, 0.0)), IW)))
inner_loop = f.edge_loop([
    f.oriented_edge(ei01, True), f.oriented_edge(ei12, True),
    f.oriented_edge(ei23, True), f.oriented_edge(ei30, True),
])
ax_top = f.axis2_placement_3d(p_E, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
face_top = f.advanced_face([
    f.face_outer_bound(top_outer_loop),
    f.face_bound(inner_loop),  # small inner wire at 1e15 offset — THE DEFECT
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
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa153.stp")
