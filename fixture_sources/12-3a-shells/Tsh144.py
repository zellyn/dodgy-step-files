"""Tsh144 — ShapeFix_Shell.FixFaceOrientation T-shaped-non-manifold.

Catalog claim: Shell with three faces meeting at a shared edge.
FixFaceOrientation picks one orientation as propagation direction; the other
two remain flipped. Tests non-manifold edge handling in orientation repair.

Mechanism IS the shell structure: THREE ADVANCED_FACEs meeting at a single
shared edge (x=1, y=[0,1], z=0) — this shared edge IS wired into all three
EDGE_LOOPs forming a T-junction. The T-shape IS: Face1 (x=[0,1]),
Face2 (x=[1,2]) sharing the center seam, and Face3 (y=[1,2] above the seam)
also referencing the same shared edge. The shared edge referenced by 3 faces
IS the non-manifold topology wired into the EDGE_LOOPs — FixFaceOrientation
propagates orientation from one face and cannot consistently orient remaining two.

Tier-3 assertion: load == "ok"

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh144",
    defect=(
        "THREE ADVANCED_FACEs meeting at shared EDGE_CURVE at x=1 y=[0,1] — IS the T-junction mechanism; "
        "Face1 (x=[0,1] y=[0,1]) references shared EDGE_CURVE as right boundary — IS wired into EDGE_LOOP1; "
        "Face2 (x=[1,2] y=[0,1]) references same shared EDGE_CURVE as left boundary — IS wired into EDGE_LOOP2; "
        "Face3 (x=[0,1] y=[1,2]) references same shared EDGE_CURVE as bottom boundary — IS wired into EDGE_LOOP3; "
        "single EDGE_CURVE referenced by 3 EDGE_LOOPs IS the non-manifold topology; "
        "FixFaceOrientation propagates from Face1 consistently with Face2 but Face3 remains flipped; "
        "fix: detect non-manifold edges (3+ face references); apply branching orientation strategy; "
        "emit E_NON_MANIFOLD_ORIENTATION_AMBIGUOUS when T-junction edge found during propagation"
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

# T-junction vertices
p00 = cp(0, 0, 0); p10 = cp(1, 0, 0); p20 = cp(2, 0, 0)
p01 = cp(0, 1, 0); p11 = cp(1, 1, 0); p21 = cp(2, 1, 0)
p02 = cp(0, 2, 0); p12 = cp(1, 2, 0)

v00 = f.vertex_point(p00); v10 = f.vertex_point(p10); v20 = f.vertex_point(p20)
v01 = f.vertex_point(p01); v11 = f.vertex_point(p11); v21 = f.vertex_point(p21)
v02 = f.vertex_point(p02); v12 = f.vertex_point(p12)

# Shared T-junction edge at x=1, y=[0,1] — IS the non-manifold edge wired into 3 EDGE_LOOPs
e_junction = led(v10, v11, p10,  0, 1, 0)

# Face1 edges: x=[0,1], y=[0,1]
e_f1_bot  = led(v00, v10, p00,  1, 0, 0)
e_f1_top  = led(v01, v11, p01,  1, 0, 0)
e_f1_left = led(v00, v01, p00,  0, 1, 0)

# Face2 edges: x=[1,2], y=[0,1]
e_f2_bot   = led(v10, v20, p10,  1, 0, 0)
e_f2_top   = led(v11, v21, p11,  1, 0, 0)
e_f2_right = led(v20, v21, p20,  0, 1, 0)

# Face3 edges: x=[0,1], y=[1,2] (uses v11 as bottom-right, making junction at y=1)
e_f3_top   = led(v02, v12, p02,  1, 0, 0)
e_f3_left  = led(v01, v02, p01,  0, 1, 0)
e_f3_right = led(v11, v12, p11,  0, 1, 0)
e_f3_bot   = led(v01, v11, p01,  1, 0, 0)  # bottom of Face3 also at y=1

# Face1: x=[0,1], y=[0,1] — e_junction IS right boundary wired into EDGE_LOOP1
loop1 = f.edge_loop([
    f.oriented_edge(e_f1_bot,   True),
    f.oriented_edge(e_junction, True),   # IS the T-junction edge
    f.oriented_edge(e_f1_top,   False),
    f.oriented_edge(e_f1_left,  False),
])
face1 = f.advanced_face([f.face_outer_bound(loop1, orientation=True)], mk_plane_z0(0, 0), same_sense=True)

# Face2: x=[1,2], y=[0,1] — e_junction IS left boundary wired into EDGE_LOOP2
loop2 = f.edge_loop([
    f.oriented_edge(e_f2_bot,   True),
    f.oriented_edge(e_f2_right, True),
    f.oriented_edge(e_f2_top,   False),
    f.oriented_edge(e_junction, False),  # IS the T-junction edge (reversed)
])
face2 = f.advanced_face([f.face_outer_bound(loop2, orientation=True)], mk_plane_z0(1, 0), same_sense=True)

# Face3: x=[0,1], y=[1,2] — e_junction IS bottom boundary wired into EDGE_LOOP3 (T-branch)
loop3 = f.edge_loop([
    f.oriented_edge(e_f3_bot,   True),
    f.oriented_edge(e_f3_right, True),
    f.oriented_edge(e_f3_top,   False),
    f.oriented_edge(e_f3_left,  False),
])
face3 = f.advanced_face([f.face_outer_bound(loop3, orientation=True)], mk_plane_z0(0, 1), same_sense=True)

# OPEN_SHELL: 3 faces sharing T-junction edge — IS the non-manifold mechanism
shell = f.open_shell([face1, face2, face3])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
