"""Tsh094 — ShapeFix_Shell.FixFaceOrientation duplicate-face removal.

Catalog claim: Shell contains two ADVANCED_FACEs that are geometrically identical
(same surface + same outer wire). FixFaceOrientation processes both independently;
aMapAdded tracks duplicates but only warns. Duplicate faces are not removed before
orientation propagation, causing inconsistent outward direction markers.

Mechanism IS the shell structure: Two ADVANCED_FACEs share the identical
PLANE surface and the same EDGE_LOOP geometry (same four corner points, same
four EDGE_CURVEs reused by reference). Both faces carry FACE_OUTER_BOUND
orientation=True. The duplicate ADVANCED_FACE referencing the same geometry IS
directly wired into the OPEN_SHELL face list. FixFaceOrientation processes each
face independently via aMapAdded; the second encounter IS flagged as duplicate
but both faces survive into orientation propagation, producing conflicting
direction markers.

Tier-3 assertion: n_faces_total == 2

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh094",
    defect=(
        "OPEN_SHELL with 2 ADVANCED_FACEs that share identical surface geometry — IS the duplicate mechanism; "
        "both faces reference the same PLANE and same EDGE_LOOP corners — IS directly wired in face list; "
        "FACE_OUTER_BOUND orientation=True on both faces — identical orientation flags; "
        "duplicate ADVANCED_FACE in OPEN_SHELL IS the mechanism that triggers aMapAdded duplicate path; "
        "FixFaceOrientation processes both independently; duplicate not removed before propagation; "
        "both faces survive into orientation propagation — conflicting direction markers; "
        "fix: remove duplicate face from shell before orientation propagation step; "
        "emit E_DUPLICATE_FACE_IN_SHELL when aMapAdded detects repeated geometry"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Shared geometry: unit quad at z=0 — same points, same edges reused
p00 = cp(0, 0, 0); p10 = cp(1, 0, 0)
p11 = cp(1, 1, 0); p01 = cp(0, 1, 0)
v00 = f.vertex_point(p00); v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11); v01 = f.vertex_point(p01)
e0 = led(v00, v10, p00,  1, 0, 0)
e1 = led(v10, v11, p10,  0, 1, 0)
e2 = led(v11, v01, p11, -1, 0, 0)
e3 = led(v01, v00, p01,  0, -1, 0)

# Shared EDGE_LOOP: IS the identical outer wire used by both faces
shared_loop = f.edge_loop([
    f.oriented_edge(e0, True), f.oriented_edge(e1, True),
    f.oriented_edge(e2, True), f.oriented_edge(e3, True),
])
# Shared PLANE surface
shared_pl = f.plane(f.axis2_placement_3d(p00, dir3(0, 0, 1), dir3(1, 0, 0)))

# Face A: references shared loop and shared plane — IS the first duplicate
face_a = f.advanced_face(
    [f.face_outer_bound(shared_loop, orientation=True)], shared_pl, same_sense=True
)
# Face B: references same shared loop and same shared plane — IS the duplicate mechanism
face_b = f.advanced_face(
    [f.face_outer_bound(shared_loop, orientation=True)], shared_pl, same_sense=True
)

# OPEN_SHELL with both faces — duplicate in face list IS directly wired into shell topology
shell = f.open_shell([face_a, face_b])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
