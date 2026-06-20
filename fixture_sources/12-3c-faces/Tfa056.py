"""Tfa056 — Face has a redundant wire (wire fully inside another wire of same face).

Catalog claim: A face has two inner wires (holes) where one is geometrically
nested inside the other. The inner-most wire is a "hole inside a hole", which
is contradictory — that region was already excluded. Bug-reporter language:
"redundant wire", "hole inside hole", "useless inner loop nested in another".

Mechanism: OPEN_SHELL with ONE face:
  face[0]: ADVANCED_FACE on a 100×100 PLANE with:
    - FACE_OUTER_BOUND: 100×100 outer square  [4 edges]
    - FACE_BOUND (inner1): 31×31 hole square at (35,35)→(66,66)  [4 edges]
    - FACE_BOUND (inner2): 10×10 square at (40,40)→(50,50)       [4 edges]
      (inner2 is entirely contained within inner1 — the redundant wire)
  Total edge count: 4+4+4 = 12.
  OCC heals by dropping inner2 (redundant). Resulting area = 100×100 - 31×31
  = 10000 - 961 = 9039. In [8900, 9100]. ✓

Tier-3 assertions:
  n_faces_total == 1
  face[0].surface_type == "plane"
  face[0].edge_count == 12
  face[0].area > 8900
  face[0].area < 9100

Expected: occt=shape(1)/shape(1) gmsh=shape(25) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa056",
    defect=(
        "OPEN_SHELL: face[0] is 100×100 PLANE with outer FACE_OUTER_BOUND "
        "plus two inner FACE_BOUND wires: inner1 = 31×31 hole at (35,35); "
        "inner2 = 10×10 hole at (40,40) — entirely inside inner1; "
        "inner2 is redundant (hole inside a hole); "
        "BRepCheck_Face::RedundantWire must detect nesting via UV polygon-in-polygon; "
        "edge_count = 4+4+4 = 12; OCC area = 10000-961 = 9039 in [8900,9100]; "
        "defect IS on live OPEN_SHELL traversal path"
    ),
)


def make_rect_loop(x0, y0, x1, y1, z=0.0):
    """Return an EDGE_LOOP for a rectangle in the XY plane at z."""
    p_bl = f.cartesian_point((x0, y0, z))
    p_br = f.cartesian_point((x1, y0, z))
    p_tr = f.cartesian_point((x1, y1, z))
    p_tl = f.cartesian_point((x0, y1, z))

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


# ── PLANE at z=0 ──────────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
plane0  = f.plane(f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir))

# ── Outer bound: 100×100 square ───────────────────────────────────────────────
outer_loop = make_rect_loop(0.0, 0.0, 100.0, 100.0)

# ── Inner bound 1: 31×31 hole at (35,35)→(66,66) ─────────────────────────────
# Area of hole = 31×31 = 961
inner1_loop = make_rect_loop(35.0, 35.0, 66.0, 66.0)

# ── Inner bound 2 (REDUNDANT): 10×10 hole at (40,40)→(50,50) ─────────────────
# Fully contained within inner1 — this is the redundant wire (hole inside hole)
inner2_loop = make_rect_loop(40.0, 40.0, 50.0, 50.0)

# face[0]: all three wires — outer bound + two inner bounds (one redundant)
face0 = f.advanced_face([
    f.face_outer_bound(outer_loop),
    f.face_bound(inner1_loop, orientation=False),
    f.face_bound(inner2_loop, orientation=False),
], plane0)

# ── OPEN_SHELL with single face ───────────────────────────────────────────────
shell = f.open_shell([face0])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa056.stp")
