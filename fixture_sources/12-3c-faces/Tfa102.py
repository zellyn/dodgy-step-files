"""Tfa102 — ShapeAnalysis_CheckSmallFace.CheckSmallArea aspect-ratio infinite.

Catalog claim: Face with one dimension at 1000.0 and another at 0.0001;
aspect-ratio overflow in CheckSmallArea's classification logic.

Mechanism: MANIFOLD_SOLID_BREP with a CLOSED_SHELL containing a 1000.0×0.0001
thin-rectangle PLANE face (THE DEFECT: aspect ratio 1e7, causing float overflow
in CheckSmallArea's classification) plus five side/cap faces to close the box.
Dimensions: 1000.0 × 0.0001 × 1.0 box.

face[0]: bottom z=0 — 1000.0×0.0001 PLANE strip (the defect)
face[1]: top z=1    — 1000.0×0.0001 PLANE strip
face[2]: front y=0  — 1000.0×1.0 side
face[3]: back y=0.0001 — 1000.0×1.0 side
face[4]: left x=0   — 0.0001×1.0 end
face[5]: right x=1000.0 — 0.0001×1.0 end

Tier-3 assertion: n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa102",
    defect=(
        "CLOSED_SHELL: face[0] is 1000.0×0.0001 PLANE strip at z=0; "
        "aspect ratio = 1.0E7 → float overflow in "
        "ShapeAnalysis_CheckSmallFace::CheckSmallArea classification logic; "
        "box is 1000.0×0.0001×1.0; defect IS on live CLOSED_SHELL traversal path"
    ),
)

L = 1000.0    # long dimension X
W = 0.0001    # tiny dimension Y
H = 1.0       # height Z

# Box corners
p000 = f.cartesian_point((0.0, 0.0, 0.0)); p100 = f.cartesian_point((L,   0.0, 0.0))
p110 = f.cartesian_point((L,   W,   0.0)); p010 = f.cartesian_point((0.0, W,   0.0))
p001 = f.cartesian_point((0.0, 0.0, H));   p101 = f.cartesian_point((L,   0.0, H))
p111 = f.cartesian_point((L,   W,   H));   p011 = f.cartesian_point((0.0, W,   H))

v000 = f.vertex_point(p000); v100 = f.vertex_point(p100)
v110 = f.vertex_point(p110); v010 = f.vertex_point(p010)
v001 = f.vertex_point(p001); v101 = f.vertex_point(p101)
v111 = f.vertex_point(p111); v011 = f.vertex_point(p011)

# Bottom edges (z=0)
eb0 = f.edge_curve(v000, v100, f.line(p000, f.vector(f.direction(( 1.0, 0.0, 0.0)), L)))
eb1 = f.edge_curve(v100, v110, f.line(p100, f.vector(f.direction(( 0.0, 1.0, 0.0)), W)))
eb2 = f.edge_curve(v110, v010, f.line(p110, f.vector(f.direction((-1.0, 0.0, 0.0)), L)))
eb3 = f.edge_curve(v010, v000, f.line(p010, f.vector(f.direction(( 0.0,-1.0, 0.0)), W)))

# Top edges (z=H)
et0 = f.edge_curve(v001, v101, f.line(p001, f.vector(f.direction(( 1.0, 0.0, 0.0)), L)))
et1 = f.edge_curve(v101, v111, f.line(p101, f.vector(f.direction(( 0.0, 1.0, 0.0)), W)))
et2 = f.edge_curve(v111, v011, f.line(p111, f.vector(f.direction((-1.0, 0.0, 0.0)), L)))
et3 = f.edge_curve(v011, v001, f.line(p011, f.vector(f.direction(( 0.0,-1.0, 0.0)), W)))

# Vertical edges
ev0 = f.edge_curve(v000, v001, f.line(p000, f.vector(f.direction((0.0, 0.0, 1.0)), H)))
ev1 = f.edge_curve(v100, v101, f.line(p100, f.vector(f.direction((0.0, 0.0, 1.0)), H)))
ev2 = f.edge_curve(v110, v111, f.line(p110, f.vector(f.direction((0.0, 0.0, 1.0)), H)))
ev3 = f.edge_curve(v010, v011, f.line(p010, f.vector(f.direction((0.0, 0.0, 1.0)), H)))

# ── face[0]: bottom strip z=0 — THE DEFECT ─────────────────────────────────────
bot_loop = f.edge_loop([
    f.oriented_edge(eb0, True), f.oriented_edge(eb1, True),
    f.oriented_edge(eb2, True), f.oriented_edge(eb3, True),
])
ax_bot = f.axis2_placement_3d(p000, f.direction((0.0, 0.0, -1.0)), f.direction((1.0, 0.0, 0.0)))
face0 = f.advanced_face([f.face_outer_bound(bot_loop)], f.plane(ax_bot))

# ── face[1]: top strip z=H ─────────────────────────────────────────────────────
top_loop = f.edge_loop([
    f.oriented_edge(et0, True), f.oriented_edge(et1, True),
    f.oriented_edge(et2, True), f.oriented_edge(et3, True),
])
ax_top = f.axis2_placement_3d(p001, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
face1 = f.advanced_face([f.face_outer_bound(top_loop)], f.plane(ax_top))

# ── face[2]: front y=0 ────────────────────────────────────────────────────────
frt_loop = f.edge_loop([
    f.oriented_edge(eb0, True),  f.oriented_edge(ev1, True),
    f.oriented_edge(et0, False), f.oriented_edge(ev0, False),
])
ax_frt = f.axis2_placement_3d(p000, f.direction((0.0, -1.0, 0.0)), f.direction((1.0, 0.0, 0.0)))
face2 = f.advanced_face([f.face_outer_bound(frt_loop)], f.plane(ax_frt))

# ── face[3]: back y=W ─────────────────────────────────────────────────────────
bk_loop = f.edge_loop([
    f.oriented_edge(ev3, True),  f.oriented_edge(et2, False),
    f.oriented_edge(ev2, False), f.oriented_edge(eb2, False),
])
ax_bk = f.axis2_placement_3d(p010, f.direction((0.0, 1.0, 0.0)), f.direction((1.0, 0.0, 0.0)))
face3 = f.advanced_face([f.face_outer_bound(bk_loop)], f.plane(ax_bk))

# ── face[4]: left x=0 ─────────────────────────────────────────────────────────
lft_loop = f.edge_loop([
    f.oriented_edge(ev0, True),  f.oriented_edge(et3, False),
    f.oriented_edge(ev3, False), f.oriented_edge(eb3, False),
])
ax_lft = f.axis2_placement_3d(p000, f.direction((-1.0, 0.0, 0.0)), f.direction((0.0, 1.0, 0.0)))
face4 = f.advanced_face([f.face_outer_bound(lft_loop)], f.plane(ax_lft))

# ── face[5]: right x=L ────────────────────────────────────────────────────────
rgt_loop = f.edge_loop([
    f.oriented_edge(eb1, True),  f.oriented_edge(ev2, True),
    f.oriented_edge(et1, False), f.oriented_edge(ev1, False),
])
ax_rgt = f.axis2_placement_3d(p100, f.direction((1.0, 0.0, 0.0)), f.direction((0.0, 1.0, 0.0)))
face5 = f.advanced_face([f.face_outer_bound(rgt_loop)], f.plane(ax_rgt))

# ── CLOSED_SHELL → MANIFOLD_SOLID_BREP ────────────────────────────────────────
closed_sh = f.closed_shell([face0, face1, face2, face3, face4, face5])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa102.stp")
