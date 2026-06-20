"""Tfa052 — ADVANCED_FACE split because surface area exceeds threshold.

Catalog claim: A single face whose surface area exceeds a caller-specified
threshold; downstream meshing performance requires it be split into N sub-faces
of bounded area. The N is computed from total area / threshold.

Reproducer recipe (from catalog): A 100x100 face when the caller supplies a
maximum area of 100 mm² — must divide into >= 100 sub-faces.

Mechanism: face[0] is a 100×100 ADVANCED_FACE on a PLANE. Its area is
10000 mm² >> caller threshold 100 mm². ShapeUpgrade_FaceDivideArea::Perform
must divide it into >= 100 sub-faces.

The fixture is a closed box 100×100×1 mm:
  face[0]: bottom z=0 — the large 100×100 PLANE face (THE DEFECT)
  face[1]: top z=1    — large 100×100 plane
  face[2]: front y=0  — 100×1 plane
  face[3]: back y=100 — 100×1 plane
  face[4]: left x=0   — 100×1 plane
  face[5]: right x=100 — 100×1 plane

The CLOSED_SHELL places face[0] on the live traversal path.

Tier-3 assertions:
  n_edges_total >= 4
  face[0].surface_type == "plane"
  n_vertices_total >= 8

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa052",
    defect=(
        "CLOSED_SHELL: face[0] is 100×100 mm ADVANCED_FACE on PLANE at z=0; "
        "face area = 10000 mm² far exceeds caller-supplied threshold of 100 mm²; "
        "ShapeUpgrade_FaceDivideArea::Perform must divide into >= 100 sub-faces; "
        "sub-faces share edges along U/V cuts; outer wire connectivity preserved; "
        "face[1..5] are plane faces forming closed 100×100×1 mm box; "
        "defect IS on live CLOSED_SHELL traversal path"
    ),
)

X = 100.0; Y = 100.0; H = 1.0

# Box vertices (z=0 bottom, z=H top)
p000 = f.cartesian_point((0.0, 0.0, 0.0)); p100 = f.cartesian_point((X,   0.0, 0.0))
p110 = f.cartesian_point((X,   Y,   0.0)); p010 = f.cartesian_point((0.0, Y,   0.0))
p001 = f.cartesian_point((0.0, 0.0, H));   p101 = f.cartesian_point((X,   0.0, H))
p111 = f.cartesian_point((X,   Y,   H));   p011 = f.cartesian_point((0.0, Y,   H))

v000 = f.vertex_point(p000); v100 = f.vertex_point(p100)
v110 = f.vertex_point(p110); v010 = f.vertex_point(p010)
v001 = f.vertex_point(p001); v101 = f.vertex_point(p101)
v111 = f.vertex_point(p111); v011 = f.vertex_point(p011)

# Bottom edges (z=0)
eb0 = f.edge_curve(v000, v100, f.line(p000, f.vector(f.direction(( 1.0, 0.0, 0.0)), X)))
eb1 = f.edge_curve(v100, v110, f.line(p100, f.vector(f.direction(( 0.0, 1.0, 0.0)), Y)))
eb2 = f.edge_curve(v110, v010, f.line(p110, f.vector(f.direction((-1.0, 0.0, 0.0)), X)))
eb3 = f.edge_curve(v010, v000, f.line(p010, f.vector(f.direction(( 0.0,-1.0, 0.0)), Y)))

# Top edges (z=H)
et0 = f.edge_curve(v001, v101, f.line(p001, f.vector(f.direction(( 1.0, 0.0, 0.0)), X)))
et1 = f.edge_curve(v101, v111, f.line(p101, f.vector(f.direction(( 0.0, 1.0, 0.0)), Y)))
et2 = f.edge_curve(v111, v011, f.line(p111, f.vector(f.direction((-1.0, 0.0, 0.0)), X)))
et3 = f.edge_curve(v011, v001, f.line(p011, f.vector(f.direction(( 0.0,-1.0, 0.0)), Y)))

# Vertical edges
ev0 = f.edge_curve(v000, v001, f.line(p000, f.vector(f.direction((0.0, 0.0, 1.0)), H)))
ev1 = f.edge_curve(v100, v101, f.line(p100, f.vector(f.direction((0.0, 0.0, 1.0)), H)))
ev2 = f.edge_curve(v110, v111, f.line(p110, f.vector(f.direction((0.0, 0.0, 1.0)), H)))
ev3 = f.edge_curve(v010, v011, f.line(p010, f.vector(f.direction((0.0, 0.0, 1.0)), H)))

# ── face[0]: bottom z=0 — large 100×100 PLANE face (THE DEFECT) ──────────────
bot_loop = f.edge_loop([
    f.oriented_edge(eb0, True), f.oriented_edge(eb1, True),
    f.oriented_edge(eb2, True), f.oriented_edge(eb3, True),
])
ax_bot = f.axis2_placement_3d(p000, f.direction((0.0, 0.0, -1.0)), f.direction((1.0, 0.0, 0.0)))
face0 = f.advanced_face([f.face_outer_bound(bot_loop)], f.plane(ax_bot))

# ── face[1]: top z=H ─────────────────────────────────────────────────────────
top_loop = f.edge_loop([
    f.oriented_edge(et0, True), f.oriented_edge(et1, True),
    f.oriented_edge(et2, True), f.oriented_edge(et3, True),
])
ax_top = f.axis2_placement_3d(p001, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
face1 = f.advanced_face([f.face_outer_bound(top_loop)], f.plane(ax_top))

# ── face[2]: front y=0 ───────────────────────────────────────────────────────
frt_loop = f.edge_loop([
    f.oriented_edge(eb0, True), f.oriented_edge(ev1, True),
    f.oriented_edge(et0, False), f.oriented_edge(ev0, False),
])
ax_frt = f.axis2_placement_3d(p000, f.direction((0.0, -1.0, 0.0)), f.direction((1.0, 0.0, 0.0)))
face2 = f.advanced_face([f.face_outer_bound(frt_loop)], f.plane(ax_frt))

# ── face[3]: back y=Y ────────────────────────────────────────────────────────
bk_loop = f.edge_loop([
    f.oriented_edge(ev3, True), f.oriented_edge(et2, False),
    f.oriented_edge(ev2, False), f.oriented_edge(eb2, False),
])
ax_bk = f.axis2_placement_3d(p010, f.direction((0.0, 1.0, 0.0)), f.direction((1.0, 0.0, 0.0)))
face3 = f.advanced_face([f.face_outer_bound(bk_loop)], f.plane(ax_bk))

# ── face[4]: left x=0 ────────────────────────────────────────────────────────
lft_loop = f.edge_loop([
    f.oriented_edge(ev0, True), f.oriented_edge(et3, False),
    f.oriented_edge(ev3, False), f.oriented_edge(eb3, False),
])
ax_lft = f.axis2_placement_3d(p000, f.direction((-1.0, 0.0, 0.0)), f.direction((0.0, 1.0, 0.0)))
face4 = f.advanced_face([f.face_outer_bound(lft_loop)], f.plane(ax_lft))

# ── face[5]: right x=X ───────────────────────────────────────────────────────
rgt_loop = f.edge_loop([
    f.oriented_edge(eb1, True), f.oriented_edge(ev2, True),
    f.oriented_edge(et1, False), f.oriented_edge(ev1, False),
])
ax_rgt = f.axis2_placement_3d(p100, f.direction((1.0, 0.0, 0.0)), f.direction((0.0, 1.0, 0.0)))
face5 = f.advanced_face([f.face_outer_bound(rgt_loop)], f.plane(ax_rgt))

# ── CLOSED_SHELL + MANIFOLD_SOLID_BREP ────────────────────────────────────────
closed_sh = f.closed_shell([face0, face1, face2, face3, face4, face5])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa052.stp")
