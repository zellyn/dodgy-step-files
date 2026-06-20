"""Gb004 — Pcurve and 3D curve disagree by a measurable distance (CheckCurveOnSurface).

Catalog claim: An EDGE_CURVE has a 3D LINE and a PCURVE whose surface-evaluation
diverges 0.01 mm from the line at the mid-point. GeomLib_CheckCurveOnSurface
reports max distance exceeds tolerance. Heal by reprojecting or bumping tolerance.

OCC behavior: silently accepts, empty result. Expected: occt=empty.

STEP mechanism (literal):
  - A flat PLANE is the ADVANCED_FACE.face_geometry (carrier surface).
  - The defect EDGE_CURVE uses a SURFACE_CURVE whose:
      curve_3d = a LINE along X (y=0, z=0)
      associated pcurves = a PCURVE whose B_SPLINE_CURVE_2D deviates 0.01 in V
        at the midpoint, making the surface-evaluated 3D path diverge from the
        LINE by 0.01 mm.
  - Byte assertions: contains(b'PCURVE('), contains(b'SURFACE_CURVE('),
    contains(b'EDGE_CURVE(').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: SURFACE_CURVE with mismatched LINE (3D) + deviated PCURVE
    (2D B-spline, 0.01 mm max divergence at midpoint) IS the defect
    EDGE_CURVE.edge_geometry; wired as the bottom edge of the ADVANCED_FACE.
  - shape_null driver: pcurve/3D-curve inconsistency detected by
    GeomLib_CheckCurveOnSurface; tolerance gap forces null shape.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gb004",
    defect=(
        "SURFACE_CURVE: 3D LINE along X (y=0) paired with 2D B-spline pcurve "
        "that bows 0.01 in V at midpoint; max surface-eval vs 3D distance = 0.01 mm "
        "exceeds declared tolerance; GeomLib_CheckCurveOnSurface reports deviation; "
        "IS defect EDGE_CURVE.edge_geometry in ADVANCED_FACE loop; shape(1) (live OCC heals)"
    ),
)

# ── CARRIER PLANE: face_geometry ─────────────────────────────────────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
norm = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
ax3  = f._emit_raw(f"AXIS2_PLACEMENT_3D('ax3',#{orig.eid},#{norm.eid},#{xdir.eid})")
plane = f._emit_raw(f"PLANE('carrier_plane',#{ax3.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── CATALOG MECHANISM: 3D LINE + deviated 2D B-spline pcurve ─────────────────
# 3D LINE: along X axis from (0,0,0) to (4,0,0)
p3_start = f.cartesian_point((0.0, 0.0, 0.0))
d3 = f.direction((1.0, 0.0, 0.0))
v3 = f.vector(d3, 4.0)
line_3d = f.line(p3_start, v3)

# 2D pcurve B-spline: degree-2, bows to V=0.01 at midpoint (t=0.5).
# Control points: (0,0), (0.5, 0.01), (1.0, 0)  — parabolic bow in V.
# U coordinate maps to X (face is 4 units wide); V offset = 0.01 in world units.
pp0 = f.cartesian_point((0.0,  0.0))
pp1 = f.cartesian_point((0.5,  0.01))   # 0.01 mm bow from the 3D line
pp2 = f.cartesian_point((1.0,  0.0))

pc_bspline = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gb004_deviated_pc',2,"
    f"(#{pp0.eid},#{pp1.eid},#{pp2.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3),(0.0,1.0),.UNSPECIFIED.)"
)

pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('gb004_pcdef',(#{pc_bspline.eid}),#{prc.eid})")
pcurve = f._emit_raw(f"PCURVE('gb004_pc',#{plane.eid},#{pcd.eid})")

# SURFACE_CURVE: 3D line paired with deviated pcurve — the mismatch IS the defect
sc_defect = f._emit_raw(
    f"SURFACE_CURVE('gb004_sc',#{line_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

# ── Topology: defect SURFACE_CURVE IS the bottom edge of the face ─────────────
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((4.0, 0.0, 0.0))
p_c = f.cartesian_point((4.0, 4.0, 0.0))
p_d = f.cartesian_point((0.0, 4.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gb004_defect',#{v_a.eid},#{v_b.eid},#{sc_defect.eid},.T.)"
)

def mk_line_edge(vs, ve, p3, d3t, p2t, d2t, length):
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t)
    v3e = f.vector(d3e, length)
    l3e = f.line(p3e, v3e)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t)
    v2e = f.vector(d2e, length)
    l2e = f.line(p2e, v2e)
    pcd2 = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2e.eid}),#{prc.eid})")
    pc2  = f._emit_raw(f"PCURVE('pc',#{plane.eid},#{pcd2.eid})")
    sc_  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc2.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc_.eid},.T.)")

e_right = mk_line_edge(v_b, v_c, (4.0, 0.0, 0.0), (0.,1.,0.), (1.0, 0.0), (0.,1.), 4.0)
e_top   = mk_line_edge(v_c, v_d, (4.0, 4.0, 0.0), (-1.,0.,0.), (1.0, 1.0), (-1.,0.), 4.0)
e_left  = mk_line_edge(v_d, v_a, (0.0, 4.0, 0.0), (0.,-1.,0.), (0.0, 1.0), (0.,-1.), 4.0)

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
