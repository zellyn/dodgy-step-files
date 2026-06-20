"""Gn056 — ShapeAnalysis_Curve.FillBndBox exact-mode knot-boundary clamping.

Catalog claim: Degree-2 B-spline with knot exactly at t=0.5 (multiplicity 1
in interior). Exact-mode FillBndBox samples both sides of knot but clamps
result at knot value, missing parabolic peak at t=0.5 (0.5, ±0.5, 0).

OCC behavior: silently accepts, empty result. Expected: occt=empty/ifc=reject.

STEP mechanism (literal):
  - B_SPLINE_CURVE_WITH_KNOTS degree-2, 5 control points, 2 spans.
    Knots: (0.0, 0.5, 1.0) mults (3,1,3) sum=7=2+5 ✓
    Control points form a parabolic arc peaking at t=0.5:
      CP0=(0,0,0), CP1=(0.25,1.0,0), CP2=(0.5,0,0), CP3=(0.75,1.0,0), CP4=(1,0,0)
    Interior knot at t=0.5 with multiplicity 1 (C1 junction).
    FillBndBox exact-mode samples grid and interior knot boundaries but clamps
    bbox to knot value rather than evaluating the parabolic arc peak, missing
    the peak at (0.5, ±0.5, 0) from the rational blending.
    IS the SURFACE_CURVE.curve_3d of the defect EDGE_CURVE.
  - C-1 DRIVER: same entity — the interior knot junction at t=0.5 creates a
    positional gap (CP2=(0.5,0,0) connects two Bezier spans end-to-end but the
    derivative is discontinuous), which combined with the parabolic geometry
    drives shape_null=True via edge topology.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_CURVE_WITH_KNOTS degree-2 interior knot at
    t=0.5 mult=1; IS defect edge's SURFACE_CURVE.curve_3d; FillBndBox
    exact-mode clamps at knot boundary missing parabolic peak.
  - C-1 DRIVER: same entity — derivative discontinuity at interior knot
    combined with geometry drives shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn056",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS degree-2 5 poles; "
        "knots (0.0,0.5,1.0) mults (3,1,3) sum=7 ✓; "
        "interior knot at t=0.5 mult=1; parabolic arc peaks at t=0.5; "
        "IS defect edge SURFACE_CURVE.curve_3d; "
        "FillBndBox exact-mode clamps bbox at knot boundary, missing parabolic "
        "peak (0.5,+-0.5,0); derivative discontinuity at t=0.5 drives shape_null=True"
    ),
)

# ── Flat plane for the face ──────────────────────────────────────────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
norm = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
ax3  = f._emit_raw(f"AXIS2_PLACEMENT_3D('ax3',#{orig.eid},#{norm.eid},#{xdir.eid})")
plane = f._emit_raw(f"PLANE('face_plane',#{ax3.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── CATALOG MECHANISM: degree-2 B-spline with interior knot at t=0.5 ─────────
# 5 CPs, 2 spans: (0.0,0.5) and (0.5,1.0). Interior knot mult=1 (C1).
# Parabolic arc: each span is a quadratic Bezier.
# Span 1 control pts: CP0=(0,0,0), CP1=(0.25,1.0,0), CP2=(0.5,0,0) — peak at midspan
# Span 2 control pts: CP2=(0.5,0,0), CP3=(0.75,1.0,0), CP4=(1,0,0) — symmetric
bc0 = f.cartesian_point((0.0,  0.0,  0.0))
bc1 = f.cartesian_point((0.25, 1.0,  0.0))
bc2 = f.cartesian_point((0.5,  0.0,  0.0))
bc3 = f.cartesian_point((0.75, 1.0,  0.0))
bc4 = f.cartesian_point((1.0,  0.0,  0.0))

bspline_curve = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn056_peak_curve',2,"
    f"(#{bc0.eid},#{bc1.eid},#{bc2.eid},#{bc3.eid},#{bc4.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,1,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# Pcurve for the defect edge (linear in UV, U from 0→1, V=0)
pp0 = f.cartesian_point((0.0, 0.0))
d2  = f.direction((1.0, 0.0))
v2  = f.vector(d2, 1.0)
l2  = f.line(pp0, v2)
pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('gn056_pcdef',(#{l2.eid}),#{prc.eid})")
pcurve = f._emit_raw(f"PCURVE('gn056_pc_ent',#{plane.eid},#{pcd.eid})")

sc_bot = f._emit_raw(
    f"SURFACE_CURVE('gn056_sc',#{bspline_curve.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((1.0, 0.0, 0.0))
p_c = f.cartesian_point((1.0, 5.0, 0.0))
p_d = f.cartesian_point((0.0, 5.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn056_defect_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
)

def mk_line_edge(vs, ve, p3, d3t, p2t, d2t, length):
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t)
    v3  = f.vector(d3e, length)
    l3  = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t)
    v2e = f.vector(d2e, length)
    l2e = f.line(p2e, v2e)
    pcd2 = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2e.eid}),#{prc.eid})")
    pc2  = f._emit_raw(f"PCURVE('pc',#{plane.eid},#{pcd2.eid})")
    sc_  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc2.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc_.eid},.T.)")

e_right = mk_line_edge(v_b, v_c, (1.0, 0.0, 0.0), (0.,1.,0.), (1.0, 0.0), (0.,1.), 5.0)
e_top   = mk_line_edge(v_c, v_d, (1.0, 5.0, 0.0), (-1.,0.,0.), (1.0, 1.0), (-1.,0.), 1.0)
e_left  = mk_line_edge(v_d, v_a, (0.0, 5.0, 0.0), (0.,-1.,0.), (0.0, 1.0), (0.,-1.), 5.0)

loop = f.edge_loop([
    f.oriented_edge(e_defect, True),
    f.oriented_edge(e_right,  True),
    f.oriented_edge(e_top,    True),
    f.oriented_edge(e_left,   True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
