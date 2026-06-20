"""Gn123 — ShapeAnalysis_Curve.IsClosed COMPOSITE_CURVE with-direction-reversal.

Catalog claim: Composite curve with 2 line segments: first forward
(0,0,0)→(2,0,0), second reversed (2,0,0)→(0,0,0). IsClosed checks endpoint
coincidence but ignores direction reversal, missing the topological mismatch.

STEP mechanism (literal):
  - Two LINE curves wired into a COMPOSITE_CURVE.
    Segment 1: forward sense (.T.), 3D line from (0,0,0) direction (1,0,0)
    length 2 → traversal (0,0,0)→(2,0,0).
    Segment 2: reversed sense (.F.), same 3D line from (0,0,0) direction
    (1,0,0) length 2 → reversed traversal (2,0,0)→(0,0,0).
    The composite curve is "closed" by endpoint coincidence but the
    direction reversal on segment 2 is a topological contradiction:
    a forward-traversal of the reversed segment would go (0,0,0)→(2,0,0)
    again (backtracking over segment 1). IsClosed confirms the endpoints
    match without flagging this contradiction → shape_null=True.
    The COMPOSITE_CURVE IS the SURFACE_CURVE.curve_3d of the defect EDGE_CURVE
    (mechanism IS the defect edge 3D curve).
  - C-1 DRIVER: direction reversal on segment 2 → topological contradiction
    → IsClosed blind to reversal → shape analysis failure → shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: COMPOSITE_CURVE two-segment; seg1 LINE (0,0,0)→(2,0,0)
    sense=.T.; seg2 same LINE sense=.F. (reversed: traversal (2,0,0)→(0,0,0));
    endpoints coincide (0,0,0)==(0,0,0) so IsClosed returns true;
    direction reversal is topological mismatch;
    IS defect edge SURFACE_CURVE.curve_3d; shape_null=True.
  - C-1 DRIVER: composite segment direction contradiction → IsClosed blind
    to reversal → shape analysis failure → shape_null=True.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn123",
    defect=(
        "COMPOSITE_CURVE two-segment; "
        "seg1 LINE (0,0,0)→(2,0,0) sense=.T.; "
        "seg2 same LINE sense=.F. (reversed traversal (2,0,0)→(0,0,0)); "
        "endpoints coincide → IsClosed true but direction-reversal mismatch; "
        "IS defect edge SURFACE_CURVE.curve_3d; "
        "IsClosed ignores reversal contradiction → shape_null=True"
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

# ── CATALOG MECHANISM: COMPOSITE_CURVE with direction-reversal ─────────────────
# Segment 1: LINE from (0,0,0) dir (1,0,0) length 2 → forward (0,0,0)→(2,0,0).
# Segment 2: same LINE, reversed sense → traversal (2,0,0)→(0,0,0).
# Composite curve then "starts" at (0,0,0) and "ends" at (0,0,0) by coincidence.
# IsClosed sees matching endpoints but ignores the reversal contradiction.

p_line_orig = f.cartesian_point((0.0, 0.0, 0.0))
d_line      = f.direction((1.0, 0.0, 0.0))
v_line      = f.vector(d_line, 2.0)
line_3d     = f.line(p_line_orig, v_line)

# COMPOSITE_CURVE_SEGMENT: sense flag .T. for forward, .F. for reversed.
# COMPOSITE_CURVE_SEGMENT(transition, same_sense, parent_curve)
seg1 = f._emit_raw(
    f"COMPOSITE_CURVE_SEGMENT(.DISCONTINUOUS.,.T.,#{line_3d.eid})"
)
seg2 = f._emit_raw(
    f"COMPOSITE_CURVE_SEGMENT(.DISCONTINUOUS.,.F.,#{line_3d.eid})"
)

mech_3d = f._emit_raw(
    f"COMPOSITE_CURVE('gn123_direction_reversal',(#{seg1.eid},#{seg2.eid}),.F.)"
)

# pcurve: 2D line companion — composite maps to a 2D line segment and back
pp_s   = f.cartesian_point((0.0, 0.0))
d2     = f.direction((1.0, 0.0))
v2     = f.vector(d2, 2.0)
line2d = f.line(pp_s, v2)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('gn123_pcdef',(#{line2d.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('gn123_pc_ent',#{plane.eid},#{defrep.eid})")
sc_defect = f._emit_raw(
    f"SURFACE_CURVE('gn123_sc',#{mech_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

# The composite curve starts and ends at (0,0,0); use a single vertex for both.
p_v = f.cartesian_point((0.0, 0.0, 0.0))
v_shared = f.vertex_point(p_v)

e_defect = f._emit_raw(
    f"EDGE_CURVE('gn123_defect_edge',#{v_shared.eid},#{v_shared.eid},"
    f"#{sc_defect.eid},.T.)"
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
