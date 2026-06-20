"""Gp039 — Pcurve projection unstable on closed B-spline curve.

Catalog defect (OCCT GitHub#967, #894, #890, #600): A closed B-spline curve
(degree 3, 8 control points with first == last) is projected onto a surface to
compute a pcurve. The projection algorithm fails at the closing seam —
producing a pcurve with a wild spike near seam parameter. The pcurve's
parameter range no longer matches the input curve's range.

Fixture: A PLANE face whose top edge is a closed B_SPLINE_CURVE_WITH_KNOTS
(first ctrl pt == last ctrl pt, simulating a closed loop). Its PCURVE carries
a B_SPLINE_CURVE_WITH_KNOTS whose last control point is wildly displaced
(a spike at the seam parameter) — modelling the unstable projection artifact.
The other three edges are correct straight lines with clean pcurves.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp039",
    defect=(
        "Top edge on PLANE: closed B-spline 3D curve projected to pcurve; "
        "resulting PCURVE B-spline has wild spike at seam (last ctrl pt displaced "
        "by (0,100) in UV) — projection unstable at closure seam, parameter range "
        "no longer matches input curve range"
    ),
)

# Planar surface: XY plane.
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
surf = f.plane(plc)

# UV parametric context
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Rectangle (0,0,0)-(1,0,0)-(1,1,0)-(0,1,0).
p00 = f.cartesian_point((0.0, 0.0, 0.0))
p10 = f.cartesian_point((1.0, 0.0, 0.0))
p11 = f.cartesian_point((1.0, 1.0, 0.0))
p01 = f.cartesian_point((0.0, 1.0, 0.0))
v00 = f.vertex_point(p00)
v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11)
v01 = f.vertex_point(p01)

# Helper: correct straight edge.
def make_correct_edge(p_s, p_e, vs, ve, uv_s, uv_e, name):
    dx = p_e[0] - p_s[0]
    dy = p_e[1] - p_s[1]
    length = (dx*dx + dy*dy) ** 0.5
    pt3  = f.cartesian_point(p_s)
    d3   = f.direction((dx/length, dy/length, 0.0))
    v3   = f.vector(d3, length)
    l3d  = f.line(pt3, v3)
    du = uv_e[0] - uv_s[0]
    dv = uv_e[1] - uv_s[1]
    uvlen = (du*du + dv*dv) ** 0.5
    pc_s = f.cartesian_point(uv_s)
    pc_d = f.direction((du/uvlen, dv/uvlen))
    pc_v = f.vector(pc_d, uvlen)
    pc_l = f.line(pc_s, pc_v)
    pc_def = f._emit_raw(
        f"DEFINITIONAL_REPRESENTATION('pc_{name}',(#{pc_l.eid}),#{prc.eid})"
    )
    pcv = f._emit_raw(f"PCURVE('pcv_{name}',#{surf.eid},#{pc_def.eid})")
    sc  = f._emit_raw(
        f"SURFACE_CURVE('{name}',#{l3d.eid},(#{pcv.eid}),.PCURVE_S1.)"
    )
    return f._emit_raw(
        f"EDGE_CURVE('{name}',#{vs.eid},#{ve.eid},#{sc.eid},.T.)"
    )

e_bot   = make_correct_edge(
    (0.0,0.0,0.0),(1.0,0.0,0.0), v00,v10, (0.0,0.0),(1.0,0.0), 'bot')
e_right = make_correct_edge(
    (1.0,0.0,0.0),(1.0,1.0,0.0), v10,v11, (1.0,0.0),(1.0,1.0), 'right')
e_left  = make_correct_edge(
    (0.0,1.0,0.0),(0.0,0.0,0.0), v01,v00, (0.0,1.0),(0.0,0.0), 'left')

# ---- THE DEFECT: top edge — closed B-spline 3D curve with spiked pcurve ----
# 3D B-spline: degree 3, 8 control points (first == last → closed loop).
# The closed curve goes from (0,1,0) → ... → (1,1,0) ... → (0,1,0) back.
# We use a cubic B-spline with clamped knots over [0,1].
# Control points: close the loop by making cp[0] == cp[7].
# The 3D curve physically visits (0,1,0) and (1,1,0).
bsp_3d = f.b_spline_curve_with_knots(
    degree=3,
    control_points=[
        f.cartesian_point((0.0, 1.0, 0.0)),  # cp0 = start/end (closure)
        f.cartesian_point((0.2, 1.0, 0.0)),
        f.cartesian_point((0.4, 1.05, 0.0)),
        f.cartesian_point((0.5, 1.0, 0.0)),
        f.cartesian_point((0.6, 0.95, 0.0)),
        f.cartesian_point((0.8, 1.0, 0.0)),
        f.cartesian_point((1.0, 1.0, 0.0)),
        f.cartesian_point((0.0, 1.0, 0.0)),  # cp7 == cp0: closed curve
    ],
    knot_multiplicities=[4, 1, 1, 1, 1, 4],
    knots=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
    curve_form="UNSPECIFIED",
    closed=True,
    self_intersect=False,
)

# PCURVE B-spline: same knot structure but with a wild spike at the seam.
# Control points in UV: cp0=(0,1) ... cp6=(1,1) ... cp7 has a spike: (0,101).
# The seam parameter (t=1.0) should map to UV (0,1), but the instability
# sends the last control point to (0, 101) — 100 units off in V.
# This models the "wild excursion near the seam" defect.
# Build the 2D B-spline inline with _emit_raw since builder takes 3-tuples.
uv_cps = [
    f.cartesian_point((0.0, 1.0)),    # cp0: correct
    f.cartesian_point((0.2, 1.0)),
    f.cartesian_point((0.4, 1.05)),
    f.cartesian_point((0.5, 1.0)),
    f.cartesian_point((0.6, 0.95)),
    f.cartesian_point((0.8, 1.0)),
    f.cartesian_point((1.0, 1.0)),
    f.cartesian_point((0.0, 101.0)),  # DEFECT: spike at seam (should be (0,1))
]
cp_refs = ",".join(f"#{cp.eid}" for cp in uv_cps)
pc_bsp = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('pc_spike_bsp',3,({cp_refs}),"
    f".UNSPECIFIED.,.T.,.F.,(4,1,1,1,1,4),(0.,0.2,0.4,0.6,0.8,1.),.UNSPECIFIED.)"
)
pc_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_spike_def',(#{pc_bsp.eid}),#{prc.eid})"
)
pcurve_top = f._emit_raw(f"PCURVE('top_spiked',#{surf.eid},#{pc_def.eid})")
sc_top = f._emit_raw(
    f"SURFACE_CURVE('top_edge',#{bsp_3d.eid},(#{pcurve_top.eid}),.PCURVE_S1.)"
)
e_top = f._emit_raw(
    f"EDGE_CURVE('top_edge',#{v11.eid},#{v01.eid},#{sc_top.eid},.T.)"
)

loop = f.edge_loop([
    f.oriented_edge(e_bot,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_left,  True),
])
face = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
