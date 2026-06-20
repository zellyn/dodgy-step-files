"""Twi037 — Free bounds need joining (sewing) — adjacent faces don't share edge.

Catalog claim: After Boolean op or translation, two faces that should share an
edge each carry their own copy of it; geometrically coincident, topologically
separate. The shell appears to have free / dangling edges where it actually has
duplicated edges. Stitching pairs the duplicates into shared edges and
reconstructs the closed shell.

Mechanism IS the pair of EDGE_LOOPs on two planar ADVANCED_FACEs that each
reference a separate EDGE_CURVE at the shared boundary: edge_shared_A (used by
face_left) and edge_shared_B (used by face_right) are geometrically coincident
but are distinct STEP entities. Both EDGE_CURVEs ARE wired into their
respective EDGE_LOOPs, which ARE referenced by FACE_OUTER_BOUNDs in two
ADVANCED_FACEs inside the same OPEN_SHELL; never orphaned. The sewing pass
must identify the geometrically coincident free-edge pair and merge them into a
single shared edge, closing the shell.

Reproducer: OPEN_SHELL of two planar faces side-by-side; the shared vertical
edge is present as two separate EDGE_CURVE instances (one per face).

Byte assertions:
  - count_entity_def(b'PLANE') == 2
  - count_entity_def(b'EDGE_LOOP') == 2

Tier-3 assertions:
  - n_edges_total >= 8
  - face[0].surface_type == "plane"
  - face[1].surface_type == "plane"

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi037",
    defect=(
        "OPEN_SHELL with two ADVANCED_FACEs, each on a separate PLANE; "
        "face_left: 2x2 square at x in [0,1]; "
        "face_right: 2x2 square at x in [1,2]; "
        "shared boundary is the vertical edge at x=1 (y: 0→2); "
        "face_left EDGE_LOOP references edge_shared_A (v_lt→v_lb on x=1 line); "
        "face_right EDGE_LOOP references edge_shared_B — a DISTINCT EDGE_CURVE "
        "with separate LINE and VERTEX_POINT entities at the same x=1 positions; "
        "two geometrically coincident EDGE_CURVEs in separate EDGE_LOOPs IS the mechanism "
        "(unstitched seam: free/dangling edges from un-sewn shell); "
        "both EDGE_LOOPs ARE wired into FACE_OUTER_BOUNDs in two ADVANCED_FACEs in OPEN_SHELL; "
        "sewing pass must merge the coincident pair into one shared edge"
    ),
)

# ── Plane for face_left: normal +Z, origin at (0,0,0) ────────────────────────
pl_L_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_L_zdir = f.direction((0.0, 0.0, 1.0))
pl_L_xdir = f.direction((1.0, 0.0, 0.0))
pl_L_plc  = f.axis2_placement_3d(pl_L_orig, pl_L_zdir, pl_L_xdir)
plane_L   = f._emit_raw(f"PLANE('',#{pl_L_plc.eid})")

# ── Plane for face_right: same orientation, shifted origin ────────────────────
pl_R_orig = f.cartesian_point((1.0, 0.0, 0.0))
pl_R_zdir = f.direction((0.0, 0.0, 1.0))
pl_R_xdir = f.direction((1.0, 0.0, 0.0))
pl_R_plc  = f.axis2_placement_3d(pl_R_orig, pl_R_zdir, pl_R_xdir)
plane_R   = f._emit_raw(f"PLANE('',#{pl_R_plc.eid})")

# ── Vertices for face_left (x in [0,1]) ───────────────────────────────────────
v_ll_bl = f.vertex_point(f.cartesian_point((0.0, 0.0, 0.0)))  # left-bottom-left
v_ll_br = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))  # left-bottom-right
v_ll_tr = f.vertex_point(f.cartesian_point((1.0, 2.0, 0.0)))  # left-top-right
v_ll_tl = f.vertex_point(f.cartesian_point((0.0, 2.0, 0.0)))  # left-top-left

# ── Vertices for face_right (x in [1,2]) — separate entities at shared boundary
v_lr_bl = f.vertex_point(f.cartesian_point((1.0, 0.0, 0.0)))  # right-bottom-left (dup)
v_lr_br = f.vertex_point(f.cartesian_point((2.0, 0.0, 0.0)))  # right-bottom-right
v_lr_tr = f.vertex_point(f.cartesian_point((2.0, 2.0, 0.0)))  # right-top-right
v_lr_tl = f.vertex_point(f.cartesian_point((1.0, 2.0, 0.0)))  # right-top-left (dup)

# ── Face_left edges ───────────────────────────────────────────────────────────
# Bottom: v_ll_bl → v_ll_br
lf_bot_dir  = f.direction((1.0, 0.0, 0.0))
lf_bot_vec  = f.vector(lf_bot_dir, 1.0)
lf_bot_line = f.line(f.cartesian_point((0.0, 0.0, 0.0)), lf_bot_vec)
lf_bot_ec   = f.edge_curve(v_ll_bl, v_ll_br, lf_bot_line)
oe_lf_bot   = f.oriented_edge(lf_bot_ec, True)

# Right (shared A): v_ll_br → v_ll_tr  — IS one half of the coincident pair
lf_rgt_dir  = f.direction((0.0, 1.0, 0.0))
lf_rgt_vec  = f.vector(lf_rgt_dir, 2.0)
lf_rgt_line = f.line(f.cartesian_point((1.0, 0.0, 0.0)), lf_rgt_vec)
edge_shared_A = f.edge_curve(v_ll_br, v_ll_tr, lf_rgt_line)
oe_shared_A   = f.oriented_edge(edge_shared_A, True)

# Top: v_ll_tr → v_ll_tl
lf_top_dir  = f.direction((-1.0, 0.0, 0.0))
lf_top_vec  = f.vector(lf_top_dir, 1.0)
lf_top_line = f.line(f.cartesian_point((1.0, 2.0, 0.0)), lf_top_vec)
lf_top_ec   = f.edge_curve(v_ll_tr, v_ll_tl, lf_top_line)
oe_lf_top   = f.oriented_edge(lf_top_ec, True)

# Left: v_ll_tl → v_ll_bl
lf_lft_dir  = f.direction((0.0, -1.0, 0.0))
lf_lft_vec  = f.vector(lf_lft_dir, 2.0)
lf_lft_line = f.line(f.cartesian_point((0.0, 2.0, 0.0)), lf_lft_vec)
lf_lft_ec   = f.edge_curve(v_ll_tl, v_ll_bl, lf_lft_line)
oe_lf_lft   = f.oriented_edge(lf_lft_ec, True)

loop_L = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_lf_bot.eid},#{oe_shared_A.eid},"
    f"#{oe_lf_top.eid},#{oe_lf_lft.eid}))"
)

# ── Face_right edges ──────────────────────────────────────────────────────────
# Left (shared B): v_lr_tl → v_lr_bl — DISTINCT EDGE_CURVE at x=1 IS the mechanism
rf_lft_dir  = f.direction((0.0, -1.0, 0.0))
rf_lft_vec  = f.vector(rf_lft_dir, 2.0)
rf_lft_line = f.line(f.cartesian_point((1.0, 2.0, 0.0)), rf_lft_vec)
edge_shared_B = f.edge_curve(v_lr_tl, v_lr_bl, rf_lft_line)
oe_shared_B   = f.oriented_edge(edge_shared_B, True)

# Bottom: v_lr_bl → v_lr_br
rf_bot_dir  = f.direction((1.0, 0.0, 0.0))
rf_bot_vec  = f.vector(rf_bot_dir, 1.0)
rf_bot_line = f.line(f.cartesian_point((1.0, 0.0, 0.0)), rf_bot_vec)
rf_bot_ec   = f.edge_curve(v_lr_bl, v_lr_br, rf_bot_line)
oe_rf_bot   = f.oriented_edge(rf_bot_ec, True)

# Right: v_lr_br → v_lr_tr
rf_rgt_dir  = f.direction((0.0, 1.0, 0.0))
rf_rgt_vec  = f.vector(rf_rgt_dir, 2.0)
rf_rgt_line = f.line(f.cartesian_point((2.0, 0.0, 0.0)), rf_rgt_vec)
rf_rgt_ec   = f.edge_curve(v_lr_br, v_lr_tr, rf_rgt_line)
oe_rf_rgt   = f.oriented_edge(rf_rgt_ec, True)

# Top: v_lr_tr → v_lr_tl
rf_top_dir  = f.direction((-1.0, 0.0, 0.0))
rf_top_vec  = f.vector(rf_top_dir, 1.0)
rf_top_line = f.line(f.cartesian_point((2.0, 2.0, 0.0)), rf_top_vec)
rf_top_ec   = f.edge_curve(v_lr_tr, v_lr_tl, rf_top_line)
oe_rf_top   = f.oriented_edge(rf_top_ec, True)

loop_R = f._emit_raw(
    f"EDGE_LOOP('',(#{oe_shared_B.eid},#{oe_rf_bot.eid},"
    f"#{oe_rf_rgt.eid},#{oe_rf_top.eid}))"
)

# Wire both faces into same OPEN_SHELL — never orphan.
fob_L  = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop_L.eid},.T.)")
fob_R  = f._emit_raw(f"FACE_OUTER_BOUND('',#{loop_R.eid},.T.)")
face_L = f._emit_raw(f"ADVANCED_FACE('',(#{fob_L.eid}),#{plane_L.eid},.T.)")
face_R = f._emit_raw(f"ADVANCED_FACE('',(#{fob_R.eid}),#{plane_R.eid},.T.)")
shell  = f._emit_raw(f"OPEN_SHELL('',(#{face_L.eid},#{face_R.eid}))")
sbsm   = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
