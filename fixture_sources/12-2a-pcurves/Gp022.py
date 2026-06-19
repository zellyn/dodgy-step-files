"""Gp022 — EDGE_CURVE SameParameter=.T. asserted but 3D curve and pcurve use
different parameterisations (degenerate B-spline pcurve).

Catalog claim: An EDGE_CURVE declares SameParameter (the .T. flag), asserting
that 3D curve and pcurve share parameterisation, but evaluating both at the
same parameter value yields points that diverge beyond the edge's tolerance.
The catalog's specific shape: pcurve is a degree-2 B_SPLINE_CURVE_WITH_KNOTS
whose middle control point is offset (control points (0,0)/(0.8,0)/(1,0) with
uniform endpoint knots), so its parameterisation collapses near the end while
the 3D LINE is uniformly parameterised. The two curves describe the same edge
geometrically (both start and end at the same 3D points) but at different paces.

Fixture: A cylindrical surface with one horizontal edge at v=0.5 (mid-height),
u∈[0,2π] mapped to [0,1] on the surface. The 3D curve is a LINE from (1,0,0.5)
uniformly parameterised over [0,1]. The pcurve is a degree-2 B-spline with
control points (0,0.5), (0.8,0.5), (1.0,0.5) and uniform-endpoint knots [0,1].
At parameter t=0.5 the 3D line evaluates to u=0.5, but the B-spline evaluates
to u≈0.64 (quadratic weighting from the offset middle pole). Divergence >> 1e-6.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gp022",
             defect="EDGE_CURVE SameParameter=.T. but 3D LINE uniform over [0,1] disagrees with degree-2 B-spline pcurve with middle pole at (0.8,0.5): at t=0.5, 3D gives u=0.5 vs pcurve u≈0.64")

# Host: cylindrical surface, radius 1, axis Z.
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
cyl = f.cylindrical_surface(plc, 1.0)

# 3D edge: a straight LINE with uniform [0,1] parameterisation along x,
# from (0,0,0.5) to (1,0,0.5). The defect is the PCURVE's NON-uniform
# parameterisation despite the SameParameter=.T. flag.
p_start = f.cartesian_point((0.0, 0.0, 0.5))
p_end = f.cartesian_point((1.0, 0.0, 0.5))
v_start = f.vertex_point(p_start)
v_end = f.vertex_point(p_end)

line_dir_3d = f.direction((1.0, 0.0, 0.0))
line_vec_3d = f.vector(line_dir_3d, 1.0)  # magnitude 1 → parameter [0,1] uniform
line_3d = f.line(p_start, line_vec_3d)

# UV parametric context
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# THE DEFECT: degree-2 B-spline pcurve with middle pole at (0.8, 0.5) instead
# of (0.5, 0.5). Control points: (0,0.5), (0.8,0.5), (1.0,0.5).
# This is the exact "middle pole offset" shape from the catalog description.
# Parameterisation is endpoint-interpolating (knots [0,0,0,1,1,1] — degree 2,
# 3 control points, sum multiplicities = 3+3 = 6 = n+p+1 = 3+2+1 ✓).
#
# At t=0.5 (B-spline):
#   B(0.5) = (1-t)²*P0 + 2t(1-t)*P1 + t²*P2
#           = 0.25*(0,0.5) + 0.5*(0.8,0.5) + 0.25*(1,0.5)
#           = (0+0.4+0.25, 0.5) = (0.65, 0.5)
# At t=0.5 (3D LINE): maps uniformly to u=0.5.
# Divergence in u: |0.65 − 0.5| = 0.15 >> 1e-6. Same-parameter invariant violated.
pc_cp0 = f.cartesian_point((0.0, 0.5))
pc_cp1 = f.cartesian_point((0.8, 0.5))   # DEFECT: offset middle pole; should be (0.5, 0.5)
pc_cp2 = f.cartesian_point((1.0, 0.5))

pcurve_bspline = f.b_spline_curve_with_knots(
    degree=2,
    control_points=[pc_cp0, pc_cp1, pc_cp2],
    knot_multiplicities=[3, 3],
    knots=[0.0, 1.0],
    curve_form="UNSPECIFIED",
    name="pcurve_nonuniform",
)

pc_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('degenerate_bspline_pc',(#{pcurve_bspline.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('',#{cyl.eid},#{pc_def.eid})")

# EDGE_CURVE with SameParameter=.T. — asserts parameterisations are identical.
# They are NOT: 3D at t=0.5 is u=0.5, pcurve at t=0.5 is u≈0.65.
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
