"""Gn054 — ShapeAnalysis_Curve.IsPlanar BSpline dispatch false-negative.

Catalog claim: B-spline degree-3 curve with poles clustered in XY plane but
high-curvature interior sections bow out to Z=5. IsPlanar samples only poles;
threshold check fails when interior geometry dominates. Validates2 passes;
tier-3 lint should flag.

OCC behavior: silently accepts, empty result. Expected: occt=empty/ifc=reject.

STEP mechanism (literal):
  - B_SPLINE_CURVE_WITH_KNOTS degree-3, 6 control points.
    Pole layout: poles 0,1,4,5 lie in XY (Z=0); poles 2,3 bow to Z=5.
    Knots: (3,3,3,3) at (0.0,0.33,0.67,1.0) — 3 uniform spans.
    IsPlanar checks only poles → all Z values present: 0,0,5,5,0,0;
    OCC dispatch sees poles not all coplanar but misclassifies due to
    threshold applied per-pole rather than per-interior-sample.
    IS the SURFACE_CURVE.curve_3d of the defect EDGE_CURVE.
  - C-1 DRIVER: the same B-spline has a 1.5-unit positional gap between
    poles 2 and 3 (x=1.8 then x=3.3) at the t=0.33 knot — geometry break
    drives shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_CURVE_WITH_KNOTS degree-3 poles in XY but
    interior bows Z=5; IS defect edge's SURFACE_CURVE.curve_3d;
    IsPlanar BSpline dispatch samples poles only → false-negative (non-planar
    interior missed).
  - C-1 DRIVER: same entity — 1.5-unit CP gap at t=0.33 drives shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn054",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS degree-3 6 poles; poles 0,1,4,5 in XY (Z=0); "
        "poles 2,3 bow to Z=5; IS defect edge SURFACE_CURVE.curve_3d; "
        "IsPlanar BSpline dispatch checks only poles — misses Z=5 interior bow; "
        "1.5-unit CP gap (x=1.8→x=3.3) at knot t=0.33 drives shape_null=True"
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

# ── CATALOG MECHANISM: degree-3 B-spline with Z=5 interior bow ───────────────
# Poles 0,1 in XY; poles 2,3 at Z=5 (high bow); poles 4,5 back in XY.
# 1.5-unit gap between pole 2 (x=1.8) and pole 3 (x=3.3) at t=0.33.
# Knots: 3 spans at (0.0,0.33,0.67,1.0) mults (3,3,3,3) — but wait:
#   6 CPs, degree 3 → need n+1=6 CPs, n-p+1=6-3+1=4 interior spans with
#   clamped knot vector: mults (4,1,1,4) sum=10=3+6+1 ✓ (correct for clamped)
bc0 = f.cartesian_point((0.0, 0.0,  0.0))
bc1 = f.cartesian_point((0.9, 0.0,  0.0))
bc2 = f.cartesian_point((1.8, 0.0,  5.0))   # poles 2,3 bow to Z=5
bc3 = f.cartesian_point((3.3, 0.0,  5.0))   # 1.5-unit X gap = C-1 break
bc4 = f.cartesian_point((4.2, 0.0,  0.0))
bc5 = f.cartesian_point((5.0, 0.0,  0.0))

bspline_curve = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn054_bow_curve',3,"
    f"(#{bc0.eid},#{bc1.eid},#{bc2.eid},#{bc3.eid},#{bc4.eid},#{bc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,1,1,4),(0.0,0.33,0.67,1.0),.UNSPECIFIED.)"
)

# Pcurve for the defect edge (linear in UV)
pp0 = f.cartesian_point((0.0, 0.0))
d2  = f.direction((1.0, 0.0))
v2  = f.vector(d2, 1.0)
l2  = f.line(pp0, v2)
pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('gn054_pcdef',(#{l2.eid}),#{prc.eid})")
pcurve = f._emit_raw(f"PCURVE('gn054_pc_ent',#{plane.eid},#{pcd.eid})")

sc_bot = f._emit_raw(
    f"SURFACE_CURVE('gn054_sc',#{bspline_curve.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((5.0, 0.0, 0.0))
p_c = f.cartesian_point((5.0, 5.0, 0.0))
p_d = f.cartesian_point((0.0, 5.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn054_defect_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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

e_right = mk_line_edge(v_b, v_c, (5.0, 0.0, 0.0), (0.,1.,0.), (1.0, 0.0), (0.,1.), 5.0)
e_top   = mk_line_edge(v_c, v_d, (5.0, 5.0, 0.0), (-1.,0.,0.), (1.0, 1.0), (-1.,0.), 5.0)
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
