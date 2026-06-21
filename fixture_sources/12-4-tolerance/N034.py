"""N034 — +/- tolerance bounds inverted, equal, or wrong measure type.

PLUS_MINUS_TOLERANCE recorded with: (1) upper_bound < lower_bound (inverted),
(2) upper_bound == lower_bound (equal), (3) wrong type PLANE_ANGLE_MEASURE_WITH_UNIT
instead of LENGTH_MEASURE_WITH_UNIT, (4) correct form for comparison.

Byte assertions:
  count_entity_def(b'PLUS_MINUS_TOLERANCE') == 4
  contains(b'-0.005') and contains(b'0.005')
  contains(b'PLANE_ANGLE_MEASURE_WITH_UNIT')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="N034",
    defect=(
        "4×PLUS_MINUS_TOLERANCE: inverted bounds (-0.005/0.005), equal bounds, "
        "wrong PLANE_ANGLE_MEASURE_WITH_UNIT type, correct form; SFA flags; "
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
shape_asp = f._emit_raw(f"SHAPE_ASPECT('feature','',{pds_ref},.T.)")

# Length unit measures.
len_upper = f._emit_raw(f"LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.005),{lu_ref})")
len_lower = f._emit_raw(f"LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(-0.005),{lu_ref})")
len_equal = f._emit_raw(f"LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.005),{lu_ref})")

# Angle unit (wrong type for length tolerance).
pau_ref = f._emit_raw("(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.))")
angle_val = f._emit_raw(
    f"PLANE_ANGLE_MEASURE_WITH_UNIT(PLANE_ANGLE_MEASURE(0.005),#{pau_ref.eid})"
)

# TOLERANCE_VALUE entity for each case.
# 1. Inverted: upper(-0.005) < lower(0.005)
tv_inverted = f._emit_raw(
    f"TOLERANCE_VALUE(#{len_lower.eid},#{len_upper.eid})"
)
# 2. Equal: upper == lower
len_eq1 = f._emit_raw(f"LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.005),{lu_ref})")
len_eq2 = f._emit_raw(f"LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.005),{lu_ref})")
tv_equal = f._emit_raw(f"TOLERANCE_VALUE(#{len_eq1.eid},#{len_eq2.eid})")
# 3. Wrong type: angle measure used for length tolerance
tv_wrongtype = f._emit_raw(
    f"TOLERANCE_VALUE(#{angle_val.eid},#{angle_val.eid})"
)
# 4. Correct form
tv_correct = f._emit_raw(
    f"TOLERANCE_VALUE(#{len_lower.eid},#{len_upper.eid})"
)

# Four PLUS_MINUS_TOLERANCE instances.
f._emit_raw(
    f"PLUS_MINUS_TOLERANCE(#{tv_inverted.eid},'',#{shape_asp.eid})"
)
f._emit_raw(
    f"PLUS_MINUS_TOLERANCE(#{tv_equal.eid},'',#{shape_asp.eid})"
)
f._emit_raw(
    f"PLUS_MINUS_TOLERANCE(#{tv_wrongtype.eid},'',#{shape_asp.eid})"
)
f._emit_raw(
    f"PLUS_MINUS_TOLERANCE(#{tv_correct.eid},'',#{shape_asp.eid})"
)
