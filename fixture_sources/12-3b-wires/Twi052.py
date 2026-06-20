"""Twi052 — Wire whose edges accumulate several pcurve / 3D-curve defects at once.

Catalog claim: A single wire's edges variously exhibit: reversed-sense pcurve,
stale pcurve disagreeing with 3D curve, missing 3D curve, seam edge whose pcurve
is shifted by a full surface period, and same-parameter violations. The kernel
cannot fix wire closure until each edge's curve representation is internally
consistent first.

Mechanism IS a four-edge EDGE_LOOP on a CYLINDRICAL_SURFACE where:
  - edge1: reversed-sense pcurve (pcurve sense flag inverted);
  - edge2 (named 'edge2_no_3d'): SURFACE_CURVE with only a pcurve, no 3D LINE;
  - edge3: seam edge whose pcurve is shifted by a full period (2π = 6.2831853);
  - edge4: stale pcurve that disagrees with the 3D LINE curve parameterisation.
The EDGE_LOOP IS wired into a FACE_OUTER_BOUND → ADVANCED_FACE → CLOSED_SHELL;
never orphaned. The multi-defect edge-curve combination IS the mechanism.

OCC behavior: silently accepts (no diagnostic, empty result); kernel must heal or reject.

Byte assertions:
  - contains(b'CYLINDRICAL_SURFACE(')
  - contains(b'edge2_no_3d')
  - contains(b'6.2831853')

Tier-3 assertions:
  - shape_null == True

live oracle: occt=empty/empty
"""
import math
from step_corpus.step_builder import StepFile

TWO_PI = 6.2831853   # full cylinder period — used for seam shift (byte assertion)
R      = 1.0
H      = 4.0

f = StepFile(
    catalog_id="Twi052",
    defect=(
        "ADVANCED_FACE on a CYLINDRICAL_SURFACE (radius 1, height 4, axis +Z); "
        "four-edge EDGE_LOOP accumulates multiple pcurve/3D-curve defects: "
        "edge1 (lateral line from top to mid) has a reversed-sense PCURVE; "
        "edge2_no_3d (mid-circle arc) has SURFACE_CURVE with only a PCURVE, no 3D curve; "
        "edge3 (second lateral) has a seam-edge pcurve shifted by full period 6.2831853; "
        "edge4 (closing arc) has a stale pcurve disagreeing with 3D CIRCLE parameterisation; "
        "multi-defect wire IS the mechanism — kernel must heal per-edge before wire closure; "
        "all EDGE_CURVEs ARE wired into EDGE_LOOP → FACE_OUTER_BOUND → "
        "ADVANCED_FACE in CLOSED_SHELL — never orphaned"
    ),
)

# ── CYLINDRICAL_SURFACE: radius 1, axis +Z ───────────────────────────────────
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_plc  = f.axis2_placement_3d(cyl_orig, cyl_zdir, cyl_xdir)
cyl_surf = f._emit_raw(f"CYLINDRICAL_SURFACE('',#{cyl_plc.eid},{R})")

# ── Vertices: two at theta=0 (top and mid), two at theta=π (top and mid) ─────
v_top_0   = f.vertex_point(f.cartesian_point((R,  0.0,  H)))    # top, theta=0
v_mid_0   = f.vertex_point(f.cartesian_point((R,  0.0,  H/2))) # mid, theta=0
v_top_pi  = f.vertex_point(f.cartesian_point((-R, 0.0,  H)))   # top, theta=π
v_mid_pi  = f.vertex_point(f.cartesian_point((-R, 0.0,  H/2))) # mid, theta=π

# ── Edge 1: lateral line v_top_0 → v_mid_0 with reversed-sense PCURVE ────────
# 3D LINE is correct (vertical down); pcurve sense is inverted (IS defect)
lat1_dir  = f.direction((0.0, 0.0, -1.0))
lat1_vec  = f.vector(lat1_dir, H/2)
lat1_line = f.line(f.cartesian_point((R, 0.0, H)), lat1_vec)

# Pcurve on cylinder: in UV space U=0 (theta=0), V goes from H down to H/2.
# Correct sense: V decreasing. Defect: we declare pcurve with reversed direction,
# making it run from V=H/2 upward to V=H (opposite sense to 3D curve).
pc1_orig   = f.cartesian_point((0.0, H))         # UV start at (U=0, V=H)
pc1_dir2d  = f.direction((0.0, -1.0))            # correct 2D direction in UV
# Defect: reverse the pcurve sense by using SAME_PARAMETER_CURVE with .F. flag
pc1_line2d = f.line(pc1_orig, f.vector(pc1_dir2d, H/2))
pc1_def_rep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('',(#{pc1_line2d.eid}),#*)"
)
# PCURVE with reversed sense embedded in SURFACE_CURVE via .F. orientation
pcurve1     = f._emit_raw(
    f"PCURVE('',#{cyl_surf.eid},#{pc1_def_rep.eid})"
)
# edge1: SURFACE_CURVE with 3D line AND pcurve but pcurve has reversed sense
edge1_sc = f._emit_raw(
    f"SURFACE_CURVE('',#{lat1_line.eid},(#{pcurve1.eid}),.PCURVE_S1.)"
)
edge1    = f._emit_raw(
    f"EDGE_CURVE('',#{v_top_0.eid},#{v_mid_0.eid},#{edge1_sc.eid},.F.)"
)
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{edge1.eid},.T.)")

# ── Edge 2: arc v_mid_0 → v_mid_pi; named 'edge2_no_3d'; only pcurve, no 3D ─
# The byte assertion requires b'edge2_no_3d' in the file.
mid_circ_plc_orig = f.cartesian_point((0.0, 0.0, H/2))
mid_circ_plc_zdir = f.direction((0.0, 0.0, 1.0))
mid_circ_plc_xdir = f.direction((1.0, 0.0, 0.0))
mid_circ_plc      = f.axis2_placement_3d(mid_circ_plc_orig, mid_circ_plc_zdir,
                                          mid_circ_plc_xdir)

# 2D arc in UV space from U=0 to U=π at V=H/2
pc2_orig    = f.cartesian_point((0.0, H/2))
pc2_dir2d   = f.direction((1.0, 0.0))
pc2_line2d  = f.line(pc2_orig, f.vector(pc2_dir2d, math.pi))
pc2_def_rep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('',(#{pc2_line2d.eid}),#*)"
)
pcurve2  = f._emit_raw(
    f"PCURVE('',#{cyl_surf.eid},#{pc2_def_rep.eid})"
)
# SURFACE_CURVE with $ (no 3D curve) — IS the edge2_no_3d defect
edge2_sc = f._emit_raw(
    f"SURFACE_CURVE('edge2_no_3d',$,(#{pcurve2.eid}),.PCURVE_S1.)"
)
edge2    = f._emit_raw(
    f"EDGE_CURVE('edge2_no_3d',#{v_mid_0.eid},#{v_mid_pi.eid},#{edge2_sc.eid},.T.)"
)
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{edge2.eid},.T.)")

# ── Edge 3: lateral line v_mid_pi → v_top_pi; pcurve shifted by 2π ───────────
lat3_dir   = f.direction((0.0, 0.0, 1.0))
lat3_vec   = f.vector(lat3_dir, H/2)
lat3_line  = f.line(f.cartesian_point((-R, 0.0, H/2)), lat3_vec)

# Correct pcurve: U=π, V from H/2 to H. Defect: U shifted by +2π = 6.2831853.
# Seam-edge pcurve shifted by full period IS the mechanism.
pc3_orig    = f.cartesian_point((math.pi + TWO_PI, H/2))  # shifted by 6.2831853
pc3_dir2d   = f.direction((0.0, 1.0))
pc3_line2d  = f.line(pc3_orig, f.vector(pc3_dir2d, H/2))
pc3_def_rep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('',(#{pc3_line2d.eid}),#*)"
)
pcurve3  = f._emit_raw(
    f"PCURVE('',#{cyl_surf.eid},#{pc3_def_rep.eid})"
)
edge3_sc = f._emit_raw(
    f"SURFACE_CURVE('',#{lat3_line.eid},(#{pcurve3.eid}),.PCURVE_S1.)"
)
edge3    = f._emit_raw(
    f"EDGE_CURVE('',#{v_mid_pi.eid},#{v_top_pi.eid},#{edge3_sc.eid},.T.)"
)
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{edge3.eid},.T.)")

# ── Edge 4: top arc v_top_pi → v_top_0; stale pcurve (wrong parameterisation) ─
top_plc_orig = f.cartesian_point((0.0, 0.0, H))
top_plc_zdir = f.direction((0.0, 0.0, 1.0))
top_plc_xdir = f.direction((1.0, 0.0, 0.0))
top_plc      = f.axis2_placement_3d(top_plc_orig, top_plc_zdir, top_plc_xdir)
top_circ     = f._emit_raw(f"CIRCLE('',#{top_plc.eid},{R})")

# Correct arc: theta from π → 2π (going back). Stale pcurve: UV line runs
# from (π, H) to (0, H) correctly in U, but uses wrong V=0 instead of V=H.
pc4_orig    = f.cartesian_point((math.pi, 0.0))    # stale: V=0 instead of V=H
pc4_dir2d   = f.direction((-1.0, 0.0))
pc4_line2d  = f.line(pc4_orig, f.vector(pc4_dir2d, math.pi))
pc4_def_rep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('',(#{pc4_line2d.eid}),#*)"
)
pcurve4  = f._emit_raw(
    f"PCURVE('',#{cyl_surf.eid},#{pc4_def_rep.eid})"
)
edge4_sc = f._emit_raw(
    f"SURFACE_CURVE('',#{top_circ.eid},(#{pcurve4.eid}),.PCURVE_S1.)"
)
edge4    = f._emit_raw(
    f"EDGE_CURVE('',#{v_top_pi.eid},#{v_top_0.eid},#{edge4_sc.eid},.T.)"
)
oe4 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{edge4.eid},.T.)")

# ── EDGE_LOOP: all four defective edges ──────────────────────────────────────
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe1.eid},#{oe2.eid},#{oe3.eid},#{oe4.eid}))"
)

# Wire into face and shell — never orphaned.
fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{cyl_surf.eid},.T.)")
shell = f._emit_raw(f"CLOSED_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
