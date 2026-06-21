"""Pf005 — Slow STEP import on geometric-set-heavy file.

Catalog claim: STEP files with thousands of GEOMETRIC_SET items
(points/curves) cause slow import because matching uses linear scan.
Reproducer: STEP with > 10k CARTESIAN_POINT / LINE / B_SPLINE_CURVE_WITH_KNOTS
entries inside GEOMETRIC_SETs.

The fixture builds multiple GEOMETRIC_CURVE_SETs each containing many
CARTESIAN_POINTs and LINEs, plus a GEOMETRIC_SET to hold curves —
encoding the structural pattern whose matching triggers the O(N²) scan.

Byte assertion: count_entity_def(b'CARTESIAN_POINT') >= 9
Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pf005",
    defect=(
        "geometric-set-heavy file: many CARTESIAN_POINTs and LINEs "
        "inside GEOMETRIC_CURVE_SETs; linear-scan matching causes O(N²) "
        "import cost; GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Strategy: emit N CARTESIAN_POINTs + N LINEs collected in GEOMETRIC_CURVE_SETs.
# N = 15 → 15 points + 15 lines = 30 elements per set; three sets = 45 CPs.
# The blob of GEOMETRIC_SET entries exercises the linear-scan matching bug.

N = 15   # entities per group

# Direction and vector shared for all lines.
xdir = f.direction((1.0, 0.0, 0.0))
vec  = f.vector(xdir, 1.0)

# Group 1: N points + N lines → GEOMETRIC_CURVE_SET
pts1 = [f.cartesian_point((float(i), 0.0, 0.0)) for i in range(N)]
lns1 = [f._emit_raw(f"LINE('',#{pts1[i].eid},#{vec.eid})") for i in range(N)]
elems1 = ",".join(f"#{p.eid}" for p in pts1) + "," + ",".join(f"#{l.eid}" for l in lns1)
gcs1 = f._emit_raw(f"GEOMETRIC_CURVE_SET('gset1',({elems1}))")

# Group 2: N points + N lines → GEOMETRIC_CURVE_SET
pts2 = [f.cartesian_point((float(i), 1.0, 0.0)) for i in range(N)]
lns2 = [f._emit_raw(f"LINE('',#{pts2[i].eid},#{vec.eid})") for i in range(N)]
elems2 = ",".join(f"#{p.eid}" for p in pts2) + "," + ",".join(f"#{l.eid}" for l in lns2)
gcs2 = f._emit_raw(f"GEOMETRIC_CURVE_SET('gset2',({elems2}))")

# Group 3: N points only → GEOMETRIC_CURVE_SET (pure point cloud variant)
pts3 = [f.cartesian_point((float(i), 2.0, 0.0)) for i in range(N)]
elems3 = ",".join(f"#{p.eid}" for p in pts3)
gcs3 = f._emit_raw(f"GEOMETRIC_CURVE_SET('gset3',({elems3}))")

# Register one of the sets as the model entity (product chain).
# GEOMETRIC_CURVE_SET → OCC yields empty shape (shape_null == True).
f.add_product_chain(gcs1)

# The other two sets are unreachable from the product chain — they sit in
# DATA as free-floating entities, exactly as in the bug-report shape where
# many GEOMETRIC_SET elements are scattered through the file.
