"""Gn077 — ShapeAnalysis_Curve.IsClosed with self-intersecting direction reversal.

Catalog claim: IsClosed correctly detects closure and topological validity.
B-spline degree-2 curve with control polygon [P0,P1,P2,P3,P4] where P4=P0
(closes) but P2 direction-reversal causes self-intersection. IsClosed reports
closed but misses crossing.

OCC behavior: silently accepts, empty result. Expected: occt=empty/empty.

STEP mechanism (literal):
  - B_SPLINE_CURVE_WITH_KNOTS degree 2, 5 control points.
    Knots: (0.0, 0.5, 1.0) mults (3,2,3) sum=8=2+5+1 ✓
    Control points: P0=(0,0,0), P1=(2,2,0), P2=(1,-1,0) [direction reversal],
    P3=(-1,2,0), P4=(0,0,0)=P0. Closed by matching endpoints but
    P2 reversal creates self-intersection; IsClosed returns true, silently
    ignoring crossing. Near-degenerate parameterization at crossing drives
    shape_null=True.
    IS the SURFACE_CURVE.curve_3d of the defect EDGE_CURVE
    (the catalog mechanism IS the defect edge 3D curve).
  - C-1 DRIVER: direction-reversal control point at P2 introduces near-zero
    velocity near the crossing, driving shape_null=True via edge topology failure.

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_CURVE_WITH_KNOTS degree-2 5 poles; P4=P0
    (closed), P2=(1,-1,0) reversal creates self-intersection; IS defect edge
    SURFACE_CURVE.curve_3d; IsClosed misses crossing — reports closed but invalid.
  - C-1 DRIVER: near-zero velocity at crossing drives shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn077",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS degree-2 5 poles; "
        "knots (0.0,0.5,1.0) mults (3,2,3) sum=8 ✓; "
        "P0=(0,0,0) P1=(2,2,0) P2=(1,-1,0) [direction reversal] P3=(-1,2,0) P4=(0,0,0)=P0; "
        "IS defect edge SURFACE_CURVE.curve_3d; "
        "IsClosed reports closed but self-intersection at P2 reversal is missed; "
        "near-zero velocity at crossing drives shape_null=True"
    ),
)

# ── Flat plane for the face ───────────────────────────────────────────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
norm = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
ax3  = f._emit_raw(f"AXIS2_PLACEMENT_3D('ax3',#{orig.eid},#{norm.eid},#{xdir.eid})")
plane = f._emit_raw(f"PLANE('face_plane',#{ax3.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── CATALOG MECHANISM: B-spline degree-2, 5 poles, closed with direction reversal ──
# Knots (0.0,0.5,1.0) mults (3,2,3) sum=8=2+5+1 ✓
# P0=P4=(0,0,0); P2=(1,-1,0) causes direction reversal → self-intersection
cp0 = f.cartesian_point((0.0,  0.0, 0.0))
cp1 = f.cartesian_point((2.0,  2.0, 0.0))
cp2 = f.cartesian_point((1.0, -1.0, 0.0))  # direction reversal → self-intersection
cp3 = f.cartesian_point((-1.0, 2.0, 0.0))
cp4 = f.cartesian_point((0.0,  0.0, 0.0))  # = P0, closes the loop

mech_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn077_isclosed_reversal',2,"
    f"(#{cp0.eid},#{cp1.eid},#{cp2.eid},#{cp3.eid},#{cp4.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,2,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# pcurve: 2D line u∈[0,1] along bottom of face
pp0 = f.cartesian_point((0.0, 0.0))
pp1 = f.cartesian_point((1.0, 0.0))
d2  = f.direction((1.0, 0.0))
v2  = f.vector(d2, 1.0)
l2  = f.line(pp0, v2)
pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('gn077_pcdef',(#{l2.eid}),#{prc.eid})")
pc  = f._emit_raw(f"PCURVE('gn077_pc',#{plane.eid},#{pcd.eid})")
sc_defect = f._emit_raw(
    f"SURFACE_CURVE('gn077_sc',#{mech_3d.eid},(#{pc.eid}),.PCURVE_S1.)"
)

# Corner vertices; face spans [0,2]×[0,2] in XY
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((2.0, 0.0, 0.0))
p_c = f.cartesian_point((2.0, 2.0, 0.0))
p_d = f.cartesian_point((0.0, 2.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn077_defect_edge',#{v_a.eid},#{v_b.eid},#{sc_defect.eid},.T.)"
)

def mk_line_edge(vs, ve, p3, d3t, p2t, d2t, length):
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t)
    v3  = f.vector(d3e, length)
    l3  = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t)
    v2_ = f.vector(d2e, length)
    l2_ = f.line(p2e, v2_)
    pcd_ = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2_.eid}),#{prc.eid})")
    pc_  = f._emit_raw(f"PCURVE('pc',#{plane.eid},#{pcd_.eid})")
    sc_  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc_.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc_.eid},.T.)")

e_right = mk_line_edge(v_b, v_c, (2.0, 0.0, 0.0), (0.,1.,0.), (1.0, 0.0), (0.,1.), 2.0)
e_top   = mk_line_edge(v_c, v_d, (2.0, 2.0, 0.0), (-1.,0.,0.), (1.0, 1.0), (-1.,0.), 2.0)
e_left  = mk_line_edge(v_d, v_a, (0.0, 2.0, 0.0), (0.,-1.,0.), (0.0, 1.0), (0.,-1.), 2.0)

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
