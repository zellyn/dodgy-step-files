"""Pf032 — Reader hangs during XCAF tree build on deep assembly.

Catalog claim: XCAF document is built from a large STEP file with a deep assembly
tree. The XCAF builder iterates assembly nodes recursively; for an N-level tree
with M instances per level, it visits every instance N times — exponential.
Apparent hang on files with deep assemblies. Scaled-down representative: 3 levels
x 2 instances per level (8 NAUO chain links).

Byte assertion: contains(b'NEXT_ASSEMBLY_USAGE_OCCURRENCE')
Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pf032",
    defect=(
        "Reader hangs during XCAF tree build on deep assembly: XCAF builder recurses "
        "assembly nodes and visits every instance N times for N-level trees; exponential "
        "without memoization; production scale: 8 levels x 10 instances = 10^8 visits; "
        "heal: memoize visited nodes, coerce visit count to linear in distinct nodes; "
        "scaled-down: 3 levels x 2 instances per level; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Root product
anchor = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{anchor.eid}))")
f.add_product_chain(gcs)

# Build the deep assembly chain via NEXT_ASSEMBLY_USAGE_OCCURRENCE.
# 3 levels x 2 children per level.
# After add_product_chain, the root PRODUCT_DEFINITION is at eid 9054.
root_pdef_eid = 9054

def make_child_pdef(name: str) -> int:
    """Create PRODUCT + PDF + PDEF chain and return the PDEF eid."""
    ap_ctx = f._emit_raw(f"APPLICATION_CONTEXT('automotive_design')")
    p_ctx  = f._emit_raw(f"PRODUCT_CONTEXT('',#{ap_ctx.eid},'mechanical')")
    prod   = f._emit_raw(f"PRODUCT('{name}','{name}','',(#{p_ctx.eid}))")
    pdf    = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{prod.eid})")
    pdc    = f._emit_raw(f"PRODUCT_DEFINITION_CONTEXT('',#{ap_ctx.eid},'design')")
    pdef   = f._emit_raw(f"PRODUCT_DEFINITION('design','',#{pdf.eid},#{pdc.eid})")
    return pdef.eid


# Level 1: two children under root
l1a = make_child_pdef("L1A")
l1b = make_child_pdef("L1B")
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('1a','','',#{root_pdef_eid},#{l1a},$)"
)
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('1b','','',#{root_pdef_eid},#{l1b},$)"
)

# Level 2: two children under each L1
l2aa = make_child_pdef("L2AA")
l2ab = make_child_pdef("L2AB")
l2ba = make_child_pdef("L2BA")
l2bb = make_child_pdef("L2BB")
f._emit_raw(f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('2aa','','',#{l1a},#{l2aa},$)")
f._emit_raw(f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('2ab','','',#{l1a},#{l2ab},$)")
f._emit_raw(f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('2ba','','',#{l1b},#{l2ba},$)")
f._emit_raw(f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('2bb','','',#{l1b},#{l2bb},$)")

# Level 3: two children under each L2
for parent, label in [(l2aa,"aa"),(l2ab,"ab"),(l2ba,"ba"),(l2bb,"bb")]:
    c1 = make_child_pdef(f"L3{label}A")
    c2 = make_child_pdef(f"L3{label}B")
    f._emit_raw(f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('3{label}a','','',#{parent},#{c1},$)")
    f._emit_raw(f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('3{label}b','','',#{parent},#{c2},$)")
