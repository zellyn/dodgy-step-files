"""Tfa163 — ShapeFix_Face.FixSplitFace splitter-along-edge.

Catalog claim: Face with splitter line (virtual dividing edge) that
geometrically coincides with existing outer boundary edge. FixSplitFace fails
to detect coincidence and produces duplicate faces instead of merging.
Fixture: rectangular face (2.0 x 1.0 PLANE) simulates scenario where splitter
at interior u=1.0 aligns with outer edge.

Mechanism: OPEN_SHELL with ONE ADVANCED_FACE: a 2.0×1.0 rectangle on a
PLANE surface. The right-hand edge at x=2.0 is the "outer boundary edge"
that geometrically coincides with the virtual splitter at u=2.0.
A second inner edge (FACE_BOUND) at x=2.0 is added — same x position as the
outer right edge — to simulate the splitter-coincidence scenario.
FixSplitFace fails to detect that the splitter is coincident with the outer
boundary edge.
Defect IS on live face traversal path.

Byte assertions:
  - contains(b'ADVANCED_FACE')
  - contains(b'FACE_OUTER_BOUND')

Tier-3 assertion: n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(1) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa163",
    defect=(
        "OPEN_SHELL: single ADVANCED_FACE on PLANE (2.0×1.0 rectangle); "
        "outer right edge at x=2.0 (v_tr→v_br direction); "
        "inner FACE_BOUND degenerate splitter: two edges at x=2.0 forming a "
        "zero-area sliver loop coincident with the outer right edge; "
        "FixSplitFace fails to detect coincidence between splitter and outer edge; "
        "produces duplicate faces instead of merging; "
        "defect IS on live OPEN_SHELL traversal path; "
        "no orphaned entities"
    ),
)

# ── PLANE surface at origin, normal +Z ────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
plane   = f.plane(f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir))

# ── Outer rectangle: 2.0 × 1.0 ───────────────────────────────────────────────
p_bl = f.cartesian_point((0.0, 0.0, 0.0))
p_br = f.cartesian_point((2.0, 0.0, 0.0))
p_tr = f.cartesian_point((2.0, 1.0, 0.0))
p_tl = f.cartesian_point((0.0, 1.0, 0.0))

v_bl = f.vertex_point(p_bl)
v_br = f.vertex_point(p_br)
v_tr = f.vertex_point(p_tr)
v_tl = f.vertex_point(p_tl)

ec_bot   = f.edge_curve(v_bl, v_br, f.line(p_bl, f.vector(f.direction(( 1.0, 0.0, 0.0)), 2.0)))
ec_right = f.edge_curve(v_br, v_tr, f.line(p_br, f.vector(f.direction(( 0.0, 1.0, 0.0)), 1.0)))
ec_top   = f.edge_curve(v_tr, v_tl, f.line(p_tr, f.vector(f.direction((-1.0, 0.0, 0.0)), 2.0)))
ec_left  = f.edge_curve(v_tl, v_bl, f.line(p_tl, f.vector(f.direction(( 0.0,-1.0, 0.0)), 1.0)))

outer_loop = f.edge_loop([
    f.oriented_edge(ec_bot,   True),
    f.oriented_edge(ec_right, True),
    f.oriented_edge(ec_top,   True),
    f.oriented_edge(ec_left,  True),
])

# ── Splitter loop: zero-area sliver at x=2.0 (coincides with outer right edge)
# Two edges: v_br→v_tr (up the right edge) and v_tr→v_br (back down) — splitter path
sp_up   = f.edge_curve(v_br, v_tr, f.line(p_br, f.vector(f.direction((0.0,  1.0, 0.0)), 1.0)))
sp_down = f.edge_curve(v_tr, v_br, f.line(p_tr, f.vector(f.direction((0.0, -1.0, 0.0)), 1.0)))

splitter_loop = f.edge_loop([
    f.oriented_edge(sp_up,   True),
    f.oriented_edge(sp_down, True),
])

# ── ADVANCED_FACE: outer bound + splitter inner bound ─────────────────────────
face = f.advanced_face([
    f.face_outer_bound(outer_loop),
    f.face_bound(splitter_loop, orientation=True),
], plane)

shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa163.stp")
