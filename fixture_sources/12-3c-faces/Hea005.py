"""Hea005 — Triangular notch detour detected on a free-bound EDGE_LOOP contour.

Catalog claim: A free-bound contour (EDGE_LOOP / outer wire) has a notch:
a sharp inward triangular detour where a straight side has been broken into
3+ ORIENTED_EDGEs through extra VERTEX_POINTs offset perpendicular to the
main side. Detour pattern: (0,0)->(4.5,0)->(5.0,0.05)->(5.5,0)->(10,0).

The kernel (ShapeAnalysis_FreeBoundsProperties::CheckNotches) must report
each notch with (location, width, depth) so the user can decide whether
to flatten or split the host face.

Mechanism: OPEN_SHELL with one 10×10 rectangular ADVANCED_FACE on a PLANE.
The bottom edge is replaced by a 3-edge notch detour:
  - bottom-1: V1(0,0) -> V_notch_a(4.5,0)          [along +X]
  - notch_up:  V_notch_a -> V_notch_apex(5.0,0.05)  [angled up]
  - notch_dn:  V_notch_apex -> V_notch_b(5.5,0)     [angled down]
  - bottom-2:  V_notch_b -> V2(10,0)                [along +X]
Plus right, top, left = 7 total ORIENTED_EDGEs.

Tier-3 assertions:
  n_edges_total >= 7
  face[0].surface_type == "plane"
  n_vertices_total >= 8

Expected: occt=shape(1)/shape(1) gmsh=shape(15) ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Hea005",
    defect=(
        "OPEN_SHELL with 10x10 face on PLANE; "
        "bottom edge replaced by triangular notch detour: "
        "V1(0,0)->V_notch_a(4.5,0)->V_notch_apex(5.0,0.05)->V_notch_b(5.5,0)->V2(10,0); "
        "7 total ORIENTED_EDGEs; "
        "ShapeAnalysis_FreeBoundsProperties::CheckNotches must report notch "
        "with width~1.0 and depth~0.05; "
        "defect: triangular bump on free-bound contour bottom side"
    ),
)

# ── Plane at origin ───────────────────────────────────────────────────────────
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# ── 7 vertices ────────────────────────────────────────────────────────────────
p_V1       = f.cartesian_point((0.0, 0.0, 0.0))
p_notch_a  = f.cartesian_point((4.5, 0.0, 0.0))
p_notch_ap = f.cartesian_point((5.0, 0.05, 0.0), name="notch_apex_inward")
p_notch_b  = f.cartesian_point((5.5, 0.0, 0.0))
p_V2       = f.cartesian_point((10.0, 0.0, 0.0))
p_V3       = f.cartesian_point((10.0, 10.0, 0.0))
p_V4       = f.cartesian_point((0.0, 10.0, 0.0))

v_V1       = f.vertex_point(p_V1, name="V1")
v_notch_a  = f.vertex_point(p_notch_a, name="V_notch_a")
v_notch_ap = f.vertex_point(p_notch_ap, name="V_notch_apex")
v_notch_b  = f.vertex_point(p_notch_b, name="V_notch_b")
v_V2       = f.vertex_point(p_V2, name="V2")
v_V3       = f.vertex_point(p_V3, name="V3")
v_V4       = f.vertex_point(p_V4, name="V4")

# ── Notch edges ───────────────────────────────────────────────────────────────
# bottom-1: V1 -> V_notch_a (4.5 units along +X)
ec_b1 = f.edge_curve(v_V1, v_notch_a,
                      f.line(p_V1, f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)),
                      name="b1")

# notch_up: V_notch_a(4.5,0) -> V_notch_apex(5.0,0.05)
# direction: dx=0.5, dy=0.05 -> mag = sqrt(0.25+0.0025) = sqrt(0.2525)
_mag_up = _math.sqrt(0.5**2 + 0.05**2)
_nu_dx  = 0.5  / _mag_up
_nu_dy  = 0.05 / _mag_up
ec_nu = f.edge_curve(v_notch_a, v_notch_ap,
                      f.line(p_notch_a, f.vector(f.direction((_nu_dx, _nu_dy, 0.0)), _mag_up)),
                      name="notch_up")

# notch_dn: V_notch_apex(5.0,0.05) -> V_notch_b(5.5,0)
# direction: dx=0.5, dy=-0.05
_nd_dx = 0.5  / _mag_up
_nd_dy = -0.05 / _mag_up
ec_nd = f.edge_curve(v_notch_ap, v_notch_b,
                      f.line(p_notch_ap, f.vector(f.direction((_nd_dx, _nd_dy, 0.0)), _mag_up)),
                      name="notch_down")

# bottom-2: V_notch_b(5.5,0) -> V2(10,0) (4.5 units along +X)
ec_b2 = f.edge_curve(v_notch_b, v_V2,
                      f.line(p_notch_b, f.vector(f.direction((1.0, 0.0, 0.0)), 1.0)),
                      name="b2")

# right: V2 -> V3
ec_r = f.edge_curve(v_V2, v_V3,
                     f.line(p_V2, f.vector(f.direction((0.0, 1.0, 0.0)), 1.0)),
                     name="right")
# top: V3 -> V4
ec_t = f.edge_curve(v_V3, v_V4,
                     f.line(p_V3, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)),
                     name="top")
# left: V4 -> V1
ec_l = f.edge_curve(v_V4, v_V1,
                     f.line(p_V4, f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)),
                     name="left")

# ── EDGE_LOOP: b1 + notch_up + notch_dn + b2 + right + top + left = 7 ────────
loop = f.edge_loop([
    f.oriented_edge(ec_b1, True),
    f.oriented_edge(ec_nu, True),
    f.oriented_edge(ec_nd, True),
    f.oriented_edge(ec_b2, True),
    f.oriented_edge(ec_r, True),
    f.oriented_edge(ec_t, True),
    f.oriented_edge(ec_l, True),
], name="outer_with_notch")
fob  = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane, name="face_with_notch")

shell = f.open_shell([face], name="shell_with_notch_contour")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Hea005.stp")
