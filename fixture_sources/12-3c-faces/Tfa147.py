"""Tfa147 — ShapeAnalysis_CheckSmallFace.CheckTwisted face-on-plane.

Catalog claim: Small face on PLANE; CheckTwisted's tangent-test for twist
doesn't make sense for planes but produces a deterministic verdict anyway.
Trigger: call CheckTwisted() on small planar face (1mm × 1mm square on z=0
plane). CheckTwisted should skip or return false for planar faces since twist
is undefined; if the algorithm applies the twist test to planes it produces a
spurious TWISTED verdict.

Mechanism: CLOSED_SHELL box built from two sizes — a tiny 1×1×1 mm unit
cube. The bottom face (z=0) is the 1mm×1mm planar square that CheckTwisted
receives. Defect is live on the CLOSED_SHELL traversal path.

Byte assertions:
  - contains(b'ADVANCED_FACE')
  - contains(b'FACE_OUTER_BOUND')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa147",
    defect=(
        "CLOSED_SHELL: tiny 1×1×1 mm unit cube; "
        "bottom face (z=0) is a 1mm×1mm planar square; "
        "ShapeAnalysis_CheckSmallFace::CheckTwisted applies tangent-based "
        "twist test to this PLANE face and produces a spurious TWISTED verdict "
        "instead of skipping (twist is undefined for planes); "
        "defect IS on live CLOSED_SHELL traversal path"
    ),
)

S = 1.0   # 1mm unit cube side

# Vertices
p_A = f.cartesian_point((0.0, 0.0, 0.0))
p_B = f.cartesian_point(( S,   0.0, 0.0))
p_C = f.cartesian_point(( S,   S,   0.0))
p_D = f.cartesian_point((0.0,  S,   0.0))
p_E = f.cartesian_point((0.0, 0.0,  S))
p_F = f.cartesian_point(( S,   0.0,  S))
p_G = f.cartesian_point(( S,   S,    S))
p_pH = f.cartesian_point((0.0,  S,    S))

vA = f.vertex_point(p_A); vB = f.vertex_point(p_B)
vC = f.vertex_point(p_C); vD = f.vertex_point(p_D)
vE = f.vertex_point(p_E); vF = f.vertex_point(p_F)
vG = f.vertex_point(p_G); vH = f.vertex_point(p_pH)

# Bottom edges
eAB = f.edge_curve(vA, vB, f.line(p_A, f.vector(f.direction(( 1.0, 0.0, 0.0)), S)))
eBC = f.edge_curve(vB, vC, f.line(p_B, f.vector(f.direction(( 0.0, 1.0, 0.0)), S)))
eCD = f.edge_curve(vC, vD, f.line(p_C, f.vector(f.direction((-1.0, 0.0, 0.0)), S)))
eDA = f.edge_curve(vD, vA, f.line(p_D, f.vector(f.direction(( 0.0,-1.0, 0.0)), S)))

# Top edges
eEF = f.edge_curve(vE, vF, f.line(p_E, f.vector(f.direction(( 1.0, 0.0, 0.0)), S)))
eFG = f.edge_curve(vF, vG, f.line(p_F, f.vector(f.direction(( 0.0, 1.0, 0.0)), S)))
eGH = f.edge_curve(vG, vH, f.line(p_G, f.vector(f.direction((-1.0, 0.0, 0.0)), S)))
eHE = f.edge_curve(vH, vE, f.line(p_pH, f.vector(f.direction(( 0.0,-1.0, 0.0)), S)))

# Vertical edges
eAE = f.edge_curve(vA, vE, f.line(p_A, f.vector(f.direction((0.0, 0.0, 1.0)), S)))
eBF = f.edge_curve(vB, vF, f.line(p_B, f.vector(f.direction((0.0, 0.0, 1.0)), S)))
eCG = f.edge_curve(vC, vG, f.line(p_C, f.vector(f.direction((0.0, 0.0, 1.0)), S)))
eDH = f.edge_curve(vD, vH, f.line(p_D, f.vector(f.direction((0.0, 0.0, 1.0)), S)))

# ── Bottom face: THE DEFECT — small 1mm×1mm planar face ─────────────────────
bot_loop = f.edge_loop([
    f.oriented_edge(eAB, True), f.oriented_edge(eBC, True),
    f.oriented_edge(eCD, True), f.oriented_edge(eDA, True),
])
ax_bot = f.axis2_placement_3d(p_A, f.direction((0.0, 0.0, -1.0)), f.direction((1.0, 0.0, 0.0)))
face_bot = f.advanced_face([f.face_outer_bound(bot_loop)], f.plane(ax_bot))

# ── Top face ─────────────────────────────────────────────────────────────────
top_loop = f.edge_loop([
    f.oriented_edge(eEF, True), f.oriented_edge(eFG, True),
    f.oriented_edge(eGH, True), f.oriented_edge(eHE, True),
])
ax_top = f.axis2_placement_3d(p_E, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
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
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa147.stp")
