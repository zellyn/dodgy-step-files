"""Twi031 — Degenerate edges duplicated at apex (Pro/E).

Catalog claim: Some Pro/E exports emit two degenerate edges where one is
sufficient at a cone/sphere apex. Causes downstream wire reorder confusion.

Mechanism IS the EDGE_LOOP that contains two zero-length ORIENTED_EDGEs at the
cone apex (same vertex at both ends of each, same geometric position) instead
of exactly one. The two degenerate EDGE_CURVEs at the apex ARE wired into the
EDGE_LOOP alongside the two lateral edges and the base arc; the EDGE_LOOP IS
referenced by a FACE_OUTER_BOUND in an ADVANCED_FACE in an OPEN_SHELL; never
orphaned. A healing pass must detect and dedupe to a single canonical apex bridge.

Reproducer: Pro/E-style ADVANCED_FACE on CONICAL_SURFACE whose apex wire carries
two ORIENTED_EDGEs wrapping two separate degenerate EDGE_CURVEs at the same apex
vertex.

Byte assertions:
  - count_entity_def(b'CONICAL_SURFACE') == 1
  - count_entity_def(b'EDGE_LOOP') == 1

Tier-3 assertions:
  - face[0].surface_type == "cone"
  - n_edges_total >= 4
  - n_vertices_total >= 8
  - brepcheck.valid == True

live oracle: occt=shape(1)/shape(1)
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi031",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a CONICAL_SURFACE "
        "(semi-angle 30°, axis +Z, apex at origin); "
        "FACE_OUTER_BOUND references an EDGE_LOOP containing: "
        "two degenerate ORIENTED_EDGEs (degen_A and degen_B) both at the apex "
        "— same zero-length EDGE_CURVEs with apex vertex at both ends — "
        "two lateral line edges from apex to base, "
        "and one base semi-circle arc; "
        "two degenerate apex EDGE_CURVEs in the same EDGE_LOOP IS the mechanism "
        "(Pro/E redundant apex bridge); "
        "EDGE_LOOP IS wired into FACE_OUTER_BOUND, ADVANCED_FACE, OPEN_SHELL; "
        "kernel must detect and dedupe to a single canonical apex bridge"
    ),
)

# ── CONICAL_SURFACE: apex at origin, axis +Z, semi-angle 30° ─────────────────
SEMI_ANGLE_DEG = 30.0
SEMI_ANGLE_RAD = math.radians(SEMI_ANGLE_DEG)
HEIGHT = 2.0
BASE_R = HEIGHT * math.tan(SEMI_ANGLE_RAD)

cone_orig = f.cartesian_point((0.0, 0.0, 0.0))
cone_zdir = f.direction((0.0, 0.0, 1.0))
cone_xdir = f.direction((1.0, 0.0, 0.0))
cone_plc  = f.axis2_placement_3d(cone_orig, cone_zdir, cone_xdir)
cone_surf = f._emit_raw(
    f"CONICAL_SURFACE('',#{cone_plc.eid},{HEIGHT},{SEMI_ANGLE_RAD:.10f})"
)

# ── Vertices ──────────────────────────────────────────────────────────────────
v_apex    = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))
v_base_0  = f.vertex_point(f.cartesian_point((BASE_R, 0.0, HEIGHT)))
v_base_pi = f.vertex_point(f.cartesian_point((-BASE_R, 0.0, HEIGHT)))

# ── Degenerate apex edge A — first redundant apex bridge ──────────────────────
degen_dir_A  = f.direction((1.0, 0.0, 0.0))
degen_vec_A  = f.vector(degen_dir_A, 0.0)
degen_line_A = f.line(f.cartesian_point((0.0, 0.0, 0.0)), degen_vec_A)
degen_ec_A   = f._emit_raw(
    f"EDGE_CURVE('',#{v_apex.eid},#{v_apex.eid},#{degen_line_A.eid},.T.)"
)
oe_degen_A = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{degen_ec_A.eid},.T.)")

# ── Degenerate apex edge B — second redundant apex bridge (IS the defect) ────
degen_dir_B  = f.direction((1.0, 0.0, 0.0))
degen_vec_B  = f.vector(degen_dir_B, 0.0)
degen_line_B = f.line(f.cartesian_point((0.0, 0.0, 0.0)), degen_vec_B)
degen_ec_B   = f._emit_raw(
    f"EDGE_CURVE('',#{v_apex.eid},#{v_apex.eid},#{degen_line_B.eid},.T.)"
)
oe_degen_B = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{degen_ec_B.eid},.T.)")

# ── Left lateral: apex → base_0 ──────────────────────────────────────────────
_mag = math.hypot(BASE_R, HEIGHT)
lat_L_dir = f.direction((BASE_R / _mag, 0.0, HEIGHT / _mag))
lat_L_vec = f.vector(lat_L_dir, _mag)
lat_L_ln  = f.line(f.cartesian_point((0.0, 0.0, 0.0)), lat_L_vec)
edge_lat_L = f.edge_curve(v_apex, v_base_0, lat_L_ln)
oe_lat_L   = f.oriented_edge(edge_lat_L, True)

# ── Base semi-circle: base_0 → base_pi ───────────────────────────────────────
base_plc_orig = f.cartesian_point((0.0, 0.0, HEIGHT))
base_plc_zdir = f.direction((0.0, 0.0, 1.0))
base_plc_xdir = f.direction((1.0, 0.0, 0.0))
base_plc  = f.axis2_placement_3d(base_plc_orig, base_plc_zdir, base_plc_xdir)
base_circ = f._emit_raw(f"CIRCLE('',#{base_plc.eid},{BASE_R:.10f})")
base_arc_edge = f._emit_raw(
    f"EDGE_CURVE('',#{v_base_0.eid},#{v_base_pi.eid},#{base_circ.eid},.T.)"
)
oe_base = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{base_arc_edge.eid},.T.)")

# ── Right lateral: base_pi → apex ────────────────────────────────────────────
lat_R_dir = f.direction((-BASE_R / _mag, 0.0, HEIGHT / _mag))
lat_R_vec = f.vector(lat_R_dir, _mag)
lat_R_ln  = f.line(f.cartesian_point((-BASE_R, 0.0, HEIGHT)), lat_R_vec)
edge_lat_R = f.edge_curve(v_base_pi, v_apex, lat_R_ln)
oe_lat_R   = f.oriented_edge(edge_lat_R, True)

# ── EDGE_LOOP: two degenerate apex edges IS the mechanism ────────────────────
# Order: degen_A, degen_B (both at apex), lat_L, base_arc, lat_R.
# Wire: apex→apex(A)→apex(B)→base_0→base_pi→apex.
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_degen_A.eid},#{oe_degen_B.eid},#{oe_lat_L.eid},"
    f"#{oe_base.eid},#{oe_lat_R.eid}))"
)

# Wire into face/shell topology — never orphan.
fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{cone_surf.eid},.T.)")
shell = f._emit_raw(f"OPEN_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
