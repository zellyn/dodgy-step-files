"""Gn064 — ShapeAnalysis_Curve.IsClosed periodic vs closed semantic.

Catalog claim: B-spline curve with periodic=TRUE but first pole ≠ last pole.
IsClosed() returns True because it only checks the periodic tag, not geometric
closure. The curve therefore appears closed to downstream topology even though
the control polygon is open.

OCC behavior: silently accepts, empty result. Expected: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_CURVE_WITH_KNOTS degree 3, 6 poles, periodic=TRUE.
    First pole = (0,0,0), last pole = (1,0,0) — geometrically open.
    Knots: (0.0, 0.25, 0.5, 0.75, 1.0) mults (1,1,1,1,1) periodic form.
    IsClosed() checks periodic flag only → returns True despite open polygon.
    IS the SURFACE_CURVE.curve_3d of the defect EDGE_CURVE.
  - C-1 DRIVER: periodic B-spline with non-closing poles creates a topological
    gap at the seam that drives shape_null=True via edge topology failure.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_CURVE_WITH_KNOTS degree-3 6 poles periodic=TRUE;
    first pole (0,0,0) ≠ last pole (1,0,0); IS defect edge SURFACE_CURVE.curve_3d;
    IsClosed() checks only periodic flag, misreports geometrically-open curve as closed.
  - C-1 DRIVER: same entity — seam gap on periodic non-closing curve drives shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn064",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS degree-3 6 poles periodic=TRUE; "
        "first pole (0,0,0) ≠ last pole (1,0,0) — geometrically open; "
        "knots (0.0,0.25,0.5,0.75,1.0) mults (1,1,1,1,1); "
        "IS defect edge SURFACE_CURVE.curve_3d; "
        "IsClosed() checks only periodic flag, reports closed on open polygon; "
        "seam gap drives shape_null=True via edge topology failure"
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

# ── CATALOG MECHANISM: periodic B-spline, degree 3, 6 poles ──────────────────
# periodic=TRUE but first (0,0,0) ≠ last (1,0,0) — open polygon.
# Knots for periodic: 5 interior spans, mults all=1.
cp0 = f.cartesian_point((0.0,  0.0,  0.0))   # first pole
cp1 = f.cartesian_point((0.2,  0.5,  0.0))
cp2 = f.cartesian_point((0.4,  0.0,  0.0))
cp3 = f.cartesian_point((0.6,  0.5,  0.0))
cp4 = f.cartesian_point((0.8,  0.0,  0.0))
cp5 = f.cartesian_point((1.0,  0.0,  0.0))   # last pole ≠ first → open

periodic_curve = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn064_periodic_curve',3,"
    f"(#{cp0.eid},#{cp1.eid},#{cp2.eid},#{cp3.eid},#{cp4.eid},#{cp5.eid}),"
    f".UNSPECIFIED.,.F.,.T.,"
    f"(1,1,1,1,1,1),(0.0,0.2,0.4,0.6,0.8,1.0),.UNSPECIFIED.)"
)

# Pcurve: linear in UV
pp0 = f.cartesian_point((0.0, 0.0))
d2  = f.direction((1.0, 0.0))
v2  = f.vector(d2, 1.0)
l2  = f.line(pp0, v2)
pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('gn064_pcdef',(#{l2.eid}),#{prc.eid})")
pcurve = f._emit_raw(f"PCURVE('gn064_pc_ent',#{plane.eid},#{pcd.eid})")

sc_bot = f._emit_raw(
    f"SURFACE_CURVE('gn064_sc',#{periodic_curve.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((1.0, 0.0, 0.0))
p_c = f.cartesian_point((1.0, 1.0, 0.0))
p_d = f.cartesian_point((0.0, 1.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn064_defect_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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

e_right = mk_line_edge(v_b, v_c, (1.0, 0.0, 0.0), (0.,1.,0.), (1.0, 0.0), (0.,1.), 1.0)
e_top   = mk_line_edge(v_c, v_d, (1.0, 1.0, 0.0), (-1.,0.,0.), (1.0, 1.0), (-1.,0.), 1.0)
e_left  = mk_line_edge(v_d, v_a, (0.0, 1.0, 0.0), (0.,-1.,0.), (0.0, 1.0), (0.,-1.), 1.0)

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
