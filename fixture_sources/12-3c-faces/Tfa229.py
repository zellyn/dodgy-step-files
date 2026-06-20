"""Tfa229 — ShapeFix_Face.FixLoopWire.orientation-handling

Seam-edge reversal for dual-edge UV-periodic representation; non-seam edges
skip reversal logic.

Mechanism: CLOSED_SHELL with ONE ADVANCED_FACE on a CYLINDRICAL_SURFACE.
The face uses a full-revolution 4-edge EDGE_LOOP: seam edge appears twice
(forward and reversed) flanked by top and bottom circles. The
ShapeFix_Face::FixLoopWire() orientation-handling path evaluates each edge
to determine if it is the seam; seam edges receive reversal treatment while
non-seam edges (the circles) skip the reversal logic. The fixture exercises
the dual-edge seam orientation dispatch path.

Byte assertions:
  - contains(b'CYLINDRICAL_SURFACE')
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa229",
    defect=(
        "CLOSED_SHELL: single ADVANCED_FACE on CYLINDRICAL_SURFACE; "
        "radius=1.0, height=1.5; standard 4-edge EDGE_LOOP: "
        "seam(T) + top-circle(T) + seam(F) + bottom-circle(F); "
        "ShapeFix_Face::FixLoopWire() orientation-handling: "
        "seam edges receive reversal treatment; "
        "non-seam edges (circles) skip reversal logic; "
        "dual-edge seam orientation dispatch evaluated; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

R = 1.0
H = 1.5

# ── CYLINDRICAL_SURFACE ───────────────────────────────────────────────────────
cyl_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
cyl_surf = f.cylindrical_surface(cyl_plc, R)

# ── Seam vertices ─────────────────────────────────────────────────────────────
pt_bot = f.cartesian_point((R, 0.0, 0.0))
pt_top = f.cartesian_point((R, 0.0, H))
v_bot = f.vertex_point(pt_bot)
v_top = f.vertex_point(pt_top)

# ── Seam edge: vertical line bot→top ─────────────────────────────────────────
seam_edge = f.edge_curve(
    v_bot, v_top,
    f.line(pt_bot, f.vector(f.direction((0.0, 0.0, 1.0)), H))
)

# ── Bottom circle: z=0, axis -Z (full revolution) ─────────────────────────────
bot_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, -1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
bot_circle = f.circle(bot_plc, R)
bot_edge = f.edge_curve(v_bot, v_bot, bot_circle)

# ── Top circle: z=H, axis +Z (full revolution) ────────────────────────────────
top_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, H)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
top_circle = f.circle(top_plc, R)
top_edge = f.edge_curve(v_top, v_top, top_circle)

# ── EDGE_LOOP: seam(T) + top(T) + seam(F) + bot(F) ──────────────────────────
# Seam edge used twice: forward then reversed — exercises orientation-handling
cyl_loop = f.edge_loop([
    f.oriented_edge(seam_edge, True),
    f.oriented_edge(top_edge, True),
    f.oriented_edge(seam_edge, False),
    f.oriented_edge(bot_edge, False),
])
face = f.advanced_face([f.face_outer_bound(cyl_loop)], cyl_surf)

closed_sh = f.closed_shell([face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa229.stp")
