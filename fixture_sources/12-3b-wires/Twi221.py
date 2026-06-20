"""Twi221 — ShapeFix_Wire.FixDummySeam non-canonical-seam-position.

Catalog claim: Surface with seam at u=pi/4 (not standard 0 or 2pi).
FixDummySeam's heuristic assumes canonical seam positions only and fails
on non-standard placements.

Mechanism: A CYLINDRICAL_SURFACE whose X-direction reference axis is rotated
by pi/4 about +Z from the global X-axis. This places the seam (u=0 in the
cylinder's own parametric space, which is the x-direction of the placement)
at a real-space angle of pi/4 from global X. The EDGE_LOOP forms a full closed
band around the cylinder (one seam edge + top circle + bottom circle), with
the seam edge at the non-canonical angular position (global angle = pi/4).
FixDummySeam looks for seam edges at canonical u=0 or u=2pi positions; the
seam at u=pi/4 (global 45 degrees) is not recognized — FixDummySeam fails to
repair the wire's seam IS the mechanism.

Wire on CYLINDRICAL_SURFACE (radius 1, height 2):
  - Cylinder placement: X-reference direction = (cos(pi/4), sin(pi/4), 0)
    → seam at global angle pi/4 (45 degrees)
  - v_bot = vertex at seam, z=0: (cos(pi/4), sin(pi/4), 0)
  - v_top = vertex at seam, z=H: (cos(pi/4), sin(pi/4), H)
  - E0: seam lateral from v_bot to v_top (going up along the seam line)
  - E1: full top circle from v_top back to v_top
  - E2: seam lateral back from v_top to v_bot (going down, same EDGE_CURVE reversed)
  - E3: full bottom circle from v_bot back to v_bot
  The full circular face around the cylinder with seam at pi/4.

Tier-3 assertion: load == "ok"
Expected: occt=shape(1)/shape(1)
"""
import math as _math
from pathlib import Path as _Path
from step_corpus.step_builder import StepFile

R = 1.0
H = 2.0
SEAM_ANGLE = _math.pi / 4.0   # non-canonical seam position IS the defect

f = StepFile(
    catalog_id="Twi221",
    defect=(
        "Single ADVANCED_FACE on CYLINDRICAL_SURFACE (radius 1, height 2) in "
        "CLOSED_SHELL; cylinder X-reference rotated by pi/4 about +Z places "
        "seam at global angle pi/4 — non-canonical seam position IS the defect; "
        "full closed band EDGE_LOOP (seam-lateral + full-top-circle + "
        "seam-lateral-reversed + full-bottom-circle); "
        "FixDummySeam heuristic only looks for seam at u=0 or u=2pi — "
        "fails on non-standard pi/4 placement IS the mechanism; "
        "EDGE_LOOP IS wired into FACE_OUTER_BOUND -> ADVANCED_FACE in "
        "CLOSED_SHELL — never orphaned"
    ),
)

# -- CYLINDRICAL_SURFACE with seam at pi/4 ------------------------------------
# X-reference rotated by pi/4: places seam at global angle pi/4 (45 degrees)
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
# Rotate X-axis by pi/4 about Z → seam at pi/4
cyl_xdir = f.direction((_math.cos(SEAM_ANGLE), _math.sin(SEAM_ANGLE), 0.0))
cyl_plc  = f.axis2_placement_3d(cyl_orig, cyl_zdir, cyl_xdir)
cyl_surf = f.cylindrical_surface(cyl_plc, R)

# Seam point in 3D: (R*cos(pi/4), R*sin(pi/4), z)
seam_x = R * _math.cos(SEAM_ANGLE)
seam_y = R * _math.sin(SEAM_ANGLE)

v_bot = f.vertex_point(f.cartesian_point((seam_x, seam_y, 0.0)))
v_top = f.vertex_point(f.cartesian_point((seam_x, seam_y, H)))

# -- E0: seam lateral from v_bot to v_top (going UP) -------------------------
seam_3d = f.line(
    f.cartesian_point((seam_x, seam_y, 0.0)),
    f.vector(f.direction((0.0, 0.0, 1.0)), H),
)
# Pcurve for seam: u=0 in cyl UV space, v: 0→H
def _pcurve_2d(surf, u0, v0, du, dv, length):
    pc_orig = f.cartesian_point((u0, v0))
    mag = _math.sqrt(du*du + dv*dv)
    pc_dir  = f.direction((du/mag, dv/mag))
    pc_line = f.line(pc_orig, f.vector(pc_dir, length))
    pc_def  = f._emit_raw(
        f"DEFINITIONAL_REPRESENTATION('',(#{pc_line.eid}),#*)"
    )
    return f._emit_raw(f"PCURVE('',#{surf.eid},#{pc_def.eid})")

pc_seam_up = _pcurve_2d(cyl_surf, 0.0, 0.0, 0.0, 1.0, H)   # u=0, v:0→H
seam_sc = f._emit_raw(
    f"SURFACE_CURVE('',#{seam_3d.eid},(#{pc_seam_up.eid}),.PCURVE_S1.)"
)
seam_edge = f._emit_raw(
    f"EDGE_CURVE('',#{v_bot.eid},#{v_top.eid},#{seam_sc.eid},.T.)"
)
oe_seam_up = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{seam_edge.eid},.T.)")

# -- E1: top full circle from v_top back to v_top ----------------------------
# 3D full circle at z=H; traversed from seam point counterclockwise, full 2pi
top_circ_orig = f.cartesian_point((0.0, 0.0, H))
top_circ_plc  = f.axis2_placement_3d(top_circ_orig, cyl_zdir, cyl_xdir)
top_circ      = f._emit_raw(f"CIRCLE('',#{top_circ_plc.eid},{R})")
# Pcurve: u: 0→2pi at v=H
pc_top = _pcurve_2d(cyl_surf, 0.0, H, 1.0, 0.0, 2.0*_math.pi)
top_sc = f._emit_raw(
    f"SURFACE_CURVE('',#{top_circ.eid},(#{pc_top.eid}),.PCURVE_S1.)"
)
top_edge = f._emit_raw(
    f"EDGE_CURVE('',#{v_top.eid},#{v_top.eid},#{top_sc.eid},.T.)"
)
oe_top = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{top_edge.eid},.T.)")

# -- E2: seam lateral from v_top back to v_bot (reversed) --------------------
# Use same seam_edge with orientation=.F. (reverse the seam edge)
oe_seam_dn = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{seam_edge.eid},.F.)")

# -- E3: bottom full circle from v_bot back to v_bot -------------------------
bot_circ_orig = f.cartesian_point((0.0, 0.0, 0.0))
bot_circ_plc  = f.axis2_placement_3d(bot_circ_orig, cyl_zdir, cyl_xdir)
bot_circ      = f._emit_raw(f"CIRCLE('',#{bot_circ_plc.eid},{R})")
# Pcurve: u: 0→-2pi (reversed, going CW) at v=0 — complement direction
pc_bot = _pcurve_2d(cyl_surf, 0.0, 0.0, -1.0, 0.0, 2.0*_math.pi)
bot_sc = f._emit_raw(
    f"SURFACE_CURVE('',#{bot_circ.eid},(#{pc_bot.eid}),.PCURVE_S1.)"
)
bot_edge = f._emit_raw(
    f"EDGE_CURVE('',#{v_bot.eid},#{v_bot.eid},#{bot_sc.eid},.T.)"
)
oe_bot = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{bot_edge.eid},.T.)")

# -- EDGE_LOOP -----------------------------------------------------------------
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_seam_up.eid},#{oe_top.eid},#{oe_seam_dn.eid},#{oe_bot.eid}))"
)
fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{cyl_surf.eid},.T.)")
shell = f._emit_raw(f"CLOSED_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi221.stp")
