"""Tfa050 — Pin face produces edge-correspondence map for healing.

Catalog claim: As Tfa049 but additionally builds a map from old edges to new
edges that result from snipping the pin. Healing relies on this map to splice
the trimmed face back into its incident shell without leaving naked edges.

Reproducer recipe (from catalog): Same long thin triangular ADVANCED_FACE as
Tfa049 — vertices (0,0,0), (10,0.001,0), (10,-0.001,0).

Mechanism: Identical geometry to Tfa049. The defect is the same triangular
pin face, but the analyzer is ShapeAnalysis_CheckSmallFace::CheckPinFace
which returns the 2-entry edge correspondence map (old→new) for the two long
edges that get split when the pin is snipped at a re-bounding vertex.

The fixture is a triangular prism (extruded 1mm in Z):
  face[0]: front triangle at z=0  — the defective pin face
  face[1]: back triangle at z=1
  face[2]: top sliver side (tip→top extruded)
  face[3]: bottom sliver side (tip→bot extruded)
  face[4]: base rectangular side (top→bot at x=10)

Tier-3 assertions:
  face[0].sliver_aspect_max_min > 1e3
  n_edges_total >= 3
  face[0].surface_type == "plane"
  n_vertices_total >= 6

Expected: occt=shape(1)/shape(1) gmsh=shape(7) ifc=schema_n/a
"""
import math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa050",
    defect=(
        "CLOSED_SHELL: face[0] is triangular pin ADVANCED_FACE on PLANE at z=0; "
        "pin tip at (0,0,0); base vertices at (10,0.001,0) and (10,-0.001,0); "
        "aspect ratio ≈ 10/0.001 = 1e4 > 1e3 (pin face criterion); "
        "ShapeAnalysis_CheckSmallFace::CheckPinFace builds 2-entry edge map; "
        "map captures: long-edge-tip-top → split-edges-A, long-edge-tip-bot → split-edges-B; "
        "caller uses map to splice trimmed face back into shell without naked edges; "
        "prism extruded 1mm in Z to form closed shell; "
        "defect IS on live CLOSED_SHELL traversal path"
    ),
)

# Pin face vertices (same as Tfa049)
tip_x, tip_y = 0.0, 0.0
top_x, top_y = 10.0, 0.001
bot_x, bot_y = 10.0, -0.001

def _len3(ax, ay, az, bx, by, bz):
    return math.sqrt((bx-ax)**2 + (by-ay)**2 + (bz-az)**2)

def _dir3(ax, ay, az, bx, by, bz):
    d = _len3(ax, ay, az, bx, by, bz)
    return ((bx-ax)/d, (by-ay)/d, (bz-az)/d)

# Points at z=0 (front triangular face)
p_tip0 = f.cartesian_point((tip_x, tip_y, 0.0))
p_top0 = f.cartesian_point((top_x, top_y, 0.0))
p_bot0 = f.cartesian_point((bot_x, bot_y, 0.0))

# Points at z=1 (back triangular face)
p_tip1 = f.cartesian_point((tip_x, tip_y, 1.0))
p_top1 = f.cartesian_point((top_x, top_y, 1.0))
p_bot1 = f.cartesian_point((bot_x, bot_y, 1.0))

v_tip0 = f.vertex_point(p_tip0); v_top0 = f.vertex_point(p_top0); v_bot0 = f.vertex_point(p_bot0)
v_tip1 = f.vertex_point(p_tip1); v_top1 = f.vertex_point(p_top1); v_bot1 = f.vertex_point(p_bot1)

# Front face edges (z=0)
L_tt = _len3(tip_x, tip_y, 0.0, top_x, top_y, 0.0)
L_tb = _len3(top_x, top_y, 0.0, bot_x, bot_y, 0.0)
L_bt = _len3(bot_x, bot_y, 0.0, tip_x, tip_y, 0.0)

ec_tip_top0 = f.edge_curve(v_tip0, v_top0,
    f.line(p_tip0, f.vector(f.direction(_dir3(tip_x, tip_y, 0.0, top_x, top_y, 0.0)), L_tt)))
ec_top_bot0 = f.edge_curve(v_top0, v_bot0,
    f.line(p_top0, f.vector(f.direction(_dir3(top_x, top_y, 0.0, bot_x, bot_y, 0.0)), L_tb)))
ec_bot_tip0 = f.edge_curve(v_bot0, v_tip0,
    f.line(p_bot0, f.vector(f.direction(_dir3(bot_x, bot_y, 0.0, tip_x, tip_y, 0.0)), L_bt)))

# Back face edges (z=1)
ec_tip_top1 = f.edge_curve(v_tip1, v_top1,
    f.line(p_tip1, f.vector(f.direction(_dir3(tip_x, tip_y, 0.0, top_x, top_y, 0.0)), L_tt)))
ec_top_bot1 = f.edge_curve(v_top1, v_bot1,
    f.line(p_top1, f.vector(f.direction(_dir3(top_x, top_y, 0.0, bot_x, bot_y, 0.0)), L_tb)))
ec_bot_tip1 = f.edge_curve(v_bot1, v_tip1,
    f.line(p_bot1, f.vector(f.direction(_dir3(bot_x, bot_y, 0.0, tip_x, tip_y, 0.0)), L_bt)))

# Vertical edges (Z direction)
ec_tip_z = f.edge_curve(v_tip0, v_tip1, f.line(p_tip0, f.vector(f.direction((0.0, 0.0, 1.0)), 1.0)))
ec_top_z = f.edge_curve(v_top0, v_top1, f.line(p_top0, f.vector(f.direction((0.0, 0.0, 1.0)), 1.0)))
ec_bot_z = f.edge_curve(v_bot0, v_bot1, f.line(p_bot0, f.vector(f.direction((0.0, 0.0, 1.0)), 1.0)))

# ── face[0]: front triangular pin face at z=0 (THE DEFECT) ───────────────────
front_loop = f.edge_loop([
    f.oriented_edge(ec_tip_top0, True),
    f.oriented_edge(ec_top_bot0, True),
    f.oriented_edge(ec_bot_tip0, True),
])
ax_frt = f.axis2_placement_3d(p_tip0, f.direction((0.0, 0.0, -1.0)), f.direction((1.0, 0.0, 0.0)))
face0 = f.advanced_face([f.face_outer_bound(front_loop)], f.plane(ax_frt))

# ── face[1]: back triangular face at z=1 ─────────────────────────────────────
back_loop = f.edge_loop([
    f.oriented_edge(ec_tip_top1, True),
    f.oriented_edge(ec_top_bot1, True),
    f.oriented_edge(ec_bot_tip1, True),
])
ax_bk = f.axis2_placement_3d(p_tip1, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0)))
face1 = f.advanced_face([f.face_outer_bound(back_loop)], f.plane(ax_bk))

# ── face[2]: top sliver side (tip→top edge extruded in Z) ────────────────────
top_side_loop = f.edge_loop([
    f.oriented_edge(ec_tip_top0, True),
    f.oriented_edge(ec_top_z,    True),
    f.oriented_edge(ec_tip_top1, False),
    f.oriented_edge(ec_tip_z,    False),
])
dx_tt = top_x - tip_x; dy_tt = top_y - tip_y
n_len = math.sqrt(dy_tt**2 + dx_tt**2)
n_top_side = (dy_tt/n_len, -dx_tt/n_len, 0.0)
ax_ts = f.axis2_placement_3d(p_tip0, f.direction(n_top_side), f.direction(_dir3(tip_x, tip_y, 0.0, top_x, top_y, 0.0)))
face2 = f.advanced_face([f.face_outer_bound(top_side_loop)], f.plane(ax_ts))

# ── face[3]: bottom sliver side (tip→bot edge extruded in Z) ─────────────────
bot_side_loop = f.edge_loop([
    f.oriented_edge(ec_bot_tip0, True),
    f.oriented_edge(ec_tip_z,    True),
    f.oriented_edge(ec_bot_tip1, False),
    f.oriented_edge(ec_bot_z,    False),
])
dx_bt = tip_x - bot_x; dy_bt = tip_y - bot_y
n_bot_side = (dy_bt/n_len, -dx_bt/n_len, 0.0)
ax_bs = f.axis2_placement_3d(p_bot0, f.direction(n_bot_side), f.direction(_dir3(bot_x, bot_y, 0.0, tip_x, tip_y, 0.0)))
face3 = f.advanced_face([f.face_outer_bound(bot_side_loop)], f.plane(ax_bs))

# ── face[4]: base rectangular side at x=10 (top→bot extruded in Z) ───────────
base_loop = f.edge_loop([
    f.oriented_edge(ec_top_bot0, True),
    f.oriented_edge(ec_bot_z,    True),
    f.oriented_edge(ec_top_bot1, False),
    f.oriented_edge(ec_top_z,    False),
])
ax_base = f.axis2_placement_3d(p_top0, f.direction((1.0, 0.0, 0.0)), f.direction((0.0, 1.0, 0.0)))
face4 = f.advanced_face([f.face_outer_bound(base_loop)], f.plane(ax_base))

# ── CLOSED_SHELL + MANIFOLD_SOLID_BREP ────────────────────────────────────────
closed_sh = f.closed_shell([face0, face1, face2, face3, face4])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa050.stp")
