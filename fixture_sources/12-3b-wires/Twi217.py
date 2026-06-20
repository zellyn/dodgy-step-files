"""Twi217 — ShapeFix_Wire.FixSeam pcurve-direction-not-matching-3d.

Catalog claim: Seam edge where parametric curve direction (u-orientation)
differs from 3D curve direction. FixSeam corrects PCurve but the original
3D curve becomes orphaned/unreferenced.

Mechanism: A 4-edge EDGE_LOOP on a CYLINDRICAL_SURFACE. The seam edge (E0)
runs upward in 3D (z: 0 → H, same_sense=.T.) but its PCURVE is set up with
opposite u-orientation — the pcurve's 2D line points from (0, H) downward to
(0, 0) in UV space, antiparallel to what the edge traversal requires. This
u-orientation mismatch between the 3D curve and pcurve IS the defect.
FixSeam detects the mismatch and corrects the pcurve, but in doing so it
creates a new PCURVE and leaves the old LINE (used only for the old PCURVE's
DEFINITIONAL_REPRESENTATION) unreferenced — orphaned geometry IS the
secondary mechanism.

Wire on CYLINDRICAL_SURFACE (radius 1, height 2, axis +Z):
  Seam at u=0: 3D line along (1,0,0..2), pcurve at u=0 but V direction flipped.
  E0: seam lateral (0,H) → (0,0) in 3D — but pcurve goes v=H→0 (antiparallel)
  E1: top circle at z=H (full circle, v_top→v_top)
  Actually encode minimal: just E0 seam + surrounding rectangular patch.

Tier-3 assertion: load == "ok"
Expected: occt=shape(1)/shape(1)
"""
import math as _math
from pathlib import Path as _Path
from step_corpus.step_builder import StepFile

R = 1.0
H = 2.0
TWO_PI = 2.0 * _math.pi

f = StepFile(
    catalog_id="Twi217",
    defect=(
        "Single ADVANCED_FACE on CYLINDRICAL_SURFACE (radius 1, height 2) in "
        "CLOSED_SHELL; 4-edge EDGE_LOOP forming patch from u=0 to u=pi; "
        "seam edge E0 has 3D LINE going upward (z: 0->2, same_sense=T) but "
        "PCURVE 2D direction going downward in UV (v: H->0) — "
        "u-orientation of pcurve antiparallel to 3D curve IS the defect; "
        "FixSeam corrects pcurve but old 3D geometry becomes orphaned — "
        "orphaned 3D curve IS the secondary mechanism; "
        "EDGE_LOOP IS wired into FACE_OUTER_BOUND -> ADVANCED_FACE in "
        "CLOSED_SHELL — never orphaned"
    ),
)

# -- CYLINDRICAL_SURFACE: radius 1, height 2, axis +Z -------------------------
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_plc  = f.axis2_placement_3d(cyl_orig, cyl_zdir, cyl_xdir)
cyl_surf = f.cylindrical_surface(cyl_plc, R)

# Patch: u in [0, pi], v in [0, H]
# 3D corners:
#   v_bot_0  = (R, 0, 0)          at u=0,   z=0
#   v_top_0  = (R, 0, H)          at u=0,   z=H
#   v_bot_pi = (-R, 0, 0)         at u=pi,  z=0
#   v_top_pi = (-R, 0, H)         at u=pi,  z=H

v_bot_0  = f.vertex_point(f.cartesian_point((R,   0.0, 0.0)))
v_top_0  = f.vertex_point(f.cartesian_point((R,   0.0, H)))
v_bot_pi = f.vertex_point(f.cartesian_point((-R,  0.0, 0.0)))
v_top_pi = f.vertex_point(f.cartesian_point((-R,  0.0, H)))


def _pcurve_2d(surf, u0, v0, du, dv, length):
    """Build a PCURVE with a 2D LINE in UV space."""
    pc_orig = f.cartesian_point((u0, v0))
    mag = _math.sqrt(du*du + dv*dv)
    pc_dir  = f.direction((du/mag, dv/mag))
    pc_line = f.line(pc_orig, f.vector(pc_dir, length))
    pc_def  = f._emit_raw(
        f"DEFINITIONAL_REPRESENTATION('',(#{pc_line.eid}),#*)"
    )
    return f._emit_raw(f"PCURVE('',#{surf.eid},#{pc_def.eid})")


# -- E0: seam lateral at u=0, v_bot_0 -> v_top_0 (3D: z goes UP) --------------
# 3D LINE: from (R,0,0) going up to (R,0,H), same_sense=.T.
e0_3d  = f.line(
    f.cartesian_point((R, 0.0, 0.0)),
    f.vector(f.direction((0.0, 0.0, 1.0)), H),
)
# DEFECT: pcurve at u=0 with v going DOWNWARD (H → 0) — antiparallel to 3D curve
# 3D goes up (z: 0→H); pcurve should go v: 0→H; instead we write v: H→0
pc0 = _pcurve_2d(cyl_surf, 0.0, H, 0.0, -1.0, H)   # v: H→0 IS the defect
e0_sc = f._emit_raw(
    f"SURFACE_CURVE('',#{e0_3d.eid},(#{pc0.eid}),.PCURVE_S1.)"
)
e0  = f._emit_raw(f"EDGE_CURVE('',#{v_bot_0.eid},#{v_top_0.eid},#{e0_sc.eid},.T.)")
oe0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e0.eid},.T.)")

# -- E1: top arc at z=H, u: 0→pi (v_top_0 → v_top_pi) -----------------------
# 3D: half circle at z=H from (R,0,H) to (-R,0,H)
arc1_orig = f.cartesian_point((0.0, 0.0, H))
arc1_plc  = f.axis2_placement_3d(arc1_orig, cyl_zdir, cyl_xdir)
arc1_circ = f._emit_raw(f"CIRCLE('',#{arc1_plc.eid},{R})")
pc1 = _pcurve_2d(cyl_surf, 0.0, H, 1.0, 0.0, _math.pi)  # u: 0→pi at v=H
e1_sc = f._emit_raw(
    f"SURFACE_CURVE('',#{arc1_circ.eid},(#{pc1.eid}),.PCURVE_S1.)"
)
e1  = f._emit_raw(f"EDGE_CURVE('',#{v_top_0.eid},#{v_top_pi.eid},#{e1_sc.eid},.T.)")
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e1.eid},.T.)")

# -- E2: lateral at u=pi, v_top_pi -> v_bot_pi (3D: z goes DOWN) --------------
e2_3d = f.line(
    f.cartesian_point((-R, 0.0, H)),
    f.vector(f.direction((0.0, 0.0, -1.0)), H),
)
pc2 = _pcurve_2d(cyl_surf, _math.pi, H, 0.0, -1.0, H)  # u=pi, v: H→0
e2_sc = f._emit_raw(
    f"SURFACE_CURVE('',#{e2_3d.eid},(#{pc2.eid}),.PCURVE_S1.)"
)
e2  = f._emit_raw(f"EDGE_CURVE('',#{v_top_pi.eid},#{v_bot_pi.eid},#{e2_sc.eid},.T.)")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e2.eid},.T.)")

# -- E3: bottom arc at z=0, u: pi→0 (v_bot_pi → v_bot_0) --------------------
# 3D: half circle at z=0 from (-R,0,0) back to (R,0,0), traversed backward
arc3_orig = f.cartesian_point((0.0, 0.0, 0.0))
arc3_plc  = f.axis2_placement_3d(arc3_orig, cyl_zdir, cyl_xdir)
arc3_circ = f._emit_raw(f"CIRCLE('',#{arc3_plc.eid},{R})")
# pcurve: u from pi to 0 (going backward), v=0
pc3 = _pcurve_2d(cyl_surf, _math.pi, 0.0, -1.0, 0.0, _math.pi)
e3_sc = f._emit_raw(
    f"SURFACE_CURVE('',#{arc3_circ.eid},(#{pc3.eid}),.PCURVE_S1.)"
)
e3  = f._emit_raw(f"EDGE_CURVE('',#{v_bot_pi.eid},#{v_bot_0.eid},#{e3_sc.eid},.T.)")
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e3.eid},.T.)")

# -- EDGE_LOOP -----------------------------------------------------------------
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe0.eid},#{oe1.eid},#{oe2.eid},#{oe3.eid}))"
)
fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{cyl_surf.eid},.T.)")
shell = f._emit_raw(f"CLOSED_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi217.stp")
