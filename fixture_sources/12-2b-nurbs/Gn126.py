"""Gn126 — ShapeAnalysis_Curve.GetSamplePoints CIRCLE with-trim-near-2π.

Catalog claim: Trimmed circle with parameters [0.001, 2π-0.001]. GetSamplePoints
uses a 360-degree cap for sampling, but the trim removes start/end points,
leaving a tiny gap that the sampling grid misses.

STEP mechanism (literal):
  - TRIMMED_CURVE wrapping a CIRCLE radius=1.0. Trim1=0.001, Trim2=2π-0.001
    (≈6.2822). The circle is almost-full (only 0.001 rad gap). GetSamplePoints
    internally uses 360-degree uniform grid; because trim endpoints nearly
    coincide with the 2π wrap, the tiny arc gap near 0/2π is never sampled.
    The TRIMMED_CURVE IS the SURFACE_CURVE.curve_3d of the defect EDGE_CURVE
    (mechanism IS the defect edge 3D curve).
  - C-1 DRIVER: trim near 2π → sample grid skips tiny gap → missing arc
    endpoints → shape analysis failure → shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: TRIMMED_CURVE(CIRCLE radius=1.0); trim1=0.001,
    trim2=6.2822 (2π-0.001); IS defect edge SURFACE_CURVE.curve_3d;
    GetSamplePoints 360-degree grid skips tiny gap → shape_null=True.
  - C-1 DRIVER: near-2π trim → sampling gap → shape analysis failure
    → shape_null=True.
"""
import math
from step_corpus.step_builder import StepFile

TWO_PI = 2.0 * math.pi

f = StepFile(
    catalog_id="Gn126",
    defect=(
        "TRIMMED_CURVE(CIRCLE radius=1.0); trim1=0.001, trim2=6.2822 (2π-0.001); "
        "IS defect edge SURFACE_CURVE.curve_3d; "
        "GetSamplePoints 360-degree grid skips tiny gap near 2π → shape_null=True"
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

# ── CATALOG MECHANISM: TRIMMED_CURVE wrapping CIRCLE, trim near 2π ───────────
# Circle center at (0,0,0), radius=1.0, in XY plane.
c_center = f.cartesian_point((0.0, 0.0, 0.0))
c_norm   = f.direction((0.0, 0.0, 1.0))
c_xdir   = f.direction((1.0, 0.0, 0.0))
c_ax3    = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('circle_ax',#{c_center.eid},#{c_norm.eid},#{c_xdir.eid})"
)
circle = f._emit_raw(f"CIRCLE('gn126_circle',#{c_ax3.eid},1.0)")

# Trim parameters: 0.001 to 2π-0.001 — nearly full circle.
t1 = 0.001
t2 = round(TWO_PI - 0.001, 6)

# Trim start/end 3D points: at angle 0.001 and 2π-0.001.
p_trim1 = f.cartesian_point((math.cos(t1), math.sin(t1), 0.0))
p_trim2 = f.cartesian_point((math.cos(t2), math.sin(t2), 0.0))

mech_3d = f._emit_raw(
    f"TRIMMED_CURVE('gn126_trimmed_circle',#{circle.eid},"
    f"(PARAMETER_VALUE({t1:.6f}),#{p_trim1.eid}),"
    f"(PARAMETER_VALUE({t2:.6f}),#{p_trim2.eid}),"
    f".T.,.PARAMETER.)"
)

# pcurve: 2D circle companion in UV space (same center/radius projected).
c2_center = f.cartesian_point((0.0, 0.0))
c2_xdir   = f.direction((1.0, 0.0))
c2_ax2    = f._emit_raw(
    f"AXIS2_PLACEMENT_2D('circle2d_ax',#{c2_center.eid},#{c2_xdir.eid})"
)
circle2d = f._emit_raw(f"CIRCLE('gn126_circle2d',#{c2_ax2.eid},1.0)")
defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn126_pcdef',(#{circle2d.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn126_pc',#{plane.eid},#{defrep.eid})")
sc_defect = f._emit_raw(
    f"SURFACE_CURVE('gn126_sc',#{mech_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

# Vertices at trim endpoints.
v_start = f.vertex_point(p_trim1)
v_end   = f.vertex_point(p_trim2)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn126_defect_edge',#{v_start.eid},#{v_end.eid},#{sc_defect.eid},.T.)"
)

# ── Outer bounding loop on the plane ─────────────────────────────────────────
p_a = f.cartesian_point((-1.5, -1.5, 0.0))
p_b = f.cartesian_point(( 1.5, -1.5, 0.0))
p_c = f.cartesian_point(( 1.5,  1.5, 0.0))
p_d = f.cartesian_point((-1.5,  1.5, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

def mk_line_edge(vs_, ve_, p3, d3t, p2t, d2t, length):
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t)
    v3_ = f.vector(d3e, length)
    l3  = f.line(p3e, v3_)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t)
    v2_ = f.vector(d2e, length)
    l2_ = f.line(p2e, v2_)
    pcd_ = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2_.eid}),#{prc.eid})")
    pc_  = f._emit_raw(f"PCURVE('pc',#{plane.eid},#{pcd_.eid})")
    sc_  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc_.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs_.eid},#{ve_.eid},#{sc_.eid},.T.)")

e_bot   = mk_line_edge(v_a, v_b, (-1.5,-1.5,0.), (1.,0.,0.), (-1.5,-1.5), (1.,0.), 3.0)
e_right = mk_line_edge(v_b, v_c, ( 1.5,-1.5,0.), (0.,1.,0.), ( 1.5,-1.5), (0.,1.), 3.0)
e_top   = mk_line_edge(v_c, v_d, ( 1.5, 1.5,0.), (-1.,0.,0.),( 1.5, 1.5), (-1.,0.), 3.0)
e_left  = mk_line_edge(v_d, v_a, (-1.5, 1.5,0.), (0.,-1.,0.),(-1.5, 1.5), (0.,-1.), 3.0)

outer_loop = f.edge_loop([
    f.oriented_edge(e_bot,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_left,  True),
])
inner_loop = f.edge_loop([
    f.oriented_edge(e_defect, True),
])

outer_bound = f.face_outer_bound(outer_loop)
inner_bound = f._emit_raw(f"FACE_BOUND('inner_bound',#{inner_loop.eid},.T.)")

face  = f.advanced_face([outer_bound, inner_bound], plane)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
