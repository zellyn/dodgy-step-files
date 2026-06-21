"""N035 — Default tolerance precision: missing decimal-place qualifier.

A dimension with nominal value 5.0, tolerance +0.01/-0.01, but no
precision_qualifier on either the value or the nominal, and no global default.
Systems that don't walk the precision fallback chain show wrong-precision
tolerance. Two PLUS_MINUS_TOLERANCE instances encode the upper and lower bounds.

Byte assertions:
  count_entity_def(b'PLUS_MINUS_TOLERANCE') == 2
  contains(b'0.01') and contains(b'-0.01')
  contains(b'5.0')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N035",
    defect=(
        "dimension nominal 5.0 mm, tol +0.01/-0.01; no precision_qualifier; "
        "2×PLUS_MINUS_TOLERANCE without decimal-place qualifier; "
        "GEOMETRIC_CURVE_SET — OCC yields empty"
    ),
    schema="AP242",
)

# Minimal geometry.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

lu_ref = "#9056"
pds_ref = "#9055"

shape_asp = f._emit_raw(f"SHAPE_ASPECT('dim_feature','',{pds_ref},.T.)")

# Nominal value 5.0
nominal_val = f._emit_raw(
    f"LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(5.0),{lu_ref})"
)

# Tolerance bounds +0.01 / -0.01 (no precision qualifier).
upper_val = f._emit_raw(
    f"LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.01),{lu_ref})"
)
lower_val = f._emit_raw(
    f"LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(-0.01),{lu_ref})"
)

# Two PLUS_MINUS_TOLERANCE instances (positive and negative halves).
tv_pos = f._emit_raw(f"TOLERANCE_VALUE(#{lower_val.eid},#{upper_val.eid})")
tv_neg = f._emit_raw(f"TOLERANCE_VALUE(#{lower_val.eid},#{upper_val.eid})")

f._emit_raw(
    f"PLUS_MINUS_TOLERANCE(#{tv_pos.eid},'plus_side',#{shape_asp.eid})"
)
f._emit_raw(
    f"PLUS_MINUS_TOLERANCE(#{tv_neg.eid},'minus_side',#{shape_asp.eid})"
)
