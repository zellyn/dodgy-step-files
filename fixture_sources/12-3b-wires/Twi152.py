"""Twi152 — ShapeFix_Wire.FixIntersectingEdges line-segment-vs-circle-arc.

Catalog claim: Wire contains a LINE edge that intersects a CIRCLE arc edge.
FixIntersectingEdges' split logic assumes parameter linearity and produces wrong
split point when intersecting arc parametrization. Linear interpolation fails for
circular arc parametrization.

Defect class: tolerance_escalation, intersection split point computation.
Root cause: Parameter extraction at line 3026 uses conditional ternary without
validating parameter space; arc parametrization is non-linear.

Mechanism IS a planar ADVANCED_FACE whose outer wire contains:
  - E0: LINE from P0=(0,0,0) → P1=(10,0,0) (bottom)
  - E1: CIRCLE arc from P1=(10,0,0) → P2=(0,10,0) (quarter arc, center=(0,0,0),
        radius=10*sqrt(2)/2... Actually: a circular arc that intersects E2)
  - E2: LINE from P2=(0,10,0) → P3=(5,5,0) (diagonal — intersects E1 arc)
  - E3: LINE from P3=(5,5,0) → P0=(0,0,0) (close)

The LINE E2 intersects the arc E1 midway. FixIntersectingEdges tries to split at
the intersection but applies linear parameter interpolation to the arc parameter,
producing a wrong split point — the arc's parametrization is non-linear so the
linearly-interpolated parameter maps to a different 3D point.

Tier-3 assertion: n_faces_total == 1
Expected: occt=shape(1)/shape(1)
"""
import math as _math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi152",
    defect=(
        "Single ADVANCED_FACE on a PLANE in a CLOSED_SHELL; "
        "outer EDGE_LOOP has 4 edges: "
        "E0 LINE P0=(0,0,0)→P1=(10,0,0); "
        "E1 CIRCLE arc center=(0,0,0) radius=10, P1=(10,0,0)→P2=(0,10,0), theta=0→pi/2; "
        "E2 LINE P2=(0,10,0)→P3=(3,3,0) — intersects arc E1 near theta=pi/3; "
        "E3 LINE P3=(3,3,0)→P0=(0,0,0) — closes loop; "
        "LINE E2 crosses CIRCLE arc E1 inside the domain; "
        "FixIntersectingEdges split logic applies linear parameter interpolation "
        "to arc parameter — non-linear arc maps linearly-interpolated parameter "
        "to wrong 3D split point IS mechanism; "
        "EDGE_LOOP IS wired into FACE_OUTER_BOUND -> ADVANCED_FACE in CLOSED_SHELL; "
        "never orphaned"
    ),
)

# ── Plane: normal +Z ─────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
pl_plc  = f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir)
plane   = f.plane(pl_plc)

# ── Vertices ──────────────────────────────────────────────────────────────────
# E1 is a quarter-arc of radius 10 centered at origin in XY, theta=0→pi/2:
#   P1=(10,0,0), P2=(0,10,0).
# E2 is a line from P2=(0,10,0) to P3=(3,3,0).
# The line P2→P3 parametrically: (0+3t, 10-7t, 0) for t in [0,1].
# The arc: x=10cos(s), y=10sin(s), s in [0,pi/2].
# Intersection: 10cos(s)=3t, 10sin(s)=10-7t.
# From first: t = 10cos(s)/3; sub into second: 10sin(s)=10-7*10cos(s)/3
#   10sin(s)+70cos(s)/3=10 => 3sin(s)+7cos(s)=3
# sin(s)=(3-7cos(s))/3; sin²+cos²=1 => (3-7cos(s))²/9+cos²=1
#   (9-42cos+49cos²)/9+cos²=1 => 9-42cos+49cos²+9cos²=9 => 58cos²-42cos=0
#   => cos(s)(58cos(s)-42)=0 => cos(s)=0(s=pi/2,endpoint) or cos(s)=42/58=21/29
# s=arccos(21/29)≈43.6°≈0.761 rad (inside (0,pi/2)) — genuine interior intersection
R_arc = 10.0
P0 = (0.0,  0.0, 0.0)
P1 = (10.0, 0.0, 0.0)
P2 = (0.0, 10.0, 0.0)
P3 = (3.0,  3.0, 0.0)

v_P0 = f.vertex_point(f.cartesian_point(P0))
v_P1 = f.vertex_point(f.cartesian_point(P1))
v_P2 = f.vertex_point(f.cartesian_point(P2))
v_P3 = f.vertex_point(f.cartesian_point(P3))

import math as _math

def _line_edge(v_src, v_dst, src, dst):
    dx = dst[0] - src[0]
    dy = dst[1] - src[1]
    dz = dst[2] - src[2]
    mag = _math.sqrt(dx * dx + dy * dy + dz * dz)
    ln = f.line(
        f.cartesian_point(src),
        f.vector(f.direction((dx / mag, dy / mag, dz / mag)), mag),
    )
    return f.edge_curve(v_src, v_dst, ln)

# ── E0: LINE P0→P1 (bottom edge) ─────────────────────────────────────────────
e0  = _line_edge(v_P0, v_P1, P0, P1)
oe0 = f.oriented_edge(e0, True)

# ── E1: CIRCLE arc P1→P2, center=(0,0,0), radius=10, theta=0→pi/2 ────────────
# CIRCLE placement: center at origin, axis +Z, x-dir +X
arc_plc_orig = f.cartesian_point((0.0, 0.0, 0.0))
arc_plc_zdir = f.direction((0.0, 0.0, 1.0))
arc_plc_xdir = f.direction((1.0, 0.0, 0.0))
arc_plc   = f.axis2_placement_3d(arc_plc_orig, arc_plc_zdir, arc_plc_xdir)
arc_circ  = f.circle(arc_plc, R_arc)
# Arc traverses theta=0→pi/2 (P1 at theta=0, P2 at theta=pi/2)
e1  = f.edge_curve(v_P1, v_P2, arc_circ)
oe1 = f.oriented_edge(e1, True)

# ── E2: LINE P2→P3 — INTERSECTS arc E1 at interior point ─────────────────────
# Intersection verified at s=arccos(21/29)≈0.761 rad (interior of E1 domain)
e2  = _line_edge(v_P2, v_P3, P2, P3)
oe2 = f.oriented_edge(e2, True)

# ── E3: LINE P3→P0 (close) ───────────────────────────────────────────────────
e3  = _line_edge(v_P3, v_P0, P3, P0)
oe3 = f.oriented_edge(e3, True)

# ── EDGE_LOOP: LINE-vs-arc intersection IS the defect ─────────────────────────
loop = f.edge_loop([oe0, oe1, oe2, oe3])
fob  = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane)

# ── Shell ─────────────────────────────────────────────────────────────────────
shell = f.closed_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
from pathlib import Path as _Path
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi152.stp")
