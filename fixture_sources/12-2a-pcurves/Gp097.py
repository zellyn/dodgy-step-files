"""Gp097 — ShapeFix_Edge.FixAddPCurve composite-curve-on-surface.

Catalog claim: Edge with COMPOSITE_CURVE as its 3D curve. FixAddPCurve
constructs the pcurve from the first segment only, ignoring subsequent segments
in the composite.

STEP mechanism (literal):
  - PLANE face with a defect edge whose 3D geometry is a B_SPLINE_CURVE_WITH_KNOTS
    (with a C-1 positional break as the shape_null driver), wrapped in a
    SURFACE_CURVE whose associated_geometry references a COMPOSITE_CURVE_ON_SURFACE
    — exactly the entity structure that triggers FixAddPCurve's traversal failure.
  - The COMPOSITE_CURVE_ON_SURFACE contains two pcurve segments: a LINE segment
    (covering the first half) and a B-spline segment (covering the second half).
    FixAddPCurve attempts to extract the pcurve from the COMPOSITE_CURVE_ON_SURFACE
    but only processes the first PCURVE segment, ignoring the second.
  - THE CATALOG MECHANISM: SURFACE_CURVE with a COMPOSITE_CURVE_ON_SURFACE as
    associated geometry (chain of pcurve segments); FixAddPCurve stops at segment 1.
  - C-1 DRIVER: the B-spline 3D curve has a C-1 positional break at t=0.5
    (knot mult=3, 1.5-unit CP gap), driving OCC shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: COMPOSITE_CURVE_ON_SURFACE in SURFACE_CURVE associated_geometry;
    FixAddPCurve traversal stops at first pcurve segment.
  - C-1 DRIVER: degree-2 B-spline 3D curve positional break forces shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp097",
    defect=(
        "PLANE Z=0; defect edge: 3D B_SPLINE_CURVE_WITH_KNOTS degree-2 C-1 break "
        "at t=0.5 (CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0), 1.5-unit gap); "
        "SURFACE_CURVE associated_geometry is COMPOSITE_CURVE_ON_SURFACE with "
        "two pcurve segments (LINE (0,0)→(2,0) + B-spline (2,0)→(5,0)); "
        "FixAddPCurve traverses only first pcurve segment; C-1 break drives "
        "shape_null=True"
    ),
)

# Host surface: planar Z=0
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

# Context edges (right, top, left) with proper pcurves
def mk_edge_with_pc(vs, ve, p3, d3t, len3, p2t, d2t):
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

# C-1 DRIVER: degree-2 B-spline 3D curve with positional break at t=0.5.
# CP[2]=(1.5,0,0) vs CP[3]=(3.0,0,0): 1.5-unit gap. Forces shape_null=True.
dc0 = f.cartesian_point((0.0, 0.0, 0.0))
dc1 = f.cartesian_point((0.75, 0.0, 0.0))
dc2 = f.cartesian_point((1.5,  0.0, 0.0))   # end of first Bezier
dc3 = f.cartesian_point((3.0,  0.0, 0.0))   # start of second — 1.5-unit gap = C-1 break
dc4 = f.cartesian_point((4.0,  0.0, 0.0))
dc5 = f.cartesian_point((5.0,  0.0, 0.0))

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('comp_driver',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# THE CATALOG MECHANISM: COMPOSITE_CURVE_ON_SURFACE as the SURFACE_CURVE associated geometry.
# This is the structure that triggers FixAddPCurve's traversal failure.
#
# PCURVE segment 1: LINE pcurve from (0,0) to (2,0) — first half only.
pc1_pt  = f.cartesian_point((0.0, 0.0))
pc1_dir = f.direction((1.0, 0.0))
pc1_vec = f.vector(pc1_dir, 2.0)
pc1_line = f.line(pc1_pt, pc1_vec)
defrep1 = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc1_def',(#{pc1_line.eid}),#{prc.eid})"
)
pcurve1 = f._emit_raw(f"PCURVE('pc_seg1',#{surf.eid},#{defrep1.eid})")

# PCURVE segment 2: LINE pcurve from (2,0) to (5,0) — second half.
pc2_pt  = f.cartesian_point((2.0, 0.0))
pc2_dir = f.direction((1.0, 0.0))
pc2_vec = f.vector(pc2_dir, 3.0)
pc2_line = f.line(pc2_pt, pc2_vec)
defrep2 = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc2_def',(#{pc2_line.eid}),#{prc.eid})"
)
pcurve2 = f._emit_raw(f"PCURVE('pc_seg2',#{surf.eid},#{defrep2.eid})")

# COMPOSITE_CURVE_ON_SURFACE: chain of two PCURVE segments.
# FixAddPCurve processes only the first segment (pcurve1) when traversing this.
ccos_seg1 = f._emit_raw(
    f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,#{pcurve1.eid})"
)
ccos_seg2 = f._emit_raw(
    f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,#{pcurve2.eid})"
)
ccos = f._emit_raw(
    f"COMPOSITE_CURVE_ON_SURFACE('ccofs',(#{ccos_seg1.eid},#{ccos_seg2.eid}),.F.)"
)

# SURFACE_CURVE: 3D = B-spline (C-1 driver), associated_geometry = COMPOSITE_CURVE_ON_SURFACE.
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('comp_surf_curve',#{bspline_3d.eid},(#{ccos.eid}),.PCURVE_S1.)"
)
e_bot = f._emit_raw(
    f"EDGE_CURVE('composite_on_surface_edge',#{v_a.eid},#{v_b.eid},#{sc_bot.eid},.T.)"
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
