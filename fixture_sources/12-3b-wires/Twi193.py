"""Twi193 — ShapeAnalysis_Wire.CheckOrder index-mode-clash.

Catalog claim: CheckOrder fails to detect when edge[0]'s natural parametric
order (forward traversal in 3D) differs from edge[0]'s pcurve order on a
periodic surface seam.

Mechanism: Wire wraps around a cylindrical seam where edge[0] traverses forward
in 3D geometry (along +Z) but backward in 2D angular parameter space due to
seam topology discontinuity. CheckOrder picks 3D mode and gets the order
classification wrong, failing to flag the reversed pcurve.

Concretely: CYLINDRICAL_SURFACE (radius 1, height 4, axis +Z). The 4-edge wire
forms a patch that straddles the seam (u=0/2π boundary):

  E0: lateral at u=2π (= seam) from v0 (z=4) down to v1 (z=0).
      In 3D: x=1, y=0, z goes 4→0 (forward: going down).
      pcurve: u=2π (seam), v: 4→0 (backward in v-direction relative to
              canonical u=0 representation).
      CheckOrder in 3D-mode sees edge is going "down" (forward); pcurve says
      it's going from v_hi to v_lo (backward) — the mode clash.

  E1: bottom arc from v1 (u=2π, z=0) to v2 (u=1.0, z=0) going backward in u.
  E2: lateral at u=1.0 from v2 (z=0) up to v3 (z=4).
  E3: top arc from v3 (u=1.0, z=4) to v0 (u=2π, z=4).

The seam edge E0 has its pcurve at u=2π rather than u=0. When CheckOrder
evaluates edge[0] in 3D mode, the 3D traversal direction (z: 4→0) appears
"forward" (the loop proceeds in a valid 3D sense). But the pcurve has u=2π
(the seam copy, equivalent to u=0 but numerically different), and the v
direction runs backward. CheckOrder using 3D mode classifies the edge as
correctly ordered but misses the pcurve backward direction — the pcurve
orientation is wrong for the FACE's outer boundary winding.

Tier-3 assertion: n_faces_total == 1
Expected: occt=shape(1)/shape(1)
"""
import math as _math
from pathlib import Path as _Path
from step_corpus.step_builder import StepFile

R = 1.0
H = 4.0
TWO_PI = _math.pi * 2

f = StepFile(
    catalog_id="Twi193",
    defect=(
        "Single ADVANCED_FACE on CYLINDRICAL_SURFACE (radius 1, height 4) in "
        "CLOSED_SHELL; outer EDGE_LOOP has 4 edges; E0 is the seam lateral at "
        "u=2pi: traverses z=4→0 (forward in 3D) but pcurve has u=2pi (seam copy) "
        "v going 4→0 (backward relative to canonical u=0 sense) IS the defect; "
        "CheckOrder uses theMode3D=true, sees E0 is 'forward' in 3D but misses "
        "the reversed pcurve order on the periodic seam — index-mode-clash IS "
        "the mechanism; EDGE_LOOP IS wired into FACE_OUTER_BOUND -> ADVANCED_FACE "
        "in CLOSED_SHELL — never orphaned"
    ),
)

# ── CYLINDRICAL_SURFACE: radius 1, height 4, axis +Z ─────────────────────────
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_plc  = f.axis2_placement_3d(cyl_orig, cyl_zdir, cyl_xdir)
cyl_surf = f.cylindrical_surface(cyl_plc, R)

# ── Vertices ──────────────────────────────────────────────────────────────────
# Patch: u from 1.0 to 2π (≈6.283), z from 0 to H=4
# Corners: (u=2π, z=4), (u=2π, z=0), (u=1.0, z=0), (u=1.0, z=4)
# In 3D: u=2π = u=0 → (R,0,z) = (1,0,z); u=1.0 → (cos1, sin1, z)
vp_seam_top = (R,               0.0,         H)   # u=2π, z=4 (same as u=0)
vp_seam_bot = (R,               0.0,         0.0) # u=2π, z=0
vp_u1_bot   = (R * _math.cos(1.0), R * _math.sin(1.0), 0.0)
vp_u1_top   = (R * _math.cos(1.0), R * _math.sin(1.0), H)

v0 = f.vertex_point(f.cartesian_point(vp_seam_top))  # u=2π, z=4
v1 = f.vertex_point(f.cartesian_point(vp_seam_bot))  # u=2π, z=0
v2 = f.vertex_point(f.cartesian_point(vp_u1_bot))    # u=1.0, z=0
v3 = f.vertex_point(f.cartesian_point(vp_u1_top))    # u=1.0, z=4


def _pcurve_line(surf, u_start, v_start, du, dv, length):
    """2D line pcurve in cylinder UV parameter space."""
    pc_orig  = f.cartesian_point((u_start, v_start))
    mag = _math.sqrt(du * du + dv * dv)
    pc_dir   = f.direction((du / mag, dv / mag))
    pc_line  = f.line(pc_orig, f.vector(pc_dir, length))
    pc_def   = f._emit_raw(
        f"DEFINITIONAL_REPRESENTATION('',(#{pc_line.eid}),#*)"
    )
    return f._emit_raw(f"PCURVE('',#{surf.eid},#{pc_def.eid})")


# ── E0: seam lateral v0(seam,H)→v1(seam,0): 3D goes down, pcurve u=2π,v:H→0 ─
# 3D: correct vertical line from z=H down to z=0 at x=R, y=0
e0_3d = f.line(
    f.cartesian_point(vp_seam_top),
    f.vector(f.direction((0.0, 0.0, -1.0)), H),
)
# DEFECT: pcurve uses u=2π (seam copy), v going 4→0 (reversed from expected)
# The standard representation would be u=0, v:0→H (forward upward traversal).
# Using u=2π and v:H→0 IS the index-mode-clash defect.
pc0 = _pcurve_line(cyl_surf, TWO_PI, H, 0.0, -1.0, H)  # u=2π IS the seam copy
e0_sc = f._emit_raw(
    f"SURFACE_CURVE('',#{e0_3d.eid},(#{pc0.eid}),.PCURVE_S1.)"
)
e0  = f._emit_raw(f"EDGE_CURVE('',#{v0.eid},#{v1.eid},#{e0_sc.eid},.T.)")
oe0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e0.eid},.T.)")

# ── E1: bottom arc v1(2π,0)→v2(u=1,0): arc at z=0, u:2π→1.0 (going backward) ─
# 3D arc at z=0, from (R,0,0) to (cos1,sin1,0): traversed clockwise (u decreasing)
arc1_plc_orig = f.cartesian_point((0.0, 0.0, 0.0))
arc1_plc_zdir = f.direction((0.0, 0.0, 1.0))
arc1_plc_xdir = f.direction((1.0, 0.0, 0.0))
arc1_plc  = f.axis2_placement_3d(arc1_plc_orig, arc1_plc_zdir, arc1_plc_xdir)
arc1_circ = f._emit_raw(f"CIRCLE('',#{arc1_plc.eid},{R})")
# pcurve: u from 2π to 1.0 (backward; length = 2π - 1.0 ≈ 5.283), v=0
du_e1 = TWO_PI - 1.0
pc1 = _pcurve_line(cyl_surf, TWO_PI, 0.0, -1.0, 0.0, du_e1)  # u:2π→1.0
e1_sc = f._emit_raw(
    f"SURFACE_CURVE('',#{arc1_circ.eid},(#{pc1.eid}),.PCURVE_S1.)"
)
e1  = f._emit_raw(f"EDGE_CURVE('',#{v1.eid},#{v2.eid},#{e1_sc.eid},.T.)")
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e1.eid},.T.)")

# ── E2: lateral at u=1.0 from v2(u=1,0) up to v3(u=1,H) ─────────────────────
e2_3d = f.line(
    f.cartesian_point(vp_u1_bot),
    f.vector(f.direction((0.0, 0.0, 1.0)), H),
)
pc2 = _pcurve_line(cyl_surf, 1.0, 0.0, 0.0, 1.0, H)   # u=1.0 constant, v:0→H
e2_sc = f._emit_raw(
    f"SURFACE_CURVE('',#{e2_3d.eid},(#{pc2.eid}),.PCURVE_S1.)"
)
e2  = f._emit_raw(f"EDGE_CURVE('',#{v2.eid},#{v3.eid},#{e2_sc.eid},.T.)")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e2.eid},.T.)")

# ── E3: top arc v3(u=1,H)→v0(2π,H): arc at z=H, u:1.0→2π ──────────────────
arc3_plc_orig = f.cartesian_point((0.0, 0.0, H))
arc3_plc_zdir = f.direction((0.0, 0.0, 1.0))
arc3_plc_xdir = f.direction((1.0, 0.0, 0.0))
arc3_plc  = f.axis2_placement_3d(arc3_plc_orig, arc3_plc_zdir, arc3_plc_xdir)
arc3_circ = f._emit_raw(f"CIRCLE('',#{arc3_plc.eid},{R})")
# pcurve: u from 1.0 to 2π (forward; length = 2π - 1.0 ≈ 5.283), v=H
du_e3 = TWO_PI - 1.0
pc3 = _pcurve_line(cyl_surf, 1.0, H, 1.0, 0.0, du_e3)  # u:1.0→2π
e3_sc = f._emit_raw(
    f"SURFACE_CURVE('',#{arc3_circ.eid},(#{pc3.eid}),.PCURVE_S1.)"
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
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi193.stp")
