"""Tfa182 — ShapeAnalysis_CheckSmallFace.CheckSmallArea polygon-vs-curve

Catalog claim: Wire boundary with curved edges (circular arcs) and rectangular
hole wire. CheckSmallArea approximates wire as polygon from vertices only,
missing actual enclosed area from arc bulge. Exposes gap between linear vertex
approximation and true curved-edge geometry. Small area check fails on actual
bounds.

Mechanism: OPEN_SHELL with ONE ADVANCED_FACE on a PLANE. Outer boundary is a
4-edge loop made of 4 quarter-circle arcs forming a full circle of radius 3
(actual area = π·3² ≈ 28.3). The polygon approximation using only the 4 quarter
points (±3,0), (0,±3) gives area ≈ 18.0 — significantly smaller than true area.
A rectangular inner hole wire (1×1 at centre) is present. When CheckSmallArea
computes area via vertex polygon it substantially underestimates, exposing the
polygon-vs-curve gap. Defect IS on live face traversal path.

Byte assertions:
  - contains(b'ADVANCED_FACE')
  - contains(b'FACE_OUTER_BOUND')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa182",
    defect=(
        "OPEN_SHELL: single ADVANCED_FACE on PLANE; "
        "outer boundary = 4 quarter-circle arcs (radius 3, area π·9≈28.3); "
        "inner hole = 1×1 rectangle at (-0.5,-0.5)-(0.5,0.5); "
        "CheckSmallArea uses vertex-polygon approximation (area≈18) and misses "
        "arc bulge contribution, producing large underestimate; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

R = 3.0  # circle radius

# ── PLANE surface at origin, normal +Z ────────────────────────────────────
plane = f.plane(f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
))

# ── Circle at origin radius R ──────────────────────────────────────────────
circle_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
circle = f.circle(circle_plc, R)

# 4 cardinal points on the circle
p_E = f.cartesian_point(( R,  0.0, 0.0))   # 0°
p_N = f.cartesian_point(( 0.0,  R, 0.0))   # 90°
p_W = f.cartesian_point((-R,  0.0, 0.0))   # 180°
p_S = f.cartesian_point(( 0.0, -R, 0.0))   # 270°

v_E = f.vertex_point(p_E); v_N = f.vertex_point(p_N)
v_W = f.vertex_point(p_W); v_S = f.vertex_point(p_S)

# 4 arc edges using the shared circle (quarter arcs CCW)
arc_EN = f.edge_curve(v_E, v_N, circle)   # Q1: E→N
arc_NW = f.edge_curve(v_N, v_W, circle)   # Q2: N→W
arc_WS = f.edge_curve(v_W, v_S, circle)   # Q3: W→S
arc_SE = f.edge_curve(v_S, v_E, circle)   # Q4: S→E

outer_loop = f.edge_loop([
    f.oriented_edge(arc_EN, True),
    f.oriented_edge(arc_NW, True),
    f.oriented_edge(arc_WS, True),
    f.oriented_edge(arc_SE, True),
])
outer_fob = f.face_outer_bound(outer_loop)

# ── Inner rectangular hole: 1×1 centred at origin ─────────────────────────
def _line_edge(p1, v1, p2, v2):
    dx = p2.args[1][0] - p1.args[1][0]
    dy = p2.args[1][1] - p1.args[1][1]
    length = _math.hypot(dx, dy)
    d = f.direction((dx / length, dy / length, 0.0))
    return f.edge_curve(v1, v2, f.line(p1, f.vector(d, length)))

hs = 0.5  # half-side
hp0 = f.cartesian_point((-hs, -hs, 0.0))
hp1 = f.cartesian_point(( hs, -hs, 0.0))
hp2 = f.cartesian_point(( hs,  hs, 0.0))
hp3 = f.cartesian_point((-hs,  hs, 0.0))

hv0 = f.vertex_point(hp0); hv1 = f.vertex_point(hp1)
hv2 = f.vertex_point(hp2); hv3 = f.vertex_point(hp3)

he_b = _line_edge(hp0, hv0, hp1, hv1)
he_r = _line_edge(hp1, hv1, hp2, hv2)
he_t = _line_edge(hp2, hv2, hp3, hv3)
he_l = _line_edge(hp3, hv3, hp0, hv0)

inner_loop = f.edge_loop([
    f.oriented_edge(he_b, True), f.oriented_edge(he_r, True),
    f.oriented_edge(he_t, True), f.oriented_edge(he_l, True),
])
inner_fb = f.face_bound(inner_loop, False)

face = f.advanced_face([outer_fob, inner_fb], plane)

shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa182.stp")
