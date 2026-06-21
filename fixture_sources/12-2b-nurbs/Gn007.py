"""Gn007 — Under-sampled B_SPLINE_CURVE_WITH_KNOTS for long helical thread.

Catalog claim: long thin parts exported from PTC Creo at default relative accuracy
produce B-spline approximations of helical threads with far too few control points;
poles zig-zag in X and barely move radially — severe under-sampling.

Byte assertion: contains(b'B_SPLINE_CURVE')
Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn007",
    defect=(
        "Under-sampled B_SPLINE_CURVE_WITH_KNOTS for helical thread: Creo default "
        "relative accuracy exports a 2500 mm shaft helix with only ~16 control points; "
        "poles zig-zag in X sign and barely move radially; far fewer poles per turn than "
        "a faithful helix needs; heal: writers preserve authored degree/knot structure; "
        "consumers warn-and-accept on geometric_validation_property mismatch; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Anchor
anchor = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{anchor.eid}))")
f.add_product_chain(gcs)

# Under-sampled helix approximation: 16 control points over z=0..2500
# Poles zig-zag in X (radius ~5mm helix on 2500mm shaft)
# This is the "Creo relative-accuracy" pattern: few poles, signs alternate
import math
poles = []
n_poles = 16
for k in range(n_poles):
    t = k / (n_poles - 1)
    z = t * 0.2500  # scale to unit range; real would be 2500 mm
    # Zig-zag in X: alternating sign, minimal radial variation
    r = 5.0 * (1.0 + 0.05 * math.sin(k))  # barely varies radially
    x = r * ((-1.0)**k) * 0.01  # sign alternates — the under-sampling artifact
    y = 0.0
    poles.append(f.cartesian_point((x, y, z)))

pole_refs = "(" + ",".join(f"#{p.eid}" for p in poles) + ")"

# Degree-3 B-spline with uniform clamped knots (16 poles, degree 3)
# nknots = n + deg + 1 = 16 + 3 + 1 = 20; clamped: mult (4, 1,1,...,1, 4)
n = n_poles
deg = 3
n_interior = n - deg - 1  # = 12
mults = [deg+1] + [1]*n_interior + [deg+1]
knot_vals = [0.0] + [k/(n_interior+1) for k in range(1, n_interior+1)] + [1.0]

mults_str = "(" + ",".join(str(m) for m in mults) + ")"
knots_str  = "(" + ",".join(f"{v:.6f}" for v in knot_vals) + ")"

f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('helix_under_sampled',{deg},"
    f"{pole_refs},.UNSPECIFIED.,.F.,.F.,"
    f"{mults_str},{knots_str},.UNSPECIFIED.)"
)
