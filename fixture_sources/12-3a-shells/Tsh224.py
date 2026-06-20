"""Tsh224 — ShapeFix_Shell.FixFaceOrientation duplicate_faces_undetected.

Catalog claim: aMapAdded tracks duplicates but only warns; FixFaceOrientation
flips one face, leaves other unchanged. Inconsistent outward directions result.

Mechanism IS the shell structure: TWO CONGRUENT ADVANCED_FACEs (both unit
squares, face A at Z=0, face B also at Z=0 with same_sense=False) in an
OPEN_SHELL IS the defect trigger. aMapAdded detects face B as a duplicate
of face A by geometry but only logs a warning without repairing; FixFaceOrientation
flips only face A (the first seen), leaving face B with opposite orientation.
The inconsistent outward normals ARE the duplicate_faces_undetected defect.

Tier-3 assertion: n_faces_total == 2

live oracle: occt=shape(1)/shape(1) gmsh=shape(18) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh224",
    defect=(
        "OPEN_SHELL with TWO CONGRUENT ADVANCED_FACEs IS the duplicate_faces_undetected trigger; "
        "face A IS a unit-square at Z=0 with same_sense=True — IS the reference face; "
        "face B IS a unit-square at Z=0 with same_sense=False — IS the congruent duplicate face with flipped orientation; "
        "face A and face B share no edges topologically — IS the distinct edge-set condition; "
        "aMapAdded maps face A geometry — IS the duplicate-detection map entry; "
        "aMapAdded detects face B as congruent to face A — IS the duplicate detection; "
        "aMapAdded only warns, does not remove or repair face B — IS the undetected-duplicate defect; "
        "FixFaceOrientation flips face A to outward normal — IS the partial fix; "
        "face B IS NOT flipped by FixFaceOrientation — IS the inconsistent direction result; "
        "face A normal IS +Z, face B normal IS -Z — IS the inconsistent outward-direction defect; "
        "fix: aMapAdded must remove or repair duplicate congruent faces, not merely warn; "
        "emit E_DUPLICATE_FACES_UNDETECTED when congruent faces survive FixFaceOrientation with opposite normals"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Face A — unit square at Z=0, same_sense=True (reference face)
pA00 = cp(0, 0, 0);  vA00 = f.vertex_point(pA00)
pA10 = cp(1, 0, 0);  vA10 = f.vertex_point(pA10)
pA11 = cp(1, 1, 0);  vA11 = f.vertex_point(pA11)
pA01 = cp(0, 1, 0);  vA01 = f.vertex_point(pA01)

eA_s = led(vA00, vA10, pA00,  1, 0, 0)
eA_e = led(vA10, vA11, pA10,  0, 1, 0)
eA_n = led(vA11, vA01, pA11, -1, 0, 0)
eA_w = led(vA01, vA00, pA01,  0,-1, 0)

loop_A = f.edge_loop([
    f.oriented_edge(eA_s, True),
    f.oriented_edge(eA_e, True),
    f.oriented_edge(eA_n, True),
    f.oriented_edge(eA_w, True),
])
plane_A = f.plane(f.axis2_placement_3d(pA00, dir3(0, 0, 1), dir3(1, 0, 0)))
face_A = f.advanced_face([f.face_outer_bound(loop_A, orientation=True)], plane_A, same_sense=True)

# Face B — congruent unit square at Z=0, same_sense=False (duplicate with flipped orientation)
# Distinct edge/vertex objects to represent topologically separate but geometrically congruent face
pB00 = cp(0, 0, 0);  vB00 = f.vertex_point(pB00)
pB10 = cp(1, 0, 0);  vB10 = f.vertex_point(pB10)
pB11 = cp(1, 1, 0);  vB11 = f.vertex_point(pB11)
pB01 = cp(0, 1, 0);  vB01 = f.vertex_point(pB01)

eB_s = led(vB00, vB10, pB00,  1, 0, 0)
eB_e = led(vB10, vB11, pB10,  0, 1, 0)
eB_n = led(vB11, vB01, pB11, -1, 0, 0)
eB_w = led(vB01, vB00, pB01,  0,-1, 0)

loop_B = f.edge_loop([
    f.oriented_edge(eB_s, True),
    f.oriented_edge(eB_e, True),
    f.oriented_edge(eB_n, True),
    f.oriented_edge(eB_w, True),
])
# Plane B same position as A — IS the congruent/duplicate geometry
plane_B = f.plane(f.axis2_placement_3d(pB00, dir3(0, 0, 1), dir3(1, 0, 0)))
face_B = f.advanced_face([f.face_outer_bound(loop_B, orientation=True)], plane_B, same_sense=False)

# OPEN_SHELL: two congruent unit-square faces at Z=0 — IS the aMapAdded duplicate trigger
shell = f.open_shell([face_A, face_B])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
