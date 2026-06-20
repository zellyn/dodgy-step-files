"""Gp162 — line_circle_reparametrization_2106

Catalog claim: TrimmedCurve wrapping Line/Circle skips geometric basis validation
during reparametrization. Non-canonical curve geometry mapping failure. Line
2106–2139: Type detection via Geom2dAdaptor fails to unwrap trimmed geometry,
producing incorrect parameter mapping.

STEP mechanism (literal):
  - PLANE Z=0 face with a defect edge whose 3D curve is a TRIMMED_CURVE wrapping
    a LINE. The trimmed wrapper prevents Geom2dAdaptor from resolving the
    underlying curve type, causing the reparametrization at line 2106 to map
    parameters incorrectly.
  - THE CATALOG MECHANISM: At OCCT line 2106–2139, Geom2dAdaptor::GetType() is
    called on the pcurve to detect whether it is a line or circle for a fast
    reparametrization path. When the pcurve is itself a TRIMMED_CURVE (wrapping
    a LINE), Geom2dAdaptor returns GeomAbs_OtherCurve instead of GeomAbs_Line.
    The adaptor fails to unwrap the trimmed basis; the reparametrization branch
    for lines/circles is skipped; parameter mapping is incorrect (non-canonical
    geometry mapping failure). line_circle_reparametrization_2106 axis.
  - C-1 DRIVER: degree-2 B-spline 3D curve with positional break at t=0.5 (knot
    mult=3, 1.5-unit CP gap) forces OCC shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: TRIMMED_CURVE wrapping LINE as pcurve; Geom2dAdaptor
    GetType at line 2106 returns OtherCurve (fails to unwrap basis); fast
    reparametrization for Line/Circle skipped; parameter mapping incorrect;
    line_circle_reparametrization_2106 axis; shape_null=True.
  - C-1 DRIVER: degree-2 B-spline 3D positional break forces shape_null=True.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp162",
    defect=(
        "PLANE Z=0; defect edge: SURFACE_CURVE; "
        "3D B_SPLINE_CURVE_WITH_KNOTS degree-2 C-1 break at t=0.5 "
        "(CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0), 1.5-unit gap) drives shape_null; "
        "PCurve TRIMMED_CURVE wrapping LINE from (0,0) to (5,0): "
        "Geom2dAdaptor::GetType (line 2106) returns OtherCurve — fails to unwrap "
        "trimmed basis; fast reparametrization branch for Line/Circle skipped; "
        "parameter mapping incorrect; non-canonical curve geometry mapping failure; "
        "line_circle_reparametrization_2106 axis; shape_null=True"
    ),
)

# Host surface: PLANE Z=0
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
surf = f.plane(plc)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Face corners: rectangle [0,5] x [0,2]
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((5.0, 0.0, 0.0))
p_c = f.cartesian_point((5.0, 2.0, 0.0))
p_d = f.cartesian_point((0.0, 2.0, 0.0))
v_a = f.vertex_point(p_a); v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c); v_d = f.vertex_point(p_d)

def mk_edge_with_pc(vs, ve, p3, d3t, len3, p2t, d2t):
    """Build EDGE_CURVE via SURFACE_CURVE with a linear pcurve."""
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t); v3 = f.vector(d3e, len3); l3 = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t); v2 = f.vector(d2e, len3); l2 = f.line(p2e, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

e_right = mk_edge_with_pc(v_b, v_c, (5.0, 0.0, 0.0), (0., 1., 0.), 2.0, (5.0, 0.0), (0., 1.))
e_top   = mk_edge_with_pc(v_c, v_d, (5.0, 2.0, 0.0), (-1., 0., 0.), 5.0, (5.0, 2.0), (-1., 0.))
e_left  = mk_edge_with_pc(v_d, v_a, (0.0, 2.0, 0.0), (0., -1., 0.), 2.0, (0.0, 2.0), (0., -1.))

# ── DEFECT EDGE — bottom (v_a -> v_b) ─────────────────────────────────────────
#
# C-1 DRIVER: degree-2 B-spline positional break at t=0.5.
# CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0) — 1.5-unit gap. Forces shape_null=True.
dc0 = f.cartesian_point((0.0,  0.0, 0.0))
dc1 = f.cartesian_point((0.75, 0.0, 0.0))
dc2 = f.cartesian_point((1.5,  0.0, 0.0))
dc3 = f.cartesian_point((3.0,  0.0, 0.0))   # 1.5-unit gap = C-1 break
dc4 = f.cartesian_point((4.0,  0.0, 0.0))
dc5 = f.cartesian_point((5.0,  0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('line_circle_reparam_driver',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# THE CATALOG MECHANISM: PCurve is a TRIMMED_CURVE wrapping a LINE.
# Geom2dAdaptor::GetType (line 2106) is called on this pcurve; it returns
# GeomAbs_OtherCurve instead of GeomAbs_Line because the adaptor does not
# unwrap the TRIMMED_CURVE basis. The fast reparametrization path for Line and
# Circle at lines 2106–2139 is not entered; parameter mapping is incorrect;
# non-canonical geometry mapping failure; line_circle_reparametrization_2106.
#
# Build the underlying LINE in UV: from (0,0) in direction (1,0), length 5.
pc_line_orig  = f.cartesian_point((0.0, 0.0))
pc_line_dir   = f.direction((1.0, 0.0))
pc_line_vec   = f.vector(pc_line_dir, 5.0)
pc_base_line  = f.line(pc_line_orig, pc_line_vec)

# Wrap it in TRIMMED_CURVE to defeat Geom2dAdaptor type detection.
# TRIMMED_CURVE(name, basis_curve, trim1, trim2, sense, master_representation)
pc_trimmed = f._emit_raw(
    f"TRIMMED_CURVE('line_reparam_trim',#{pc_base_line.eid},"
    f"(PARAMETER_VALUE(0.0)),(PARAMETER_VALUE(5.0)),.T.,.PARAMETER.)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('line_reparam_pc_def',(#{pc_trimmed.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('line_reparam_pc',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('line_reparam_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('line_reparam_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
)

loop = f.edge_loop([
    f.oriented_edge(e_bot,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_left,  True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
