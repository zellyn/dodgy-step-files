"""Ad094 — Shell translator dereferences null on empty face list.

Catalog claim: a CONNECTED_FACE_SET or OPEN_SHELL entity contains an empty
face list (()). The shell-translator iterates the face list expecting at
least one element, dereferences a null pointer on the first iteration.

Reproducer recipe: STEP file with OPEN_SHELL('',()) (zero-face shell).

Byte assertions:
  matches(rb"OPEN_SHELL\\('[^']*',\\(\\)\\)")
  matches(rb'\\(\\)\\)')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad094",
    defect=(
        "OPEN_SHELL with empty face list (()) causes null dereference in "
        "shell-translator; translator iterates face list expecting >= 1 element; "
        "first-iteration null dereference produces OOB read, junk attributes, or crash; "
        "must diagnose malformed shell and skip without crashing; "
        "OCCT MANTIS#0033312, #0023938, #0024517; See also Tsh023, Tsh024; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Attack payload 1: OPEN_SHELL with an empty face list.
# Satisfies:
#   matches(rb"OPEN_SHELL\('[^']*',\(\)\)")
#   matches(rb'\(\)\)')
f._emit_raw("OPEN_SHELL('zero_face_shell',())")

# Attack payload 2: CLOSED_SHELL with an empty face list (same class of bug).
f._emit_raw("CLOSED_SHELL('zero_face_closed',())")

# Attack payload 3: CONNECTED_FACE_SET variant.
f._emit_raw("CONNECTED_FACE_SET('zero_face_cfs',())")
