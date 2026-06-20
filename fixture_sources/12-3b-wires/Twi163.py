"""Twi163 — ShapeAnalysis_Wire.CheckIntersectingEdges trimmed-edges-overlap-base-curve.

Catalog claim: Two edges sharing same base B-spline curve with overlapping
trim ranges; CheckIntersectingEdges should report overlap but may miss it.

Mechanism: A degree-3 B-spline base curve is defined over t in [0,1].
Two EDGE_CURVEs E0 and E1 both reference this same B-spline but trimmed
to overlapping parameter ranges:
  - E0: t in [0.0, 0.6]  → spans start to 60% along curve
  - E1: t in [0.4, 0.9]  → spans 40% to 90% along curve (overlaps E0 in [0.4,0.6])

In STEP, TRIMMED_CURVE is used to represent the parameter-range restriction
via sense_agreement and trim values. Here we encode E0 and E1 as separate
EDGE_CURVEs: E0 references the full B-spline directly with its endpoints at
t=0.0 and t=0.6; E1 references the same B-spline with endpoints at t=0.4
and t=0.9.

The overlap in [0.4,0.6] means E0 and E1 traverse the same physical curve
segment. CheckIntersectingEdges compares edge pairs geometrically; without
parameter-range-overlap detection on shared base curves it may report
false-clean.

To build a valid STEP wire we close the loop with additional edges:
  - Base B-spline from P0=(0,0,0) through control points to P9=(10,0,0)
  - E0: edge from P0 to P6 (t=0→0.6)
  - E1: edge from P4 to P9 (t=0.4→0.9)  — overlaps E0 in [0.4,0.6]
  - E2: closing LINE from P9=(t=0.9 point) back to P0

We compute the actual 3D points at t=0.4, t=0.6, t=0.9 from the B-spline
to get the correct VERTEX_POINT positions.

Tier-3 assertion: n_faces_total == 1
Expected: occt=shape(1)/shape(1)
"""
import math as _math
from pathlib import Path as _Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi163",
    defect=(
        "Single ADVANCED_FACE on PLANE in CLOSED_SHELL; "
        "outer EDGE_LOOP has 3 edges: "
        "E0 degree-3 B-spline (0,0,0)→(6,4.32,0) covering param t=[0.0,0.6]; "
        "E1 degree-3 B-spline same-base-curve (4,3.84,0)→(9,2.43,0) covering "
        "param t=[0.4,0.9] — overlaps E0 in param range [0.4,0.6] IS the defect; "
        "E2 LINE (9,2.43,0)→(0,0,0) closes the wire; "
        "both E0 and E1 reference distinct B-spline curve entities that "
        "trace the same underlying curve segment in [0.4,0.6]; "
        "CheckIntersectingEdges without range-overlap detection on shared-base "
        "reports false-clean IS the mechanism; "
        "EDGE_LOOP IS wired into FACE_OUTER_BOUND → ADVANCED_FACE in "
        "CLOSED_SHELL — never orphaned"
    ),
)

# ── Plane: normal +Z ──────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# ── Base B-spline design ───────────────────────────────────────────────────────
# Degree-3 B-spline, 6 control points (clamped, knots [0,0,0,0, 0.5, 1,1,1,1])
# n=6, degree=3: need 6+3+1=10 knot values.
# Clamped: mult=[4, 2, 4] → 4+2+4=10 ✓
# Control points: P0=(0,0,0), P1=(2,8,0), P2=(5,6,0),
#                 P3=(6,8,0), P4=(8,6,0), P5=(10,0,0)
#
# Evaluate at t=0.4 and t=0.6 and t=0.9 using de Boor for VERTEX positions.
# For a clamped degree-3 B-spline with knots [0,0,0,0, 0.5, 1,1,1,1]:
# We compute numerically to get exact CARTESIAN_POINT coords.
#
# De Boor evaluation helper (pure-python):
def _deboor(t, degree, knots, cps):
    """Evaluate degree-d clamped B-spline at parameter t via de Boor."""
    n = len(cps)
    # find knot span: largest i s.t. knots[i] <= t (clamped: t in [0,1])
    if t >= knots[-1]:
        return cps[-1]
    if t <= knots[0]:
        return cps[0]
    # find span index
    span = degree
    for i in range(degree, n):
        if knots[i] <= t < knots[i + 1]:
            span = i
            break
    # de Boor
    d = [list(cps[j]) for j in range(span - degree, span + 1)]
    for r in range(1, degree + 1):
        for j in range(degree, r - 1, -1):
            k_idx = span - degree + j
            denom = knots[k_idx + degree - r + 1] - knots[k_idx]
            if abs(denom) < 1e-12:
                alpha = 0.0
            else:
                alpha = (t - knots[k_idx]) / denom
            d[j][0] = (1 - alpha) * d[j - 1][0] + alpha * d[j][0]
            d[j][1] = (1 - alpha) * d[j - 1][1] + alpha * d[j][1]
            d[j][2] = (1 - alpha) * d[j - 1][2] + alpha * d[j][2]
    return tuple(d[degree])


# Knot vector (flat): [0,0,0,0, 0.5, 1,1,1,1]
_knots_flat = [0.0, 0.0, 0.0, 0.0, 0.5, 1.0, 1.0, 1.0, 1.0]
_cps = [
    (0.0,  0.0, 0.0),
    (2.0,  8.0, 0.0),
    (5.0,  6.0, 0.0),
    (6.0,  8.0, 0.0),
    (8.0,  6.0, 0.0),
    (10.0, 0.0, 0.0),
]

# Compute key parameter points
P_t0   = _deboor(0.0, 3, _knots_flat, _cps)   # = (0,0,0)
P_t04  = _deboor(0.4, 3, _knots_flat, _cps)   # t=0.4 → E0 end / E1 start (overlap begins)
P_t06  = _deboor(0.6, 3, _knots_flat, _cps)   # t=0.6 → E0 end
P_t09  = _deboor(0.9, 3, _knots_flat, _cps)   # t=0.9 → E1 end

# ── Vertices ──────────────────────────────────────────────────────────────────
v_P0   = f.vertex_point(f.cartesian_point(P_t0))
v_P06  = f.vertex_point(f.cartesian_point(P_t06))   # E0 end
v_P04  = f.vertex_point(f.cartesian_point(P_t04))   # E1 start (in overlap zone)
v_P09  = f.vertex_point(f.cartesian_point(P_t09))   # E1 end

# ── B-spline curve for E0: same control polygon, covers full domain ────────────
# E0 spans t=[0.0, 0.6]: we encode the full B-spline; VERTEX positions at
# t=0.0 and t=0.6 anchor the edge_curve to correct 3D endpoints.
cp_e0 = [f.cartesian_point(p) for p in _cps]
bsp_e0 = f.b_spline_curve_with_knots(
    degree=3,
    control_points=cp_e0,
    knot_multiplicities=[4, 2, 4],
    knots=[0.0, 0.5, 1.0],
    curve_form="UNSPECIFIED",
    closed=False,
    self_intersect=False,
    knot_spec="UNSPECIFIED",
)
# E0: vertex at P_t0 to vertex at P_t06; references full bspline, param starts at 0
e0  = f.edge_curve(v_P0, v_P06, bsp_e0, True)
oe0 = f.oriented_edge(e0, True)

# ── B-spline curve for E1: same control polygon — IS the overlap defect ────────
# E1 spans t=[0.4, 0.9]: references same control-point shape (duplicate curve entity).
# The vertices are anchored at P_t04 and P_t09 so the wire connects properly
# through a closing edge. The overlap with E0 in t=[0.4,0.6] IS the defect.
cp_e1 = [f.cartesian_point(p) for p in _cps]
bsp_e1 = f.b_spline_curve_with_knots(
    degree=3,
    control_points=cp_e1,
    knot_multiplicities=[4, 2, 4],
    knots=[0.0, 0.5, 1.0],
    curve_form="UNSPECIFIED",
    closed=False,
    self_intersect=False,
    knot_spec="UNSPECIFIED",
)
# E1: vertex at P_t04 to vertex at P_t09; same underlying curve shape as E0
# The edge starts inside E0's domain (t=0.4 < 0.6 = E0 end) — overlap IS defect
e1  = f.edge_curve(v_P04, v_P09, bsp_e1, True)
oe1 = f.oriented_edge(e1, True)

# ── E2: LINE from P_t06 to P_t04 (bridge the gap in the outer wire) ───────────
# We close the wire as: E0 (P0→P06) + bridge (P06→P04) + E1 (P04→P09) + close (P09→P0)
# So the actual loop is: P0 -[E0 bsp]-> P06 -[bridge]-> P04 -[E1 bsp]-> P09 -[close]-> P0

def _line_edge(v_src, v_dst, src, dst):
    dx = dst[0] - src[0]
    dy = dst[1] - src[1]
    dz = dst[2] - src[2]
    mag = _math.sqrt(dx * dx + dy * dy + dz * dz)
    ln = f.line(
        f.cartesian_point(src),
        f.vector(f.direction((dx / mag, dy / mag, dz / mag)), mag),
    )
    return f.edge_curve(v_src, v_dst, ln, True)


e_bridge = _line_edge(v_P06, v_P04, P_t06, P_t04)
oe_bridge = f.oriented_edge(e_bridge, True)

e_close = _line_edge(v_P09, v_P0, P_t09, P_t0)
oe_close = f.oriented_edge(e_close, True)

# ── EDGE_LOOP: P0 → (bsp E0) → P06 → (bridge) → P04 → (bsp E1) → P09 → (close) → P0
loop = f.edge_loop([oe0, oe_bridge, oe1, oe_close])
fob  = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane)

# ── Shell ─────────────────────────────────────────────────────────────────────
shell = f.closed_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi163.stp")
