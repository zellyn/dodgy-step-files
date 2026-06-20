"""Gp084 — FixSameParameter cone-apex singularity tolerance.

Catalog claim: Edge near cone apex where geometric tolerance diverges due to
apex singularity; FixSameParameter clamps tolerance and produces incorrect
magnitude without accounting for local metric scaling.

Fixture: CONICAL_SURFACE (semi-angle 45°, apex at origin, axis Z, base radius 0).
The defect edge runs from near (but NOT at) the apex (v=ε, ε=0.01) to the
rim at v=1. At v=ε the cone metric is degenerate: a unit UV step in U maps
to v*sin(α) ≈ ε in 3D — the local scale factor vanishes near the apex.
FixSameParameter uses a tolerance UNCERTAINTY value from the STEP header (0.01)
without scaling by the local metric; near v=ε this tolerance is orders of
magnitude wrong. OCC heals and produces shape(1). The tolerance is encoded in
the GEOMETRIC_REPRESENTATION_CONTEXT UNCERTAINTY measure.

Note: the 3D endpoint at v=ε is NOT the apex itself — it is offset enough that
OCC can form a valid edge, avoiding shape_null.
"""
import math
from step_corpus.step_builder import StepFile

EPS = 0.01   # v-offset from apex: small enough to make metric singular

f = StepFile(catalog_id="Gp084",
             defect="CONICAL_SURFACE pcurve near apex (v=0.01); FixSameParameter "
                    "tolerance not scaled by local metric (v*sin(alpha)); "
                    "apex singularity causes incorrect tolerance magnitude")

# CONICAL_SURFACE: semi-angle 45° (pi/4), apex at origin, axis Z, base radius 0.
# Parametric map: P(u,v) = (v*cos(u), v*sin(u), v)  [since tan(pi/4)=1, base=0]
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
cone = f.conical_surface(plc, 0.0, math.pi / 4)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# The defect spoke: from v=EPS (near-apex) to v=1 at u=0.
# 3D start: (EPS*cos(0), EPS*sin(0), EPS) = (EPS, 0, EPS)
# 3D end:   (1*cos(0),   1*sin(0),   1)   = (1,   0, 1)
p_near_apex = f.cartesian_point((EPS, 0.0, EPS))
p_rim       = f.cartesian_point((1.0, 0.0, 1.0))
v_near_apex = f.vertex_point(p_near_apex)
v_rim       = f.vertex_point(p_rim)

# 3D LINE for the defect spoke (from near-apex to rim at u=0).
# Direction: (1-EPS, 0, 1-EPS)/|..| normalized.
spoke_len = math.sqrt((1.0 - EPS)**2 + (1.0 - EPS)**2)  # = (1-EPS)*sqrt(2)
spoke_d   = f.direction(((1.0 - EPS) / spoke_len, 0.0, (1.0 - EPS) / spoke_len))
spoke_v   = f.vector(spoke_d, spoke_len)
spoke_line_3d = f.line(p_near_apex, spoke_v)

# Pcurve: LINE in UV from (u=0, v=EPS) to (u=0, v=1).
pc_start = f.cartesian_point((0.0, EPS))
pc_dir   = f.direction((0.0, 1.0))
pc_vec   = f.vector(pc_dir, 1.0 - EPS)
pc_line  = f.line(pc_start, pc_vec)
defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('spoke_pc_def',(#{pc_line.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('near_apex_spoke',#{cone.eid},#{defrep.eid})")
sc_spoke = f._emit_raw(
    f"SURFACE_CURVE('spoke',#{spoke_line_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
edge_spoke = f._emit_raw(
    f"EDGE_CURVE('spoke_u0',#{v_near_apex.eid},#{v_rim.eid},#{sc_spoke.eid},.T.)"
)

# Second spoke at u=pi/2 to close the face (also clean).
# 3D: from (0, EPS, EPS) to (0, 1, 1).
p_near_apex2 = f.cartesian_point((0.0, EPS, EPS))
p_rim2       = f.cartesian_point((0.0, 1.0, 1.0))
v_near_apex2 = f.vertex_point(p_near_apex2)
v_rim2       = f.vertex_point(p_rim2)

spoke2_d  = f.direction((0.0, (1.0 - EPS) / spoke_len, (1.0 - EPS) / spoke_len))
spoke2_v  = f.vector(spoke2_d, spoke_len)
spoke2_line_3d = f.line(p_near_apex2, spoke2_v)
pc2_start = f.cartesian_point((math.pi / 2.0, EPS))
pc2_vec   = f.vector(pc_dir, 1.0 - EPS)
pc2_line  = f.line(pc2_start, pc2_vec)
defrep2 = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('spoke2_pc_def',(#{pc2_line.eid}),#{prc.eid})"
)
pcurve2 = f._emit_raw(f"PCURVE('spoke2',#{cone.eid},#{defrep2.eid})")
sc_spoke2 = f._emit_raw(
    f"SURFACE_CURVE('spoke2',#{spoke2_line_3d.eid},(#{pcurve2.eid}),.PCURVE_S1.)"
)
edge_spoke2 = f._emit_raw(
    f"EDGE_CURVE('spoke_u90',#{v_near_apex2.eid},#{v_rim2.eid},#{sc_spoke2.eid},.T.)"
)

# Bottom arc near the apex at v=EPS: quarter-circle in the near-apex plane.
# Center at (0, 0, EPS) projected (since on cone at v=EPS, all u map to radius=EPS*tan(pi/4)=EPS).
arc_near_ctr = f.cartesian_point((0.0, 0.0, EPS))
arc_near_axis = f.axis2_placement_3d(arc_near_ctr, zdir, xdir)
arc_near_circ = f._emit_raw(f"CIRCLE('near_apex_arc',#{arc_near_axis.eid},{EPS})")
near_arc_pc_start = f.cartesian_point((0.0, EPS))
near_arc_pc_dir   = f.direction((1.0, 0.0))
near_arc_pc_vec   = f.vector(near_arc_pc_dir, math.pi / 2.0)
near_arc_pc_line  = f.line(near_arc_pc_start, near_arc_pc_vec)
defrep_near_arc = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('near_arc_pc_def',(#{near_arc_pc_line.eid}),#{prc.eid})"
)
pcurve_near_arc = f._emit_raw(f"PCURVE('near_arc_pc',#{cone.eid},#{defrep_near_arc.eid})")
sc_near_arc = f._emit_raw(
    f"SURFACE_CURVE('near_arc',#{arc_near_circ.eid},(#{pcurve_near_arc.eid}),.PCURVE_S1.)"
)
edge_near_arc = f._emit_raw(
    f"EDGE_CURVE('near_apex_arc_edge',#{v_near_apex.eid},#{v_near_apex2.eid},#{sc_near_arc.eid},.T.)"
)

# Rim arc at v=1: quarter-circle from p_rim to p_rim2.
arc_rim_ctr  = f.cartesian_point((0.0, 0.0, 1.0))
arc_rim_axis = f.axis2_placement_3d(arc_rim_ctr, zdir, xdir)
arc_rim_circ = f._emit_raw(f"CIRCLE('rim_arc',#{arc_rim_axis.eid},1.0)")
rim_arc_pc_start = f.cartesian_point((0.0, 1.0))
rim_arc_pc_vec   = f.vector(near_arc_pc_dir, math.pi / 2.0)
rim_arc_pc_line  = f.line(rim_arc_pc_start, rim_arc_pc_vec)
defrep_rim_arc = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('rim_arc_pc_def',(#{rim_arc_pc_line.eid}),#{prc.eid})"
)
pcurve_rim_arc = f._emit_raw(f"PCURVE('rim_arc_pc',#{cone.eid},#{defrep_rim_arc.eid})")
sc_rim_arc = f._emit_raw(
    f"SURFACE_CURVE('rim_arc',#{arc_rim_circ.eid},(#{pcurve_rim_arc.eid}),.PCURVE_S1.)"
)
edge_rim = f._emit_raw(
    f"EDGE_CURVE('rim_arc_edge',#{v_rim.eid},#{v_rim2.eid},#{sc_rim_arc.eid},.T.)"
)

# Loop: near_apex_arc (fwd) + spoke2 (fwd) + rim_arc (rev) + spoke (rev).
loop = f.edge_loop([
    f.oriented_edge(edge_near_arc, True),
    f.oriented_edge(edge_spoke2,   True),
    f.oriented_edge(edge_rim,      False),
    f.oriented_edge(edge_spoke,    False),
])
face = f.advanced_face([f.face_outer_bound(loop)], cone)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
