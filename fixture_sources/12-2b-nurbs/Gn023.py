"""Gn023 — STEP→BREP silently injects new B_SPLINE_CURVE_WITH_KNOTS.

Catalog claim: After STEP→BREP round-trip via OCC BRepTools write,
B_SPLINE_CURVE_WITH_KNOTS instances appear that were never in the source;
analytic CIRCLE edges bounding a CYLINDRICAL_SURFACE are replaced with NURBS
approximations. Source: a cylinder with two CIRCLE cap edges where each
EDGE_CURVE uses the same VERTEX_POINT for start and end (closed circular
edges with one self-paired vertex per cap).

OCC behavior: silently accepts (no diagnostic, empty result). Expected: occt=empty.

STEP mechanism (literal):
  - CYLINDRICAL_SURFACE with radius=10.0, height=20.0 (lateral face).
  - Two cap faces bounded by closed circular EDGE_CURVE where start==end vertex
    (self-paired vertex — the hallmark of the closed-circle analytic edge that
    OCC's BRepTools writer replaces with B_SPLINE_CURVE_WITH_KNOTS on round-trip).
  - B_SPLINE_CURVE_WITH_KNOTS (degree 2, 9-CP rational circle approximation)
    labelled 'bspline_injected' to mark it as the injected curve.
  - The ADVANCED_FACE references this B_SPLINE_CURVE_WITH_KNOTS via SURFACE_CURVE
    instead of the original CIRCLE — this is the defect: silently-injected NURBS.
  - The structural mechanism (self-paired vertex + injected B-spline curve) IS the
    defect; no additional C-1 break needed (silent injection itself causes empty result).

Mechanism vs driver:
  - CATALOG MECHANISM: closed cap EDGE_CURVE with self-paired vertex (start==end)
    referencing B_SPLINE_CURVE_WITH_KNOTS 'bspline_injected' that replaced the
    source CIRCLE; this is the silently-injected NURBS defect.
  - No separate C-1 driver (silent injection mechanism drives shape_null).
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn023",
    defect=(
        "CYLINDRICAL_SURFACE lateral face + B_SPLINE_CURVE_WITH_KNOTS cap edge "
        "(degree 2, rational 9-CP circle approximation, self-paired vertex start==end); "
        "B-spline labelled 'bspline_injected' — CIRCLE replaced silently in BRep round-trip; "
        "structural mechanism: closed EDGE_CURVE with coincident start/end vertex + "
        "injected B-spline in lieu of analytic CIRCLE; silent injection IS the defect"
    ),
)

w_mid = math.sqrt(2.0) / 2.0  # ~0.7071 for exact NURBS circle

# ── DEFECT SURFACE: CYLINDRICAL_SURFACE ──────────────────────────────────────
# Cylinder: axis at origin, Z-up, radius=10, height=20.
# The lateral surface — the cylinder itself.
cyl_origin = f.cartesian_point((0.0, 0.0, 0.0))
cyl_axis_z = f.direction((0.0, 0.0, 1.0))
cyl_ref_x  = f.direction((1.0, 0.0, 0.0))
cyl_axis2  = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('cyl_ax',#{cyl_origin.eid},#{cyl_axis_z.eid},#{cyl_ref_x.eid})"
)
cyl_surf = f._emit_raw(
    f"CYLINDRICAL_SURFACE('cyl_surf',#{cyl_axis2.eid},10.0)"
)

# ── Parametric context ────────────────────────────────────────────────────────
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── INJECTED B_SPLINE_CURVE_WITH_KNOTS (rational 90°×4 arc circle approx) ────
# This is the curve that OCC's BRepTools writer silently injects instead of CIRCLE.
# Degree 2, 9 CPs (4 arcs of 90°), radius 10 in XY at Z=0.
# CPs: (10,0), (10,10), (0,10), (-10,10), (-10,0), (-10,-10), (0,-10), (10,-10), (10,0)
# Weights: alternating (1, w_mid, 1, w_mid, ...)
circle_xy = [
    (10.0,  0.0),
    (10.0,  10.0),
    (0.0,   10.0),
    (-10.0, 10.0),
    (-10.0, 0.0),
    (-10.0, -10.0),
    (0.0,   -10.0),
    (10.0,  -10.0),
    (10.0,  0.0),
]
weights_v = [1.0, w_mid, 1.0, w_mid, 1.0, w_mid, 1.0, w_mid, 1.0]

cap_cps = [f.cartesian_point((x, y, 0.0)) for (x, y) in circle_xy]
w_str = "(" + ",".join(str(w) for w in weights_v) + ")"

# Rational B-spline circle (complex entity with RATIONAL_B_SPLINE_CURVE)
# V knots: 4 arcs of 90°: (0, 0.25, 0.5, 0.75, 1.0) mults (3,2,2,2,3) sum=12=2+9+1 ✓
cp_ids = "(" + ",".join(f"#{p.eid}" for p in cap_cps) + ")"
injected_bspline = f._emit_raw(
    f"(B_SPLINE_CURVE('bspline_injected',2,"
    f"{cp_ids},"
    f".UNSPECIFIED.,.F.,.F.)"
    f"B_SPLINE_CURVE_WITH_KNOTS((3,2,2,2,3),"
    f"(0.0,0.25,0.5,0.75,1.0),.UNSPECIFIED.)"
    f"RATIONAL_B_SPLINE_CURVE({w_str})"
    f"REPRESENTATION_ITEM('bspline_injected')"
    f"BOUNDED_CURVE()"
    f"CURVE())"
)

# ── Closed cap edge with self-paired vertex (start == end) ───────────────────
# This is the structural hallmark: one vertex reused for both ends of a closed circle.
seam_pt = f.cartesian_point((10.0, 0.0, 0.0))
v_seam  = f.vertex_point(seam_pt)

# Pcurve for cap circle on cylindrical surface: V full revolution at U=0
pp0 = f.cartesian_point((0.0,   0.0))
pp1 = f.cartesian_point((0.0,   math.pi * 0.5))
pp2 = f.cartesian_point((0.0,   math.pi))
pp3 = f.cartesian_point((0.0,   math.pi * 1.5))
pp4 = f.cartesian_point((0.0,   math.pi * 2.0))

cap_pc_cps = [f.cartesian_point((0.0, 0.0)), f.cartesian_point((0.0, math.pi * 0.5)),
              f.cartesian_point((0.0, math.pi)), f.cartesian_point((0.0, math.pi * 1.5)),
              f.cartesian_point((0.0, math.pi * 2.0))]
cap_pc_ids = "(" + ",".join(f"#{p.eid}" for p in cap_pc_cps) + ")"

cap_pc_bspline = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('cap_pc',1,"
    f"{cap_pc_ids},"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(2,1,1,1,2),(0.0,0.25,0.5,0.75,1.0),.UNSPECIFIED.)"
)

cap_pcd = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('cap_pcdef',(#{cap_pc_bspline.eid}),#{prc.eid})"
)
cap_pc = f._emit_raw(f"PCURVE('cap_pc_ent',#{cyl_surf.eid},#{cap_pcd.eid})")
sc_cap = f._emit_raw(
    f"SURFACE_CURVE('cap_sc',#{injected_bspline.eid},(#{cap_pc.eid}),.PCURVE_S1.)"
)

# Self-paired vertex: start == end (closed edge — the hallmark of the CIRCLE replacement)
e_cap = f._emit_raw(
    f"EDGE_CURVE('cap_edge',#{v_seam.eid},#{v_seam.eid},#{sc_cap.eid},.T.)"
)

loop = f.edge_loop([
    f.oriented_edge(e_cap, True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], cyl_surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
