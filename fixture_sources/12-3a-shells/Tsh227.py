"""Tsh227 — ShapeFix_Shell.FixFaceOrientation error_faces_mebius_assumption.

Catalog claim: Two coplanar unit squares with ambiguous orientations. aErrFaces
mis-classified as Mobius-leaf; intrinsic non-orientability unconfirmed, spurious
single-face shells created.

Mechanism IS the shell structure: TWO COPLANAR ADJACENT ADVANCED_FACEs sharing
ONE EDGE with OPPOSITE same_sense flags in an OPEN_SHELL IS the defect trigger.
The shared edge between face A (same_sense=True) and face B (same_sense=False)
creates an orientation conflict. FixFaceOrientation cannot resolve the conflict
and places both faces in aErrFaces. aErrFaces logic incorrectly labels the
configuration as a Mobius-leaf (non-orientable) and creates spurious single-face
shells — IS the Mobius-assumption defect.

Tier-3 assertion: n_faces_total == 2

live oracle: occt=shape(1)/shape(1) gmsh=shape(18) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh227",
    defect=(
        "OPEN_SHELL with TWO COPLANAR ADJACENT ADVANCED_FACEs sharing one edge IS the error_faces_mebius_assumption trigger; "
        "face A IS a unit-square at X=0..1, Y=0..1, Z=0 with same_sense=True — IS the first face; "
        "face B IS a unit-square at X=1..2, Y=0..1, Z=0 with same_sense=False — IS the second face with flipped orientation; "
        "shared edge IS e_mid from (1,0,0) to (1,1,0) — IS the common topological edge; "
        "face A uses e_mid forward (same_sense=True) — IS the A-side orientation; "
        "face B uses e_mid reversed (same_sense=False) — IS the B-side conflicting orientation; "
        "shared edge orientation conflict prevents FixFaceOrientation from resolving — IS the orientation ambiguity; "
        "both faces are placed in aErrFaces — IS the error-face classification; "
        "aErrFaces logic applies Mobius-leaf assumption — IS the mis-classification; "
        "intrinsic non-orientability is NOT confirmed for two coplanar squares — IS the incorrect assumption; "
        "spurious single-face shells created from aErrFaces — IS the erroneous shell decomposition; "
        "fix: aErrFaces must verify actual non-orientability before applying Mobius-leaf handling; "
        "emit E_ERROR_FACES_MEBIUS_ASSUMPTION when aErrFaces labels orientable face pair as Mobius-leaf"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Face A corners: (0,0,0) to (1,1,0)
pA00 = cp(0, 0, 0);  vA00 = f.vertex_point(pA00)
pA10 = cp(1, 0, 0);  vA10 = f.vertex_point(pA10)
pA11 = cp(1, 1, 0);  vA11 = f.vertex_point(pA11)
pA01 = cp(0, 1, 0);  vA01 = f.vertex_point(pA01)

# Face B corners: (1,0,0) to (2,1,0) — shares X=1 edge with face A
pB10 = cp(2, 0, 0);  vB10 = f.vertex_point(pB10)
pB11 = cp(2, 1, 0);  vB11 = f.vertex_point(pB11)

# Shared middle edge (X=1 column) — IS the common topological edge
e_mid = led(vA10, vA11, pA10, 0, 1, 0)   # (1,0,0) -> (1,1,0)

# Face A private edges
eA_s = led(vA00, vA10, pA00,  1, 0, 0)   # (0,0,0) -> (1,0,0)
eA_n = led(vA11, vA01, pA11, -1, 0, 0)   # (1,1,0) -> (0,1,0)
eA_w = led(vA01, vA00, pA01,  0,-1, 0)   # (0,1,0) -> (0,0,0)

# Face B private edges
eB_s = led(vA10, vB10, pA10,  1, 0, 0)   # (1,0,0) -> (2,0,0)
eB_e = led(vB10, vB11, pB10,  0, 1, 0)   # (2,0,0) -> (2,1,0)
eB_n = led(vB11, vA11, pB11, -1, 0, 0)   # (2,1,0) -> (1,1,0)

# Face A loop: CCW from (0,0) — same_sense=True, normal = +Z
loop_A = f.edge_loop([
    f.oriented_edge(eA_s,  True),    # (0,0)->(1,0)
    f.oriented_edge(e_mid, True),    # (1,0)->(1,1)
    f.oriented_edge(eA_n,  True),    # (1,1)->(0,1)
    f.oriented_edge(eA_w,  True),    # (0,1)->(0,0)
])
plane_A = f.plane(f.axis2_placement_3d(pA00, dir3(0, 0, 1), dir3(1, 0, 0)))
face_A = f.advanced_face([f.face_outer_bound(loop_A, orientation=True)], plane_A, same_sense=True)

# Face B loop: uses e_mid reversed — IS the orientation conflict (same_sense=False)
loop_B = f.edge_loop([
    f.oriented_edge(eB_s,  True),    # (1,0)->(2,0)
    f.oriented_edge(eB_e,  True),    # (2,0)->(2,1)
    f.oriented_edge(eB_n,  True),    # (2,1)->(1,1)
    f.oriented_edge(e_mid, False),   # (1,1)->(1,0) reversed — IS the conflict
])
plane_B = f.plane(f.axis2_placement_3d(pA10, dir3(0, 0, 1), dir3(1, 0, 0)))
face_B = f.advanced_face([f.face_outer_bound(loop_B, orientation=True)], plane_B, same_sense=False)

# OPEN_SHELL: two coplanar adjacent faces with shared-edge orientation conflict
# IS the aErrFaces Mobius-assumption trigger
shell = f.open_shell([face_A, face_B])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
