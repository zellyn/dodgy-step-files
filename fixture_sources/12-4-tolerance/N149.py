"""N149 — FindCandidates.equidistant_precision_test.

Precision-equality guard absent: candidates differing by 1e-11 inserted as
distinct despite Precision::Confusion (~1e-10) threshold. Tiebreaker logic
bypassed for numerically identical distances.

Mechanism IS wired into 2 real ADVANCED_FACEs (not a faceless
GEOMETRIC_CURVE_SET): Face1 occupies y=[-1,0] with free top edge eA at
y=0; Face2 occupies y=[1e-11,1+1e-11] with free bottom edge
eB_sub_confusion at y=1e-11 -- a genuine gap below Precision::Confusion
(~1e-10) between two real face boundaries. FindCandidates's missing
precision-equality guard treats this sub-confusion-threshold pair as
numerically distinct instead of collapsing it via the tiebreaker.

Fixture kind: scaffold (kernel-test-pair) -- the STEP file provides the
genuine sub-confusion-threshold candidate-edge-pair-on-real-faces setup;
the tiebreaker bug fires when FindCandidates is invoked at runtime.

Tier-3: n_faces_total == 2
Expected: occt=shape(1)/shape(1) gmsh=shape(18) ifc=schema_n/a  [NEEDS-ORACLE-REFRESH]
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N149",
    defect=(
        "FindCandidates equidistant_precision: two ADVANCED_FACEs whose "
        "facing free edges (eA, eB_sub_confusion) are 1e-11mm apart; "
        "Precision::Confusion ~1e-10; tiebreaker logic bypassed on real "
        "face boundaries"
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


# Face1: x=[0,1], y=[-1,0] -- top edge at y=0 IS the candidate eA.
p00 = cp(0, -1, 0)
p10 = cp(1, -1, 0)
p11 = cp(1, 0, 0)
p01 = cp(0, 0, 0)
v00 = f.vertex_point(p00)
v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11)
v01 = f.vertex_point(p01)
e1_bot = led(v00, v10, p00, 1, 0, 0, 1.0)
e1_right = led(v10, v11, p10, 0, 1, 0, 1.0)
eA = led(v01, v11, p01, 1, 0, 0, 1.0)  # top edge, y=0 -- candidate
e1_left = led(v00, v01, p00, 0, 1, 0, 1.0)
face1 = face4(
    [(e1_bot, True), (e1_right, True), (eA, False), (e1_left, False)],
    mk_plane_z0(),
)

# Face2: x=[0,1], y=[1e-11, 1+1e-11] -- bottom edge at y=1e-11 IS
# eB_sub_confusion, a genuinely separate candidate below Precision::Confusion.
GAP = 1.0e-11
p00b = cp(0, GAP, 0)
p10b = cp(1, GAP, 0)
p11b = cp(1, 1 + GAP, 0)
p01b = cp(0, 1 + GAP, 0)
v00b = f.vertex_point(p00b)
v10b = f.vertex_point(p10b)
v11b = f.vertex_point(p11b)
v01b = f.vertex_point(p01b)
eB_sub_confusion = led(v00b, v10b, p00b, 1, 0, 0, 1.0)  # bottom edge, y=1e-11
e2_right = led(v10b, v11b, p10b, 0, 1, 0, 1.0)
e2_top = led(v01b, v11b, p01b, 1, 0, 0, 1.0)
e2_left = led(v00b, v01b, p00b, 0, 1, 0, 1.0)
face2 = face4(
    [(eB_sub_confusion, True), (e2_right, True), (e2_top, False), (e2_left, False)],
    mk_plane_z0(),
)

# OPEN_SHELL with two faces whose free edges are 1e-11mm apart (below
# Precision::Confusion) IS the equidistant-precision candidate mechanism.
shell = f.open_shell([face1, face2])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm, uncertainty=1.0e-10)
