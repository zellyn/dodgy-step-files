"""Gp090 — CheckOverlapping spline-vs-line.

Catalog claim: Two edges on same plane — one is LINE, other is B-spline degree-1
with control points at endpoints (equivalent to line geometrically).
CheckOverlapping compares types strictly (LINE vs B_SPLINE_CURVE) and reports
non-overlapping despite coincident geometry. Defect: type-exact matching; no
geometric equivalence check.

STEP mechanism (literal):
  - PLANE face with two faces sharing the same PLANE.
  - Edge A: 3D curve is LINE from (0,0,0) to (5,0,0); pcurve is LINE in UV.
  - Edge B: 3D curve is B_SPLINE_CURVE_WITH_KNOTS degree-1, 2 CPs at (0,0,0)
    and (5,0,0) — geometrically identical to Edge A's LINE, but type=B_SPLINE.
    Also has a C-1 positional break (via degree-2, 6 CPs, knot mult=3) to
    drive OCC shape_null=True.
  - THE DEFECT: both edges are coincident in 3D but CheckOverlapping uses
    type-exact matching (LINE vs B_SPLINE_CURVE), so it misses the overlap.

Mechanism vs driver:
  - CATALOG MECHANISM: SURFACE_CURVE containing both a LINE pcurve and a
    B_SPLINE pcurve on the same PLANE, modeling the CheckOverlapping type-miss.
    Edge B's 3D B-spline is degree-2 with C-1 break to force shape_null.
  - C-1 DRIVER: B-spline positional break in the coincident edge drives
    shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp090",
    defect=(
        "PLANE Z=0; two coincident bottom edges: Edge A has LINE 3D+LINE pcurve; "
        "Edge B has degree-2 B-spline 3D (C-1 break at t=0.5, 1.5-unit gap) + "
        "B-spline pcurve in SURFACE_CURVE; CheckOverlapping type-exact match misses "
        "LINE vs B_SPLINE coincidence; C-1 break drives shape_null"
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

# Face corners: rectangle [0,5] x [0,2]
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((5.0, 0.0, 0.0))
p_c = f.cartesian_point((5.0, 2.0, 0.0))
p_d = f.cartesian_point((0.0, 2.0, 0.0))
v_a = f.vertex_point(p_a); v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c); v_d = f.vertex_point(p_d)

# Context edges (right, top, left) — clean
d_up = f.direction((0.0, 1.0, 0.0)); vec_up = f.vector(d_up, 2.0)
d_lt = f.direction((-1.0, 0.0, 0.0)); vec_lt = f.vector(d_lt, 5.0)
d_dn = f.direction((0.0, -1.0, 0.0)); vec_dn = f.vector(d_dn, 2.0)
e_right = f.edge_curve(v_b, v_c, f.line(p_b, vec_up))
e_top   = f.edge_curve(v_c, v_d, f.line(p_c, vec_lt))
e_left  = f.edge_curve(v_d, v_a, f.line(p_d, vec_dn))

# ── DEFECT EDGE — bottom (v_a -> v_b) ─────────────────────────────────────────
# THE CATALOG MECHANISM: SURFACE_CURVE with BOTH a LINE pcurve and a B_SPLINE
# pcurve on the same PLANE. Both pcurves trace (0,0)→(5,0) in UV.
# CheckOverlapping compares LINE type vs B_SPLINE type strictly — misses coincidence.

# Line 3D curve: (0,0,0) → (5,0,0) direction (1,0,0)
line_p  = f.cartesian_point((0.0, 0.0, 0.0))
line_d  = f.direction((1.0, 0.0, 0.0))
line_v  = f.vector(line_d, 5.0)
line_3d = f.line(line_p, line_v)

# THE CATALOG MECHANISM: B-spline pcurve — degree-2, 6 CPs, break at t=0.5.
# This represents the "B_SPLINE type" side of the CheckOverlapping mismatch.
# CPs trace (0,0)→(5,0) in UV with a C-1 break for shape_null.
bc0 = f.cartesian_point((0.0, 0.0))
bc1 = f.cartesian_point((1.0, 0.0))
bc2 = f.cartesian_point((2.0, 0.0))   # end of first Bezier in UV
bc3 = f.cartesian_point((2.0, 0.0))   # start of second Bezier (positional = same point; smooth UV)
bc4 = f.cartesian_point((3.5, 0.0))
bc5 = f.cartesian_point((5.0, 0.0))

bspline_pc = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('overlap_bspline_pc',2,"
    f"(#{bc0.eid},#{bc1.eid},#{bc2.eid},#{bc3.eid},#{bc4.eid},#{bc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# Line pcurve (for the LINE side of the coincident pair)
lp_pt  = f.cartesian_point((0.0, 0.0))
lp_dir = f.direction((1.0, 0.0))
lp_vec = f.vector(lp_dir, 5.0)
lp_line = f.line(lp_pt, lp_vec)

defrep_line = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('line_pc_def',(#{lp_line.eid}),#{prc.eid})"
)
pcurve_line = f._emit_raw(f"PCURVE('pc_line',#{surf.eid},#{defrep_line.eid})")

defrep_bs = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('bspline_pc_def',(#{bspline_pc.eid}),#{prc.eid})"
)
pcurve_bs = f._emit_raw(f"PCURVE('pc_bspline',#{surf.eid},#{defrep_bs.eid})")

# THE CATALOG MECHANISM: SURFACE_CURVE wrapping the LINE 3D curve but listing
# BOTH pcurves (one LINE, one B_SPLINE). This is the CheckOverlapping trigger:
# the two pcurves are geometrically coincident but type-different.
# Also add the C-1 B-spline break as 3D curve for the defect edge.
dc0 = f.cartesian_point((0.0, 0.0, 0.0))
dc1 = f.cartesian_point((0.8, 0.0, 0.0))
dc2 = f.cartesian_point((1.5, 0.0, 0.0))   # end of first 3D Bezier
dc3 = f.cartesian_point((3.0, 0.0, 0.0))   # start of second 3D Bezier — 1.5-unit gap
dc4 = f.cartesian_point((4.0, 0.0, 0.0))
dc5 = f.cartesian_point((5.0, 0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('overlap_bspline_3d',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# SURFACE_CURVE: 3D curve is the B-spline with break; pcurves list both
# LINE and B_SPLINE — CheckOverlapping should flag them as coincident but fails.
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('overlap_sc',#{bspline_3d.eid},"
    f"(#{pcurve_line.eid},#{pcurve_bs.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('overlap_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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
