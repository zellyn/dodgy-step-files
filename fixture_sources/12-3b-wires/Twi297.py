"""Twi297 — B-spline surface pinched to a single point at its V=0 boundary
(all V=0 control points coincident); the wire bounding the face touching
that pinch is missing its degenerate edge (missing subvariant of
tkshh-wire-missing-or-bad-degenerated-edge, distinct from Twi021's
analytic-cone-apex case; bug 24055 path).

Catalog claim (occt-coverage/tkshhealing/problems.json,
tkshh-wire-missing-or-bad-degenerated-edge, subvariant "B-spline surface
pinched to a point at a U- or V-boundary: pinch detected by 3D distance
test, degenerated edge at the pinch (FixMissingSeam, bug 24055)" —
evidence: ShapeFix_Face::FixMissingSeam, ShapeFix_Face.cxx:1657-1681,
the B-spline V/U pinch branch). Twi021 demonstrates the missing-degenerate
mechanism on an ANALYTIC CONICAL_SURFACE, whose apex is intrinsic to the
surface's quadric parametrization (ShapeAnalysis_Surface::
ComputeSingularities detects it directly from the cone's semi-angle).
A B_SPLINE_SURFACE has no such intrinsic-singularity flag — a pinch is
purely a PROPERTY OF THE CONTROL NET (an entire row of control points
placed at the identical 3D point), which FixMissingSeam's B-spline branch
must detect via an explicit 3D-distance test over the boundary's poles,
not by reading a semi-angle. This fixture's B_SPLINE_SURFACE_WITH_KNOTS
(u_degree=3, v_degree=1) has ALL FOUR of its V=0 control points set to the
identical point (0,0,5) -- a genuine full-row pinch -- while its V=1
control points spread into a real curved boundary.

Mechanism IS the half-patch ADVANCED_FACE on the B_SPLINE_SURFACE: because
v_degree=1, the two U=const lateral boundaries collapse to straight LINEs
from the pinch to the V=1 boundary's endpoints, and the V=1 boundary
itself is exactly the surface's own cubic Bezier control polygon (Q0..Q3)
-- both reused directly as the wire's EDGE_CURVE geometry (no
approximation). The wire's two lateral edges (u=0 and u=1) both terminate
at the SAME pinch point (0,0,5) but via TWO SEPARATE VERTEX_POINT
instances (mirroring Twi021's two-separate-apex-vertex pattern). NO
degenerate ORIENTED_EDGE bridges them. The defect EDGE_LOOP IS referenced
by a FACE_OUTER_BOUND in an ADVANCED_FACE in an OPEN_SHELL; never
orphaned.

Byte assertions:
  - count_entity_def(b'B_SPLINE_SURFACE_WITH_KNOTS') == 1
  - count_entity_def(b'VERTEX_POINT') >= 4
  - contains(b'(0.0,0.0,5.0)')

Tier-3 assertions:
  - face[0].surface_type == "bspline"
  - n_edges_total >= 3
  - n_vertices_total >= 6

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi297",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a B_SPLINE_SURFACE_WITH_KNOTS "
        "(u_degree=3, v_degree=1, 4x2 control net); ALL FOUR V=0 control points "
        "are the IDENTICAL point (0,0,5) -- a genuine full-row pinch, detected "
        "only via a 3D-distance test over the control net (unlike a CONICAL_SURFACE's "
        "intrinsic apex, Twi021's mechanism); V=1 control points Q0(3,0,0), "
        "Q1(3,3,0), Q2(0,4,0), Q3(-2,3,0) form a real curved boundary; "
        "FACE_OUTER_BOUND references an EDGE_LOOP with two LINE lateral edges "
        "(u=0: pinch->Q0; u=1: Q3->pinch -- both isoparametric straight lines "
        "since v_degree=1 makes the V-direction linear) plus one B_SPLINE_CURVE "
        "base edge (Q0->Q3, the surface's own V=1 control polygon, degree 3, "
        "reused exactly, no approximation); "
        "NO degenerate ORIENTED_EDGE inserted at the pinch -- the two lateral "
        "edges terminate at the SAME 3D point via TWO SEPARATE VERTEX_POINT "
        "instances, exactly mirroring Twi021's missing-apex-edge pattern but on "
        "a B-spline control-net pinch instead of an analytic cone; "
        "missing pinch-bridging degenerate edge IS the mechanism; "
        "pinch VERTEX_POINTs ARE wired into EDGE_LOOP lateral edges, "
        "FACE_OUTER_BOUND, ADVANCED_FACE, OPEN_SHELL; never orphaned; "
        "kernel must insert a degenerate edge at the pinch (ShapeFix_Face::"
        "FixMissingSeam B-spline branch, bug 24055) or reject as malformed"
    ),
)

APEX = (0.0, 0.0, 5.0)
Q0 = (3.0, 0.0, 0.0)
Q1 = (3.0, 3.0, 0.0)
Q2 = (0.0, 4.0, 0.0)
Q3 = (-2.0, 3.0, 0.0)

# ── Control net: grid[u][v], nu=4 (u_degree 3, no internal knot), nv=2
#    (v_degree 1, no internal knot). ALL v=0 poles == APEX (full-row pinch). ──
p_apex = f.cartesian_point(APEX)
p_q0 = f.cartesian_point(Q0)
p_q1 = f.cartesian_point(Q1)
p_q2 = f.cartesian_point(Q2)
p_q3 = f.cartesian_point(Q3)

grid = [
    [p_apex, p_q0],
    [f.cartesian_point(APEX), p_q1],
    [f.cartesian_point(APEX), p_q2],
    [f.cartesian_point(APEX), p_q3],
]

surf = f.b_spline_surface_with_knots(
    u_degree=3,
    v_degree=1,
    control_points_grid=grid,
    u_multiplicities=[4, 4],
    v_multiplicities=[2, 2],
    u_knots=[0.0, 1.0],
    v_knots=[0.0, 1.0],
)

# ── Two separate apex vertex instances -- no degenerate edge inserted ────────
v_apex_0 = f.vertex_point(f.cartesian_point(APEX))  # from u=0 lateral edge
v_apex_1 = f.vertex_point(f.cartesian_point(APEX))  # from u=1 lateral edge

v_q0 = f.vertex_point(p_q0)
v_q3 = f.vertex_point(p_q3)

# ── Lateral edge at u=0: straight LINE, pinch -> Q0 (isoparametric, v_degree=1) ─
lat0_dir_vec = (Q0[0] - APEX[0], Q0[1] - APEX[1], Q0[2] - APEX[2])
import math as _math
lat0_len = _math.sqrt(sum(c * c for c in lat0_dir_vec))
lat0_dir = f.direction(tuple(c / lat0_len for c in lat0_dir_vec))
lat0_ln = f.line(f.cartesian_point(APEX), f.vector(lat0_dir, lat0_len))
edge_lat0 = f.edge_curve(v_apex_0, v_q0, lat0_ln)
oe_lat0 = f.oriented_edge(edge_lat0, True)

# ── Base edge Q0 -> Q3: exactly the surface's own V=1 cubic Bezier control
#    polygon (degree 3, no internal knots) -- reused, not approximated ───────
base_curve = f.b_spline_curve_with_knots(
    degree=3,
    control_points=[p_q0, p_q1, p_q2, p_q3],
    knot_multiplicities=[4, 4],
    knots=[0.0, 1.0],
)
edge_base = f.edge_curve(v_q0, v_q3, base_curve)
oe_base = f.oriented_edge(edge_base, True)

# ── Lateral edge at u=1: straight LINE, Q3 -> pinch ──────────────────────────
lat1_dir_vec = (APEX[0] - Q3[0], APEX[1] - Q3[1], APEX[2] - Q3[2])
lat1_len = _math.sqrt(sum(c * c for c in lat1_dir_vec))
lat1_dir = f.direction(tuple(c / lat1_len for c in lat1_dir_vec))
lat1_ln = f.line(f.cartesian_point(Q3), f.vector(lat1_dir, lat1_len))
edge_lat1 = f.edge_curve(v_q3, v_apex_1, lat1_ln)
oe_lat1 = f.oriented_edge(edge_lat1, True)

# ── EDGE_LOOP: pinch_0 -> Q0 -> Q3 -> pinch_1 -- open at the pinch, no
#    degenerate edge bridges v_apex_0 <-> v_apex_1 (the defect) ──────────────
loop = f.edge_loop([oe_lat0, oe_base, oe_lat1])
fob = f.face_outer_bound(loop)
face = f.advanced_face([fob], surf)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
