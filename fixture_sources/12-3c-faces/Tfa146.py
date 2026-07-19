"""Tfa146 — ShapeFix_Face.FixOrientation parametric-vs-3D-winding.

Catalog claim: Outer wire winds correctly in 3D but the parametric (u,v)
winding is reversed; FixOrientation uses parametric winding test instead
of 3D test. Calling FixOrientation on a planar rectangular face with
standard CCW winding in 3D demonstrates the defect: if the algorithm
relies only on parametric (u,v) tests, it may incorrectly classify the wire
as reversed and flip it unnecessarily.

Mechanism: CLOSED_SHELL box (10×10×1 mm). The top face (z=1) has its
PLANE axis placed so the (u,v) parameterization runs clockwise while the
3D outer loop runs counter-clockwise. FixOrientation must consult 3D
geometry; relying on parametric winding gives the wrong answer.

Byte assertions:
  - contains(b'ADVANCED_FACE')
  - contains(b'FACE_OUTER_BOUND')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa146",
    defect=(
        "CLOSED_SHELL: 10×10×1 box; "
        "top face (z=1) has PLANE axis with x-direction reversed (-X) so "
        "parametric (u,v) winding is CW while 3D wire is CCW; "
        "FixOrientation parametric-winding test incorrectly flags wire as "
        "reversed; 3D test would confirm correct winding; "
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

# Top edges (CCW in 3D: E→F→G→H→E)
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

# ── Top face: THE DEFECT — PLANE axis has x-dir reversed (-X) ───────────────
# 3D winding is CCW (E→F→G→H→E viewed from above).
# PLANE xdir = (-1,0,0): parametric u runs right-to-left, making (u,v)
# winding appear CW. FixOrientation's parametric test would reverse the wire.
top_loop = f.edge_loop([
    f.oriented_edge(eEF, True), f.oriented_edge(eFG, True),
    f.oriented_edge(eGH, True), f.oriented_edge(eHE, True),
])
# Normal = zdir × xdir_reversed: zdir=(0,0,1), xdir=(-1,0,0) → still valid plane
# but parametric cross-product gives CW appearance
ax_top = f.axis2_placement_3d(p_G, f.direction((0.0, 0.0, 1.0)), f.direction((-1.0, 0.0, 0.0)))
face_top = f.advanced_face([f.face_outer_bound(top_loop)], f.plane(ax_top))

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
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa146.stp")
