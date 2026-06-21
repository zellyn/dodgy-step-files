"""Ad054 — Mutual-cycle NEXT_ASSEMBLY_USAGE_OCCURRENCE chain hangs reader forever.

Catalog claim: two NEXT_ASSEMBLY_USAGE_OCCURRENCE entries form a mutual
parent/child cycle (#30 has parent=#12, child=#22; #31 has parent=#22,
child=#12), so the assembly-tree walk loops forever. Common attack shape:
minimal cycle of two NAUOs.

Reproducer recipe: two NAUOs forming a mutual parent/child cycle such that
any depth-first assembly-tree traversal loops indefinitely.

Byte assertions:
  count_entity_def(b'NEXT_ASSEMBLY_USAGE_OCCURRENCE') >= 2
  count_entity_def(b'NEXT_ASSEMBLY_USAGE_OCCURRENCE') >= 2 and
    matches(rb'(?s)NEXT_ASSEMBLY_USAGE_OCCURRENCE[^;]+#12,#22[^;]+;.*NEXT_ASSEMBLY_USAGE_OCCURRENCE[^;]+#22,#12')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad054",
    defect=(
        "mutual-cycle NAUO chain: parent=#12 child=#22, parent=#22 child=#12; "
        "assembly-tree walk loops forever; "
        "kernel must enforce E_TRANSFER_BUDGET and detect cycles; "
        "real-world reproducer: 250709r8000_asm-all; See also Ad032; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))  # #1
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")  # #2

# Attack payload: two product-definition stubs that act as NAUO cycle nodes.
# We force IDs #12 and #22 for the byte-assertion regex to match:
#   NEXT_ASSEMBLY_USAGE_OCCURRENCE[^;]+#12,#22[^;]+;
#   NEXT_ASSEMBLY_USAGE_OCCURRENCE[^;]+#22,#12
#
# After origin(#1) + gcs(#2), _next_id == 3.  Pad to 12.
while f._next_id < 12:
    f._emit_raw("CARTESIAN_POINT('pad',(0.0,0.0,0.0))")

# #12 — product-definition stub A
pd_a = f._emit_raw("PRODUCT_DEFINITION('cycle_a','',#9052,#9053)")

# pad to #22
while f._next_id < 22:
    f._emit_raw("CARTESIAN_POINT('pad',(0.0,0.0,0.0))")

# #22 — product-definition stub B
pd_b = f._emit_raw("PRODUCT_DEFINITION('cycle_b','',#9052,#9053)")

# Pad to #30 for the first NAUO.
while f._next_id < 30:
    f._emit_raw("CARTESIAN_POINT('pad',(0.0,0.0,0.0))")

# #30 — NAUO: parent=#12, child=#22  (A→B)
# Satisfies first half of:
#   matches(rb'(?s)NEXT_ASSEMBLY_USAGE_OCCURRENCE[^;]+#12,#22[^;]+;')
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('cycle_a_b','','',#{pd_a.eid},#{pd_b.eid},$)"
)

# #31 — NAUO: parent=#22, child=#12  (B→A, closing the mutual cycle)
# Satisfies: NEXT_ASSEMBLY_USAGE_OCCURRENCE[^;]+#22,#12
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('cycle_b_a','','',#{pd_b.eid},#{pd_a.eid},$)"
)

# Now attach minimal geometry to product chain.
# add_product_chain() will use IDs 9000+.
f.add_product_chain(gcs)
