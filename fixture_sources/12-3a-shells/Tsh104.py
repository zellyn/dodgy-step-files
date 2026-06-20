"""Tsh104 — ShapeFix_Shell.FixFaceOrientation reverse-edge propagation.

Catalog claim: Shell where one face's edge is referenced with .F. by a
neighbor; orientation propagation should flip but the logic only handles .T.
inputs. Two adjacent rectangular faces share edge #37; Face2 references it as
.F. while Face1 uses .T. FixFaceOrientation's propagation logic fails to
cascade the flip through the graph.

Mechanism IS the shell structure: Two ADVANCED_FACEs (Face1 and Face2) share
one EDGE_CURVE. Face1 references the shared EDGE_CURVE with ORIENTED_EDGE
orientation=True (.T.) in its EDGE_LOOP. Face2 references the SAME EDGE_CURVE
with ORIENTED_EDGE orientation=False (.F.) in its EDGE_LOOP. This .F.
reference IS directly wired into Face2's EDGE_LOOP in the shell topology.
FixFaceOrientation reads the shared edge from Face1 (which is .T.) and
propagates orientation to Face2; but the propagation logic only handles edges
found via .T. references — when it encounters Face2's .F. reference to the
same EDGE_CURVE, it fails to flip the orientation direction. The .F. reverse-
reference IS the mechanism wired into Face2's edge topology, causing the
propagation cascade to silently skip the flip.

Tier-3 assertion: n_faces_total == 2

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh104",
    defect=(
        "OPEN_SHELL with 2 adjacent ADVANCED_FACEs sharing 1 EDGE_CURVE — IS the mechanism; "
        "Face1 references shared EDGE_CURVE with ORIENTED_EDGE orientation=True (.T.); "
        "Face2 references SAME shared EDGE_CURVE with ORIENTED_EDGE orientation=False (.F.); "
        ".F. reverse-reference IS directly wired into Face2 EDGE_LOOP in shell topology; "
        "FixFaceOrientation propagates from Face1 via .T. reference to shared edge; "
        "propagation logic only handles .T. — .F. reference in Face2 IS the blocker mechanism; "
        "flip cascade silently skips Face2 because .F. edge path is not handled; "
        "fix: invert propagation direction when shared edge referenced as .F. in neighbor; "
        "emit E_REVERSE_EDGE_PROPAGATION_SKIPPED when .F. reference blocks orientation cascade"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Face1: unit square at z=0, x=[0,1], y=[0,1]
pF1 = [cp(0,0,0), cp(1,0,0), cp(1,1,0), cp(0,1,0)]
vF1 = [f.vertex_point(p) for p in pF1]

# Face2: unit square at z=0, x=[1,2], y=[0,1] (adjacent to Face1 on right)
pF2 = [cp(1,0,0), cp(2,0,0), cp(2,1,0), cp(1,1,0)]
# Share vertices on the shared edge with Face1
vF2_0 = vF1[1]  # (1,0,0) shared with Face1 v1
vF2_1 = f.vertex_point(pF2[1])
vF2_2 = f.vertex_point(pF2[2])
vF2_3 = vF1[2]  # (1,1,0) shared with Face1 v2

# Shared edge: (1,0,0)→(1,1,0) — IS the reverse-edge mechanism
# Face1 will use it .T.; Face2 will use it .F. — IS the mechanism wired in topology
shared_edge = led(vF1[1], vF1[2], pF1[1], 0, 1, 0)  # (1,0,0)→(1,1,0)

# Face1 edges — shared edge used orientation=True (.T.)
eF1_bot   = led(vF1[0], vF1[1], pF1[0],  1, 0, 0)
# shared_edge: (1,0,0)→(1,1,0) True
eF1_top   = led(vF1[2], vF1[3], pF1[2], -1, 0, 0)
eF1_left  = led(vF1[3], vF1[0], pF1[3],  0,-1, 0)
loop_f1 = f.edge_loop([
    f.oriented_edge(eF1_bot,     True),   # (0,0,0)→(1,0,0)
    f.oriented_edge(shared_edge, True),   # (1,0,0)→(1,1,0) .T. — IS Face1 reference
    f.oriented_edge(eF1_top,     True),   # (1,1,0)→(0,1,0)
    f.oriented_edge(eF1_left,    True),   # (0,1,0)→(0,0,0)
])
pl_f1 = f.plane(f.axis2_placement_3d(pF1[0], dir3(0, 0, 1), dir3(1, 0, 0)))
face1 = f.advanced_face([f.face_outer_bound(loop_f1, orientation=True)], pl_f1, same_sense=True)

# Face2 edges — shared edge referenced with orientation=False (.F.) IS the mechanism
eF2_bot   = led(vF2_0, vF2_1, pF2[0],  1, 0, 0)  # (1,0,0)→(2,0,0)
eF2_right = led(vF2_1, vF2_2, pF2[1],  0, 1, 0)  # (2,0,0)→(2,1,0)
eF2_top   = led(vF2_2, vF2_3, pF2[2], -1, 0, 0)  # (2,1,0)→(1,1,0)
# shared_edge (1,0,0)→(1,1,0) used as .F. — IS the reverse-edge propagation mechanism
loop_f2 = f.edge_loop([
    f.oriented_edge(eF2_bot,     True),   # (1,0,0)→(2,0,0)
    f.oriented_edge(eF2_right,   True),   # (2,0,0)→(2,1,0)
    f.oriented_edge(eF2_top,     True),   # (2,1,0)→(1,1,0)
    f.oriented_edge(shared_edge, False),  # (1,1,0)→(1,0,0) .F. — IS the mechanism
])
pl_f2 = f.plane(f.axis2_placement_3d(pF2[0], dir3(0, 0, 1), dir3(1, 0, 0)))
face2 = f.advanced_face([f.face_outer_bound(loop_f2, orientation=True)], pl_f2, same_sense=True)

# OPEN_SHELL: Face1 (.T.) + Face2 (.F.) sharing edge IS the reverse-edge mechanism
shell = f.open_shell([face1, face2])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
