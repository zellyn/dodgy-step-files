"""N148 — EvaluateDistances.projection_direction_selection.

Curve-length comparison fails at parity (5.0 vs 4.9): backwards projection
direction selected, reporting distance to far branch. True separation 0.1
masked when lengths nearly equal.

Mechanism IS wired into 2 real ADVANCED_FACEs (not a faceless
GEOMETRIC_CURVE_SET): Face1 (x=[0,5], y=[-1,0]) has free top edge eA_5mm
(length 5.0) at y=0; Face2 (x=[0,4.9], y=[0.1,1.1]) has free bottom edge
eB_4p9mm (length 4.9) at y=0.1. The near-parity lengths (5.0 vs 4.9) and
the genuine 0.1mm gap between the two real face boundaries is exactly the
near-parity input that flips EvaluateDistances's projection-direction
selection.

Fixture kind: scaffold (kernel-test-pair) -- the STEP file provides the
genuine near-parity-length candidate-edge-pair-on-real-faces setup; the
projection-direction bug fires when EvaluateDistances is invoked at
runtime.

Tier-3: n_faces_total == 2
Expected: occt=shape(1)/shape(1) gmsh=shape(18) ifc=schema_n/a  [NEEDS-ORACLE-REFRESH]
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N148",
    defect=(
        "EvaluateDistances projection_direction: two ADVANCED_FACEs whose "
        "facing free edges (eA_5mm length 5.0, eB_4p9mm length 4.9) are "
        "0.1mm apart; near-parity lengths trigger backwards projection "
        "direction selection on real face boundaries"
    ),
)


def cp(x, y, z):
    return f.cartesian_point((float(x), float(y), float(z)))


def dir3(x, y, z):
    return f.direction((float(x), float(y), float(z)))


def led(va, vb, pt, dx, dy, dz, length):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, length)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)


def mk_plane_z0():
    orig = cp(0, 0, 0)
    return f.plane(f.axis2_placement_3d(orig, dir3(0, 0, 1), dir3(1, 0, 0)))


def face4(edges_with_ori, plane):
    loop = f.edge_loop([f.oriented_edge(e, o) for e, o in edges_with_ori])
    return f.advanced_face([f.face_outer_bound(loop, orientation=True)], plane, same_sense=True)


# Face1: x=[0,5], y=[-1,0] -- top edge at y=0, length 5.0, IS eA_5mm.
p00 = cp(0, -1, 0)
p10 = cp(5, -1, 0)
p11 = cp(5, 0, 0)
p01 = cp(0, 0, 0)
v00 = f.vertex_point(p00)
v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11)
v01 = f.vertex_point(p01)
e1_bot = led(v00, v10, p00, 1, 0, 0, 5.0)
e1_right = led(v10, v11, p10, 0, 1, 0, 1.0)
eA_5mm = led(v01, v11, p01, 1, 0, 0, 5.0)  # top edge, y=0, length 5.0
e1_left = led(v00, v01, p00, 0, 1, 0, 1.0)
face1 = face4(
    [(e1_bot, True), (e1_right, True), (eA_5mm, False), (e1_left, False)],
    mk_plane_z0(),
)

# Face2: x=[0,4.9], y=[0.1,1.1] -- bottom edge at y=0.1, length 4.9, IS eB_4p9mm.
p00b = cp(0, 0.1, 0)
p10b = cp(4.9, 0.1, 0)
p11b = cp(4.9, 1.1, 0)
p01b = cp(0, 1.1, 0)
v00b = f.vertex_point(p00b)
v10b = f.vertex_point(p10b)
v11b = f.vertex_point(p11b)
v01b = f.vertex_point(p01b)
eB_4p9mm = led(v00b, v10b, p00b, 1, 0, 0, 4.9)  # bottom edge, y=0.1, length 4.9
e2_right = led(v10b, v11b, p10b, 0, 1, 0, 1.0)
e2_top = led(v01b, v11b, p01b, 1, 0, 0, 4.9)
e2_left = led(v00b, v01b, p00b, 0, 1, 0, 1.0)
face2 = face4(
    [(eB_4p9mm, True), (e2_right, True), (e2_top, False), (e2_left, False)],
    mk_plane_z0(),
)

# OPEN_SHELL with two near-parity-length faces 0.1mm apart IS the
# projection-direction near-parity mechanism.
shell = f.open_shell([face1, face2])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
