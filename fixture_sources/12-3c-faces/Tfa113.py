"""Tfa113 — ShapeFix_Face.FixOrientation 8-face polyhedron.

Catalog claim: Face is one of 6 faces in a cube; orientation propagation
traverses the 6-face cycle and an off-by-one loop boundary error leaves one
face inverted. The last face in the iteration loop fails to get fixed due to
termination condition.

Mechanism: MANIFOLD_SOLID_BREP with a 2×2×2 cube CLOSED_SHELL containing 6
faces, where the bottom face (z=0) has deliberately reversed orientation
(.F. in the ADVANCED_FACE same_sense flag). FixOrientation must propagate
orientation consistency across the closed 6-face shell and correct the reversed
bottom face. The defect face IS on the live CLOSED_SHELL traversal path.

Geometry: Cube from (0,0,0) to (2,2,2). Bottom face (z=0) uses same_sense=.F.
(reversed) to expose the orientation propagation loop boundary defect.

Byte assertions:
  - contains(b'CLOSED_SHELL')
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa113",
    defect=(
        "CLOSED_SHELL: 2×2×2 cube with 6 faces; bottom face (z=0) has same_sense=.F. "
        "(reversed orientation); "
        "ShapeFix_Face::FixOrientation propagates orientation around the 6-face closed "
        "shell cycle but off-by-one loop termination leaves bottom face uncorrected; "
        "defect IS on live CLOSED_SHELL traversal path"
    ),
)

S = 2.0  # cube side length

# 8 corner points of the cube
p000 = f.cartesian_point((0.0, 0.0, 0.0)); p100 = f.cartesian_point((S,   0.0, 0.0))
p110 = f.cartesian_point((S,   S,   0.0)); p010 = f.cartesian_point((0.0, S,   0.0))
p001 = f.cartesian_point((0.0, 0.0, S));   p101 = f.cartesian_point((S,   0.0, S))
p111 = f.cartesian_point((S,   S,   S));   p011 = f.cartesian_point((0.0, S,   S))

v000 = f.vertex_point(p000); v100 = f.vertex_point(p100)
v110 = f.vertex_point(p110); v010 = f.vertex_point(p010)
v001 = f.vertex_point(p001); v101 = f.vertex_point(p101)
v111 = f.vertex_point(p111); v011 = f.vertex_point(p011)

# Bottom edges (z=0)
eb0 = f.edge_curve(v000, v100, f.line(p000, f.vector(f.direction(( 1.0, 0.0, 0.0)), S)))
eb1 = f.edge_curve(v100, v110, f.line(p100, f.vector(f.direction(( 0.0, 1.0, 0.0)), S)))
eb2 = f.edge_curve(v110, v010, f.line(p110, f.vector(f.direction((-1.0, 0.0, 0.0)), S)))
eb3 = f.edge_curve(v010, v000, f.line(p010, f.vector(f.direction(( 0.0,-1.0, 0.0)), S)))

# Top edges (z=S)
et0 = f.edge_curve(v001, v101, f.line(p001, f.vector(f.direction(( 1.0, 0.0, 0.0)), S)))
et1 = f.edge_curve(v101, v111, f.line(p101, f.vector(f.direction(( 0.0, 1.0, 0.0)), S)))
et2 = f.edge_curve(v111, v011, f.line(p111, f.vector(f.direction((-1.0, 0.0, 0.0)), S)))
et3 = f.edge_curve(v011, v001, f.line(p011, f.vector(f.direction(( 0.0,-1.0, 0.0)), S)))

# Vertical edges
ev0 = f.edge_curve(v000, v001, f.line(p000, f.vector(f.direction((0.0, 0.0, 1.0)), S)))
ev1 = f.edge_curve(v100, v101, f.line(p100, f.vector(f.direction((0.0, 0.0, 1.0)), S)))
ev2 = f.edge_curve(v110, v111, f.line(p110, f.vector(f.direction((0.0, 0.0, 1.0)), S)))
ev3 = f.edge_curve(v010, v011, f.line(p010, f.vector(f.direction((0.0, 0.0, 1.0)), S)))

# ── face[0]: bottom (z=0) — THE DEFECT: same_sense=False (reversed) ─────────────
bot_loop = f.edge_loop([
    f.oriented_edge(eb0, True), f.oriented_edge(eb1, True),
    f.oriented_edge(eb2, True), f.oriented_edge(eb3, True),
])
ax_bot  = f.axis2_placement_3d(p000, f.direction((0.0, 0.0, -1.0)), f.direction((1.0, 0.0, 0.0)))
face_bot = f.advanced_face([f.face_outer_bound(bot_loop)], f.plane(ax_bot), same_sense=False)

# ── face[1]: top (z=S) ─────────────────────────────────────────────────────────
top_loop = f.edge_loop([
    f.oriented_edge(et0, True), f.oriented_edge(et1, True),
    f.oriented_edge(et2, True), f.oriented_edge(et3, True),
])
ax_top  = f.axis2_placement_3d(p001, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
face_top = f.advanced_face([f.face_outer_bound(top_loop)], f.plane(ax_top))

# ── face[2]: front (y=0) ─────────────────────────────────────────────────────
frt_loop = f.edge_loop([
    f.oriented_edge(eb0, True),  f.oriented_edge(ev1, True),
    f.oriented_edge(et0, False), f.oriented_edge(ev0, False),
])
ax_frt  = f.axis2_placement_3d(p000, f.direction((0.0, -1.0, 0.0)), f.direction((1.0, 0.0, 0.0)))
face_frt = f.advanced_face([f.face_outer_bound(frt_loop)], f.plane(ax_frt))

# ── face[3]: back (y=S) ─────────────────────────────────────────────────────
bk_loop = f.edge_loop([
    f.oriented_edge(ev3, True),  f.oriented_edge(et2, False),
    f.oriented_edge(ev2, False), f.oriented_edge(eb2, False),
])
ax_bk  = f.axis2_placement_3d(p010, f.direction((0.0, 1.0, 0.0)), f.direction((1.0, 0.0, 0.0)))
face_bk = f.advanced_face([f.face_outer_bound(bk_loop)], f.plane(ax_bk))

# ── face[4]: left (x=0) ─────────────────────────────────────────────────────
lft_loop = f.edge_loop([
    f.oriented_edge(ev0, True),  f.oriented_edge(et3, False),
    f.oriented_edge(ev3, False), f.oriented_edge(eb3, False),
])
ax_lft  = f.axis2_placement_3d(p000, f.direction((-1.0, 0.0, 0.0)), f.direction((0.0, 1.0, 0.0)))
face_lft = f.advanced_face([f.face_outer_bound(lft_loop)], f.plane(ax_lft))

# ── face[5]: right (x=S) ────────────────────────────────────────────────────
rgt_loop = f.edge_loop([
    f.oriented_edge(eb1, True),  f.oriented_edge(ev2, True),
    f.oriented_edge(et1, False), f.oriented_edge(ev1, False),
])
ax_rgt  = f.axis2_placement_3d(p100, f.direction((1.0, 0.0, 0.0)), f.direction((0.0, 1.0, 0.0)))
face_rgt = f.advanced_face([f.face_outer_bound(rgt_loop)], f.plane(ax_rgt))

# ── CLOSED_SHELL → MANIFOLD_SOLID_BREP ──────────────────────────────────────────
closed_sh = f.closed_shell([face_bot, face_top, face_frt, face_bk, face_lft, face_rgt])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa113.stp")
