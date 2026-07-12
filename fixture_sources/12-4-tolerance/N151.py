"""N151 — BRepBuilderAPI_Sewing.SameParameterEdge.recursive-tolerance-comparison.

Accept second recursive sewing attempt only if both SameParameter achieved AND
tolerance improved (tolReached_2 < tolReached). Missing check causes
worse-tolerance fallbacks. First attempt tol=0.08 (good), second attempt
tol=0.12 (worse). Without guard, worse result selected.

Mechanism IS wired into 2 real ADVANCED_FACEs (not a faceless
GEOMETRIC_CURVE_SET): Face1 (x=[0,5], y=[-1,0]) has free top edge eA at
y=0; Face2 (x=[0,5], y=[0.08,1.08]) has free bottom edge eB_gap at
y=0.08 -- a genuine 0.08mm gap between two real face boundaries, matching
the first-attempt achieved tolerance the recursive-comparison bug
operates on. The second-attempt-worse-tolerance retry (0.12) is a
runtime-only SameParameterEdge internal recursion state that cannot be
encoded as a second static geometry without misrepresenting the input;
it is documented here and left as the scaffold's runtime half.

Fixture kind: scaffold (kernel-test-pair) -- the STEP file provides the
genuine first-attempt-tolerance candidate-edge-pair-on-real-faces setup;
the recursive monotonicity bug fires when SameParameterEdge is invoked
at runtime and internally retries.

Tier-3: n_faces_total == 2
Expected: occt=shape(1)/shape(1) gmsh=shape(18) ifc=schema_n/a  [NEEDS-ORACLE-REFRESH]
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N151",
    defect=(
        "SameParameterEdge recursive-tolerance-comparison: two "
        "ADVANCED_FACEs whose facing free edges (eA, eB_gap) are 0.08mm "
        "apart on real face boundaries -- first-attempt achieved tolerance "
        "for the recursive-retry monotonicity bug (1st attempt tol=0.08, "
        "2nd tol=0.12 is a runtime-only retry state)"
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


# Face1: x=[0,5], y=[-1,0] -- top edge at y=0, length 5.0, IS eA.
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
eA = led(v01, v11, p01, 1, 0, 0, 5.0)  # top edge, y=0 -- candidate
e1_left = led(v00, v01, p00, 0, 1, 0, 1.0)
face1 = face4(
    [(e1_bot, True), (e1_right, True), (eA, False), (e1_left, False)],
    mk_plane_z0(),
)

# Face2: x=[0,5], y=[0.08,1.08] -- bottom edge at y=0.08, length 5.0, IS eB_gap.
GAP = 0.08
p00b = cp(0, GAP, 0)
p10b = cp(5, GAP, 0)
p11b = cp(5, 1 + GAP, 0)
p01b = cp(0, 1 + GAP, 0)
v00b = f.vertex_point(p00b)
v10b = f.vertex_point(p10b)
v11b = f.vertex_point(p11b)
v01b = f.vertex_point(p01b)
eB_gap = led(v00b, v10b, p00b, 1, 0, 0, 5.0)  # bottom edge, y=0.08
e2_right = led(v10b, v11b, p10b, 0, 1, 0, 1.0)
e2_top = led(v01b, v11b, p01b, 1, 0, 0, 5.0)
e2_left = led(v00b, v01b, p00b, 0, 1, 0, 1.0)
face2 = face4(
    [(eB_gap, True), (e2_right, True), (e2_top, False), (e2_left, False)],
    mk_plane_z0(),
)

# OPEN_SHELL with two faces whose free edges are 0.08mm apart IS the
# first-attempt-tolerance candidate-pair mechanism (recursive comparison
# is a runtime SameParameterEdge retry state on top of this real setup).
shell = f.open_shell([face1, face2])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm, uncertainty=0.08)
