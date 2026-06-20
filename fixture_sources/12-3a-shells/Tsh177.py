"""Tsh177 — ShapeFix_Shell.Perform infinite-loop-detection.

Catalog claim: Shell whose fix repeatedly invalidates a previous fix; Perform
should detect loop but uses simple counter that fires too late.

Mechanism IS the shell structure: TWO ADVANCED_FACEs sharing the SAME
TRIANGULAR EDGE_LOOP with OPPOSITE same_sense values are wired into an
OPEN_SHELL. face_fwd uses the three shared EDGE_CURVEs in forward
orientation (same_sense=True, normal +Z); face_rev uses the SAME three
EDGE_CURVEs reversed (same_sense=False, normal -Z). Both faces ARE wired
into the same OPEN_SHELL using the SAME edge entities — e_ab, e_bc, e_ca IS
each shared. The fix oscillation IS triggered by the conflicting same_sense:
fixing face_fwd's orientation makes face_rev invalid; fixing face_rev makes
face_fwd invalid again. Perform's counter-based loop detection exhausts its
iteration limit before achieving stabilization. The shared triangular edge
loop IS the minimal structure that creates fix oscillation.

Tier-3 assertion: n_faces_total == 2

live oracle: occt=shape(1)/shape(1) gmsh=shape(8) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh177",
    defect=(
        "TWO ADVANCED_FACEs sharing SAME TRIANGULAR EDGE_CURVEs with OPPOSITE same_sense — "
        "IS the infinite-loop-detection mechanism; "
        "e_ab IS EDGE_CURVE from (0,0,0) to (1,0,0) — shared by both faces; "
        "e_bc IS EDGE_CURVE from (1,0,0) to (0.5,1,0) — shared by both faces; "
        "e_ca IS EDGE_CURVE from (0.5,1,0) to (0,0,0) — shared by both faces; "
        "face_fwd IS wired with loop_fwd (e_ab .T., e_bc .T., e_ca .T.) same_sense=True — normal +Z; "
        "face_rev IS wired with loop_rev (e_ab .F., e_bc .F., e_ca .F.) same_sense=False — normal -Z; "
        "both ADVANCED_FACEs reference THE SAME EDGE_CURVE entities — IS the shared loop; "
        "fixing face_fwd orientation invalidates face_rev — IS the first oscillation step; "
        "fixing face_rev re-invalidates face_fwd — IS the second oscillation step; "
        "Perform counter-based loop detection exhausts limit before convergence — IS the defect; "
        "fix: detect conflicting same_sense on shared edges before fix loop; "
        "emit E_PERFORM_LOOP_DETECTED when counter exceeds threshold without convergence"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Shared triangle vertices
pa = cp(0,   0, 0)
pb = cp(1,   0, 0)
pc = cp(0.5, 1, 0)
va = f.vertex_point(pa)
vb = f.vertex_point(pb)
vc = f.vertex_point(pc)

# THREE shared EDGE_CURVEs — IS the shared triangular edge loop
e_ab = led(va, vb, pa,  1, 0, 0)            # (0,0,0)→(1,0,0)
e_bc = led(vb, vc, pb, -0.5, 1, 0)          # (1,0,0)→(0.5,1,0)
e_ca = led(vc, va, pc, -0.5, -1, 0)         # (0.5,1,0)→(0,0,0)

# face_fwd: triangle traversed forward — same_sense=True, normal +Z
# CCW viewed from +Z: a→b→c→a
loop_fwd = f.edge_loop([
    f.oriented_edge(e_ab, True),    # (0,0,0)→(1,0,0)
    f.oriented_edge(e_bc, True),    # (1,0,0)→(0.5,1,0)
    f.oriented_edge(e_ca, True),    # (0.5,1,0)→(0,0,0)
])
plane_fwd = f.plane(f.axis2_placement_3d(pa, dir3(0, 0, 1), dir3(1, 0, 0)))
face_fwd = f.advanced_face([f.face_outer_bound(loop_fwd, orientation=True)], plane_fwd, same_sense=True)

# face_rev: SAME triangle traversed reversed — same_sense=False, normal -Z
# Uses identical e_ab, e_bc, e_ca in reverse — IS the oscillation trigger
loop_rev = f.edge_loop([
    f.oriented_edge(e_ca, False),   # reversed: (0,0,0)→(0.5,1,0)
    f.oriented_edge(e_bc, False),   # reversed: (0.5,1,0)→(1,0,0)
    f.oriented_edge(e_ab, False),   # reversed: (1,0,0)→(0,0,0)
])
# same plane — same_sense=False gives normal -Z — conflicting with face_fwd
plane_rev = f.plane(f.axis2_placement_3d(pa, dir3(0, 0, 1), dir3(1, 0, 0)))
face_rev = f.advanced_face([f.face_outer_bound(loop_rev, orientation=True)], plane_rev, same_sense=False)

# OPEN_SHELL: two faces sharing same triangular EDGE_CURVEs with opposite same_sense
# IS the oscillation mechanism — Perform loop detection fires too late
shell = f.open_shell([face_fwd, face_rev])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
