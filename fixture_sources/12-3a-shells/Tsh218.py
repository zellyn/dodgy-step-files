"""Tsh218 — ShapeFix_Shell.FixFaceOrientation.shells_extraction_loss.

Catalog claim: GetShells() fails to partition disconnected face clusters;
edge-classification gap creates orphaned faces.

Mechanism IS the shell structure: TWO DISCONNECTED ADVANCED_FACEs (no shared
edges, no connectivity) placed in a single OPEN_SHELL IS the defect trigger.
GetShells() must partition connected components; the two isolated faces ARE
the two separate clusters. Gap in edge-classification logic causes one cluster
to be orphaned — IS the extraction-loss defect.

Tier-3 assertion: n_faces_total == 2

live oracle: occt=shape(1)/shape(1) gmsh=shape(14) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh218",
    defect=(
        "OPEN_SHELL with TWO DISCONNECTED ADVANCED_FACEs IS the shells_extraction_loss trigger; "
        "face A IS a unit-square at Z=0 — IS the first disconnected cluster; "
        "face B IS a unit-square at Z=5 (5 units away, no shared edges) — IS the second disconnected cluster; "
        "no shared vertices or edges between face A and face B — IS the disconnected topology; "
        "GetShells() must partition all faces into connected components — IS the partitioning requirement; "
        "edge-classification gap in GetShells() fails to reach face B — IS the extraction-loss defect; "
        "face B IS orphaned and discarded — IS the shell-extraction-loss outcome; "
        "fix: GetShells() must classify ALL edges and reach all connected clusters; "
        "emit E_SHELLS_EXTRACTION_LOSS when faces remain after partitioning"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Face A — unit square at Z=0 (cluster 1, IS the first connected component)
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

# Face B — unit square at Z=5, NO shared edges with face A (cluster 2, IS the orphaned component)
pB00 = cp(0, 0, 5); vB00 = f.vertex_point(pB00)
pB10 = cp(1, 0, 5); vB10 = f.vertex_point(pB10)
pB11 = cp(1, 1, 5); vB11 = f.vertex_point(pB11)
pB01 = cp(0, 1, 5); vB01 = f.vertex_point(pB01)

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
plane_B = f.plane(f.axis2_placement_3d(pB00, dir3(0, 0, 1), dir3(1, 0, 0)))
face_B = f.advanced_face([f.face_outer_bound(loop_B, orientation=True)], plane_B, same_sense=True)

# OPEN_SHELL: two disconnected faces — IS the GetShells() partition-failure trigger
shell = f.open_shell([face_A, face_B])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
