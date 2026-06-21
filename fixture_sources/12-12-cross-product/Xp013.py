"""Xp013 — Cone apex pcurve × surface-folded × non-manifold vertex."""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(catalog_id="Xp013",
             defect='Cone apex pcurve x surface-folded x non-manifold vertex')

# Defect 1: CONICAL_SURFACE with a face whose wire passes through the apex
# Cone: apex at (0,0,0), half_angle=pi/4, axis along Z
import math
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
cone = f.conical_surface(plc, 0.0, math.pi / 4.0)  # radius=0 at apex

def line_edge(pa, pb, va, vb):
    dx = pb.args[1][0] - pa.args[1][0]
    dy = pb.args[1][1] - pa.args[1][1]
    dz = pb.args[1][2] - pa.args[1][2]
    length = max((dx**2 + dy**2 + dz**2) ** 0.5, 1.0e-15)
    d = f.direction((dx/length, dy/length, dz/length))
    vec = f.vector(d, length)
    ln = f.line(pa, vec)
    return f.edge_curve(va, vb, ln)

# Face 1: cone face whose wire goes through apex (0,0,0)
p_apex = f.cartesian_point((0.0,  0.0, 0.0))  # cone apex — singular point
p_rim0 = f.cartesian_point((1.0,  0.0, 1.0))  # on cone surface (r=1, z=1)
p_rim1 = f.cartesian_point((0.0,  1.0, 1.0))
v_apex = f.vertex_point(p_apex)
v_rim0 = f.vertex_point(p_rim0)
v_rim1 = f.vertex_point(p_rim1)
e_ca0 = line_edge(p_apex, p_rim0, v_apex, v_rim0)
e_ca1 = line_edge(p_rim0, p_rim1, v_rim0, v_rim1)
e_ca2 = line_edge(p_rim1, p_apex, v_rim1, v_apex)
loop_cone = f.edge_loop([
    f.oriented_edge(e_ca0, True),
    f.oriented_edge(e_ca1, True),
    f.oriented_edge(e_ca2, True),
])
face_cone = f.advanced_face([f.face_outer_bound(loop_cone)], cone)

# Defect 2: B-spline surface with folded control net (Jacobian sign flip)
# 3x2 control net — middle row placed to cause fold
cp00 = f.cartesian_point((0.0, 0.0, 0.0)); cp01 = f.cartesian_point((0.0, 1.0, 0.0))
cp10 = f.cartesian_point((1.0, 0.0, 1.0)); cp11 = f.cartesian_point((1.0, 1.0, 1.0))
cp20 = f.cartesian_point((0.5, 0.0, 0.0)); cp21 = f.cartesian_point((0.5, 1.0, 0.0))
# cp20/cp21 fold back — causes Jacobian sign flip in U
bsurf = f.b_spline_surface_with_knots(
    2, 1,
    [[cp00, cp01], [cp10, cp11], [cp20, cp21]],
    [3, 3], [2, 2],
    [0.0, 1.0], [0.0, 1.0],
)

p_s0 = f.cartesian_point((0.0, 0.0, 0.0)); p_s1 = f.cartesian_point((1.0, 0.0, 1.0))
p_s2 = f.cartesian_point((1.0, 1.0, 1.0)); p_s3 = f.cartesian_point((0.0, 1.0, 0.0))
vs0 = f.vertex_point(p_s0); vs1 = f.vertex_point(p_s1)
vs2 = f.vertex_point(p_s2); vs3 = f.vertex_point(p_s3)
es0 = line_edge(p_s0, p_s1, vs0, vs1)
es1 = line_edge(p_s1, p_s2, vs1, vs2)
es2 = line_edge(p_s2, p_s3, vs2, vs3)
es3 = line_edge(p_s3, p_s0, vs3, vs0)
loop_surf = f.edge_loop([
    f.oriented_edge(es0, True), f.oriented_edge(es1, True),
    f.oriented_edge(es2, True), f.oriented_edge(es3, True),
])
face_surf = f.advanced_face([f.face_outer_bound(loop_surf)], bsurf)

# Defect 3: non-manifold vertex — v_apex is shared by 4 edges from different shell components
# We emit extra edges incident to v_apex to demonstrate the non-manifold condition
p_extra0 = f.cartesian_point((0.5, 0.5, 0.5))
p_extra1 = f.cartesian_point((-0.5, 0.5, 0.5))
v_ex0 = f.vertex_point(p_extra0)
v_ex1 = f.vertex_point(p_extra1)
e_nm0 = line_edge(p_apex, p_extra0, v_apex, v_ex0)
e_nm1 = line_edge(p_apex, p_extra1, v_apex, v_ex1)
f._emit_raw(f"/* xp013 defect-3: v_apex #{v_apex.eid} shared by edges "
            f"#{e_ca0.eid}, #{e_ca2.eid}, #{e_nm0.eid}, #{e_nm1.eid} — non-manifold vertex */")

shell = f.open_shell([face_cone, face_surf])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
