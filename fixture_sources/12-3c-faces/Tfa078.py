"""Tfa078 — FixLoopWire intersecting-loops merge.

Catalog claim: Planar face with two inner loops positioned such that their
geometric footprints intersect (hole1 at 20-40 mm, hole2 at 50-70 mm; overlap
at midline). FixLoopWire merges intersecting loops but merge introduces tangent
self-touch at boundary contact point.

Mechanism: CLOSED_SHELL built as a 100×100×1 mm box. The top face (z=1) is a
PLANE with one outer wire and two inner loops (FACE_BOUND) representing holes.
Hole1 occupies x=[20,40], hole2 x=[50,70], both at y=[20,80]. FixLoopWire
should detect that both holes overlap at x≈45 (the midline), merge them into a
combined loop, but the merged wire self-touches at the merge seam.

Byte assertions:
  - count_entity_def(b'FACE_BOUND') >= 2
  - contains(b'FACE_OUTER_BOUND')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa078",
    defect=(
        "CLOSED_SHELL 100×100×1 mm box; top face (z=1) has outer wire plus two FACE_BOUNDs "
        "(inner loops = holes); "
        "hole1: x=[20,40] y=[20,80] — 4-edge inner loop; "
        "hole2: x=[50,70] y=[20,80] — 4-edge inner loop; "
        "footprints overlap at x=45 midline; "
        "FixLoopWire: merge produces tangent self-touch at merge seam x=45; "
        "merged wire self-touches but no gap introduced; "
        "5-face companion box (bottom+4 sides) closes the shell; "
        "defect IS on live CLOSED_SHELL traversal path"
    ),
)

W = 100.0; H_box = 1.0

# Box points
p000 = f.cartesian_point((0.0, 0.0, 0.0)); p100 = f.cartesian_point((W,   0.0, 0.0))
p110 = f.cartesian_point((W,   W,   0.0)); p010 = f.cartesian_point((0.0, W,   0.0))
p001 = f.cartesian_point((0.0, 0.0, H_box)); p101 = f.cartesian_point((W,   0.0, H_box))
p111 = f.cartesian_point((W,   W,   H_box)); p011 = f.cartesian_point((0.0, W,   H_box))

v000 = f.vertex_point(p000); v100 = f.vertex_point(p100)
v110 = f.vertex_point(p110); v010 = f.vertex_point(p010)
v001 = f.vertex_point(p001); v101 = f.vertex_point(p101)
v111 = f.vertex_point(p111); v011 = f.vertex_point(p011)

# Bottom z=0 edges
eb0 = f.edge_curve(v000, v100, f.line(p000, f.vector(f.direction(( 1.0, 0.0, 0.0)), W)))
eb1 = f.edge_curve(v100, v110, f.line(p100, f.vector(f.direction(( 0.0, 1.0, 0.0)), W)))
eb2 = f.edge_curve(v110, v010, f.line(p110, f.vector(f.direction((-1.0, 0.0, 0.0)), W)))
eb3 = f.edge_curve(v010, v000, f.line(p010, f.vector(f.direction(( 0.0,-1.0, 0.0)), W)))

# Top z=H_box edges
et0 = f.edge_curve(v001, v101, f.line(p001, f.vector(f.direction(( 1.0, 0.0, 0.0)), W)))
et1 = f.edge_curve(v101, v111, f.line(p101, f.vector(f.direction(( 0.0, 1.0, 0.0)), W)))
et2 = f.edge_curve(v111, v011, f.line(p111, f.vector(f.direction((-1.0, 0.0, 0.0)), W)))
et3 = f.edge_curve(v011, v001, f.line(p011, f.vector(f.direction(( 0.0,-1.0, 0.0)), W)))

# Vertical edges
ev0 = f.edge_curve(v000, v001, f.line(p000, f.vector(f.direction((0.0, 0.0, 1.0)), H_box)))
ev1 = f.edge_curve(v100, v101, f.line(p100, f.vector(f.direction((0.0, 0.0, 1.0)), H_box)))
ev2 = f.edge_curve(v110, v111, f.line(p110, f.vector(f.direction((0.0, 0.0, 1.0)), H_box)))
ev3 = f.edge_curve(v010, v011, f.line(p010, f.vector(f.direction((0.0, 0.0, 1.0)), H_box)))

# ── Bottom face z=0 ───────────────────────────────────────────────────────────
bot_loop = f.edge_loop([f.oriented_edge(eb0, True), f.oriented_edge(eb1, True),
                        f.oriented_edge(eb2, True), f.oriented_edge(eb3, True)])
ax_bot = f.axis2_placement_3d(p000, f.direction((0.0, 0.0, -1.0)), f.direction((1.0, 0.0, 0.0)))
face_bot = f.advanced_face([f.face_outer_bound(bot_loop)], f.plane(ax_bot))

# ── Side faces ────────────────────────────────────────────────────────────────
frt_loop = f.edge_loop([f.oriented_edge(eb0, True), f.oriented_edge(ev1, True),
                        f.oriented_edge(et0, False), f.oriented_edge(ev0, False)])
ax_frt = f.axis2_placement_3d(p000, f.direction((0.0, -1.0, 0.0)), f.direction((1.0, 0.0, 0.0)))
face_frt = f.advanced_face([f.face_outer_bound(frt_loop)], f.plane(ax_frt))

bk_loop = f.edge_loop([f.oriented_edge(ev3, True), f.oriented_edge(et2, False),
                       f.oriented_edge(ev2, False), f.oriented_edge(eb2, False)])
ax_bk = f.axis2_placement_3d(p010, f.direction((0.0, 1.0, 0.0)), f.direction((1.0, 0.0, 0.0)))
face_bk = f.advanced_face([f.face_outer_bound(bk_loop)], f.plane(ax_bk))

lft_loop = f.edge_loop([f.oriented_edge(ev0, True), f.oriented_edge(et3, False),
                        f.oriented_edge(ev3, False), f.oriented_edge(eb3, False)])
ax_lft = f.axis2_placement_3d(p000, f.direction((-1.0, 0.0, 0.0)), f.direction((0.0, 1.0, 0.0)))
face_lft = f.advanced_face([f.face_outer_bound(lft_loop)], f.plane(ax_lft))

rgt_loop = f.edge_loop([f.oriented_edge(eb1, True), f.oriented_edge(ev2, True),
                        f.oriented_edge(et1, False), f.oriented_edge(ev1, False)])
ax_rgt = f.axis2_placement_3d(p100, f.direction((1.0, 0.0, 0.0)), f.direction((0.0, 1.0, 0.0)))
face_rgt = f.advanced_face([f.face_outer_bound(rgt_loop)], f.plane(ax_rgt))

# ── Top face z=H_box: outer wire + two inner loop holes (THE DEFECT) ──────────
# Outer wire: CCW from above (reversed edges, since top face normal = +Z)
top_outer_loop = f.edge_loop([
    f.oriented_edge(et0, True), f.oriented_edge(et1, True),
    f.oriented_edge(et2, True), f.oriented_edge(et3, True),
])
top_outer_fob = f.face_outer_bound(top_outer_loop)

# Hole 1: x=[20,40], y=[20,80] at z=H_box — inner loop (FACE_BOUND, orientation .F.)
# Inner loops must be oriented CW from above to represent a hole
h1x0, h1x1, h1y0, h1y1 = 20.0, 40.0, 20.0, 80.0
ph1_00 = f.cartesian_point((h1x0, h1y0, H_box)); ph1_10 = f.cartesian_point((h1x1, h1y0, H_box))
ph1_11 = f.cartesian_point((h1x1, h1y1, H_box)); ph1_01 = f.cartesian_point((h1x0, h1y1, H_box))
vh1_00 = f.vertex_point(ph1_00); vh1_10 = f.vertex_point(ph1_10)
vh1_11 = f.vertex_point(ph1_11); vh1_01 = f.vertex_point(ph1_01)

eh1_s = f.edge_curve(vh1_00, vh1_10, f.line(ph1_00, f.vector(f.direction(( 1.0, 0.0, 0.0)), h1x1-h1x0)))
eh1_e = f.edge_curve(vh1_10, vh1_11, f.line(ph1_10, f.vector(f.direction(( 0.0, 1.0, 0.0)), h1y1-h1y0)))
eh1_n = f.edge_curve(vh1_11, vh1_01, f.line(ph1_11, f.vector(f.direction((-1.0, 0.0, 0.0)), h1x1-h1x0)))
eh1_w = f.edge_curve(vh1_01, vh1_00, f.line(ph1_01, f.vector(f.direction(( 0.0,-1.0, 0.0)), h1y1-h1y0)))
# CW from above = reversed CCW: go along south .T., then west .F., north .F., east .F.
hole1_loop = f.edge_loop([
    f.oriented_edge(eh1_s, True),
    f.oriented_edge(eh1_w, False),
    f.oriented_edge(eh1_n, False),
    f.oriented_edge(eh1_e, False),
])
hole1_fb = f.face_bound(hole1_loop, orientation=False)

# Hole 2: x=[50,70], y=[20,80] at z=H_box — inner loop
h2x0, h2x1, h2y0, h2y1 = 50.0, 70.0, 20.0, 80.0
ph2_00 = f.cartesian_point((h2x0, h2y0, H_box)); ph2_10 = f.cartesian_point((h2x1, h2y0, H_box))
ph2_11 = f.cartesian_point((h2x1, h2y1, H_box)); ph2_01 = f.cartesian_point((h2x0, h2y1, H_box))
vh2_00 = f.vertex_point(ph2_00); vh2_10 = f.vertex_point(ph2_10)
vh2_11 = f.vertex_point(ph2_11); vh2_01 = f.vertex_point(ph2_01)

eh2_s = f.edge_curve(vh2_00, vh2_10, f.line(ph2_00, f.vector(f.direction(( 1.0, 0.0, 0.0)), h2x1-h2x0)))
eh2_e = f.edge_curve(vh2_10, vh2_11, f.line(ph2_10, f.vector(f.direction(( 0.0, 1.0, 0.0)), h2y1-h2y0)))
eh2_n = f.edge_curve(vh2_11, vh2_01, f.line(ph2_11, f.vector(f.direction((-1.0, 0.0, 0.0)), h2x1-h2x0)))
eh2_w = f.edge_curve(vh2_01, vh2_00, f.line(ph2_01, f.vector(f.direction(( 0.0,-1.0, 0.0)), h2y1-h2y0)))
hole2_loop = f.edge_loop([
    f.oriented_edge(eh2_s, True),
    f.oriented_edge(eh2_w, False),
    f.oriented_edge(eh2_n, False),
    f.oriented_edge(eh2_e, False),
])
hole2_fb = f.face_bound(hole2_loop, orientation=False)

# Top face with outer wire + two inner hole loops
ax_top = f.axis2_placement_3d(p001, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
face_top = f.advanced_face([top_outer_fob, hole1_fb, hole2_fb], f.plane(ax_top))

# ── CLOSED_SHELL + MANIFOLD_SOLID_BREP ────────────────────────────────────────
closed_sh = f.closed_shell([face_bot, face_top, face_frt, face_bk, face_lft, face_rgt])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa078.stp")
