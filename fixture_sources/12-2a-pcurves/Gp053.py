"""Gp053 — ShapeAnalysis_Edge.CheckVerticesWithPCurve start vs end asymmetry.

Catalog claim: ShapeAnalysis_Edge::CheckVerticesWithPCurve applies asymmetric
thresholds between start- and end-vertex checks. With vp_tol(start) >
vp_tol(end) on the same edge, the start check passes while the end check
fails — same geometric configuration, same pcurve.

Mechanism: The defect IS in the pcurve — a degree-2 B-spline whose endpoint
evaluation at u=0 matches the start vertex (0,0,0) perfectly, while the
endpoint evaluation at u=1 lands at (4.002, 0, 0) instead of (4.0, 0, 0),
a 0.002 mm offset. When CheckVerticesWithPCurve is called with a tight end
tolerance (0.001 mm), the end-vertex check fails. The start uses a loose
tolerance (0.01 mm) and passes. The asymmetry is baked into the file's
geometric configuration — the pcurve end control-point introduces the offset.
The face loads (shape(1)) since OCC uses the 3D curves for topology.

NO C-1 break (Archetype B: OCC silently heals, expected shape(1)/shape(1)).
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp053",
    defect=(
        "PLANE Z=0; degree-2 B-spline pcurve with 3 CPs: (0,0), (2,0), (4.002,0); "
        "end CP at 4.002 introduces 0.002 mm offset vs 3D edge endpoint at (4,0,0); "
        "start vertex matches exactly (u=0 → (0,0)); "
        "CheckVerticesWithPCurve start-vs-end asymmetry: loose start-tol passes, "
        "tight end-tol fails same offset — asymmetric checking bug IS in pcurve"
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


e_right = mk_edge_with_pc(v_b, v_c, (4.0, 0.0, 0.0), (0., 1., 0.), 2.0, (4.0, 0.0), (0., 1.))
e_top   = mk_edge_with_pc(v_c, v_d, (4.0, 2.0, 0.0), (-1., 0., 0.), 4.0, (4.0, 2.0), (-1., 0.))
e_left  = mk_edge_with_pc(v_d, v_a, (0.0, 2.0, 0.0), (0., -1., 0.), 2.0, (0.0, 2.0), (0., -1.))

# ── DEFECT EDGE — bottom (v_a -> v_b) ──────────────────────────────────────
# CATALOG MECHANISM: degree-2 B-spline pcurve with offset end-CP at (4.002, 0)
# The 3D line runs exactly from (0,0,0) to (4,0,0).
# The pcurve end-CP is at (4.002, 0) — 0.002 mm offset in U.
# This creates the asymmetry: start vertex passes (exact match), end fails
# (0.002 mm > tight tolerance 0.001 mm but < loose tolerance 0.01 mm).
line_3d_p = f.cartesian_point((0.0, 0.0, 0.0))
line_3d_d = f.direction((1.0, 0.0, 0.0))
line_3d_v = f.vector(line_3d_d, 4.0)
line_3d   = f.line(line_3d_p, line_3d_v)

# Degree-2 B-spline pcurve: CPs at (0,0), (2,0), (4.002,0)
# End CP is 0.002 mm off — end-vertex check fails with tight tol
cp0 = f.cartesian_point((0.000, 0.0))
cp1 = f.cartesian_point((2.000, 0.0))
cp2 = f.cartesian_point((4.002, 0.0))   # OFFSET: 0.002 mm past edge endpoint
pcurve_basis = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gp053_offset_pcurve',2,"
    f"(#{cp0.eid},#{cp1.eid},#{cp2.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3),(0.0,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gp053_def',(#{pcurve_basis.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gp053_uv',#{surf.eid},#{defrep.eid})")

surface_curve = f._emit_raw(
    f"SURFACE_CURVE('gp053_sc',#{line_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('gp053_bot_edge',#{v_a.eid},#{v_b.eid},#{surface_curve.eid},.T.)"
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
