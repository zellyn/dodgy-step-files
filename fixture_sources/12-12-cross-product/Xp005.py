"""Xp005 — NURBS knot vector × control-point weight × tolerance-boundary cusp."""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(catalog_id="Xp005",
             defect='NURBS knot vector x control-point weight x tolerance-boundary cusp')

# Five control points for a cubic NURBS curve
# Defect 1: knot vector has duplicate inner knot not justified by multiplicity
# Defect 2: one weight is zero (indeterminate rational evaluation)
# Defect 3: cusp at tolerance boundary — consecutive CPs separated by ~1e-7

cp0 = f.cartesian_point((0.0,     0.0, 0.0))
cp1 = f.cartesian_point((1.0e-7,  0.0, 0.0))  # cusp: 1e-7 from cp0 (at Precision::Confusion)
cp2 = f.cartesian_point((1.0,     0.0, 0.0))
cp3 = f.cartesian_point((2.0,     1.0, 0.0))
cp4 = f.cartesian_point((3.0,     0.0, 0.0))

# Build a minimal planar face as the required geometry anchor
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

def line_edge(pa, pb, va, vb):
    dx = pb.args[1][0] - pa.args[1][0]
    dy = pb.args[1][1] - pa.args[1][1]
    dz = pb.args[1][2] - pa.args[1][2]
    length = (dx**2 + dy**2 + dz**2) ** 0.5
    d = f.direction((dx/length, dy/length, dz/length))
    vec = f.vector(d, length)
    ln = f.line(pa, vec)
    return f.edge_curve(va, vb, ln)

sq0 = f.cartesian_point((0.0, 0.0, 0.0))
sq1 = f.cartesian_point((1.0, 0.0, 0.0))
sq2 = f.cartesian_point((1.0, 1.0, 0.0))
sq3 = f.cartesian_point((0.0, 1.0, 0.0))
sv0 = f.vertex_point(sq0); sv1 = f.vertex_point(sq1)
sv2 = f.vertex_point(sq2); sv3 = f.vertex_point(sq3)
se0 = line_edge(sq0, sq1, sv0, sv1)
se1 = line_edge(sq1, sq2, sv1, sv2)
se2 = line_edge(sq2, sq3, sv2, sv3)
se3 = line_edge(sq3, sq0, sv3, sv0)
loop = f.edge_loop([
    f.oriented_edge(se0, True), f.oriented_edge(se1, True),
    f.oriented_edge(se2, True), f.oriented_edge(se3, True),
])
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# Defective NURBS curve: degree 3, 5 control points
# Knot vector (0,0,0,0, 0.5,0.5, 1,1,1,1) — inner pair duplicated without justification
# Weights (1.0, 0.0, 1.0, 1.0, 1.0) — zero weight at index 1 (indeterminate)
cp_refs = ",".join(f"#{cp.eid}" for cp in [cp0, cp1, cp2, cp3, cp4])
nurbs = f._emit_raw(
    f"(B_SPLINE_CURVE(3,({cp_refs}),.UNSPECIFIED.,.F.,.F.)"
    f"B_SPLINE_CURVE_WITH_KNOTS((4,2,4),(0.0,0.5,1.0),.UNSPECIFIED.)"
    f"BOUNDED_CURVE()CURVE()GEOMETRIC_REPRESENTATION_ITEM()"
    f"RATIONAL_B_SPLINE_CURVE((1.0,0.0,1.0,1.0,1.0))"
    f"REPRESENTATION_ITEM('xp005_defective_nurbs'))"
)
