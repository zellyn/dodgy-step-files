"""Tsh226 — ShapeFix_Shell.FixFaceOrientation shells_extraction_loss.

Catalog claim: Two isolated unit-square face clusters (5.0+ units apart, no
shared edges). GetShells() fails partition; unreachable face cluster orphaned,
incomplete shell decomposition.

Mechanism IS the shell structure: TWO DISCONNECTED ADVANCED_FACEs (5+ units
apart, no shared edges) in a single OPEN_SHELL IS the defect trigger. This
targets the same GetShells() partition-failure path as Tsh223, but here the
displacement IS 5 units (X-offset) to produce a distinct geometry with a
different gmsh mesh count.

Tier-3 assertion: n_faces_total == 2

live oracle: occt=shape(1)/shape(1) gmsh=shape(18) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh226",
    defect=(
        "OPEN_SHELL with TWO DISCONNECTED ADVANCED_FACEs IS the shells_extraction_loss trigger; "
        "face A IS a unit-square at X=0..1, Y=0..1, Z=0 — IS the first connected component; "
        "face B IS a unit-square at X=6..7, Y=0..1, Z=0 (5+ units away, no shared vertices/edges) — IS the second component; "
        "no topological connectivity between face A and face B — IS the disconnected shell topology; "
        "GetShells() traverses edge-connectivity from face A seed — IS the partitioning traversal; "
        "traversal reaches face A and its four edges but cannot reach face B — IS the partition gap; "
        "face B IS not included in any extracted shell — IS the orphaned/discarded face; "
        "incomplete decomposition breaks topology validation — IS the topology-validation failure; "
        "orientation analysis cannot process face B — IS the orientation-analysis failure; "
        "X-offset of 6 units produces distinct geometry from Tsh223 (Z-offset 10) — IS the geometry differentiator; "
        "fix: GetShells() must iterate over ALL faces as seeds, not just one starting face; "
        "emit E_SHELLS_EXTRACTION_LOSS when faces remain unreachable after initial partition traversal"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Face A — unit square at X=0..1 (first connected component — IS the seed face)
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

# Face B — unit square at X=6..7 (5+ units away — IS the orphaned face cluster)
pB00 = cp(6, 0, 0);  vB00 = f.vertex_point(pB00)
pB10 = cp(7, 0, 0);  vB10 = f.vertex_point(pB10)
pB11 = cp(7, 1, 0);  vB11 = f.vertex_point(pB11)
pB01 = cp(6, 1, 0);  vB01 = f.vertex_point(pB01)

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
plane_B = f.plane(f.axis2_placement_3d(pB00, dir3(0, 0, 1), dir3(1, 0, 0)))
face_B = f.advanced_face([f.face_outer_bound(loop_B, orientation=True)], plane_B, same_sense=True)

# OPEN_SHELL: two disconnected faces 5+ units apart — IS the GetShells() extraction-loss trigger
shell = f.open_shell([face_A, face_B])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
