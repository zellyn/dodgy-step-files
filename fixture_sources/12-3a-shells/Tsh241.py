"""Tsh241 — Cone-apex degenerate edge referenced from the bounds of TWO
different ADVANCED_FACEs (extends Tsh035's single-face pattern to multi-face).

Catalog claim (occt-coverage GAP `stp-degenerate-edge-multiface`): per the
occt-coverage audit (problems.json), no existing fixture presents a
degenerate edge entity referenced from SEVERAL faces' bounds — the nearest
candidates (Tsh035, Twi031, Gs189, Xp013) each keep their degenerate/apex
edges within a single face's own EDGE_LOOP. This fixture builds a genuine
CONICAL_SURFACE split into TWO half-cone ADVANCED_FACEs (front, y>=0, and
back, y<=0), sharing:
  - the SAME degenerate apex EDGE_CURVE entity (zero-length, apex vertex at
    both ends) in BOTH faces' EDGE_LOOPs, and
  - the two lateral (radial) EDGE_CURVEs at the seam, each referenced with
    opposite ORIENTED_EDGE sense by the two faces (a genuine manifold split,
    not merely two independent half-cones taped together).

This forces StepToTopoDS_TranslateEdge::Init's cached-degenerated-edge
retranslation path: the FIRST face to be translated builds and caches a
TopoDS_Edge for the degenerate apex EDGE_CURVE with a pcurve specific to
that face's CONICAL_SURFACE parametrization; the SECOND face references the
identical EDGE_CURVE entity and must retranslate/reconstruct a per-face
copy (a fresh degenerate edge with its own pcurve for its own face), since a
degenerate edge's pcurve is inherently a per-face artifact even when the
underlying 3D edge entity is shared.

Mechanism IS the topology: the shared degenerate EDGE_CURVE and the two
shared lateral EDGE_CURVEs are wired directly into BOTH ADVANCED_FACEs'
EDGE_LOOPs (via FACE_OUTER_BOUND), both faces live in one OPEN_SHELL —
never orphaned.

Byte assertions:
  - count_entity_def(b'CONICAL_SURFACE') == 1
  - count_entity_def(b'ADVANCED_FACE') == 2
  - count_entity_def(b'EDGE_LOOP') == 2

Tier-3 assertions (live-computed via tier3_geometric.py):
  - n_faces_total == 2
  - face[0].surface_type == "cone"
  - face[1].surface_type == "cone"

live oracle (computed via validate2.py against this worktree's bytes):
  occt=shape(1)/shape(1) gmsh=shape(20)
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh241",
    defect=(
        "OPEN_SHELL with TWO ADVANCED_FACEs on the SAME CONICAL_SURFACE "
        "(semi-angle 30 deg, axis +Z, apex at origin), split front/back "
        "(y>=0 / y<=0) at a shared diametral seam; ONE degenerate apex "
        "EDGE_CURVE entity (zero-length, apex vertex at both ends) IS "
        "referenced from the bounds of BOTH ADVANCED_FACEs' EDGE_LOOPs "
        "(not confined to a single face's wire); the two radial seam "
        "EDGE_CURVEs are also shared between the faces with opposite "
        "ORIENTED_EDGE senses — forces per-face retranslation of the "
        "cached degenerate edge (StepToTopoDS_TranslateEdge::Init)"
    ),
)

# ── CONICAL_SURFACE: apex at origin, axis +Z, semi-angle 30 deg ──────────────
SEMI_ANGLE_DEG = 30.0
SEMI_ANGLE_RAD = math.radians(SEMI_ANGLE_DEG)
HEIGHT = 2.0
BASE_R = HEIGHT * math.tan(SEMI_ANGLE_RAD)

cone_orig = f.cartesian_point((0.0, 0.0, 0.0))
cone_zdir = f.direction((0.0, 0.0, 1.0))
cone_xdir = f.direction((1.0, 0.0, 0.0))
cone_plc = f.axis2_placement_3d(cone_orig, cone_zdir, cone_xdir)
cone_surf = f._emit_raw(
    f"CONICAL_SURFACE('',#{cone_plc.eid},{HEIGHT},{SEMI_ANGLE_RAD:.10f})"
)

# ── Vertices: apex, base_0 (u=0 deg), base_pi (u=180 deg) ────────────────────
v_apex = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
v_base_0 = f.vertex_point(f.cartesian_point((BASE_R, 0.0, HEIGHT)))
v_base_pi = f.vertex_point(f.cartesian_point((-BASE_R, 0.0, HEIGHT)))

# ── SHARED degenerate apex edge: apex -> apex, zero-length ───────────────────
# ONE entity, referenced (via two separate ORIENTED_EDGEs wrapping it) from
# BOTH faces below — this IS the multi-face mechanism.
degen_dir = f.direction((1.0, 0.0, 0.0))
degen_vec = f.vector(degen_dir, 0.0)
degen_line = f.line(f.cartesian_point((0.0, 0.0, 0.0)), degen_vec)
degen_edge = f._emit_raw(
    f"EDGE_CURVE('tsh241_degen_apex',#{v_apex.eid},#{v_apex.eid},#{degen_line.eid},.T.)"
)

# ── SHARED lateral (radial) edges: apex<->base_0 and apex<->base_pi ─────────
_mag = math.hypot(BASE_R, HEIGHT)
lat0_dir = f.direction((BASE_R / _mag, 0.0, HEIGHT / _mag))
lat0_vec = f.vector(lat0_dir, _mag)
lat0_ln = f.line(f.cartesian_point((0.0, 0.0, 0.0)), lat0_vec)
lat_edge_0 = f.edge_curve(v_apex, v_base_0, lat0_ln)  # apex -> base_0

latpi_dir = f.direction((-BASE_R / _mag, 0.0, HEIGHT / _mag))
latpi_vec = f.vector(latpi_dir, _mag)
latpi_ln = f.line(f.cartesian_point((0.0, 0.0, 0.0)), latpi_vec)
lat_edge_pi = f.edge_curve(v_apex, v_base_pi, latpi_ln)  # apex -> base_pi

# ── Base circle, shared by both half-arcs ────────────────────────────────────
base_plc_orig = f.cartesian_point((0.0, 0.0, HEIGHT))
base_plc_zdir = f.direction((0.0, 0.0, 1.0))
base_plc_xdir = f.direction((1.0, 0.0, 0.0))
base_plc = f.axis2_placement_3d(base_plc_orig, base_plc_zdir, base_plc_xdir)
base_circ = f._emit_raw(f"CIRCLE('',#{base_plc.eid},{BASE_R:.10f})")

# Front half-arc: base_0 (u=0) -> base_pi (u=180), traversing y>=0 (u: 0 -> pi).
base_arc_front = f._emit_raw(
    f"EDGE_CURVE('',#{v_base_0.eid},#{v_base_pi.eid},#{base_circ.eid},.T.)"
)
# Back half-arc: base_pi (u=180) -> base_0 (u=360=0), traversing y<=0 (u: pi -> 2pi).
base_arc_back = f._emit_raw(
    f"EDGE_CURVE('',#{v_base_pi.eid},#{v_base_0.eid},#{base_circ.eid},.T.)"
)

# ── Face A (front, y>=0): degen(apex->apex), lat0(apex->base_0), ────────────
# base_arc_front(base_0->base_pi), lat_pi REVERSED(base_pi->apex).
oe_degen_A = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{degen_edge.eid},.T.)")
oe_lat0_A = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{lat_edge_0.eid},.T.)")
oe_base_front = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{base_arc_front.eid},.T.)")
oe_latpi_A = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{lat_edge_pi.eid},.F.)")
loop_A = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_degen_A.eid},#{oe_lat0_A.eid},#{oe_base_front.eid},#{oe_latpi_A.eid}))"
)
fob_A = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop_A.eid},.T.)")
face_A = f._emit_raw(f"ADVANCED_FACE('tsh241_face_front',(#{fob_A.eid}),#{cone_surf.eid},.T.)")

# ── Face B (back, y<=0): degen(apex->apex) SAME ENTITY as face A, ───────────
# lat_pi(apex->base_pi), base_arc_back(base_pi->base_0), lat0 REVERSED(base_0->apex).
oe_degen_B = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{degen_edge.eid},.T.)")
oe_latpi_B = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{lat_edge_pi.eid},.T.)")
oe_base_back = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{base_arc_back.eid},.T.)")
oe_lat0_B = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{lat_edge_0.eid},.F.)")
loop_B = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_degen_B.eid},#{oe_latpi_B.eid},#{oe_base_back.eid},#{oe_lat0_B.eid}))"
)
fob_B = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop_B.eid},.T.)")
face_B = f._emit_raw(f"ADVANCED_FACE('tsh241_face_back',(#{fob_B.eid}),#{cone_surf.eid},.T.)")

# ── Both faces in one OPEN_SHELL — never orphaned ────────────────────────────
shell = f._emit_raw(f"OPEN_SHELL('',(#{face_A.eid},#{face_B.eid}))")
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
