"""Gn040 — ShapeAnalysis_Curve.FillBndBox S-curve extremum undersample.

Catalog claim: 2-point sampling on a high-curvature S-curve misses the
inflection peak; the bounding box omits the Z-coordinate extremum, breaking
downstream extent calculations. Load succeeds; geometry is accepted but
extents are wrong.

OCC behavior: shape(1) — loads successfully; extents wrong but not rejected.
Expected: occt=shape(1) (tier-3: load == ok).

STEP mechanism (literal):
  - B_SPLINE_CURVE_WITH_KNOTS degree 3, 7 control points forming an S-curve
    in 3D with a high-curvature peak at t≈0.5. The control points are arranged
    so that the midpoint rises to Z=4.0 while endpoints are at Z=0.
  - ShapeAnalysis_Curve.FillBndBox uses only 2 sample points (t=0 and t=1),
    missing the Z=4.0 peak; the reported bounding box omits the Z extremum.
  - No C-1 break: fixture is expected to load successfully (tier-3: load==ok).

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_CURVE_WITH_KNOTS S-curve with Z-extremum at
    t≈0.5 (Z=4.0 peak); ShapeAnalysis 2-point sampling misses the peak;
    bounding box Z-range is reported as [0,0] instead of [0,4]; downstream
    extent calculations break on the truncated box.
  - No C-1 driver (expected outcome: load == ok).
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn040",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS degree 3, 7-CP S-curve: endpoints at Z=0.0, "
        "midpoint control points drive peak to Z=4.0 at t≈0.5; "
        "ShapeAnalysis_Curve.FillBndBox 2-point sampling (t=0,t=1) misses "
        "Z-extremum peak; bounding box Z-range reported [0,0] not [0,4]; "
        "downstream extent calculations break; load succeeds (tier-3: load==ok)"
    ),
)

# ── HOST SURFACE: flat PLANE at Z=0 ──────────────────────────────────────────
plane_origin = f.cartesian_point((0.0, 0.0, 0.0))
plane_normal = f.direction((0.0, 0.0, 1.0))
plane_ref    = f.direction((1.0, 0.0, 0.0))
plane_ax2 = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('plane_ax',#{plane_origin.eid},#{plane_normal.eid},#{plane_ref.eid})"
)
surf = f._emit_raw(f"PLANE('flat_plane',#{plane_ax2.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── CATALOG MECHANISM: S-curve with Z-extremum missed by 2-point sampling ────
# Degree 3, 7 control points.
# Knots: (0,1,2,3,4) mults (4,1,1,1,4) => sum=11 = degree+7+1=11 ✓
# The S-curve rises to Z=4.0 near t≈0.5 (midpoint CPs at Z=4.0).
# With only 2-point sampling at t=0 and t=1 (both Z=0), the peak is invisible.
sc0 = f.cartesian_point((0.0, 0.0, 0.0))   # start: Z=0
sc1 = f.cartesian_point((1.0, 0.0, 1.5))   # rising
sc2 = f.cartesian_point((2.0, 0.0, 4.0))   # peak: Z=4.0
sc3 = f.cartesian_point((3.0, 0.0, 4.0))   # peak plateau
sc4 = f.cartesian_point((4.0, 0.0, 4.0))   # descending from peak
sc5 = f.cartesian_point((5.0, 0.0, 1.5))   # falling
sc6 = f.cartesian_point((6.0, 0.0, 0.0))   # end: Z=0

# THE MECHANISM: S-curve with Z-extremum invisible at t=0 and t=1 endpoints.
s_curve = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('s_curve_z_peak',3,"
    f"(#{sc0.eid},#{sc1.eid},#{sc2.eid},#{sc3.eid},#{sc4.eid},#{sc5.eid},#{sc6.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,1,1,1,4),(0.0,1.0,2.0,3.0,4.0),.UNSPECIFIED.)"
)

# The S-curve is used as a 3D edge geometry in a normal (valid) SURFACE_CURVE.
# The fixture loads fine — the bug is in bounding box computation, not loading.
pp0 = f.cartesian_point((0.0,  0.0))
pp1 = f.cartesian_point((0.25, 0.0))
pp2 = f.cartesian_point((0.5,  0.0))
pp3 = f.cartesian_point((0.5,  0.0))
pp4 = f.cartesian_point((0.75, 0.0))
pp5 = f.cartesian_point((1.0,  0.0))

pc_bspline = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn040_pc',2,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid},#{pp4.eid},#{pp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn040_pcdef',(#{pc_bspline.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn040_pc_ent',#{surf.eid},#{defrep.eid})")
sc_edge = f._emit_raw(
    f"SURFACE_CURVE('gn040_sc',#{s_curve.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((6.0, 0.0, 0.0))
p_c = f.cartesian_point((6.0, 5.0, 0.0))
p_d = f.cartesian_point((0.0, 5.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

e_s_curve = f._emit_raw(
    f"EDGE_CURVE('gn040_edge',#{v_a.eid},#{v_b.eid},#{sc_edge.eid},.T.)"
)

def mk_line_edge(vs, ve, p3, d3t, p2t, d2t, length):
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t)
    v3  = f.vector(d3e, length)
    l3  = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t)
    v2  = f.vector(d2e, length)
    l2  = f.line(p2e, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc_ = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc_.eid},.T.)")

e_right = mk_line_edge(v_b, v_c, (6.0, 0.0, 0.0), (0.,1.,0.), (1.0, 0.0), (0.,1.), 5.0)
e_top   = mk_line_edge(v_c, v_d, (6.0, 5.0, 0.0), (-1.,0.,0.), (1.0, 1.0), (-1.,0.), 6.0)
e_left  = mk_line_edge(v_d, v_a, (0.0, 5.0, 0.0), (0.,-1.,0.), (0.0, 1.0), (0.,-1.), 5.0)

loop = f.edge_loop([
    f.oriented_edge(e_s_curve, True),
    f.oriented_edge(e_right,   True),
    f.oriented_edge(e_top,     True),
    f.oriented_edge(e_left,    True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
