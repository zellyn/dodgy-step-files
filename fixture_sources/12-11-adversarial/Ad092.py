"""Ad092 — Crash reading large STEP file: exception during transfer.

Catalog claim: a STEP file containing several million entities exceeds internal
buffer / map sizes. Reader processes most of the file then crashes near the end
with an out-of-range exception in the entity-map rebuild.

Reproducer recipe: STEP file with many CARTESIAN_POINT entities (all with
distinct IDs); reader crashes during transfer phase.

Byte assertions:
  count_entity_def(b'CARTESIAN_POINT') >= 20
  count(b'#') >= 30

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad092",
    defect=(
        "large STEP file with many CARTESIAN_POINT entities exceeds internal "
        "buffer/map sizes; reader crashes near end with out-of-range exception "
        "in entity-map rebuild; dynamically-sized structures must be used; "
        "OCCT MANTIS#0028662, #0028256, #0029108, #0033377; See also Pf027; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))   # #1
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")  # #2
f.add_product_chain(gcs)

# Attack payload: emit many CARTESIAN_POINT entities with distinct IDs.
# The catalog byte assertion needs >= 20 CARTESIAN_POINTs and >= 30 '#'.
# We emit 50 distinct anonymous points (varied coords to avoid deduplication).
# Satisfies:
#   count_entity_def(b'CARTESIAN_POINT') >= 20  (50 > 20)
#   count(b'#') >= 30 (50 entity defs each have a '#', plus the ones above)
for i in range(50):
    x = float(i)
    y = float(i * 2)
    z = float(i * 3)
    f._emit_raw(f"CARTESIAN_POINT('pt{i:04d}',({x},{y},{z}))")
