"""Gn051 — ShapeAnalysis_Curve.GetSamplePoints offset/trimmed recursion depth.

Catalog claim: Curve nesting OFFSET_CURVE(TRIMMED_CURVE(B_SPLINE)) with
0.5mm offset on trimmed domain [0.25, 0.75]. GetSamplePoints recursion selects
incorrect sample density when unwrapping nested derivative curves; interior
evaluation may fail.

OCC behavior: silently accepts, empty result. Expected: occt=empty.

STEP mechanism (literal):
  - Base: B_SPLINE_CURVE_WITH_KNOTS degree-2, 4-point in XY plane.
  - TRIMMED_CURVE wrapping that B-spline, trim parameters [0.25, 0.75].
  - OFFSET_CURVE_3D wrapping the trimmed curve, offset distance 0.5, direction Z.
  - The OFFSET_CURVE_3D IS the SURFACE_CURVE.curve_3d of the defect EDGE_CURVE;
    GetSamplePoints hits nested recursion path that selects wrong density.
  - C-1 DRIVER: the B-spline base has a 1.5-unit positional gap at its interior
    knot (t=0.5) which also drives shape_null via topology.

Mechanism vs driver:
  - CATALOG MECHANISM: nested OFFSET_CURVE_3D(TRIMMED_CURVE(B_SPLINE_CURVE_WITH_KNOTS))
    IS the defect edge's SURFACE_CURVE.curve_3d; GetSamplePoints unwraps nested
    bases and selects incorrect sample density, causing interior evaluation failure.
  - C-1 DRIVER: B-spline base has 1.5-unit positional gap at t=0.5 driving
    shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn051",
    defect=(
        "OFFSET_CURVE_3D wrapping TRIMMED_CURVE(B_SPLINE_CURVE_WITH_KNOTS) "
        "IS defect edge SURFACE_CURVE.curve_3d; offset 0.5mm Z-direction on "
        "trimmed domain [0.25,0.75]; GetSamplePoints nested recursion selects "
        "wrong sample density unwrapping OFFSET→TRIMMED→BSPLINE; "
        "B-spline base has 1.5-unit CP gap at t=0.5 driving shape_null=True"
    ),
)

# ── Plane surface for the face ───────────────────────────────────────────────
# Simple flat surface as face geometry (the mechanism is on the edge, not the surface)
orig = f.cartesian_point((0.0, 0.0, 0.0))
norm = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
ax3  = f._emit_raw(f"AXIS2_PLACEMENT_3D('ax3',#{orig.eid},#{norm.eid},#{xdir.eid})")
plane = f._emit_raw(f"PLANE('face_plane',#{ax3.eid})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── CATALOG MECHANISM: B_SPLINE base → TRIMMED → OFFSET ─────────────────────
# B-spline degree-2, 4 control points. Interior knot at t=0.5.
# CP gap: (2.0,0,0) then (3.5,0,0) = 1.5-unit jump = C-1 break + shape_null driver.
bc0 = f.cartesian_point((0.0, 0.0, 0.0))
bc1 = f.cartesian_point((1.0, 0.5, 0.0))
bc2 = f.cartesian_point((2.0, 0.0, 0.0))
bc3 = f.cartesian_point((3.5, 0.0, 0.0))   # 1.5-unit gap at t=0.5
bc4 = f.cartesian_point((4.5, 0.5, 0.0))
bc5 = f.cartesian_point((5.0, 0.0, 0.0))

base_bspline = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('gn051_base',2,"
    f"(#{bc0.eid},#{bc1.eid},#{bc2.eid},#{bc3.eid},#{bc4.eid},#{bc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# TRIMMED_CURVE: trims the B-spline to domain [0.25, 0.75] (PARAMETER sense)
trim_sense_lo = f._emit_raw(f"PARAMETER_VALUE(0.25)")
trim_sense_hi = f._emit_raw(f"PARAMETER_VALUE(0.75)")
trimmed = f._emit_raw(
    f"TRIMMED_CURVE('gn051_trimmed',#{base_bspline.eid},"
    f"(#{trim_sense_lo.eid}),(#{trim_sense_hi.eid}),.T.,.PARAMETER.)"
)

# OFFSET_CURVE_3D: 0.5mm offset in Z direction
off_dir = f.direction((0.0, 0.0, 1.0))
offset_curve = f._emit_raw(
    f"OFFSET_CURVE_3D('gn051_offset',#{trimmed.eid},0.5,#{off_dir.eid})"
)

# Pcurve for the defect edge (linear in UV, from (0,0) to (1,0))
pp0 = f.cartesian_point((0.0, 0.0))
pp1 = f.cartesian_point((1.0, 0.0))
d2  = f.direction((1.0, 0.0))
v2  = f.vector(d2, 1.0)
l2  = f.line(pp0, v2)
pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('gn051_pcdef',(#{l2.eid}),#{prc.eid})")
pcurve = f._emit_raw(f"PCURVE('gn051_pc_ent',#{plane.eid},#{pcd.eid})")

# SURFACE_CURVE: offset_curve IS the curve_3d
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('gn051_sc',#{offset_curve.eid},(#{pcurve.eid}),.PCURVE_S1.)"
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
    f"EDGE_CURVE('gn051_defect_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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

e_right = mk_line_edge(v_b, v_c, (5.0, 0.0, 0.0), (0.,1.,0.), (1.0, 0.0), (0.,1.), 5.0)
e_top   = mk_line_edge(v_c, v_d, (5.0, 5.0, 0.0), (-1.,0.,0.), (1.0, 1.0), (-1.,0.), 5.0)
e_left  = mk_line_edge(v_d, v_a, (0.0, 5.0, 0.0), (0.,-1.,0.), (0.0, 1.0), (0.,-1.), 5.0)

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
