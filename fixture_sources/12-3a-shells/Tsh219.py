"""Tsh219 — duplicate_faces_undetected.

Catalog claim: Duplicate faces in shell; aMapAdded only warns. Independent
orientation fixes yield inconsistent outward directions. Closure criterion fails.

Mechanism IS the shell structure: THREE ADVANCED_FACEs in one OPEN_SHELL where
TWO FACES ARE CONGRUENT (same geometry, same position) IS the defect trigger.
aMapAdded tracks duplicates in FixFaceOrientation but only emits a warning;
independent orientation fixes on each duplicate may yield opposing outward
normals — IS the inconsistent-direction defect. Closure criterion checks shared
edges; duplicate faces share no edges topologically, so free edges remain —
IS the closure-failure outcome.

Tier-3 assertion: n_faces_total == 3

live oracle: occt=shape(1)/shape(1) gmsh=shape(19) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh219",
    defect=(
        "OPEN_SHELL with THREE ADVANCED_FACEs where TWO ARE CONGRUENT IS the duplicate_faces_undetected trigger; "
        "face A IS a unit-square at Z=0 with same_sense=True — IS the base face; "
        "face B IS a congruent unit-square at Z=0 with same_sense=False — IS the duplicate face (different orientation); "
        "face C IS a unit-square at Z=1 with same_sense=True — IS the distinct third face; "
        "face A and face B share the SAME geometry but are SEPARATE ADVANCED_FACE entities — IS the duplication; "
        "aMapAdded in FixFaceOrientation detects the duplicate but only warns — IS the detection gap; "
        "independent orientation fix on face A yields outward normal +Z — IS the first direction; "
        "independent orientation fix on face B yields outward normal -Z — IS the inconsistent direction; "
        "inconsistent outward normals on congruent faces — IS the orientation-inconsistency defect; "
        "free edges remain on face C because face A/B topology is not shared — IS the closure-criterion failure; "
        "fix: aMapAdded duplicate detection must trigger deduplication, not just warn; "
        "emit E_DUPLICATE_FACES_UNDETECTED when congruent faces produce orientation inconsistency"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Shared corners for the Z=0 plane (face A)
pA00 = cp(0, 0, 0); vA00 = f.vertex_point(pA00)
pA10 = cp(1, 0, 0); vA10 = f.vertex_point(pA10)
pA11 = cp(1, 1, 0); vA11 = f.vertex_point(pA11)
pA01 = cp(0, 1, 0); vA01 = f.vertex_point(pA01)

eA_bot = led(vA00, vA10, pA00,  1, 0, 0)
eA_rgt = led(vA10, vA11, pA10,  0, 1, 0)
eA_top = led(vA11, vA01, pA11, -1, 0, 0)
eA_lft = led(vA01, vA00, pA01,  0,-1, 0)

loop_A = f.edge_loop([
    f.oriented_edge(eA_bot, True),
    f.oriented_edge(eA_rgt, True),
    f.oriented_edge(eA_top, True),
    f.oriented_edge(eA_lft, True),
])
plane_A = f.plane(f.axis2_placement_3d(pA00, dir3(0, 0, 1), dir3(1, 0, 0)))
face_A = f.advanced_face([f.face_outer_bound(loop_A, orientation=True)], plane_A, same_sense=True)

# Duplicate face B — congruent unit-square at Z=0 but SEPARATE edges/vertices,
# same_sense=False (IS the inconsistent duplicate orientation)
pB00 = cp(0, 0, 0); vB00 = f.vertex_point(pB00)
pB10 = cp(1, 0, 0); vB10 = f.vertex_point(pB10)
pB11 = cp(1, 1, 0); vB11 = f.vertex_point(pB11)
pB01 = cp(0, 1, 0); vB01 = f.vertex_point(pB01)

eB_bot = led(vB00, vB10, pB00,  1, 0, 0)
eB_rgt = led(vB10, vB11, pB10,  0, 1, 0)
eB_top = led(vB11, vB01, pB11, -1, 0, 0)
eB_lft = led(vB01, vB00, pB01,  0,-1, 0)

loop_B = f.edge_loop([
    f.oriented_edge(eB_bot, True),
    f.oriented_edge(eB_rgt, True),
    f.oriented_edge(eB_top, True),
    f.oriented_edge(eB_lft, True),
])
plane_B = f.plane(f.axis2_placement_3d(pB00, dir3(0, 0, -1), dir3(1, 0, 0)))
face_B = f.advanced_face([f.face_outer_bound(loop_B, orientation=True)], plane_B, same_sense=False)

# Face C — distinct unit-square at Z=1
pC00 = cp(0, 0, 1); vC00 = f.vertex_point(pC00)
pC10 = cp(1, 0, 1); vC10 = f.vertex_point(pC10)
pC11 = cp(1, 1, 1); vC11 = f.vertex_point(pC11)
pC01 = cp(0, 1, 1); vC01 = f.vertex_point(pC01)

eC_bot = led(vC00, vC10, pC00,  1, 0, 0)
eC_rgt = led(vC10, vC11, pC10,  0, 1, 0)
eC_top = led(vC11, vC01, pC11, -1, 0, 0)
eC_lft = led(vC01, vC00, pC01,  0,-1, 0)

loop_C = f.edge_loop([
    f.oriented_edge(eC_bot, True),
    f.oriented_edge(eC_rgt, True),
    f.oriented_edge(eC_top, True),
    f.oriented_edge(eC_lft, True),
])
plane_C = f.plane(f.axis2_placement_3d(pC00, dir3(0, 0, 1), dir3(1, 0, 0)))
face_C = f.advanced_face([f.face_outer_bound(loop_C, orientation=True)], plane_C, same_sense=True)

# OPEN_SHELL: three faces, two are congruent duplicates — IS the aMapAdded detection gap
shell = f.open_shell([face_A, face_B, face_C])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
