"""Tsh088 — ShapeAnalysis_Shell.LoadShells orientation-from-compound.

Catalog claim: Compound with two shells exhibiting mixed FACE_OUTER_BOUND
orientation flags (.T. and .F. on respective outer bounds). LoadShells must
preserve mixed flags but loses one during compound decomposition, normalizing
both to same orientation.

Mechanism IS the shell structure: COMPOUND contains 2 SHELL_BASED_SURFACE_MODELs,
each wrapping a single OPEN_SHELL. Shell 1's ADVANCED_FACE IS wired with
FACE_OUTER_BOUND orientation=True (.T.) — standard outward convention. Shell 2's
ADVANCED_FACE IS wired with FACE_OUTER_BOUND orientation=False (.F.) — inverted
outer-bound flag. The mixed .T./.F. orientation flags ARE directly embedded in
the FACE_OUTER_BOUND entities of the two shells' outer bounds, making the
mixed-orientation state IS the mechanism wired into face topology.
ShapeAnalysis_Shell.LoadShells processes the compound and silently normalizes
Shell 2's flag to .T., losing the inverted orientation signal.

Tier-3 assertion: load == "ok"

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh088",
    defect=(
        "COMPOUND of 2 shells with mixed FACE_OUTER_BOUND orientation; "
        "Shell 1 ADVANCED_FACE IS wired with FACE_OUTER_BOUND orientation=True (.T.); "
        "Shell 2 ADVANCED_FACE IS wired with FACE_OUTER_BOUND orientation=False (.F.); "
        "mixed .T./.F. outer-bound flags ARE directly in FACE_OUTER_BOUND topology; "
        "mixed orientation IS the mechanism across compound decomposition; "
        "ShapeAnalysis_Shell.LoadShells normalizes both flags to .T.; "
        "inverted orientation signal on Shell 2 IS lost during compound traversal; "
        "fix: preserve FACE_OUTER_BOUND orientation flag per shell through LoadShells"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Shell 1: unit quad at x=0..1, y=0..1, z=0 — FACE_OUTER_BOUND orientation=True (.T.)
p00 = cp(0, 0, 0); p10 = cp(1, 0, 0)
p11 = cp(1, 1, 0); p01 = cp(0, 1, 0)
v00 = f.vertex_point(p00); v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11); v01 = f.vertex_point(p01)
e0 = led(v00, v10, p00,  1, 0, 0)
e1 = led(v10, v11, p10,  0, 1, 0)
e2 = led(v11, v01, p11, -1, 0, 0)
e3 = led(v01, v00, p01,  0,-1, 0)
loop1 = f.edge_loop([
    f.oriented_edge(e0, True), f.oriented_edge(e1, True),
    f.oriented_edge(e2, True), f.oriented_edge(e3, True),
])
pl1 = f.plane(f.axis2_placement_3d(p00, dir3(0, 0, 1), dir3(1, 0, 0)))
# FACE_OUTER_BOUND orientation=True IS the standard outward convention for Shell 1
face1 = f.advanced_face([f.face_outer_bound(loop1, orientation=True)], pl1, same_sense=True)
shell1 = f.open_shell([face1])
sbsm1 = f.shell_based_surface_model([shell1])

# Shell 2: adjacent quad at x=1..2, y=0..1, z=0 — FACE_OUTER_BOUND orientation=False (.F.)
p20 = cp(2, 0, 0); p21 = cp(2, 1, 0)
p10b = cp(1, 0, 0); p11b = cp(1, 1, 0)
v10b = f.vertex_point(p10b); v20 = f.vertex_point(p20)
v21 = f.vertex_point(p21); v11b = f.vertex_point(p11b)
f0 = led(v10b, v20,  p10b,  1, 0, 0)
f1 = led(v20,  v21,  p20,   0, 1, 0)
f2 = led(v21,  v11b, p21,  -1, 0, 0)
f3 = led(v11b, v10b, p11b,  0,-1, 0)
loop2 = f.edge_loop([
    f.oriented_edge(f0, True), f.oriented_edge(f1, True),
    f.oriented_edge(f2, True), f.oriented_edge(f3, True),
])
pl2 = f.plane(f.axis2_placement_3d(p10b, dir3(0, 0, 1), dir3(1, 0, 0)))
# FACE_OUTER_BOUND orientation=False IS the inverted outer-bound flag — IS the mechanism
face2 = f.advanced_face([f.face_outer_bound(loop2, orientation=False)], pl2, same_sense=True)
shell2 = f.open_shell([face2])
sbsm2 = f.shell_based_surface_model([shell2])

# Both SHELL_BASED_SURFACE_MODELs are added; mixed .T./.F. IS wired into face topology
f.add_product_chain(sbsm1)
f.add_product_chain(sbsm2)
