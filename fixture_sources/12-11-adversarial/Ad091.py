"""Ad091 — Crash on STEP file from non-C locale (decimal separator).

Catalog claim: a STEP file written under a non-C locale (e.g., Czech, German)
uses comma as the decimal separator (`1,5` instead of `1.5`). When read on a
system with C locale, the parser interprets `1,5` as two integers separated by
a comma; the second integer is silently shifted into the next parameter.
Misalignment leads to crash deeper in the geometry builder.

Reproducer recipe:
  CARTESIAN_POINT('',(1,5,2,5,3,5)) — intended as (1.5, 2.5, 3.5).

Byte assertions:
  matches(rb"CARTESIAN_POINT\\([^;]*,\\(\\s*\\d+\\s*,\\s*\\d+\\s*,\\s*\\d+\\s*,\\s*\\d+")
  count(b',') >= 5 and matches(rb'\\(\\d+,\\d+,\\d+,\\d+,\\d+,\\d+\\)')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad091",
    defect=(
        "STEP file from non-C locale uses comma as decimal separator; "
        "CARTESIAN_POINT('',(1,5,2,5,3,5)) intended as (1.5, 2.5, 3.5); "
        "C-locale reader interprets as 6 separate integers shifting parameters; "
        "misalignment crashes geometry builder; "
        "OCCT MANTIS#0024759; See also Le023; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))   # #1 (uses dot separator — valid)
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")  # #2
f.add_product_chain(gcs)

# Attack payload 1: CARTESIAN_POINT with comma decimal separators.
# In Czech/German locale '1,5' means 1.5; the STEP reader running under
# C locale sees 6 integers instead of 3 floats.
# Satisfies:
#   matches(rb"CARTESIAN_POINT\([^;]*,\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*\d+")
#   count(b',') >= 5
#   matches(rb'\(\d+,\d+,\d+,\d+,\d+,\d+\)')
f._emit_raw("CARTESIAN_POINT('locale_comma_1',(1,5,2,5,3,5))")

# Attack payload 2: a second point to ensure the pattern appears twice and
# that the parameter-shift misalignment can cascade across entity boundaries.
f._emit_raw("CARTESIAN_POINT('locale_comma_2',(0,0,1,0,0,0))")

# Attack payload 3: DIRECTION with comma decimal separators.
# A unit direction like (0,7071068,0,7071068,0,0) for (0.707…, 0.707…, 0.0).
f._emit_raw("DIRECTION('locale_dir',(0,7071068,0,7071068,0,0))")

# Attack payload 4: scalar VECTOR magnitude also from non-C locale.
# '1,5' is intended as magnitude 1.5.
f._emit_raw(f"VECTOR('locale_vec',#{origin.eid},1,5)")
