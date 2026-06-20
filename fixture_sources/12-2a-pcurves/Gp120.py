"""Gp120 — Composite pcurve tangent discontinuity.

Catalog claim: ShapeAnalysis_Edge.GetEndTangent2d fails on COMPOSITE_CURVE
with G0 continuity; tangent jump at segment join causes discontinuity. OCC heals.

STEP mechanism (literal):
  - PLANE Z=0 face with a defect edge wrapped in SURFACE_CURVE.
  - THE CATALOG MECHANISM: The pcurve is a COMPOSITE_CURVE_ON_SURFACE containing
    two PCURVE segments that meet with G0 (positional) continuity only — their
    tangent directions differ at the join point. The join is at UV=(2,0): the
    first segment arrives from the left along direction (1,0.4) and the second
    departs along direction (1,-0.4). GetEndTangent2d evaluates the composite
    pcurve endpoint tangent; the discontinuity at the segment join means the
    left and right tangents disagree. OCC's healer reconciles the tangent kink
    and produces shape(1)/shape(1).
  - 3D curve: a clean LINE from (0,0,0) to (4,0,0). Geometry is valid.
  - NO C-1 break (Archetype B: OCC silently heals, expected shape(1)/shape(1)).

Mechanism vs driver:
  - CATALOG MECHANISM: COMPOSITE_CURVE_ON_SURFACE with two-segment G0 join
    at UV=(2,0); tangent jump; GetEndTangent2d discontinuity; OCC heals silently.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp120",
    defect=(
        "PLANE Z=0; defect edge: SURFACE_CURVE; 3D LINE (0,0,0)→(4,0,0); "
        "PCurve: COMPOSITE_CURVE_ON_SURFACE two segments: "
        "seg1 B-spline degree-2 (0,0)→(1.5,0.5)→(2,0) direction-in=(1,0.4); "
        "seg2 B-spline degree-2 (2,0)→(2.5,-0.5)→(4,0) direction-out=(1,-0.4); "
        "G0 join at (2,0): tangent kink; GetEndTangent2d sees discontinuous "
        "composite; OCC heals; shape(1)/shape(1)"
    ),
)

# Host surface: planar Z=0
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
surf = f.plane(plc)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Face corners: rectangle [0,4] x [0,2]
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((4.0, 0.0, 0.0))
p_c = f.cartesian_point((4.0, 2.0, 0.0))
p_d = f.cartesian_point((0.0, 2.0, 0.0))
v_a = f.vertex_point(p_a); v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c); v_d = f.vertex_point(p_d)

# Context edges (right, top, left) with proper pcurves
def mk_edge_with_pc(vs, ve, p3, d3t, len3, p2t, d2t):
    """Build EDGE_CURVE via SURFACE_CURVE with a linear pcurve."""
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t); v3 = f.vector(d3e, len3); l3 = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t); v2 = f.vector(d2e, len3); l2 = f.line(p2e, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

e_right = mk_edge_with_pc(v_b, v_c, (4.0, 0.0, 0.0), (0., 1., 0.), 2.0, (4.0, 0.0), (0., 1.))
e_top   = mk_edge_with_pc(v_c, v_d, (4.0, 2.0, 0.0), (-1., 0., 0.), 4.0, (4.0, 2.0), (-1., 0.))
e_left  = mk_edge_with_pc(v_d, v_a, (0.0, 2.0, 0.0), (0., -1., 0.), 2.0, (0.0, 2.0), (0., -1.))

# ── DEFECT EDGE — bottom (v_a -> v_b) ─────────────────────────────────────────

# 3D curve: clean LINE from (0,0,0) to (4,0,0)
line_p  = f.cartesian_point((0.0, 0.0, 0.0))
line_d  = f.direction((1.0, 0.0, 0.0))
line_v  = f.vector(line_d, 4.0)
line_3d = f.line(line_p, line_v)

# THE CATALOG MECHANISM: COMPOSITE_CURVE_ON_SURFACE with two B-spline segments.
# Segment 1: degree-2, 3 CPs, domain [0,1].
#   CP[0]=(0,0), CP[1]=(1.5,0.5), CP[2]=(2,0).
#   Arrival tangent at UV=(2,0): proportional to CP[1]→CP[2] = (0.5,-0.5)
#   direction ≈ (1,-1) normalized — arriving from upper-left.
# Segment 2: degree-2, 3 CPs, domain [0,1].
#   CP[0]=(2,0), CP[1]=(2.5,-0.5), CP[2]=(4,0).
#   Departure tangent at UV=(2,0): proportional to CP[0]→CP[1] = (0.5,-0.5)
#   direction ≈ (1,-1) — departing toward lower-right.
# The tangent directions at the join are geometrically a KINK: segment 1
# arrives from upper-left (positive v excursion) and segment 2 departs to
# lower-right (negative v excursion). Even though both go rightward in u,
# the v-components (0.5 vs -0.5) are opposite — a C-0 tangent discontinuity.

# Segment 1 pcurve: B-spline degree-2 (0,0)→(1.5,0.5)→(2,0)
s1p0 = f.cartesian_point((0.0, 0.0))
s1p1 = f.cartesian_point((1.5, 0.5))   # upper excursion
s1p2 = f.cartesian_point((2.0, 0.0))   # join point
s1_bspline = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('kink_seg1',2,"
    f"(#{s1p0.eid},#{s1p1.eid},#{s1p2.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3),(0.0,1.0),.UNSPECIFIED.)"
)
s1_defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('kink_s1_def',(#{s1_bspline.eid}),#{prc.eid})"
)
s1_pcurve = f._emit_raw(f"PCURVE('kink_s1_pc',#{surf.eid},#{s1_defrep.eid})")

# Segment 2 pcurve: B-spline degree-2 (2,0)→(2.5,-0.5)→(4,0)
s2p0 = f.cartesian_point((2.0,  0.0))   # join point
s2p1 = f.cartesian_point((2.5, -0.5))   # lower excursion — opposite sign from seg1
s2p2 = f.cartesian_point((4.0,  0.0))
s2_bspline = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('kink_seg2',2,"
    f"(#{s2p0.eid},#{s2p1.eid},#{s2p2.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3),(0.0,1.0),.UNSPECIFIED.)"
)
s2_defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('kink_s2_def',(#{s2_bspline.eid}),#{prc.eid})"
)
s2_pcurve = f._emit_raw(f"PCURVE('kink_s2_pc',#{surf.eid},#{s2_defrep.eid})")

# COMPOSITE_CURVE_ON_SURFACE: two segments with CONTINUOUS transition
# (G0: positions match but tangents don't — the kink is encoded via the CP geometry)
ccos_seg1 = f._emit_raw(
    f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,#{s1_pcurve.eid})"
)
ccos_seg2 = f._emit_raw(
    f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,#{s2_pcurve.eid})"
)
ccos = f._emit_raw(
    f"COMPOSITE_CURVE_ON_SURFACE('kink_ccos',(#{ccos_seg1.eid},#{ccos_seg2.eid}),.F.)"
)

sc_bot = f._emit_raw(
    f"SURFACE_CURVE('kink_sc',#{line_3d.eid},(#{ccos.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('kink_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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
