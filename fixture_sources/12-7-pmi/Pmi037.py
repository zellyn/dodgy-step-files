"""Pmi037 — shape_aspect.product_definitional flag wrong polarity.

Catalog claim: shape_aspect.product_definitional is .F. where it must be .T.
for a feature carrying a dimensional_size, or vice-versa for datum-target
placement.

Reproducer recipe: shape_aspect carrying a dimensional_size with
product_definitional = .F.

Byte assertions:
  contains(b'SHAPE_ASPECT')
  contains(b'DIMENSIONAL_SIZE')
  contains(b'PLUS_MINUS_TOLERANCE')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi037",
    defect=(
        "SHAPE_ASPECT carrying a DIMENSIONAL_SIZE has product_definitional = .F. "
        "instead of the required .T.; receivers must warn and not silently rewrite "
        "the flag; silently accepting the wrong-polarity flag is forbidden; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT

# Defect: product_definitional = .F. — wrong polarity for a feature with dimensional_size.
asp = f._emit_raw("SHAPE_ASPECT('hole_feature','',#9055,.F.)")

# DIMENSIONAL_SIZE attached to the shape_aspect.
# 'diameter' is the correct name for a hole diameter per AP242 RP table.
dim_size = f._emit_raw(f"DIMENSIONAL_SIZE(#{asp.eid},'diameter')")

# Tolerance value.
tol_val = f._emit_raw(
    "MEASURE_REPRESENTATION_ITEM('tol',LENGTH_MEASURE(0.05),#9056)"
)

# TOLERANCE_VALUE for the plus/minus tolerance.
tol_value_ent = f._emit_raw(
    "TOLERANCE_VALUE(LENGTH_MEASURE(0.05),LENGTH_MEASURE(0.05))"
)

# PLUS_MINUS_TOLERANCE referencing the dimensional_size and the tolerance value.
f._emit_raw(
    f"PLUS_MINUS_TOLERANCE(#{tol_value_ent.eid},#{dim_size.eid})"
)
