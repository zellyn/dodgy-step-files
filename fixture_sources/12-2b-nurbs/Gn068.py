"""Gn068 — ShapeAnalysis_Curve.FillBndBox elliptic-arc midpoint sampling.

Catalog claim: Trimmed ELLIPSE arc with high aspect ratio (semi-major=3,
semi-minor=0.3). FillBndBox samples the midpoint at parameter π/2 (correct
for unit circle), but the actual Y-maximum of a high-eccentricity ellipse arc
occurs at a different parameter — the bounding box is therefore wrong.

OCC behavior: silently accepts, empty result. Expected: occt=empty/empty.

STEP mechanism (literal):
  - TRIMMED_CURVE wrapping an ELLIPSE with semi_axis=3.0, semi_axis2=0.3.
    Trim parameters: sense_agreement=TRUE, trim from 0.0 to π (parameter form).
    High eccentricity: aspect ratio 10:1. FillBndBox evaluates midpoint at
    t=π/2 but peak Y occurs at t=arctan(semi_minor/semi_major)≠π/2 for
    high-eccentricity arcs in the presence of axis rotation.
    IS the SURFACE_CURVE.curve_3d of the defect EDGE_CURVE.
  - C-1 DRIVER: the TRIMMED_CURVE exposes a near-degenerate geometry at trim
    boundary that drives shape_null=True via edge topology failure.

Mechanism vs driver:
  - CATALOG MECHANISM: TRIMMED_CURVE on ELLIPSE semi_axis=3.0 semi_axis2=0.3
    trim [0, π]; IS defect edge SURFACE_CURVE.curve_3d; FillBndBox samples
    midpoint at π/2, misses true Y-max of high-eccentricity arc.
  - C-1 DRIVER: near-degenerate trim boundary geometry drives shape_null=True.
"""
from step_corpus.step_builder import StepFile
import math

f = StepFile(
    catalog_id="Gn068",
    defect=(
        "TRIMMED_CURVE on ELLIPSE semi_axis=3.0 semi_axis2=0.3 trim [0, π]; "
        "IS defect edge SURFACE_CURVE.curve_3d; "
        "FillBndBox samples midpoint at π/2, misses true Y-max of 10:1 eccentricity arc; "
        "near-degenerate trim boundary drives shape_null=True"
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

# ── CATALOG MECHANISM: high-aspect ELLIPSE wrapped in TRIMMED_CURVE ───────────
# Ellipse center at (1.5, 0, 0), semi_axis=3.0, semi_axis2=0.3.
# AXIS2_PLACEMENT_3D: center (1.5,0,0), ref_dir (1,0,0), normal (0,0,1).
e_orig = f.cartesian_point((1.5, 0.0, 0.0))
e_norm = f.direction((0.0, 0.0, 1.0))
e_xdir = f.direction((1.0, 0.0, 0.0))
e_ax3  = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('ell_ax3',#{e_orig.eid},#{e_norm.eid},#{e_xdir.eid})"
)
ellipse = f._emit_raw(
    f"ELLIPSE('gn068_ellipse',#{e_ax3.eid},3.0,0.3)"
)

# TRIMMED_CURVE: parameter trim 0.0 to π. sense_agreement=TRUE.
# Trim pts: start = (1.5+3, 0, 0) = (4.5,0,0), end = (1.5-3, 0, 0) = (-1.5,0,0)
t_start_pt = f.cartesian_point((4.5,  0.0, 0.0))
t_end_pt   = f.cartesian_point((-1.5, 0.0, 0.0))
pi_val = round(math.pi, 10)

trimmed = f._emit_raw(
    f"TRIMMED_CURVE('gn068_trimmed_ellipse',#{ellipse.eid},"
    f"(#{t_start_pt.eid},PARAMETER_VALUE(0.0)),"
    f"(#{t_end_pt.eid},PARAMETER_VALUE({pi_val})),"
    f".T.,.PARAMETER.)"
)

# Pcurve: linear in UV along bottom edge
pp0 = f.cartesian_point((0.0, 0.0))
d2  = f.direction((1.0, 0.0))
v2  = f.vector(d2, 3.0)
l2  = f.line(pp0, v2)
pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('gn068_pcdef',(#{l2.eid}),#{prc.eid})")
pcurve = f._emit_raw(f"PCURVE('gn068_pc_ent',#{plane.eid},#{pcd.eid})")

sc_bot = f._emit_raw(
    f"SURFACE_CURVE('gn068_sc',#{trimmed.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

p_a = f.cartesian_point(( 0.0, 0.0, 0.0))
p_b = f.cartesian_point(( 3.0, 0.0, 0.0))
p_c = f.cartesian_point(( 3.0, 0.3, 0.0))
p_d = f.cartesian_point(( 0.0, 0.3, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn068_defect_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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

e_right = mk_line_edge(v_b, v_c, (3.0, 0.0, 0.0), (0.,1.,0.), (1.0, 0.0), (0.,1.), 0.3)
e_top   = mk_line_edge(v_c, v_d, (3.0, 0.3, 0.0), (-1.,0.,0.), (1.0, 1.0), (-1.,0.), 3.0)
e_left  = mk_line_edge(v_d, v_a, (0.0, 0.3, 0.0), (0.,-1.,0.), (0.0, 1.0), (0.,-1.), 0.3)

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
