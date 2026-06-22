"""Ad026 — Self-referencing complex-entity instance during construction.

Catalog claim: #1=(A() B(#1)); sub-entity references outer instance during
construction. Two-phase build that derefs #1 while still constructing →
half-initialised vtable use (UAF in C++).

Byte assertions:
  matches(rb'(?s)#(\\d+)=\\([^;]*#\\1[^;]*\\);')
  matches(rb'#\\d+=\\(')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad026",
    defect=(
        "self-referencing complex entity during construction; "
        "#N=(A() B(#N)) — sub-entity references outer instance; "
        "vtable use before init → UAF; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Attack payloads:
# Pattern A: simple self-reference inside complex entity.
# Satisfies matches(rb'(?s)#(\d+)=\([^;]*#\1[^;]*\);') and matches(rb'#\d+=\(').
self_id = f._next_id
f._emit_raw(f"(NAMED_UNIT(*) DERIVED_UNIT_ELEMENT(#{self_id}, 1.0))")

# Pattern B: self-reference via COMPOSITE_CURVE_SEGMENT list
# (OCCT Q023 composite curve self-cyclic variant).
cc_id = f._next_id
seg_id = cc_id + 1
f._emit_raw(f"COMPOSITE_CURVE('',(#{seg_id}),.F.)")
f._emit_raw(f"COMPOSITE_CURVE_SEGMENT(.CONTINUOUS.,.T.,#{cc_id})")

# Pattern C: complex entity with self-reference in BOTH sub-entities.
# Another instance satisfying the self-ref regex.
complex_self_id = f._next_id
f._emit_raw(
    f"(GEOMETRIC_REPRESENTATION_ITEM()"
    f" REPRESENTATION_ITEM('self')"
    f" STYLED_ITEM('',(#{complex_self_id}),#{complex_self_id}))"
)
