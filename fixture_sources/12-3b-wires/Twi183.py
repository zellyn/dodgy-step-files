"""Twi183 — ShapeAnalysis_Wire.CheckSeam non-cylindrical-seam.

Catalog claim: Wire on sphere (non-cylindrical closed surface); seam detection
heuristic doesn't generalize. Edges crossing meridian singularities on sphere
are not flagged as seams; downstream PCurve fixes are skipped.

Mechanism: SPHERICAL_SURFACE with radius 5 centered at origin. The sphere's
parameter domain is (u=longitude 0..2π, v=latitude -π/2..+π/2). A wire on the
sphere crosses the meridian seam (u=0/2π boundary) while travelling around the
equatorial belt. CheckSeam's heuristic was designed for cylindrical surfaces and
checks only the "seam edge" annotation; on a sphere the seam is implicit and the
heuristic misses it.

Wire layout — 4 edges forming a belt around the equator that crosses u=0:
  E0: arc at v=0.1 (near-equator), u: 5.0 → 2π  (approaching seam)
  E1: short lateral at u=2π=0, v: 0.1 → -0.1    (crossing the seam)
  E2: arc at v=-0.1, u: 0 → 1.0                 (departing seam)
  E3: lateral from v=-0.1 to v=0.1 at u=1.0     (close lateral)

In 3D:
  Sphere: x = R cos(v) cos(u), y = R cos(v) sin(u), z = R sin(v)
  R=5, using v≈0:
    At u=5.0: P_A ≈ (5*cos5, 5*sin5, 0) ≈ (1.418, -4.794, 0)
    At u=2π:  P_B = (5, 0, 0)  (u=0 seam)
    At u=0:   P_C = (5*cos(0)*cos(0), ...) same as P_B shifted in v
    At u=1.0: P_D ≈ (5*cos1, 5*sin1, 0) ≈ (2.702, 4.207, 0) wrong ...

Simpler: parametrize so the wire is clearly on the sphere and crosses the
longitude seam. Use SURFACE_CURVE+PCURVE to show the seam crossing.

Tier-3 assertion: n_faces_total == 1
Expected: occt=shape(1)/shape(1)
"""
import math as _math
from pathlib import Path as _Path
from step_corpus.step_builder import StepFile

R = 5.0  # sphere radius

f = StepFile(
    catalog_id="Twi183",
    defect=(
        "Single ADVANCED_FACE on SPHERICAL_SURFACE (radius 5) in CLOSED_SHELL; "
        "outer EDGE_LOOP 4 edges cross the meridian seam (u=0/2pi boundary); "
        "E0 arc at v=+0.1 from u=5.0 to u=2pi approaching the seam; "
        "E1 lateral at u=0/2pi from v=+0.1 to v=-0.1 crossing the seam meridian; "
        "E2 arc at v=-0.1 from u=0 to u=1.0 departing the seam; "
        "E3 lateral at u=1.0 from v=-0.1 to v=+0.1 closing the loop; "
        "CheckSeam heuristic designed for cylinder does not flag meridian edge "
        "on sphere as seam — downstream PCurve fix is skipped IS mechanism; "
        "EDGE_LOOP IS wired into FACE_OUTER_BOUND -> ADVANCED_FACE in "
        "CLOSED_SHELL — never orphaned"
    ),
)

# ── SPHERICAL_SURFACE: radius 5, centered at origin ───────────────────────────
sph_orig = f.cartesian_point((0.0, 0.0, 0.0))
sph_zdir = f.direction((0.0, 0.0, 1.0))
sph_xdir = f.direction((1.0, 0.0, 0.0))
sph_plc  = f.axis2_placement_3d(sph_orig, sph_zdir, sph_xdir)
sph_surf = f.spherical_surface(sph_plc, R)

# ── 3D point helper for sphere: x=R*cos(v)*cos(u), y=R*cos(v)*sin(u), z=R*sin(v)
def sphere_pt(u, v):
    return (R * _math.cos(v) * _math.cos(u),
            R * _math.cos(v) * _math.sin(u),
            R * _math.sin(v))

# Wire belt crossing the seam at u=2π=0:
#   P_A: u=5.0, v=+0.1
#   P_B: u=2π,  v=+0.1   (=u=0)
#   P_C: u=0,   v=-0.1   (same seam meridian, other latitude)
#   P_D: u=1.0, v=-0.1

u_A = 5.0
u_B = 2.0 * _math.pi   # ≡ 0 (seam)
u_C = 0.0
u_D = 1.0
v_pos = 0.1
v_neg = -0.1

PA = sphere_pt(u_A, v_pos)
PB = sphere_pt(u_B, v_pos)   # same 3D as u=0, v=+0.1
PC = sphere_pt(u_C, v_neg)   # u=0, v=-0.1
PD = sphere_pt(u_D, v_neg)

v_A = f.vertex_point(f.cartesian_point(PA))
v_B = f.vertex_point(f.cartesian_point(PB))
v_C = f.vertex_point(f.cartesian_point(PC))
v_D = f.vertex_point(f.cartesian_point(PD))


def _pcurve_line_sph(surf, u_start, v_start, du, dv, length):
    """2D line pcurve on the sphere parameter space."""
    pc_orig   = f.cartesian_point((u_start, v_start))
    mag = _math.sqrt(du * du + dv * dv)
    pc_dir2d  = f.direction((du / mag, dv / mag))
    pc_line2d = f.line(pc_orig, f.vector(pc_dir2d, length))
    pc_def    = f._emit_raw(
        f"DEFINITIONAL_REPRESENTATION('',(#{pc_line2d.eid}),#*)"
    )
    return f._emit_raw(f"PCURVE('',#{surf.eid},#{pc_def.eid})")


# ── E0: arc at v=+0.1 from PA (u=5.0) to PB (u=2π) ──────────────────────────
# 3D: small-circle arc at v=0.1, radius R*cos(0.1) ≈ 4.975
# Place the arc circle at z=R*sin(v_pos)
arc_r  = R * _math.cos(v_pos)
arc_z0 = R * _math.sin(v_pos)
arc0_orig = f.cartesian_point((0.0, 0.0, arc_z0))
arc0_zdir = f.direction((0.0, 0.0, 1.0))
arc0_xdir = f.direction((1.0, 0.0, 0.0))
arc0_plc  = f.axis2_placement_3d(arc0_orig, arc0_zdir, arc0_xdir)
arc0_circ = f._emit_raw(f"CIRCLE('',#{arc0_plc.eid},{arc_r})")
# pcurve: u from 5.0 to 2π (length = 2π-5.0 ≈ 1.283), v=v_pos constant
du_e0 = u_B - u_A   # ≈ 1.283
pc0 = _pcurve_line_sph(sph_surf, u_A, v_pos, 1.0, 0.0, du_e0)
e0_sc = f._emit_raw(
    f"SURFACE_CURVE('',#{arc0_circ.eid},(#{pc0.eid}),.PCURVE_S1.)"
)
e0  = f._emit_raw(f"EDGE_CURVE('',#{v_A.eid},#{v_B.eid},#{e0_sc.eid},.T.)")
oe0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e0.eid},.T.)")

# ── E1: lateral (meridian) at u=0/2π from PB (v=+0.1) to PC (v=-0.1) ─────────
# 3D: arc on the meridian circle (u=0: x=R*cos(v), y=0, z=R*sin(v))
# At u=0: x=R*cos(v), y=0; so this is an arc in the XZ plane.
# Circle centered at origin in XZ-plane, radius R=5, from theta=v_pos to v_neg.
# Meridian circle: center=(0,0,0), in XZ plane, axis=+Y
lat1_plc_orig = f.cartesian_point((0.0, 0.0, 0.0))
lat1_plc_zdir = f.direction((0.0, 1.0, 0.0))   # axis = +Y for meridian
lat1_plc_xdir = f.direction((1.0, 0.0, 0.0))
lat1_plc  = f.axis2_placement_3d(lat1_plc_orig, lat1_plc_zdir, lat1_plc_xdir)
lat1_circ = f._emit_raw(f"CIRCLE('',#{lat1_plc.eid},{R})")
# pcurve: u=0 constant (crossing the seam IS the defect), v: +0.1 → -0.1
dv_e1 = v_neg - v_pos  # = -0.2
pc1 = _pcurve_line_sph(sph_surf, 0.0, v_pos, 0.0, -1.0, abs(dv_e1))
e1_sc = f._emit_raw(
    f"SURFACE_CURVE('',#{lat1_circ.eid},(#{pc1.eid}),.PCURVE_S1.)"
)
e1  = f._emit_raw(f"EDGE_CURVE('',#{v_B.eid},#{v_C.eid},#{e1_sc.eid},.T.)")
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e1.eid},.T.)")

# ── E2: arc at v=-0.1 from PC (u=0) to PD (u=1.0) ───────────────────────────
arc_r2  = R * _math.cos(v_neg)
arc_z2  = R * _math.sin(v_neg)
arc2_orig = f.cartesian_point((0.0, 0.0, arc_z2))
arc2_zdir = f.direction((0.0, 0.0, 1.0))
arc2_xdir = f.direction((1.0, 0.0, 0.0))
arc2_plc  = f.axis2_placement_3d(arc2_orig, arc2_zdir, arc2_xdir)
arc2_circ = f._emit_raw(f"CIRCLE('',#{arc2_plc.eid},{arc_r2})")
# pcurve: u from 0 to 1.0, v=v_neg constant
pc2 = _pcurve_line_sph(sph_surf, 0.0, v_neg, 1.0, 0.0, 1.0)
e2_sc = f._emit_raw(
    f"SURFACE_CURVE('',#{arc2_circ.eid},(#{pc2.eid}),.PCURVE_S1.)"
)
e2  = f._emit_raw(f"EDGE_CURVE('',#{v_C.eid},#{v_D.eid},#{e2_sc.eid},.T.)")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e2.eid},.T.)")

# ── E3: lateral at u=1.0 from PD (v=-0.1) to PA (v=+0.1) ────────────────────
# 3D: arc on the meridian at u=1.0
# At u=1.0: x=R*cos(v)*cos(1), y=R*cos(v)*sin(1), z=R*sin(v)
# Meridian circle at u=1.0: center=(0,0,0), radius R, axis=(sin1,-cos1,0)
# Simpler: use a B-spline line approximation or just a 3D line between the pts
# (for latitudinal variation of 0.2 the surface is nearly flat in v, so a
# straight-line 3D approximation is acceptable for the defect demonstration).
lat3_3d = f.line(
    f.cartesian_point(PD),
    f.vector(
        f.direction((
            (PA[0] - PD[0]) / _math.dist(PA, PD),
            (PA[1] - PD[1]) / _math.dist(PA, PD),
            (PA[2] - PD[2]) / _math.dist(PA, PD),
        )),
        _math.dist(PA, PD),
    ),
)
# pcurve: u=1.0 constant, v: -0.1 → +0.1
pc3 = _pcurve_line_sph(sph_surf, u_D, v_neg, 0.0, 1.0, abs(v_pos - v_neg))
e3_sc = f._emit_raw(
    f"SURFACE_CURVE('',#{lat3_3d.eid},(#{pc3.eid}),.PCURVE_S1.)"
)
e3  = f._emit_raw(f"EDGE_CURVE('',#{v_D.eid},#{v_A.eid},#{e3_sc.eid},.T.)")
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e3.eid},.T.)")

# ── EDGE_LOOP ─────────────────────────────────────────────────────────────────
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe0.eid},#{oe1.eid},#{oe2.eid},#{oe3.eid}))"
)
fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{sph_surf.eid},.T.)")
shell = f._emit_raw(f"CLOSED_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi183.stp")
