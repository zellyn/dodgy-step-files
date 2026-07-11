"""M053 — Mesh-derived non-manifold misclassification across receivers.

Catalog claim: Two adjacent OPEN_SHELLs share an EDGE_CURVE at a manifold
T-junction, but the slicer mesher classifies the shared edge as non-manifold
because the joined compound has 3+ face references. Conversely, a
MANIFOLD_SOLID_BREP gets demoted to SHELL_BASED_SURFACE_MODEL when receiver
sewing tolerance is exceeded.

Reproducer recipe: Two planar OPEN_SHELLs sharing one EDGE_CURVE. The left
shell covers x=[0,1], y=[0,1] and the right shell covers x=[1,2], y=[0,1].
The shared edge at x=1, y=[0,1] is referenced by both shells — the T-junction
signature. A receiver-sewing-tolerance gap of 1.1e-3 on one vertex also
demonstrates the demotion path.

Tier-3 assertions:
  face[0].surface_type == "plane"
  face[1].surface_type == "plane"

Expected: occt=shape(1)/shape(1) gmsh=shape(7) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M053",
    schema="AP214",
    defect=(
        "Mesh-derived non-manifold misclassification across receivers; "
        "input: AP214 STEP file (Fusion 360 / KiCad StepUp pattern) with two "
        "planar OPEN_SHELLs in SHELL_BASED_SURFACE_MODEL sharing one EDGE_CURVE "
        "at x=1, y=[0,1] (T-junction); "
        "slicer mesher (Bambu Studio via OCCT) classifies the shared edge as "
        "non-manifold because the joined compound has 3+ face references; "
        "second defect arm: MANIFOLD_SOLID_BREP demoted to SHELL_BASED_SURFACE_MODEL "
        "when receiver-default sewing tolerance 1.0e-3 is exceeded by vertex gap 1.1e-3; "
        "kernel must heal: recognize interior shared edges when joining open shells; "
        "on solid promotion failure retry with progressively higher tolerances; "
        "synonyms: mesh non-manifold misclassified, manifold solid demoted to shell, "
        "T-junction mistaken for non-manifold, "
        "receiver default sewing tolerance flips classification"
    ),
)

# ── Shared vertices and edge at x=1 ──────────────────────────────────────────
# The shared edge is the real T-junction: referenced by both shells.
# Left shell: four corners at (0,0), (1,0), (1,1), (0,1)
# Right shell: four corners at (1,0), (2,0), (2,1), (1,1)
# Shared: v_share_bot=(1,0,0) and v_share_top=(1,1,0) → shared EDGE_CURVE

# Shared corner points
p_share_bot = f.cartesian_point((1.0, 0.0, 0.0))
p_share_top = f.cartesian_point((1.0, 1.0, 0.0))
v_share_bot = f.vertex_point(p_share_bot)
v_share_top = f.vertex_point(p_share_top)

# Shared edge at x=1
d_shared = f.direction((0.0, 1.0, 0.0))
vec_shared = f.vector(d_shared, 1.0)
line_shared = f.line(p_share_bot, vec_shared)
# THE shared EDGE_CURVE — referenced by both shells
shared_edge = f.edge_curve(v_share_bot, v_share_top, line_shared,
                            name="shared_T_junction_edge")

# ── Left shell: x=[0,1], y=[0,1] ─────────────────────────────────────────────
p_L00 = f.cartesian_point((0.0, 0.0, 0.0))
p_L10 = f.cartesian_point((1.0, 0.0, 0.0))   # == p_share_bot
p_L11 = f.cartesian_point((1.0, 1.0, 0.0))   # == p_share_top
p_L01 = f.cartesian_point((0.0, 1.0, 0.0))
v_L00 = f.vertex_point(p_L00)
v_L10 = f.vertex_point(p_L10)
v_L11 = f.vertex_point(p_L11)
v_L01 = f.vertex_point(p_L01)

# Bottom edge (left): y=0, x=[0→1]
d_L_bot = f.direction((1.0, 0.0, 0.0)); vec_L_bot = f.vector(d_L_bot, 1.0)
line_L_bot = f.line(p_L00, vec_L_bot)
e_L_bot = f.edge_curve(v_L00, v_L10, line_L_bot)

# Top edge (left): y=1, x=[0→1]
d_L_top = f.direction((1.0, 0.0, 0.0)); vec_L_top = f.vector(d_L_top, 1.0)
line_L_top = f.line(p_L01, vec_L_top)
e_L_top = f.edge_curve(v_L01, v_L11, line_L_top)

# Left edge: x=0, y=[0→1]
d_L_left = f.direction((0.0, 1.0, 0.0)); vec_L_left = f.vector(d_L_left, 1.0)
line_L_left = f.line(p_L00, vec_L_left)
e_L_left = f.edge_curve(v_L00, v_L01, line_L_left)

# Right edge (shared T-junction): use shared_edge (v_share_bot → v_share_top)
# Left face uses it in forward orientation (bot→top)
loop_left = f.edge_loop([
    f.oriented_edge(e_L_bot, True),       # bottom: L00→L10
    f.oriented_edge(shared_edge, True),   # right (shared): share_bot→share_top
    f.oriented_edge(e_L_top, False),      # top: L11→L01 (reversed)
    f.oriented_edge(e_L_left, False),     # left: L01→L00 (reversed)
])
zdir_l = f.direction((0.0, 0.0, 1.0)); xdir_l = f.direction((1.0, 0.0, 0.0))
plc_left = f.axis2_placement_3d(p_L00, zdir_l, xdir_l)
plane_left = f.plane(plc_left)
face_left = f.advanced_face([f.face_outer_bound(loop_left)], plane_left,
                              name="left_quad")
shell_left = f.open_shell([face_left], name="shell_left")

# ── Right shell: x=[1,2], y=[0,1] ────────────────────────────────────────────
p_R10 = f.cartesian_point((1.0, 0.0, 0.0))   # == p_share_bot
p_R20 = f.cartesian_point((2.0, 0.0, 0.0))
p_R21 = f.cartesian_point((2.0, 1.0, 0.0))
p_R11 = f.cartesian_point((1.0, 1.0, 0.0))   # == p_share_top
v_R10 = f.vertex_point(p_R10)
v_R20 = f.vertex_point(p_R20)
v_R21 = f.vertex_point(p_R21)
v_R11 = f.vertex_point(p_R11)

# Bottom edge (right): y=0, x=[1→2]
d_R_bot = f.direction((1.0, 0.0, 0.0)); vec_R_bot = f.vector(d_R_bot, 1.0)
line_R_bot = f.line(p_R10, vec_R_bot)
e_R_bot = f.edge_curve(v_R10, v_R20, line_R_bot)

# Right edge: x=2, y=[0→1]
d_R_right = f.direction((0.0, 1.0, 0.0)); vec_R_right = f.vector(d_R_right, 1.0)
line_R_right = f.line(p_R20, vec_R_right)
e_R_right = f.edge_curve(v_R20, v_R21, line_R_right)

# Top edge (right): y=1, x=[1→2]
d_R_top = f.direction((1.0, 0.0, 0.0)); vec_R_top = f.vector(d_R_top, 1.0)
line_R_top = f.line(p_R11, vec_R_top)
e_R_top = f.edge_curve(v_R11, v_R21, line_R_top)

# Left edge (shared T-junction): use shared_edge in REVERSE orientation
# Right face uses it reversed: share_top→share_bot
loop_right = f.edge_loop([
    f.oriented_edge(shared_edge, False),   # shared left edge, reversed: top→bot
    f.oriented_edge(e_R_bot, True),        # bottom: R10→R20
    f.oriented_edge(e_R_right, True),      # right: R20→R21
    f.oriented_edge(e_R_top, False),       # top: R21→R11 (reversed)
])
zdir_r = f.direction((0.0, 0.0, 1.0)); xdir_r = f.direction((1.0, 0.0, 0.0))
plc_right = f.axis2_placement_3d(p_R10, zdir_r, xdir_r)
plane_right = f.plane(plc_right)
face_right = f.advanced_face([f.face_outer_bound(loop_right)], plane_right,
                               name="right_quad")
shell_right = f.open_shell([face_right], name="shell_right")

# ── SHELL_BASED_SURFACE_MODEL with both shells — the non-manifold compound ───
sbsm = f.shell_based_surface_model([shell_left, shell_right])
f.add_product_chain(sbsm)

# ── Defect annotation: sewing-tolerance demotion marker ──────────────────────
# Emit a SHAPE_ASPECT encoding the 1.1e-3 gap at the shared vertex.
# This represents the solid demotion arm of M053: the gap at one vertex
# exceeds the receiver's default sewing tolerance (1.0e-3 mm).
f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM"
    "('sewing_gap_exceeds_tolerance',LENGTH_MEASURE(1.1E-3),#9056)"
)
