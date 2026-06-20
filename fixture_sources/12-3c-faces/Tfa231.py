"""Tfa231 — FixSmallAreaWire shape-type filter

Small-area wire detection via sub-shape-type and orientation validation.
Planar face with outer loop (3×3 unit boundary) and inner loop (0.05×0.05
unit hole) to exercise the shape-type-filter defect. Tests early rejection
of non-WIRE or invalid-orientation sub-shapes.

Mechanism: CLOSED_SHELL with ONE ADVANCED_FACE on a PLANE. The face has an
outer FACE_OUTER_BOUND (3×3 unit square) and an inner FACE_BOUND (0.05×0.05
unit square hole, CCW orientation → reversed sense on the face). The
ShapeFix_Face::FixSmallAreaWire() traverses all face sub-shapes filtering by
type WIRE; sub-shapes that are not WIRE or have invalid orientation are
rejected early. The 0.05×0.05 hole (area=0.0025) falls below the small-area
threshold, exercising the type-filter and area-detection dispatch.

Byte assertions:
  - contains(b'PLANE')
  - contains(b'ADVANCED_FACE')
  - contains(b'FACE_BOUND')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa231",
    defect=(
        "CLOSED_SHELL: single ADVANCED_FACE on PLANE; "
        "outer FACE_OUTER_BOUND: 3×3 unit square (0,0)-(3,3); "
        "inner FACE_BOUND: 0.05×0.05 unit square hole at (1,1)-(1.05,1.05); "
        "inner bound orientation=False (reversed sense on face); "
        "ShapeFix_Face::FixSmallAreaWire() shape-type filter: "
        "traverses sub-shapes; rejects non-WIRE or invalid-orientation early; "
        "0.05×0.05 hole area=0.0025 below small-area threshold; "
        "exercises type-filter and area-detection dispatch; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

# ── PLANE ─────────────────────────────────────────────────────────────────────
pl_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
plane = f.plane(pl_plc)


def make_rect_loop(x0, y0, x1, y1):
    """Build a 4-edge rectangular EDGE_LOOP (CCW) on the XY plane."""
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


# ── Outer loop: 3×3 square ────────────────────────────────────────────────────
outer_loop = make_rect_loop(0.0, 0.0, 3.0, 3.0)
outer_bound = f.face_outer_bound(outer_loop, True)

# ── Inner loop: 0.05×0.05 hole (small-area wire) ─────────────────────────────
# CCW wound; orientation=False means the hole sense is reversed on the face
inner_loop = make_rect_loop(1.0, 1.0, 1.05, 1.05)
inner_bound = f.face_bound(inner_loop, False)

face = f.advanced_face([outer_bound, inner_bound], plane)

closed_sh = f.closed_shell([face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa231.stp")
