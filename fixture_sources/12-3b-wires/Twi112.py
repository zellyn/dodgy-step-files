"""Twi112 — ShapeFix_Wire.FixGaps2d 2D-gap repair on cylindrical surface.

Catalog claim: Wire on cylindrical surface with consecutive edges' parametric
curves (pcurves) leaving a 2D gap in the parameter domain. First edge pcurve
ranges [0.0, 1.0], second edge pcurve starts at [1.01, ...], creating a 0.01-unit
discontinuity. FixGaps2d should bridge with a new pcurve segment to restore
continuity.

Mechanism IS a cylindrical ADVANCED_FACE (radius 1, height 5) whose outer 4-edge
EDGE_LOOP has all 3D curves correct and vertices connected, but E0's pcurve ends
at v=1.0 while E1's pcurve starts at v=1.01 — a 0.01-unit 2D gap in the
parameter domain's v-coordinate. The 3D geometry is consistent (same 3D point).
FixGaps2d detects the 2D discontinuity and bridges it.

Tier-3 assertion: load == "ok"
Expected: occt=shape(1)/shape(1)
"""
import math as _math
from step_corpus.step_builder import StepFile

R = 1.0
H = 5.0

f = StepFile(
    catalog_id="Twi112",
    defect=(
        "Single ADVANCED_FACE on a CYLINDRICAL_SURFACE (radius 1, height 5, axis +Z); "
        "outer EDGE_LOOP has 4 edges; 3D curves correct, vertices connected; "
        "E0 lateral (u=0, v:0→1.0): pcurve ends at v=1.0; "
        "E1 bottom arc (u:0→pi/2, v=1.01): pcurve starts at v=1.01 — "
        "0.01-unit 2D gap in v-parameter (E0 end v=1.0, E1 start v=1.01); "
        "3D junction is geometrically consistent (same 3D point (1,0,1.0)); "
        "ShapeFix_Wire.FixGaps2d detects parametric discontinuity and bridges it "
        "with a new pcurve segment IS mechanism; "
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

# ── Vertices ──────────────────────────────────────────────────────────────────
# We use a 4-edge loop: E0(lateral at theta=0), E1(arc at z_mid), E2(lateral at
# theta=pi/2), E3(arc at z=0).
# All 3D vertices are exactly on the cylinder surface.
z_mid = 1.0   # z height where the 2D gap occurs in v

v_A = f.vertex_point(f.cartesian_point((R,   0.0,  0.0)))    # theta=0, z=0
v_B = f.vertex_point(f.cartesian_point((R,   0.0,  z_mid)))  # theta=0, z=z_mid (3D exact)
v_C = f.vertex_point(f.cartesian_point((0.0, R,    z_mid)))  # theta=pi/2, z=z_mid
v_D = f.vertex_point(f.cartesian_point((0.0, R,    0.0)))    # theta=pi/2, z=0


def _pcurve_line(cyl, u_start, v_start, du, dv, length):
    mag = _math.sqrt(du * du + dv * dv)
    pc_orig   = f.cartesian_point((u_start, v_start))
    pc_dir2d  = f.direction((du / mag, dv / mag))
    pc_line2d = f.line(pc_orig, f.vector(pc_dir2d, length))
    pc_def_rep = f._emit_raw(
        f"DEFINITIONAL_REPRESENTATION('',(#{pc_line2d.eid}),#*)"
    )
    return f._emit_raw(f"PCURVE('',#{cyl.eid},#{pc_def_rep.eid})")


# ── E0: lateral vA(R,0,0)→vB(R,0,z_mid), u=0, v: 0→1.0 ─────────────────────
# 3D: correct vertical line from z=0 to z=z_mid=1.0
# pcurve: u=0, v: 0→1.0  (correct — ends at v=1.0)
lat0_3d = f.line(
    f.cartesian_point((R, 0.0, 0.0)),
    f.vector(f.direction((0.0, 0.0, 1.0)), z_mid),
)
pc0 = _pcurve_line(cyl_surf, 0.0, 0.0, 0.0, 1.0, z_mid)   # v: 0→1.0
e0_sc = f._emit_raw(
    f"SURFACE_CURVE('',#{lat0_3d.eid},(#{pc0.eid}),.PCURVE_S1.)"
)
e0  = f._emit_raw(f"EDGE_CURVE('',#{v_A.eid},#{v_B.eid},#{e0_sc.eid},.T.)")
oe0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e0.eid},.T.)")

# ── E1: arc vB(R,0,z_mid)→vC(0,R,z_mid), theta=0→pi/2, z=z_mid ─────────────
# 3D: correct arc at z=z_mid, theta 0→pi/2
# pcurve DEFECT: starts at v=1.01 instead of v=1.0 — 0.01-unit 2D gap!
arc1_plc_orig = f.cartesian_point((0.0, 0.0, z_mid))
arc1_plc_zdir = f.direction((0.0, 0.0, 1.0))
arc1_plc_xdir = f.direction((1.0, 0.0, 0.0))
arc1_plc    = f.axis2_placement_3d(arc1_plc_orig, arc1_plc_zdir, arc1_plc_xdir)
arc1_circle = f._emit_raw(f"CIRCLE('',#{arc1_plc.eid},{R})")
# Correct pcurve end would be at v=1.0 (same as E0 end); defective start is 1.01
pc1 = _pcurve_line(cyl_surf, 0.0, 1.01, _math.pi / 2, 0.0, _math.pi / 2)  # v_start=1.01 IS defect
e1_sc = f._emit_raw(
    f"SURFACE_CURVE('',#{arc1_circle.eid},(#{pc1.eid}),.PCURVE_S1.)"
)
e1  = f._emit_raw(f"EDGE_CURVE('',#{v_B.eid},#{v_C.eid},#{e1_sc.eid},.T.)")
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e1.eid},.T.)")

# ── E2: lateral vC(0,R,z_mid)→vD(0,R,0), u=pi/2, v: z_mid→0 ────────────────
lat2_3d = f.line(
    f.cartesian_point((0.0, R, z_mid)),
    f.vector(f.direction((0.0, 0.0, -1.0)), z_mid),
)
pc2 = _pcurve_line(cyl_surf, _math.pi / 2, z_mid, 0.0, -1.0, z_mid)
e2_sc = f._emit_raw(
    f"SURFACE_CURVE('',#{lat2_3d.eid},(#{pc2.eid}),.PCURVE_S1.)"
)
e2  = f._emit_raw(f"EDGE_CURVE('',#{v_C.eid},#{v_D.eid},#{e2_sc.eid},.T.)")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e2.eid},.T.)")

# ── E3: arc vD(0,R,0)→vA(R,0,0), theta=pi/2→0, z=0 ─────────────────────────
arc3_plc_orig = f.cartesian_point((0.0, 0.0, 0.0))
arc3_plc_zdir = f.direction((0.0, 0.0, 1.0))
arc3_plc_xdir = f.direction((1.0, 0.0, 0.0))
arc3_plc    = f.axis2_placement_3d(arc3_plc_orig, arc3_plc_zdir, arc3_plc_xdir)
arc3_circle = f._emit_raw(f"CIRCLE('',#{arc3_plc.eid},{R})")
pc3 = _pcurve_line(cyl_surf, _math.pi / 2, 0.0, -(_math.pi / 2), 0.0, _math.pi / 2)
e3_sc = f._emit_raw(
    f"SURFACE_CURVE('',#{arc3_circle.eid},(#{pc3.eid}),.PCURVE_S1.)"
)
e3  = f._emit_raw(f"EDGE_CURVE('',#{v_D.eid},#{v_A.eid},#{e3_sc.eid},.T.)")
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
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi112.stp")
