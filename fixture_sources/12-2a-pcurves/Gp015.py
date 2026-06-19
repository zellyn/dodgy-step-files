"""Gp015 — Pcurve/3D-curve trimming failure ("Trimming of 2D curve failed").

Catalog claim: When the translator clips a PCURVE to the parameter range of
its hosting EDGE_CURVE, the trim operation fails because the 3D-curve
parameter range [first,last] maps to a UV band where the pcurve is
undefined.

Specific defect: EDGE_CURVE whose 3D curve spans [0, 2.0] (by vector
magnitude), but the pcurve's DEFINITIONAL_REPRESENTATION contains a
B-spline whose knot domain is [0, 1]. The translator must clip the pcurve
to the 3D edge's parameter range [0, 2.0], but the pcurve is only defined
on [0, 1]. The clip fails because 2.0 is outside the pcurve's domain.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gp015",
             defect="EDGE_CURVE 3D-range [0,2] exceeds PCURVE B-spline domain [0,1]: trim fails")

# Cylindrical surface as host
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
cyl = f.cylindrical_surface(plc, 1.0)

# 3D line for the edge: from (1,0,0) to (1,0,2) — parameter runs [0, 2.0]
# (the LINE's vector has magnitude 2.0, so the EDGE_CURVE spans [0, 2.0])
p_start_3d = f.cartesian_point((1.0, 0.0, 0.0))
p_end_3d = f.cartesian_point((1.0, 0.0, 2.0))
v_start = f.vertex_point(p_start_3d)
v_end = f.vertex_point(p_end_3d)
line_dir_3d = f.direction((0.0, 0.0, 1.0))
line_vec_3d = f.vector(line_dir_3d, 2.0)   # magnitude 2.0 → 3D domain [0, 2]
line_3d = f.line(p_start_3d, line_vec_3d)

# UV parametric context
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# PCURVE: B-spline in UV with knot domain [0, 1] ONLY.
# Represents a vertical line on the cylinder at u=0, v going from 0 to 1.
# But the 3D edge spans [0, 2.0], so the translator must clip the pcurve
# to parameter 2.0 — which is OUTSIDE the pcurve's domain [0, 1].
# This is the "Trimming of 2D curve failed" defect.
pc_cp0 = f.cartesian_point((0.0, 0.0))
pc_cp1 = f.cartesian_point((0.0, 1.0))

# Degree-1 B-spline (linear), 2 control points, knot domain [0, 1]
# Knot-mult sum = 2 + 1 + 1 = 4, so (2, 2) at [0, 1]
pcurve_basis = f.b_spline_curve_with_knots(
    degree=1,
    control_points=[pc_cp0, pc_cp1],
    knot_multiplicities=[2, 2],
    knots=[0.0, 1.0],
    curve_form="UNSPECIFIED",
    name="pcurve_domain_0_to_1",
)

pc_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_short',(#{pcurve_basis.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('',#{cyl.eid},#{pc_def.eid})")

# SURFACE_CURVE and EDGE_CURVE: 3D range is [0, 2] but pcurve domain is [0, 1]
# Clipping the pcurve to [0, 2] fails: 2.0 > pcurve_domain_max (1.0)
surface_curve = f._emit_raw(
    f"SURFACE_CURVE('',#{line_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
edge = f._emit_raw(
    f"EDGE_CURVE('',#{v_start.eid},#{v_end.eid},#{surface_curve.eid},.T.)"
)

loop = f.edge_loop([f.oriented_edge(edge, True)])
face = f.advanced_face([f.face_outer_bound(loop)], cyl)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
