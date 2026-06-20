"""Tfa149 — ShapeAnalysis_CheckSmallFace.CheckSplittingVertices wire-not-closed.

Catalog claim: Wire that isn't closed (open path); CheckSplittingVertices
produces a verdict on the open path even though splitting-vertex semantics
requires closure. Trigger: CheckSplittingVertices() on open 3-edge path
(first and last vertices differ by 4.5mm). CheckSplittingVertices should
fail or skip open wires since splitting-vertex analysis assumes topological
closure.

Mechanism: CLOSED_SHELL box (10×8×1 mm). The top face (z=1) has a standard
outer loop plus an inner FACE_BOUND wire that is an open 3-edge path — the
last vertex does not return to the first. The wire ends are 4.5mm apart.
CheckSplittingVertices proceeds on the open path and generates an inconsistent
verdict. The defect is live on the CLOSED_SHELL traversal path.

Byte assertions:
  - contains(b'ADVANCED_FACE')
  - contains(b'FACE_BOUND')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa149",
    defect=(
        "CLOSED_SHELL: 10×8×1 mm box; "
        "top face (z=1) outer loop 10×8 plus inner FACE_BOUND with an open "
        "3-edge path (start vertex at (2,2,1) and end vertex at (6.5,4,1), "
        "gap = 4.5 mm); "
        "ShapeAnalysis_CheckSmallFace::CheckSplittingVertices proceeds on the "
        "open wire and generates inconsistent splitting-vertex verdicts instead "
        "of failing or skipping non-closed wires; "
        "defect IS on live CLOSED_SHELL traversal path"
    ),
)

L = 10.0
W = 8.0
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

# ── Top face: outer loop + open 3-edge FACE_BOUND wire — THE DEFECT ──────────
top_outer_loop = f.edge_loop([
    f.oriented_edge(eEF, True), f.oriented_edge(eFG, True),
    f.oriented_edge(eGH, True), f.oriented_edge(eHE, True),
])
# Open 3-edge path: (2,2,H) → (4,2,H) → (4,4,H) → (6.5,4,H)
# The path does NOT close: start=(2,2,H) end=(6.5,4,H), gap=4.5mm
p_o0 = f.cartesian_point((2.0, 2.0, H))
p_o1 = f.cartesian_point((4.0, 2.0, H))
p_o2 = f.cartesian_point((4.0, 4.0, H))
p_o3 = f.cartesian_point((6.5, 4.0, H))
vo0 = f.vertex_point(p_o0); vo1 = f.vertex_point(p_o1)
vo2 = f.vertex_point(p_o2); vo3 = f.vertex_point(p_o3)
eo01 = f.edge_curve(vo0, vo1, f.line(p_o0, f.vector(f.direction((1.0, 0.0, 0.0)), 2.0)))
eo12 = f.edge_curve(vo1, vo2, f.line(p_o1, f.vector(f.direction((0.0, 1.0, 0.0)), 2.0)))
eo23 = f.edge_curve(vo2, vo3, f.line(p_o2, f.vector(f.direction((1.0, 0.0, 0.0)), 2.5)))
open_wire_loop = f.edge_loop([
    f.oriented_edge(eo01, True),
    f.oriented_edge(eo12, True),
    f.oriented_edge(eo23, True),
])
ax_top = f.axis2_placement_3d(p_E, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
face_top = f.advanced_face([
    f.face_outer_bound(top_outer_loop),
    f.face_bound(open_wire_loop),   # open path — THE DEFECT
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
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa149.stp")
