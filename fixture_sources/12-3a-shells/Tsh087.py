"""Tsh087 — ShapeFix_Shell.Perform face-removal during iteration.

Catalog claim: Shell with three faces where middle face (intentionally
degenerate or marked for removal) gets excised during Perform loop.
Subsequent iteration references stale face index from before removal,
causing index bounds violation or silent data corruption.

Mechanism IS the shell structure: OPEN_SHELL contains 3 ADVANCED_FACEs.
Face B (middle) IS wired as a zero-area degenerate face: all four
VERTEX_POINTs share the same coordinates (1,0,0), so every EDGE_CURVE
collapses to zero length. The degenerate FACE IS directly embedded in the
ADVANCED_FACE topology between two valid neighbours. ShapeFix_Shell.Perform
encounters the degenerate face and removes it mid-loop; the iterator
continues with a stale face list, reading past the (now-shrunk) valid index
range and silently corrupting or crashing.

Tier-3 assertion: load == "ok"

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh087",
    defect=(
        "OPEN_SHELL with 3 ADVANCED_FACEs; "
        "Face A (x=0..1) IS a valid unit quad; "
        "Face B (middle) IS wired degenerate: all 4 VERTEX_POINTs at (1,0,0); "
        "every EDGE_CURVE of Face B IS zero-length — IS the mechanism; "
        "degenerate zero-area face IS directly embedded in ADVANCED_FACE topology; "
        "Face C (x=1..2) IS a valid unit quad; "
        "ShapeFix_Shell.Perform removes Face B mid-loop; "
        "stale face index references removed entry causing bounds violation; "
        "fix: snapshot face list before Perform loop or use stable iterator"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Face A: valid unit quad x=0..1, y=0..1, z=0
pA00 = cp(0, 0, 0); pA10 = cp(1, 0, 0)
pA11 = cp(1, 1, 0); pA01 = cp(0, 1, 0)
vA00 = f.vertex_point(pA00); vA10 = f.vertex_point(pA10)
vA11 = f.vertex_point(pA11); vA01 = f.vertex_point(pA01)
eA0 = led(vA00, vA10, pA00,  1, 0, 0)
eA1 = led(vA10, vA11, pA10,  0, 1, 0)
eA2 = led(vA11, vA01, pA11, -1, 0, 0)
eA3 = led(vA01, vA00, pA01,  0,-1, 0)
loopA = f.edge_loop([
    f.oriented_edge(eA0, True), f.oriented_edge(eA1, True),
    f.oriented_edge(eA2, True), f.oriented_edge(eA3, True),
])
plA = f.plane(f.axis2_placement_3d(pA00, dir3(0, 0, 1), dir3(1, 0, 0)))
faceA = f.advanced_face([f.face_outer_bound(loopA)], plA, same_sense=True)

# Face B: degenerate — all 4 vertices at same point (1,0,0) IS the mechanism
pDeg = cp(1, 0, 0)
vD0 = f.vertex_point(pDeg); vD1 = f.vertex_point(pDeg)
vD2 = f.vertex_point(pDeg); vD3 = f.vertex_point(pDeg)
# Zero-length edges: each edge_curve starts and ends at same coordinate
eD0 = led(vD0, vD1, pDeg, 1, 0, 0)
eD1 = led(vD1, vD2, pDeg, 0, 1, 0)
eD2 = led(vD2, vD3, pDeg, -1, 0, 0)
eD3 = led(vD3, vD0, pDeg, 0, -1, 0)
loopB = f.edge_loop([
    f.oriented_edge(eD0, True), f.oriented_edge(eD1, True),
    f.oriented_edge(eD2, True), f.oriented_edge(eD3, True),
])
plB = f.plane(f.axis2_placement_3d(pDeg, dir3(0, 0, 1), dir3(1, 0, 0)))
# Degenerate face IS wired directly into shell topology as Face B (middle)
faceB = f.advanced_face([f.face_outer_bound(loopB)], plB, same_sense=True)

# Face C: valid unit quad x=1..2, y=0..1, z=0
pC10 = cp(1, 0, 0); pC20 = cp(2, 0, 0)
pC21 = cp(2, 1, 0); pC11 = cp(1, 1, 0)
vC10 = f.vertex_point(pC10); vC20 = f.vertex_point(pC20)
vC21 = f.vertex_point(pC21); vC11 = f.vertex_point(pC11)
eC0 = led(vC10, vC20, pC10,  1, 0, 0)
eC1 = led(vC20, vC21, pC20,  0, 1, 0)
eC2 = led(vC21, vC11, pC21, -1, 0, 0)
eC3 = led(vC11, vC10, pC11,  0,-1, 0)
loopC = f.edge_loop([
    f.oriented_edge(eC0, True), f.oriented_edge(eC1, True),
    f.oriented_edge(eC2, True), f.oriented_edge(eC3, True),
])
plC = f.plane(f.axis2_placement_3d(pC10, dir3(0, 0, 1), dir3(1, 0, 0)))
faceC = f.advanced_face([f.face_outer_bound(loopC)], plC, same_sense=True)

# OPEN_SHELL: degenerate Face B IS embedded between valid Face A and Face C
shell = f.open_shell([faceA, faceB, faceC])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
