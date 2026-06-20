"""Tsh095 — ShapeUpgrade_ShellSewing.ApplySewing self-intersecting shell.

Catalog claim: Shell with two faces that intersect each other (T-intersection
or X-crossing). Face A spans (0..4 x 0..4 x 0), Face B spans (2..2.5 x -1..5 x 0).
Their edges cross geometrically; ApplySewing must detect and reject but proceeds
without error.

Mechanism IS the shell structure: Face A IS a 4x4 quad at z=0. Face B IS a
0.5-wide strip that spans x=2..2.5, y=-1..5, also at z=0. Face B's boundary
physically crosses Face A's interior — the edge at x=2, y=-1..0 passes through
Face A's plane before reaching Face A's boundary. This geometric crossing IS
directly embedded in the ADVANCED_FACE extents: Face B's VERTEX_POINTs at y=-1
lie outside Face A, while its y=0..4 strip overlaps Face A's area. The
overlapping faces sharing the same z=0 PLANE IS the self-intersection mechanism
wired into the shell topology. ApplySewing proceeds without rejecting the
self-intersecting arrangement.

Tier-3 assertion: n_faces_total == 2

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh095",
    defect=(
        "OPEN_SHELL with 2 ADVANCED_FACEs that geometrically intersect at z=0 — IS the self-intersection mechanism; "
        "Face A IS 4x4 quad: x=0..4 y=0..4 z=0 wired into EDGE_LOOP with 4 EDGE_CURVEs; "
        "Face B IS 0.5-wide strip: x=2..2.5 y=-1..5 z=0 wired into EDGE_LOOP with 4 EDGE_CURVEs; "
        "Face B boundary crosses Face A interior — geometric crossing IS directly in VERTEX_POINT extents; "
        "both faces on identical z=0 PLANE — coplanar overlap IS the mechanism wired into face topology; "
        "ApplySewing does not detect self-intersection; proceeds and produces malformed topology; "
        "fix: check for face-face geometric intersection before sewing; reject or report; "
        "emit E_SHELL_SELF_INTERSECTING_FACES when coplanar face overlap detected"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Face A: 4x4 quad at z=0 (x=0..4, y=0..4)
pA = [cp(0,0,0), cp(4,0,0), cp(4,4,0), cp(0,4,0)]
vA = [f.vertex_point(p) for p in pA]
eA = [
    led(vA[0], vA[1], pA[0],  1, 0, 0),
    led(vA[1], vA[2], pA[1],  0, 1, 0),
    led(vA[2], vA[3], pA[2], -1, 0, 0),
    led(vA[3], vA[0], pA[3],  0,-1, 0),
]
loop_a = f.edge_loop([f.oriented_edge(e, True) for e in eA])
pl_a = f.plane(f.axis2_placement_3d(pA[0], dir3(0, 0, 1), dir3(1, 0, 0)))
# Face A wired with EDGE_LOOP IS the large face spanning the intersection zone
face_a = f.advanced_face([f.face_outer_bound(loop_a, orientation=True)], pl_a, same_sense=True)

# Face B: 0.5-wide strip at z=0 (x=2..2.5, y=-1..5) — crosses Face A's interior
# y=-1..5 means it extends beyond Face A's boundary (y=0..4) in both directions
pB = [cp(2,-1,0), cp(2.5,-1,0), cp(2.5,5,0), cp(2,5,0)]
vB = [f.vertex_point(p) for p in pB]
eB = [
    led(vB[0], vB[1], pB[0],  1, 0, 0),
    led(vB[1], vB[2], pB[1],  0, 1, 0),
    led(vB[2], vB[3], pB[2], -1, 0, 0),
    led(vB[3], vB[0], pB[3],  0,-1, 0),
]
loop_b = f.edge_loop([f.oriented_edge(e, True) for e in eB])
pl_b = f.plane(f.axis2_placement_3d(pB[0], dir3(0, 0, 1), dir3(1, 0, 0)))
# Face B crossing Face A IS the self-intersection mechanism wired into shell topology
face_b = f.advanced_face([f.face_outer_bound(loop_b, orientation=True)], pl_b, same_sense=True)

# OPEN_SHELL with crossing faces — IS the self-intersecting shell mechanism
shell = f.open_shell([face_a, face_b])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
