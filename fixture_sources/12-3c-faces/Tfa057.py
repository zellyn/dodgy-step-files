"""Tfa057 — Face wire's orientation contradicts the outer/inner role.

Catalog claim: An ADVANCED_FACE has its outer wire wound clockwise (CW) when the
surface normal is taken as outward, and its inner wire wound counter-clockwise
(CCW). The orientations are swapped relative to the STEP convention (outer should
be CCW, inner should be CW). Bug-reporter language: "wire winds wrong way",
"outer loop reversed", "hole oriented as outer".

Mechanism: OPEN_SHELL with ONE face:
  face[0]: ADVANCED_FACE on a 100×100 PLANE at z=0:
    - FACE_OUTER_BOUND: outer 100×100 square but traced CW (bottom→left→top→right)
      — oriented_edge orientations produce CW traversal relative to +Z normal.
    - FACE_BOUND (inner hole): 20×20 square at (40,40)→(60,60) traced CCW.
      Both are reversed from the correct convention.
  Total edge count: 4 (outer) + 4 (inner) = 8. ✓
  OCC heals by flipping loops; computes area = 100×100 - 20×20 = 10000 - 400 = 9600.
  Area ∈ (9500, 9700). ✓

Tier-3 assertions:
  n_faces_total == 1
  face[0].surface_type == "plane"
  face[0].edge_count == 8
  face[0].area > 9500
  face[0].area < 9700

Expected: occt=shape(1)/shape(1) gmsh=shape(17) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa057",
    defect=(
        "OPEN_SHELL: face[0] is 100×100 PLANE; "
        "FACE_OUTER_BOUND outer loop traced CW (oriented_edges in reverse direction); "
        "FACE_BOUND inner 20×20 hole at (40,40) traced CCW; "
        "both loops have reversed orientation relative to STEP convention; "
        "BRepCheck_Face::BadOrientationOfSubshape detects signed-area mismatch; "
        "edge_count = 4+4 = 8; OCC area = 10000-400 = 9600 ∈ (9500,9700); "
        "defect IS on live OPEN_SHELL traversal path"
    ),
)

# ── PLANE at z=0 ──────────────────────────────────────────────────────────────
pl_orig = f.cartesian_point((0.0, 0.0, 0.0))
pl_zdir = f.direction((0.0, 0.0, 1.0))
pl_xdir = f.direction((1.0, 0.0, 0.0))
plane0  = f.plane(f.axis2_placement_3d(pl_orig, pl_zdir, pl_xdir))

# ── OUTER loop: 100×100 square traced CLOCKWISE ───────────────────────────────
# In STEP with +Z normal, CCW is correct for outer. We trace CW by going:
# (0,0) → (0,100) → (100,100) → (100,0) → back to (0,0)
# i.e., left edge up, top edge right, right edge down, bottom edge left
p_bl = f.cartesian_point((  0.0,   0.0, 0.0))
p_br = f.cartesian_point((100.0,   0.0, 0.0))
p_tr = f.cartesian_point((100.0, 100.0, 0.0))
p_tl = f.cartesian_point((  0.0, 100.0, 0.0))

v_bl = f.vertex_point(p_bl)
v_br = f.vertex_point(p_br)
v_tr = f.vertex_point(p_tr)
v_tl = f.vertex_point(p_tl)

# Edge curves defined in their natural forward direction (CCW)
ec_b = f.edge_curve(v_bl, v_br, f.line(p_bl, f.vector(f.direction(( 1.0, 0.0, 0.0)), 100.0)))
ec_r = f.edge_curve(v_br, v_tr, f.line(p_br, f.vector(f.direction(( 0.0, 1.0, 0.0)), 100.0)))
ec_t = f.edge_curve(v_tr, v_tl, f.line(p_tr, f.vector(f.direction((-1.0, 0.0, 0.0)), 100.0)))
ec_l = f.edge_curve(v_tl, v_bl, f.line(p_tl, f.vector(f.direction(( 0.0,-1.0, 0.0)), 100.0)))

# CW traversal: bl→tl→tr→br — use False orientation to reverse each edge
outer_loop = f.edge_loop([
    f.oriented_edge(ec_l, False),   # tl→bl reversed → bl→tl : left edge going up
    f.oriented_edge(ec_t, False),   # tr→tl reversed → tl→tr : top edge going right
    f.oriented_edge(ec_r, False),   # br→tr reversed → tr→br : right edge going down
    f.oriented_edge(ec_b, False),   # bl→br reversed → br→bl : bottom edge going left
])

# ── INNER loop: 20×20 hole at (40,40) traced COUNTER-CLOCKWISE ───────────────
# Correct inner loop would be CW; we wind CCW (same as an outer) — wrong.
pi_bl = f.cartesian_point(( 40.0,  40.0, 0.0))
pi_br = f.cartesian_point(( 60.0,  40.0, 0.0))
pi_tr = f.cartesian_point(( 60.0,  60.0, 0.0))
pi_tl = f.cartesian_point(( 40.0,  60.0, 0.0))

vi_bl = f.vertex_point(pi_bl)
vi_br = f.vertex_point(pi_br)
vi_tr = f.vertex_point(pi_tr)
vi_tl = f.vertex_point(pi_tl)

ei_b = f.edge_curve(vi_bl, vi_br, f.line(pi_bl, f.vector(f.direction(( 1.0, 0.0, 0.0)), 20.0)))
ei_r = f.edge_curve(vi_br, vi_tr, f.line(pi_br, f.vector(f.direction(( 0.0, 1.0, 0.0)), 20.0)))
ei_t = f.edge_curve(vi_tr, vi_tl, f.line(pi_tr, f.vector(f.direction((-1.0, 0.0, 0.0)), 20.0)))
ei_l = f.edge_curve(vi_tl, vi_bl, f.line(pi_tl, f.vector(f.direction(( 0.0,-1.0, 0.0)), 20.0)))

# CCW traversal (wrong for inner): bl→br→tr→tl — all True orientation
inner_loop = f.edge_loop([
    f.oriented_edge(ei_b, True),
    f.oriented_edge(ei_r, True),
    f.oriented_edge(ei_t, True),
    f.oriented_edge(ei_l, True),
])

# face[0]: outer (CW — wrong) + inner (CCW — wrong)
face0 = f.advanced_face([
    f.face_outer_bound(outer_loop),
    f.face_bound(inner_loop, orientation=True),  # True = CCW for inner (wrong)
], plane0)

# ── OPEN_SHELL with single face ───────────────────────────────────────────────
shell = f.open_shell([face0])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa057.stp")
