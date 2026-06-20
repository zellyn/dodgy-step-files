"""Gp106 — CheckSameParameter spline-vs-spline-shifted.

Catalog claim: Edge with B-spline 3D curve and B-spline pcurve; pcurve's
parameter range [1, 2] is shifted 1.0 unit from 3D curve [0, 1].
CheckSameParameter compares raw ranges and reports false mismatch despite
representing identical geometry.

STEP mechanism (literal):
  - PLANE Z=0 face.
  - 3D curve: B_SPLINE_CURVE_WITH_KNOTS degree-2, 6 CPs, knot vector (3,3,3)
    at (0.0, 0.5, 1.0) — domain [0, 1]. C-1 positional break at t=0.5
    (CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0), 1.5-unit gap) drives shape_null=True.
  - PCurve: B_SPLINE_CURVE_WITH_KNOTS degree-2, 6 CPs, knot vector (3,3,3)
    at (1.0, 1.5, 2.0) — domain [1, 2] (shifted +1.0 from 3D domain).
    Smooth (no break). UV path (0,0)→(5,0).
  - THE CATALOG MECHANISM: 3D domain [0,1] vs PCurve domain [1,2]. A 1.0 shift.
    CheckSameParameter compares knot vectors numerically; finds domain mismatch
    and reports a false "SameParameter" failure even though the geometry is
    identical after reparametrization.
  - C-1 DRIVER: B-spline positional break forces shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp106",
    defect=(
        "PLANE Z=0; defect edge: 3D B_SPLINE_CURVE_WITH_KNOTS degree-2 knot "
        "domain [0,1] with C-1 break at t=0.5 (CP[2]=(1.5,0,0) vs "
        "CP[3]=(3.0,0,0), 1.5-unit gap); PCurve B_SPLINE_CURVE_WITH_KNOTS "
        "degree-2 knot domain [1,2] (+1.0 shift); CheckSameParameter compares "
        "raw knot ranges and reports false mismatch; C-1 break drives shape_null=True"
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

# THE CATALOG MECHANISM PART 1:
# 3D B-spline: degree-2, knot vector (3,3,3) at (0.0, 0.5, 1.0) — domain [0, 1].
# C-1 positional break at t=0.5: CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0) — 1.5-unit gap.
dc0 = f.cartesian_point((0.0, 0.0, 0.0))
dc1 = f.cartesian_point((0.75, 0.0, 0.0))
dc2 = f.cartesian_point((1.5,  0.0, 0.0))   # end of first Bezier
dc3 = f.cartesian_point((3.0,  0.0, 0.0))   # start of second — 1.5-unit gap = C-1 break
dc4 = f.cartesian_point((4.0,  0.0, 0.0))
dc5 = f.cartesian_point((5.0,  0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('shift_3d',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# THE CATALOG MECHANISM PART 2:
# PCurve B-spline: degree-2, knot vector (3,3,3) at (1.0, 1.5, 2.0) — domain [1, 2].
# Shifted +1.0 from the 3D domain [0,1]. Smooth path (0,0)→(5,0) in UV.
# CheckSameParameter compares domains [0,1] vs [1,2] and reports false mismatch.
pc0 = f.cartesian_point((0.0, 0.0))
pc1 = f.cartesian_point((1.2, 0.0))
pc2 = f.cartesian_point((2.5, 0.0))
pc3 = f.cartesian_point((3.5, 0.0))
pc4 = f.cartesian_point((4.3, 0.0))
pc5 = f.cartesian_point((5.0, 0.0))

bspline_pc = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('shift_pc',2,"
    f"(#{pc0.eid},#{pc1.eid},#{pc2.eid},#{pc3.eid},#{pc4.eid},#{pc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(1.0,1.5,2.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('shift_pc_def',(#{bspline_pc.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('shift_pc_ent',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('shift_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('shift_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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
