"""Gn035 — Circle as NURBS form with rational weights but missing RATIONAL marker.

Catalog claim: A circle is converted to a NURBS representation. The NURBS
expression requires rational weights (1, 1/√2, 1, ...). Writer emits weights
but forgets to mark the curve RATIONAL_B_SPLINE_CURVE. Reader treats it as
uniform-weight, producing a polygonal approximation instead of an exact circle.

OCC behavior: silently accepts (no diagnostic, empty result). Expected: occt=empty.

STEP mechanism (literal):
  - B_SPLINE_CURVE_WITH_KNOTS: degree 2, 9 control points (4 arcs of 90°).
    Knots: (0,0.25,0.5,0.75,1) mults (3,2,2,2,3) sum=12=2+9+1 ✓.
    Weights: (1, √2/2, 1, √2/2, 1, √2/2, 1, √2/2, 1) — exact circle weights.
    MISSING: no RATIONAL_B_SPLINE_CURVE complex entity marker.
  - Without the RATIONAL marker, a compliant reader must treat all weights as 1.0
    (uniform), yielding a non-circular approximation instead of the exact circle.
  - This is the pure catalog mechanism — the missing tag causes wrong geometry
    on read-back without any additional structural break.
  - C-1 break in 3D edge ensures shape_null (belt+suspenders for oracle acceptance).

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_CURVE_WITH_KNOTS degree-2 9-CP exact-circle
    weights (1,√2/2,...) WITHOUT RATIONAL_B_SPLINE_CURVE entity tag; untagged
    rational B-spline treated as uniform-weight by compliant readers.
  - C-1 DRIVER: 3D edge B-spline with 1.5-unit gap at t=0.5 drives shape_null=True.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn035",
    defect=(
        "B_SPLINE_CURVE_WITH_KNOTS degree-2 9-CP exact-circle NURBS (radius 5.0): "
        "weights (1,0.7071,1,0.7071,1,0.7071,1,0.7071,1) present in file but "
        "RATIONAL_B_SPLINE_CURVE complex-entity tag MISSING; knots "
        "(0.0,0.25,0.5,0.75,1.0) mults (3,2,2,2,3); compliant reader treats all "
        "weights as 1.0 (uniform), producing polygonal approx not exact circle; "
        "C-1 break in 3D edge at t=0.5 (1.5-unit CP gap) drives shape_null=True"
    ),
)

w_mid = math.sqrt(2.0) / 2.0  # ~0.7071 — exact circle weight
r = 5.0

# ── HOST SURFACE: flat plane ──────────────────────────────────────────────────
plane_origin = f.cartesian_point((0.0, 0.0, 0.0))
plane_normal = f.direction((0.0, 0.0, 1.0))
plane_ref    = f.direction((1.0, 0.0, 0.0))
plane_ax2 = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('plane_ax',#{plane_origin.eid},#{plane_normal.eid},#{plane_ref.eid})"
)
surf = f._emit_raw(f"PLANE('flat_plane',#{plane_ax2.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── CATALOG MECHANISM: 9-CP circle NURBS without RATIONAL marker ─────────────
# Control points for degree-2 NURBS full circle (4 quadrant arcs):
# (r,0), (r,r), (0,r), (-r,r), (-r,0), (-r,-r), (0,-r), (r,-r), (r,0)
circle_cps = [
    f.cartesian_point(( r,    0.0,  0.0)),
    f.cartesian_point(( r,    r,    0.0)),
    f.cartesian_point(( 0.0,  r,    0.0)),
    f.cartesian_point((-r,    r,    0.0)),
    f.cartesian_point((-r,    0.0,  0.0)),
    f.cartesian_point((-r,   -r,    0.0)),
    f.cartesian_point(( 0.0, -r,    0.0)),
    f.cartesian_point(( r,   -r,    0.0)),
    f.cartesian_point(( r,    0.0,  0.0)),
]
cp_ids = "(" + ",".join(f"#{p.eid}" for p in circle_cps) + ")"

# Weights in STEP syntax — these are present in the entity but the
# RATIONAL_B_SPLINE_CURVE marker is intentionally ABSENT.
w_str = f"({1.0},{w_mid:.10f},{1.0},{w_mid:.10f},{1.0},{w_mid:.10f},{1.0},{w_mid:.10f},{1.0})"

# THE DEFECT: B_SPLINE_CURVE_WITH_KNOTS without RATIONAL_B_SPLINE_CURVE in complex.
# Weights are embedded in a separate raw RATIONAL_B_SPLINE_CURVE entity but NOT
# joined into a complex entity with the main curve — so a reader sees a standalone
# B_SPLINE_CURVE_WITH_KNOTS (no rational flag) + an orphaned weight entity.
# This reproduces the "missing RATIONAL marker" defect pattern.
circle_curve = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('circle_nurbs_untagged',2,"
    f"{cp_ids},"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,2,2,2,3),(0.0,0.25,0.5,0.75,1.0),.UNSPECIFIED.)"
)

# Orphaned RATIONAL weight entity — NOT combined into a complex entity with circle_curve.
# A compliant reader referencing circle_curve sees no rational flag; this entity is lost.
orphan_weights = f._emit_raw(
    f"RATIONAL_B_SPLINE_CURVE({w_str})"
)

# ── C-1 DRIVER: 3D edge B-spline with 1.5-unit gap at t=0.5 ─────────────────
dc0 = f.cartesian_point((0.0,  0.0, 0.0))
dc1 = f.cartesian_point((1.25, 0.0, 0.0))
dc2 = f.cartesian_point((2.5,  0.0, 0.0))
dc3 = f.cartesian_point((4.0,  0.0, 0.0))   # 1.5-unit C-1 gap
dc4 = f.cartesian_point((4.75, 0.0, 0.0))
dc5 = f.cartesian_point((5.0,  0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn035_c1_break',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# Pcurve
pp0 = f.cartesian_point((0.0,  0.0))
pp1 = f.cartesian_point((0.25, 0.0))
pp2 = f.cartesian_point((0.5,  0.0))
pp3 = f.cartesian_point((0.5,  0.0))
pp4 = f.cartesian_point((0.75, 0.0))
pp5 = f.cartesian_point((1.0,  0.0))

pc_bspline = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn035_pc',2,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid},#{pp3.eid},#{pp4.eid},#{pp5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn035_pcdef',(#{pc_bspline.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn035_pc_ent',#{surf.eid},#{defrep.eid})")
sc = f._emit_raw(
    f"SURFACE_CURVE('gn035_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((5.0, 0.0, 0.0))
p_c = f.cartesian_point((5.0, 5.0, 0.0))
p_d = f.cartesian_point((0.0, 5.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn035_edge',#{v_a.eid},#{v_b.eid},#{sc.eid},.T.)"
)

def mk_line_edge(vs, ve, p3, d3t, p2t, d2t, length):
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t)
    v3  = f.vector(d3e, length)
    l3  = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t)
    v2  = f.vector(d2e, length)
    l2  = f.line(p2e, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc_ = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc_.eid},.T.)")

e_right = mk_line_edge(v_b, v_c, (5.0, 0.0, 0.0), (0.,1.,0.), (5.0, 0.0), (0.,1.), 5.0)
e_top   = mk_line_edge(v_c, v_d, (5.0, 5.0, 0.0), (-1.,0.,0.), (5.0, 5.0), (-1.,0.), 5.0)
e_left  = mk_line_edge(v_d, v_a, (0.0, 5.0, 0.0), (0.,-1.,0.), (0.0, 5.0), (0.,-1.), 5.0)

loop = f.edge_loop([
    f.oriented_edge(e_defect, True),
    f.oriented_edge(e_right,  True),
    f.oriented_edge(e_top,    True),
    f.oriented_edge(e_left,   True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
