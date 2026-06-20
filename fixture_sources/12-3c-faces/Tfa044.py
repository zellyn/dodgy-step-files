"""Tfa044 — Pin face: long thin protrusion at a vertex.

Catalog claim: A face whose outer wire pinches to a single near-vertex pin; a
sharp protrusion whose width tapers to 0 at one corner. Subsequent
meshing/Boolean operations corrupt at the pin tip.

Reproducer recipe (from catalog): A triangular face with vertices at (0,0),
(10, 0.001), (10, -0.001) — opening angle ≈ 0.0002 rad.

Mechanism: face[0] is a triangular ADVANCED_FACE on a PLANE at z=0.
  - v_tip: (0, 0, 0) — the pin tip (width = 0 here)
  - v_top: (10, 0.001, 0) — top of the base
  - v_bot: (10, -0.001, 0) — bottom of the base
  - long edges: tip→top (length≈10) and tip→bot (length≈10)
  - short base edge: top→bot (length=0.002)
  - aspect ratio ≈ 10/0.001 = 1e4 > 1e3 (pin-face criterion)
  - 3 edges, so n_edges_total >= 3 is met by face[0] alone

A valid 10×10 reference face is face[1] at z=1 to ensure shape(1) and meet
n_vertices_total >= 6.

Tier-3 assertions:
  face[0].sliver_aspect_max_min > 1e3
  n_edges_total >= 3
  face[0].surface_type == "plane"
  n_vertices_total >= 6

Expected: occt=shape(1)/shape(1) gmsh=shape(7) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path
import math

f = StepFile(
    catalog_id="Tfa044",
    defect=(
        "OPEN_SHELL: face[0] is triangular pin ADVANCED_FACE on PLANE at z=0; "
        "pin tip at (0,0,0); base vertices at (10,0.001,0) and (10,-0.001,0); "
        "opening angle ≈ 0.0002 rad; long-edge length ≈ 10; base width = 0.002; "
        "aspect ratio ≈ 10/0.001 = 1e4 > 1e3 (pin face criterion); "
        "ShapeFix_FixSmallFace::FixPinFace must detect and repair; "
        "face[1] is valid 10×10 plane to ensure shape(1); "
        "defect IS on live OPEN_SHELL traversal path"
    ),
)

# ── face[0]: triangular pin face ──────────────────────────────────────────────
# tip=(0,0), top=(10,+0.001), bot=(10,-0.001) all at z=0
tip_xy = (0.0, 0.0)
top_xy = (10.0, 0.001)
bot_xy = (10.0, -0.001)

def _len(ax, ay, bx, by):
    return math.sqrt((bx-ax)**2 + (by-ay)**2)

def _dir(ax, ay, bx, by):
    d = _len(ax, ay, bx, by)
    return ((bx-ax)/d, (by-ay)/d, 0.0)

p_tip = f.cartesian_point((tip_xy[0], tip_xy[1], 0.0))
p_top = f.cartesian_point((top_xy[0], top_xy[1], 0.0))
p_bot = f.cartesian_point((bot_xy[0], bot_xy[1], 0.0))

v_tip = f.vertex_point(p_tip)
v_top = f.vertex_point(p_top)
v_bot = f.vertex_point(p_bot)

# edges: tip→top, top→bot, bot→tip
L_tip_top = _len(tip_xy[0], tip_xy[1], top_xy[0], top_xy[1])
L_top_bot = _len(top_xy[0], top_xy[1], bot_xy[0], bot_xy[1])
L_bot_tip = _len(bot_xy[0], bot_xy[1], tip_xy[0], tip_xy[1])

ec_tip_top = f.edge_curve(
    v_tip, v_top,
    f.line(p_tip, f.vector(f.direction(_dir(tip_xy[0], tip_xy[1], top_xy[0], top_xy[1])), L_tip_top))
)
ec_top_bot = f.edge_curve(
    v_top, v_bot,
    f.line(p_top, f.vector(f.direction(_dir(top_xy[0], top_xy[1], bot_xy[0], bot_xy[1])), L_top_bot))
)
ec_bot_tip = f.edge_curve(
    v_bot, v_tip,
    f.line(p_bot, f.vector(f.direction(_dir(bot_xy[0], bot_xy[1], tip_xy[0], tip_xy[1])), L_bot_tip))
)

pin_loop = f.edge_loop([
    f.oriented_edge(ec_tip_top, True),
    f.oriented_edge(ec_top_bot, True),
    f.oriented_edge(ec_bot_tip, True),
])

pin_orig  = f.cartesian_point((0.0, 0.0, 0.0))
pin_zdir  = f.direction((0.0, 0.0, 1.0))
pin_xdir  = f.direction((1.0, 0.0, 0.0))
pin_plc   = f.axis2_placement_3d(pin_orig, pin_zdir, pin_xdir)
pin_plane = f.plane(pin_plc)
face0 = f.advanced_face([f.face_outer_bound(pin_loop)], pin_plane)

# ── face[1]: valid 10×10 reference plane at z=1 (offset to avoid collision) ───
p0 = f.cartesian_point((  0.0, 0.0, 1.0))
p1 = f.cartesian_point(( 10.0, 0.0, 1.0))
p2 = f.cartesian_point(( 10.0,10.0, 1.0))
p3 = f.cartesian_point((  0.0,10.0, 1.0))
v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)

e0 = f.edge_curve(v0, v1, f.line(p0, f.vector(f.direction(( 1.0, 0.0, 0.0)), 10.0)))
e1 = f.edge_curve(v1, v2, f.line(p1, f.vector(f.direction(( 0.0, 1.0, 0.0)), 10.0)))
e2 = f.edge_curve(v2, v3, f.line(p2, f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0)))
e3 = f.edge_curve(v3, v0, f.line(p3, f.vector(f.direction(( 0.0,-1.0, 0.0)), 10.0)))

ref_loop  = f.edge_loop([
    f.oriented_edge(e0, True), f.oriented_edge(e1, True),
    f.oriented_edge(e2, True), f.oriented_edge(e3, True),
])
ref_orig  = f.cartesian_point((0.0, 0.0, 1.0))
ref_zdir  = f.direction((0.0, 0.0, 1.0))
ref_xdir  = f.direction((1.0, 0.0, 0.0))
ref_plc   = f.axis2_placement_3d(ref_orig, ref_zdir, ref_xdir)
ref_plane = f.plane(ref_plc)
face1 = f.advanced_face([f.face_outer_bound(ref_loop)], ref_plane)

# ── OPEN_SHELL ────────────────────────────────────────────────────────────────
shell = f.open_shell([face0, face1])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa044.stp")
