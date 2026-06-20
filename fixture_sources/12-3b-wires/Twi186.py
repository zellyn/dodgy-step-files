"""Twi186 — ShapeFix_Wire.FixIntersectingEdges parametric-overlap.

Catalog claim: Two edges with overlapping parametric ranges on torus but no 3D
intersection; 2D analysis produces false split.

Mechanism: TOROIDAL_SURFACE (major R=5, minor r=2) with parameter domain
(u=0..2π longitude, v=0..2π tube-angle). The wire has 4 edges forming a closed
loop on the torus surface. Two edges E0 and E2 both run in the u-direction at
different v-values, but their u-parameter ranges overlap: E0 has u∈[0.3, 1.8]
and E2 has u∈[0.3, 1.8] (same u-range, different v-level). In 3D the edges are
on different latitude circles of the tube and don't intersect; but
FixIntersectingEdges' 2D parametric test sees their u-parameter projections
overlap and incorrectly flags a "phantom" intersection, then splits one edge.

Wire layout (4 edges on torus):
  P_A: u=0.3, v=0.1    → 3D point on torus
  P_B: u=1.8, v=0.1    → 3D point on torus
  P_C: u=1.8, v=1.0    → 3D point on torus
  P_D: u=0.3, v=1.0    → 3D point on torus

  E0: arc at v=0.1 from P_A to P_B  (u: 0.3→1.8)
  E1: arc at u=1.8 from P_B to P_C  (v: 0.1→1.0)
  E2: arc at v=1.0 from P_C to P_D  (u: 1.8→0.3, traversed backwards)
  E3: arc at u=0.3 from P_D to P_A  (v: 1.0→0.1)

E0 (u: 0.3→1.8) and E2 (u: 1.8→0.3 = reversed, same u-range) share the same
u-parameter range. FixIntersectingEdges 2D overlap test fires because both
edges span u∈[0.3,1.8]. In 3D they are at v=0.1 vs v=1.0 on the tube — no
actual 3D intersection.

Tier-3 assertion: n_faces_total == 1
Expected: occt=shape(1)/shape(1)
"""
import math as _math
from pathlib import Path as _Path
from step_corpus.step_builder import StepFile

R_maj = 5.0   # torus major radius
R_min = 2.0   # torus minor radius

f = StepFile(
    catalog_id="Twi186",
    defect=(
        "Single ADVANCED_FACE on TOROIDAL_SURFACE (major R=5, minor r=2) in "
        "CLOSED_SHELL; outer EDGE_LOOP has 4 edges forming a rectangular patch "
        "in parameter space; E0 (u:0.3→1.8, v=0.1) and E2 (u:1.8→0.3, v=1.0) "
        "have the same u-parameter range — overlapping parametric projections; "
        "in 3D they are on different tube latitudes (v=0.1 vs v=1.0) and never "
        "intersect; FixIntersectingEdges 2D test fires on u-range overlap and "
        "creates false split at phantom 3D intersection IS mechanism; "
        "EDGE_LOOP IS wired into FACE_OUTER_BOUND -> ADVANCED_FACE in "
        "CLOSED_SHELL — never orphaned"
    ),
)

# ── TOROIDAL_SURFACE: major R=5, minor r=2, axis +Z ──────────────────────────
tor_orig = f.cartesian_point((0.0, 0.0, 0.0))
tor_zdir = f.direction((0.0, 0.0, 1.0))
tor_xdir = f.direction((1.0, 0.0, 0.0))
tor_plc  = f.axis2_placement_3d(tor_orig, tor_zdir, tor_xdir)
tor_surf = f.toroidal_surface(tor_plc, R_maj, R_min)

# 3D point on torus: x=(R+r*cos(v))*cos(u), y=(R+r*cos(v))*sin(u), z=r*sin(v)
def torus_pt(u, v):
    rho = R_maj + R_min * _math.cos(v)
    return (rho * _math.cos(u), rho * _math.sin(u), R_min * _math.sin(v))

u_lo = 0.3
u_hi = 1.8
v_lo = 0.1
v_hi = 1.0

PA = torus_pt(u_lo, v_lo)
PB = torus_pt(u_hi, v_lo)
PC = torus_pt(u_hi, v_hi)
PD = torus_pt(u_lo, v_hi)

v_A = f.vertex_point(f.cartesian_point(PA))
v_B = f.vertex_point(f.cartesian_point(PB))
v_C = f.vertex_point(f.cartesian_point(PC))
v_D = f.vertex_point(f.cartesian_point(PD))


def _pcurve_line(surf, u_start, v_start, du, dv, length):
    """Emit a 2D line PCURVE in the surface parameter space."""
    pc_orig  = f.cartesian_point((u_start, v_start))
    mag = _math.sqrt(du * du + dv * dv)
    pc_dir   = f.direction((du / mag, dv / mag))
    pc_line  = f.line(pc_orig, f.vector(pc_dir, length))
    pc_def   = f._emit_raw(
        f"DEFINITIONAL_REPRESENTATION('',(#{pc_line.eid}),#*)"
    )
    return f._emit_raw(f"PCURVE('',#{surf.eid},#{pc_def.eid})")


# ── E0: tube-latitude arc at v=v_lo from PA to PB (u: u_lo → u_hi) ───────────
# 3D: circle of radius (R_maj + R_min*cos(v_lo)) in XY plane at z=R_min*sin(v_lo)
rho_lo = R_maj + R_min * _math.cos(v_lo)
z_lo   = R_min * _math.sin(v_lo)
arc0_orig = f.cartesian_point((0.0, 0.0, z_lo))
arc0_zdir = f.direction((0.0, 0.0, 1.0))
arc0_xdir = f.direction((1.0, 0.0, 0.0))
arc0_plc  = f.axis2_placement_3d(arc0_orig, arc0_zdir, arc0_xdir)
arc0_circ = f._emit_raw(f"CIRCLE('',#{arc0_plc.eid},{rho_lo})")
# pcurve: u from u_lo to u_hi, v=v_lo constant
du_e0 = u_hi - u_lo
pc0 = _pcurve_line(tor_surf, u_lo, v_lo, 1.0, 0.0, du_e0)
e0_sc = f._emit_raw(
    f"SURFACE_CURVE('',#{arc0_circ.eid},(#{pc0.eid}),.PCURVE_S1.)"
)
e0  = f._emit_raw(f"EDGE_CURVE('',#{v_A.eid},#{v_B.eid},#{e0_sc.eid},.T.)")
oe0 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e0.eid},.T.)")

# ── E1: tube-circle arc at u=u_hi from PB to PC (v: v_lo → v_hi) ─────────────
# 3D: circle of radius R_min around the tube cross-section at longitude u_hi
# Circle center at (R_maj*cos(u_hi), R_maj*sin(u_hi), 0), in the radial plane.
# Outward direction at u_hi: (cos(u_hi), sin(u_hi), 0)
# Axis of tube circle = tangent to major circle = (-sin(u_hi), cos(u_hi), 0)
cx1 = R_maj * _math.cos(u_hi)
cy1 = R_maj * _math.sin(u_hi)
arc1_orig = f.cartesian_point((cx1, cy1, 0.0))
# Axis of tube circle is perpendicular to major circle tangent and to radial:
# outward = (cos u, sin u, 0); tube axis = tangent = (-sin u, cos u, 0)
# ref_dir for the tube arc = outward direction
arc1_zdir = f.direction((-_math.sin(u_hi), _math.cos(u_hi), 0.0))
arc1_xdir = f.direction((_math.cos(u_hi),   _math.sin(u_hi), 0.0))
arc1_plc  = f.axis2_placement_3d(arc1_orig, arc1_zdir, arc1_xdir)
arc1_circ = f._emit_raw(f"CIRCLE('',#{arc1_plc.eid},{R_min})")
# pcurve: u=u_hi constant, v from v_lo to v_hi
dv_e1 = v_hi - v_lo
pc1 = _pcurve_line(tor_surf, u_hi, v_lo, 0.0, 1.0, dv_e1)
e1_sc = f._emit_raw(
    f"SURFACE_CURVE('',#{arc1_circ.eid},(#{pc1.eid}),.PCURVE_S1.)"
)
e1  = f._emit_raw(f"EDGE_CURVE('',#{v_B.eid},#{v_C.eid},#{e1_sc.eid},.T.)")
oe1 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e1.eid},.T.)")

# ── E2: tube-latitude arc at v=v_hi from PC to PD (u: u_hi → u_lo) ───────────
# Same u-range as E0 but at different v; IS the parametric-overlap defect.
rho_hi = R_maj + R_min * _math.cos(v_hi)
z_hi   = R_min * _math.sin(v_hi)
arc2_orig = f.cartesian_point((0.0, 0.0, z_hi))
arc2_zdir = f.direction((0.0, 0.0, 1.0))
arc2_xdir = f.direction((1.0, 0.0, 0.0))
arc2_plc  = f.axis2_placement_3d(arc2_orig, arc2_zdir, arc2_xdir)
arc2_circ = f._emit_raw(f"CIRCLE('',#{arc2_plc.eid},{rho_hi})")
# pcurve: u from u_hi to u_lo (negative direction), v=v_hi constant
du_e2 = u_hi - u_lo   # length of arc (positive); direction is -u
pc2 = _pcurve_line(tor_surf, u_hi, v_hi, -1.0, 0.0, du_e2)
e2_sc = f._emit_raw(
    f"SURFACE_CURVE('',#{arc2_circ.eid},(#{pc2.eid}),.PCURVE_S1.)"
)
e2  = f._emit_raw(f"EDGE_CURVE('',#{v_C.eid},#{v_D.eid},#{e2_sc.eid},.T.)")
oe2 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e2.eid},.T.)")

# ── E3: tube-circle arc at u=u_lo from PD to PA (v: v_hi → v_lo) ─────────────
cx3 = R_maj * _math.cos(u_lo)
cy3 = R_maj * _math.sin(u_lo)
arc3_orig = f.cartesian_point((cx3, cy3, 0.0))
arc3_zdir = f.direction((-_math.sin(u_lo), _math.cos(u_lo), 0.0))
arc3_xdir = f.direction((_math.cos(u_lo),   _math.sin(u_lo), 0.0))
arc3_plc  = f.axis2_placement_3d(arc3_orig, arc3_zdir, arc3_xdir)
arc3_circ = f._emit_raw(f"CIRCLE('',#{arc3_plc.eid},{R_min})")
# pcurve: u=u_lo constant, v from v_hi to v_lo (negative direction)
dv_e3 = v_hi - v_lo   # length; direction is -v
pc3 = _pcurve_line(tor_surf, u_lo, v_hi, 0.0, -1.0, dv_e3)
e3_sc = f._emit_raw(
    f"SURFACE_CURVE('',#{arc3_circ.eid},(#{pc3.eid}),.PCURVE_S1.)"
)
e3  = f._emit_raw(f"EDGE_CURVE('',#{v_D.eid},#{v_A.eid},#{e3_sc.eid},.T.)")
oe3 = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{e3.eid},.T.)")

# ── EDGE_LOOP ─────────────────────────────────────────────────────────────────
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe0.eid},#{oe1.eid},#{oe2.eid},#{oe3.eid}))"
)
fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{tor_surf.eid},.T.)")
shell = f._emit_raw(f"CLOSED_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi186.stp")
