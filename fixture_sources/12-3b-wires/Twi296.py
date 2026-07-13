"""Twi296 — Degenerated ("spindle") torus: major radius < minor radius, so
the torus surface pinches to a single point at aPhi = acos(-R/r); the wire
bounding a face crossing that singular row is missing its degenerate apex
edge (missing subvariant of tkshh-wire-missing-or-bad-degenerated-edge,
distinct from Twi021's cone-apex case).

Catalog claim (occt-coverage/tkshhealing/problems.json,
tkshh-wire-missing-or-bad-degenerated-edge, subvariant "degenerated torus
(major radius < minor radius): apex edge at aPhi = acos(-R/r)
(FixMissingSeam)"). Twi021 demonstrates the missing-degenerate-edge
mechanism on a CONICAL_SURFACE apex. Twi287 demonstrates a DIFFERENT torus
defect (full-period closed meridian edges, R>r ordinary torus). Neither
covers the torus-specific singularity: when a torus's major radius R is
smaller than its minor (tube) radius r ("spindle torus", self-intersecting
in 3D but a legal STEP TOROIDAL_SURFACE), the tube radius R + r*cos(v)
reaches zero at v = acos(-R/r) -- at that one V-row the ENTIRE U-circle
collapses to the single point (0, 0, r*sin(v)) on the torus's own axis,
exactly analogous to a cone's apex or a sphere's pole. A face whose wire
crosses this V-row needs a degenerate edge bridging it; this fixture's
wire (mirroring Twi021's half-cone construction almost exactly) omits it.

Mechanism IS the half-face on the TOROIDAL_SURFACE (major_radius=2,
minor_radius=5, so R<r): two "meridian" CIRCLE-arc EDGE_CURVEs (u=0 and
u=pi) run from the outer-equator base circle (v=0, radius R+r=7) to the
singular row (v=acos(-2/5)~=113.58deg, where BOTH meridians converge on
the SAME 3D point (0,0,~4.583) but via TWO SEPARATE VERTEX_POINT
instances, exactly mirroring Twi021's two-separate-apex-vertex pattern),
closed by a base semicircle arc (u:0->pi at v=0). NO degenerate
ORIENTED_EDGE bridges the two apex vertex instances. The defect EDGE_LOOP
IS referenced by a FACE_OUTER_BOUND in an ADVANCED_FACE in an OPEN_SHELL;
never orphaned.

Byte assertions:
  - count_entity_def(b'TOROIDAL_SURFACE') == 1
  - count_entity_def(b'VERTEX_POINT') >= 4

Tier-3 assertions:
  - face[0].surface_type == "torus"
  - n_edges_total >= 3
  - n_vertices_total >= 6

live oracle: occt=shape(1)/shape(1)
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi296",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a TOROIDAL_SURFACE (major_radius=2, "
        "minor_radius=5 -- major < minor, a 'spindle' torus whose tube radius "
        "R + r*cos(v) reaches ZERO at v=acos(-R/r), collapsing the entire U-circle "
        "at that row to a single point on the torus axis, a genuine surface "
        "singularity analogous to a cone apex); "
        "FACE_OUTER_BOUND references an EDGE_LOOP with two meridian CIRCLE-arc "
        "edges (u=0 and u=pi) running from the outer-equator base circle (v=0) to "
        "the singular row (v=acos(-2/5)), plus one base semicircle arc closing "
        "u:0->pi at v=0; "
        "NO degenerate ORIENTED_EDGE inserted at the singular row -- the two "
        "meridian edges terminate at the SAME 3D point via TWO SEPARATE "
        "VERTEX_POINT instances, exactly mirroring Twi021's missing-apex-edge "
        "cone pattern but on a torus singularity instead; "
        "missing apex-bridging degenerate edge IS the mechanism; "
        "apex VERTEX_POINTs ARE wired into EDGE_LOOP meridian edges, "
        "FACE_OUTER_BOUND, ADVANCED_FACE, OPEN_SHELL; never orphaned; "
        "kernel must insert a degenerate edge at aPhi=acos(-R/r) or reject as "
        "malformed"
    ),
)

MAJOR_R = 2.0  # R
MINOR_R = 5.0  # r  (R < r: degenerated/spindle torus)

v_apex_param = math.acos(-MAJOR_R / MINOR_R)
apex_z = MINOR_R * math.sin(v_apex_param)  # torus-axis point height

# ── TOROIDAL_SURFACE: axis +Z, origin at torus centre ─────────────────────────
tor_orig = f.cartesian_point((0.0, 0.0, 0.0))
tor_zdir = f.direction((0.0, 0.0, 1.0))
tor_xdir = f.direction((1.0, 0.0, 0.0))
tor_plc = f.axis2_placement_3d(tor_orig, tor_zdir, tor_xdir)
tor_surf = f._emit_raw(
    f"TOROIDAL_SURFACE('',#{tor_plc.eid},{MAJOR_R:.10f},{MINOR_R:.10f})"
)

# ── Apex vertices (singular point) -- two separate instances, no degenerate
#    edge inserted, mirroring Twi021's two-separate-apex-vertex pattern ──────
v_apex_0 = f.vertex_point(f.cartesian_point((0.0, 0.0, apex_z)))   # from u=0 meridian
v_apex_pi = f.vertex_point(f.cartesian_point((0.0, 0.0, apex_z)))  # from u=pi meridian

# ── Base-circle (v=0, outer equator, radius R+r) vertices at u=0 and u=pi ────
BASE_R = MAJOR_R + MINOR_R
v_base_0 = f.vertex_point(f.cartesian_point((BASE_R, 0.0, 0.0)))
v_base_pi = f.vertex_point(f.cartesian_point((-BASE_R, 0.0, 0.0)))

# ── Meridian at u=0: circle in the XZ-plane (y=0), centre (R,0,0), radius r ──
mer0_orig = f.cartesian_point((MAJOR_R, 0.0, 0.0))
mer0_axis = f.direction((0.0, 1.0, 0.0))
mer0_ref = f.direction((1.0, 0.0, 0.0))
mer0_plc = f.axis2_placement_3d(mer0_orig, mer0_axis, mer0_ref)
mer0_circ = f._emit_raw(f"CIRCLE('',#{mer0_plc.eid},{MINOR_R:.10f})")
# apex_0 -> base_0 (points (0,0,apex_z) and (R+r,0,0) both lie on this circle:
# centre (R,0,0), radius r -- check: dist((0,0,apex_z),(R,0,0)) = sqrt(R^2+apex_z^2)
# = r by construction of v_apex_param)
edge_mer0 = f._emit_raw(
    f"EDGE_CURVE('',#{v_apex_0.eid},#{v_base_0.eid},#{mer0_circ.eid},.T.)"
)
oe_mer0 = f.oriented_edge(edge_mer0, True)

# ── Meridian at u=pi: circle in the XZ-plane (y=0), centre (-R,0,0), radius r ─
mer_pi_orig = f.cartesian_point((-MAJOR_R, 0.0, 0.0))
mer_pi_axis = f.direction((0.0, 1.0, 0.0))
mer_pi_ref = f.direction((-1.0, 0.0, 0.0))
mer_pi_plc = f.axis2_placement_3d(mer_pi_orig, mer_pi_axis, mer_pi_ref)
mer_pi_circ = f._emit_raw(f"CIRCLE('',#{mer_pi_plc.eid},{MINOR_R:.10f})")
# base_pi -> apex_pi
edge_mer_pi = f._emit_raw(
    f"EDGE_CURVE('',#{v_base_pi.eid},#{v_apex_pi.eid},#{mer_pi_circ.eid},.T.)"
)
oe_mer_pi = f.oriented_edge(edge_mer_pi, True)

# ── Base semicircle arc (v=0, outer equator): u=0 -> u=pi, radius R+r ────────
base_orig = f.cartesian_point((0.0, 0.0, 0.0))
base_axis = f.direction((0.0, 0.0, 1.0))
base_ref = f.direction((1.0, 0.0, 0.0))
base_plc = f.axis2_placement_3d(base_orig, base_axis, base_ref)
base_circ = f._emit_raw(f"CIRCLE('',#{base_plc.eid},{BASE_R:.10f})")
edge_base = f._emit_raw(
    f"EDGE_CURVE('',#{v_base_0.eid},#{v_base_pi.eid},#{base_circ.eid},.T.)"
)
oe_base = f.oriented_edge(edge_base, True)

# ── EDGE_LOOP: apex_0 -> base_0 -> base_pi -> apex_pi -- open at the apex,
#    no degenerate edge bridges v_apex_0 <-> v_apex_pi (the defect) ──────────
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_mer0.eid},#{oe_base.eid},#{oe_mer_pi.eid}))"
)

fob = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{tor_surf.eid},.T.)")
shell = f._emit_raw(f"OPEN_SHELL('',(#{face.eid}))")
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
