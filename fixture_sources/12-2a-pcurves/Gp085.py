"""Gp085 — GetEndTangent2d ellipse derivative asymmetry.

Catalog claim: P-curve is an ELLIPSE entity; GetEndTangent2d uses
finite-difference fallback whose result depends on parameter direction
(increasing vs decreasing); assumes parameter increases only. When
EDGE_CURVE same_sense=.F. (reversed), the method evaluates the derivative
in the wrong direction and returns an incorrect end tangent.

Fixture: PLANE face. The defect edge uses:
  - 3D curve: a CIRCLE (clean, loadable, matching the 3D projection of the ellipse).
  - 2D pcurve: an ELLIPSE entity in UV space (semi-axes a=2, b=1 in UV).
  - EDGE_CURVE same_sense=.F. — reversal triggers the asymmetric finite-difference.

The 3D CIRCLE is centred at (2, 0.5, 0) with radius 1, lying in the Z=0 plane.
Its 3D extent in X is [1, 3], in Y is [-0.5, 1.5]. The face is a parallelogram
whose bottom edge is this reversed arc.

OCC ignores the pcurve tangent anomaly and heals cleanly: shape(1).
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gp085",
             defect="ELLIPSE pcurve with EDGE_CURVE same_sense=.F.; "
                    "GetEndTangent2d finite-difference uses increasing-param "
                    "assumption; reversal flips derivative sign → wrong tangent")

# Host surface: plane Z=0.
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
surf = f.plane(plc)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# 3D CIRCLE for the defect edge: centre (2, 0.5, 0), radius 1, in Z=0 plane.
# Parametrically: P(t) = (2 + cos(t), 0.5 + sin(t), 0), t ∈ [0, π].
# t=0 → (3, 0.5, 0); t=π → (1, 0.5, 0).
# same_sense=.F. means the edge traverses t decreasing: start=(1,0.5,0), end=(3,0.5,0).
circ_ctr  = f.cartesian_point((2.0, 0.5, 0.0))
circ_norm = f.direction((0.0, 0.0, 1.0))
circ_xref = f.direction((1.0, 0.0, 0.0))
circ_axis = f.axis2_placement_3d(circ_ctr, circ_norm, circ_xref)
circle3d  = f.circle(circ_axis, 1.0)

# Vertex positions: because same_sense=.F., the EDGE_CURVE start/end vertices
# are the geometric t=0 and t=π endpoints:
#   t=0 (geometric start):  (3.0, 0.5, 0)
#   t=π (geometric end):    (1.0, 0.5, 0)
# The edge traversal goes from t=π back to t=0 (reversed), so topological:
#   v_start (topo) = geometric end = (1.0, 0.5, 0)
#   v_end   (topo) = geometric start = (3.0, 0.5, 0)
p_geo_start = f.cartesian_point((3.0, 0.5, 0.0))  # t=0
p_geo_end   = f.cartesian_point((1.0, 0.5, 0.0))  # t=π
v_geo_start = f.vertex_point(p_geo_start)          # EDGE_CURVE start arg
v_geo_end   = f.vertex_point(p_geo_end)            # EDGE_CURVE end arg

# 2D ELLIPSE pcurve in UV space:
# Centre (2, 0.5) in UV, semi-axis ref along X with a=2, b=1.
# On a plane Z=0, UV = (X, Y), so the ellipse in UV projects to an ellipse
# in 3D Z=0 with X semi-axis=2 (wider than the 3D circle radius=1) and Y semi-axis=1.
# GetEndTangent2d finite-differences the ELLIPSE at t=0 or t=π depending on
# direction; the derivative at t=0 for ELLIPSE is (-a*sin(0), b*cos(0)) = (0, b)
# and in the reversed direction it should be (0, -b) — the bug is using (0, b) always.
uv_ctr    = f.cartesian_point((2.0, 0.5))
uv_zdir2d = f.direction((0.0, 0.0, 1.0))   # normal to the 2D "plane" (unused for ELLIPSE)
uv_xdir2d = f.direction((1.0, 0.0, 0.0))   # ref direction

# ELLIPSE in 2D needs AXIS2_PLACEMENT_2D.
# In STEP, AXIS2_PLACEMENT_2D is (#location, #ref_direction) — 2D only.
uv_loc    = f.cartesian_point((2.0, 0.5))
uv_refdir = f.direction((1.0, 0.0))
uv_axis2d = f._emit_raw(
    f"AXIS2_PLACEMENT_2D('uv_ellipse_axis',#{uv_loc.eid},#{uv_refdir.eid})"
)
# ELLIPSE: semi_axis_1=2.0, semi_axis_2=1.0
uv_ellipse = f._emit_raw(
    f"ELLIPSE('pcurve_ellipse',#{uv_axis2d.eid},2.0,1.0)"
)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('ellipse_pc_def',(#{uv_ellipse.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('ellipse_pcurve',#{surf.eid},#{defrep.eid})")
sc_bot = f._emit_raw(
    f"SURFACE_CURVE('arc_bot',#{circle3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
# same_sense=.F. triggers GetEndTangent2d asymmetry.
e_bot = f._emit_raw(
    f"EDGE_CURVE('arc_reversed',#{v_geo_start.eid},#{v_geo_end.eid},#{sc_bot.eid},.F.)"
)

# Remaining edges: build a quadrilateral face.
# Because same_sense=.F. the arc is traversed from (1,0.5,0) to (3,0.5,0).
# We'll add three clean LINE edges to close the face.
p_top_left  = f.cartesian_point((1.0, 1.5, 0.0))
p_top_right = f.cartesian_point((3.0, 1.5, 0.0))
v_top_left  = f.vertex_point(p_top_left)
v_top_right = f.vertex_point(p_top_right)

d_up   = f.direction((0.0, 1.0, 0.0)); vec_up   = f.vector(d_up, 1.0)
d_lt   = f.direction((-1.0, 0.0, 0.0)); vec_lt = f.vector(d_lt, 2.0)
d_dn   = f.direction((0.0, -1.0, 0.0)); vec_dn  = f.vector(d_dn, 1.0)

# v_geo_end = (1, 0.5, 0) is the topological start (same_sense=.F.)
# so the edge traversal is: v_geo_start(3,0.5,0) -> v_geo_end(1,0.5,0) reversed.
# Topo: arc goes (1,0.5) → (3,0.5); then right up, top left, left down.
e_right = f.edge_curve(v_geo_end, v_top_left,  f.line(p_geo_end,   vec_up))
e_top   = f.edge_curve(v_top_left, v_top_right, f.line(p_top_left, f.vector(f.direction((1.0, 0.0, 0.0)), 2.0)))
e_left  = f.edge_curve(v_top_right, v_geo_start, f.line(p_top_right, vec_dn))

loop = f.edge_loop([
    f.oriented_edge(e_bot,   True),   # reversed arc: (3,0.5)→(1,0.5) topologically
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_left,  True),
])
face = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
