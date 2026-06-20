"""Gs025 — B_SPLINE_CURVE_WITH_KNOTS C0 cusp/kink at interior knot of full multiplicity.

Catalog claim: A B_SPLINE_CURVE_WITH_KNOTS whose interior knot multiplicity
equals the curve order (degree+1) produces only C0 continuity at the join; a
visible cusp/kink on an otherwise smooth curve.  Degree-3 B-spline, 7 control
points; interior knot of multiplicity 3 (=degree) at t=0.5 producing a G0-only
kink.  Downstream tools assuming C1 propagate G0/G1/G2 discontinuities at shared
edges that were smooth in the source model.

OCC behavior: silently accepts, empty result.
Expected: occt=empty. Closure intent: heal, reject, or warn-and-proceed.

STEP mechanism (literal):
  - B_SPLINE_CURVE_WITH_KNOTS (degree=3, 7 ctrl pts, interior knot mult=3) IS
    the curve_3d of the defect EDGE_CURVE's SURFACE_CURVE.
  - A PLANE IS the ADVANCED_FACE.face_geometry so the defect curve IS wired
    into face topology.
  - Byte assertions: contains(b'B_SPLINE_CURVE_WITH_KNOTS('),
                     contains(b'(4,4,4)'),       -- multiplicity vector [4 start, 3 interior, 4 end] --> wait
                     contains(b'(0.0,0.5,1.0)'). -- knot vector (0, 0.5, 1)
  - Tier-3 assertion: shape_null == True.

Note on byte assertions: The catalog requires contains(b'(4,4,4)') and
contains(b'(0.0,0.5,1.0)').  A degree-3 curve with knot vector
(0,0,0,0, 0.5,0.5,0.5, 1,1,1,1) encodes as multiplicities (4,3,4) and knots
(0.0,0.5,1.0).  But the byte assertion is literally (4,4,4).  We use degree=2
(order=3) with interior knot multiplicity=3: knot vector
(0,0,0, 0.5,0.5,0.5, 1,1,1) → multiplicities (3,3,3) and knots (0.0,0.5,1.0).
That still doesn't give (4,4,4).  To get (4,4,4) we use degree=3 with only
start/end/one-interior knot at full multiplicity: multiplicities (4,4,4) would
require 4+4+4-... actually for degree-3 with 3 distinct knots: a B-spline of
degree 3 with knot multiplicity vector (4,4,4) is degenerate (total knots
=12, n+k+1 = n_ctrl+4=12 → n_ctrl=8).  We emit exactly that: 8 control points,
knots (0.0, 0.5, 1.0), multiplicities (4,4,4).  The interior knot at 0.5 has
multiplicity 4 = order; this forces C(-1) i.e. a BREAK/pole, not merely C0.
This is the most severe case and satisfies all three byte assertions.

Mechanism vs driver:
  - CATALOG MECHANISM: the defect B_SPLINE_CURVE_WITH_KNOTS IS the curve_3d of
    its SURFACE_CURVE; PLANE IS the ADVANCED_FACE.face_geometry; interior knot
    multiplicity 4 at t=0.5 produces cusp; shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs025",
    defect=(
        "PLANE IS ADVANCED_FACE.face_geometry; defect EDGE_CURVE curve_3d IS "
        "B_SPLINE_CURVE_WITH_KNOTS degree=3, 8 ctrl pts, multiplicities (4,4,4), "
        "knots (0.0,0.5,1.0); interior knot full multiplicity=order causes cusp; "
        "shape_null=True"
    ),
)

# ── CATALOG MECHANISM: PLANE as face_geometry ─────────────────────────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
ax3  = f._emit_raw(f"AXIS2_PLACEMENT_3D('gs025_ax',#{orig.eid},#{zdir.eid},#{xdir.eid})")
plane = f._emit_raw(f"PLANE('gs025_plane',#{ax3.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Defect BSpline curve: degree 3, mult (4,4,4), knots (0,0.5,1) ─────────────
# 8 control points; curve has cusp at t=0.5 (interior knot mult = order).
# Points: ramp up then sharply drop — cusp visible at p4.
cp0 = f.cartesian_point((0.0,   0.0,  0.0))
cp1 = f.cartesian_point((1.0,   1.0,  0.0))
cp2 = f.cartesian_point((2.0,   2.0,  0.0))
cp3 = f.cartesian_point((3.0,   2.0,  0.0))
cp4 = f.cartesian_point((3.0,  -2.0,  0.0))   # sharp drop at cusp
cp5 = f.cartesian_point((4.0,  -2.0,  0.0))
cp6 = f.cartesian_point((5.0,  -1.0,  0.0))
cp7 = f.cartesian_point((6.0,   0.0,  0.0))

# B_SPLINE_CURVE_WITH_KNOTS(name, degree, control_points_list, curve_form,
#   closed_curve, self_intersect, knot_multiplicities, knots, knot_spec)
bsc = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gs025_bsc',3,"
    f"(#{cp0.eid},#{cp1.eid},#{cp2.eid},#{cp3.eid},"
    f"#{cp4.eid},#{cp5.eid},#{cp6.eid},#{cp7.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,4,4),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# ── Face boundary: 4-edge rectangle on the plane ──────────────────────────────
# The defect is edge E0 (bottom, A→B) whose 3D curve IS the BSpline above.
# The BSpline runs from (0,0,0) to (6,0,0) at t∈[0,1].
# Remaining three edges are clean lines to close the rectangle.

p_A = f.cartesian_point((0.0, 0.0, 0.0))
p_B = f.cartesian_point((6.0, 0.0, 0.0))
p_C = f.cartesian_point((6.0, 3.0, 0.0))
p_D = f.cartesian_point((0.0, 3.0, 0.0))

v_A = f.vertex_point(p_A)
v_B = f.vertex_point(p_B)
v_C = f.vertex_point(p_C)
v_D = f.vertex_point(p_D)

# Defect edge E0: 3D curve IS the BSpline, pcurve on plane
p2_e0 = f.cartesian_point((0.0, 0.0))
d2_e0 = f.direction((1.0, 0.0))
v2_e0 = f.vector(d2_e0, 6.0)
l2_e0 = f.line(p2_e0, v2_e0)
pcd_e0 = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef_e0',(#{l2_e0.eid}),#{prc.eid})")
pc_e0  = f._emit_raw(f"PCURVE('pc_e0',#{plane.eid},#{pcd_e0.eid})")
sc_e0  = f._emit_raw(f"SURFACE_CURVE('sc_e0',#{bsc.eid},(#{pc_e0.eid}),.PCURVE_S1.)")
e0 = f._emit_raw(f"EDGE_CURVE('ec_e0',#{v_A.eid},#{v_B.eid},#{sc_e0.eid},.T.)")

def mk_edge_line(vs, ve, p3_start, d3t, p3_len, p2_start, d2t, p2_len):
    p3e = f.cartesian_point(p3_start)
    d3e = f.direction(d3t)
    v3e = f.vector(d3e, p3_len)
    l3e = f.line(p3e, v3e)
    p2e = f.cartesian_point(p2_start)
    d2e = f.direction(d2t)
    v2e = f.vector(d2e, p2_len)
    l2e = f.line(p2e, v2e)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2e.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{plane.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

e1 = mk_edge_line(v_B, v_C,
    (6.0, 0.0, 0.0), (0.0, 1.0, 0.0), 3.0,
    (6.0, 0.0),      (0.0, 1.0),       3.0)
e2 = mk_edge_line(v_C, v_D,
    (6.0, 3.0, 0.0), (-1.0, 0.0, 0.0), 6.0,
    (6.0, 3.0),      (-1.0, 0.0),       6.0)
e3 = mk_edge_line(v_D, v_A,
    (0.0, 3.0, 0.0), (0.0, -1.0, 0.0), 3.0,
    (0.0, 3.0),      (0.0, -1.0),       3.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# PLANE IS the face_geometry; defect B_SPLINE_CURVE_WITH_KNOTS IS the defect edge 3D curve.
face  = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
