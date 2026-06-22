"""Ad087 — STEP reader crashes on unresolved entity reference.

Catalog claim: a STEP file references an entity ID (#999) that is not present
in the file (the producer truncated the file or omitted the record).
Reader's TransferRoots follows the reference, dereferences a null pointer, and
crashes. Cross-oracle: pure-Python Part-21 validator rejects
(reject(E_UNRESOLVED_REFS)); OCCT silently accepts with empty result.

Reproducer recipe: MANIFOLD_SOLID_BREP (or similar entity) that references
#999 but #999 is undefined in the DATA section.

Byte assertions:
  contains(b'#999')
  matches(rb'#\\d+=[^;]*#999')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad087",
    defect=(
        "dangling reference to #999 (entity never defined); "
        "TransferRoots dereferences null pointer on unresolved reference; "
        "cross-oracle: Part-21 validator → reject(E_UNRESOLVED_REFS); "
        "OCCT silently accepts with empty result; "
        "MANTIS#0033487, #0033665, #0033603, #0032314; See also Ad078; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Attack payload 1: MANIFOLD_SOLID_BREP whose outer shell ref is #999
# (entity #999 is never declared in this file).
# Satisfies: contains(b'#999') and matches(rb'#\d+=[^;]*#999')
f._emit_raw(
    "MANIFOLD_SOLID_BREP('dangling_brep',#999)"
)

# Attack payload 2: SHAPE_REPRESENTATION referencing #999 in its items list.
# Satisfies: matches(rb'#\d+=[^;]*#999') (second match for robustness)
f._emit_raw(
    "SHAPE_REPRESENTATION('dangling_rep',(#999),#9010)"
)

# Attack payload 3: FACE_OUTER_BOUND → EDGE_LOOP → dangling #999.
# Tests that cycle of null-dereferences along the topology chain also crashes.
f._emit_raw(
    "FACE_OUTER_BOUND('dangling_bound',#999,.T.)"
)

# Attack payload 4: NEXT_ASSEMBLY_USAGE_OCCURRENCE with dangling related (#999).
# Tests assembly-transfer path for the same null-deref class.
f._emit_raw(
    "NEXT_ASSEMBLY_USAGE_OCCURRENCE('n1','','',#9001,#999,$)"
)
