"""Twi110 — CheckEdgeCurves 3D-vs-2D Coherence.

Catalog claim: Cylindrical wire where edge E3 3D curve (LINE P2→P3) is
geometrically correct but pcurve maps to surface parameters (u, v) that evaluate
to misaligned 3D point, failing curve/pcurve coherence.

Pattern: 4-edge cylindrical loop; E3 pcurve v-extent artificially expanded to
-5.0 to break sampling alignment.

Coverage: ShapeAnalysis_Wire.CheckEdgeCurves 3D curve vs pcurve-on-surface point
sampling mismatch.

Mechanism IS a cylindrical ADVANCED_FACE (radius 1, height 4) whose outer 4-edge
EDGE_LOOP has edges:
  E0: bottom arc, correct 3D+pcurve
  E1: lateral line, correct 3D+pcurve
  E2: top arc, correct 3D+pcurve
  E3: lateral line (3D curve correct: from v3=(1,0,4) to v0=(1,0,0)) but pcurve
      v-range is artificially set to v_start=-5.0 (instead of v=4) so that the
      pcurve evaluates to 3D point (1,0,-5) at parameter start — far from the
      3D curve start at (1,0,4). CheckEdgeCurves samples mid-curve and detects
      mismatch between 3D point and pcurve-on-surface point.

Tier-3 assertion: n_faces_total == 1
Expected: occt=shape(1)/shape(1)
"""
import math as _math
from step_corpus.step_builder import StepFile

R = 1.0
H = 4.0

f = StepFile(
    catalog_id="Twi110",
    defect=(
        "Single ADVANCED_FACE on a CYLINDRICAL_SURFACE (radius 1, height 4, axis +Z); "
        "outer EDGE_LOOP has 4 edges: E0 bottom arc, E1 lateral, E2 top arc (all correct); "
        "E3 lateral: 3D LINE from v3=(1,0,4) to v0=(1,0,0) is geometrically correct; "
        "but pcurve v-start is set to -5.0 instead of 4.0 — "
        "pcurve evaluates to 3D point (1,0,-5) at parameter start; "
        "mid-curve sampling mismatch: 3D midpoint=(1,0,2), pcurve midpoint=(1,0,-2.5); "
        "ShapeAnalysis_Wire.CheckEdgeCurves detects 3D-vs-pcurve incoherence IS mechanism; "
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
v0 = f.vertex_point(f.cartesian_point((R,   0.0,  0.0)))   # theta=0, z=0
v1 = f.vertex_point(f.cartesian_point((0.0, R,    0.0)))   # theta=pi/2, z=0
v2 = f.vertex_point(f.cartesian_point((0.0, R,    H)))     # theta=pi/2, z=H
v3 = f.vertex_point(f.cartesian_point((R,   0.0,  H)))     # theta=0,   z=H


def _pcurve_line(cyl, u_start, v_start, du, dv, length):
    """Emit a PCURVE whose definitional representation is a 2D LINE in UV."""
    mag = _math.sqrt(du * du + dv * dv)
    pc_orig   = f.cartesian_point((u_start, v_start))
    pc_dir2d  = f.direction((du / mag, dv / mag))
    pc_line2d = f.line(pc_orig, f.vector(pc_dir2d, length))
    pc_def_rep = f._emit_raw(
        f"DEFINITIONAL_REPRESENTATION('',(#{pc_line2d.eid}),#*)"
    )
    return f._emit_raw(f"PCURVE('',#{cyl.eid},#{pc_def_rep.eid})")


# ── E0: bottom arc v0(R,0,0) → v1(0,R,0), theta=0→pi/2 ──────────────────────
arc0_plc_orig = f.cartesian_point((0.0, 0.0, 0.0))
arc0_plc_zdir = f.direction((0.0, 0.0, 1.0))
arc0_plc_xdir = f.direction((1.0, 0.0, 0.0))
arc0_plc    = f.axis2_placement_3d(arc0_plc_orig, arc0_plc_zdir, arc0_plc_xdir)
arc0_circle = f._emit_raw(f"CIRCLE('',#{arc0_plc.eid},{R})")
pc0 = _pcurve_line(cyl_surf, 0.0, 0.0, _math.pi / 2, 0.0, _math.pi / 2)
e0_sc = f._emit_raw(
    f"SURFACE_CURVE('',#{arc0_circle.eid},(#{pc0.eid}),.PCURVE_S1.)"
)
e0  = f._emit_raw(f"EDGE_CURVE('',#{v0.eid},#{v1.eid},#{e0_sc.eid},.T.)")
oe0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e0.eid},.T.)")

# ── E1: lateral v1(0,R,0)→v2(0,R,H), u=pi/2, v: 0→H ──────────────────────────
lat1_3d = f.line(
    f.cartesian_point((0.0, R, 0.0)),
    f.vector(f.direction((0.0, 0.0, 1.0)), H),
)
pc1 = _pcurve_line(cyl_surf, _math.pi / 2, 0.0, 0.0, 1.0, H)
e1_sc = f._emit_raw(
    f"SURFACE_CURVE('',#{lat1_3d.eid},(#{pc1.eid}),.PCURVE_S1.)"
)
e1  = f._emit_raw(f"EDGE_CURVE('',#{v1.eid},#{v2.eid},#{e1_sc.eid},.T.)")
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e1.eid},.T.)")

# ── E2: top arc v2(0,R,H)→v3(R,0,H), theta=pi/2→0 ───────────────────────────
arc2_plc_orig = f.cartesian_point((0.0, 0.0, H))
arc2_plc_zdir = f.direction((0.0, 0.0, 1.0))
arc2_plc_xdir = f.direction((1.0, 0.0, 0.0))
arc2_plc    = f.axis2_placement_3d(arc2_plc_orig, arc2_plc_zdir, arc2_plc_xdir)
arc2_circle = f._emit_raw(f"CIRCLE('',#{arc2_plc.eid},{R})")
pc2 = _pcurve_line(cyl_surf, _math.pi / 2, H, -(_math.pi / 2), 0.0, _math.pi / 2)
e2_sc = f._emit_raw(
    f"SURFACE_CURVE('',#{arc2_circle.eid},(#{pc2.eid}),.PCURVE_S1.)"
)
e2  = f._emit_raw(f"EDGE_CURVE('',#{v2.eid},#{v3.eid},#{e2_sc.eid},.T.)")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e2.eid},.T.)")

# ── E3: lateral v3(R,0,H)→v0(R,0,0), u=0, v: H→0 ────────────────────────────
# 3D curve is geometrically correct: vertical line from (R,0,H) to (R,0,0)
lat3_3d = f.line(
    f.cartesian_point((R, 0.0, H)),
    f.vector(f.direction((0.0, 0.0, -1.0)), H),
)
# DEFECT: pcurve v-start is -5.0 instead of correct 4.0.
# Correct pcurve: u=0, v: H→0 (length H).
# Defective pcurve: u=0, v: -5.0→-9.0 (direction -v, length H).
# Surface evaluation at u=0, v=-5.0: (R*cos(0), R*sin(0), -5.0) = (1,0,-5)
#   vs 3D start (1,0,4) — 9-unit mismatch at start; midpoint (1,0,-2.5) vs (1,0,2).
# CheckEdgeCurves samples along the 3D curve and the pcurve and detects mismatch.
pc3 = _pcurve_line(cyl_surf, 0.0, -5.0, 0.0, -1.0, H)  # v_start=-5.0 IS defect
e3_sc = f._emit_raw(
    f"SURFACE_CURVE('',#{lat3_3d.eid},(#{pc3.eid}),.PCURVE_S1.)"
)
e3  = f._emit_raw(f"EDGE_CURVE('',#{v3.eid},#{v0.eid},#{e3_sc.eid},.T.)")
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
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi110.stp")
