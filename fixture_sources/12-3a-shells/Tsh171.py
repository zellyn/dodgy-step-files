"""Tsh171 — ShapeUpgrade_ShellSewing.Apply with-cross-shell-intersection.

Catalog claim: Two distinct shells geometrically overlapping. Apply() ignores
intersection; merged shell contains self-intersecting face topology.

Mechanism IS the shell structure: TWO ADVANCED_FACEs each in their OWN
OPEN_SHELL, both wired into a SHELL_BASED_SURFACE_MODEL — shell_a IS a unit
square on Z=0 (x=[0,1], y=[0,1]) and shell_b IS a quarter-offset square on
Z=0 (x=[0.5,1.5], y=[0.5,1.5]) that geometrically overlaps shell_a. Both
shells ARE wired separately as OPEN_SHELLs and assembled in one
SHELL_BASED_SURFACE_MODEL. The geometric overlap IS the cross-shell
intersection: the region x=[0.5,1], y=[0.5,1] IS inside both face boundaries
simultaneously. Apply() performs sewing based on edge proximity; the two
faces have no close edges, so no sewing occurs; output retains both faces
with overlapping interiors — IS the self-intersecting topology defect.

Tier-3 assertion: n_faces_total == 2

live oracle: occt=shape(1)/shape(1) gmsh=shape(18) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh171",
    defect=(
        "TWO ADVANCED_FACEs in TWO OPEN_SHELLs in SHELL_BASED_SURFACE_MODEL — IS the cross-shell mechanism; "
        "face_a IS a unit square x=[0,1] y=[0,1] on Z=0 — wired into shell_a OPEN_SHELL; "
        "face_b IS a quarter-offset square x=[0.5,1.5] y=[0.5,1.5] on Z=0 — wired into shell_b OPEN_SHELL; "
        "geometric overlap region x=[0.5,1] y=[0.5,1] IS the cross-shell intersection zone; "
        "shell_a and shell_b have NO shared edges — IS the sewing-trigger absence; "
        "SHELL_BASED_SURFACE_MODEL([shell_a, shell_b]) IS what Apply() receives as compound input; "
        "Apply() sews by edge proximity; no edges are close — no sewing occurs; "
        "output retains both faces with overlapping interiors — IS self-intersecting topology; "
        "cross-shell interior intersection IS not detected by Apply(); "
        "fix: check face interior intersection in addition to edge proximity; "
        "emit E_SEWING_CROSS_SHELL_INTERSECTION when face interiors overlap in output"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# face_a: unit square x=[0,1] y=[0,1] z=0 — IS face of shell_a
pa00 = cp(0, 0, 0); pa10 = cp(1, 0, 0); pa11 = cp(1, 1, 0); pa01 = cp(0, 1, 0)
va00 = f.vertex_point(pa00); va10 = f.vertex_point(pa10)
va11 = f.vertex_point(pa11); va01 = f.vertex_point(pa01)
ea_bot   = led(va00, va10, pa00,  1, 0, 0)
ea_right = led(va10, va11, pa10,  0, 1, 0)
ea_top   = led(va01, va11, pa01,  1, 0, 0)
ea_left  = led(va00, va01, pa00,  0, 1, 0)
loop_a = f.edge_loop([
    f.oriented_edge(ea_bot,   True),
    f.oriented_edge(ea_right, True),
    f.oriented_edge(ea_top,   False),
    f.oriented_edge(ea_left,  False),
])
plane_a = f.plane(f.axis2_placement_3d(pa00, dir3(0, 0, 1), dir3(1, 0, 0)))
face_a = f.advanced_face([f.face_outer_bound(loop_a, orientation=True)], plane_a, same_sense=True)

# shell_a: OPEN_SHELL containing only face_a — IS one of the two distinct shells
shell_a = f.open_shell([face_a])

# face_b: offset square x=[0.5,1.5] y=[0.5,1.5] z=0 — overlaps face_a in [0.5,1]x[0.5,1]
pb00 = cp(0.5, 0.5, 0); pb10 = cp(1.5, 0.5, 0); pb11 = cp(1.5, 1.5, 0); pb01 = cp(0.5, 1.5, 0)
vb00 = f.vertex_point(pb00); vb10 = f.vertex_point(pb10)
vb11 = f.vertex_point(pb11); vb01 = f.vertex_point(pb01)
eb_bot   = led(vb00, vb10, pb00,  1, 0, 0)
eb_right = led(vb10, vb11, pb10,  0, 1, 0)
eb_top   = led(vb01, vb11, pb01,  1, 0, 0)
eb_left  = led(vb00, vb01, pb00,  0, 1, 0)
loop_b = f.edge_loop([
    f.oriented_edge(eb_bot,   True),
    f.oriented_edge(eb_right, True),
    f.oriented_edge(eb_top,   False),
    f.oriented_edge(eb_left,  False),
])
plane_b = f.plane(f.axis2_placement_3d(pb00, dir3(0, 0, 1), dir3(1, 0, 0)))
face_b = f.advanced_face([f.face_outer_bound(loop_b, orientation=True)], plane_b, same_sense=True)

# shell_b: OPEN_SHELL containing only face_b — IS the second distinct overlapping shell
shell_b = f.open_shell([face_b])

# SHELL_BASED_SURFACE_MODEL with two shells — IS the compound that Apply() receives
# shell_a and shell_b have no shared edges; their face interiors overlap — IS the defect
sbsm = f.shell_based_surface_model([shell_a, shell_b])
f.add_product_chain(sbsm)
