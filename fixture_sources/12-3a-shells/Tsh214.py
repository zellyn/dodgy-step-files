"""Tsh214 — ShapeFix_Shell.FixFaceOrientation.duplicate_faces_undetected.

Catalog claim: Duplicate faces in shell; aMapAdded detects but only warns;
independent orientation fixes create inconsistency.

Mechanism IS the shell structure: AN OPEN_SHELL containing TWO IDENTICAL
ADVANCED_FACEs (same plane, same boundary loop geometry, same surface) — IS
the duplicate-faces defect trigger. ShapeFix_Shell.FixFaceOrientation IS the
defect path: aMapAdded detects the duplicate face on the second pass and warns,
but does NOT skip it; independent orientation fixes are applied to both copies
in isolation, yielding inconsistent outward-normal directions between the
duplicate pair — IS the defect.

Tier-3 assertion: n_faces_total == 2

live oracle: occt=shape(1)/shape(1) gmsh=shape(10) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh214",
    defect=(
        "OPEN_SHELL with TWO IDENTICAL ADVANCED_FACEs (same plane geometry, same loop) IS the duplicate-faces defect trigger; "
        "face_a IS unit square (0,0,0)-(1,1,0) with normal +Z — IS the first copy; "
        "face_b IS IDENTICAL unit square (0,0,0)-(1,1,0) with normal +Z — IS the duplicate copy; "
        "face_a and face_b share the same PLANE placement and same boundary geometry — IS the duplicate condition; "
        "face_b has same_sense=False to differ in sense but share topology — IS the orientation inconsistency setup; "
        "FixFaceOrientation IS the defect path: aMapAdded IS populated after first face fix; "
        "aMapAdded detects face_b as duplicate and warns — IS the warning-only behavior; "
        "aMapAdded does NOT skip face_b — IS the detection-without-suppression gap; "
        "independent orientation fix IS applied to face_b in isolation — IS the inconsistent fix; "
        "result: duplicate faces receive independently computed orientations — IS the inconsistency; "
        "fix: FixFaceOrientation must skip or unify orientation of aMapAdded-detected duplicates; "
        "emit E_DUPLICATE_FACE_ORIENTATION_CONFLICT when duplicate face escapes consistent fixing"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Shared corner points — IS the identical geometry for both faces
p00 = cp(0, 0, 0); v00 = f.vertex_point(p00)
p10 = cp(1, 0, 0); v10 = f.vertex_point(p10)
p11 = cp(1, 1, 0); v11 = f.vertex_point(p11)
p01 = cp(0, 1, 0); v01 = f.vertex_point(p01)

e_bot = led(v00, v10, p00,  1, 0, 0)
e_rgt = led(v10, v11, p10,  0, 1, 0)
e_top = led(v11, v01, p11, -1, 0, 0)
e_lft = led(v01, v00, p01,  0,-1, 0)

# face_a loop — IS the first face boundary
loop_a = f.edge_loop([
    f.oriented_edge(e_bot, True),
    f.oriented_edge(e_rgt, True),
    f.oriented_edge(e_top, True),
    f.oriented_edge(e_lft, True),
])

# face_b loop — IS the duplicate face boundary (same edges, same geometry)
loop_b = f.edge_loop([
    f.oriented_edge(e_bot, True),
    f.oriented_edge(e_rgt, True),
    f.oriented_edge(e_top, True),
    f.oriented_edge(e_lft, True),
])

plane = f.plane(f.axis2_placement_3d(p00, dir3(0, 0, 1), dir3(1, 0, 0)))

# face_a: same_sense=True — IS the first copy
face_a = f.advanced_face([f.face_outer_bound(loop_a, orientation=True)], plane, same_sense=True)
# face_b: same_sense=False — IS the duplicate with inverted sense (orientation inconsistency)
face_b = f.advanced_face([f.face_outer_bound(loop_b, orientation=True)], plane, same_sense=False)

# OPEN_SHELL: two duplicate faces — IS the duplicate-faces-undetected mechanism
shell = f.open_shell([face_a, face_b])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
