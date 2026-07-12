"""Tsh027 — Coincident-but-not-shared faces between adjacent solids.

Catalog claim: "A built-up assembly imports as N disconnected
MANIFOLD_SOLID_BREPs; faces shared between adjacent parts are
coincident-but-not-shared (each part has its own copy)."

Demonstration: two MANIFOLD_SOLID_BREPs whose oriented bounding boxes
touch along a single shared planar face — each brep has its OWN copy
of the interface face (distinct entity IDs, identical control points).
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tsh027",
             defect="Two MANIFOLD_SOLID_BREPs share an interface face that is duplicated, not shared")


def _quad_face(p_topleft, p_topright, p_botright, p_botleft, normal_axis):
    """Build a quadrilateral ADVANCED_FACE on a plane."""
    pts = [p_topleft, p_topright, p_botright, p_botleft]
    verts = [f.vertex_point(p) for p in pts]
    oriented = []
    for i in range(4):
        p_from, p_to = pts[i], pts[(i+1)%4]
        v_from, v_to = verts[i], verts[(i+1)%4]
        dx = p_to.args[1][0] - p_from.args[1][0]
        dy = p_to.args[1][1] - p_from.args[1][1]
        dz = p_to.args[1][2] - p_from.args[1][2]
        length = (dx*dx + dy*dy + dz*dz) ** 0.5
        d = f.direction((dx/length, dy/length, dz/length))
        vec = f.vector(d, length)
        line = f.line(p_from, vec)
        oriented.append(f.oriented_edge(f.edge_curve(v_from, v_to, line)))
    loop = f.edge_loop(oriented)
    nx = normal_axis.args[1][0]
    ref_dir = f.direction((0.0, 0.0, 1.0)) if abs(nx) > 0.9 else f.direction((1.0, 0.0, 0.0))
    plc = f.axis2_placement_3d(p_topleft, normal_axis, ref_dir)
    plane = f.plane(plc)
    return f.advanced_face([f.face_outer_bound(loop)], plane)


# SOLID A: cube from (0,0,0) to (1,1,1). Built using only the +x face.
# For brevity we use a single-face "shell" — sufficient to demonstrate
# the coincident-face-not-shared topology pattern.
A_plus_x_p0 = f.cartesian_point((1.0, 0.0, 0.0), name="A_face_p0")
A_plus_x_p1 = f.cartesian_point((1.0, 1.0, 0.0), name="A_face_p1")
A_plus_x_p2 = f.cartesian_point((1.0, 1.0, 1.0), name="A_face_p2")
A_plus_x_p3 = f.cartesian_point((1.0, 0.0, 1.0), name="A_face_p3")
A_face = _quad_face(A_plus_x_p0, A_plus_x_p1, A_plus_x_p2, A_plus_x_p3,
                    f.direction((1.0, 0.0, 0.0)))
A_shell = f.closed_shell([A_face])
A_brep = f.manifold_solid_brep(A_shell, name="SolidA")

# SOLID B: cube from (1,0,0) to (2,1,1). Its -x face is at x=1 — the SAME
# plane as A's +x face. But it has its OWN points (B_face_p0 != A_face_p0
# even though coords match).
B_minus_x_p0 = f.cartesian_point((1.0, 0.0, 0.0), name="B_face_p0")
B_minus_x_p1 = f.cartesian_point((1.0, 0.0, 1.0), name="B_face_p1")
B_minus_x_p2 = f.cartesian_point((1.0, 1.0, 1.0), name="B_face_p2")
B_minus_x_p3 = f.cartesian_point((1.0, 1.0, 0.0), name="B_face_p3")
B_face = _quad_face(B_minus_x_p0, B_minus_x_p1, B_minus_x_p2, B_minus_x_p3,
                    f.direction((-1.0, 0.0, 0.0)))
B_shell = f.closed_shell([B_face])
B_brep = f.manifold_solid_brep(B_shell, name="SolidB")

# Both solids exist independently. A_face and B_face have IDENTICAL coords
# (1,0,0), (1,1,0), (1,1,1), (1,0,1) but DIFFERENT entity IDs.
# The sewing operation should detect this and merge.

# Register both breps as the model (use the first as the chain anchor)
f.add_product_chain(A_brep, mode="brep_shape")
