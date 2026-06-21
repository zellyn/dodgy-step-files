"""Ad049 — Real literal lacks decimal point or has Fortran D exponent.

Catalog claim: per spec, REAL must have '.'; exponent is uppercase 'E';
integers may not have leading '.'.  Generators emit '1', '.5', '1e+18',
'1.0D5', '+1.0', '1_000.0', '1,5' (locale comma), '0x10' (hex).  Stepcode
silently coerces INTEGER→REAL via istringstream, hiding unit-corruption bugs.

Reproducer recipe: IFCDIRECTION((1,0,0)), IFCDIRECTION((1.0D5,0.,0.)),
IFCREAL(1_000.0).

Byte assertions:
  contains(b'1_000.0') or contains(b'1.5e+02') or contains(b'1.0D5') or matches(rb'\\(\\s*1\\s*,\\s*0\\s*,')
  matches(rb'1\\.5e\\+02|1\\.0D5|1_000\\.0|\\(1,0,0\\)')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad049",
    defect=(
        "malformed REAL literals: '1.0D5' (Fortran D-exponent), '1_000.0' "
        "(underscore separator), '1.5e+02' (lowercase e), '(1,0,0)' (INTEGER "
        "coordinates without decimal point); Stepcode silently coerces "
        "INTEGER→REAL hiding unit-corruption bugs; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Attack payload 1: DIRECTION with INTEGER coordinate values (no decimal point).
# Satisfies: matches(rb'\(\s*1\s*,\s*0\s*,') and matches(rb'\(1,0,0\)')
f._emit_raw("DIRECTION('integer_coords',(1,0,0))")

# Attack payload 2: DIRECTION with Fortran D-exponent (1.0D5).
# Satisfies: matches(rb'1\.0D5')
f._emit_raw("DIRECTION('fortran_d_exp',(1.0D5,0.,0.))")

# Attack payload 3: DIRECTION with underscore numeric separator (1_000.0).
# Satisfies: contains(b'1_000.0')
f._emit_raw("DIRECTION('underscore_sep',(1_000.0,0.0,0.0))")

# Attack payload 4: DIRECTION with lowercase-e exponent (1.5e+02).
# Satisfies: matches(rb'1\.5e\+02')
f._emit_raw("DIRECTION('lowercase_e_exp',(1.5e+02,0.0,0.0))")

# Attack payload 5: CARTESIAN_POINT with INTEGER coordinates — no decimal point.
# Reinforces the integer-as-real coercion path.
f._emit_raw("CARTESIAN_POINT('int_point',(0,0,0))")
