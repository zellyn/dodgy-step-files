"""Tfa077 — FixSmallAreaWire small-area early-exit.

Catalog claim: Planar face with micro-scale outer wire (0.001×0.001 mm²).
Area is below tolerance threshold; SmallAreaWire fixer should remove it.
Degenerate orientation check bypasses early exit even though wire is small,
keeping low-area wire in face.

Mechanism: CLOSED_SHELL containing a micro-scale square face at z=0 (0.001×0.001 mm)
plus a companion box that ensures OCC loads shape(1). The micro face IS on the live
CLOSED_SHELL traversal path. FixSmallAreaWire threshold check on degenerate
orientation prevents early-exit removal of the small-area wire.

Byte assertions:
  - contains(b'ADVANCED_FACE')
  - contains(b'FACE_OUTER_BOUND')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa077",
    defect=(
        "CLOSED_SHELL: face[0] is micro-scale 0.001×0.001 mm square ADVANCED_FACE on PLANE at z=0; "
        "wire area = 1e-6 mm² below default SmallAreaWire threshold; "
        "FixSmallAreaWire: degenerate-orientation check bypasses early exit — wire kept; "
        "companion box (1×1×1 mm, faces 1-6) provides shape(1) for OCC; "
        "micro face shares bottom plane with companion box; "
        "defect IS on live CLOSED_SHELL traversal path"
    ),
)

# Micro face: 0.001 × 0.001 square at z=0, offset from companion box
S = 0.001   # micro-face side length
# Place micro face at (2, 0, 0) to avoid overlapping the companion box at origin
OX, OY = 2.0, 0.0

pm00 = f.cartesian_point((OX,     OY,     0.0))
pm10 = f.cartesian_point((OX + S, OY,     0.0))
pm11 = f.cartesian_point((OX + S, OY + S, 0.0))
pm01 = f.cartesian_point((OX,     OY + S, 0.0))

vm00 = f.vertex_point(pm00); vm10 = f.vertex_point(pm10)
vm11 = f.vertex_point(pm11); vm01 = f.vertex_point(pm01)

em0 = f.edge_curve(vm00, vm10, f.line(pm00, f.vector(f.direction(( 1.0, 0.0, 0.0)), S)))
em1 = f.edge_curve(vm10, vm11, f.line(pm10, f.vector(f.direction(( 0.0, 1.0, 0.0)), S)))
em2 = f.edge_curve(vm11, vm01, f.line(pm11, f.vector(f.direction((-1.0, 0.0, 0.0)), S)))
em3 = f.edge_curve(vm01, vm00, f.line(pm01, f.vector(f.direction(( 0.0,-1.0, 0.0)), S)))

micro_loop = f.edge_loop([
    f.oriented_edge(em0, True), f.oriented_edge(em1, True),
    f.oriented_edge(em2, True), f.oriented_edge(em3, True),
])
ax_micro = f.axis2_placement_3d(
    f.cartesian_point((OX, OY, 0.0)),
    f.direction((0.0, 0.0, -1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
face_micro = f.advanced_face([f.face_outer_bound(micro_loop)], f.plane(ax_micro))

# ── Companion 1×1×1 mm box to give OCC shape(1) ──────────────────────────────
p000 = f.cartesian_point((0.0, 0.0, 0.0)); p100 = f.cartesian_point((1.0, 0.0, 0.0))
p110 = f.cartesian_point((1.0, 1.0, 0.0)); p010 = f.cartesian_point((0.0, 1.0, 0.0))
p001 = f.cartesian_point((0.0, 0.0, 1.0)); p101 = f.cartesian_point((1.0, 0.0, 1.0))
p111 = f.cartesian_point((1.0, 1.0, 1.0)); p011 = f.cartesian_point((0.0, 1.0, 1.0))

v000 = f.vertex_point(p000); v100 = f.vertex_point(p100)
v110 = f.vertex_point(p110); v010 = f.vertex_point(p010)
v001 = f.vertex_point(p001); v101 = f.vertex_point(p101)
v111 = f.vertex_point(p111); v011 = f.vertex_point(p011)

# Bottom z=0
eb0 = f.edge_curve(v000, v100, f.line(p000, f.vector(f.direction(( 1.0, 0.0, 0.0)), 1.0)))
eb1 = f.edge_curve(v100, v110, f.line(p100, f.vector(f.direction(( 0.0, 1.0, 0.0)), 1.0)))
eb2 = f.edge_curve(v110, v010, f.line(p110, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)))
eb3 = f.edge_curve(v010, v000, f.line(p010, f.vector(f.direction(( 0.0,-1.0, 0.0)), 1.0)))
# Top z=1
et0 = f.edge_curve(v001, v101, f.line(p001, f.vector(f.direction(( 1.0, 0.0, 0.0)), 1.0)))
et1 = f.edge_curve(v101, v111, f.line(p101, f.vector(f.direction(( 0.0, 1.0, 0.0)), 1.0)))
et2 = f.edge_curve(v111, v011, f.line(p111, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)))
et3 = f.edge_curve(v011, v001, f.line(p011, f.vector(f.direction(( 0.0,-1.0, 0.0)), 1.0)))
# Vertical
ev0 = f.edge_curve(v000, v001, f.line(p000, f.vector(f.direction((0.0, 0.0, 1.0)), 1.0)))
ev1 = f.edge_curve(v100, v101, f.line(p100, f.vector(f.direction((0.0, 0.0, 1.0)), 1.0)))
ev2 = f.edge_curve(v110, v111, f.line(p110, f.vector(f.direction((0.0, 0.0, 1.0)), 1.0)))
ev3 = f.edge_curve(v010, v011, f.line(p010, f.vector(f.direction((0.0, 0.0, 1.0)), 1.0)))

# Bottom face
bot_loop = f.edge_loop([f.oriented_edge(eb0, True), f.oriented_edge(eb1, True),
                        f.oriented_edge(eb2, True), f.oriented_edge(eb3, True)])
ax_bot = f.axis2_placement_3d(p000, f.direction((0.0, 0.0, -1.0)), f.direction((1.0, 0.0, 0.0)))
face_bot = f.advanced_face([f.face_outer_bound(bot_loop)], f.plane(ax_bot))

# Top face
top_loop = f.edge_loop([f.oriented_edge(et0, True), f.oriented_edge(et1, True),
                        f.oriented_edge(et2, True), f.oriented_edge(et3, True)])
ax_top = f.axis2_placement_3d(p001, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
face_top = f.advanced_face([f.face_outer_bound(top_loop)], f.plane(ax_top))

# Front face y=0
frt_loop = f.edge_loop([f.oriented_edge(eb0, True), f.oriented_edge(ev1, True),
                        f.oriented_edge(et0, False), f.oriented_edge(ev0, False)])
ax_frt = f.axis2_placement_3d(p000, f.direction((0.0, -1.0, 0.0)), f.direction((1.0, 0.0, 0.0)))
face_frt = f.advanced_face([f.face_outer_bound(frt_loop)], f.plane(ax_frt))

# Back face y=1
bk_loop = f.edge_loop([f.oriented_edge(ev3, True), f.oriented_edge(et2, False),
                       f.oriented_edge(ev2, False), f.oriented_edge(eb2, False)])
ax_bk = f.axis2_placement_3d(p010, f.direction((0.0, 1.0, 0.0)), f.direction((1.0, 0.0, 0.0)))
face_bk = f.advanced_face([f.face_outer_bound(bk_loop)], f.plane(ax_bk))

# Left face x=0
lft_loop = f.edge_loop([f.oriented_edge(ev0, True), f.oriented_edge(et3, False),
                        f.oriented_edge(ev3, False), f.oriented_edge(eb3, False)])
ax_lft = f.axis2_placement_3d(p000, f.direction((-1.0, 0.0, 0.0)), f.direction((0.0, 1.0, 0.0)))
face_lft = f.advanced_face([f.face_outer_bound(lft_loop)], f.plane(ax_lft))

# Right face x=1
rgt_loop = f.edge_loop([f.oriented_edge(eb1, True), f.oriented_edge(ev2, True),
                        f.oriented_edge(et1, False), f.oriented_edge(ev1, False)])
ax_rgt = f.axis2_placement_3d(p100, f.direction((1.0, 0.0, 0.0)), f.direction((0.0, 1.0, 0.0)))
face_rgt = f.advanced_face([f.face_outer_bound(rgt_loop)], f.plane(ax_rgt))

# ── CLOSED_SHELL: micro face + companion box ──────────────────────────────────
closed_sh = f.closed_shell([face_micro, face_bot, face_top, face_frt, face_bk, face_lft, face_rgt])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa077.stp")
