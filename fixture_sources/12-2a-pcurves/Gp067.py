"""Gp067 -- ShapeAnalysis_Edge.CheckCurve3dWithPCurve trimmed-bspline misclassification.

Catalog claim: Edge whose 3D curve is a TRIMMED_CURVE wrapping a BSpline;
the trim window restricts to a portion where the PCurve mismatch is hidden,
causing misclassification (edge marked OK when it should be flagged).

Fixture: PLANE face. The defect edge's 3D curve is a TRIMMED_CURVE with:
  - BASIS_CURVE: degree-2 B-spline, 6 control points, with a C-1 POSITIONAL
    BREAK at t=0.3 (knot mult=3, CP[2]=(0,0,0) vs CP[3]=(1.5,0,0) -- a
    1.5-unit gap). The break is at t=0.3, OUTSIDE the trim window [0.5, 1.0].
  - TRIM range: [0.5, 1.0] (PARAMETER_VALUE trim type). The trim window
    starts AFTER the break, masking the out-of-window discontinuity.
  - PCurve: linear (1.5,0)->(3.5,0), matching the trimmed portion endpoint
    positions but ignoring the break at t=0.3 outside the window.

CheckCurve3dWithPCurve evaluates only within [0.5, 1.0] (the trim window)
and sees no mismatch there; the large positional break at t=0.3 outside the
window goes unreported. The broken basis B-spline causes OCC shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp067",
    defect=(
        "PLANE face; defect edge: 3D curve is TRIMMED_CURVE(basis=degree-2 "
        "B-spline 6CPs with C-1 positional break at t=0.3 (knot mult=3, "
        "CP[2]=(0,0,0) vs CP[3]=(1.5,0,0)), trim=[0.5,1.0]); "
        "PCurve linear (1.5,0)->(3.5,0) matches trim window; "
        "CheckCurve3dWithPCurve misses break outside trim; OCC shape_null"
    ),
)

# Host surface: planar XY
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
surf = f.plane(plc)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Face vertices at the trim-window 3D endpoints:
# At t=0.5 in the basis B-spline, the curve is at approximately (1.5, 0, 0).
# At t=1.0, the curve ends at (3.5, 0, 0).
p_a = f.cartesian_point((1.5, 0.0, 0.0))
p_b = f.cartesian_point((3.5, 0.0, 0.0))
p_c = f.cartesian_point((3.5, 1.0, 0.0))
p_d = f.cartesian_point((1.5, 1.0, 0.0))
v_a = f.vertex_point(p_a); v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c); v_d = f.vertex_point(p_d)

d_up = f.direction((0.0, 1.0, 0.0)); vec_up = f.vector(d_up, 1.0)
d_lt = f.direction((-1.0, 0.0, 0.0)); vec_lt = f.vector(d_lt, 2.0)
d_dn = f.direction((0.0, -1.0, 0.0)); vec_dn = f.vector(d_dn, 1.0)
e_right = f.edge_curve(v_b, v_c, f.line(p_b, vec_up))
e_top   = f.edge_curve(v_c, v_d, f.line(p_c, vec_lt))
e_left  = f.edge_curve(v_d, v_a, f.line(p_d, vec_dn))

# ── DEFECT EDGE — bottom (v_a -> v_b) ────────────────────────────────────────
# Basis B-spline: degree 2, 6 CPs.
# knot vector: mult=3 at t=0.0, mult=3 at t=0.3 (break), mult=3 at t=1.0.
# Break at t=0.3: CP[2]=(0.0,0.0,0.0) vs CP[3]=(1.5,0.0,0.0) -- 1.5-unit gap.
# This break is OUTSIDE the trim window [0.5, 1.0].
# Within [0.5, 1.0] (the second Bezier segment), CPs [3..5] form a smooth
# path from approximately (1.5,0,0) to (3.5,0,0) -- appears linear to
# CheckCurve3dWithPCurve.
bc0 = f.cartesian_point((0.0, 0.5, 0.0))     # outside trim: oscillation before break
bc1 = f.cartesian_point((0.0, 0.0, 0.0))     # outside trim: pre-break segment control
bc2 = f.cartesian_point((0.0, 0.0, 0.0))     # immediately before break
bc3 = f.cartesian_point((1.5, 0.0, 0.0))     # immediately after break: 1.5-unit X gap
bc4 = f.cartesian_point((2.5, 0.0, 0.0))     # smooth within trim window
bc5 = f.cartesian_point((3.5, 0.0, 0.0))     # end of basis curve (= trim end)

basis_bspline = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('trimmed_basis',2,"
    f"(#{bc0.eid},#{bc1.eid},#{bc2.eid},#{bc3.eid},#{bc4.eid},#{bc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.3,1.0),.UNSPECIFIED.)"
)

# TRIMMED_CURVE: trim window [0.5, 1.0] -- starts AFTER the break at t=0.3.
# CheckCurve3dWithPCurve only samples t in [0.5, 1.0] and sees a clean path;
# the break at t=0.3 is outside and invisible to the checker.
trim_3d = f._emit_raw(
    f"TRIMMED_CURVE('trimmed_masking',#{basis_bspline.eid},"
    f"(PARAMETER_VALUE(0.5)),(PARAMETER_VALUE(1.0)),.T.,.PARAMETER.)"
)

# PCurve: linear (1.5,0)->(3.5,0) -- matches the trim-window portion.
pc_start = f.cartesian_point((1.5, 0.0))
pc_dir   = f.direction((1.0, 0.0))
pc_vec   = f.vector(pc_dir, 2.0)
pc_line  = f.line(pc_start, pc_vec)
defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('bot_pc_def',(#{pc_line.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('bot_linear',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('bot',#{trim_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('bot',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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
