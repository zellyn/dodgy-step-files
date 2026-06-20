"""Tsh184 — ShapeFix_Shell.FixFaceOrientation duplicate-face inconsistency.

Catalog claim: Shell containing two identical faces; orientation-fix processes
both independently without detecting duplication. Results in inconsistent
orientation outcomes where one face is corrected while its duplicate remains in
original orientation. This breaks closure assumptions downstream.

Mechanism IS the shell structure: A CLOSED_SHELL with THREE ADVANCED_FACEs IS
the defect trigger. TWO of those faces (face_dup_a and face_dup_b) ARE
IDENTICAL GEOMETRY sharing the SAME underlying surface but wired as SEPARATE
STEP entities. FixFaceOrientation IS the defect path: it processes each face
independently, corrects one and leaves the duplicate in its original
orientation, producing a mixed-orientation shell. The inconsistency IS the
defect: aMapAdded never tracks duplicates, so both entries remain but only one
is corrected.

Tier-3 assertion: n_faces_total == 3

live oracle: occt=shape(1)/shape(1) gmsh=reject ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh184",
    defect=(
        "CLOSED_SHELL with THREE ADVANCED_FACEs IS the FixFaceOrientation defect trigger; "
        "face_dup_a and face_dup_b ARE IDENTICAL GEOMETRY — same vertices, same plane — IS the duplicate pair; "
        "face_base IS the unique reference face (Z=0 square, same_sense=True) — IS the orientation anchor; "
        "face_dup_a IS the top cap (Z=1 square, same_sense=True) — IS the first duplicate; "
        "face_dup_b IS SAME GEOMETRY as face_dup_a (Z=1 square, same_sense=False) — IS the duplicate; "
        "FixFaceOrientation processes face_dup_a and face_dup_b independently — IS the defect path; "
        "aMapAdded tracking misses duplicate; one corrected, one left in original orientation — IS the defect; "
        "mixed-orientation shell breaks closure assumptions downstream — IS the model impact; "
        "fix: FixFaceOrientation must detect and skip or unify duplicate face geometry; "
        "emit E_FIX_ORIENTATION_DUPLICATE when shell contains duplicate face geometry"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Base face: unit square in Z=0 plane
p00 = cp(0, 0, 0); v00 = f.vertex_point(p00)
p10 = cp(1, 0, 0); v10 = f.vertex_point(p10)
p11 = cp(1, 1, 0); v11 = f.vertex_point(p11)
p01 = cp(0, 1, 0); v01 = f.vertex_point(p01)

e_b0 = led(v00, v10, p00,  1, 0, 0)
e_b1 = led(v10, v11, p10,  0, 1, 0)
e_b2 = led(v11, v01, p11, -1, 0, 0)
e_b3 = led(v01, v00, p01,  0,-1, 0)

loop_base = f.edge_loop([
    f.oriented_edge(e_b0, True),
    f.oriented_edge(e_b1, True),
    f.oriented_edge(e_b2, True),
    f.oriented_edge(e_b3, True),
])
plane_base = f.plane(f.axis2_placement_3d(p00, dir3(0, 0, 1), dir3(1, 0, 0)))
face_base = f.advanced_face([f.face_outer_bound(loop_base, orientation=True)], plane_base, same_sense=True)

# Duplicate face geometry: unit square in Z=1 plane (first copy)
q00 = cp(0, 0, 1); w00 = f.vertex_point(q00)
q10 = cp(1, 0, 1); w10 = f.vertex_point(q10)
q11 = cp(1, 1, 1); w11 = f.vertex_point(q11)
q01 = cp(0, 1, 1); w01 = f.vertex_point(q01)

e_d0 = led(w00, w10, q00,  1, 0, 0)
e_d1 = led(w10, w11, q10,  0, 1, 0)
e_d2 = led(w11, w01, q11, -1, 0, 0)
e_d3 = led(w01, w00, q01,  0,-1, 0)

loop_dup_a = f.edge_loop([
    f.oriented_edge(e_d0, True),
    f.oriented_edge(e_d1, True),
    f.oriented_edge(e_d2, True),
    f.oriented_edge(e_d3, True),
])
plane_dup = f.plane(f.axis2_placement_3d(q00, dir3(0, 0, 1), dir3(1, 0, 0)))
face_dup_a = f.advanced_face([f.face_outer_bound(loop_dup_a, orientation=True)], plane_dup, same_sense=True)

# Duplicate face: same geometry, same_sense=False — IS the duplicate with inverted orientation
r00 = cp(0, 0, 1); x00 = f.vertex_point(r00)
r10 = cp(1, 0, 1); x10 = f.vertex_point(r10)
r11 = cp(1, 1, 1); x11 = f.vertex_point(r11)
r01 = cp(0, 1, 1); x01 = f.vertex_point(r01)

e_e0 = led(x00, x10, r00,  1, 0, 0)
e_e1 = led(x10, x11, r10,  0, 1, 0)
e_e2 = led(x11, x01, r11, -1, 0, 0)
e_e3 = led(x01, x00, r01,  0,-1, 0)

loop_dup_b = f.edge_loop([
    f.oriented_edge(e_e0, True),
    f.oriented_edge(e_e1, True),
    f.oriented_edge(e_e2, True),
    f.oriented_edge(e_e3, True),
])
plane_dup_b = f.plane(f.axis2_placement_3d(r00, dir3(0, 0, 1), dir3(1, 0, 0)))
# same_sense=False: IS the duplicate with original (uncorrected) orientation
face_dup_b = f.advanced_face([f.face_outer_bound(loop_dup_b, orientation=True)], plane_dup_b, same_sense=False)

# CLOSED_SHELL: three faces (base + two duplicates) IS the mixed-orientation mechanism
shell = f.closed_shell([face_base, face_dup_a, face_dup_b])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
