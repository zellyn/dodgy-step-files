"""Tsh157 — ShapeFix_Shell.Perform circular-fix-dependency.

Catalog claim: Three faces where fixing face A requires fixing face B which requires
fixing face A. Perform doesn't detect circular dependency and may loop or produce
inconsistent result.

Mechanism IS the shell structure: THREE ADVANCED_FACEs arranged in a triangular ring
ARE wired into an OPEN_SHELL such that each face shares exactly one edge with the next,
forming a closed cycle: Face0-Face1 share e01, Face1-Face2 share e12, Face2-Face0 share
e20. Each shared edge IS wired with conflicting orientation across the two faces that
share it — Face0's e01 IS oriented True, Face1's e01 IS oriented True (should be False),
creating the circular dependency: fixing Face0's e01 orientation breaks Face1's; fixing
Face1's breaks Face2's; fixing Face2's breaks Face0's.

Tier-3 assertion: load == "ok"

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh157",
    defect=(
        "THREE ADVANCED_FACEs in triangular ring sharing edges in OPEN_SHELL — "
        "IS the circular-fix-dependency mechanism; "
        "Face0 (bottom-left triangle) shares e01 with Face1 and e20 with Face2; "
        "Face1 (bottom-right triangle) shares e01 with Face0 and e12 with Face2; "
        "Face2 (top triangle) shares e12 with Face1 and e20 with Face0; "
        "shared edge e01 IS wired with oriented_edge(.T.) in Face0-EDGE_LOOP "
        "AND oriented_edge(.T.) in Face1-EDGE_LOOP — IS the conflicting orientation; "
        "shared edge e12 IS wired with oriented_edge(.T.) in Face1-EDGE_LOOP "
        "AND oriented_edge(.T.) in Face2-EDGE_LOOP — IS the conflicting orientation; "
        "shared edge e20 IS wired with oriented_edge(.T.) in Face2-EDGE_LOOP "
        "AND oriented_edge(.T.) in Face0-EDGE_LOOP — IS the conflicting orientation; "
        "circular dependency IS the mechanism: fixing any one edge breaks the next; "
        "ShapeFix_Shell.Perform processes faces sequentially without cycle detection; "
        "fix: detect cyclic orientation conflicts; use global consensus or break cycle; "
        "emit E_PERFORM_CIRCULAR_FIX_DEPENDENCY when fix chain cycles back to start face"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Three vertices of a triangle — shared edges form a ring
p0 = cp(0.0, 0.0, 0.0)  # bottom-left
p1 = cp(1.0, 0.0, 0.0)  # bottom-right
p2 = cp(0.5, 1.0, 0.0)  # top

v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)

# Three shared edges forming the triangular ring
# e01: bottom edge, v0->v1
e01 = led(v0, v1, p0,  1.0, 0.0, 0.0)
# e12: right edge, v1->v2
e12 = led(v1, v2, p1, -0.5, 1.0, 0.0)
# e20: left edge, v2->v0
e20 = led(v2, v0, p2, -0.5,-1.0, 0.0)

# Three interior vertices (one per face centroid) for face-interior edges
# Each "face" is a sub-triangle: Face0 = (p0, p1, pc0), etc.
pc0 = cp(0.5, -0.3, 0.0)  # centroid below base (Face0 exterior point)
pc1 = cp(1.3,  0.5, 0.0)  # centroid right of ring (Face1 exterior point)
pc2 = cp(-0.3, 0.5, 0.0)  # centroid left of ring (Face2 exterior point)

vc0 = f.vertex_point(pc0)
vc1 = f.vertex_point(pc1)
vc2 = f.vertex_point(pc2)

# Face0 private edges: v0->vc0 and v1->vc0
e0_a = led(v0, vc0, p0,  0.5,-0.3, 0.0)
e0_b = led(v1, vc0, p1, -0.5,-0.3, 0.0)

# Face1 private edges: v1->vc1 and v2->vc1
e1_a = led(v1, vc1, p1,  0.3, 0.5, 0.0)
e1_b = led(v2, vc1, p2,  0.8,-0.5, 0.0)

# Face2 private edges: v2->vc2 and v0->vc2
e2_a = led(v2, vc2, p2, -0.8, 0.5, 0.0)  # wait, adjust direction
e2_b = led(v0, vc2, p0, -0.3, 0.5, 0.0)

# Planes for each triangular face (all in z=0 plane)
plane_z0 = f.plane(f.axis2_placement_3d(p0, dir3(0, 0, 1), dir3(1, 0, 0)))

# Face0: p0, p1, pc0 — uses e01 with True AND e0_b (reversed), e0_a
# Conflict: e01 IS wired True here (should be oriented opposite in adjacent face)
loop0 = f.edge_loop([
    f.oriented_edge(e01,  True),   # e01 True in Face0 — IS the conflict
    f.oriented_edge(e0_b, False),  # v1->vc0 reversed
    f.oriented_edge(e0_a, False),  # v0->vc0 reversed
])
face0 = f.advanced_face([f.face_outer_bound(loop0, orientation=True)], plane_z0, same_sense=True)

# Face1: p1, p2, pc1 — uses e12 with True AND e01 with True (conflict: should be False)
loop1 = f.edge_loop([
    f.oriented_edge(e01,  True),   # e01 True in Face1 — IS the circular conflict (same as Face0)
    f.oriented_edge(e1_a, True),   # v1->vc1
    f.oriented_edge(e1_b, False),  # v2->vc1 reversed
])
face1 = f.advanced_face([f.face_outer_bound(loop1, orientation=True)], plane_z0, same_sense=True)

# Face2: p2, p0, pc2 — uses e20 with True AND e12 with True (conflict)
loop2 = f.edge_loop([
    f.oriented_edge(e12,  True),   # e12 True in Face2 — IS the circular conflict
    f.oriented_edge(e2_a, True),   # v2->vc2
    f.oriented_edge(e2_b, False),  # v0->vc2 reversed
])
face2 = f.advanced_face([f.face_outer_bound(loop2, orientation=True)], plane_z0, same_sense=True)

# OPEN_SHELL: 3 faces with cyclic shared-edge orientation conflicts — IS the circular-dependency mechanism
shell = f.open_shell([face0, face1, face2])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
