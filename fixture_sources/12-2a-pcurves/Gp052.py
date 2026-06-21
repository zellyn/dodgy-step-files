"""Gp052 — ShapeFix_Edge.FixSameParameter copyedge stale range.

Catalog claim: When SameParameter copies edge into new TEdge, the new edge's
vertex parameter range references OLD curve domain (5, 10) instead of NEW
reparametrized domain (0, 1). Mismatch between 3D curve domain and pcurve range.

Mechanism: The defect IS in the pcurve — a degree-2 B-spline pcurve with
knot domain (5, 10) while the 3D curve lives on domain (0, 1). After
FixSameParameter copies the edge into a new TEdge and calls GeomLib::SameRange
to reparametrize the pcurve, the stale domain (5,10) is retained on the vertex
parameters instead of being updated to (0,1). The face loads cleanly (shape(1))
but the stale range is detectable via tolerance analysis.

NO C-1 break (Archetype B: OCC silently heals, expected shape(1)/shape(1)).
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp052",
    defect=(
        "PLANE Z=0; 3D B-spline curve parametrized on [0,1] (degree-2, 3 CPs); "
        "pcurve B-spline also degree-2 but with knot domain [5,10] (stale range); "
        "after FixSameParameter reparametrizes via GeomLib::SameRange, new TEdge "
        "retains stale domain (5,10) on vertex parameters instead of updated (0,1); "
        "domain mismatch IS in pcurve wired through SURFACE_CURVE"
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

# Face corners: rectangle [0,3] x [0,2]
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((3.0, 0.0, 0.0))
p_c = f.cartesian_point((3.0, 2.0, 0.0))
p_d = f.cartesian_point((0.0, 2.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)


def mk_edge_with_pc(vs, ve, p3, d3t, len3, p2t, d2t):
    """Build a normal EDGE_CURVE with SURFACE_CURVE + linear PCURVE."""
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


e_right = mk_edge_with_pc(v_b, v_c, (3.0, 0.0, 0.0), (0., 1., 0.), 2.0, (3.0, 0.0), (0., 1.))
e_top   = mk_edge_with_pc(v_c, v_d, (3.0, 2.0, 0.0), (-1., 0., 0.), 3.0, (3.0, 2.0), (-1., 0.))
e_left  = mk_edge_with_pc(v_d, v_a, (0.0, 2.0, 0.0), (0., -1., 0.), 2.0, (0.0, 2.0), (0., -1.))

# ── DEFECT EDGE — bottom (v_a -> v_b) ──────────────────────────────────────
# CATALOG MECHANISM: 3D curve domain [0,1], pcurve domain [5,10].
# The SameParameter check compares edge parameter range to curve domain;
# the stale (5,10) range from before reparametrization is the bug.
#
# 3D curve: degree-2 B-spline, domain [0,1]
# 3 CPs at (0,0,0), (1.5,0,0), (3,0,0) — parametrized on [0,1]
cp3d_0 = f.cartesian_point((0.0, 0.0, 0.0))
cp3d_1 = f.cartesian_point((1.5, 0.0, 0.0))
cp3d_2 = f.cartesian_point((3.0, 0.0, 0.0))
curve_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gp052_3d',2,"
    f"(#{cp3d_0.eid},#{cp3d_1.eid},#{cp3d_2.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3),(0.0,1.0),.UNSPECIFIED.)"
)

# DEFECT: degree-2 pcurve B-spline with STALE domain [5,10]
# CPs at (0,0), (1.5,0), (3,0) — same path, but parametrized on [5,10]
cp2d_0 = f.cartesian_point((0.0, 0.0))
cp2d_1 = f.cartesian_point((1.5, 0.0))
cp2d_2 = f.cartesian_point((3.0, 0.0))
pcurve_basis = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gp052_stale_pcurve',2,"
    f"(#{cp2d_0.eid},#{cp2d_1.eid},#{cp2d_2.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3),(5.0,10.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gp052_def',(#{pcurve_basis.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gp052_uv',#{surf.eid},#{defrep.eid})")

surface_curve = f._emit_raw(
    f"SURFACE_CURVE('gp052_sc',#{curve_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('gp052_bot_edge',#{v_a.eid},#{v_b.eid},#{surface_curve.eid},.T.)"
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
