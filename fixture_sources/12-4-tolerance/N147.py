"""N147 — FindCandidates.acceptance_criteria_composite_filter.

Composite AND condition omitted: candidates exceeding myTolerance (0.15 >
0.1) with undersized coverage falsely accepted. Full condition
(aMaxDist<=tol AND arrLen>minTol) required but first clause alone applied.

Mechanism IS wired into 2 real ADVANCED_FACEs (not a faceless
GEOMETRIC_CURVE_SET): Face1 occupies y=[-1,0] with free top edge eA at
y=0; Face2 occupies y=[0.15,1.15] with free bottom edge eB_offset at
y=0.15. The 0.15 mm gap between eA and eB_offset exceeds myTolerance
(0.1 mm, encoded via the global UNCERTAINTY_MEASURE_WITH_UNIT) -- exactly
the over-tolerance candidate pair FindCandidates's composite filter
should reject via the (aMaxDist<=tol AND arrLen>minTol) AND, but the
missing second clause lets through.

Fixture kind: scaffold (kernel-test-pair) -- the STEP file provides the
genuine over-tolerance candidate-edge-pair-on-real-faces setup; the
composite-filter bug fires when FindCandidates is invoked at runtime.

Tier-3: n_faces_total == 2
Expected: occt=shape(1)/shape(1) gmsh=shape(18) ifc=schema_n/a  [NEEDS-ORACLE-REFRESH]
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N147",
    defect=(
        "FindCandidates composite_filter: two ADVANCED_FACEs whose facing "
        "free edges (eA, eB_offset) are 0.15mm apart; myTolerance=0.1mm; "
        "first clause only accepts (0.15 > 0.1 not checked) -- candidate "
        "pair genuinely exceeds tolerance on real face boundaries"
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

# Face2: x=[0,1], y=[0.15,1.15] -- bottom edge at y=0.15 IS eB_offset, a
# genuinely separate candidate 0.15mm away from eA (over tolerance).
p00b = cp(0, 0.15, 0)
p10b = cp(1, 0.15, 0)
p11b = cp(1, 1.15, 0)
p01b = cp(0, 1.15, 0)
v00b = f.vertex_point(p00b)
v10b = f.vertex_point(p10b)
v11b = f.vertex_point(p11b)
v01b = f.vertex_point(p01b)
eB_offset = led(v00b, v10b, p00b, 1, 0, 0, 1.0)  # bottom edge, y=0.15
e2_right = led(v10b, v11b, p10b, 0, 1, 0, 1.0)
e2_top = led(v01b, v11b, p01b, 1, 0, 0, 1.0)
e2_left = led(v00b, v01b, p00b, 0, 1, 0, 1.0)
face2 = face4(
    [(eB_offset, True), (e2_right, True), (e2_top, False), (e2_left, False)],
    mk_plane_z0(),
)

# OPEN_SHELL with two faces whose free edges are 0.15mm apart (> myTolerance
# 0.1mm) IS the over-tolerance composite-filter candidate mechanism.
shell = f.open_shell([face1, face2])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm, uncertainty=0.1)
