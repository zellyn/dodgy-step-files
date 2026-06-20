"""Gn020 — Spline approximation of analytic primitive (sender philosophy).

Catalog claim: A face that started as analytic is exported as a B_SPLINE_SURFACE_WITH_KNOTS
because the source kernel/exporter doesn't preserve the analytic form. Affects feature
recognition, Booleans, mass properties. Common shape: a cylinder of radius 25.0 mm
exported as a B_SPLINE_SURFACE_WITH_KNOTS of degree (2,1) with rational weights;
no CYLINDRICAL_SURFACE anywhere in the file.

OCC behavior: silently accepts (no diagnostic, empty result). Expected: occt=empty.

STEP mechanism (literal):
  - RATIONAL_B_SPLINE_SURFACE complex entity of degree (2,1) representing a
    half-cylinder (180° arc) of radius 25.0, height 50.0, extruded in V (Z direction).
    U direction: degree-2 rational B-spline arc (0 to π). V direction: degree-1 linear.
    U knots: (0.0, 1.0) mults (3,3) sum=6=2+3+1 ✓.  [3 CPs: start, mid, end of arc]
    V knots: (0.0, 1.0) mults (2,2) sum=4=1+2+1 ✓.  [2 rows: bottom, top]
    Control net (2 rows x 3 CPs):
      Bottom: (25,0,0), (25,25,0), (0,25,0)   [quarter arc of radius 25 at Z=0]
      Top:    (25,0,50), (25,25,50), (0,25,50) [same arc at Z=50]
    Wait: for a 90° arc of radius r, middle CP is at (r, r, z) with weight sqrt(2)/2.
    For a 180° arc: 2 quadrant arcs → 5 CPs. Let's use 90° (1 arc) as half-cylinder
    segment: 3 CPs, w=(1, sqrt(2)/2, 1), radius=25.
    CP[0]=(25,0,z), CP[1]=(25,25,z), CP[2]=(0,25,z): quarter-circle in XY plane.
    No CYLINDRICAL_SURFACE entity — cylinder hidden as rational B-spline.
  - C-1 DRIVER: bottom edge B_SPLINE_CURVE_WITH_KNOTS degree-2 positional break
    at t=0.5 (CP[2]=(12.5,0,0) vs CP[3]=(25.0,0,0), 12.5-unit gap) forces shape_null.

Mechanism vs driver:
  - CATALOG MECHANISM: RATIONAL_B_SPLINE_SURFACE degree (2,1) 3x2 net with
    sqrt(2)/2 middle weights encoding a quarter-cylinder arc of radius 25 extruded
    50 mm; no analytic CYLINDRICAL_SURFACE in the file; sender philosophy — exporter
    emits NURBS instead of preserving the primitive; feature recognition cannot recover.
  - C-1 DRIVER: B-spline positional break at t=0.5 forces shape_null=True.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn020",
    defect=(
        "RATIONAL_B_SPLINE_SURFACE complex entity degree (2,1) 3x2 net; "
        "U knots (0.0,1.0) mults (3,3) sum=6=2+3+1 ✓; "
        "V knots (0.0,1.0) mults (2,2) sum=4=1+2+1 ✓; "
        "encodes quarter-cylinder arc r=25 extruded h=50; weights (1,sqrt(2)/2,1) per row; "
        "no CYLINDRICAL_SURFACE in file — analytic primitive hidden as rational NURBS; "
        "sender philosophy: exporter emits B-spline instead of preserving cylinder; "
        "feature recognition / geometry simplification cannot recover primitive; "
        "defect edge B_SPLINE_CURVE_WITH_KNOTS degree-2 C-1 break at t=0.5 "
        "(CP[2]=(12.5,0,0) vs CP[3]=(25.0,0,0), 12.5-unit gap) drives shape_null=True"
    ),
)

w_mid = math.sqrt(2.0) / 2.0  # ~0.7071

# ── DEFECT SURFACE: rational B-spline quarter-cylinder ───────────────────────
# Quarter-circle arc at radius=25 in XY: (25,0) → (25,25) → (0,25)
# Extended in Z from 0 to 50.
# 3 CPs in U (arc), 2 rows in V (linear extrusion in Z).
bot0 = f.cartesian_point((25.0, 0.0,  0.0))
bot1 = f.cartesian_point((25.0, 25.0, 0.0))
bot2 = f.cartesian_point((0.0,  25.0, 0.0))
top0 = f.cartesian_point((25.0, 0.0,  50.0))
top1 = f.cartesian_point((25.0, 25.0, 50.0))
top2 = f.cartesian_point((0.0,  25.0, 50.0))

bot_row = f"(#{bot0.eid},#{bot1.eid},#{bot2.eid})"
top_row = f"(#{top0.eid},#{top1.eid},#{top2.eid})"

# Weights: 2 rows x 3 CPs; middle CP has weight sqrt(2)/2
w_row = f"(1.0,{w_mid},1.0)"
weights_str = f"({w_row},{w_row})"

# Complex entity: B_SPLINE_SURFACE + B_SPLINE_SURFACE_WITH_KNOTS + RATIONAL_B_SPLINE_SURFACE
surf = f._emit_raw(
    f"(B_SPLINE_SURFACE('cylinder_as_nurbs_r25',2,1,"
    f"({bot_row},{top_row}),"
    f".UNSPECIFIED.,.F.,.F.,.F.)"
    f"B_SPLINE_SURFACE_WITH_KNOTS((3,3),(2,2),"
    f"(0.0,1.0),(0.0,1.0),.UNSPECIFIED.)"
    f"RATIONAL_B_SPLINE_SURFACE({weights_str})"
    f"REPRESENTATION_ITEM('cylinder_as_nurbs_r25')"
    f"SURFACE())"
)

# ── Parametric context ────────────────────────────────────────────────────────
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Face corners in 3D space (arc corner points + extrusion)
p_a = f.cartesian_point((25.0, 0.0,  0.0))   # UV (0,0)
p_b = f.cartesian_point((0.0,  25.0, 0.0))   # UV (1,0) — arc end at Z=0
p_c = f.cartesian_point((0.0,  25.0, 50.0))  # UV (1,1)
p_d = f.cartesian_point((25.0, 0.0,  50.0))  # UV (0,1)
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)


def mk_edge_with_pc(vs, ve, p3, d3t, len3, p2t, d2t):
    """Build EDGE_CURVE via SURFACE_CURVE with a linear pcurve."""
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t)
    v3  = f.vector(d3e, len3)
    l3  = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t)
    v2  = f.vector(d2e, len3)
    l2  = f.line(p2e, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")


# Side edges (linear in Z, V direction)
e_right = mk_edge_with_pc(v_b, v_c, (0.0, 25.0, 0.0),  (0., 0., 1.), 50.0, (1.0, 0.0), (0., 1.))
e_top   = mk_edge_with_pc(v_c, v_d, (0.0, 25.0, 50.0), (0., -1., 0.), 25.0, (1.0, 1.0), (-1., 0.))
e_left  = mk_edge_with_pc(v_d, v_a, (25.0, 0.0, 50.0), (0., 0., -1.), 50.0, (0.0, 1.0), (0., -1.))

# ── DEFECT EDGE — bottom arc (v_a -> v_b) — C-1 DRIVER ───────────────────────
# 3D: approximate arc bottom from (25,0,0) to (0,25,0) with C-1 break at midpoint.
# Use 6-CP degree-2 B-spline with positional gap.
dc0 = f.cartesian_point((25.0,  0.0, 0.0))
dc1 = f.cartesian_point((25.0, 12.5, 0.0))
dc2 = f.cartesian_point((12.5, 25.0, 0.0))   # end of first piece
dc3 = f.cartesian_point((25.0, 25.0, 0.0))   # 12.5-unit gap = C-1 break
dc4 = f.cartesian_point((12.5, 25.0, 0.0))
dc5 = f.cartesian_point((0.0,  25.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('cylinder_nurbs_c1_break',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# Pcurve for bottom arc: U from 0→1 (arc direction), V=0
pp0 = f.cartesian_point((0.0,  0.0))
pp1 = f.cartesian_point((0.25, 0.0))
pp2 = f.cartesian_point((0.5,  0.0))
pp3 = f.cartesian_point((0.5,  0.0))
pp4 = f.cartesian_point((0.75, 0.0))
pp5 = f.cartesian_point((1.0,  0.0))

bspline_pc = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('cylinder_nurbs_c1_break_pc',2,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid},#{pp4.eid},#{pp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('cylinder_nurbs_pc_def',(#{bspline_pc.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('cylinder_nurbs_pc_ent',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('cylinder_nurbs_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('cylinder_nurbs_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
)

loop = f.edge_loop([
    f.oriented_edge(e_bot,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_left,  True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
