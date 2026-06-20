"""Bo001 — Outer shell of a solid is empty (zero faces).

Catalog claim: A MANIFOLD_SOLID_BREP (or BREP_WITH_VOIDS) references a
CLOSED_SHELL whose face list is empty. The solid has no boundary at all.

Mechanism IS the CLOSED_SHELL topology: the CLOSED_SHELL('outer',()) with
cfs_faces=() IS the outer shell of the MANIFOLD_SOLID_BREP. The empty face
list IS wired into the brep shell structure — there is no ADVANCED_FACE
anywhere in the file. A strict kernel must reject or produce an invalid solid.

Byte assertions:
  - matches(rb'CLOSED_SHELL\\s*\\(\\s*\\'[^\\']*\\'\\s*,\\s*\\(\\s*\\)\\s*\\)')
  - contains(b'MANIFOLD_SOLID_BREP')
  - count_entity_def(b'ADVANCED_FACE') == 0

Tier-3 assertion: load == "ok"  (OCCT silently accepts → shape(1))
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Bo001",
    defect=(
        "CLOSED_SHELL('outer',()) with zero faces IS the outer shell of "
        "MANIFOLD_SOLID_BREP; empty cfs_faces IS wired into brep shell topology; "
        "OCCT silently accepts (shape(1)) — strict kernels must reject"
    ),
)

# ── CATALOG MECHANISM: CLOSED_SHELL with empty face list ─────────────────────
# Byte assertion: matches(rb'CLOSED_SHELL\s*\(\s*\'[^\']*\'\s*,\s*\(\s*\)\s*\)')
# Byte assertion: contains(b'MANIFOLD_SOLID_BREP')
# Byte assertion: count_entity_def(b'ADVANCED_FACE') == 0
#
# The empty CLOSED_SHELL IS the outer shell of the solid — mechanism wired in.
shell = f._emit_raw("CLOSED_SHELL('outer',(  ))")
msb   = f._emit_raw(f"MANIFOLD_SOLID_BREP('empty_solid',#{shell.eid})")

f.add_product_chain(msb, mode="brep_shape")
