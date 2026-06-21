"""Ad086 — Translator silently masks segfault-class faults as "transfer failed".

Catalog claim: a translator catches all exceptions at the per-entity boundary
and downgrades them uniformly to a "transfer failed" status, hiding
memory-corruption-class faults. Attack shape: combined type-confusion and
overflow attributes —
  - AXIS2_PLACEMENT_3D whose location slot points at a PRODUCT_DEFINITION
    instead of a CARTESIAN_POINT;
  - CARTESIAN_POINT with only 2 coordinates (arity mismatch);
  - CARTESIAN_POINT with coordinate 1.0E+999 (numeric overflow);
  - LINE whose direction VECTOR references a CARTESIAN_POINT where DIRECTION
    is required.

Reproducer recipe: any input that triggers an access-violation in translator.

Byte assertions:
  contains(b'ISO-10303-21')
  contains(b'END-ISO-10303-21')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad086",
    defect=(
        "translator silently masks segfault-class faults as 'transfer failed'; "
        "AXIS2_PLACEMENT_3D.location → PRODUCT_DEFINITION (type confusion); "
        "CARTESIAN_POINT with 2-coord arity mismatch; "
        "CARTESIAN_POINT with coordinate 1.0E+999 (overflow); "
        "LINE direction VECTOR references CARTESIAN_POINT where DIRECTION required; "
        "Q078; R073; See also Ad043; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))   # #1
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")  # #2

# All attack payloads are emitted BEFORE add_product_chain so that their
# references to well-known product-chain IDs (#9001, #9003) are forward refs.

# Attack payload 1 (Q078/a): CARTESIAN_POINT with only 2 coords (arity mismatch).
f._emit_raw("CARTESIAN_POINT('arity_mismatch',(1.0,2.0))")     # #3

# Attack payload 2 (Q078/b): CARTESIAN_POINT with numeric overflow coordinate.
f._emit_raw("CARTESIAN_POINT('overflow_coord',(1.0E+999,0.0,0.0))")  # #4

# Attack payload 3 (Q078/c): PRODUCT_DEFINITION used as a wrong-type location.
# add_product_chain emits the PRODUCT_DEFINITION at #9001; we forward-ref it.
f._emit_raw(
    "AXIS2_PLACEMENT_3D('type_confused_loc',#9001,$,$)"         # #5
)

# Attack payload 4 (Q078/d): CARTESIAN_POINT used where DIRECTION is required.
wrong_type_pt = f._emit_raw(
    "CARTESIAN_POINT('wrong_type_for_dir',(1.0,0.0,0.0))"      # #6
)

# VECTOR referencing the CARTESIAN_POINT where a DIRECTION is required.
bad_vec = f._emit_raw(
    f"VECTOR('bad_dir_ref',#{wrong_type_pt.eid},1.0)"           # #7
)

# LINE using the mis-typed VECTOR; its point ref is #1 (origin, correct type).
f._emit_raw(
    f"LINE('type_confused_line',#{origin.eid},#{bad_vec.eid})"  # #8
)

# Canonical PRODUCT chain (IDs 9000+); the PRODUCT_DEFINITION at #9001 is
# referenced by the AXIS2_PLACEMENT_3D above as a type-confusion forward ref.
f.add_product_chain(gcs)
