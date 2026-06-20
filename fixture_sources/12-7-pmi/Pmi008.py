"""Pmi008 — Tolerance precision: missing decimal-place qualifier fallback chain.

Catalog claim: Some CAD systems ignore tolerance values lacking an explicit
decimal-place qualifier even when a default precision is set globally.
The fallback hierarchy is: precision at tolerance value → precision at nominal
value → global default. This fixture emits a dimension with PLUS_MINUS_TOLERANCE
and TOLERANCE_VALUE but no PRECISION_QUALIFIER anywhere.

Reproducer: dimension nominal 5.0, tolerance +0.01/-0.01, no PRECISION_QUALIFIER
on either value, no global default.

Byte assertions:
  contains(b'PLUS_MINUS_TOLERANCE')
  contains(b'TOLERANCE_VALUE')
  count_entity_def(b'PRECISION_QUALIFIER') == 0

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi008",
    defect=(
        "PLUS_MINUS_TOLERANCE + TOLERANCE_VALUE with no PRECISION_QUALIFIER; "
        "fallback hierarchy broken — no precision at tolerance, nominal, or global; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT

# Shape aspect for the dimensioned feature.
shape_asp = f._emit_raw("SHAPE_ASPECT('dim_feature','',#9055,.T.)")

# Dimensional size: nominal 5.0 mm.
dim_size = f._emit_raw(f"DIMENSIONAL_SIZE(#{shape_asp.eid},'shaft_diameter')")
nom_mri = f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('nominal',LENGTH_MEASURE(5.0),#9056)"
)

# Tolerance values: +0.01 / -0.01.
upper_val = f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('upper',LENGTH_MEASURE(0.01),#9056)"
)
lower_val = f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('lower',LENGTH_MEASURE(0.01),#9056)"
)

# TOLERANCE_VALUE: holds upper and lower bound MRIs.
tol_val = f._emit_raw(
    f"TOLERANCE_VALUE(#{upper_val.eid},#{lower_val.eid})"
)

# Defect: PLUS_MINUS_TOLERANCE with no PRECISION_QUALIFIER on any value.
# The fallback chain has nothing to fall back to.
f._emit_raw(
    f"PLUS_MINUS_TOLERANCE(#{tol_val.eid},#{dim_size.eid})"
)
# Intentionally no PRECISION_QUALIFIER — that is the defect.
