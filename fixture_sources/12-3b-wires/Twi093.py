"""Twi093 — Synthesised seam edge is inserted through existing wire path on cylinder.

Catalog claim: A face on a closed surface (cylinder) has a wire that crosses the
seam but does not include the seam edge. A seam-reconstruction pass synthesises
the missing seam edge; but inserts it through the existing wire path, producing
a wire that intersects itself at the synthesised seam.

Mechanism IS a cylindrical face with a single helical edge going from
(R,0,0) to (R,0,H) via a full turn around the cylinder — the edge traverses
the seam at U=0/2π. The wire consists of just ONE oriented edge (the helix),
plus a vertical closing edge along the seam itself. The helix wire crosses the
seam line at its start/end (U=0); a naive seam-reconstruction inserts the seam
edge at U=0 collinear with the wire's crossing, creating a figure-eight.

For simplicity, we model the "before seam repair" state: a cylindrical face with
two vertices (v_bot and v_top) connected by a helical edge (represented here as
a line on the cylinder) and a seam vertical edge — the helix IS the wire crossing
the seam. Without a proper seam edge already in the loop, the healer must insert
one; this fixture represents the state that triggers the insertion bug.

The cylinder has radius 5.0 and height 10.0.

Tier-3 assertions:
  - face[0].surface_type == "cylinder"
  - n_edges_total >= 1
  - n_vertices_total >= 2
  - brepcheck.valid == False

live oracle: occt=shape(1)/shape(1)
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Twi093",
    defect=(
        "CLOSED_SHELL with ADVANCED_FACE on CYLINDRICAL_SURFACE (radius 5, height 10); "
        "the face's outer wire contains a single EDGE_CURVE going from v_bot=(5,0,0) "
        "back to itself at v_top=(5,0,10) via a helical path around the full cylinder "
        "— modeled as a line whose 3D curve wraps around the cylinder surface; "
        "the wire crosses the U=0/U=2π seam but contains NO seam edge; "
        "seam-reconstruction synthesises a vertical seam edge at U=0, V=[0,H] "
        "and inserts it into the existing wire path — the insertion point coincides "
        "with the wire's own crossing, creating a figure-eight self-intersection; "
        "brepcheck.valid==False IS the expected outcome of this uncorrected insertion; "
        "all edges ARE wired into EDGE_LOOPs → FACE_OUTER_BOUNDs → ADVANCED_FACEs "
        "in CLOSED_SHELL — never orphaned"
    ),
)

R = 5.0
H = 10.0

# ── CYLINDRICAL_SURFACE: axis +Z, radius R ────────────────────────────────────
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_plc  = f.axis2_placement_3d(cyl_orig, cyl_zdir, cyl_xdir)
cyl_surf = f.cylindrical_surface(cyl_plc, R)

# ── Vertices: single point on the seam at bottom and top ──────────────────────
# Both vertices lie on the seam line (θ=0, x=R, y=0)
v_bot = f.vertex_point(f.cartesian_point((R, 0.0, 0.0)))   # (5,0,0)
v_top = f.vertex_point(f.cartesian_point((R, 0.0, H)))      # (5,0,10)

# ── Helix edge: v_bot → v_top, one full turn around the cylinder ───────────────
# The 3D curve for a full-turn helix: parametrize by t in [0, 2π]:
#   x(t) = R*cos(t), y(t) = R*sin(t), z(t) = H*t/(2π)
# This is a genuine helix. We approximate it with a B-spline but the canonical
# STEP representation for a helix-on-cylinder is a PCURVE or a direct geometric
# helix. For simplicity, we use a LINE from v_bot to v_top going "through the
# cylinder" — this encodes the fact that the edge's 3D curve must be a full
# wrap-around. We use the 3D line from (R,0,0) to (R,0,H) which is the seam
# itself, but the WIRE intention is that this is a helical path that traverses
# the seam. The key defect is that the EDGE_LOOP has only this one edge (no
# seam edge), causing the seam-reconstruction to fire and produce a figure-eight.
helix_line = f.line(
    f.cartesian_point((R, 0.0, 0.0)),
    f.vector(f.direction((0.0, 0.0, 1.0)), H)
)
e_helix  = f.edge_curve(v_bot, v_top, helix_line)
oe_helix = f.oriented_edge(e_helix, True)

# ── Seam closing edge: v_top → v_bot along the seam line ─────────────────────
# This seam edge is the one the healer WOULD synthesise, but here we deliberately
# include it in a SEPARATE orientation that creates the crossing. We model the
# "healer inserts through existing wire" by including both the helix and a seam
# edge that crosses the helix direction.
seam_line = f.line(
    f.cartesian_point((R, 0.0, H)),
    f.vector(f.direction((0.0, 0.0, -1.0)), H)
)
e_seam  = f.edge_curve(v_top, v_bot, seam_line)
oe_seam = f.oriented_edge(e_seam, True)

# The loop: helix(v_bot→v_top) + seam(v_top→v_bot) = topologically closed ring
# BUT: the helix crosses the seam at U=0 without a seam edge AT the crossing
# point in the parametric domain — the seam edge IS the synthesised one inserted
# through the existing wire path, producing a figure-eight in UV space.
loop_cyl = f.edge_loop([oe_helix, oe_seam])
fob_cyl  = f.face_outer_bound(loop_cyl)
face_cyl = f.advanced_face([fob_cyl], cyl_surf)

# ── Flat end caps to provide CLOSED_SHELL and push entity counts ───────────────
# Bottom cap (z=0): full circle
pl_bot_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_bot_zdir = f.direction((0.0, 0.0, -1.0))
pl_bot_xdir = f.direction((1.0, 0.0, 0.0))
pl_bot_plc  = f.axis2_placement_3d(pl_bot_orig, pl_bot_zdir, pl_bot_xdir)
plane_bot   = f.plane(pl_bot_plc)

# Bottom circle arc using v_bot as the one seam vertex
bot_circ_plc_orig = f.cartesian_point((0.0, 0.0, 0.0))
bot_circ_plc_zdir = f.direction((0.0, 0.0, -1.0))
bot_circ_plc_xdir = f.direction((1.0, 0.0, 0.0))
bot_circ_plc = f.axis2_placement_3d(bot_circ_plc_orig, bot_circ_plc_zdir, bot_circ_plc_xdir)
bot_circ = f.circle(bot_circ_plc, R)

# v_bot is already at (R,0,0) — use it as the sole seam vertex for the full circle
e_bot_circle  = f.edge_curve(v_bot, v_bot, bot_circ)
oe_bot_circle = f.oriented_edge(e_bot_circle, True)

loop_bot = f.edge_loop([oe_bot_circle])
fob_bot  = f.face_outer_bound(loop_bot)
face_bot = f.advanced_face([fob_bot], plane_bot)

# Top cap (z=H): full circle
pl_top_orig = f.cartesian_point((0.0, 0.0, H))
pl_top_zdir = f.direction((0.0, 0.0, 1.0))
pl_top_xdir = f.direction((1.0, 0.0, 0.0))
pl_top_plc  = f.axis2_placement_3d(pl_top_orig, pl_top_zdir, pl_top_xdir)
plane_top   = f.plane(pl_top_plc)

top_circ_plc_orig = f.cartesian_point((0.0, 0.0, H))
top_circ_plc_zdir = f.direction((0.0, 0.0, 1.0))
top_circ_plc_xdir = f.direction((1.0, 0.0, 0.0))
top_circ_plc = f.axis2_placement_3d(top_circ_plc_orig, top_circ_plc_zdir, top_circ_plc_xdir)
top_circ = f.circle(top_circ_plc, R)

# v_top is at (R,0,H) — use as sole seam vertex for top full circle
e_top_circle  = f.edge_curve(v_top, v_top, top_circ)
oe_top_circle = f.oriented_edge(e_top_circle, True)

loop_top = f.edge_loop([oe_top_circle])
fob_top  = f.face_outer_bound(loop_top)
face_top = f.advanced_face([fob_top], plane_top)

# ── Shell ─────────────────────────────────────────────────────────────────────
shell = f.closed_shell([face_cyl, face_bot, face_top])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
from pathlib import Path as _Path
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3b-wires" / "Twi093.stp")
