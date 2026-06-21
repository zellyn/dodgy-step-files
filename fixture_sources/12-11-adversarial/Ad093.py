"""Ad093 — Empty / null input file path causes crash.

Catalog claim: a STEP reader is invoked with empty or null filename (e.g.,
`stepread ''` from a script). Reader does not validate input, attempts to open
file, fails, and crashes during cleanup of partially initialised state.

Reproducer recipe: invoke reader with empty filename `""` or null path.

Provenance tier: runtime-only; there is no `.stp` to author; the defect is
triggered by an empty or null path passed to the reader API, which fails before
any file content is read. Demonstrating this requires invoking the reader with
bad arguments, not a fixture file. This fixture is a companion file that
documents the defect pattern and satisfies the byte assertions.

Byte assertions:
  contains(b'ISO-10303-21')
  contains(b'END-ISO-10303-21')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad093",
    defect=(
        "reader invoked with empty or null filename crashes during cleanup; "
        "reader must validate filename at entry and reject empty/null path; "
        "defect is runtime-only (no .stp to author); "
        "this fixture is a companion file documenting the defect pattern; "
        "OCCT MANTIS#0024246, #0032115; See also Ad082; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
# The rendered output satisfies contains(b'ISO-10303-21') and
# contains(b'END-ISO-10303-21') via the standard STEP file header/trailer.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Companion payload: document the defect trigger pattern as STEP comments.
# A well-formed file that passes structural checks but whose defect cannot
# be exercised without a test harness calling the reader with empty path.
f._emit_raw("/* empty-path trigger: reader_api.read('') */\n/* null-path trigger: reader_api.read(None) */\nCARTESIAN_POINT('probe',(0.0,0.0,0.0))")
