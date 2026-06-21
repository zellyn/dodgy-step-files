"""Ad089 — Reader broken parsing on missing last parameter.

Catalog claim: a STEP entity record ends with a trailing comma and missing
final parameter (`#1=ENTITY_NAME(a, b,);`). The parser's parameter consumer
expects N parameters but sees N-1 with a trailing comma; falls off the end of
the parameter list and reads the next entity's first byte as the missing
parameter.

Reproducer recipe:
  #1=CARTESIAN_POINT('',(1.0,2.0,3.0,)); — extra trailing comma in parameter list.
  Parser reads the next entity as the missing parameter.

Byte assertions:
  matches(rb',\\s*\\)\\s*\\)\\s*;')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad089",
    defect=(
        "trailing comma in CARTESIAN_POINT coordinate list (1.0,2.0,3.0,); "
        "parser parameter-consumer falls off end of list, reads next entity's "
        "first byte as missing parameter; "
        "OCCT MANTIS#0031756; See also Ad088; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))   # #1
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")  # #2
f.add_product_chain(gcs)

# Attack payload 1: CARTESIAN_POINT with trailing comma inside the coordinate
# list — the inner list ends with a comma before the closing ')'.
# Satisfies: matches(rb',\s*\)\s*\)\s*;')
# The pattern is: ,(trailing_comma) ) ) ;  i.e. ,)) where the first ) closes
# the coordinate sub-list and the second ) closes the entity parameter list.
f._emit_raw("CARTESIAN_POINT('trailing_comma',(1.0,2.0,3.0,))")

# Attack payload 2: DIRECTION entity with trailing comma in its ratio list.
# Ensures the defect pattern appears more than once, stressing the parser
# across entity boundaries.
f._emit_raw("DIRECTION('trailing_dir',(1.0,0.0,0.0,))")

# Attack payload 3: VECTOR whose magnitude parameter has a trailing comma
# at the entity level (not inside a sub-list).
f._emit_raw("VECTOR('trailing_vec',#1,1.0,)")
