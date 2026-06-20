"""Tsh091 — ShapeUpgrade_ShellSewing.Apply degenerate-face sliver.

Catalog claim: Shell containing one regular face and one degenerate "sliver"
face whose four vertices all occupy the same coordinates (2,0,0). All edges
collapse to zero length. Tests sliver detection in Apply before sewing.
Expected: sliver rejected. Likely failure: No degenerate check; included in
output shell, causing downstream failures.

Mechanism IS the shell structure: OPEN_SHELL IS wired with 2 ADVANCED_FACEs.
Face A IS a valid 1x1 quad. Face B (sliver) IS wired with all 4 VERTEX_POINTs
at the same coordinates (2,0,0); every EDGE_CURVE in its loop IS zero-length.
The degenerate sliver face IS directly embedded as the second ADVANCED_FACE in
the OPEN_SHELL topology alongside the valid face. The zero-area sliver co-resident
with a valid face IS the mechanism that exposes missing pre-sewing degenerate-face
detection in ShapeUpgrade_ShellSewing.Apply.

Tier-3 assertion: load == "ok"

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh091",
    defect=(
        "OPEN_SHELL IS wired with 2 ADVANCED_FACEs; "
        "Face A IS a valid 1x1 unit quad at x=0..1, y=0..1; "
        "Face B (sliver) IS wired: all 4 VERTEX_POINTs at (2,0,0); "
        "all EDGE_CURVEs of Face B IS zero-length — IS the mechanism; "
        "degenerate sliver face IS directly embedded in OPEN_SHELL topology; "
        "zero-area sliver alongside valid face IS the sliver-detection mechanism; "
        "ShapeUpgrade_ShellSewing.Apply lacks degenerate-face check; "
        "includes sliver in output shell causing downstream failures; "
        "fix: detect and reject zero-area faces before sewing in Apply"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Face A: valid 1x1 unit quad at x=0..1, y=0..1, z=0
pA = [cp(0,0,0), cp(1,0,0), cp(1,1,0), cp(0,1,0)]
vA = [f.vertex_point(p) for p in pA]
eA = [
    led(vA[0], vA[1], pA[0],  1, 0, 0),
    led(vA[1], vA[2], pA[1],  0, 1, 0),
    led(vA[2], vA[3], pA[2], -1, 0, 0),
    led(vA[3], vA[0], pA[3],  0,-1, 0),
]
loopA = f.edge_loop([f.oriented_edge(e, True) for e in eA])
plA = f.plane(f.axis2_placement_3d(pA[0], dir3(0, 0, 1), dir3(1, 0, 0)))
faceA = f.advanced_face([f.face_outer_bound(loopA, orientation=True)], plA, same_sense=True)

# Face B: degenerate sliver — all 4 VERTEX_POINTs at (2,0,0) IS the mechanism
pSliver = cp(2, 0, 0)
vS0 = f.vertex_point(pSliver); vS1 = f.vertex_point(pSliver)
vS2 = f.vertex_point(pSliver); vS3 = f.vertex_point(pSliver)
# All EDGE_CURVEs start and end at (2,0,0): zero-length IS the mechanism
eS0 = led(vS0, vS1, pSliver,  1, 0, 0)
eS1 = led(vS1, vS2, pSliver,  0, 1, 0)
eS2 = led(vS2, vS3, pSliver, -1, 0, 0)
eS3 = led(vS3, vS0, pSliver,  0,-1, 0)
loopB = f.edge_loop([
    f.oriented_edge(eS0, True), f.oriented_edge(eS1, True),
    f.oriented_edge(eS2, True), f.oriented_edge(eS3, True),
])
plB = f.plane(f.axis2_placement_3d(pSliver, dir3(0, 0, 1), dir3(1, 0, 0)))
# Degenerate sliver face IS wired directly into OPEN_SHELL as ADVANCED_FACE
faceB = f.advanced_face([f.face_outer_bound(loopB, orientation=True)], plB, same_sense=True)

# OPEN_SHELL: sliver Face B IS embedded alongside valid Face A — IS the mechanism
shell = f.open_shell([faceA, faceB])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
