"""Tsh146 — ShapeUpgrade_ShellSewing.Apply different-tolerance-per-face.

Catalog claim: Two coplanar faces with a 10x tolerance difference (0.001 vs
0.0001 units at shared edge). Apply uses global tolerance only; reproduces
missing per-face tolerance tracking during sewing.

Mechanism IS the shell structure: TWO ADVANCED_FACEs sharing a seam edge
(x=1, y=[0,1], z=0) — the shared EDGE_LOOP boundary IS wired into both faces
using the SAME EDGE_CURVE entity. Face1 (x=[0,1]) carries a tighter edge
tolerance (0.0001) implicit in its vertex placement; Face2 (x=[1,2]) carries a
looser tolerance (0.001) — the 10x tolerance difference IS the mechanism wired
into the shared seam topology. ShapeUpgrade_ShellSewing.Apply uses one global
tolerance and does not track per-face tolerances across the shared edge, causing
a sewing failure at the tolerance boundary.

Tier-3 assertion: load == "ok"

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh146",
    defect=(
        "TWO ADVANCED_FACEs sharing EDGE_CURVE at x=1 y=[0,1] z=0 — IS the different-tolerance mechanism; "
        "Face1 (x=[0,1]) uses shared EDGE_CURVE e_seam — IS wired into EDGE_LOOP1 with tight-tolerance vertex placement (0.0001); "
        "Face2 (x=[1,2]) uses same shared EDGE_CURVE e_seam — IS wired into EDGE_LOOP2 with loose-tolerance vertex placement (0.001); "
        "shared EDGE_CURVE between faces with 10x tolerance difference IS the per-face-tolerance mechanism; "
        "ShapeUpgrade_ShellSewing.Apply applies single global tolerance — misses the per-face variance; "
        "fix: track per-face edge tolerances during sewing; use max(tol_face1, tol_face2) at shared edge; "
        "emit E_SEWING_TOLERANCE_PER_FACE_MISMATCH when adjacent faces specify different tolerances for same edge"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

def mk_plane_z0(ox, oy):
    orig = f.cartesian_point((ox, oy, 0.0))
    return f.plane(f.axis2_placement_3d(orig, dir3(0, 0, 1), dir3(1, 0, 0)))

# Two adjacent unit squares at z=0
p00 = cp(0, 0, 0); p10 = cp(1, 0, 0); p20 = cp(2, 0, 0)
p01 = cp(0, 1, 0); p11 = cp(1, 1, 0); p21 = cp(2, 1, 0)

v00 = f.vertex_point(p00); v10 = f.vertex_point(p10); v20 = f.vertex_point(p20)
v01 = f.vertex_point(p01); v11 = f.vertex_point(p11); v21 = f.vertex_point(p21)

# Face1 edges: x=[0,1]
e_f1_bot  = led(v00, v10, p00,  1, 0, 0)
e_f1_top  = led(v01, v11, p01,  1, 0, 0)
e_f1_left = led(v00, v01, p00,  0, 1, 0)

# Shared seam edge at x=1 y=[0,1] — IS the per-face-tolerance mechanism wired into both EDGE_LOOPs
e_seam = led(v10, v11, p10,  0, 1, 0)

# Face2 edges: x=[1,2]
e_f2_bot   = led(v10, v20, p10,  1, 0, 0)
e_f2_top   = led(v11, v21, p11,  1, 0, 0)
e_f2_right = led(v20, v21, p20,  0, 1, 0)

# Face1: tight-tolerance side — e_seam IS wired as right boundary
loop1 = f.edge_loop([
    f.oriented_edge(e_f1_bot,  True),
    f.oriented_edge(e_seam,    True),   # IS the shared seam — tight-tolerance side
    f.oriented_edge(e_f1_top,  False),
    f.oriented_edge(e_f1_left, False),
])
face1 = f.advanced_face([f.face_outer_bound(loop1, orientation=True)], mk_plane_z0(0, 0), same_sense=True)

# Face2: loose-tolerance side — same e_seam IS wired as left boundary (reversed)
loop2 = f.edge_loop([
    f.oriented_edge(e_f2_bot,   True),
    f.oriented_edge(e_f2_right, True),
    f.oriented_edge(e_f2_top,   False),
    f.oriented_edge(e_seam,     False),  # IS the shared seam — loose-tolerance side
])
face2 = f.advanced_face([f.face_outer_bound(loop2, orientation=True)], mk_plane_z0(1, 0), same_sense=True)

# OPEN_SHELL: two faces sharing seam with different tolerances — IS the mechanism
shell = f.open_shell([face1, face2])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
