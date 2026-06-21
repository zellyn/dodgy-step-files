"""Ad002 — Stack overflow via deeply nested aggregate parentheses.

Catalog claim: recursive descent over LIST/SET/BAG aggregates without a
depth bound; thousands of nested (((..))) blow the call stack long before
the inner literal is reached.

Byte assertions:
  max_paren_depth >= 50
  count(b'((((') >= 5

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad002",
    defect=(
        "deeply nested aggregate parentheses; "
        "~120 levels of (((..))) on FOO entity; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Attack payload: FOO entity with ~120 levels of nested parens.
# max_paren_depth >= 50 and count(b'((((') >= 5.
depth = 120
open_parens = "(" * depth
close_parens = ")" * depth
f._emit_raw(f"FOO({open_parens}0{close_parens})")
