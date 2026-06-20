"""Twi109 — FixShifted Period-Shift on Closed Surface.

Catalog claim: Cylindrical wire (periodic in U) where edge E3 pcurve is shifted
by +2π in parameter space, breaking U continuity. 3D curve correct; pcurve jumps
discontinuously.

Pattern: 4-edge closed loop on CYLINDRICAL_SURFACE; E3 pcurve uses u∈[8.06,8.06]
(shifted) instead of u∈[0.78,0.78] (true).

Coverage: ShapeFix_Wire.FixShifted periodic surface parameter normalization.

Mechanism IS a cylindrical ADVANCED_FACE (radius 1, height 4) whose outer 4-edge
EDGE_LOOP has edges:
  E0: bottom-arc v0(1,0,0)→v1(0,1,0), theta=0→π/2; pcurve u:0→π/2
  E1: lateral  v1(0,1,0)→v2(0,1,4), v-direction; pcurve u=π/2, v:0→4
  E2: top-arc  v2(0,1,4)→v3(1,0,4), theta=π/2→0; pcurve u:π/2→0
  E3: lateral  v3(1,0,4)→v0(1,0,0), v-direction; pcurve SHIFTED u=0+2π=6.283...,
      v:4→0 (IS defect — shifted by full period +2π instead of correct u=0)
FixShifted normalizes the period-shifted pcurve back to the canonical range.

Tier-3 assertion: n_faces_total == 1
Expected: occt=shape(1)/shape(1)
"""
import math as _math
from step_corpus.step_builder import StepFile

TWO_PI = _math.pi * 2   # 6.28318530718

R = 1.0
H = 4.0

f = StepFile(
    catalog_id="Twi109",
    defect=(
        "Single ADVANCED_FACE on a CYLINDRICAL_SURFACE (radius 1, height 4, axis +Z); "
        "outer EDGE_LOOP has 4 edges: "
        "E0 bottom arc (theta 0→pi/2, v=0); E1 lateral (u=pi/2, v:0→4); "
        "E2 top arc (theta pi/2→0, v=4); "
        "E3 lateral 3D-curve correct (u=0, v:4→0) but pcurve shifted +2pi "
        "— pcurve starts at u=6.28318530718 instead of u=0; "
        "U-continuity breaks at E2/E3 junction in parameter space; "
        "ShapeFix_Wire.FixShifted normalizes period-shifted pcurve IS mechanism; "
        "EDGE_LOOP IS wired into FACE_OUTER_BOUND -> ADVANCED_FACE in CLOSED_SHELL; "
        "never orphaned"
    ),
)

# ── CYLINDRICAL_SURFACE: radius 1, axis +Z ────────────────────────────────────
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_plc  = f.axis2_placement_3d(cyl_orig, cyl_zdir, cyl_xdir)
cyl_surf = f.cylindrical_surface(cyl_plc, R)

# ── Vertices: quarter-cylinder patch ─────────────────────────────────────────
# theta=0: x=R, y=0; theta=pi/2: x=0, y=R
v0 = f.vertex_point(f.cartesian_point((R,   0.0,  0.0)))   # theta=0, z=0
v1 = f.vertex_point(f.cartesian_point((0.0, R,    0.0)))   # theta=pi/2, z=0
v2 = f.vertex_point(f.cartesian_point((0.0, R,    H)))     # theta=pi/2, z=H
v3 = f.vertex_point(f.cartesian_point((R,   0.0,  H)))     # theta=0,   z=H


def _pcurve_line(cyl, u_start, v_start, du, dv, length):
    """Emit a PCURVE whose definitional representation is a 2D LINE in UV."""
    pc_orig    = f.cartesian_point((u_start, v_start))
    if length == 0:
        raise ValueError("zero-length pcurve")
    mag = _math.sqrt(du * du + dv * dv)
    pc_dir2d   = f.direction((du / mag, dv / mag))
    pc_line2d  = f.line(pc_orig, f.vector(pc_dir2d, length))
    pc_def_rep = f._emit_raw(
        f"DEFINITIONAL_REPRESENTATION('',(#{pc_line2d.eid}),#*)"
    )
    return f._emit_raw(f"PCURVE('',#{cyl.eid},#{pc_def_rep.eid})")


# ── E0: bottom arc v0(R,0,0) → v1(0,R,0), theta=0→pi/2 ──────────────────────
arc0_plc_orig = f.cartesian_point((0.0, 0.0, 0.0))
arc0_plc_zdir = f.direction((0.0, 0.0, 1.0))
arc0_plc_xdir = f.direction((1.0, 0.0, 0.0))
arc0_plc   = f.axis2_placement_3d(arc0_plc_orig, arc0_plc_zdir, arc0_plc_xdir)
arc0_circle = f._emit_raw(f"CIRCLE('',#{arc0_plc.eid},{R})")
# pcurve: u: 0→pi/2, v=0 (constant)
pc0 = _pcurve_line(cyl_surf, 0.0, 0.0, _math.pi / 2, 0.0, _math.pi / 2)
e0_sc = f._emit_raw(
    f"SURFACE_CURVE('',#{arc0_circle.eid},(#{pc0.eid}),.PCURVE_S1.)"
)
e0 = f._emit_raw(
    f"EDGE_CURVE('',#{v0.eid},#{v1.eid},#{e0_sc.eid},.T.)"
)
oe0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e0.eid},.T.)")

# ── E1: lateral v1(0,R,0)→v2(0,R,H), u=pi/2, v: 0→H ──────────────────────────
lat1_3d = f.line(
    f.cartesian_point((0.0, R, 0.0)),
    f.vector(f.direction((0.0, 0.0, 1.0)), H),
)
# pcurve: u=pi/2 (constant), v: 0→H
pc1 = _pcurve_line(cyl_surf, _math.pi / 2, 0.0, 0.0, 1.0, H)
e1_sc = f._emit_raw(
    f"SURFACE_CURVE('',#{lat1_3d.eid},(#{pc1.eid}),.PCURVE_S1.)"
)
e1 = f._emit_raw(
    f"EDGE_CURVE('',#{v1.eid},#{v2.eid},#{e1_sc.eid},.T.)"
)
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e1.eid},.T.)")

# ── E2: top arc v2(0,R,H)→v3(R,0,H), theta=pi/2→0 ───────────────────────────
arc2_plc_orig = f.cartesian_point((0.0, 0.0, H))
arc2_plc_zdir = f.direction((0.0, 0.0, 1.0))
arc2_plc_xdir = f.direction((1.0, 0.0, 0.0))
arc2_plc   = f.axis2_placement_3d(arc2_plc_orig, arc2_plc_zdir, arc2_plc_xdir)
arc2_circle = f._emit_raw(f"CIRCLE('',#{arc2_plc.eid},{R})")
# pcurve: u: pi/2→0 (length = pi/2, direction = -u)
pc2 = _pcurve_line(cyl_surf, _math.pi / 2, H, -_math.pi / 2, 0.0, _math.pi / 2)
e2_sc = f._emit_raw(
    f"SURFACE_CURVE('',#{arc2_circle.eid},(#{pc2.eid}),.PCURVE_S1.)"
)
# arc from v2→v3 traversed backwards on the circle (reversed sense)
e2 = f._emit_raw(
    f"EDGE_CURVE('',#{v2.eid},#{v3.eid},#{e2_sc.eid},.T.)"
)
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e2.eid},.T.)")

# ── E3: lateral v3(R,0,H)→v0(R,0,0), u=0, v: H→0 ───────────────────────────
# 3D curve is correct (vertical line down at x=R, y=0)
lat3_3d = f.line(
    f.cartesian_point((R, 0.0, H)),
    f.vector(f.direction((0.0, 0.0, -1.0)), H),
)
# DEFECT: pcurve u is shifted by +2π instead of correct u=0
# Correct: u=0, v: H→0.  Defective: u=0+2π=6.28318530718, v: H→0
u_shifted = TWO_PI   # 6.28318530718 instead of 0.0
pc3 = _pcurve_line(cyl_surf, u_shifted, H, 0.0, -1.0, H)
e3_sc = f._emit_raw(
    f"SURFACE_CURVE('',#{lat3_3d.eid},(#{pc3.eid}),.PCURVE_S1.)"
)
e3 = f._emit_raw(
    f"EDGE_CURVE('',#{v3.eid},#{v0.eid},#{e3_sc.eid},.T.)"
)
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e3.eid},.T.)")

# ── EDGE_LOOP ─────────────────────────────────────────────────────────────────
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe0.eid},#{oe1.eid},#{oe2.eid},#{oe3.eid}))"
)
fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{cyl_surf.eid},.T.)")
shell = f._emit_raw(f"CLOSED_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
from pathlib import Path as _Path
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi109.stp")
