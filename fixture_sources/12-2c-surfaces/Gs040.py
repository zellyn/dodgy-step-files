"""Gs040 — High-curvature curve / cusp from NURBS knot insertion.

Catalog claim: A B_SPLINE_CURVE with a multi-knot near full-degree
multiplicity producing a near-cusp. Rational or polynomial BSpline with
a full-multiplicity interior knot creates a C0-only (cusp) point; downstream
meshers over-resolve or fail. Knot sequence (4,3,4) with parameter (0.0,0.5,1.0)
demonstrates a degree-3 curve with interior knot at multiplicity 3 (= degree),
producing a cusp.

OCC behavior: silently accepts (empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_CURVE_WITH_KNOTS IS the curve_3d of the defect EDGE_CURVE's
    SURFACE_CURVE, which IS wired into the ADVANCED_FACE boundary.
  - Knot multiplicities (4,3,4) with knot values (0.0,0.5,1.0) on a degree-3
    curve: interior multiplicity 3 == degree → C0 cusp at t=0.5.
  - Byte assertions: contains(b'B_SPLINE_CURVE_WITH_KNOTS('),
                     contains(b'(4,3,4)'),
                     contains(b'(0.0,0.5,1.0)').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: PLANE IS the ADVANCED_FACE.face_geometry;
    B_SPLINE_CURVE_WITH_KNOTS with knot multiplicity (4,3,4)/(0.0,0.5,1.0)
    IS the curve_3d of the defect EDGE_CURVE; near-cusp IS wired into face
    topology via the defect edge.
  - shape_null driver: C0 cusp in edge curve cannot be meshed; strict
    heal-or-reject kernels produce null shape.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs040",
    defect=(
        "PLANE IS ADVANCED_FACE.face_geometry; "
        "B_SPLINE_CURVE_WITH_KNOTS degree-3 with knot multiplicities (4,3,4) "
        "at (0.0,0.5,1.0) — interior multiplicity=degree creates C0 cusp — "
        "IS curve_3d of defect EDGE_CURVE; cusp IS wired into face topology; shape(1) (live OCC heals)"
    ),
)

# ── CATALOG MECHANISM: PLANE as face_geometry ─────────────────────────────────
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
ax3   = f._emit_raw(f"AXIS2_PLACEMENT_3D('gs040_ax',#{orig.eid},#{zdir.eid},#{xdir.eid})")
plane = f._emit_raw(f"PLANE('gs040_plane',#{ax3.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── B_SPLINE_CURVE_WITH_KNOTS: degree 3, multiplicities (4,3,4) ───────────────
# Degree 3 with interior knot multiplicity 3 == degree → C0 cusp at t=0.5.
# Control points: 4+3+4 - (3+1) = 6 control points (n+1 = degree + sum(mult) - degree - 1)
# Actually for degree d, sum(mult) = n+d+2 where n+1 = #ctrl pts.
# sum(mult) = 4+3+4 = 11; n+1 = 11 - d - 1 = 11 - 3 - 1 = 7 control points.
# Byte assertion: contains(b'B_SPLINE_CURVE_WITH_KNOTS(')
cp0 = f.cartesian_point((0.0, 0.0, 0.0))
cp1 = f.cartesian_point((1.0, 2.0, 0.0))
cp2 = f.cartesian_point((2.0, -2.0, 0.0))
cp3 = f.cartesian_point((3.0, 0.0, 0.0))   # cusp vertex — duplicated control
cp4 = f.cartesian_point((3.0, 0.0, 0.0))   # same point → cusp
cp5 = f.cartesian_point((4.0, 2.0, 0.0))
cp6 = f.cartesian_point((5.0, 0.0, 0.0))

# Byte assertion: contains(b'(4,3,4)')
# Byte assertion: contains(b'(0.0,0.5,1.0)')
bsc = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gs040_bsc',3,"
    f"(#{cp0.eid},#{cp1.eid},#{cp2.eid},#{cp3.eid},#{cp4.eid},#{cp5.eid},#{cp6.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,3,4),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# ── Face boundary: defect edge E0 uses B_SPLINE_CURVE as curve_3d ─────────────
p_A = f.cartesian_point((0.0, 0.0, 0.0))
p_B = f.cartesian_point((5.0, 0.0, 0.0))
p_C = f.cartesian_point((5.0, 4.0, 0.0))
p_D = f.cartesian_point((0.0, 4.0, 0.0))

v_A = f.vertex_point(p_A)
v_B = f.vertex_point(p_B)
v_C = f.vertex_point(p_C)
v_D = f.vertex_point(p_D)

# Defect edge E0: curve_3d IS B_SPLINE_CURVE_WITH_KNOTS (cusp at t=0.5)
p2_e0 = f.cartesian_point((0.0, 0.0))
d2_e0 = f.direction((1.0, 0.0))
v2_e0 = f.vector(d2_e0, 5.0)
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

e1 = mk_edge_line(v_B, v_C, (5.0,0.0,0.0), (0.0,1.0,0.0), 4.0, (5.0,0.0), (0.0,1.0), 4.0)
e2 = mk_edge_line(v_C, v_D, (5.0,4.0,0.0), (-1.0,0.0,0.0), 5.0, (5.0,4.0), (-1.0,0.0), 5.0)
e3 = mk_edge_line(v_D, v_A, (0.0,4.0,0.0), (0.0,-1.0,0.0), 4.0, (0.0,4.0), (0.0,-1.0), 4.0)

loop = f.edge_loop([
    f.oriented_edge(e0, True),
    f.oriented_edge(e1, True),
    f.oriented_edge(e2, True),
    f.oriented_edge(e3, True),
])

# PLANE IS the face_geometry; B_SPLINE_CURVE_WITH_KNOTS(cusp) IS the defect edge 3D curve.
face  = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
