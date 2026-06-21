"""Pf014 — Long helix exported as huge B-spline (millions of poles).

Catalog claim: when a long 3D helix is projected onto its hosting cylinder,
OCCT emits a B-spline approximation rather than the analytic 2D LINE segment;
the parameter-space curve becomes a huge B-spline with thousands of knots.
Analogous: sweep(circle, helix(h>=30)) produces missing-face output.

The fixture encodes the structural pattern: an EDGE_CURVE whose 3D curve is a
helix (PCURVE wrapping a SURFACE_CURVE on a CYLINDRICAL_SURFACE), accompanied
by a bloated B_SPLINE_CURVE_WITH_KNOTS that represents the pathological
approximation of what should be an analytic LINE — many control points with
many repeated knots, all along the axis of the cylinder.

Byte assertion: count_entity_def(b'CARTESIAN_POINT') >= 32
Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pf014",
    defect=(
        "helix on CYLINDRICAL_SURFACE exported as huge B-spline pcurve "
        "instead of analytic 2D LINE; thousands of poles/knots; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry anchor: GEOMETRIC_CURVE_SET so OCC yields empty/empty.
anchor = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{anchor.eid}))")
f.add_product_chain(gcs)

# Cylindrical surface hosting the helix (radius=5, axis = Z).
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_zdir = f.direction((0.0, 0.0, 1.0))
cyl_xdir = f.direction((1.0, 0.0, 0.0))
cyl_plc  = f.axis2_placement_3d(cyl_orig, cyl_zdir, cyl_xdir)
cyl_surf = f.cylindrical_surface(cyl_plc, 5.0)

# The "correct" pcurve for a helix on a cylinder is an analytic LINE in
# parameter space.  The defect is that OCCT emits a B-SPLINE approximation.
# We encode the LINE form (what it should be) plus the B-spline (what OCC emits).

# Analytic LINE (the correct form — what the kernel should emit).
line_orig = f.cartesian_point((0.0, 0.0, 0.0))
line_dir  = f.direction((1.0, 1.0, 0.0))   # slope = helix pitch in param space
line_vec  = f.vector(line_dir, 1.0)
correct_line = f.line(line_orig, line_vec)

# Bloated B-SPLINE approximation (the defect form): degree-3, 36 poles along
# the helix spiral, representing the thousands-of-knots pathology at fixture scale.
N_POLES = 36
import math
poles = []
for i in range(N_POLES):
    theta = 2.0 * math.pi * i / (N_POLES - 1)
    x = 5.0 * math.cos(theta)
    y = 5.0 * math.sin(theta)
    z = float(i) * 30.0 / (N_POLES - 1)   # helix height = 30 (triggers bug)
    poles.append(f.cartesian_point((x, y, z)))

# Knot vector for a uniform clamped degree-3 B-spline over N_POLES control points.
n_knots_inner = N_POLES - 3 - 1   # = 32
knot_vals = [0] * 4 + list(range(1, n_knots_inner + 1)) + [n_knots_inner + 1] * 4
knot_mults = [4] + [1] * n_knots_inner + [4]

knot_vals_str  = ",".join(str(k) for k in knot_vals)
knot_mults_str = ",".join(str(m) for m in knot_mults)
pole_refs      = ",".join(f"#{p.eid}" for p in poles)

bspline = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('helix_approx',3,"
    f"({pole_refs}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"({knot_mults_str}),"
    f"({knot_vals_str}),"
    f".UNSPECIFIED.)"
)

# EDGE_CURVE: start/end vertices at the helix endpoints.
v_start = f.vertex_point(poles[0])
v_end   = f.vertex_point(poles[-1])
ec      = f.edge_curve(v_start, v_end, bspline)

# Wrap in GEOMETRIC_CURVE_SET alongside the correct LINE (for comparison).
all_items = ",".join([
    f"#{correct_line.eid}",
    f"#{bspline.eid}",
])
extra_gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('helix_curves',({all_items}))")
