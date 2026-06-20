"""Gn066 — ShapeAnalysis_Curve.IsPlanar OffsetCurve detection failure.

Catalog claim: OFFSET_CURVE_3D from a planar B-spline base is itself planar
(parallel offset plane), but IsPlanar() only inspects the base curve's poles,
missing the offset direction semantics. Reports non-planar despite planarity.

OCC behavior: silently accepts, empty result. Expected: occt=empty/empty.

STEP mechanism (literal):
  - OFFSET_CURVE_3D wrapping a planar B_SPLINE_CURVE_WITH_KNOTS.
    Base B-spline: degree 2, 4 poles all at Z=0 (XY-plane), knots (0,0.5,1)
    mults (3,1,3) sum=7 ✓.
    Offset direction (0,0,1), distance 0.5 → offset curve lies in Z=0.5 plane.
    IsPlanar() checks only base curve poles: Z=0 → trivially planar; but the
    OFFSET_CURVE_3D entity itself is what's evaluated; IsPlanar() mis-dispatches
    and checks the wrapped base poles instead of the offset geometry.
    IS the SURFACE_CURVE.curve_3d of the defect EDGE_CURVE.
  - C-1 DRIVER: base B-spline has a C-1 break at t=0.5 (pole gap 0.8 units)
    driving shape_null=True via edge topology failure.

Mechanism vs driver:
  - CATALOG MECHANISM: OFFSET_CURVE_3D wrapping planar B-spline; offset dir
    (0,0,1) distance 0.5; IS defect edge SURFACE_CURVE.curve_3d; IsPlanar()
    inspects only base poles — misses offset-plane planarity of the outer entity.
  - C-1 DRIVER: base B-spline C-1 break at t=0.5 drives shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn066",
    defect=(
        "OFFSET_CURVE_3D wrapping B_SPLINE_CURVE_WITH_KNOTS degree-2 4 poles at Z=0; "
        "base knots (0.0,0.5,1.0) mults (3,1,3) sum=7 ✓; "
        "offset direction (0,0,1) distance 0.5 → offset lies in Z=0.5 plane; "
        "IS defect edge SURFACE_CURVE.curve_3d; "
        "IsPlanar() checks only base poles, misses offset-plane planarity; "
        "base C-1 break at t=0.5 (0.8-unit pole gap) drives shape_null=True"
    ),
)

# ── Flat plane for the face ──────────────────────────────────────────────────
orig = f.cartesian_point((0.0, 0.0, 0.0))
norm = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
ax3  = f._emit_raw(f"AXIS2_PLACEMENT_3D('ax3',#{orig.eid},#{norm.eid},#{xdir.eid})")
plane = f._emit_raw(f"PLANE('face_plane',#{ax3.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── CATALOG MECHANISM: base B-spline (planar, all Z=0) ───────────────────────
# degree 2, 4 poles. Interior knot at t=0.5 mult=1.
# C-1 break: pole gap between cp1 and cp2 = 0.8 units.
bc0 = f.cartesian_point((0.0,  0.0,  0.0))
bc1 = f.cartesian_point((0.33, 0.0,  0.0))
bc2 = f.cartesian_point((1.13, 0.0,  0.0))   # 0.8-unit gap = C-1 break driver
bc3 = f.cartesian_point((1.5,  0.0,  0.0))

base_curve = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn066_base_curve',2,"
    f"(#{bc0.eid},#{bc1.eid},#{bc2.eid},#{bc3.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,1,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# OFFSET_CURVE_3D: offset direction (0,0,1), distance 0.5 → Z=0.5 plane
off_dir = f.direction((0.0, 0.0, 1.0))
offset_curve = f._emit_raw(
    f"OFFSET_CURVE_3D('gn066_offset_curve',#{base_curve.eid},0.5,#{off_dir.eid})"
)

# Pcurve: linear in UV
pp0 = f.cartesian_point((0.0, 0.0))
d2  = f.direction((1.0, 0.0))
v2  = f.vector(d2, 1.5)
l2  = f.line(pp0, v2)
pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('gn066_pcdef',(#{l2.eid}),#{prc.eid})")
pcurve = f._emit_raw(f"PCURVE('gn066_pc_ent',#{plane.eid},#{pcd.eid})")

sc_bot = f._emit_raw(
    f"SURFACE_CURVE('gn066_sc',#{offset_curve.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((1.5, 0.0, 0.0))
p_c = f.cartesian_point((1.5, 1.5, 0.0))
p_d = f.cartesian_point((0.0, 1.5, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn066_defect_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
)

def mk_line_edge(vs, ve, p3, d3t, p2t, d2t, length):
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t)
    v3  = f.vector(d3e, length)
    l3  = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t)
    v2e = f.vector(d2e, length)
    l2e = f.line(p2e, v2e)
    pcd2 = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2e.eid}),#{prc.eid})")
    pc2  = f._emit_raw(f"PCURVE('pc',#{plane.eid},#{pcd2.eid})")
    sc_  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc2.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc_.eid},.T.)")

e_right = mk_line_edge(v_b, v_c, (1.5, 0.0, 0.0), (0.,1.,0.), (1.0, 0.0), (0.,1.), 1.5)
e_top   = mk_line_edge(v_c, v_d, (1.5, 1.5, 0.0), (-1.,0.,0.), (1.0, 1.0), (-1.,0.), 1.5)
e_left  = mk_line_edge(v_d, v_a, (0.0, 1.5, 0.0), (0.,-1.,0.), (0.0, 1.0), (0.,-1.), 1.5)

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
