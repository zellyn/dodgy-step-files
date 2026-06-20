"""Tfa005 — Periodic face given by single belt wire (degenerate pole case).

Catalog claim: A periodic surface (sphere, cone, toroidal pole) is bounded
by a single closed wire that wraps once around the periodic direction. The
face has a degenerate pole and the wire crosses (or skirts) the apex/pole.

Mechanism: SHELL_BASED_SURFACE_MODEL with TWO ADVANCED_FACEs:
  face[0] on SPHERICAL_SURFACE — single belt wire passing through the pole
    vertex without a degenerate edge inserted
  face[1] on CONICAL_SURFACE — outer wire that passes through the apex
    vertex_point, no degenerate edge at the apex

OCC heals by inserting the implicit degenerate edge at the pole/apex.

Tier-3 assertions:
  face[0].surface_type == "sphere"
  face[1].surface_type == "cone"
  n_edges_total >= 8
  n_vertices_total >= 16

Expected: occt=shape(1)/shape(1) gmsh=shape(12) ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa005",
    defect=(
        "TWO ADVANCED_FACEs with single-belt wires on periodic surfaces: "
        "face[0] on SPHERICAL_SURFACE with 8-edge equatorial belt wire passing "
        "through the sphere's pole vertex — no degenerate edge at pole; "
        "face[1] on CONICAL_SURFACE with 8-edge outer wire whose endpoint "
        "is the cone apex vertex — no degenerate edge at apex; "
        "FixPeriodicDegenerated must insert the implicit degenerate edge at "
        "pole/apex to heal the face; both faces wired into OPEN_SHELL"
    ),
)

# ── SPHERE face (face[0]): radius=5, center at origin ─────────────────────────
sp_orig = f.cartesian_point((0.0, 0.0, 0.0))
sp_zdir = f.direction((0.0, 0.0, 1.0))
sp_xdir = f.direction((1.0, 0.0, 0.0))
sp_plc  = f.axis2_placement_3d(sp_orig, sp_zdir, sp_xdir)
sphere  = f.spherical_surface(sp_plc, 5.0)

# Single belt wire: 8-edge polygon starting at the north pole (0,0,5),
# going around the equator at 45° intervals, returning to north pole.
# The wire passes through the pole vertex without a degenerate edge.
sp_r = 5.0
sp_pole_pt = f.cartesian_point((0.0, 0.0, sp_r))   # north pole
sp_pole_v  = f.vertex_point(sp_pole_pt)

# 8 equatorial points at 45° intervals
sp_eq_pts = [
    f.cartesian_point((sp_r * _math.cos(a), sp_r * _math.sin(a), 0.0))
    for a in [i * _math.pi / 4 for i in range(8)]
]
sp_eq_verts = [f.vertex_point(p) for p in sp_eq_pts]

def make_line_edge(pa, pb, va, vb):
    dx = pb.args[1][0] - pa.args[1][0]
    dy = pb.args[1][1] - pa.args[1][1]
    dz = pb.args[1][2] - pa.args[1][2]
    length = (dx*dx + dy*dy + dz*dz) ** 0.5
    d   = f.direction((dx/length, dy/length, dz/length))
    vec = f.vector(d, length)
    ln  = f.line(pa, vec)
    return f.edge_curve(va, vb, ln)

# Wire: pole → eq[0] → eq[1] → ... → eq[7] → pole
# That gives 1 + 8 = 9 edges total for the sphere belt
sp_belt_edges = []
# pole → first equatorial point
sp_belt_edges.append(make_line_edge(sp_pole_pt, sp_eq_pts[0], sp_pole_v, sp_eq_verts[0]))
# equatorial ring
for i in range(7):
    sp_belt_edges.append(make_line_edge(
        sp_eq_pts[i], sp_eq_pts[i+1], sp_eq_verts[i], sp_eq_verts[i+1]
    ))
# last equatorial → pole (completing the belt without degenerate edge)
sp_belt_edges.append(make_line_edge(sp_eq_pts[7], sp_pole_pt, sp_eq_verts[7], sp_pole_v))

sp_belt_loop = f.edge_loop([f.oriented_edge(e, True) for e in sp_belt_edges])
sp_fob  = f.face_outer_bound(sp_belt_loop)
sphere_face = f.advanced_face([sp_fob], sphere)

# ── CONE face (face[1]): semi-angle=30°, radius=5, apex at (20,0,0)+z axis ───
# CONICAL_SURFACE(placement, radius, semi_angle)
# radius = bottom radius (at z=0 of local frame)
# Place apex at (20, 0, 5) by putting the axis at (20,0,0) pointing +Z
cn_orig = f.cartesian_point((20.0, 0.0, 0.0))
cn_zdir = f.direction((0.0, 0.0, 1.0))
cn_xdir = f.direction((1.0, 0.0, 0.0))
cn_plc  = f.axis2_placement_3d(cn_orig, cn_zdir, cn_xdir)
# semi_angle in radians; radius is the bottom radius
semi_angle = _math.pi / 6   # 30 degrees
cn_base_r  = 5.0
cone = f.conical_surface(cn_plc, cn_base_r, semi_angle)

# Cone apex: at cn_orig + (cn_base_r / tan(semi_angle)) * z_hat
# apex_z = cn_base_r / tan(semi_angle) = 5 / tan(30°) ≈ 8.66
apex_z  = cn_base_r / _math.tan(semi_angle)
cn_apex_pt  = f.cartesian_point((20.0, 0.0, apex_z))
cn_apex_v   = f.vertex_point(cn_apex_pt)

# 8 base-circle points at 45° intervals (at z=0 of cone local frame = global z=0)
cn_base_pts = [
    f.cartesian_point((20.0 + cn_base_r * _math.cos(a), cn_base_r * _math.sin(a), 0.0))
    for a in [i * _math.pi / 4 for i in range(8)]
]
cn_base_verts = [f.vertex_point(p) for p in cn_base_pts]

# Belt wire: apex → base[0] → base[1] → ... → base[7] → apex
# (no degenerate edge at apex — this IS the defect)
cn_belt_edges = []
# apex → first base point
cn_belt_edges.append(make_line_edge(cn_apex_pt, cn_base_pts[0], cn_apex_v, cn_base_verts[0]))
# base ring
for i in range(7):
    cn_belt_edges.append(make_line_edge(
        cn_base_pts[i], cn_base_pts[i+1], cn_base_verts[i], cn_base_verts[i+1]
    ))
# last base → apex (no degenerate edge — the missing element FixPeriodicDegenerated must add)
cn_belt_edges.append(make_line_edge(cn_base_pts[7], cn_apex_pt, cn_base_verts[7], cn_apex_v))

cn_belt_loop = f.edge_loop([f.oriented_edge(e, True) for e in cn_belt_edges])
cn_fob  = f.face_outer_bound(cn_belt_loop)
cone_face = f.advanced_face([cn_fob], cone)

# ── Wire faces into OPEN_SHELL → SBSM → product chain ────────────────────────
# face[0] = sphere, face[1] = cone (matching tier-3 assertions)
shell = f.open_shell([sphere_face, cone_face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa005.stp")
