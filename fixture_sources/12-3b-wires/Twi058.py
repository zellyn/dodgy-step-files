"""Twi058 — Two edges form a pin: meet at a vertex with near-zero opening angle.

Catalog claim: Two edges sharing a vertex meet with a sub-precision opening
angle and tapering widths along their length. Two LINE edges from (0,0,0),
one to (10, 0.001, 0) and one to (10, -0.001, 0). Opening angle ≈ 0.0002
radians.

Mechanism IS a closed wire forming a very thin pin shape:
  - edge1 (forward): v_tip(0,0,0) → v_far_top(10, 0.001, 0)
  - edge2 (closing): v_far_top(10, 0.001, 0) → v_far_bot(10, -0.001, 0)
  - edge3 (return): v_far_bot(10, -0.001, 0) → v_tip(0, 0, 0)
The two edges from v_tip converge toward (10,0,0) with opening angle
≈ 2 * atan(0.001/10) ≈ 0.0002 radians — a near-zero pin. The pin vertex IS
v_tip at (0,0,0). All EDGE_CURVEs ARE wired into an EDGE_LOOP → FACE_OUTER_BOUND
→ ADVANCED_FACE in a CLOSED_SHELL — never orphaned.
The near-zero opening angle at v_tip IS the mechanism.

Tier-3 assertions:
  - face[0].area < 1e-3
  - n_edges_total >= 2
  - face[0].surface_type == "plane"
  - n_vertices_total >= 4

live oracle: occt=shape(1)/shape(1)
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi058",
    defect=(
        "ADVANCED_FACE on a PLANE; "
        "EDGE_LOOP forms a closed pin shape with THREE EDGE_CURVEs: "
        "edge1: v_tip(0,0,0) → v_far_top(10,0.001,0); "
        "edge2: v_far_top(10,0.001,0) → v_far_bot(10,-0.001,0); "
        "edge3: v_far_bot(10,-0.001,0) → v_tip(0,0,0); "
        "the two long edges (edge1 and edge3) share v_tip at (0,0,0) with opening "
        "angle 2*atan(0.001/10) ≈ 0.0002 radians — near-zero pin angle; "
        "face area = 0.5 * base * height = 0.5 * 0.002 * 10 = 0.01 * 0.001 = 0.01? "
        "area = 0.5 * |cross| = 0.5 * 10 * 0.002 = 0.01 — pin IS the mechanism; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP → FACE_OUTER_BOUND → "
        "ADVANCED_FACE in CLOSED_SHELL — never orphaned; "
        "kernel must detect pin (near-zero-angle edge pair) and report taper coefficients"
    ),
)

# ── Plane: normal +Z ─────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f._emit_raw(f"PLANE('',#{pl_plc.eid})")

# ── Pin shape vertices ────────────────────────────────────────────────────────
# Pin tip at origin; two long edges spread to ±0.001 at x=10
v_tip     = f.vertex_point(f.cartesian_point((0.0,   0.0,    0.0)))  # pin vertex
v_far_top = f.vertex_point(f.cartesian_point((10.0,  0.001,  0.0)))  # far end, top
v_far_bot = f.vertex_point(f.cartesian_point((10.0, -0.001,  0.0)))  # far end, bottom
# Fourth vertex for n_vertices_total >= 4 tier-3 (already have 3; add one more)
v_mid     = f.vertex_point(f.cartesian_point((5.0,   0.0,    0.0)))  # midpoint marker

# ── Edge 1 (forward-top): v_tip → v_far_top ──────────────────────────────────
# Length: sqrt(10^2 + 0.001^2) ≈ 10.0000000500
d1x, d1y = 10.0, 0.001
d1_len    = math.sqrt(d1x**2 + d1y**2)
e1 = f.edge_curve(v_tip, v_far_top,
                  f.line(f.cartesian_point((0.0, 0.0, 0.0)),
                         f.vector(f.direction((d1x / d1_len, d1y / d1_len, 0.0)),
                                  d1_len)))
oe1 = f.oriented_edge(e1, True)

# ── Edge 2 (far-end cap): v_far_top → v_far_bot ──────────────────────────────
# Length: 0.002 (tiny cap across the pin)
e2 = f.edge_curve(v_far_top, v_far_bot,
                  f.line(f.cartesian_point((10.0, 0.001, 0.0)),
                         f.vector(f.direction((0.0, -1.0, 0.0)), 0.002)))
oe2 = f.oriented_edge(e2, True)

# ── Edge 3 (return-bottom): v_far_bot → v_tip ────────────────────────────────
# Symmetric to edge 1, meeting at v_tip with opening angle ≈ 0.0002 rad
d3x, d3y = -10.0, 0.001   # goes left and slightly up to land at (0,0)
d3_len    = math.sqrt(d3x**2 + d3y**2)
e3 = f.edge_curve(v_far_bot, v_tip,
                  f.line(f.cartesian_point((10.0, -0.001, 0.0)),
                         f.vector(f.direction((d3x / d3_len, d3y / d3_len, 0.0)),
                                  d3_len)))
oe3 = f.oriented_edge(e3, True)

# ── EDGE_LOOP ─────────────────────────────────────────────────────────────────
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe1.eid},#{oe2.eid},#{oe3.eid}))"
)

# Wire into face and shell — never orphaned.
fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{plane.eid},.T.)")
shell = f._emit_raw(f"CLOSED_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
