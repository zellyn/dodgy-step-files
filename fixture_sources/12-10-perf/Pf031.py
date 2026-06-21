"""Pf031 — STEP read parsing slow due to single-pass tokenisation.

Catalog claim: a STEP reader's parser reads each character in single-byte
fashion through a buffered stream; for a 100 MB file this issues hundreds of
millions of OS read calls, dominating runtime. The fixture is a scaled-down
representative with ~30 CARTESIAN_POINTs; replicate to ~10^6 to reproduce the
production-scale 100 MB I/O-dominated parse.

Byte assertion: count_entity_def(b'CARTESIAN_POINT') >= 29
Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pf031",
    defect=(
        "STEP read parsing slow due to single-pass tokenisation: parser issues one read "
        "syscall per character; 100 MB file with millions of small entities causes hundreds "
        "of millions of OS read calls; heal: use bulk-buffered I/O or memory-mapped input; "
        "scaled-down representative with 30 CARTESIAN_POINTs — replicate to 10^6 for "
        "production scale; GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Emit 30 CARTESIAN_POINTs in a 3x10 grid to represent the "millions of small entities"
# density pattern at fixture scale.
pts = []
for row in range(3):
    for col in range(10):
        pts.append(f.cartesian_point((float(col), float(row), 0.0)))

# GEOMETRIC_CURVE_SET as product entity so OCC yields empty
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{pts[0].eid}))")
f.add_product_chain(gcs)
