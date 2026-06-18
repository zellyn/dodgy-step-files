"""Bo002 — MANIFOLD_SOLID_BREP with dangling shell reference.

Catalog claim: "A MANIFOLD_SOLID_BREP whose `outer` slot is an entity
reference to a non-existent or null shell; there is no shell entity in the
data section at all."

Demonstration: emit a MANIFOLD_SOLID_BREP whose outer references DanglingRef
(entity #999 which is never defined). The file has the correct PRODUCT chain
so OCCT loads it, but the solid body itself has no shell. A strict Part-21
parser rejects with E_UNRESOLVED_REFS; OCCT produces an empty/null shape.
"""
from step_corpus.step_builder import StepFile, DanglingRef

f = StepFile(catalog_id="Bo002",
             defect="MANIFOLD_SOLID_BREP outer points to non-existent shell entity #999")

# The only geometry entity is the MANIFOLD_SOLID_BREP itself.
# Its outer slot points to #999 — a shell entity that is never defined anywhere
# in the DATA section. This is the dangling reference defect.
dangling_shell = DanglingRef(999)
solid = f.manifold_solid_brep(dangling_shell, name="dangling_solid")

# Add the product chain. Use brep_shape mode so OCCT tries to reach the solid.
# The outer being a DanglingRef means the manifold_solid_brep method receives
# something that isn't an Entity, bypassing the OPEN_SHELL warning check —
# which is correct, the defect here is that the shell doesn't exist at all.
f.add_product_chain(solid, mode="brep_shape")
