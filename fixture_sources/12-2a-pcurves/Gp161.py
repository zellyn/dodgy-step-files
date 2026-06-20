"""Gp161 — seam_detection_1843

Catalog claim: Seam edge with unreversed pcurve equality check without
parametric domain validation. BSpline surface with dual pcurves; orientation
loss on merge. Line 1843: aFaceSeq.Length() == 1 check branches onto unreversed
equality without orientation tracking.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS face with a seam edge that carries two pcurves
    (one per adjacent face, or one forward and one reverse). The seam edge is
    detected at OCCT line 1843 by the check `aFaceSeq.Length() == 1`. In this
    branch, the code compares the seam pcurves for equality using an unreversed
    comparison — it does not check whether one pcurve is the orientation-reversed
    form of the other. When the pcurves are equal in geometry but differ in
    orientation (one forward, one reversed), the equality check passes but the
    orientation is silently lost during merge; seam_detection_1843 axis.
  - 3D curve: a clean LINE on the seam of the B-spline surface. Geometry is
    valid and loadable.
  - NO C-1 break (Archetype B: OCC silently heals, expected shape(1)/shape(1)).

Mechanism vs driver:
  - CATALOG MECHANISM: B_SPLINE_SURFACE_WITH_KNOTS with a periodic-seam edge;
    seam EDGE_CURVE has SURFACE_CURVE with two PCURVE associations (both mapped
    to the same surface at u=0 and u=2pi); line 1843 branch: aFaceSeq.Length()==1;
    unreversed equality check used; orientation of second pcurve silently dropped;
    seam_detection_1843 axis; OCC heals silently.
  - NO C-1 DRIVER: Archetype B — geometry is clean and loadable.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp161",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS degree-2x1 bilinear-like patch (u periodic seam); "
        "seam edge: SURFACE_CURVE with two PCURVE associations; "
        "3D LINE along seam (clean, loadable); "
        "PCurve_1: LINE at u=0 from (0,0) to (0,1) — forward orientation; "
        "PCurve_2: LINE at u=0 from (0,1) to (0,0) — reverse orientation (same geometry); "
        "line 1843 aFaceSeq.Length()==1 branch: unreversed equality check; "
        "orientation of second pcurve dropped; seam_detection_1843 axis; "
        "OCC heals; shape(1)/shape(1)"
    ),
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# B_SPLINE_SURFACE_WITH_KNOTS: degree (2,1) bilinear-ish patch.
# u range [0, 2pi] (periodic seam at u=0/2pi), v range [0, 1].
# We use a simple cylindrical-like arrangement encoded as a B-spline surface.
# Control points: 5 in u (degree-2, wraps), 2 in v (degree-1).
# Parametric: u in [0, 2pi], v in [0, 1].
# We encode a rectangle in UV that looks like a cylinder roll.
# CPs at u={0, pi/2, pi, 3pi/2, 2pi}, v={0, 1}.
# For simplicity use a flat (planar) B-spline surface — OCC can still test seam logic.
R = 1.0  # unit roll radius

def roll_pt(u, v):
    """Cylinder-like B-spline surface point: (cos(u), sin(u), v)."""
    return (R * math.cos(u), R * math.sin(u), v)

u_vals = [0.0, math.pi / 2.0, math.pi, 3.0 * math.pi / 2.0, 2.0 * math.pi]
v_vals = [0.0, 1.0]

# Build control point grid (5 x 2).
cps = []
for v in v_vals:
    row = []
    for u in u_vals:
        pt = f.cartesian_point(roll_pt(u, v))
        row.append(pt)
    cps.append(row)

# Build CP list string for STEP: row-major (outer = v, inner = u).
cp_ids = ",".join(
    "(" + ",".join(f"#{cps[vi][ui].eid}" for ui in range(5)) + ")"
    for vi in range(2)
)

# Knots: u direction degree=2, 5 CPs → open knots [0,0,0, pi, pi, 2pi, 2pi, 2pi].
# v direction degree=1, 2 CPs → [0,0,1,1].
u_knots = [0.0, math.pi, 2.0 * math.pi]
u_mults = [3, 2, 3]
v_knots = [0.0, 1.0]
v_mults = [2, 2]

u_knots_str = ",".join(str(k) for k in u_knots)
u_mults_str = ",".join(str(m) for m in u_mults)
v_knots_str = ",".join(str(k) for k in v_knots)
v_mults_str = ",".join(str(m) for m in v_mults)

bsurf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('seam_bsurf',2,1,"
    f"({cp_ids}),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"({u_mults_str}),({v_mults_str}),"
    f"({u_knots_str}),({v_knots_str}),.UNSPECIFIED.)"
)

# Face vertices at seam corners: u=0, v=0..1 and u=2pi, v=0..1.
# At u=0 and u=2pi: same 3D points (seam is closed).
seam_bot_3d = roll_pt(0.0, 0.0)    # (1, 0, 0)
seam_top_3d = roll_pt(0.0, 1.0)    # (1, 0, 1)
# Also need far side corners for the loop.
# Use quarter-cylinder corners at u=pi/2.
far_bot_3d  = roll_pt(math.pi / 2.0, 0.0)   # (0, 1, 0)
far_top_3d  = roll_pt(math.pi / 2.0, 1.0)   # (0, 1, 1)

p_sb = f.cartesian_point(seam_bot_3d); v_sb = f.vertex_point(p_sb)
p_st = f.cartesian_point(seam_top_3d); v_st = f.vertex_point(p_st)
p_fb = f.cartesian_point(far_bot_3d);  v_fb = f.vertex_point(p_fb)
p_ft = f.cartesian_point(far_top_3d);  v_ft = f.vertex_point(p_ft)

def mk_line_edge_with_pc(vs, ve, p3, d3t, len3, p2t, d2t, len2):
    """Build EDGE_CURVE via SURFACE_CURVE with a linear pcurve."""
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t); v3 = f.vector(d3e, len3); l3 = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t); v2e = f.vector(d2e, len2); l2 = f.line(p2e, v2e)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{bsurf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# Bottom edge seam_bot → far_bot (v=0, u from 0 to pi/2).
chord_bot = tuple(far_bot_3d[i] - seam_bot_3d[i] for i in range(3))
len_bot   = math.sqrt(sum(x*x for x in chord_bot))
d_bot     = tuple(x / len_bot for x in chord_bot)
e_bot = mk_line_edge_with_pc(
    v_sb, v_fb,
    seam_bot_3d, d_bot, len_bot,
    (0.0, 0.0), (1.0, 0.0), math.pi / 2.0
)

# Right edge far_bot → far_top (u=pi/2, v from 0 to 1).
chord_right = tuple(far_top_3d[i] - far_bot_3d[i] for i in range(3))
len_right   = math.sqrt(sum(x*x for x in chord_right))
d_right     = tuple(x / len_right for x in chord_right)
e_right = mk_line_edge_with_pc(
    v_fb, v_ft,
    far_bot_3d, d_right, len_right,
    (math.pi / 2.0, 0.0), (0.0, 1.0), 1.0
)

# Top edge far_top → seam_top (v=1, u from pi/2 to 0).
chord_top = tuple(seam_top_3d[i] - far_top_3d[i] for i in range(3))
len_top   = math.sqrt(sum(x*x for x in chord_top))
d_top     = tuple(x / len_top for x in chord_top)
e_top = mk_line_edge_with_pc(
    v_ft, v_st,
    far_top_3d, d_top, len_top,
    (math.pi / 2.0, 1.0), (-1.0, 0.0), math.pi / 2.0
)

# ── DEFECT EDGE — seam: seam_top → seam_bot (u=0/2pi, v from 1 to 0) ────────
#
# THE CATALOG MECHANISM: SURFACE_CURVE with TWO PCURVE associations.
# PCurve_1 (forward): LINE at u=0, v from 1.0 down to 0.0 (direction (0,-1)).
# PCurve_2 (reverse): LINE at u=0, v from 0.0 up to 1.0 (direction (0,+1)) —
#   same geometric line but opposite orientation.
# At line 1843: aFaceSeq.Length()==1 branch — the code compares the two pcurves
# for equality without checking if one is orientation-reversed. Both lines share
# the same u=0 coordinate; the unreversed equality test passes; orientation of
# PCurve_2 is silently dropped; seam_detection_1843 axis.
# 3D: clean LINE from seam_top (1,0,1) to seam_bot (1,0,0).
seam_3d_chord = tuple(seam_bot_3d[i] - seam_top_3d[i] for i in range(3))
len_seam      = math.sqrt(sum(x*x for x in seam_3d_chord))
d_seam        = tuple(x / len_seam for x in seam_3d_chord)

line_3d_orig_seam = f.cartesian_point(seam_top_3d)
line_3d_dir_seam  = f.direction(d_seam)
line_3d_vec_seam  = f.vector(line_3d_dir_seam, len_seam)
line_3d_seam      = f.line(line_3d_orig_seam, line_3d_vec_seam)

# PCurve_1 (forward): u=0, v from 1 to 0 (decreasing v).
pc1_start = f.cartesian_point((0.0, 1.0))
pc1_dir   = f.direction((0.0, -1.0))
pc1_vec   = f.vector(pc1_dir, 1.0)
pc1_line  = f.line(pc1_start, pc1_vec)
pcd1 = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('seam_pc1_def',(#{pc1_line.eid}),#{prc.eid})"
)
pcurve1 = f._emit_raw(f"PCURVE('seam_pc1',#{bsurf.eid},#{pcd1.eid})")

# PCurve_2 (same geometry, reverse orientation): u=0, v from 0 to 1 (increasing v).
# This is the reversed form; line 1843 compares without orientation check.
pc2_start = f.cartesian_point((0.0, 0.0))
pc2_dir   = f.direction((0.0, 1.0))
pc2_vec   = f.vector(pc2_dir, 1.0)
pc2_line  = f.line(pc2_start, pc2_vec)
pcd2 = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('seam_pc2_def',(#{pc2_line.eid}),#{prc.eid})"
)
pcurve2 = f._emit_raw(f"PCURVE('seam_pc2',#{bsurf.eid},#{pcd2.eid})")

# SURFACE_CURVE with both pcurves listed — dual pcurve seam association.
sc_seam = f._emit_raw(
    f"SURFACE_CURVE('seam_sc',#{line_3d_seam.eid},"
    f"(#{pcurve1.eid},#{pcurve2.eid}),.PCURVE_S1.)"
)
e_seam = f._emit_raw(
    f"EDGE_CURVE('seam_detection_edge',#{v_st.eid},#{v_sb.eid},#{sc_seam.eid},.T.)"
)

# Loop: seam_bot→far_bot (bot), far_bot→far_top (right), far_top→seam_top (top),
#       seam_top→seam_bot (seam defect).
loop = f.edge_loop([
    f.oriented_edge(e_bot,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_seam,  True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], bsurf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
