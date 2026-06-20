"""Gp124 — ShapeFix_Edge.FixReversed2d HYPERBOLA.

Catalog claim: Pcurve is HYPERBOLA with reversed edge orientation
(EDGE_CURVE same_sense=.F.). FixReversed2d's reversal doesn't handle
asymptote-direction invariant — HYPERBOLA reversal silently handled.

STEP mechanism (literal):
  - PLANE Z=0 face, rectangle [0,4] x [0,2].
  - Defect edge: SURFACE_CURVE; 3D hyperbola arc (via TRIMMED_CURVE)
    traversed in reverse direction.
  - THE CATALOG MECHANISM: The EDGE_CURVE has same_sense=.F., meaning
    the edge is traversed opposite to the curve direction. The pcurve is
    a HYPERBOLA entity — an analytic conic that FixReversed2d must
    reverse. When reversing a HYPERBOLA, the asymptote-direction invariant
    (axis orientation) may not be preserved correctly; OCC's FixReversed2d
    handles this silently and heals to shape(1)/shape(1).
  - 3D curve: TRIMMED_CURVE wrapping a HYPERBOLA (semi-axis a=1, b=1,
    center at (2,0,0)) — a valid analytic geometry. The trim range
    [−0.5, 0.5] in hyperbola parameter (t: x=a*cosh(t), y=b*sinh(t))
    gives a small arc near the vertex.
  - EDGE_CURVE same_sense=.F. — edge traversed in reverse.
  - NO C-1 break (Archetype B: OCC silently heals; shape(1)/shape(1)).

Mechanism vs driver:
  - CATALOG MECHANISM: pcurve HYPERBOLA; EDGE_CURVE same_sense=.F.;
    FixReversed2d asymptote-direction invariant; OCC heals silently.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp124",
    defect=(
        "PLANE Z=0 rectangle [0,4]x[0,2]; defect edge: SURFACE_CURVE; "
        "3D TRIMMED_CURVE wrapping HYPERBOLA a=1 b=1 center=(2,0,0) "
        "trim t∈[-0.5,0.5] (vertex branch near (3,0,0)→(3,0,0) short arc); "
        "PCurve: HYPERBOLA entity a=1 b=1 in UV center=(2,0); "
        "EDGE_CURVE same_sense=.F. (reversed traversal); "
        "FixReversed2d reversal of HYPERBOLA skips asymptote-direction invariant; "
        "OCC heals silently; shape(1)/shape(1)"
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

# Hyperbola: HYPERBOLA(placement, semi_axis, semi_imag_axis)
# STEP parametric: x=a*cosh(t), y=b*sinh(t)
# At t=-0.5: x=cosh(0.5)≈1.128, y=-sinh(0.5)≈-0.521
# At t=+0.5: x=cosh(0.5)≈1.128, y=+sinh(0.5)≈+0.521
# With center at (2,0,0): end3D_start ≈ (3.128,-0.521,0), end3D_end ≈ (3.128,+0.521,0)
# Note: same_sense=.F. means the edge is traversed end→start in 3D
# Vertex start (t=+0.5) → end (t=-0.5) when reversed by .F.

A = 1.0; B = 1.0
T1 = -0.5; T2 = 0.5

# 3D hyperbola center at (2,0,0)
hyp3d_ctr = f.cartesian_point((2.0, 0.0, 0.0))
hyp3d_ax  = f.axis2_placement_3d(hyp3d_ctr, zdir, xdir)
hyp3d     = f._emit_raw(f"HYPERBOLA('hyp3d',#{hyp3d_ax.eid},{A},{B})")
# TRIMMED_CURVE: t from T1 to T2
hyp3d_trim = f._emit_raw(
    f"TRIMMED_CURVE('hyp_trim',#{hyp3d.eid},"
    f"(PARAMETER_VALUE({T1})),(PARAMETER_VALUE({T2})),.T.,.PARAMETER.)"
)

# 3D end-points for vertex assignment:
# t=T1: (2 + A*cosh(T1), 0 + B*sinh(T1), 0) = (2+cosh(0.5), -sinh(0.5), 0)
# t=T2: (2 + A*cosh(T2), 0 + B*sinh(T2), 0) = (2+cosh(0.5), +sinh(0.5), 0)
x3d = 2.0 + A * math.cosh(0.5)
y1_3d = B * math.sinh(T1)
y2_3d = B * math.sinh(T2)

p_start_3d = f.cartesian_point((x3d, y1_3d, 0.0))  # at t=T1
p_end_3d   = f.cartesian_point((x3d, y2_3d, 0.0))  # at t=T2
v_start = f.vertex_point(p_start_3d)
v_end   = f.vertex_point(p_end_3d)

# PCurve: HYPERBOLA in UV, same center (2,0), a=1, b=1
pc_ctr    = f.cartesian_point((2.0, 0.0))
pc_refdir = f.direction((1.0, 0.0))
pc_ax2    = f._emit_raw(f"AXIS2_PLACEMENT_2D('hyp_pc_ax2',#{pc_ctr.eid},#{pc_refdir.eid})")
pc_hyp    = f._emit_raw(f"HYPERBOLA('hyp_pcurve',#{pc_ax2.eid},{A},{B})")

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('hyp_pc_def',(#{pc_hyp.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('hyp_pc_ent',#{surf.eid},#{defrep.eid})")
sc_hyp = f._emit_raw(
    f"SURFACE_CURVE('hyp_sc',#{hyp3d_trim.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
# THE CATALOG MECHANISM: same_sense=.F. — edge is traversed reverse of curve direction.
# Curve runs from t=T1 (v_start) to t=T2 (v_end).
# With same_sense=.F., the edge is traversed v_end→v_start.
# FixReversed2d must reverse the HYPERBOLA pcurve; OCC heals silently.
e_hyp = f._emit_raw(
    f"EDGE_CURVE('hyp_reversed_edge',#{v_start.eid},#{v_end.eid},#{sc_hyp.eid},.F.)"
)

# Context: we build a closed face using the hyperbola edge plus 3 straight edges.
# The hyperbola arc end-points are at approximately:
#   v_start: (x3d, y1_3d, 0) ≈ (3.128, -0.521, 0)
#   v_end:   (x3d, y2_3d, 0) ≈ (3.128, +0.521, 0)
# The face will be a quadrilateral with:
#   bottom-left:  (1, -0.521, 0) = p_ll
#   bottom-right: (3.128, -0.521, 0) = v_start
#   top-right:    (3.128, +0.521, 0) = v_end
#   top-left:     (1, +0.521, 0) = p_ul
p_ll = f.cartesian_point((1.0, y1_3d, 0.0))
p_ul = f.cartesian_point((1.0, y2_3d, 0.0))
v_ll = f.vertex_point(p_ll)
v_ul = f.vertex_point(p_ul)

def mk_line_edge(vs, ve, p3, d3t, len3, p2t, d2t):
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t); v3 = f.vector(d3e, len3); l3 = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t); v2 = f.vector(d2e, len3); l2 = f.line(p2e, v2)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

width = x3d - 1.0
height = y2_3d - y1_3d

# bottom: v_ll → v_start  (left to right)
e_bot  = mk_line_edge(v_ll, v_start,
                      (1.0, y1_3d, 0.0), (1., 0., 0.), width,
                      (1.0, y1_3d),      (1., 0.))
# right: v_start → v_end  (bottom to top) — this is the reversed hyperbola arc
# Loop: e_bot(fwd) → e_hyp(fwd, but same_sense=.F. means it traverses end→start)
# Actually, oriented_edge(e_hyp, True) + same_sense=.F. → net: v_end→v_start
# We want a loop: v_ll→v_start→v_end→v_ul→v_ll
# With e_hyp having same_sense=.F. and vertices (v_start, v_end):
# oriented_edge(e_hyp, False) → traverses as v_end→v_start (wrong direction for our loop)
# oriented_edge(e_hyp, True) + same_sense=.F. → from v_start to v_end? No.
# EDGE_CURVE(v1=v_start, v2=v_end, curve, same_sense=.F.):
#   actual start = v_end, actual end = v_start (sense is flipped)
# So to go v_start→v_end in the loop, use oriented_edge(e_hyp, False).

# top: v_end → v_ul (right to left)
e_top  = mk_line_edge(v_end, v_ul,
                      (x3d, y2_3d, 0.0), (-1., 0., 0.), width,
                      (x3d, y2_3d),      (-1., 0.))
# left: v_ul → v_ll (top to bottom)
e_left = mk_line_edge(v_ul, v_ll,
                      (1.0, y2_3d, 0.0), (0., -1., 0.), height,
                      (1.0, y2_3d),      (0., -1.))

# Loop traversal: v_ll→v_start (e_bot fwd), v_start→v_end (e_hyp reversed sense .F.),
# v_end→v_ul (e_top fwd), v_ul→v_ll (e_left fwd).
# e_hyp has EDGE_CURVE(v_start, v_end, ..., .F.) so actual start=v_end, end=v_start.
# oriented_edge(e_hyp, False) → reverses the edge → actual start=v_start, end=v_end. ✓
loop = f.edge_loop([
    f.oriented_edge(e_bot,  True),
    f.oriented_edge(e_hyp,  False),
    f.oriented_edge(e_top,  True),
    f.oriented_edge(e_left, True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
