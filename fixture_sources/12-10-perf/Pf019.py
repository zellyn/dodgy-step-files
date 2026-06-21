"""Pf019 — Memory leaks in STEP/IGES controller initialisation enum tables.

Catalog claim: LeakSanitizer flags allocations originating from the static
enum-table initialisation triggered by the STEP/IGES controller constructor;
static singletons are retained on shutdown rather than freed at exit.

The structural pattern that exercises the controller initialisation path is a
STEP file whose parse requires the controller to build its full typed-value
enum tables: multiple entity types with enumeration attributes, spread across
a GEOMETRIC_CURVE_SET so OCC yields empty/empty.  The presence of several
distinct typed entities (CARTESIAN_POINT, DIRECTION, LINE, VECTOR) forces the
controller to populate the complete enum table for each type, exactly the
allocation path that LeakSanitizer flags on shutdown.

Byte assertion: count_entity_def(b'CARTESIAN_POINT') >= 1
Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pf019",
    defect=(
        "controller static enum-table initialisation: DIRECTION + LINE + VECTOR "
        "typed entities force full enum-table population; singletons retained on "
        "shutdown — LeakSanitizer flags on exit; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Anchor: GEOMETRIC_CURVE_SET so OCC yields empty/empty.
anchor = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{anchor.eid}))")
f.add_product_chain(gcs)

# Several typed entities to force enum-table population for each type.
# The variety of entity types is the key structural pattern.
pts = [f.cartesian_point((float(i), 0.0, 0.0)) for i in range(1, 5)]
dirs = [
    f.direction((1.0, 0.0, 0.0)),
    f.direction((0.0, 1.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
]
vecs = [f.vector(dirs[i % 3], float(i + 1)) for i in range(3)]
lines = [f._emit_raw(f"LINE('enum_line_{i}',#{pts[i].eid},#{vecs[i % 3].eid})")
         for i in range(3)]

# All items in a secondary GEOMETRIC_CURVE_SET (not the product-chain one)
# to materialise the entity references in the file.
all_refs = (
    [f"#{p.eid}" for p in pts]
    + [f"#{d.eid}" for d in dirs]
    + [f"#{v.eid}" for v in vecs]
    + [f"#{ln.eid}" for ln in lines]
)
f._emit_raw(f"GEOMETRIC_CURVE_SET('enum_table_set',({','.join(all_refs)}))")
