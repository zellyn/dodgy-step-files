"""Tsh141 — ShapeUpgrade_ShellSewing.Apply self-sewing.

Catalog claim: Sewing input includes a strip face whose two long edges should
merge with themselves (strip seam). Apply doesn't allow self-pairing and fails
silently. Expected: Apply should detect and permit self-sewing within a single
face. Geometry: Two coplanar rectangles forming a strip; one edge pair should
sew the strip into a closed loop.

OCCT exchange-layer coverage audit finding (occt-coverage/exchange/): the
PREVIOUS version of this fixture placed Face1 and Face2 side-by-side
(x=[0,1] and x=[1,2]) and claimed their outer free edges (at x=0 and x=2)
were "geometrically coincident" -- but x=0 and x=2 are 2.0mm apart, not
coincident. Byte-verified as NOT demonstrating the self-sewing claim.

Fixed here: Face2 is folded back 180 degrees flat over Face1's own
footprint (a genuine "strip folded double" -- both faces stay coplanar,
in the SAME z=0 plane, sharing the SAME PLANE entity) instead of
extending the strip further out. Face2's seam edge (shared with Face1 at
x=1) is unchanged; its far corners are NEW, topologically-distinct
vertices placed at the EXACT same 3D coordinates as Face1's free left
edge (x=0, y=0 and x=0, y=2) -- genuinely coincident (distance 0), not
merged. This is the literal self-sewing input: two independent EDGE_CURVEs
occupying the same 3D segment, on the same shell, that ShellSewing.Apply
should recognize and pair with each other but doesn't.

Tier-3 assertion: load == "ok"

live oracle: occt=shape(1)/shape(1)  [NEEDS-ORACLE-REFRESH: face footprints
now fully overlap via the fold-back, unlike the prior side-by-side layout]
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh141",
    defect=(
        "TWO ADVANCED_FACEs forming a strip folded back on itself — IS the self-sewing "
        "mechanism wired into topology; Face1 (x=[0,1], y=[0,2]) left edge at x=0 IS a "
        "free edge candidate for self-sewing; Face2 folds back over the SAME footprint "
        "(same PLANE, same_sense=.F.) so its far edge lands EXACTLY at x=0, y=[0,2] too "
        "— a genuinely coincident (distance 0) but topologically DISTINCT free edge; "
        "shared EDGE_CURVE at x=1 IS wired into both EDGE_LOOPs (manifold seam); "
        "the two coincident free edges (Face1's e_f1_left, Face2's e_f2_left_fold) ARE "
        "the self-sewing pair; ShellSewing.Apply rejects self-pairing of free edges — "
        "silently fails; fix: allow edge-to-edge self-sewing when endpoints coincide "
        "within tolerance; emit E_SELF_SEWING_REJECTED when Apply refuses valid "
        "self-pairing"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Face1 vertices: unit-strip square x=[0,1], y=[0,2].
p00 = cp(0, 0, 0); p10 = cp(1, 0, 0)
p02 = cp(0, 2, 0); p12 = cp(1, 2, 0)

v00 = f.vertex_point(p00); v10 = f.vertex_point(p10)
v02 = f.vertex_point(p02); v12 = f.vertex_point(p12)

# Face2 far-corner vertices: NEW, distinct entities placed at the EXACT
# same coordinates as Face1's free edge (x=0) — the coincident-but-unmerged
# self-sewing candidate, not a shared/reused vertex.
p00_fold = cp(0, 0, 0); p02_fold = cp(0, 2, 0)
v00_fold = f.vertex_point(p00_fold); v02_fold = f.vertex_point(p02_fold)

# Shared internal seam edge at x=1 — IS wired into both EDGE_LOOPs (manifold seam)
e_seam = led(v10, v12, p10, 0, 1, 0)  # x=1 shared seam — IS wired into both faces

# Face1 boundary edges
e_f1_bot  = led(v00, v10, p00, 1, 0, 0)   # bottom y=0
e_f1_left = led(v00, v02, p00, 0, 1, 0)   # x=0 left free edge — IS self-sewing candidate #1
e_f1_top  = led(v02, v12, p02, 1, 0, 0)   # top y=2

# Face2 boundary edges (folded back over Face1's own footprint)
e_f2_bot       = led(v10, v00_fold, p10, -1, 0, 0)       # bottom y=0, seam -> folded corner
e_f2_left_fold = led(v00_fold, v02_fold, p00_fold, 0, 1, 0)  # x=0 folded free edge — self-sewing candidate #2
e_f2_top       = led(v02_fold, v12, p02_fold, 1, 0, 0)       # top y=2, folded corner -> seam

def mk_plane_z0(ox, oy):
    orig = f.cartesian_point((ox, oy, 0.0))
    return f.plane(f.axis2_placement_3d(orig, dir3(0, 0, 1), dir3(1, 0, 0)))

def face4(edges_with_ori, plane, same_sense=True):
    loop = f.edge_loop([f.oriented_edge(e, o) for e, o in edges_with_ori])
    return f.advanced_face([f.face_outer_bound(loop, orientation=True)], plane, same_sense=same_sense)

# Both faces share the SAME plane instance — genuinely coplanar, z=0.
plane_z0 = mk_plane_z0(0, 0)

# Face1: x=[0,1], y=[0,2] — normal sense (+Z normal facing up).
face1 = face4(
    [(e_f1_bot, True), (e_seam, True), (e_f1_top, False), (e_f1_left, False)],
    plane_z0, same_sense=True,
)

# Face2: folded back onto the SAME x=[0,1], y=[0,2] footprint — opposite
# sense (it is the "under" layer of the fold, facing -Z).
face2 = face4(
    [(e_f2_bot, True), (e_f2_left_fold, True), (e_f2_top, True), (e_seam, False)],
    plane_z0, same_sense=False,
)

# OPEN_SHELL with two faces forming a strip folded back on itself — IS the
# self-sewing mechanism (coincident-but-unmerged free-edge pair).
shell = f.open_shell([face1, face2])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
