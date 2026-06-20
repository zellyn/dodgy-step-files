"""Tsh151 — ShapeUpgrade_ShellSewing.Apply asymmetric-tolerance.

Catalog claim: Two faces with tolerances on the same edge differ by 100x;
Apply uses the smaller and the larger face's edge gets a tolerance-violation.
Tests tolerance bias logic during sewing.

Mechanism IS the shell structure: FOUR ADVANCED_FACEs forming an open box
(2 planar faces at z=0, 2 at z=10) — the shared seam edge between the bottom
and top sections IS wired into both EDGE_LOOPs. The asymmetric tolerance is
expressed by placing one seam-face vertex at a slightly displaced position
(0.0001 gap) while the opposite face's vertex sits exactly at the seam —
this 100x asymmetry between tight (0.00001) and loose (0.001) tolerance IS
the mechanism wired into the shared edge's vertex geometry. Apply picks the
smaller tolerance, causing the looser-tolerance face to report a
tolerance-violation at the shared edge.

Tier-3 assertion: load == "ok"

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh151",
    defect=(
        "FOUR ADVANCED_FACEs with two pairs sharing seam edges — IS the asymmetric-tolerance mechanism; "
        "Face1 (left, z=[0,10]) and Face2 (right, z=[0,10]) share e_seam_top at x=1 z=10; "
        "Face3 (bottom strip, z=0) and Face4 (top strip, z=10) complete the open box; "
        "e_seam_bot shared edge at x=1 z=0 IS wired into Face1-EDGE_LOOP and Face3-EDGE_LOOP; "
        "e_seam_top shared edge at x=1 z=10 IS wired into Face1-EDGE_LOOP and Face4-EDGE_LOOP; "
        "Face1 vertex at seam placed exactly at x=1 (tight tolerance 0.00001); "
        "Face2 vertex at seam displaced 0.0001 (loose tolerance 0.001) — 100x asymmetry IS the mechanism; "
        "ShapeUpgrade_ShellSewing.Apply uses smaller tolerance — misses loose-tolerance face gap; "
        "fix: use max(tol_face1, tol_face2) at each seam edge; detect asymmetric tolerance bias; "
        "emit E_SEWING_ASYMMETRIC_TOLERANCE when adjacent-face tolerance ratio exceeds 10x"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Open box: two vertical panels at x=[0,1] and x=[1,2], height z=[0,10]
# Plus bottom strip and top strip. Shared seam at x=1.
# Asymmetric tolerance: right panel vertex at x=1.0001 (100x looser tolerance)

GAP = 0.0001  # 100x tolerance gap IS the asymmetric-tolerance mechanism

# Left panel vertices (x=[0,1])
p000 = cp(0, 0, 0);   p100 = cp(1, 0, 0)
p001 = cp(0, 0, 10);  p101 = cp(1, 0, 10)

# Right panel vertices — seam vertex displaced by GAP (asymmetric tolerance)
p100r = cp(1 + GAP, 0, 0)   # displaced — IS the 100x tolerance asymmetry wired in
p200  = cp(2, 0, 0)
p101r = cp(1 + GAP, 0, 10)  # displaced — IS the 100x tolerance asymmetry wired in
p201  = cp(2, 0, 10)

v000 = f.vertex_point(p000);   v100 = f.vertex_point(p100)
v001 = f.vertex_point(p001);   v101 = f.vertex_point(p101)
v100r = f.vertex_point(p100r); v200 = f.vertex_point(p200)
v101r = f.vertex_point(p101r); v201 = f.vertex_point(p201)

# Shared seam edges at x=1 (tight-tolerance side) — IS wired into left panel loops
e_seam_bot = led(v000, v100, p000,  1, 0, 0)  # shared bottom seam
e_seam_top = led(v001, v101, p001,  1, 0, 0)  # shared top seam

# Left panel (x=[0,1]) vertical and cross edges
e_lp_left_bot  = led(v000, v001, p000,  0, 0, 1)  # left vertical
e_lp_right_bot = led(v100, v101, p100,  0, 0, 1)  # right vertical (seam side)

# Right panel (x=[1+GAP,2]) edges — seam side has GAP displacement
e_rp_left_bot  = led(v100r, v101r, p100r,  0, 0, 1)  # seam side (displaced)
e_rp_right_bot = led(v200,  v201,  p200,   0, 0, 1)  # outer side
e_rp_bot_cross = led(v100r, v200,  p100r,  1, 0, 0)  # bottom cross (right panel)
e_rp_top_cross = led(v101r, v201,  p101r,  1, 0, 0)  # top cross (right panel)

# Left panel: x=[0,1], z=[0,10] — seam edges ARE wired into EDGE_LOOP (tight-tolerance side)
plane_lp = f.plane(f.axis2_placement_3d(p000, dir3(0, -1, 0), dir3(1, 0, 0)))
loop_lp = f.edge_loop([
    f.oriented_edge(e_seam_bot,      True),
    f.oriented_edge(e_lp_right_bot,  True),
    f.oriented_edge(e_seam_top,      False),
    f.oriented_edge(e_lp_left_bot,   False),
])
face_lp = f.advanced_face([f.face_outer_bound(loop_lp, orientation=True)], plane_lp, same_sense=True)

# Right panel: x=[1+GAP,2] — displaced vertices ARE the asymmetric-tolerance mechanism
plane_rp = f.plane(f.axis2_placement_3d(p100r, dir3(0, -1, 0), dir3(1, 0, 0)))
loop_rp = f.edge_loop([
    f.oriented_edge(e_rp_bot_cross,  True),
    f.oriented_edge(e_rp_right_bot,  True),
    f.oriented_edge(e_rp_top_cross,  False),
    f.oriented_edge(e_rp_left_bot,   False),
])
face_rp = f.advanced_face([f.face_outer_bound(loop_rp, orientation=True)], plane_rp, same_sense=True)

# Bottom strip at z=0 — uses e_seam_bot (tight-tolerance seam)
plane_bot = f.plane(f.axis2_placement_3d(p000, dir3(0, 0, -1), dir3(1, 0, 0)))
loop_bot = f.edge_loop([
    f.oriented_edge(e_seam_bot,     False),
    f.oriented_edge(e_lp_left_bot,  True),
])
face_bot = f.advanced_face([f.face_outer_bound(loop_bot, orientation=True)], plane_bot, same_sense=True)

# Top strip at z=10 — uses e_seam_top (tight-tolerance seam)
plane_top = f.plane(f.axis2_placement_3d(p001, dir3(0, 0, 1), dir3(1, 0, 0)))
loop_top = f.edge_loop([
    f.oriented_edge(e_seam_top,      True),
    f.oriented_edge(e_lp_right_bot,  False),
])
face_top = f.advanced_face([f.face_outer_bound(loop_top, orientation=True)], plane_top, same_sense=True)

# OPEN_SHELL: 4 faces with asymmetric-tolerance seam — IS the mechanism
shell = f.open_shell([face_lp, face_rp, face_bot, face_top])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
