"""Twi029 — STEP writer drops entire wire if it contains a degenerate edge.

Catalog claim: When an OCCT shape contains a wire with one or more degenerate
edges (apex-bridge, seam), the writer historically omitted the entire wire on
STEP export, causing the cone apex to disappear in round-trip.

Mechanism IS the EDGE_LOOP that includes a zero-length degenerate ORIENTED_EDGE
at the cone apex: the degenerate EDGE_CURVE (start == end vertex, same VERTEX_POINT,
curve is a degenerate LINE of zero magnitude) IS wired alongside the two lateral
edges and the base arc in the EDGE_LOOP. The EDGE_LOOP IS referenced by a
FACE_OUTER_BOUND in an ADVANCED_FACE in an OPEN_SHELL; never orphaned.
The writer must retain the complete wire rather than silently dropping it when
a degenerate member is present.

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
    catalog_id="Twi029",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a CONICAL_SURFACE "
        "(semi-angle 30°, axis +Z, apex at origin); "
        "FACE_OUTER_BOUND references an EDGE_LOOP containing: "
        "one degenerate ORIENTED_EDGE at the apex (zero-length EDGE_CURVE, same vertex at both ends), "
        "two lateral line edges from apex to base, "
        "and one base semi-circle arc; "
        "degenerate apex-bridge EDGE_CURVE inside EDGE_LOOP IS the mechanism; "
        "EDGE_LOOP IS wired into FACE_OUTER_BOUND, ADVANCED_FACE, OPEN_SHELL; "
        "STEP writer must emit the complete wire, not drop it when a degenerate member is present"
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
v_apex    = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))  # shared apex
v_base_0  = f.vertex_point(f.cartesian_point((BASE_R, 0.0, HEIGHT)))
v_base_pi = f.vertex_point(f.cartesian_point((-BASE_R, 0.0, HEIGHT)))

# ── Degenerate apex-bridge edge: start == end == v_apex, zero-length ──────────
# A zero-length LINE at the apex is the canonical degenerate edge.
degen_dir  = f.direction((1.0, 0.0, 0.0))      # arbitrary direction; magnitude 0
degen_vec  = f.vector(degen_dir, 0.0)           # zero magnitude
degen_line = f.line(f.cartesian_point((0.0, 0.0, 0.0)), degen_vec)
# EDGE_CURVE with same vertex at both ends — IS the degenerate edge.
degen_ec = f._emit_raw(
    f"EDGE_CURVE('',#{v_apex.eid},#{v_apex.eid},#{degen_line.eid},.T.)"
)
oe_degen = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{degen_ec.eid},.T.)")

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

# ── EDGE_LOOP: includes degenerate apex edge — IS the mechanism ───────────────
# Order: degen(apex→apex), lat_L(apex→base_0), base_arc(base_0→base_pi),
#        lat_R(base_pi→apex). Topologically closed with apex bridge.
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_degen.eid},#{oe_lat_L.eid},"
    f"#{oe_base.eid},#{oe_lat_R.eid}))"
)

# Wire into face/shell topology — never orphan.
fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{cone_surf.eid},.T.)")
shell = f._emit_raw(f"OPEN_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
