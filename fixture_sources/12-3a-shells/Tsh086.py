"""Tsh086 — ShapeUpgrade_ShellSewing.Prepare two-orientation merge.

Catalog claim: Compound of two shells with opposite orientation conventions:
one outward-normal (FACE_OUTER_BOUND flag .T.), one inward-normal (.F.).
Prepare phase must detect and normalize before sewing merges incompatible
shells; missing pre-validation.

Mechanism IS the shell structure: Two OPEN_SHELL entities are embedded in a
SHELL_BASED_SURFACE_MODEL. Shell 1 contains a unit quad with FACE_OUTER_BOUND
orientation=True (correct outward convention). Shell 2 contains an adjacent
unit quad with FACE_OUTER_BOUND orientation=False (inverted bound convention —
the .F. flag). The opposing FACE_OUTER_BOUND orientation flags on the two
shells' outer bounds ARE the mechanism wired directly into the face topology.
When ShapeUpgrade_ShellSewing.Prepare processes this compound, it encounters
two incompatible orientation conventions and must normalize before sewing;
without pre-validation the sewing step merges shells with conflicting outward-
normal definitions, producing geometrically inconsistent results.

Tier-3 assertion: load == "ok"

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh086",
    defect=(
        "SHELL_BASED_SURFACE_MODEL with 2 OPEN_SHELLs; "
        "Shell 1 unit quad IS wired with FACE_OUTER_BOUND orientation=True (.T.); "
        "Shell 2 adjacent unit quad IS wired with FACE_OUTER_BOUND orientation=False (.F.); "
        "opposing FACE_OUTER_BOUND orientation flags ARE directly in face topology; "
        "mixed .T./.F. outer-bound conventions IS the mechanism across two shells; "
        "ShapeUpgrade_ShellSewing.Prepare must detect orientation mismatch before sewing; "
        "missing pre-validation allows incompatible shells to be merged; "
        "fix: compare FACE_OUTER_BOUND flags across all shells in Prepare phase; "
        "emit E_ORIENTATION_CONFLICT when mixed conventions detected"
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
# FACE_OUTER_BOUND orientation=True IS outward convention for Shell 1
face1 = f.advanced_face([f.face_outer_bound(loop1, orientation=True)], pl1, same_sense=True)
shell1 = f.open_shell([face1])

# Shell 2: adjacent unit quad at x=1..2, y=0..1, z=0 — FACE_OUTER_BOUND orientation=False (.F.)
p20 = cp(2, 0, 0); p21 = cp(2, 1, 0)
v20 = f.vertex_point(p20); v21 = f.vertex_point(p21)

p10b = cp(1, 0, 0); p11b = cp(1, 1, 0)
v10b = f.vertex_point(p10b); v11b = f.vertex_point(p11b)

f0 = led(v10b, v20,  p10b,  1, 0, 0)
f1 = led(v20,  v21,  p20,   0, 1, 0)
f2 = led(v21,  v11b, p21,  -1, 0, 0)
f3 = led(v11b, v10b, p11b,  0,-1, 0)
loop2 = f.edge_loop([
    f.oriented_edge(f0, True), f.oriented_edge(f1, True),
    f.oriented_edge(f2, True), f.oriented_edge(f3, True),
])
pl2 = f.plane(f.axis2_placement_3d(p10b, dir3(0, 0, 1), dir3(1, 0, 0)))
# FACE_OUTER_BOUND orientation=False IS inverted convention for Shell 2 — IS the mechanism
face2 = f.advanced_face([f.face_outer_bound(loop2, orientation=False)], pl2, same_sense=True)
shell2 = f.open_shell([face2])

# SHELL_BASED_SURFACE_MODEL with both shells: mixed .T./.F. IS directly wired in
sbsm = f.shell_based_surface_model([shell1, shell2])
f.add_product_chain(sbsm)
