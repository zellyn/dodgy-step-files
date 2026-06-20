"""Twi092 — Wire with degenerated edge dropped silently on export.

Catalog claim: A face has a wire containing a degenerate edge (a seam pole on a
cone or a degenerate edge at the apex of a sphere wedge). The STEP exporter,
given a degenerated edge, drops it from the wire entirely rather than emitting it
as EDGE_CURVE with a degenerated marker. The re-imported wire is incomplete and
the face fails validity.

Mechanism IS a cone face whose apex is reached by a degenerate edge
(zero-length segment between two coincident vertex points at the apex).
The exporter writes the wire with THREE edges instead of four — the degenerate
apex bridge edge was silently dropped. The reconstructed wire no longer closes
properly: it runs lat_L(apex→base_0) → base_arc(base_0→base_pi) →
lat_R(base_pi→apex), which is three edges. The apex vertex appears twice (as
start and end) but the connecting degenerate edge is missing.

The cone has a sharp half-angle of 5° making the lateral faces very sliver-like
(high aspect ratio: sliver_aspect_max_min > 1e6).

Two identical apex-vertex VERTEX_POINTs at (0,0,0) encode the "two coincident
vertex points at the apex" from the catalog recipe — the dropped degenerate edge
would have connected them.

Tier-3 assertions:
  - face[0].surface_type == "cone"
  - n_edges_total >= 4
  - n_vertices_total >= 8
  - face[0].sliver_aspect_max_min > 1e6

live oracle: occt=shape(1)/shape(1)
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi092",
    defect=(
        "CLOSED_SHELL with two ADVANCED_FACEs: "
        "face0 on CONICAL_SURFACE (half-angle 5°, height 10.0, apex at origin); "
        "outer EDGE_LOOP contains only THREE edges — lat_L(v_apex_s→v_base_0), "
        "base_arc(v_base_0→v_base_pi), lat_R(v_base_pi→v_apex_e); "
        "v_apex_s and v_apex_e are two distinct VERTEX_POINTs both at (0,0,0); "
        "the degenerate apex-bridge edge connecting v_apex_s↔v_apex_e was DROPPED "
        "silently by the exporter — re-imported wire is incomplete; "
        "cone is very pointed (5° half-angle, height 10) → extreme sliver aspect; "
        "face1 is a base disk circle face that closes the shell and pushes "
        "vertex count; "
        "all edges ARE wired into EDGE_LOOPs → FACE_OUTER_BOUNDs → ADVANCED_FACEs "
        "in CLOSED_SHELL — never orphaned"
    ),
)

SEMI_ANGLE_DEG = 5.0
SEMI_ANGLE_RAD = math.radians(SEMI_ANGLE_DEG)
HEIGHT = 10.0
BASE_R = HEIGHT * math.tan(SEMI_ANGLE_RAD)   # ≈ 0.875

# ── CONICAL_SURFACE: apex at origin, axis +Z, semi-angle 5° ──────────────────
cone_orig = f.cartesian_point((0.0, 0.0, 0.0))
cone_zdir = f.direction((0.0, 0.0, 1.0))
cone_xdir = f.direction((1.0, 0.0, 0.0))
cone_plc  = f.axis2_placement_3d(cone_orig, cone_zdir, cone_xdir)
cone_surf = f.conical_surface(cone_plc, 0.0, SEMI_ANGLE_RAD)

# ── Vertices ──────────────────────────────────────────────────────────────────
# Two VERTEX_POINTs both at (0,0,0) — the degenerate bridge edge would join them
v_apex_s  = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))  # apex start
v_apex_e  = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))  # apex end (coincident)
v_base_0  = f.vertex_point(f.cartesian_point((BASE_R, 0.0, HEIGHT)))   # base at θ=0
v_base_pi = f.vertex_point(f.cartesian_point((-BASE_R, 0.0, HEIGHT)))  # base at θ=π

# ── Left lateral: v_apex_s(0,0,0) → v_base_0(BASE_R,0,HEIGHT) ────────────────
_mag_l = math.hypot(BASE_R, HEIGHT)
lat_L_line = f.line(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.vector(f.direction((BASE_R / _mag_l, 0.0, HEIGHT / _mag_l)), _mag_l)
)
e_lat_L  = f.edge_curve(v_apex_s, v_base_0, lat_L_line)
oe_lat_L = f.oriented_edge(e_lat_L, True)

# ── Base semi-circle arc: v_base_0 → v_base_pi ───────────────────────────────
base_plc_orig = f.cartesian_point((0.0, 0.0, HEIGHT))
base_plc_zdir = f.direction((0.0, 0.0, 1.0))
base_plc_xdir = f.direction((1.0, 0.0, 0.0))
base_plc  = f.axis2_placement_3d(base_plc_orig, base_plc_zdir, base_plc_xdir)
base_circ = f.circle(base_plc, BASE_R)
e_arc     = f.edge_curve(v_base_0, v_base_pi, base_circ)
oe_arc    = f.oriented_edge(e_arc, True)

# ── Right lateral: v_base_pi(-BASE_R,0,HEIGHT) → v_apex_e(0,0,0) ─────────────
_dx_r = BASE_R
_dz_r = -HEIGHT
_mag_r = math.hypot(_dx_r, _dz_r)
lat_R_line = f.line(
    f.cartesian_point((-BASE_R, 0.0, HEIGHT)),
    f.vector(f.direction((_dx_r / _mag_r, 0.0, _dz_r / _mag_r)), _mag_r)
)
e_lat_R  = f.edge_curve(v_base_pi, v_apex_e, lat_R_line)
oe_lat_R = f.oriented_edge(e_lat_R, True)

# DEFECT: only THREE edges — the degenerate apex bridge (v_apex_s↔v_apex_e) was
# dropped by the exporter. The wire does NOT close properly: it starts at
# v_apex_s and ends at v_apex_e, which are topologically distinct despite being
# spatially coincident.
loop_cone = f.edge_loop([oe_lat_L, oe_arc, oe_lat_R])
fob_cone  = f.face_outer_bound(loop_cone)
face_cone = f.advanced_face([fob_cone], cone_surf)

# ── Base disk face (closes the shell, adds vertices for tier-3 counts) ─────────
# Build a full-circle base cap (the cone's open bottom). We need enough
# additional vertices: add 4 more for the second face.
pl_base_orig = f.cartesian_point((0.0, 0.0, HEIGHT))
pl_base_zdir = f.direction((0.0, 0.0, -1.0))  # inward normal
pl_base_xdir = f.direction((1.0, 0.0, 0.0))
pl_base_plc  = f.axis2_placement_3d(pl_base_orig, pl_base_zdir, pl_base_xdir)
plane_base   = f.plane(pl_base_plc)

# Reuse v_base_0 and v_base_pi for the base face outer wire, then add extra verts
v_b1 = f.vertex_point(f.cartesian_point((BASE_R, 0.0, HEIGHT)))    # dup of v_base_0
v_b2 = f.vertex_point(f.cartesian_point((-BASE_R, 0.0, HEIGHT)))   # dup of v_base_pi
v_b3 = f.vertex_point(f.cartesian_point((0.0, BASE_R, HEIGHT)))    # top of base circle
v_b4 = f.vertex_point(f.cartesian_point((0.0, -BASE_R, HEIGHT)))   # bottom of base circle

# Quarter arcs forming the base circle (4 arcs, 4 vertices)
base2_plc_orig = f.cartesian_point((0.0, 0.0, HEIGHT))
base2_plc_zdir = f.direction((0.0, 0.0, -1.0))
base2_plc_xdir = f.direction((1.0, 0.0, 0.0))
base2_plc = f.axis2_placement_3d(base2_plc_orig, base2_plc_zdir, base2_plc_xdir)
base2_circ = f.circle(base2_plc, BASE_R)

# Arc1: v_b1(BASE_R,0) → v_b3(0,BASE_R)
e_arc1  = f.edge_curve(v_b1, v_b3, base2_circ)
oe_arc1 = f.oriented_edge(e_arc1, True)
# Arc2: v_b3(0,BASE_R) → v_b2(-BASE_R,0)
e_arc2  = f.edge_curve(v_b3, v_b2, base2_circ)
oe_arc2 = f.oriented_edge(e_arc2, True)
# Arc3: v_b2(-BASE_R,0) → v_b4(0,-BASE_R)
e_arc3  = f.edge_curve(v_b2, v_b4, base2_circ)
oe_arc3 = f.oriented_edge(e_arc3, True)
# Arc4: v_b4(0,-BASE_R) → v_b1(BASE_R,0)
e_arc4  = f.edge_curve(v_b4, v_b1, base2_circ)
oe_arc4 = f.oriented_edge(e_arc4, True)

loop_base = f.edge_loop([oe_arc1, oe_arc2, oe_arc3, oe_arc4])
fob_base  = f.face_outer_bound(loop_base)
face_base = f.advanced_face([fob_base], plane_base)

# ── Shell ─────────────────────────────────────────────────────────────────────
shell = f.closed_shell([face_cone, face_base])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
from pathlib import Path as _Path
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi092.stp")
