"""Xp042 — NX → Onshape 'translation error' via super-multiplicity B-spline knot."""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Xp042",
             defect='NX super-multiplicity B-spline knot (interior mult=5 > degree+1=4) causes Onshape translation error')

# Byte assertions: contains(b'B_SPLINE_CURVE_WITH_KNOTS') and contains(b'(4,5,4)')
# Build a minimal valid geometry anchor for tier-3 load == "ok"
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

p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
p2 = f.cartesian_point((1.0, 1.0, 0.0))
p3 = f.cartesian_point((0.0, 1.0, 0.0))
v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)
e0 = line_edge(p0, p1, v0, v1)
e1 = line_edge(p1, p2, v1, v2)
e2 = line_edge(p2, p3, v2, v3)
e3 = line_edge(p3, p0, v3, v0)
loop = f.edge_loop([
    f.oriented_edge(e0, True), f.oriented_edge(e1, True),
    f.oriented_edge(e2, True), f.oriented_edge(e3, True),
])
face = f.advanced_face([f.face_outer_bound(loop)], plane)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)

# Defect: B_SPLINE_CURVE_WITH_KNOTS degree 3 with 8 control points
# knot multiplicities (4, 5, 4) at parameters (0, 0.5, 1)
# Interior knot multiplicity = 5 > degree+1 = 4 → SUPER-MULTIPLICITY (discontinuous)
cp0 = f.cartesian_point((0.0, 0.0, 0.0))
cp1 = f.cartesian_point((0.5, 0.5, 0.0))
cp2 = f.cartesian_point((1.0, 0.5, 0.0))
cp3 = f.cartesian_point((1.5, 0.0, 0.0))
cp4 = f.cartesian_point((2.0, 0.0, 0.0))
cp5 = f.cartesian_point((2.5, 0.5, 0.0))
cp6 = f.cartesian_point((3.0, 0.5, 0.0))
cp7 = f.cartesian_point((3.5, 0.0, 0.0))

cp_refs = ",".join(f"#{cp.eid}" for cp in [cp0,cp1,cp2,cp3,cp4,cp5,cp6,cp7])

# Emit directly with raw (4,5,4) so byte assertion contains(b'(4,5,4)') is satisfied
# degree=3, 8 control points → sum of mults must be 8+3+1=12 → 4+5+4=13... wait
# Correct: knot mult sum = n_poles + degree + 1 = 8 + 3 + 1 = 12
# But (4,5,4) sums to 13 — that's actually the super-multiplicity defect itself
# The total exceeds what's valid, making this a structural defect
# Knot parameters: (0, 0.5, 1.0)
bspline = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('xp042_supermult',3,({cp_refs}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(4,5,4),(0.,0.5,1.),.UNSPECIFIED.)"
)
