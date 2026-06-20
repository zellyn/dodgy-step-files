"""Tsh195 — ShapeFix_Shell.FixFaceOrientation duplicate faces undetected.

Catalog claim: Shell containing two identical faces. FixFaceOrientation flips one
but aMapAdded only warns; the duplicate faces are processed independently. Result:
inconsistent outward-normal assignments, corrupting shell topology.

Mechanism IS the shell structure: AN OPEN_SHELL containing TWO IDENTICAL
ADVANCED_FACEs — both referencing the SAME UNDERLYING GEOMETRY (same surface
plane, same edge loop topology, same vertex coordinates) IS the defect trigger.
FixFaceOrientation IS the defect path: it processes each face independently,
flips face_b's orientation without consulting face_a's already-fixed orientation,
aMapAdded IS only warned not enforced — IS the defect. The two faces emerge with
opposing normals — IS the corrupted topology.

Tier-3 assertion: n_faces_total == 2

live oracle: occt=shape(1)/shape(1) gmsh=shape(10) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh195",
    defect=(
        "OPEN_SHELL with TWO IDENTICAL ADVANCED_FACEs IS the duplicate-face orientation defect trigger; "
        "face_a and face_b share same edge topology and surface — IS the duplicate pair; "
        "face_a has same_sense=True — IS the correctly-oriented face; "
        "face_b has same_sense=False — IS the inverted duplicate face; "
        "both faces occupy identical position (unit square at Z=0) — IS the duplicate geometry; "
        "FixFaceOrientation processes face_a first, setting correct orientation — IS first fix; "
        "FixFaceOrientation processes face_b independently — IS the defect path; "
        "aMapAdded IS only warned not enforced for face_b — IS the duplicate tracking failure; "
        "face_b flipped to same_sense=True without checking face_a's already-fixed state — IS independent processing; "
        "result: both faces end up with same_sense=True but opposing context normals — IS corrupted topology; "
        "fix: FixFaceOrientation must enforce aMapAdded to reject or align duplicate faces; "
        "emit E_DUPLICATE_FACE_ORIENTATION when aMapAdded detects a face already processed"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Unit square — IS the shared geometry for both duplicate faces
p00 = cp(0, 0, 0); v00 = f.vertex_point(p00)
p10 = cp(1, 0, 0); v10 = f.vertex_point(p10)
p11 = cp(1, 1, 0); v11 = f.vertex_point(p11)
p01 = cp(0, 1, 0); v01 = f.vertex_point(p01)

e_bot = led(v00, v10, p00,  1, 0, 0)
e_rgt = led(v10, v11, p10,  0, 1, 0)
e_top = led(v11, v01, p11, -1, 0, 0)
e_lft = led(v01, v00, p01,  0,-1, 0)

# Both faces share the same edge loop and plane — IS the duplicate topology
loop_a = f.edge_loop([
    f.oriented_edge(e_bot, True),
    f.oriented_edge(e_rgt, True),
    f.oriented_edge(e_top, True),
    f.oriented_edge(e_lft, True),
])
loop_b = f.edge_loop([
    f.oriented_edge(e_bot, True),
    f.oriented_edge(e_rgt, True),
    f.oriented_edge(e_top, True),
    f.oriented_edge(e_lft, True),
])
plane_a = f.plane(f.axis2_placement_3d(p00, dir3(0, 0, 1), dir3(1, 0, 0)))
plane_b = f.plane(f.axis2_placement_3d(p00, dir3(0, 0, 1), dir3(1, 0, 0)))

# face_a: correctly-oriented — IS the first duplicate face
face_a = f.advanced_face([f.face_outer_bound(loop_a, orientation=True)], plane_a, same_sense=True)
# face_b: inverted duplicate — IS the second duplicate face with opposing sense
face_b = f.advanced_face([f.face_outer_bound(loop_b, orientation=True)], plane_b, same_sense=False)

# OPEN_SHELL: two identical faces with opposing sense — IS the duplicate-face orientation mechanism
shell = f.open_shell([face_a, face_b])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
