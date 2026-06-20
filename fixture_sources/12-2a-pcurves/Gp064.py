"""Gp064 — ShapeFix_Edge.FixRemovePCurve degenerate-on-cone.

Catalog claim: Edge at cone apex where 3D curve has zero length (degenerate
point). PCurve is parametrically valid but references degenerate geometry.
FixRemovePCurve removes pcurve, leaving only unusable zero-length 3D curve.

Fixture: Face on CONICAL_SURFACE (semi-angle 45°, apex at origin, axis Z).
Face is a cone sector from u=0 to u=pi/2, v ∈ [0, 1]. Three edges:
  - left spoke  (THE DEFECT): from apex to rim at u=0
  - rim arc:    quarter-circle arc at v=1 from u=0 to u=pi/2
  - right spoke: from apex to rim at u=pi/2

THE DEFECT on the left spoke:
  - 3D curve: degree-2 B-spline with 6 CPs and a C-1 POSITIONAL BREAK at t=0.5
    (knot mult=3=degree+1 at interior). This represents the state of the spoke
    edge after FixRemovePCurve removes the valid pcurve from the degenerate apex
    region, then FixSameParameter stitches a replacement: the apex portion
    (v ∈ [0, 0.5]) maps to the degenerate apex point in 3D (all u values give the
    same 3D point), so the replacement is a zero-length stub stitched to the
    non-degenerate upper half (v ∈ [0.5, 1.0]).
  - pcurve: correct LINE from (u=0, v=0) to (u=0, v=1.0) on the cone
The 3D break at t=0.5: CP[2]=(0.0, 0.0, 0.0) vs CP[3]=(0.5, 0.0, 0.5) —
the break jumps from the apex origin to the midpoint of the spoke in 3D space
(a 0.707-unit jump). CP[0]=(0,0,0) and CP[5]=(1,0,1) are the correct vertices.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp064",
    defect=(
        "Left spoke on CONICAL_SURFACE (semi_angle=pi/4): degree-2 B-spline 3D "
        "curve with C-1 positional break at t=0.5 (knot mult=3); break at "
        "CP[2]=(0,0,0) vs CP[3]=(0.5,0,0.5) represents FixRemovePCurve removing "
        "apex pcurve and FixSameParameter stitching zero-length apex stub to "
        "non-degenerate spoke half; 0.707-unit jump → OCC empty"
    ),
)

# CONICAL_SURFACE: semi-angle 45° (pi/4), apex at origin, axis Z.
# At (u, v): 3D = (v*cos(u), v*sin(u), v)  [tan(pi/4)=1]
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
cone = f.conical_surface(plc, 0.0, math.pi / 4)

# UV parametric context
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Vertices:
#   v_apex   = (0, 0, 0) at (u=any, v=0) — cone apex (degenerate in u)
#   v_rim_0  = (1, 0, 1) at (u=0,   v=1) — rim at u=0
#   v_rim_90 = (0, 1, 1) at (u=pi/2, v=1) — rim at u=pi/2
p_apex    = f.cartesian_point((0.0, 0.0, 0.0))
p_rim_0   = f.cartesian_point((1.0, 0.0, 1.0))
p_rim_90  = f.cartesian_point((0.0, 1.0, 1.0))
v_apex    = f.vertex_point(p_apex)
v_rim_0   = f.vertex_point(p_rim_0)
v_rim_90  = f.vertex_point(p_rim_90)

# ---- LEFT SPOKE (THE DEFECT): C-1 break at midpoint ----
# 6 CPs, degree 2, knots (3,3,3) at (0.0, 0.5, 1.0) → break at t=0.5.
# The break at t=0.5 represents the stitching point between the zero-length
# apex stub (all CP map to apex=(0,0,0) in the degenerate region) and the
# non-degenerate upper spoke.
# CP[0]=(0,0,0) and CP[5]=(1,0,1) are the correct spoke endpoints.
s0 = f.cartesian_point((0.0, 0.0, 0.0))    # apex — correct start
s1 = f.cartesian_point((0.0, 0.0, 0.0))    # degenerate stub: still at apex
s2 = f.cartesian_point((0.0, 0.0, 0.0))    # degenerate stub: still at apex (C-1 before break)
s3 = f.cartesian_point((0.5, 0.0, 0.5))    # DEFECT: jumps to spoke midpoint (C-1 after break)
s4 = f.cartesian_point((0.75, 0.0, 0.75))  # spoke upper quarter
s5 = f.cartesian_point((1.0, 0.0, 1.0))    # rim — correct end (p_rim_0)

spoke0_bspline = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('fixremovepcurve_apex_stub',2,"
    f"(#{s0.eid},#{s1.eid},#{s2.eid},#{s3.eid},#{s4.eid},#{s5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# Pcurve: LINE from (u=0, v=0) to (u=0, v=1.0) — correct radial path.
# This IS the valid pcurve that FixRemovePCurve would remove (because v=0 is
# degenerate: the apex maps all u to (0,0,0)). After removal, the B-spline
# above (with its break) is what remains.
pc_s0_start = f.cartesian_point((0.0, 0.0))
pc_s0_dir   = f.direction((0.0, 1.0))
pc_s0_vec   = f.vector(pc_s0_dir, 1.0)
pc_s0_line  = f.line(pc_s0_start, pc_s0_vec)
pc_s0_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_spoke0_def',(#{pc_s0_line.eid}),#{prc.eid})"
)
pcurve_s0 = f._emit_raw(
    f"PCURVE('spoke0_degenerate_apex',#{cone.eid},#{pc_s0_def.eid})"
)
sc_s0 = f._emit_raw(
    f"SURFACE_CURVE('spoke0',#{spoke0_bspline.eid},(#{pcurve_s0.eid}),.PCURVE_S1.)"
)
edge_s0 = f._emit_raw(
    f"EDGE_CURVE('spoke_u0',#{v_apex.eid},#{v_rim_0.eid},#{sc_s0.eid},.T.)"
)

# ---- RIM ARC: quarter-circle at v=1 from rim_0 to rim_90 ----
arc_ctr  = f.cartesian_point((0.0, 0.0, 1.0))
arc_zd   = f.direction((0.0, 0.0, 1.0))
arc_xd   = f.direction((1.0, 0.0, 0.0))
arc_axis = f.axis2_placement_3d(arc_ctr, arc_zd, arc_xd)
rim_circle = f.circle(arc_axis, 1.0)
pc_rim_start = f.cartesian_point((0.0, 1.0))
pc_rim_dir   = f.direction((1.0, 0.0))
pc_rim_vec   = f.vector(pc_rim_dir, math.pi / 2.0)
pc_rim_line  = f.line(pc_rim_start, pc_rim_vec)
pc_rim_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_rim_def',(#{pc_rim_line.eid}),#{prc.eid})"
)
pcurve_rim = f._emit_raw(f"PCURVE('rim_arc',#{cone.eid},#{pc_rim_def.eid})")
sc_rim = f._emit_raw(
    f"SURFACE_CURVE('rim_arc',#{rim_circle.eid},(#{pcurve_rim.eid}),.PCURVE_S1.)"
)
edge_rim = f._emit_raw(
    f"EDGE_CURVE('rim_arc',#{v_rim_0.eid},#{v_rim_90.eid},#{sc_rim.eid},.T.)"
)

# ---- RIGHT SPOKE: correct spoke at u=pi/2 ----
d_spoke90  = f.direction((0.0, 1.0/math.sqrt(2), 1.0/math.sqrt(2)))
vec_spoke90 = f.vector(d_spoke90, math.sqrt(2.0))
spoke90_line_3d = f.line(p_apex, vec_spoke90)
pc_s90_start = f.cartesian_point((math.pi / 2.0, 0.0))
pc_s90_dir   = f.direction((0.0, 1.0))
pc_s90_vec   = f.vector(pc_s90_dir, 1.0)
pc_s90_line  = f.line(pc_s90_start, pc_s90_vec)
pc_s90_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_spoke90_def',(#{pc_s90_line.eid}),#{prc.eid})"
)
pcurve_s90 = f._emit_raw(f"PCURVE('spoke90',#{cone.eid},#{pc_s90_def.eid})")
sc_s90 = f._emit_raw(
    f"SURFACE_CURVE('spoke90',#{spoke90_line_3d.eid},(#{pcurve_s90.eid}),.PCURVE_S1.)"
)
edge_s90 = f._emit_raw(
    f"EDGE_CURVE('spoke_u90',#{v_apex.eid},#{v_rim_90.eid},#{sc_s90.eid},.T.)"
)

# 3-edge loop: left-spoke(fwd) -> rim_arc(fwd) -> right-spoke(rev)
loop = f.edge_loop([
    f.oriented_edge(edge_s0,  True),
    f.oriented_edge(edge_rim, True),
    f.oriented_edge(edge_s90, False),
])
face = f.advanced_face([f.face_outer_bound(loop)], cone)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
