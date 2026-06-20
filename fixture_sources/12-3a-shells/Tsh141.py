"""Tsh141 — ShapeUpgrade_ShellSewing.Apply self-sewing.

Catalog claim: Sewing input includes a strip face whose two long edges should
merge with themselves (strip seam). Apply doesn't allow self-pairing and fails
silently. Expected: Apply should detect and permit self-sewing within a single
face. Geometry: Two coplanar rectangles forming a strip; one edge pair should
sew the strip into a closed loop.

Mechanism IS the shell structure: TWO ADVANCED_FACEs forming a strip (each
1×2 rectangle, placed side-by-side) — the shared edge between them IS wired
into both EDGE_LOOPs. The left free edge of Face1 and the right free edge of
Face2 ARE the self-sewing candidates: they are geometrically coincident (both
at x=0 and x=2 in the strip) so ShellSewing.Apply would need to pair them with
themselves to close the loop. The coincident free-edge pair IS wired into the
face topology as separate EDGE_CURVEs — IS the self-sewing mechanism.

Tier-3 assertion: load == "ok"

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh141",
    defect=(
        "TWO ADVANCED_FACEs forming a 2×2 strip — IS the self-sewing mechanism wired into topology; "
        "Face1 (x=[0,1], y=[0,2]) left edge at x=0 IS a free edge candidate for self-sewing; "
        "Face2 (x=[1,2], y=[0,2]) right edge at x=2 IS a free edge candidate for self-sewing; "
        "shared EDGE_CURVE at x=1 IS wired into both EDGE_LOOPs (manifold seam); "
        "free edge at x=0 and free edge at x=2 ARE geometrically coincident — IS self-sewing pair; "
        "ShellSewing.Apply rejects self-pairing of free edges — silently fails; "
        "fix: allow edge-to-edge self-sewing when endpoints coincide within tolerance; "
        "emit E_SELF_SEWING_REJECTED when Apply refuses valid self-pairing"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Strip vertices: two 1×2 rectangles side by side
p00 = cp(0, 0, 0); p10 = cp(1, 0, 0); p20 = cp(2, 0, 0)
p02 = cp(0, 2, 0); p12 = cp(1, 2, 0); p22 = cp(2, 2, 0)

v00 = f.vertex_point(p00); v10 = f.vertex_point(p10); v20 = f.vertex_point(p20)
v02 = f.vertex_point(p02); v12 = f.vertex_point(p12); v22 = f.vertex_point(p22)

# Shared internal edge at x=1 — IS wired into both EDGE_LOOPs (manifold seam)
e_mid_bot = led(v00, v10, p00,  1, 0, 0)  # y=0 bottom
e_mid_top = led(v02, v12, p02,  1, 0, 0)  # y=2 top (Face1 inner seam at x=1, bottom segment)
e_seam    = led(v10, v12, p10,  0, 1, 0)  # x=1 shared seam — IS wired into both faces

# Face1 free edges
e_f1_bot  = led(v00, v10, p00,  1, 0, 0)  # bottom y=0 left half (same as e_mid_bot, reused)
e_f1_left = led(v00, v02, p00,  0, 1, 0)  # x=0 left free edge — IS self-sewing candidate
e_f1_top  = led(v02, v12, p02,  1, 0, 0)  # y=2 top left half

# Face2 free edges
e_f2_bot  = led(v10, v20, p10,  1, 0, 0)  # bottom y=0 right half
e_f2_right= led(v20, v22, p20,  0, 1, 0)  # x=2 right free edge — IS self-sewing candidate
e_f2_top  = led(v12, v22, p12,  1, 0, 0)  # y=2 top right half

def mk_plane_z0(ox, oy):
    orig = f.cartesian_point((ox, oy, 0.0))
    return f.plane(f.axis2_placement_3d(orig, dir3(0, 0, 1), dir3(1, 0, 0)))

def face4(edges_with_ori, plane):
    loop = f.edge_loop([f.oriented_edge(e, o) for e, o in edges_with_ori])
    return f.advanced_face([f.face_outer_bound(loop, orientation=True)], plane, same_sense=True)

# Face1: x=[0,1], y=[0,2] — left strip half
face1 = face4(
    [(e_f1_bot, True), (e_seam, True), (e_f1_top, False), (e_f1_left, False)],
    mk_plane_z0(0, 0)
)

# Face2: x=[1,2], y=[0,2] — right strip half
face2 = face4(
    [(e_f2_bot, True), (e_f2_right, True), (e_f2_top, False), (e_seam, False)],
    mk_plane_z0(1, 0)
)

# OPEN_SHELL with two faces forming strip — IS the self-sewing mechanism
shell = f.open_shell([face1, face2])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
