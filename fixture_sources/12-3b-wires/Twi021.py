"""Twi021 — Missing degenerate edge at surface singularity (cone apex).

Catalog claim: A face on a CONICAL_SURFACE whose apex (singular point) lies
inside the parametric domain but the wire bounding the face does NOT include the
degenerate edge (zero length in 3D, finite in UV) that bridges the singular row.
Without the bridging edge the wire is open in UV and surface-surface intersection
routines misbehave at the singularity.

Mechanism IS the EDGE_LOOP without the degenerate apex-bridging edge on the
CONICAL_SURFACE: the cone face has a proper outer wire with two lateral edges
and one base circle, but the apex is referenced as a vertex without a degenerate
ORIENTED_EDGE at the singular row. The defect EDGE_LOOP IS referenced by a
FACE_OUTER_BOUND in an ADVANCED_FACE in an OPEN_SHELL; never orphaned.

Reproducer: CONICAL_SURFACE semi-angle 30°; ADVANCED_FACE outer loop touches
cone apex vertex_point; no degenerate ORIENTED_EDGE inserted at apex.

Byte assertions:
  - count_entity_def(b'CONICAL_SURFACE') == 1
  - count_entity_def(b'VERTEX_POINT') >= 4

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
    catalog_id="Twi021",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a CONICAL_SURFACE "
        "(semi-angle 30°, axis +Z, apex at origin); "
        "FACE_OUTER_BOUND references an EDGE_LOOP with two lateral line edges "
        "and one base-circle arc that closes the side face; "
        "NO degenerate ORIENTED_EDGE inserted at the apex singular row; "
        "missing apex-bridging degenerate edge IS the mechanism; "
        "apex VERTEX_POINT IS wired into EDGE_LOOP lateral edges, FACE_OUTER_BOUND, ADVANCED_FACE, OPEN_SHELL; "
        "kernel must insert degenerate edge at apex or reject as malformed"
    ),
)

# ── CONICAL_SURFACE: apex at origin, axis +Z, semi-angle 30° ─────────────────
SEMI_ANGLE_DEG = 30.0
SEMI_ANGLE_RAD = math.radians(SEMI_ANGLE_DEG)
HEIGHT = 2.0   # cone height; base radius = HEIGHT * tan(30°)
BASE_R = HEIGHT * math.tan(SEMI_ANGLE_RAD)

cone_orig = f.cartesian_point((0.0, 0.0, 0.0))
cone_zdir = f.direction((0.0, 0.0, 1.0))
cone_xdir = f.direction((1.0, 0.0, 0.0))
cone_plc  = f.axis2_placement_3d(cone_orig, cone_zdir, cone_xdir)
cone_surf = f._emit_raw(
    f"CONICAL_SURFACE('',#{cone_plc.eid},{HEIGHT},{SEMI_ANGLE_RAD:.10f})"
)

# ── Apex vertex (singular point) — no degenerate edge inserted ────────────────
v_apex_L = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))  # left lateral
v_apex_R = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))  # right lateral

# ── Base circle vertices at theta=0 and theta=π ───────────────────────────────
v_base_0   = f.vertex_point(f.cartesian_point((BASE_R, 0.0, HEIGHT)))
v_base_pi  = f.vertex_point(f.cartesian_point((-BASE_R, 0.0, HEIGHT)))

# ── Two lateral line edges from apex to base ──────────────────────────────────
# Left lateral: apex(0,0,0) → base(BASE_R, 0, HEIGHT)
lat_L_dir = f.direction((BASE_R / HEIGHT, 0.0, 1.0))
# Normalise
_mag_L = math.hypot(BASE_R / HEIGHT, 1.0)
lat_L_dir = f.direction((BASE_R / HEIGHT / _mag_L, 0.0, 1.0 / _mag_L))
lat_L_len = math.hypot(BASE_R, HEIGHT)
lat_L_vec = f.vector(lat_L_dir, lat_L_len)
lat_L_ln  = f.line(f.cartesian_point((0.0, 0.0, 0.0)), lat_L_vec)
edge_lat_L = f.edge_curve(v_apex_L, v_base_0, lat_L_ln)
oe_lat_L   = f.oriented_edge(edge_lat_L, True)

# Right lateral: base(-BASE_R,0,HEIGHT) → apex(0,0,0) (traversed reversed)
lat_R_dir = f.direction((-BASE_R / HEIGHT / _mag_L, 0.0, 1.0 / _mag_L))
lat_R_vec = f.vector(lat_R_dir, lat_L_len)
lat_R_ln  = f.line(f.cartesian_point((-BASE_R, 0.0, HEIGHT)), lat_R_vec)
edge_lat_R = f.edge_curve(v_base_pi, v_apex_R, lat_R_ln)
oe_lat_R   = f.oriented_edge(edge_lat_R, True)

# ── Base semi-circle arc from (BASE_R,0,HEIGHT) to (-BASE_R,0,HEIGHT) ─────────
base_plc_orig = f.cartesian_point((0.0, 0.0, HEIGHT))
base_plc_zdir = f.direction((0.0, 0.0, 1.0))
base_plc_xdir = f.direction((1.0, 0.0, 0.0))
base_plc  = f.axis2_placement_3d(base_plc_orig, base_plc_zdir, base_plc_xdir)
base_circ = f._emit_raw(f"CIRCLE('',#{base_plc.eid},{BASE_R:.10f})")
base_arc_edge = f._emit_raw(
    f"EDGE_CURVE('',#{v_base_0.eid},#{v_base_pi.eid},#{base_circ.eid},.T.)"
)
oe_base = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{base_arc_edge.eid},.T.)")

# ── EDGE_LOOP: no degenerate apex edge — IS the mechanism ────────────────────
# Loop: lat_L(apex→base_0) → base_arc(base_0→base_pi) → lat_R(base_pi→apex)
# Wire closes in 3D (meets at apex) but no degenerate edge bridges UV singularity.
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_lat_L.eid},#{oe_base.eid},#{oe_lat_R.eid}))"
)

# Wire into face/shell topology — never orphan.
fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{cone_surf.eid},.T.)")
shell = f._emit_raw(f"OPEN_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
