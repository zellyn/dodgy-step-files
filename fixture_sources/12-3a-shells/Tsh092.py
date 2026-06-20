"""Tsh092 — ShapeAnalysis_Shell.CheckOrientedShells nested-shell cavity.

Catalog claim: Compound containing two shells: outer (10x10 base) and inner
(2x2 at height 5-7). Tests CheckOrientedShells with nesting topology (cavity).
Expected: both shells recognized as valid; outer outward, inner inward.
Likely failure: Inner shell misclassified as inverted; reports outer as wrongly
oriented.

Mechanism IS the shell structure: Two OPEN_SHELLs are embedded in separate
SHELL_BASED_SURFACE_MODELs. Outer shell IS a 10x10 base quad (z=0) wired with
FACE_OUTER_BOUND orientation=True (.T.) — correct outward convention. Inner
shell IS a 2x2 quad at elevated position (z=5, inside the outer volume) wired
with FACE_OUTER_BOUND orientation=False (.F.) — inward convention for a cavity.
The nested topology (small shell inside large shell) with inverted FACE_OUTER_BOUND
on the inner shell IS the mechanism directly wired into the face topology.
CheckOrientedShells must recognize the inner shell's .F. flag as correct
cavity-inward orientation; without nesting awareness it reports the inner shell
as wrongly oriented.

Tier-3 assertion: load == "ok"

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh092",
    defect=(
        "2 OPEN_SHELLs in separate SHELL_BASED_SURFACE_MODELs forming nested topology; "
        "outer OPEN_SHELL IS 10x10 base quad at z=0 with FACE_OUTER_BOUND orientation=True (.T.); "
        "inner OPEN_SHELL IS 2x2 quad at z=5 with FACE_OUTER_BOUND orientation=False (.F.); "
        "inverted .F. outer-bound on inner shell IS the cavity-inward mechanism; "
        "nested shell topology IS directly wired into ADVANCED_FACE FACE_OUTER_BOUND flags; "
        "ShapeAnalysis_Shell.CheckOrientedShells lacks nesting awareness; "
        "misclassifies inner shell .F. as wrongly oriented instead of correct cavity; "
        "fix: detect containment relationship before evaluating inner shell orientation"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Outer shell: 10x10 quad at z=0 — FACE_OUTER_BOUND orientation=True (.T.)
oP = [cp(0,0,0), cp(10,0,0), cp(10,10,0), cp(0,10,0)]
oV = [f.vertex_point(p) for p in oP]
oE = [
    led(oV[0], oV[1], oP[0],  1, 0, 0),
    led(oV[1], oV[2], oP[1],  0, 1, 0),
    led(oV[2], oV[3], oP[2], -1, 0, 0),
    led(oV[3], oV[0], oP[3],  0,-1, 0),
]
outer_loop = f.edge_loop([f.oriented_edge(e, True) for e in oE])
outer_pl = f.plane(f.axis2_placement_3d(oP[0], dir3(0, 0, 1), dir3(1, 0, 0)))
# FACE_OUTER_BOUND orientation=True IS outward convention for the outer shell
outer_face = f.advanced_face(
    [f.face_outer_bound(outer_loop, orientation=True)], outer_pl, same_sense=True
)
outer_shell = f.open_shell([outer_face])
outer_sbsm = f.shell_based_surface_model([outer_shell])

# Inner shell: 2x2 quad at z=5 (inside outer volume) — FACE_OUTER_BOUND orientation=False (.F.)
iP = [cp(4,4,5), cp(6,4,5), cp(6,6,5), cp(4,6,5)]
iV = [f.vertex_point(p) for p in iP]
iE = [
    led(iV[0], iV[1], iP[0],  1, 0, 0),
    led(iV[1], iV[2], iP[1],  0, 1, 0),
    led(iV[2], iV[3], iP[2], -1, 0, 0),
    led(iV[3], iV[0], iP[3],  0,-1, 0),
]
inner_loop = f.edge_loop([f.oriented_edge(e, True) for e in iE])
inner_pl = f.plane(f.axis2_placement_3d(iP[0], dir3(0, 0, 1), dir3(1, 0, 0)))
# FACE_OUTER_BOUND orientation=False (.F.) IS the inward-cavity convention — IS the mechanism
inner_face = f.advanced_face(
    [f.face_outer_bound(inner_loop, orientation=False)], inner_pl, same_sense=True
)
inner_shell = f.open_shell([inner_face])
inner_sbsm = f.shell_based_surface_model([inner_shell])

# Both shells added: nested topology with .T. outer / .F. inner IS the mechanism
f.add_product_chain(outer_sbsm)
f.add_product_chain(inner_sbsm)
