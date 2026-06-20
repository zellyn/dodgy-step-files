"""Twi035 — Sphere given by two meridians (special wire shape).

Catalog claim: A sphere is encoded by a face whose outer wire consists of two
meridian edges (going from north to south pole and back). Special-case for
FixShifted: the two pcurves must not be coerced by parametric shifting.

Mechanism IS the EDGE_LOOP on a SPHERICAL_SURFACE containing exactly two
meridian EDGE_CURVEs: one from north pole to south pole (theta=0 half-circle)
and one returning from south pole to north pole (theta=π half-circle), plus
two degenerate pole edges at each apex. The EDGE_LOOP IS wired into a
FACE_OUTER_BOUND in an ADVANCED_FACE in an OPEN_SHELL; never orphaned.
The healer (FixShifted) must normalise the meridian-pair pattern by inserting
pole degenerate edges if missing, not by shifting pcurves.

Reproducer: ADVANCED_FACE on SPHERICAL_SURFACE with two meridian EDGE_CURVEs
plus degenerate pole-bridge edges; BRepCheck reports invalid (shifted pcurves).

Byte assertions:
  - count_entity_def(b'SPHERICAL_SURFACE') == 1
  - count_entity_def(b'EDGE_LOOP') == 1

Tier-3 assertions:
  - face[0].surface_type == "sphere"
  - n_edges_total >= 6
  - n_vertices_total >= 8
  - brepcheck.valid == False

live oracle: occt=shape(1)/shape(1)
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi035",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a SPHERICAL_SURFACE "
        "(radius 1, centre at origin); "
        "FACE_OUTER_BOUND references an EDGE_LOOP containing: "
        "degenerate north-pole edge (v_north→v_north, zero-length), "
        "left meridian arc from north pole to south pole (theta=0 half-circle), "
        "degenerate south-pole edge (v_south→v_south, zero-length), "
        "right meridian arc from south pole to north pole (theta=π half-circle); "
        "two meridian EDGE_CURVEs in the same EDGE_LOOP IS the mechanism — "
        "lune-shaped sphere face needing FixShifted normalisation; "
        "EDGE_LOOP IS wired into FACE_OUTER_BOUND, ADVANCED_FACE, OPEN_SHELL; "
        "kernel must normalise pcurves; do not coerce by shifting"
    ),
)

# ── SPHERICAL_SURFACE: radius 1, centre origin ────────────────────────────────
R = 1.0

sph_orig = f.cartesian_point((0.0, 0.0, 0.0))
sph_zdir = f.direction((0.0, 0.0, 1.0))
sph_xdir = f.direction((1.0, 0.0, 0.0))
sph_plc  = f.axis2_placement_3d(sph_orig, sph_zdir, sph_xdir)
sph_surf = f._emit_raw(f"SPHERICAL_SURFACE('',#{sph_plc.eid},{R})")

# ── North and south pole vertices ─────────────────────────────────────────────
v_north = f.vertex_point(f.cartesian_point((0.0, 0.0,  R)))
v_south = f.vertex_point(f.cartesian_point((0.0, 0.0, -R)))

# ── Degenerate north-pole edge: v_north→v_north, zero-length ─────────────────
n_dir  = f.direction((1.0, 0.0, 0.0))
n_vec  = f.vector(n_dir, 0.0)
n_line = f.line(f.cartesian_point((0.0, 0.0, R)), n_vec)
n_ec   = f._emit_raw(
    f"EDGE_CURVE('',#{v_north.eid},#{v_north.eid},#{n_line.eid},.T.)"
)
oe_north_degen = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{n_ec.eid},.T.)")

# ── Degenerate south-pole edge: v_south→v_south, zero-length ─────────────────
s_dir  = f.direction((1.0, 0.0, 0.0))
s_vec  = f.vector(s_dir, 0.0)
s_line = f.line(f.cartesian_point((0.0, 0.0, -R)), s_vec)
s_ec   = f._emit_raw(
    f"EDGE_CURVE('',#{v_south.eid},#{v_south.eid},#{s_line.eid},.T.)"
)
oe_south_degen = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{s_ec.eid},.T.)")

# ── Left meridian arc: north pole → south pole (half-circle in xz plane) ──────
# Quarter circle in xz-plane: centre origin, xdir=(1,0,0), zdir=(0,1,0) so
# arc goes from (0,0,R) through (R,0,0) to (0,0,-R) — half-circle.
mer_L_plc_orig = f.cartesian_point((0.0, 0.0, 0.0))
mer_L_plc_zdir = f.direction((0.0, -1.0, 0.0))  # axis perpendicular to xz plane
mer_L_plc_xdir = f.direction((0.0, 0.0, 1.0))   # start direction toward north pole
mer_L_plc  = f.axis2_placement_3d(mer_L_plc_orig, mer_L_plc_zdir, mer_L_plc_xdir)
mer_L_circ = f._emit_raw(f"CIRCLE('',#{mer_L_plc.eid},{R})")
mer_L_ec   = f._emit_raw(
    f"EDGE_CURVE('',#{v_north.eid},#{v_south.eid},#{mer_L_circ.eid},.T.)"
)
oe_mer_L = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{mer_L_ec.eid},.T.)")

# ── Right meridian arc: south pole → north pole (half-circle in neg-x side) ───
mer_R_plc_orig = f.cartesian_point((0.0, 0.0, 0.0))
mer_R_plc_zdir = f.direction((0.0, 1.0, 0.0))   # axis perpendicular to neg-xz plane
mer_R_plc_xdir = f.direction((0.0, 0.0, -1.0))  # start direction toward south pole
mer_R_plc  = f.axis2_placement_3d(mer_R_plc_orig, mer_R_plc_zdir, mer_R_plc_xdir)
mer_R_circ = f._emit_raw(f"CIRCLE('',#{mer_R_plc.eid},{R})")
mer_R_ec   = f._emit_raw(
    f"EDGE_CURVE('',#{v_south.eid},#{v_north.eid},#{mer_R_circ.eid},.T.)"
)
oe_mer_R = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{mer_R_ec.eid},.T.)")

# ── EDGE_LOOP: two meridians + two pole degenerate edges IS the mechanism ─────
# Trace: north(degen), north→south (left mer), south(degen), south→north (right mer).
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_north_degen.eid},#{oe_mer_L.eid},"
    f"#{oe_south_degen.eid},#{oe_mer_R.eid}))"
)

# Wire into face/shell topology — never orphan.
fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{sph_surf.eid},.T.)")
shell = f._emit_raw(f"OPEN_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
