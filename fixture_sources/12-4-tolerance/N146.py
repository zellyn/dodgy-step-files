"""N146 — EvaluateDistances.zero_angle_count_guard.

BRepBuilderAPI_Sewing angular precision defect: division-by-zero on degenerate
surface (zero D1 normal magnitude). nbComputedAngle guard missing; tabAng
becomes NaN when evaluating edges on plane/point-like geometry.

Mechanism IS wired into 2 real ADVANCED_FACEs (not a faceless
GEOMETRIC_CURVE_SET): Face1 occupies x=[0,1], y=[-1,0]; Face2 occupies
x=[0,1], y=[0,1]. Face1's top edge (e0_degen) and Face2's bottom edge
(e1_degen_coincident) are DISTINCT, unmerged EDGE_CURVEs that occupy the
exact same 3D segment (y=0, x=[0,1]) -- a perfectly parallel, zero-distance
candidate pair. This is exactly the degenerate input EvaluateDistances's
angle computation chokes on: two exactly-coincident/parallel candidate
edges make the cross-product magnitude (and hence the angle it guards)
collapse to zero, and the missing nbComputedAngle guard lets a NaN through.

Fixture kind: scaffold (kernel-test-pair) -- the STEP file provides the
genuine coincident-free-edge-on-real-faces setup; the actual NaN is
produced only when BRepBuilderAPI_Sewing's EvaluateDistances is invoked
at runtime on this pair.

Tier-3: n_faces_total == 2
Expected: occt=shape(1)/shape(1) gmsh=shape(18) ifc=schema_n/a  [NEEDS-ORACLE-REFRESH]
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N146",
    defect=(
        "EvaluateDistances zero_angle_count_guard: two ADVANCED_FACEs whose "
        "facing free edges (e0_degen, e1_degen_coincident) are exactly "
        "coincident (distance 0, perfectly parallel) -- degenerate-surface "
        "zero-D1-normal candidate pair; nbComputedAngle guard missing; "
        "tabAng becomes NaN"
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


# Face1: x=[0,1], y=[-1,0] -- top edge at y=0 IS the degenerate candidate e0_degen.
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
e0_degen = led(v01, v11, p01, 1, 0, 0, 1.0)  # top edge, y=0 -- self-sewing candidate
e1_left = led(v00, v01, p00, 0, 1, 0, 1.0)
face1 = face4(
    [(e1_bot, True), (e1_right, True), (e0_degen, False), (e1_left, False)],
    mk_plane_z0(),
)

# Face2: x=[0,1], y=[0,1] -- bottom edge at y=0 IS a DISTINCT, exactly-coincident
# duplicate candidate edge e1_degen_coincident (same 3D segment as e0_degen).
p00b = cp(0, 0, 0)
p10b = cp(1, 0, 0)
p11b = cp(1, 1, 0)
p01b = cp(0, 1, 0)
v00b = f.vertex_point(p00b)
v10b = f.vertex_point(p10b)
v11b = f.vertex_point(p11b)
v01b = f.vertex_point(p01b)
e1_degen_coincident = led(v00b, v10b, p00b, 1, 0, 0, 1.0)  # bottom edge, y=0
e2_right = led(v10b, v11b, p10b, 0, 1, 0, 1.0)
e2_top = led(v01b, v11b, p01b, 1, 0, 0, 1.0)
e2_left = led(v00b, v01b, p00b, 0, 1, 0, 1.0)
face2 = face4(
    [(e1_degen_coincident, True), (e2_right, True), (e2_top, False), (e2_left, False)],
    mk_plane_z0(),
)

# OPEN_SHELL with two faces meeting exactly at y=0 via unmerged duplicate
# edges IS the zero-angle degenerate-candidate mechanism.
shell = f.open_shell([face1, face2])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
