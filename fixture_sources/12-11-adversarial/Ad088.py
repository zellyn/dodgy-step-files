"""Ad088 — Crash on reading STEP with malformed parameter values.

Catalog claim: a STEP entity's numeric parameter contains a malformed value;
empty string where a number is expected, comma-separated triple where two are
expected, scientific notation with non-digit exponent. Reader's
parameter-conversion crashes via an out-of-range error or uncaught
numeric-parse exception.

Reproducer recipe:
  CARTESIAN_POINT('',(1.0, , 3.0))     — empty middle parameter
  CARTESIAN_POINT('',(1.0,2.0,3.0,4.0)) — extra value
  LINE with VECTOR magnitude '1e+'      — incomplete exponent

Byte assertions:
  matches(rb'CARTESIAN_POINT\\([^;]*,\\s*,') or matches(rb'CARTESIAN_POINT\\([^;]*\\([^)]*,\\s*,[^)]*\\)')
  matches(rb'\\(\\s*\\d+\\.0\\s*,\\s*,')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad088",
    defect=(
        "malformed parameter values in STEP entities; "
        "CARTESIAN_POINT with empty middle parameter (1.0, , 3.0); "
        "CARTESIAN_POINT with extra 4th coordinate (arity overflow); "
        "LINE VECTOR magnitude '1e+' (incomplete scientific-notation exponent); "
        "reader parameter-conversion crashes via out-of-range or parse exception; "
        "OCCT MANTIS#0030876, #0029362, #0029240, #0033631; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))   # #1
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")  # #2
f.add_product_chain(gcs)

# Attack payload 1: CARTESIAN_POINT with empty middle parameter.
# Satisfies: matches(rb'CARTESIAN_POINT\([^;]*,\s*,')
#            matches(rb'\(\s*\d+\.0\s*,\s*,')
f._emit_raw("CARTESIAN_POINT('empty_middle',(1.0, , 3.0))")

# Attack payload 2: CARTESIAN_POINT with extra 4th coordinate (arity mismatch).
# ISO 10303-21 CARTESIAN_POINT takes exactly 3 coords; extra coord triggers
# parameter-consumer off-by-one on the next entity boundary.
f._emit_raw("CARTESIAN_POINT('extra_coord',(1.0,2.0,3.0,4.0))")

# Attack payload 3: LINE whose VECTOR has magnitude '1e+' (incomplete exponent).
# Satisfies: (numeric parse exception path)
bad_dir = f._emit_raw("DIRECTION('bad_dir',(0.0,0.0,1.0))")
bad_vec = f._emit_raw(f"VECTOR('bad_magnitude',#{bad_dir.eid},1e+)")
f._emit_raw(f"LINE('bad_line',#{origin.eid},#{bad_vec.eid})")

# Attack payload 4: second empty-middle variant to ensure both byte assertions
# are simultaneously satisfiable.
f._emit_raw("CARTESIAN_POINT('empty_mid2',(0.0, ,0.0))")
