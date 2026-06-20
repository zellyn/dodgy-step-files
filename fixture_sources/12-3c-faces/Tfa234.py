"""Tfa234 — FixAddNaturalBound seam-edge exclusion

Single-period cylindrical face with degenerate bottom/top loops and explicit
seam edge. Tests natural-boundary rejection logic when seam-edge is present;
validates myFixAddNaturalBoundMode conditional handling.

Mechanism: CLOSED_SHELL with ONE ADVANCED_FACE on a CYLINDRICAL_SURFACE.
The face has a 4-edge EDGE_LOOP: bottom degenerate circle, seam line (forward),
top degenerate circle, seam line (reversed). The seam edge is used twice in the
loop — once forward and once reversed — creating the classic cylindrical-seam
topology. When ShapeFix_Face::FixAddNaturalBound() evaluates whether to insert
a natural boundary, it checks whether a seam edge is already present on the
periodic surface. Finding the seam, it suppresses the natural-boundary insertion
(myFixAddNaturalBoundMode conditional), exercising the seam-edge exclusion path.

Byte assertions:
  - contains(b'CYLINDRICAL_SURFACE')
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa234",
    defect=(
        "CLOSED_SHELL: single ADVANCED_FACE on CYLINDRICAL_SURFACE; "
        "radius=1.5, axis=Z; 4-edge EDGE_LOOP: bot_circle(degenerate) + seam_line(T) "
        "+ top_circle(degenerate) + seam_line(F); "
        "seam edge used forward+reversed: classic cylindrical-seam topology; "
        "ShapeFix_Face::FixAddNaturalBound(): seam-edge exclusion: "
        "myFixAddNaturalBoundMode conditional suppresses natural boundary when seam present; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

R = 1.5
H = 3.0

# ── CYLINDRICAL_SURFACE ───────────────────────────────────────────────────────
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_plc  = f.axis2_placement_3d(cyl_orig, cyl_zdir, cyl_xdir)
cyl_surf = f._emit_raw(f"CYLINDRICAL_SURFACE('cyl',#{cyl_plc.eid},{R})")

# ── Vertices ──────────────────────────────────────────────────────────────────
pt_bot = f.cartesian_point((R, 0.0, 0.0))
pt_top = f.cartesian_point((R, 0.0, H))
v_bot  = f.vertex_point(pt_bot)
v_top  = f.vertex_point(pt_top)

# ── Seam edge: vertical line along x=R from z=0 to z=H ──────────────────────
seam_line = f.line(pt_bot, f.vector(f.direction((0.0, 0.0, 1.0)), H))
seam_edge = f.edge_curve(v_bot, v_top, seam_line)

# ── Bottom degenerate circle at z=0 ──────────────────────────────────────────
bot_ctr  = f.cartesian_point((0.0, 0.0, 0.0))
bot_plc  = f.axis2_placement_3d(bot_ctr, f.direction((0.0, 0.0, 1.0)), cyl_xdir)
bot_circ = f.circle(bot_plc, R)
bot_edge = f.edge_curve(v_bot, v_bot, bot_circ)

# ── Top degenerate circle at z=H ─────────────────────────────────────────────
top_ctr  = f.cartesian_point((0.0, 0.0, H))
top_plc  = f.axis2_placement_3d(top_ctr, f.direction((0.0, 0.0, 1.0)), cyl_xdir)
top_circ = f.circle(top_plc, R)
top_edge = f.edge_curve(v_top, v_top, top_circ)

# ── EDGE_LOOP: bot(T) + seam(T) + top(T) + seam(F) ──────────────────────────
# Seam edge used forward then reversed — classic cylindrical seam topology.
# FixAddNaturalBound detects seam presence and skips natural-boundary insertion.
face_loop = f.edge_loop([
    f.oriented_edge(bot_edge,  True),
    f.oriented_edge(seam_edge, True),
    f.oriented_edge(top_edge,  True),
    f.oriented_edge(seam_edge, False),
])
face = f.advanced_face([f.face_outer_bound(face_loop)], cyl_surf)

closed_sh = f.closed_shell([face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa234.stp")
