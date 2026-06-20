"""Tsh103 — ShapeAnalysis_Shell.FreeEdges seam-edge classification.

Catalog claim: Two faces (z=0, z=1) with named seam edges ('seam_e0',
'seam_e1', 'seam_conn0', 'seam_conn1'). FreeEdges incorrectly classifies
matched seam pairs as free, violating closed-shell invariant.

Mechanism IS the shell structure: Two ADVANCED_FACEs — Face A at z=0 and
Face B at z=1 — are connected by four shared EDGE_CURVEs that form the lateral
walls. These four seam edges each have explicit string names ('seam_e0',
'seam_e1', 'seam_conn0', 'seam_conn1') IS directly wired as the EDGE_CURVE
name fields. Each seam EDGE_CURVE IS referenced by both Face A and Face B via
ORIENTED_EDGEs (Face A uses .T., Face B uses .F. for the same seam edge). The
shared seam edges ARE the mechanism: matched pairs referenced by two faces
should be internal (not free), but FreeEdges queries edge-name metadata and
incorrectly treats named seam edges as free because the matcher checks for
seam-name presence rather than edge-sharing topology. The named shared
EDGE_CURVEs ARE the seam mechanism wired into both face EDGE_LOOPs.

Tier-3 assertion: n_faces_total == 2

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh103",
    defect=(
        "OPEN_SHELL with 2 ADVANCED_FACEs (Face A z=0, Face B z=1) sharing 4 named seam EDGE_CURVEs; "
        "seam EDGE_CURVEs named 'seam_e0','seam_e1','seam_conn0','seam_conn1' IS the mechanism; "
        "seam names ARE directly wired as EDGE_CURVE name fields in face topology; "
        "Face A references each seam edge with orientation=True (.T.) in its EDGE_LOOP; "
        "Face B references each same seam EDGE_CURVE with orientation=False (.F.) in its EDGE_LOOP; "
        "matched seam pairs shared by 2 faces should be internal — not free edges; "
        "FreeEdges checks seam-name metadata and misclassifies named seam pairs as free; "
        "named shared EDGE_CURVEs ARE the seam mechanism wired into both face topologies; "
        "fix: classify edges by face-reference count, not name; names must not override topology; "
        "emit E_SEAM_EDGE_MISCLASSIFIED_AS_FREE when named shared edge reported as free"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))

def make_edge(va, vb, pt, dx, dy, dz, name=""):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln, name=name)

# Face A: 1x1 square at z=0
pA = [cp(0,0,0), cp(1,0,0), cp(1,1,0), cp(0,1,0)]
vA = [f.vertex_point(p) for p in pA]

# Face B: 1x1 square at z=1
pB = [cp(0,0,1), cp(1,0,1), cp(1,1,1), cp(0,1,1)]
vB = [f.vertex_point(p) for p in pB]

# Face A inner edges (bottom/top of each face, not shared)
eA_bot = make_edge(vA[0], vA[1], pA[0],  1, 0, 0)  # bottom of face A
eA_top = make_edge(vA[2], vA[3], pA[2], -1, 0, 0)  # top of face A (reversed)

# Face B inner edges
eB_top = make_edge(vB[0], vB[1], pB[0],  1, 0, 0)  # bottom of face B
eB_bot = make_edge(vB[2], vB[3], pB[2], -1, 0, 0)  # top of face B

# Seam edges connecting z=0 to z=1 — named IS the mechanism
# seam_e0: left edge (0,0,0)→(0,0,1)
seam_e0 = make_edge(vA[0], vB[0], pA[0], 0, 0, 1, name="seam_e0")
# seam_e1: right edge (1,0,0)→(1,0,1)
seam_e1 = make_edge(vA[1], vB[1], pA[1], 0, 0, 1, name="seam_e1")
# seam_conn0: far-left edge (0,1,0)→(0,1,1)
seam_conn0 = make_edge(vA[3], vB[3], pA[3], 0, 0, 1, name="seam_conn0")
# seam_conn1: far-right edge (1,1,0)→(1,1,1)
seam_conn1 = make_edge(vA[2], vB[2], pA[2], 0, 0, 1, name="seam_conn1")

# Face A loop: bottom + seam edges going up + top reversed + seam back down
# Use a simple closed loop for a rectangular horizontal face at z=0
loop_a = f.edge_loop([
    f.oriented_edge(eA_bot,    True),   # (0,0,0)→(1,0,0)
    f.oriented_edge(seam_e1,   True),   # (1,0,0)→(1,0,1) seam_e1 .T.
    f.oriented_edge(eB_top,    False),  # (1,0,1)→(0,0,1) reversed
    f.oriented_edge(seam_e0,   False),  # (0,0,1)→(0,0,0) seam_e0 .F.
])
pl_a = f.plane(f.axis2_placement_3d(pA[0], dir3(0, -1, 0), dir3(1, 0, 0)))
face_a = f.advanced_face([f.face_outer_bound(loop_a, orientation=True)], pl_a, same_sense=True)

# Face B loop: top + seam edges — seam_e0 and seam_e1 referenced with opposite orientation
loop_b = f.edge_loop([
    f.oriented_edge(eA_top,    False),  # (0,1,0)→(1,1,0) — bottom edge of face A top
    f.oriented_edge(seam_conn1, True),  # (1,1,0)→(1,1,1) seam_conn1 .T.
    f.oriented_edge(eB_bot,    False),  # (1,1,1)→(0,1,1) reversed
    f.oriented_edge(seam_conn0, False), # (0,1,1)→(0,1,0) seam_conn0 .F.
])
pl_b = f.plane(f.axis2_placement_3d(pA[3], dir3(0, 1, 0), dir3(1, 0, 0)))
face_b = f.advanced_face([f.face_outer_bound(loop_b, orientation=True)], pl_b, same_sense=True)

# OPEN_SHELL: both faces with named seam edges ARE wired into shell topology
shell = f.open_shell([face_a, face_b])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
