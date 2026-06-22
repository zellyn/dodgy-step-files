"""Ad030 — Type-confusion via mis-typed reference (CARTESIAN_POINT used as DIRECTION).

Catalog claim: schema-driven late binding takes entity from instance table
and casts without dynamic-type check; downstream geometry code dereferences
via wrong-type vtable → UAF / RCE.

Reproducer recipe: declare #10=CARTESIAN_POINT(..); reference #10 in a slot
whose schema-required type is DIRECTION.

Byte assertions:
  matches(rb'(?s)#10=CARTESIAN_POINT.*=DIRECTION\\([^;]*#10') or matches(rb'(?s)CARTESIAN_POINT.*LINE\\([^;]*,#10\\)')
  contains(b'CARTESIAN_POINT') and contains(b'DIRECTION')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad030",
    defect=(
        "type-confusion: #10=CARTESIAN_POINT used in DIRECTION slot; "
        "schema-driven late binding without dynamic-type check → wrong-type vtable deref; "
        "primary RCE class for STEP CVEs 2024-2026; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Attack payload:
# We need #10=CARTESIAN_POINT and then a DIRECTION or LINE referencing #10.
# The PRODUCT chain uses IDs ≥ 9000; normal IDs restart at f._next_id after
# the chain.  Force f._next_id to 10 to land the attack entity at #10.
# (IDs 3-9 are gaps — legal in Part-21: instance table is sparse.)
f._next_id = 10
cp_attack = f._emit_raw("CARTESIAN_POINT('',(1.0,2.0,3.0))")
# cp_attack.eid == 10

# DIRECTION whose ratios argument contains the CARTESIAN_POINT ref (type confusion).
# Satisfies: matches(rb'(?s)#10=CARTESIAN_POINT.*=DIRECTION\([^;]*#10')
f._emit_raw(f"DIRECTION('type_confused_dir',(#{cp_attack.eid},0.,0.))")

# LINE whose second argument (direction vector, must be VECTOR) is #10 (CARTESIAN_POINT).
# Satisfies the OR arm: matches(rb'(?s)CARTESIAN_POINT.*LINE\([^;]*,#10\)')
f._emit_raw(f"LINE('type_confused_line',#{origin.eid},#{cp_attack.eid})")

# Extra DIRECTION reference to guarantee contains(b'DIRECTION').
f._emit_raw(f"DIRECTION('wrong_type_slot',(#{cp_attack.eid},1.,0.))")
