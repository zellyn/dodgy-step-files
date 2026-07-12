"""Twi287 — Full-period closed edge on a TOROIDAL_SURFACE belt (insurance
second fixture for seq-split-closed-edges; Twi019 covers the cylinder case —
this fixture is untouched-Twi019, distinct surface kind).

Catalog claim: An EDGE_CURVE whose underlying curve is closed (a full 360°
CIRCLE) is used as a single edge; start vertex equals end vertex. Consumers
that require every edge to be an open arc with two distinct endpoints need
the edge divided at a seam/interior point
(ShapeUpgrade_ShapeDivideClosedEdges, exposed as the `spltclosededges`
ShapeProcess operator). Twi019 demonstrates this on a CYLINDRICAL_SURFACE;
this fixture demonstrates the identical mechanism on a TOROIDAL_SURFACE belt
— a torus segment bounded by two full meridian (minor) circles — so the
insurance base does not rest on a single surface kind.

Mechanism IS the two full-period meridian EDGE_CURVEs (start==end vertex)
bounding a quarter-revolution belt of the torus: one at u=0, one at u=pi/2,
each a complete 360° circle around the tube cross-section. Two U-direction
arcs (at v=0 and v=pi, the outer and inner equators of the belt) connect the
two meridian circles into a closed EDGE_LOOP. The EDGE_LOOP IS wired into a
FACE_OUTER_BOUND on a TOROIDAL_SURFACE ADVANCED_FACE in an OPEN_SHELL; never
orphaned.

Byte assertions:
  - count_entity_def(b'TOROIDAL_SURFACE') == 1
  - count_entity_def(b'CIRCLE') >= 2

Tier-3 assertions:
  - face[0].surface_type == "torus"
  - n_edges_total >= 4
  - n_vertices_total >= 4

live oracle: occt=shape(1)/shape(1)
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi287",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a TOROIDAL_SURFACE (major=5, "
        "minor=2); FACE_OUTER_BOUND references an EDGE_LOOP bounding a "
        "quarter-revolution belt of the torus: two full-period meridian "
        "CIRCLE edges (start==end vertex) at u=0 and u=pi/2, connected by two "
        "U-direction arcs at v=0 (outer equator) and v=pi (inner equator); "
        "each meridian EDGE_CURVE wraps a full 360 degrees around the tube "
        "cross-section without being split — full-period closed edge with "
        "start==end vertex IS the mechanism, distinct surface kind (torus, "
        "not Twi019's cylinder); "
        "the EDGE_LOOP IS wired into FACE_OUTER_BOUND, ADVANCED_FACE, "
        "OPEN_SHELL, SHELL_BASED_SURFACE_MODEL — never orphaned; "
        "kernel must split each closed meridian edge at its seam parameter "
        "into two open arcs, or accept the closed single edge as a "
        "kernel-internal representation"
    ),
)

R = 5.0  # major radius (distance from torus axis to tube centre)
r = 2.0  # minor radius (tube radius)

def meridian_circle_and_vertex(u_angle: float):
    """Full 360-degree meridian (tube cross-section) circle at torus angle u.

    The tube-centre at angle u sits at (R*cos(u), R*sin(u), 0). The meridian
    plane contains the torus axis (+Z) and the radial direction at u; the
    circle's own axis (normal to that plane) is the tangential direction
    (-sin(u), cos(u), 0).
    """
    cx, cy = R * math.cos(u_angle), R * math.sin(u_angle)
    centre = f.cartesian_point((cx, cy, 0.0))
    tangential_axis = f.direction((-math.sin(u_angle), math.cos(u_angle), 0.0))
    # ref_direction: radial direction at u (points toward the seam vertex at v=0)
    radial_ref = f.direction((math.cos(u_angle), math.sin(u_angle), 0.0))
    plc = f.axis2_placement_3d(centre, tangential_axis, radial_ref)
    circle = f.circle(plc, r)
    # v=0 seam point: outer equator, at (R+r)*(cos u, sin u, 0)
    seam_pt = f.cartesian_point(((R + r) * math.cos(u_angle),
                                  (R + r) * math.sin(u_angle), 0.0))
    v_seam = f.vertex_point(seam_pt)
    edge = f.edge_curve(v_seam, v_seam, circle)   # DEFECT: full-period, start==end
    return edge, v_seam, cx, cy

# Two meridian circles bounding the belt: u=0 and u=pi/2
mer0_edge, v0_seam, _, _ = meridian_circle_and_vertex(0.0)
mer1_edge, v1_seam, _, _ = meridian_circle_and_vertex(math.pi / 2.0)

# ── Outer-equator arc (v=0): connects the two meridian seam vertices along
#    the outer rim of the torus, u: 0 -> pi/2, radius R+r, centred on torus axis
outer_ctr = f.cartesian_point((0.0, 0.0, 0.0))
outer_axis = f.direction((0.0, 0.0, 1.0))
outer_ref  = f.direction((1.0, 0.0, 0.0))
outer_plc  = f.axis2_placement_3d(outer_ctr, outer_axis, outer_ref)
outer_circ = f.circle(outer_plc, R + r)
outer_edge = f.edge_curve(v0_seam, v1_seam, outer_circ)

# ── Inner-equator arc (v=pi): connects the two meridian seam vertices along
#    the inner rim of the torus, u: 0 -> pi/2, radius R-r
inner_pt0 = f.cartesian_point(((R - r) * math.cos(0.0), (R - r) * math.sin(0.0), 0.0))
inner_pt1 = f.cartesian_point(((R - r) * math.cos(math.pi / 2.0),
                                (R - r) * math.sin(math.pi / 2.0), 0.0))
v_inner0 = f.vertex_point(inner_pt0)
v_inner1 = f.vertex_point(inner_pt1)
inner_ctr = f.cartesian_point((0.0, 0.0, 0.0))
inner_axis = f.direction((0.0, 0.0, -1.0))
inner_ref  = f.direction((1.0, 0.0, 0.0))
inner_plc  = f.axis2_placement_3d(inner_ctr, inner_axis, inner_ref)
inner_circ = f.circle(inner_plc, R - r)
inner_edge = f.edge_curve(v_inner1, v_inner0, inner_circ)

# ── TOROIDAL_SURFACE ──────────────────────────────────────────────────────────
torus_orig = f.cartesian_point((0.0, 0.0, 0.0))
torus_ax   = f.direction((0.0, 0.0, 1.0))
torus_ref  = f.direction((1.0, 0.0, 0.0))
torus_plc  = f.axis2_placement_3d(torus_orig, torus_ax, torus_ref)
torus_surf = f.toroidal_surface(torus_plc, R, r)

# ── EDGE_LOOP: meridian(u=0) -> outer-equator(u:0->pi/2) -> meridian(u=pi/2,
#    reversed) -> inner-equator(u:pi/2->0) ───────────────────────────────────
loop = f.edge_loop([
    f.oriented_edge(mer0_edge,  True),
    f.oriented_edge(outer_edge, True),
    f.oriented_edge(mer1_edge,  False),
    f.oriented_edge(inner_edge, True),
])
fob   = f.face_outer_bound(loop)
face  = f.advanced_face([fob], torus_surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
