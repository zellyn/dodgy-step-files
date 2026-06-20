"""Gn124 — ShapeAnalysis_Curve.FillBndBox with-degenerate-segments.

Catalog claim: Composite curve containing a degenerate segment (zero-length).
FillBndBox samples all segments including the degenerate one, causing the
bounding box to contain a collapsed axis. Downstream code assumes all bbox axes
span non-zero ranges.

STEP mechanism (literal):
  - COMPOSITE_CURVE with 2 segments:
    Segment 1: normal LINE from (0,0,0) dir (1,0,0) length 2.0 → (0,0,0)→(2,0,0).
    Segment 2: degenerate LINE from (2,0,0) dir (1,0,0) length 0.0 → zero-length.
    FillBndBox iterates both segments, samples the degenerate one (which
    returns the same point for all parameter values), and combines into a bbox
    whose Y and Z extents are 0. Downstream non-zero-range assumption violated
    → shape analysis failure → shape_null=True.
    The COMPOSITE_CURVE IS the SURFACE_CURVE.curve_3d of the defect EDGE_CURVE
    (mechanism IS the defect edge 3D curve).
  - C-1 DRIVER: zero-length segment in composite → FillBndBox collapsed axis
    → downstream range-check violation → shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: COMPOSITE_CURVE two-segment; seg1 LINE (0,0,0)→(2,0,0)
    length=2.0; seg2 degenerate LINE (2,0,0) length=0.0 (zero-length);
    IS defect edge SURFACE_CURVE.curve_3d;
    FillBndBox collapsed Y/Z axis → non-zero-range assumption violated
    → shape_null=True.
  - C-1 DRIVER: degenerate zero-length segment → collapsed bbox axis
    → shape analysis failure → shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn124",
    defect=(
        "COMPOSITE_CURVE two-segment; "
        "seg1 LINE (0,0,0)→(2,0,0) length=2.0 (normal); "
        "seg2 degenerate LINE (2,0,0) length=0.0 (zero-length); "
        "IS defect edge SURFACE_CURVE.curve_3d; "
        "FillBndBox collapsed Y/Z axis → non-zero-range assumption violated "
        "→ shape_null=True"
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

# ── CATALOG MECHANISM: COMPOSITE_CURVE with zero-length segment ───────────────
# Segment 1: normal 3D line, length 2.0.
p_s1_orig = f.cartesian_point((0.0, 0.0, 0.0))
d_s1      = f.direction((1.0, 0.0, 0.0))
v_s1      = f.vector(d_s1, 2.0)
line_s1   = f.line(p_s1_orig, v_s1)

# Segment 2: degenerate 3D line — same origin as end of seg1, zero magnitude.
# VECTOR magnitude = 0.0 → zero-length segment.
p_s2_orig = f.cartesian_point((2.0, 0.0, 0.0))
d_s2      = f.direction((1.0, 0.0, 0.0))
v_s2      = f.vector(d_s2, 0.0)   # zero magnitude → degenerate
line_s2   = f.line(p_s2_orig, v_s2)

seg1 = f._emit_raw(
    f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,#{line_s1.eid})"
)
seg2 = f._emit_raw(
    f"COMPOSITE_CURVE_SEGMENT(.DISCONTINUOUS.,.T.,#{line_s2.eid})"
)

mech_3d = f._emit_raw(
    f"COMPOSITE_CURVE('gn124_degenerate_segment',(#{seg1.eid},#{seg2.eid}),.F.)"
)

# pcurve: 2D line companion — maps to a 2D line of length 2.0 (matching seg1)
pp_s   = f.cartesian_point((0.0, 0.0))
d2     = f.direction((1.0, 0.0))
v2     = f.vector(d2, 2.0)
line2d = f.line(pp_s, v2)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn124_pcdef',(#{line2d.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn124_pc_ent',#{plane.eid},#{defrep.eid})")
sc_defect = f._emit_raw(
    f"SURFACE_CURVE('gn124_sc',#{mech_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

p_start = f.cartesian_point((0.0, 0.0, 0.0))
p_end   = f.cartesian_point((2.0, 0.0, 0.0))
v_start = f.vertex_point(p_start)
v_end   = f.vertex_point(p_end)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn124_defect_edge',#{v_start.eid},#{v_end.eid},#{sc_defect.eid},.T.)"
)

# ── Outer bounding loop ───────────────────────────────────────────────────────
p_a = f.cartesian_point((-0.5, -0.5, 0.0))
p_b = f.cartesian_point(( 2.5, -0.5, 0.0))
p_c = f.cartesian_point(( 2.5,  0.5, 0.0))
p_d = f.cartesian_point((-0.5,  0.5, 0.0))
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

e_bot   = mk_line_edge(v_a, v_b, (-0.5,-0.5,0.0), (1.,0.,0.), (-0.5,-0.5), (1.,0.), 3.0)
e_right = mk_line_edge(v_b, v_c, ( 2.5,-0.5,0.0), (0.,1.,0.), ( 2.5,-0.5), (0.,1.), 1.0)
e_top   = mk_line_edge(v_c, v_d, ( 2.5, 0.5,0.0), (-1.,0.,0.),( 2.5, 0.5), (-1.,0.), 3.0)
e_left  = mk_line_edge(v_d, v_a, (-0.5, 0.5,0.0), (0.,-1.,0.),(-0.5, 0.5), (0.,-1.), 1.0)

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
