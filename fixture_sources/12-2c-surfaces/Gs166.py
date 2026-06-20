"""Gs166 — SurfaceOfRevolution V-closed seam edge gap.

Catalog claim: ShapeAnalysis_Sewing.IsVClosedSurface checks V-parameter
overlap on revolution surfaces. Edge pairs separated by gap > 0 may bypass
overlap validation; no explicit distance check confirms closure. Fixture:
SURFACE_OF_REVOLUTION with closed basis; separated edge U-parameters;
verify V-closure validation.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - SURFACE_OF_REVOLUTION with LINE profile (closed basis) IS the
    ADVANCED_FACE.face_geometry; seam edge pcurves at V=0 and V=2*pi
    separated by a gap IS the mechanism wired into face topology;
    ShapeAnalysis_Sewing.IsVClosedSurface missing explicit distance check
    (gap > 0 bypasses overlap validation) IS the defect.
  - Byte assertions: contains(b'SURFACE_OF_REVOLUTION').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: SURFACE_OF_REVOLUTION (LINE profile, axis Z) IS
    ADVANCED_FACE.face_geometry; seam edge pcurves with V-parameter gap
    (V=0 vs V=6.28) IS the mechanism wired into face topology;
    ShapeAnalysis_Sewing.IsVClosedSurface missing distance check
    (gap bypasses validation) IS the defect.
  - shape_null driver: V-closure gap undetected by IsVClosedSurface;
    sewing validation incomplete; strict kernels reject; empty result.
"""
from step_corpus.step_builder import StepFile
import math

f = StepFile(
    catalog_id="Gs166",
    defect=(
        "SURFACE_OF_REVOLUTION (LINE profile, axis Z, full 2*pi rotation) IS "
        "ADVANCED_FACE.face_geometry; seam edge pcurves with V-parameter gap "
        "(V=0 vs V=6.283) IS the mechanism wired into face topology; "
        "ShapeAnalysis_Sewing.IsVClosedSurface missing distance check "
        "(gap bypasses overlap validation) IS the defect; shape_null"
    ),
)

# ── SURFACE_OF_REVOLUTION: LINE profile revolved around Z axis ───────────────
# Byte assertion: contains(b'SURFACE_OF_REVOLUTION')
#
# The surface is a cylinder: profile = LINE from (1,0,0) to (1,0,1) revolved
# 360° about Z. V parameter covers [0, 2*pi].
# ShapeAnalysis_Sewing.IsVClosedSurface checks V-parameter overlap for revolution
# surfaces but has no explicit distance check. Seam edge pcurves placed at
# V=0 and V=6.283 (slightly past 2*pi) create a gap that bypasses validation.

# Axis placement for revolution: Z axis
ax_orig = f.cartesian_point((0.0, 0.0, 0.0))
ax_dir  = f.direction((0.0, 0.0, 1.0))  # Z axis of revolution
ax_xdir = f.direction((1.0, 0.0, 0.0))
ax3d    = f._emit_raw(
    f"AXIS1_PLACEMENT('gs166_axis',#{ax_orig.eid},#{ax_dir.eid})"
)

# Profile LINE: from (1,0,0) to (1,0,1) — the generator line at radius=1
prof_p    = f.cartesian_point((1.0, 0.0, 0.0))
prof_dir  = f.direction((0.0, 0.0, 1.0))
prof_vec  = f.vector(prof_dir, 1.0)
prof_line = f.line(prof_p, prof_vec)

# SURFACE_OF_REVOLUTION(name, swept_curve, axis_position)
rev_surf = f._emit_raw(
    f"SURFACE_OF_REVOLUTION('gs166_rev_surf',#{prof_line.eid},#{ax3d.eid})"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Face boundary: cylinder face with seam edge having V-parameter gap ────────
# Cylinder corners in 3D: at radius=1, Z=0 and Z=1, on seam (Y=0, X=1).
# UV: U = axial parameter (arc length along Z: 0..1), V = angle (0..2*pi).
# Seam edge goes along V=0 (one side) and V=6.283 (other side, gap past 2*pi).
# This gap is what bypasses IsVClosedSurface overlap validation.

p_bot = f.cartesian_point((1.0, 0.0, 0.0))
p_top = f.cartesian_point((1.0, 0.0, 1.0))

v_bot = f.vertex_point(p_bot)
v_top = f.vertex_point(p_top)


def mk_edge_line(vs, ve, p3_start, d3t, p3_len, p2_start, d2t, p2_len):
    p3e = f.cartesian_point(p3_start)
    d3e = f.direction(d3t)
    v3e = f.vector(d3e, p3_len)
    l3e = f.line(p3e, v3e)
    p2e = f.cartesian_point(p2_start)
    d2e = f.direction(d2t)
    v2e = f.vector(d2e, p2_len)
    l2e = f.line(p2e, v2e)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2e.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{rev_surf.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")


two_pi = 2.0 * math.pi  # 6.283185...

# Seam edge at V=0: bot→top (forward seam)
e_seam_fwd = mk_edge_line(v_bot, v_top,
                           (1.0, 0.0, 0.0), (0.0, 0.0, 1.0), 1.0,
                           (0.0, 0.0), (1.0, 0.0), 1.0)  # U: 0→1, V=0

# Top edge: bot→top at V=0→two_pi (should close but gap: V=0 vs V=6.283)
e_top = mk_edge_line(v_top, v_top,
                     (1.0, 0.0, 1.0), (0.0, 1.0, 0.0), 0.0,  # degenerate 3D
                     (1.0, 0.0), (0.0, 1.0), two_pi)  # V: 0→2*pi at U=1

# Seam edge at V=6.283 (gap from 2*pi): top→bot (reverse seam with gap)
e_seam_rev = mk_edge_line(v_top, v_bot,
                           (1.0, 0.0, 1.0), (0.0, 0.0, -1.0), 1.0,
                           (1.0, two_pi), (-1.0, 0.0), 1.0)  # U: 1→0, V=6.283

# Bottom edge: closing at V=two_pi→0
e_bot_edge = mk_edge_line(v_bot, v_bot,
                           (1.0, 0.0, 0.0), (0.0, -1.0, 0.0), 0.0,  # degenerate 3D
                           (0.0, two_pi), (0.0, -1.0), two_pi)  # V: 2*pi→0 at U=0

loop = f.edge_loop([
    f.oriented_edge(e_seam_fwd, True),
    f.oriented_edge(e_top, True),
    f.oriented_edge(e_seam_rev, True),
    f.oriented_edge(e_bot_edge, True),
])

# SURFACE_OF_REVOLUTION IS the face_geometry; seam edge pcurves with V-parameter
# gap (V=0 vs V=6.283) IS the mechanism wired into face topology — exercises
# ShapeAnalysis_Sewing.IsVClosedSurface missing distance check.
face  = f.advanced_face([f.face_outer_bound(loop)], rev_surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
