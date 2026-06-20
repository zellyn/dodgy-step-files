"""Tfa064 — Missing-seam reconstruction fails on ADVANCED_FACE on CYLINDRICAL_SURFACE
whose wire contains a partial seam line plus horizontal CIRCLE arcs.

Catalog claim: A face on a closed surface has a wire that includes part of the
seam edge but not all. The seam-fix routine adds the missing portion to the wire
but inserts it at the wrong position, producing a wire whose edges are no longer
in topological order. Wire becomes invalid.

Mechanism: CLOSED_SHELL with cylindrical face (cylinder + top and bottom caps).
  face[0]: ADVANCED_FACE on CYLINDRICAL_SURFACE. Wire has the seam at U=0 for
    the lower half V=[0, h/2] (explicit seam_lower edge) but only a full seam
    edge (not split) for the upper portion — this creates a partial-seam wire
    where the seam fix must splice the missing upper half into topological order.
    Concretely: wire traversal is
       seam_lower (V=0..h/2) .T.  →  top_circle (full revolution) .T.
       seam_lower .F.             →  mid_circle (at V=h/2) .F.
    The seam at V=[h/2..h] is missing; seam-fix inserts it at the tail
    (wrong position) instead of between seam_lower.F. and top_circle.

  faces[1,2]: bottom disc cap and top disc cap.

Tier-3 assertions:
  face[0].surface_type == "cylinder"
  n_edges_total >= 4
  n_vertices_total >= 8
  brepcheck.valid == True

Expected: occt=shape(1)/shape(1) gmsh=shape(7) ifc=schema_n/a
"""
import math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa064",
    defect=(
        "CLOSED_SHELL: cylindrical face (r=5, h=10) whose EDGE_LOOP has seam at U=0 "
        "only for lower half V=[0,5] (seam_lower edge), plus top_circle and mid_circle "
        "arcs; seam for upper half V=[5,10] is absent; "
        "missing-seam reconstruction inserts upper-half seam at wire tail instead of "
        "adjacent to seam_lower.F. — misordered seam splice; "
        "faces[1,2] are valid bottom/top disc caps; "
        "defect IS on live cylindrical face traversal path"
    ),
)

R = 5.0
H = 10.0
H2 = H / 2.0  # = 5.0

# ── Key 3D points ──────────────────────────────────────────────────────────────
# Seam line runs at (R, 0, z) for z in [0, H]
# We have 3 horizontal levels: z=0 (bot), z=H2 (mid), z=H (top)
pt_seam_bot = f.cartesian_point((R, 0.0, 0.0))
pt_seam_mid = f.cartesian_point((R, 0.0, H2))
pt_seam_top = f.cartesian_point((R, 0.0, H))

v_seam_bot = f.vertex_point(pt_seam_bot)
v_seam_mid = f.vertex_point(pt_seam_mid)
v_seam_top = f.vertex_point(pt_seam_top)

# ── Seam lower edge: v_seam_bot → v_seam_mid (vertical, lower half) ───────────
seam_lower_line = f.line(pt_seam_bot, f.vector(f.direction((0.0, 0.0, 1.0)), H2))
seam_lower_ec   = f.edge_curve(v_seam_bot, v_seam_mid, seam_lower_line)

# ── Seam upper edge: v_seam_mid → v_seam_top (vertical, upper half) ───────────
# This is the "missing" seam half — present in geometry but NOT in wire;
# seam-fix must insert it at the correct position (adjacent to seam_lower.F.)
seam_upper_line = f.line(pt_seam_mid, f.vector(f.direction((0.0, 0.0, 1.0)), H2))
seam_upper_ec   = f.edge_curve(v_seam_mid, v_seam_top, seam_upper_line)

# ── Circles (horizontal) ───────────────────────────────────────────────────────
# Bottom circle: z=0, closed edge (start==end==v_seam_bot)
bot_ctr = f.cartesian_point((0.0, 0.0, 0.0))
bot_ax  = f.direction((0.0, 0.0, -1.0))  # outward (downward)
bot_ref = f.direction((1.0, 0.0, 0.0))
bot_circ_ec = f.edge_curve(
    v_seam_bot, v_seam_bot,
    f.circle(f.axis2_placement_3d(bot_ctr, bot_ax, bot_ref), R)
)

# Mid circle: z=H2, closed edge (start==end==v_seam_mid)
mid_ctr = f.cartesian_point((0.0, 0.0, H2))
mid_ax  = f.direction((0.0, 0.0,  1.0))
mid_ref = f.direction((1.0, 0.0, 0.0))
mid_circ_ec = f.edge_curve(
    v_seam_mid, v_seam_mid,
    f.circle(f.axis2_placement_3d(mid_ctr, mid_ax, mid_ref), R)
)

# Top circle: z=H, closed edge (start==end==v_seam_top)
top_ctr = f.cartesian_point((0.0, 0.0, H))
top_ax  = f.direction((0.0, 0.0,  1.0))  # outward (upward)
top_ref = f.direction((1.0, 0.0, 0.0))
top_circ_ec = f.edge_curve(
    v_seam_top, v_seam_top,
    f.circle(f.axis2_placement_3d(top_ctr, top_ax, top_ref), R)
)

# ── CYLINDRICAL_SURFACE ────────────────────────────────────────────────────────
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_ax   = f.direction((0.0, 0.0, 1.0))
cyl_ref  = f.direction((1.0, 0.0, 0.0))
cyl_surf = f.cylindrical_surface(f.axis2_placement_3d(cyl_orig, cyl_ax, cyl_ref), R)

# ── face[0]: cylindrical face with partial-seam wire (THE DEFECT) ─────────────
# Wire has seam_lower for the lower half, but seam_upper is absent.
# The seam-fix must splice seam_upper into correct position.
# Wire traversal (defective — missing seam_upper):
#   seam_lower .T. (bot→mid) → mid_circle .T. (mid→mid, full rev)
#   seam_lower .F. (mid→bot) → bot_circle .F. (bot→bot, full rev reversed)
# Correct wire should be (with seam-fix applied):
#   seam_lower .T. → seam_upper .T. → top_circle .T.
#   seam_upper .F. → seam_lower .F. → bot_circle .F.
# But seam-fix inserts seam_upper at the tail instead.
cyl_loop = f.edge_loop([
    f.oriented_edge(seam_lower_ec,  True),   # bot→mid (lower seam going up)
    f.oriented_edge(mid_circ_ec,    True),   # full revolution at mid-height
    f.oriented_edge(seam_lower_ec,  False),  # mid→bot (lower seam going down)
    f.oriented_edge(bot_circ_ec,    False),  # full revolution at bottom (reversed)
])
face0 = f.advanced_face([f.face_outer_bound(cyl_loop)], cyl_surf)

# ── face[1]: bottom disc cap ───────────────────────────────────────────────────
bot_disc_orig = f.cartesian_point((0.0, 0.0, 0.0))
bot_plane     = f.plane(f.axis2_placement_3d(
    bot_disc_orig, f.direction((0.0, 0.0, -1.0)), f.direction((1.0, 0.0, 0.0))
))
face1 = f.advanced_face(
    [f.face_outer_bound(f.edge_loop([f.oriented_edge(bot_circ_ec, True)]))],
    bot_plane
)

# ── face[2]: top disc cap ──────────────────────────────────────────────────────
top_disc_orig = f.cartesian_point((0.0, 0.0, H))
top_plane     = f.plane(f.axis2_placement_3d(
    top_disc_orig, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0))
))
face2 = f.advanced_face(
    [f.face_outer_bound(f.edge_loop([f.oriented_edge(top_circ_ec, True)]))],
    top_plane
)

# ── CLOSED_SHELL + MANIFOLD_SOLID_BREP ────────────────────────────────────────
closed_sh = f.closed_shell([face0, face1, face2])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa064.stp")
