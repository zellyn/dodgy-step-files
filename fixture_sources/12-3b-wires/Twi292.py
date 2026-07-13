"""Twi292 — Short arc straddling a closed curve's parameter seam: projected
endpoint parameters come back swapped (w1 > w2), requiring epsilon-safe
periodic range reconstruction (missing subvariant of
tkshh-closed-edge-full-period-unsplit, distinct from Twi019's start==end
full-period case).

Catalog claim (occt-coverage/tkshhealing/problems.json,
tkshh-closed-edge-full-period-unsplit): when a receiver derives an edge's
parametric range on a closed/periodic curve by projecting the two endpoint
vertices onto the curve's native [0, 2*pi) domain
(ShapeAnalysis_TransferParametersProj::TransferRange), an edge whose short
arc crosses the curve's own parameter seam (angle 0 / 2*pi) comes back with
the START parameter numerically GREATER than the END parameter (w1 > w2)
even though the edge is a short, ordinary, non-full-period arc. Naive
range construction (w2 - w1) either yields a negative length or silently
takes the long way around (350 degrees instead of 10); the correct fix
adds one period to the smaller parameter (epsilon-safe periodic
reconstruction) before computing the range. This is a DIFFERENT input
defect from Twi019 (whose single edge spans the FULL 360 degrees, start
vertex literally equal to end vertex) — here start and end are two
distinct, ordinary vertices bounding a genuine short arc; the defect is
purely in the RAW projected-parameter order, not in the topology.

Mechanism IS the pie-slice ADVANCED_FACE on a PLANE: two radial LINE edges
from the circle centre to the rim, joined by one CIRCLE-based EDGE_CURVE
arc whose start vertex sits at raw angle 355 degrees (w ~= 6.196 rad) and
whose end vertex sits at raw angle 5 degrees (w ~= 0.0873 rad) — the short
10-degree arc crosses the 0/2*pi seam, so naive projection gives
start_param(6.196) > end_param(0.0873), the swapped-order input. The arc
edge IS referenced by the wire's EDGE_LOOP, which IS referenced by a
FACE_OUTER_BOUND in an ADVANCED_FACE in an OPEN_SHELL; never orphaned.

Byte assertions:
  - count_entity_def(b'CIRCLE') == 1
  - contains(b'seam_straddle_arc')

Tier-3 assertions:
  - face[0].surface_type == "plane"
  - n_edges_total >= 3
  - n_vertices_total >= 3

live oracle: occt=shape(1)/shape(1)
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi292",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a PLANE; FACE_OUTER_BOUND "
        "references an EDGE_LOOP forming a thin pie-slice wedge: one CIRCLE-based "
        "EDGE_CURVE 'seam_straddle_arc' from raw angle 355deg (w~=6.196rad) to raw "
        "angle 5deg (w~=0.0873rad) — a genuine short 10-degree arc that crosses the "
        "circle's own 0/2*pi parameter seam, so naive endpoint-parameter projection "
        "yields start_param > end_param (swapped order) even though the edge is not "
        "full-period (distinct start/end vertices, not Twi019's start==end case); "
        "plus two radial LINE edges from the rim back to the circle centre closing "
        "the wedge; kernel must add one period to the smaller projected parameter "
        "(epsilon-safe periodic range reconstruction) rather than compute a negative "
        "or 350-degree-long-way range; "
        "arc edge IS wired into EDGE_LOOP, FACE_OUTER_BOUND, ADVANCED_FACE, OPEN_SHELL; "
        "never orphaned"
    ),
)

RADIUS = 3.0
ANGLE_START_DEG = 355.0
ANGLE_END_DEG = 5.0

theta_start = math.radians(ANGLE_START_DEG)
theta_end = math.radians(ANGLE_END_DEG)

p_start = (RADIUS * math.cos(theta_start), RADIUS * math.sin(theta_start), 0.0)
p_end = (RADIUS * math.cos(theta_end), RADIUS * math.sin(theta_end), 0.0)
p_centre = (0.0, 0.0, 0.0)

v_start = f.vertex_point(f.cartesian_point(p_start))
v_end = f.vertex_point(f.cartesian_point(p_end))
v_centre = f.vertex_point(f.cartesian_point(p_centre))

# ── CIRCLE: centre at origin, radius 3, in the XY plane (theta=0 at +X) ──────
circ_orig = f.cartesian_point((0.0, 0.0, 0.0))
circ_zdir = f.direction((0.0, 0.0, 1.0))
circ_xdir = f.direction((1.0, 0.0, 0.0))
circ_plc = f.axis2_placement_3d(circ_orig, circ_zdir, circ_xdir)
circle = f._emit_raw(f"CIRCLE('',#{circ_plc.eid},{RADIUS:.10f})")

# Arc: start(355deg) -> end(5deg), short way through the seam at theta=0.
# Named for the byte assertion.
arc_edge = f._emit_raw(
    f"EDGE_CURVE('seam_straddle_arc',#{v_start.eid},#{v_end.eid},#{circle.eid},.T.)"
)
arc_oe = f.oriented_edge(arc_edge, True)

# Radial line: end(5deg) -> centre
dx, dy, dz = (p_centre[0] - p_end[0], p_centre[1] - p_end[1], p_centre[2] - p_end[2])
mag = math.hypot(dx, dy)
rad1_dir = f.direction((dx / mag, dy / mag, 0.0))
rad1_ln = f.line(f.cartesian_point(p_end), f.vector(rad1_dir, mag))
rad1_edge = f.edge_curve(v_end, v_centre, rad1_ln)
rad1_oe = f.oriented_edge(rad1_edge, True)

# Radial line: centre -> start(355deg)
dx2, dy2, dz2 = (p_start[0] - p_centre[0], p_start[1] - p_centre[1], p_start[2] - p_centre[2])
mag2 = math.hypot(dx2, dy2)
rad2_dir = f.direction((dx2 / mag2, dy2 / mag2, 0.0))
rad2_ln = f.line(f.cartesian_point(p_centre), f.vector(rad2_dir, mag2))
rad2_edge = f.edge_curve(v_centre, v_start, rad2_ln)
rad2_oe = f.oriented_edge(rad2_edge, True)

loop = f.edge_loop([arc_oe, rad1_oe, rad2_oe])
fob = f.face_outer_bound(loop)

plane_orig = f.cartesian_point((0.0, 0.0, 0.0))
plane_zdir = f.direction((0.0, 0.0, 1.0))
plane_xdir = f.direction((1.0, 0.0, 0.0))
plane_plc = f.axis2_placement_3d(plane_orig, plane_zdir, plane_xdir)
plane = f.plane(plane_plc)

face = f.advanced_face([fob], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
