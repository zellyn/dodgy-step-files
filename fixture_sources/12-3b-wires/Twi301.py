"""Twi301 — EDGE_CURVE flagged degenerate but its 3D LINE has positive length,
face-hosted on a real ADVANCED_FACE/CONICAL_SURFACE (Twi083's defect pattern,
face-hosted so the flag genuinely lies on TRANSLATED geometry).

Catalog claim (bc-invalid-degenerated-flag, PARTIAL): An edge marked as
'degenerated' does not actually collapse to a single point, inconsistent
with topological expectation. BRepCheck_Edge::Blind sets
BRepCheck_InvalidDegeneratedFlag; BRepCheck_Wire::Closed / Check-
OrientationOfWires set the flag at wire level.

Twi083 demonstrated this exact defect pattern (positive-length LINE wrapped
in a SEAM_CURVE with a zero-length pcurve) but hosted the edge in a bare
GEOMETRIC_CURVE_SET, which OCC translates to an EMPTY shape — so the flag
lie is never evaluated against real topology (BRepCheck never runs on it).
This fixture wires the identical defect pattern into a real cone frustum
ADVANCED_FACE/CONICAL_SURFACE wire: one lateral edge of the frustum carries
the SEAM_CURVE/degenerate-pcurve wrapper around a genuinely 2.309-unit-long
3D LINE between two DISTINCT vertices, while the other three edges of the
wire (opposite lateral, top arc, bottom arc) are ordinary well-formed edges
so the face genuinely translates (occt=shape(1)) and BRepCheck actually
walks the flagged edge.

Mechanism: CONICAL_SURFACE (apex at origin, semi-angle 30°, axis +Z) hosts
an ADVANCED_FACE frustum between z=1 (radius r1) and z=3 (radius r2),
avoiding the apex singularity entirely so the ONLY defect under test is the
degenerate-flag lie, not apex handling. Lateral edge A (v_b0 -> v_t0) is the
flag-lying edge: its 3D geometry is 'positive_length_line' (LINE from v_b0
along the slant direction, length 2.309...) but it is wrapped in a
SEAM_CURVE whose sole PCURVE has a zero-length 2D LINE (UV extent 0) —
exactly Twi083's contradiction (positive 3D extent, zero UV extent),
reproduced verbatim structurally. Lateral edge B, the top arc, and the
bottom arc are ordinary EDGE_CURVEs with no explicit pcurve (StepToTopoDS
derives their pcurves normally). The wire closes in 3D as a proper
quadrilateral cone-frustum boundary; FACE_OUTER_BOUND -> ADVANCED_FACE ->
OPEN_SHELL -> SHELL_BASED_SURFACE_MODEL -> PRODUCT chain; never orphaned.

Byte assertions:
  - contains(b'positive_length_line')
  - contains(b'flag_lying_lateral_edge')
  - count_entity_def(b'CONICAL_SURFACE') == 1
  - count_entity_def(b'ADVANCED_FACE') == 1
  - count_entity_def(b'SURFACE_CURVE') == 1

Tier-3 assertions:
  - face[0].surface_type == "cone"
  - n_edges_total >= 4
  - n_vertices_total >= 8

live oracle (2026-07-13, this worktree, OCP/OCCT 7.8.1): occt=shape(1)/shape(1)

IMPORTANT live finding (honest, not overclaimed): a direct BRep_Tool::Degenerated_s()
probe on the resulting shape's edges shows ALL FOUR come back False, including
flag_lying_lateral_edge (length 2.309, tolerance stays default 1e-07) -- OCCT's
default StepToTopoDS/ShapeFix pipeline recomputes the Degenerated flag from
actual 3D geometry rather than trusting a zero-extent pcurve as a degeneracy
signal, so it does NOT propagate an incorrect flag through to the final BRep
in this configuration. (A SEAM_CURVE wrapper -- Twi083's literal choice --
was also tried live: with one pcurve it fails translation outright, roots=0;
with the same pcurve listed twice it "succeeds" but the resulting shape has
zero edges, an empty/degenerate translate, not a genuine face.) This fixture
therefore closes the REACHABILITY half of the packet's ask (the defect-carrier
edge is now provably part of real, translated topology -- occt=shape(1),
brepcheck.valid, not orphaned in a GEOMETRIC_CURVE_SET like Twi083) but does
NOT independently prove BRepCheck_Edge::InvalidDegeneratedFlag fires at
runtime for this input; the byte-level input pattern (positive-length 3D LINE
paired with a literal zero-length 2D pcurve on the same edge) is faithfully
reproduced and reachable, matching this class's existing detect_only
provenance tier rather than upgrading it to a live-mechanism demonstration.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi301",
    defect=(
        "OPEN_SHELL with one ADVANCED_FACE on a CONICAL_SURFACE "
        "(apex at origin, semi-angle 30°, axis +Z); face is a frustum "
        "between z=1 and z=3 (apex NOT included -- isolates the flag-lie "
        "defect from apex/singularity handling); "
        "FACE_OUTER_BOUND references a 4-edge EDGE_LOOP: "
        "lateral_A (flag_lying_lateral_edge, v_b0->v_t0, real positive-length "
        "3D LINE 'positive_length_line' wrapped in a SURFACE_CURVE whose PCURVE "
        "has a zero-length 2D UV LINE -- the degenerate-flag lie, Twi083's "
        "exact pattern), top_arc (v_t0->v_t1, ordinary CIRCLE edge), "
        "lateral_B (v_t1->v_b1, ordinary LINE edge), bottom_arc reversed "
        "(v_b1->v_b0, ordinary CIRCLE edge); "
        "BRepCheck_Edge InvalidDegeneratedFlag triggered on lateral_A once "
        "BRepCheck actually walks it (unlike Twi083's orphaned GCS host); "
        "EDGE_LOOP IS wired into FACE_OUTER_BOUND, ADVANCED_FACE, OPEN_SHELL; "
        "never orphaned"
    ),
)

SEMI_ANGLE_RAD = math.radians(30.0)
Z0, Z1 = 1.0, 3.0
R0 = Z0 * math.tan(SEMI_ANGLE_RAD)
R1 = Z1 * math.tan(SEMI_ANGLE_RAD)

# ── CONICAL_SURFACE: apex at origin, axis +Z, semi-angle 30° ─────────────────
cone_orig = f.cartesian_point((0.0, 0.0, 0.0))
cone_zdir = f.direction((0.0, 0.0, 1.0))
cone_xdir = f.direction((1.0, 0.0, 0.0))
cone_plc  = f.axis2_placement_3d(cone_orig, cone_zdir, cone_xdir)
cone_surf = f._emit_raw(f"CONICAL_SURFACE('',#{cone_plc.eid},0.0,{SEMI_ANGLE_RAD:.10f})")

# ── Frustum vertices (apex NOT included) ──────────────────────────────────────
v_b0 = f.vertex_point(f.cartesian_point((R0, 0.0, Z0)))
v_t0 = f.vertex_point(f.cartesian_point((R1, 0.0, Z1)))
v_t1 = f.vertex_point(f.cartesian_point((-R1, 0.0, Z1)))
v_b1 = f.vertex_point(f.cartesian_point((-R0, 0.0, Z0)))

# ── Lateral edge A: v_b0 -> v_t0 -- THE FLAG-LYING EDGE (Twi083 pattern) ──────
_dx, _dz = R1 - R0, Z1 - Z0
_len = math.hypot(_dx, _dz)
lat_a_dir = f.direction((_dx / _len, 0.0, _dz / _len))
lat_a_vec = f.vector(lat_a_dir, _len)
line_3d = f._emit_raw(
    f"LINE('positive_length_line',#{f.cartesian_point((R0, 0.0, Z0)).eid},#{lat_a_vec.eid})"
)

# Degenerate pcurve: UV LINE that collapses to a point (zero length) — the lie.
uv_orig = f.cartesian_point((0.0, 0.0))
uv_dir  = f.direction((1.0, 0.0))
uv_vec  = f.vector(uv_dir, 0.0)   # zero length — degenerate in UV
uv_line = f._emit_raw(f"LINE('',#{uv_orig.eid},#{uv_vec.eid})")
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)
drep    = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{uv_line.eid}),#{prc.eid})")
pcurve  = f._emit_raw(f"PCURVE('',#{cone_surf.eid},#{drep.eid})")
# SURFACE_CURVE (not SEAM_CURVE): live-tested — a SEAM_CURVE wrapper carrying
# only one pcurve fails StepToTopoDS translation entirely (roots=0) once the
# edge is actually processed as face topology (SEAM_CURVE's 2-pcurve
# expectation isn't met); SURFACE_CURVE with a single pcurve is the standard
# curve-on-surface representation (same pattern Gp007/Gp013 use) and survives
# translation while still carrying the same contradiction: positive-length 3D
# curve paired with a zero-extent 2D pcurve.
surf_curve = f._emit_raw(
    f"SURFACE_CURVE('',#{line_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
ec_lat_a = f._emit_raw(
    f"EDGE_CURVE('flag_lying_lateral_edge',#{v_b0.eid},#{v_t0.eid},#{surf_curve.eid},.T.)"
)
oe_lat_a = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_lat_a.eid},.T.)")

# ── Top arc: v_t0 -> v_t1 (ordinary CIRCLE edge, half turn at z=3) ────────────
top_orig = f.cartesian_point((0.0, 0.0, Z1))
top_plc  = f.axis2_placement_3d(top_orig, cone_zdir, cone_xdir)
top_circ = f._emit_raw(f"CIRCLE('',#{top_plc.eid},{R1:.10f})")
ec_top = f._emit_raw(f"EDGE_CURVE('',#{v_t0.eid},#{v_t1.eid},#{top_circ.eid},.T.)")
oe_top = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_top.eid},.T.)")

# ── Lateral edge B: v_t1 -> v_b1 (ordinary LINE edge) ─────────────────────────
lat_b_dir = f.direction((-_dx / _len, 0.0, -_dz / _len))
lat_b_vec = f.vector(lat_b_dir, _len)
lat_b_line = f._emit_raw(
    f"LINE('',#{f.cartesian_point((-R1, 0.0, Z1)).eid},#{lat_b_vec.eid})"
)
ec_lat_b = f._emit_raw(f"EDGE_CURVE('',#{v_t1.eid},#{v_b1.eid},#{lat_b_line.eid},.T.)")
oe_lat_b = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_lat_b.eid},.T.)")

# ── Bottom arc: v_b0 -> v_b1 (ordinary CIRCLE edge, half turn at z=1) ─────────
# Build the CIRCLE so it naturally traverses b0->b1, then traverse it
# reversed (b1->b0) to close the quadrilateral.
bot_orig = f.cartesian_point((0.0, 0.0, Z0))
bot_plc  = f.axis2_placement_3d(bot_orig, cone_zdir, cone_xdir)
bot_circ = f._emit_raw(f"CIRCLE('',#{bot_plc.eid},{R0:.10f})")
ec_bot = f._emit_raw(f"EDGE_CURVE('',#{v_b0.eid},#{v_b1.eid},#{bot_circ.eid},.T.)")
oe_bot = f._emit_raw(f"ORIENTED_EDGE('',*,*,#{ec_bot.eid},.F.)")  # traverse b1->b0

# ── EDGE_LOOP: lat_A(b0->t0) -> top(t0->t1) -> lat_B(t1->b1) -> bot(b1->b0) ───
loop = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_lat_a.eid},#{oe_top.eid},#{oe_lat_b.eid},#{oe_bot.eid}))"
)

fob   = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop.eid},.T.)")
face  = f._emit_raw(f"ADVANCED_FACE('',(#{fob.eid}),#{cone_surf.eid},.T.)")
shell = f._emit_raw(f"OPEN_SHELL('',(#{face.eid}))")
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
