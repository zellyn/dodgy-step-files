"""Gn087 — ShapeUpgrade_SplitSurface.SetUSplitValues neg-zero.

Catalog claim: Split values containing -0.0; the dedup logic doesn't treat
-0.0 == 0.0 and produces a spurious "split" at the boundary.

Fixture: Degree-(2,2) B-spline surface (3x3 net, flat patch); split values
nominally [0.0, 0.5, 1.0] but encodes -0.0 at boundary via the knot vector.

Mechanism: GEOMETRIC_CURVE_SET containing a B_SPLINE_SURFACE_WITH_KNOTS
whose first U-knot is encoded as -0.0 (negative zero). The surface is a
flat 3x3 patch. OCC yields empty (GEOMETRIC_CURVE_SET is model entity).

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn087",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS (degree 2x2, 3x3 control net); "
        "U-knot vector starts with -0.0 instead of 0.0; "
        "SetUSplitValues dedup does not treat -0.0 == 0.0; "
        "spurious split at boundary; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Anchor for GEOMETRIC_CURVE_SET
anchor = f.cartesian_point((0.0, 0.0, 0.0))

# Build 3x3 control point grid for a flat square patch
pts = []
for i in range(3):
    row = []
    for j in range(3):
        row.append(f.cartesian_point((float(i) * 5.0, float(j) * 5.0, 0.0)))
    pts.append(row)

def row_refs(i):
    return "(" + ",".join(f"#{pts[i][j].eid}" for j in range(3)) + ")"

cp_grid = "(" + ",".join(row_refs(i) for i in range(3)) + ")"

# Degree-2 in both directions: knot mults (3,3) at endpoints for clamped.
# DEFECT: U-knot vector starts with -0.0 instead of 0.0
# Using a raw string so -0.0 is preserved as-is in the STEP file.
surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('neg_zero_split_test',2,2,"
    f"{cp_grid},.UNSPECIFIED.,.F.,.F.,.F.,"
    f"(3,3),(3,3),(-0.0,1.0),(0.0,1.0),.UNSPECIFIED.)"
)

gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('neg_zero_surf',(#{anchor.eid},#{surf.eid}))")
f.add_product_chain(gcs)
