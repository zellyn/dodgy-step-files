"""Gp187 — Ill-conditioned (highly non-uniform) pcurve knot spacing
forcing arc-length reparametrization (sew-pcurve-parameter-desync-repair
subvariant, missing from the class: prior witness Gp040 is a plain
positional displacement, not a knot-ratio ill-conditioning case).

Work packet D2, item `sew-pcurve-parameter-desync-repair` (PARTIAL,
missing 3 of 4, pick 2 -- this fixture covers subvariant (b)), problem_id
`sew-pcurve-parameter-desync-repair`: "If the smoothed curve still has
severely non-uniform (ill-conditioned) knot spacing, it is further
reparametrized by arc length (curvilinear), with an automatic revert if
that reparametrization is later found to have made the achieved accuracy
worse." (BRepLib::SameParameter, BRepLib.cxx:~1481-1519 per V3 mining --
knot-ratio anomaly + arc-length reparametrization; entry guards verified
at BRepLib.cxx:1225-1233.)

Deviation from the packet spec, evidence-based: the companion subvariant
in this same class ("relaxed second smoothing attempt ... deliberate
regression so the revert-on-regression path fires") requires observing
which INTERNAL retry branch BRepLib::SameParameter takes; that state is
not introspectable through OCCT's public API (no counter, no diagnostic
enum distinguishing "first pass" from "second, more relaxed pass" is
exposed), so a STEP-input-only fixture cannot be verified to hit that
specific branch rather than the ordinary single-pass smoothing Gp040
already demonstrates. That subvariant is deferred to BACKLOG.md rather
than shipped as an unverifiable duplicate of Gp040. This fixture instead
targets the OTHER missing subvariant, which IS a purely input-side
property: a pcurve whose knot vector has an extreme spacing ratio.

Mechanism: A face on a PLANE. The edge's 3D curve is a plain LINE from
(0,0,0) to (1,0,0), uniformly parametrized over [0,1]. Its PCURVE is a
degree-3 B_SPLINE_CURVE_WITH_KNOTS with 7 control points tracing a
gentle non-collinear S-wiggle from (0,0) to (1,0) in UV -- but the
interior knot vector is (0.0001, 0.0002, 0.0003): three knots crammed
into the first three ten-thousandths of the parameter range, leaving a
single ~0.9997-wide span for the rest of the curve. The ratio of
smallest to largest knot interval is roughly 1:10000 -- the "severely
non-uniform (ill-conditioned) knot spacing" signature that defeats a
polynomial-domain SameParameter approximation and forces curvilinear
(arc-length) reparametrization.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp187",
    defect=(
        "PLANE-hosted edge: 3D LINE (0,0,0)->(1,0,0), uniform domain [0,1]. "
        "PCURVE: degree-3 B-spline, 7 non-collinear control points tracing a "
        "gentle S-wiggle (0,0)->(1,0) in UV, interior knots (0.0001,0.0002,0.0003) "
        "-- smallest:largest knot-interval ratio ~1:10000, ill-conditioned spacing "
        "that defeats polynomial-domain SameParameter approximation and forces "
        "arc-length (curvilinear) reparametrization"
    ),
)

# PLANE host surface, standard placement.
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# 3D LINE: (0,0,0) -> (1,0,0), uniform parameter domain [0,1].
p_start = f.cartesian_point((0.0, 0.0, 0.0))
p_end = f.cartesian_point((1.0, 0.0, 0.0))
v_start = f.vertex_point(p_start)
v_end = f.vertex_point(p_end)
line_3d = f.line(p_start, f.vector(f.direction((1.0, 0.0, 0.0)), 1.0))

# THE DEFECT: degree-3 pcurve B-spline, 7 control points, non-collinear
# S-wiggle in UV, interior knots crammed into [0, 0.0003] leaving a single
# huge [0.0003, 1.0] span -- ill-conditioned knot-spacing ratio ~1:10000.
uv_pts = [
    f.cartesian_point((0.00, 0.000)),
    f.cartesian_point((0.15, 0.080)),
    f.cartesian_point((0.30, -0.060)),
    f.cartesian_point((0.50, 0.050)),
    f.cartesian_point((0.70, -0.050)),
    f.cartesian_point((0.85, 0.060)),
    f.cartesian_point((1.00, 0.000)),
]
pcurve_basis = f.b_spline_curve_with_knots(
    degree=3,
    control_points=uv_pts,
    knot_multiplicities=[4, 1, 1, 1, 4],
    knots=[0.0, 0.0001, 0.0002, 0.0003, 1.0],
    name="gp187_ill_conditioned_pcurve",
)
pc_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gp187_def',(#{pcurve_basis.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gp187_uv',#{plane.eid},#{pc_def.eid})")

surface_curve = f._emit_raw(
    f"SURFACE_CURVE('gp187_sc',#{line_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
edge = f._emit_raw(
    f"EDGE_CURVE('gp187_edge',#{v_start.eid},#{v_end.eid},#{surface_curve.eid},.T.)"
)

loop = f.edge_loop([f.oriented_edge(edge, True)])
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
