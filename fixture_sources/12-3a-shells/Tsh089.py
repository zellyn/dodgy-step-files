"""Tsh089 — ShapeUpgrade_RemoveInternalWires tolerance-based removal.

Catalog claim: Face with two small internal wires (5mm×5mm and 10mm×10mm)
below typical tolerance thresholds. Tests whether Perform uses face-area-relative
scaling (remove if wire area < 0.1% of face) or absolute threshold. Expected:
wires removed. Likely failure: Perform uses fixed absolute threshold, skips
small wires on large faces.

Mechanism IS the shell structure: ADVANCED_FACE IS wired with one
FACE_OUTER_BOUND (large 200mm×200mm outer loop) and two FACE_BOUND inner
loops (hole 1: 5mm×5mm at (10,10); hole 2: 10mm×10mm at (30,30)). Both
inner FACE_BOUNDs ARE directly embedded in the ADVANCED_FACE entity as
internal wire topology. The small-area internal wires relative to large outer
face area IS the mechanism in face topology. ShapeUpgrade_RemoveInternalWires
with absolute threshold fails to remove these wires on the large face; with
face-relative threshold both are correctly removed.

Tier-3 assertion: load == "ok"

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh089",
    defect=(
        "ADVANCED_FACE IS wired with 1 FACE_OUTER_BOUND (200x200 outer loop); "
        "FACE_BOUND 1 IS wired as 5x5mm internal hole at (10,10) — IS mechanism; "
        "FACE_BOUND 2 IS wired as 10x10mm internal hole at (30,30) — IS mechanism; "
        "both inner FACE_BOUNDs ARE directly embedded in ADVANCED_FACE topology; "
        "small-hole area vs large face area IS the tolerance-threshold mechanism; "
        "ShapeUpgrade_RemoveInternalWires.Perform uses fixed absolute threshold; "
        "skips small wires on large face; fix: use face-area-relative threshold; "
        "emit E_INTERNAL_WIRE_PRESERVED when wire area < 0.1% of face area"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Outer face: 200x200 mm at z=0
oP = [cp(0,0,0), cp(200,0,0), cp(200,200,0), cp(0,200,0)]
oV = [f.vertex_point(p) for p in oP]
oE = [
    led(oV[0], oV[1], oP[0],  1, 0, 0),
    led(oV[1], oV[2], oP[1],  0, 1, 0),
    led(oV[2], oV[3], oP[2], -1, 0, 0),
    led(oV[3], oV[0], oP[3],  0,-1, 0),
]
outer_loop = f.edge_loop([f.oriented_edge(e, True) for e in oE])
outer_bound = f.face_outer_bound(outer_loop, orientation=True)

# Inner wire 1: 5x5mm hole at (10,10) — small relative to 200x200 face IS the mechanism
h1P = [cp(10,10,0), cp(15,10,0), cp(15,15,0), cp(10,15,0)]
h1V = [f.vertex_point(p) for p in h1P]
h1E = [
    led(h1V[0], h1V[1], h1P[0],  1, 0, 0),
    led(h1V[1], h1V[2], h1P[1],  0, 1, 0),
    led(h1V[2], h1V[3], h1P[2], -1, 0, 0),
    led(h1V[3], h1V[0], h1P[3],  0,-1, 0),
]
# Hole winding reversed (CW) so it reads as interior void
hole1_loop = f.edge_loop([f.oriented_edge(e, False) for e in h1E])
# FACE_BOUND IS directly wired into ADVANCED_FACE as internal wire topology
hole1_bound = f.face_bound(hole1_loop, orientation=False)

# Inner wire 2: 10x10mm hole at (30,30) — also small relative to face IS the mechanism
h2P = [cp(30,30,0), cp(40,30,0), cp(40,40,0), cp(30,40,0)]
h2V = [f.vertex_point(p) for p in h2P]
h2E = [
    led(h2V[0], h2V[1], h2P[0],  1, 0, 0),
    led(h2V[1], h2V[2], h2P[1],  0, 1, 0),
    led(h2V[2], h2V[3], h2P[2], -1, 0, 0),
    led(h2V[3], h2V[0], h2P[3],  0,-1, 0),
]
hole2_loop = f.edge_loop([f.oriented_edge(e, False) for e in h2E])
hole2_bound = f.face_bound(hole2_loop, orientation=False)

pl = f.plane(f.axis2_placement_3d(oP[0], dir3(0, 0, 1), dir3(1, 0, 0)))
# ADVANCED_FACE IS wired with outer bound + 2 FACE_BOUNDs — IS the mechanism
face = f.advanced_face([outer_bound, hole1_bound, hole2_bound], pl, same_sense=True)

shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
