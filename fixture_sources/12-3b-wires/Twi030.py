"""Twi030 — Degenerate edge re-encountered for multiple faces.

Catalog claim: A degenerate edge bridges a singular row shared by adjacent faces;
the translator processes it once per face, building it again with potentially
divergent vertex tolerance. A translator without a per-face entity cache creates
duplicate EDGE_CURVE instances instead of reusing the shared edge.

Mechanism IS the pair of EDGE_LOOP wires on two adjacent SPHERICAL_SURFACE faces
that each reference a separate (non-shared) EDGE_CURVE at the sphere pole: two
EDGE_CURVE entities are emitted at the exact same pole location instead of one.
Both pole EDGE_CURVEs ARE wired into their respective EDGE_LOOPs, FACE_OUTER_BOUNDs,
ADVANCED_FACEs, all in the same OPEN_SHELL; never orphaned.

Reproducer: Two ADVANCED_FACEs on a SPHERICAL_SURFACE each with a degenerate
pole edge; pole EDGE_CURVEs are distinct entities sharing the same geometry
instead of a single shared entity.

Byte assertions:
  - count_entity_def(b'SPHERICAL_SURFACE') == 1
  - count_entity_def(b'EDGE_LOOP') == 2

Tier-3 assertions:
  - face[0].surface_type == "sphere"
  - n_edges_total >= 4
  - face[1].surface_type == "sphere"
  - n_vertices_total >= 8

live oracle: occt=shape(1)/shape(1)
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi030",
    defect=(
        "OPEN_SHELL with two ADVANCED_FACEs on a single SPHERICAL_SURFACE "
        "(radius 1, centre at origin); "
        "face-0 (upper hemisphere, phi 0→90°) has its own degenerate EDGE_CURVE "
        "at the north pole (v_pole_A) in its EDGE_LOOP; "
        "face-1 (lower hemisphere, phi 90→180°, approaching south pole) has a "
        "second distinct degenerate EDGE_CURVE also at the north-pole location "
        "(v_pole_B) in its EDGE_LOOP; "
        "duplicate degenerate pole EDGE_CURVEs IS the mechanism — same geometry, "
        "separate entities with potentially divergent vertex tolerance; "
        "both EDGE_LOOPs ARE wired into FACE_OUTER_BOUNDs in two ADVANCED_FACEs in OPEN_SHELL; "
        "translator must cache and reuse the degenerate edge across adjacent faces"
    ),
)

# ── Single SPHERICAL_SURFACE ──────────────────────────────────────────────────
R = 1.0
sph_orig = f.cartesian_point((0.0, 0.0, 0.0))
sph_zdir = f.direction((0.0, 0.0, 1.0))
sph_xdir = f.direction((1.0, 0.0, 0.0))
sph_plc  = f.axis2_placement_3d(sph_orig, sph_zdir, sph_xdir)
sph_surf = f._emit_raw(
    f"SPHERICAL_SURFACE('',#{sph_plc.eid},{R})"
)

# ── Shared equator vertices at theta=0 and theta=π ───────────────────────────
v_eq_0  = f.vertex_point(f.cartesian_point((R, 0.0, 0.0)))
v_eq_pi = f.vertex_point(f.cartesian_point((-R, 0.0, 0.0)))

# ── Equator semi-circle shared between the two faces ─────────────────────────
eq_plc_orig = f.cartesian_point((0.0, 0.0, 0.0))
eq_plc_zdir = f.direction((0.0, 0.0, 1.0))
eq_plc_xdir = f.direction((1.0, 0.0, 0.0))
eq_plc  = f.axis2_placement_3d(eq_plc_orig, eq_plc_zdir, eq_plc_xdir)
eq_circ = f._emit_raw(f"CIRCLE('',#{eq_plc.eid},{R})")
eq_edge = f._emit_raw(
    f"EDGE_CURVE('',#{v_eq_0.eid},#{v_eq_pi.eid},#{eq_circ.eid},.T.)"
)

# ── North pole: two distinct VERTEX_POINTs (IS the defect — should be shared) ─
v_pole_A = f.vertex_point(f.cartesian_point((0.0, 0.0, R)))
v_pole_B = f.vertex_point(f.cartesian_point((0.0, 0.0, R)))

# ── Degenerate pole edge A (used by face-0): same vertex at both ends ─────────
pole_dir_A  = f.direction((1.0, 0.0, 0.0))
pole_vec_A  = f.vector(pole_dir_A, 0.0)
pole_line_A = f.line(f.cartesian_point((0.0, 0.0, R)), pole_vec_A)
pole_ec_A   = f._emit_raw(
    f"EDGE_CURVE('',#{v_pole_A.eid},#{v_pole_A.eid},#{pole_line_A.eid},.T.)"
)

# ── Degenerate pole edge B (used by face-1): DISTINCT entity, same geometry ──
pole_dir_B  = f.direction((1.0, 0.0, 0.0))
pole_vec_B  = f.vector(pole_dir_B, 0.0)
pole_line_B = f.line(f.cartesian_point((0.0, 0.0, R)), pole_vec_B)
pole_ec_B   = f._emit_raw(
    f"EDGE_CURVE('',#{v_pole_B.eid},#{v_pole_B.eid},#{pole_line_B.eid},.T.)"
)

# ── Meridian edges: two arcs from equator to north pole ───────────────────────
# Meridian from eq_0 (1,0,0) to north pole (0,0,1): quarter-circle in xz plane
mer_plc_0_orig = f.cartesian_point((0.0, 0.0, 0.0))
mer_plc_0_zdir = f.direction((0.0, -1.0, 0.0))   # normal of xz plane
mer_plc_0_xdir = f.direction((1.0, 0.0, 0.0))
mer_plc_0  = f.axis2_placement_3d(mer_plc_0_orig, mer_plc_0_zdir, mer_plc_0_xdir)
mer_circ_0 = f._emit_raw(f"CIRCLE('',#{mer_plc_0.eid},{R})")
mer_edge_0 = f._emit_raw(
    f"EDGE_CURVE('',#{v_eq_0.eid},#{v_pole_A.eid},#{mer_circ_0.eid},.T.)"
)

# Meridian from eq_pi (-1,0,0) to north pole (0,0,1): quarter-circle in neg-xz
mer_plc_pi_orig = f.cartesian_point((0.0, 0.0, 0.0))
mer_plc_pi_zdir = f.direction((0.0, 1.0, 0.0))   # normal of neg-xz plane
mer_plc_pi_xdir = f.direction((-1.0, 0.0, 0.0))
mer_plc_pi  = f.axis2_placement_3d(mer_plc_pi_orig, mer_plc_pi_zdir, mer_plc_pi_xdir)
mer_circ_pi = f._emit_raw(f"CIRCLE('',#{mer_plc_pi.eid},{R})")
mer_edge_pi = f._emit_raw(
    f"EDGE_CURVE('',#{v_eq_pi.eid},#{v_pole_B.eid},#{mer_circ_pi.eid},.T.)"
)

# ── EDGE_LOOP for face-0: pole_A, mer_0, equator forward ─────────────────────
oe_pole_A   = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{pole_ec_A.eid},.T.)")
oe_mer_0    = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{mer_edge_0.eid},.F.)")   # pole→eq0
oe_eq_fwd   = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{eq_edge.eid},.T.)")      # eq0→eq_pi
oe_mer_pi_A = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{mer_edge_pi.eid},.T.)") # eq_pi→pole
loop_0 = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_pole_A.eid},#{oe_mer_0.eid},"
    f"#{oe_eq_fwd.eid},#{oe_mer_pi_A.eid}))"
)

# ── EDGE_LOOP for face-1 (same face, lower hemi — reuse same surface) ────────
# Face-1 reuses same equator in reverse and pole_B.
oe_pole_B   = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{pole_ec_B.eid},.T.)")
oe_mer_pi_B = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{mer_edge_pi.eid},.F.)") # pole→eq_pi
oe_eq_rev   = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{eq_edge.eid},.F.)")     # eq_pi→eq0
oe_mer_0B   = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{mer_edge_0.eid},.T.)") # eq0→pole
loop_1 = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_pole_B.eid},#{oe_mer_pi_B.eid},"
    f"#{oe_eq_rev.eid},#{oe_mer_0B.eid}))"
)

# Wire both faces into same OPEN_SHELL — never orphan.
fob_0  = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop_0.eid},.T.)")
fob_1  = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop_1.eid},.T.)")
face_0 = f._emit_raw(f"ADVANCED_FACE('',(#{fob_0.eid}),#{sph_surf.eid},.T.)")
face_1 = f._emit_raw(f"ADVANCED_FACE('',(#{fob_1.eid}),#{sph_surf.eid},.T.)")
shell  = f._emit_raw(f"OPEN_SHELL('',(#{face_0.eid},#{face_1.eid}))")
sbsm   = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
