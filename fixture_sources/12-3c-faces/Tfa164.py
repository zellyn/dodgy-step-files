"""Tfa164 — ShapeAnalysis_CheckSmallFace.CheckPin two-pins-on-one-face.

Catalog claim: Face with two thin pin extensions (small protruding edges) at
different locations. CheckPin iterates pole-grid once, reports first pin,
then halts—missing second pin. Fixture: 1.0 x 1.0 rectangular loop with two
degenerate pin-like edges appended (0.5 x 0.001 and parallel), triggering
missed-detection at iteration boundary.

Mechanism: OPEN_SHELL with ONE ADVANCED_FACE: a 1.0×1.0 square on a PLANE
plus two thin FACE_BOUND wires representing pin extensions.
Pin A: a 0.5×0.001 rectangle anchored at (0.2, 0.0) pointing into the face.
Pin B: a 0.5×0.001 rectangle anchored at (0.6, 0.0) pointing into the face.
CheckPin's pole-grid iteration stops after finding pin A, missing pin B.
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
    catalog_id="Tfa164",
    defect=(
        "OPEN_SHELL: single ADVANCED_FACE on PLANE (1.0×1.0 square); "
        "TWO thin pin-extension FACE_BOUND wires: "
        "pin_A: 0.5×0.001 rectangle at (0.2,0.0)→(0.7,0.001); "
        "pin_B: 0.5×0.001 rectangle at (0.6,0.0)→(1.1,0.001); "
        "CheckPin pole-grid iteration reports first pin (A) then halts; "
        "second pin (B) is missed — iteration-boundary failure; "
        "defect IS on live OPEN_SHELL traversal path; "
        "no orphaned entities"
    ),
)

# ── PLANE surface at origin, normal +Z ────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
plane   = f.plane(f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir))


def make_rect_loop(x0, y0, x1, y1):
    """Return an EDGE_LOOP for a rectangle in the XY plane at z=0."""
    p_bl = f.cartesian_point((x0, y0, 0.0))
    p_br = f.cartesian_point((x1, y0, 0.0))
    p_tr = f.cartesian_point((x1, y1, 0.0))
    p_tl = f.cartesian_point((x0, y1, 0.0))

    v_bl = f.vertex_point(p_bl)
    v_br = f.vertex_point(p_br)
    v_tr = f.vertex_point(p_tr)
    v_tl = f.vertex_point(p_tl)

    dx = x1 - x0
    dy = y1 - y0

    ec_b = f.edge_curve(v_bl, v_br, f.line(p_bl, f.vector(f.direction(( 1.0, 0.0, 0.0)), dx)))
    ec_r = f.edge_curve(v_br, v_tr, f.line(p_br, f.vector(f.direction(( 0.0, 1.0, 0.0)), dy)))
    ec_t = f.edge_curve(v_tr, v_tl, f.line(p_tr, f.vector(f.direction((-1.0, 0.0, 0.0)), dx)))
    ec_l = f.edge_curve(v_tl, v_bl, f.line(p_tl, f.vector(f.direction(( 0.0,-1.0, 0.0)), dy)))

    return f.edge_loop([
        f.oriented_edge(ec_b, True),
        f.oriented_edge(ec_r, True),
        f.oriented_edge(ec_t, True),
        f.oriented_edge(ec_l, True),
    ])


# ── Outer 1.0×1.0 square ──────────────────────────────────────────────────────
outer_loop = make_rect_loop(0.0, 0.0, 1.0, 1.0)

# ── Pin A: 0.5×0.001 rectangle at (0.2, 0.0) — first pin CheckPin finds ───────
pin_a_loop = make_rect_loop(0.2, 0.0, 0.7, 0.001)

# ── Pin B: 0.5×0.001 rectangle at (0.6, 0.0) — second pin CheckPin misses ─────
pin_b_loop = make_rect_loop(0.6, 0.0, 1.1, 0.001)

# ── ADVANCED_FACE: outer bound + two pin inner bounds ─────────────────────────
face = f.advanced_face([
    f.face_outer_bound(outer_loop),
    f.face_bound(pin_a_loop, orientation=True),
    f.face_bound(pin_b_loop, orientation=True),
], plane)

shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa164.stp")
