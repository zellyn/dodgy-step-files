"""Ad050 — Empty EDGE_LOOP / empty wire / empty entity iterator crashes reader.

Catalog claim: schema requires non-empty list; producer emits '()'.  Reader's
iterator-step crashes on empty.

Reproducer recipe: #1=EDGE_LOOP('',()); referenced from FACE_BOUND.

Byte assertions:
  matches(rb"EDGE_LOOP\\('[^']*',\\(\\)\\)")
  contains(b'EDGE_LOOP')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad050",
    defect=(
        "empty EDGE_LOOP: EDGE_LOOP('',()) with zero oriented edges; "
        "schema requires non-empty list; reader iterator-step crashes on empty; "
        "FACE_BOUND referencing the empty loop exposes the null-deref; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Attack payload 1: EDGE_LOOP with empty edge list.
# Satisfies: matches(rb"EDGE_LOOP\('[^']*',\(\)\)")
# and: contains(b'EDGE_LOOP')
empty_loop = f._emit_raw("EDGE_LOOP('',())")

# Attack payload 2: FACE_BOUND referencing the empty loop.
# This creates the reader-path that dereferences the empty iterator.
empty_fbound = f._emit_raw(f"FACE_BOUND(#{empty_loop.eid},.T.)")

# Attack payload 3: A second empty EDGE_LOOP variant (named) to stress
# the iterator across multiple code paths.
empty_loop2 = f._emit_raw("EDGE_LOOP('empty_wire',())")

# Attack payload 4: FACE_OUTER_BOUND also referencing empty loop — exercises
# the outer-bound iterator path (bug33307 / bug25014 class).
f._emit_raw(f"FACE_OUTER_BOUND(#{empty_loop2.eid},.T.)")

# Attack payload 5: TESSELLATED_SHELL with empty list (I004 variant).
f._emit_raw("TESSELLATED_SHELL('',(),$)")
