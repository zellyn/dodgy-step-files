"""Tfa227 — ShapeFix_Face.ClearModes.init-all-modes

Mode-flag initialization (-1 default) prevents undefined comparisons in
NeedFix(); healer state precondition.

Mechanism: CLOSED_SHELL with ONE ADVANCED_FACE on a TOROIDAL_SURFACE. The face
has a standard quad EDGE_LOOP (4 line edges forming a unit square near the
surface origin). The ShapeFix_Face::ClearModes() initializer sets all fix-mode
flags to -1 (the "use global default" sentinel); without this initialization,
residual stack values could make NeedFix() comparisons return incorrect results,
causing the healer to skip or double-apply fix operations. The fixture exercises
the ClearModes → NeedFix dispatch path via a toroidal face where at least one
mode flag comparison is evaluated.

Byte assertions:
  - contains(b'TOROIDAL_SURFACE')
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa227",
    defect=(
        "CLOSED_SHELL: single ADVANCED_FACE on TOROIDAL_SURFACE; "
        "major_radius=2.0, minor_radius=0.5 (valid torus); "
        "quad EDGE_LOOP: 4 line edges forming 1×1 square in XY at z=0; "
        "ShapeFix_Face::ClearModes() sets all fix-mode flags to -1 sentinel; "
        "without -1 init: residual stack values corrupt NeedFix() comparisons; "
        "healer skips or double-applies fix operations on mode-flag mismatch; "
        "fixture exercises ClearModes → NeedFix dispatch via torus face; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

# ── TOROIDAL_SURFACE: valid torus (minor < major) ─────────────────────────────
# major=2.0, minor=0.5 — well-formed torus, exercises ClearModes NeedFix path
torus_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
torus_surf = f.toroidal_surface(torus_plc, 2.0, 0.5)

# ── Quad EDGE_LOOP: 1×1 square in XY plane ───────────────────────────────────
p_ll = f.cartesian_point((0.0, 0.0, 0.0))
p_lr = f.cartesian_point((1.0, 0.0, 0.0))
p_ur = f.cartesian_point((1.0, 1.0, 0.0))
p_ul = f.cartesian_point((0.0, 1.0, 0.0))

v_ll = f.vertex_point(p_ll)
v_lr = f.vertex_point(p_lr)
v_ur = f.vertex_point(p_ur)
v_ul = f.vertex_point(p_ul)

e_bot = f.edge_curve(v_ll, v_lr, f.line(p_ll, f.vector(f.direction(( 1.0, 0.0, 0.0)), 1.0)))
e_rgt = f.edge_curve(v_lr, v_ur, f.line(p_lr, f.vector(f.direction(( 0.0, 1.0, 0.0)), 1.0)))
e_top = f.edge_curve(v_ur, v_ul, f.line(p_ur, f.vector(f.direction((-1.0, 0.0, 0.0)), 1.0)))
e_lft = f.edge_curve(v_ul, v_ll, f.line(p_ul, f.vector(f.direction(( 0.0,-1.0, 0.0)), 1.0)))

face_loop = f.edge_loop([
    f.oriented_edge(e_bot, True),
    f.oriented_edge(e_rgt, True),
    f.oriented_edge(e_top, True),
    f.oriented_edge(e_lft, True),
])
face = f.advanced_face([f.face_outer_bound(face_loop)], torus_surf)

closed_sh = f.closed_shell([face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa227.stp")
