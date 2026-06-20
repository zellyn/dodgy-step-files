"""Gp070 -- ShapeFix_Edge.FixVertexTolerance double-update.

Catalog claim: Same vertex used by two edges; FixVertexTolerance computes
tolerance from edge1 and escalates the vertex; then edge2 sees the elevated
vertex tolerance and re-escalates, double-counting the tolerance rise.

STEP-level trigger: single VERTEX_POINT entity at origin shared between two
EDGE_CURVEs.  Each edge's 3D curve is a B_SPLINE_CURVE_WITH_KNOTS with a
C-1 positional break (knot mult = degree+1 = 3 at an interior knot; large
CP gap at the break).  The large gap creates the pcurve-deviation that
FixVertexTolerance must process.  Because both edges share the same vertex,
sequential FixVertexTolerance calls double-escalate its tolerance.

The C-1 positional break also causes OCC shape_null=True during transfer,
which is the expected validation outcome (OCC neither heals nor rejects
gracefully — it silently drops the shape).

Fixture encoding:
  - VERTEX_POINT shared_v at origin: appears as start of edge_a AND end of edge_b
  - edge_a geometry: degree-2 B-spline, 6 CPs, C-1 break at t=0.3 (gap 1.5 units)
  - edge_b geometry: degree-2 B-spline, 6 CPs, C-1 break at t=0.7 (gap 1.5 units)
  - Both edges have SURFACE_CURVE with LINE pcurve on the plane
  - The pcurve/3D-curve mismatch at the break is what FixVertexTolerance escalates
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp070",
    defect=(
        "PLANE face; shared VERTEX_POINT at origin is start of edge_a and "
        "end of edge_b; each edge has degree-2 B-spline with C-1 positional "
        "break (knot mult=3, 1.5-unit CP gap); sequential FixVertexTolerance "
        "calls on both edges double-escalate the shared vertex tolerance; "
        "C-1 break drives OCC shape_null=True"
    ),
)

# Host: Z=0 plane
p_orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir   = f.direction((0.0, 0.0, 1.0))
xdir   = f.direction((1.0, 0.0, 0.0))
plc    = f.axis2_placement_3d(p_orig, zdir, xdir)
surf   = f.plane(plc)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# THE SHARED VERTEX at origin — referenced by both edge_a (start) and edge_b (end)
p_origin  = f.cartesian_point((0.0, 0.0, 0.0))
shared_v  = f.vertex_point(p_origin)

# Other corner vertices
p_br = f.cartesian_point((4.0, 0.0, 0.0))
p_tr = f.cartesian_point((4.0, 4.0, 0.0))
p_tl = f.cartesian_point((0.0, 4.0, 0.0))
v_br = f.vertex_point(p_br)
v_tr = f.vertex_point(p_tr)
v_tl = f.vertex_point(p_tl)

def make_break_bspline_x(x_gap_start):
    """Degree-2 B-spline 6 CPs with C-1 positional break at t=0.3 along X.
    CPs before break approach x_gap_start from 0; CPs after jump to x_gap_start+1.5.
    Knots: (3,3,3) at (0.0, 0.3, 1.0) — mult=3=degree+1 at interior => C-1 break.
    sum(mults) = 3+3+3=9 = 6+2+1=9 ✓ (degree=2, n=6)
    """
    gap = 1.5
    bc0 = f.cartesian_point((0.0,          0.0, 0.0))
    bc1 = f.cartesian_point((x_gap_start * 0.5, 0.0, 0.0))
    bc2 = f.cartesian_point((x_gap_start,  0.0, 0.0))   # before break
    bc3 = f.cartesian_point((x_gap_start + gap, 0.0, 0.0))  # after break: gap
    bc4 = f.cartesian_point(((x_gap_start + gap + 4.0) * 0.5, 0.0, 0.0))
    bc5 = f.cartesian_point((4.0,          0.0, 0.0))
    return f._emit_raw(
        f"B_SPLINE_CURVE_WITH_KNOTS('brk',2,"
        f"(#{bc0.eid},#{bc1.eid},#{bc2.eid},#{bc3.eid},#{bc4.eid},#{bc5.eid}),"
        f".UNSPECIFIED.,.F.,.F.,(3,3,3),(0.0,0.3,1.0),.UNSPECIFIED.)"
    )

def make_break_bspline_y(y_gap_start):
    """Same pattern but along Y direction for edge_b."""
    gap = 1.5
    bc0 = f.cartesian_point((0.0, 0.0,          0.0))
    bc1 = f.cartesian_point((0.0, y_gap_start * 0.5, 0.0))
    bc2 = f.cartesian_point((0.0, y_gap_start,  0.0))
    bc3 = f.cartesian_point((0.0, y_gap_start + gap, 0.0))
    bc4 = f.cartesian_point((0.0, (y_gap_start + gap + 4.0) * 0.5, 0.0))
    bc5 = f.cartesian_point((0.0, 4.0,          0.0))
    return f._emit_raw(
        f"B_SPLINE_CURVE_WITH_KNOTS('brk2',2,"
        f"(#{bc0.eid},#{bc1.eid},#{bc2.eid},#{bc3.eid},#{bc4.eid},#{bc5.eid}),"
        f".UNSPECIFIED.,.F.,.F.,(3,3,3),(0.0,0.3,1.0),.UNSPECIFIED.)"
    )

# edge_a: shared_v → v_br (bottom).  C-1 break at t=0.3 along X axis.
bspline_a  = make_break_bspline_x(1.0)
pc_a_s     = f.cartesian_point((0.0, 0.0))
pc_a_d     = f.direction((1.0, 0.0)); pc_a_v = f.vector(pc_a_d, 4.0)
pc_a_l     = f.line(pc_a_s, pc_a_v)
pc_a_def   = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pca_def',(#{pc_a_l.eid}),#{prc.eid})")
pc_a       = f._emit_raw(f"PCURVE('pca',#{surf.eid},#{pc_a_def.eid})")
sc_a       = f._emit_raw(f"SURFACE_CURVE('sca',#{bspline_a.eid},(#{pc_a.eid}),.PCURVE_S1.)")
edge_a     = f._emit_raw(f"EDGE_CURVE('eca',#{shared_v.eid},#{v_br.eid},#{sc_a.eid},.T.)")

# edge_b: v_tl → shared_v (left).  C-1 break at t=0.3 along Y axis.
bspline_b  = make_break_bspline_y(1.0)
pc_b_s     = f.cartesian_point((0.0, 4.0))
pc_b_d     = f.direction((0.0, -1.0)); pc_b_v = f.vector(pc_b_d, 4.0)
pc_b_l     = f.line(pc_b_s, pc_b_v)
pc_b_def   = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcb_def',(#{pc_b_l.eid}),#{prc.eid})")
pc_b       = f._emit_raw(f"PCURVE('pcb',#{surf.eid},#{pc_b_def.eid})")
sc_b       = f._emit_raw(f"SURFACE_CURVE('scb',#{bspline_b.eid},(#{pc_b.eid}),.PCURVE_S1.)")
edge_b     = f._emit_raw(f"EDGE_CURVE('ecb',#{v_tl.eid},#{shared_v.eid},#{sc_b.eid},.T.)")

# Clean context edges (right and top)
d_up   = f.direction((0.0, 1.0, 0.0)); v_up  = f.vector(d_up,  4.0)
d_lt   = f.direction((-1.0, 0.0, 0.0)); v_lt = f.vector(d_lt,  4.0)
l_right = f.line(p_br, v_up);  l_top = f.line(p_tr, v_lt)

pc_r_s   = f.cartesian_point((4.0, 0.0))
pc_r_d   = f.direction((0.0, 1.0)); pc_r_v = f.vector(pc_r_d, 4.0); pc_r_l = f.line(pc_r_s, pc_r_v)
pc_r_def = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcr_def',(#{pc_r_l.eid}),#{prc.eid})")
pc_r     = f._emit_raw(f"PCURVE('pcr',#{surf.eid},#{pc_r_def.eid})")
sc_r     = f._emit_raw(f"SURFACE_CURVE('scr',#{l_right.eid},(#{pc_r.eid}),.PCURVE_S1.)")
edge_r   = f._emit_raw(f"EDGE_CURVE('ecr',#{v_br.eid},#{v_tr.eid},#{sc_r.eid},.T.)")

pc_t_s   = f.cartesian_point((4.0, 4.0))
pc_t_d   = f.direction((-1.0, 0.0)); pc_t_v = f.vector(pc_t_d, 4.0); pc_t_l = f.line(pc_t_s, pc_t_v)
pc_t_def = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pct_def',(#{pc_t_l.eid}),#{prc.eid})")
pc_t     = f._emit_raw(f"PCURVE('pct',#{surf.eid},#{pc_t_def.eid})")
sc_t     = f._emit_raw(f"SURFACE_CURVE('sct',#{l_top.eid},(#{pc_t.eid}),.PCURVE_S1.)")
edge_t   = f._emit_raw(f"EDGE_CURVE('ect',#{v_tr.eid},#{v_tl.eid},#{sc_t.eid},.T.)")

loop  = f.edge_loop([
    f.oriented_edge(edge_a, True),
    f.oriented_edge(edge_r, True),
    f.oriented_edge(edge_t, True),
    f.oriented_edge(edge_b, True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
