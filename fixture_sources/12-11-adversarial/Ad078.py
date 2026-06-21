"""Ad078 — NEXT_ASSEMBLY_USAGE_OCCURRENCE child as PRODUCT_DEFINITION_SHAPE (mis-typed select).

Catalog claim: NAUO can refer to either PRODUCT_DEFINITION or
PRODUCT_DEFINITION_SHAPE; schema-strict reader rejected the latter, while
permissive reader cast across vtables. Fix: warn and accept PDS child,
resolve PDS→PD silently with diagnostic.

Reproducer recipe: NEXT_ASSEMBLY_USAGE_OCCURRENCE whose 'related' (child)
slot references a PRODUCT_DEFINITION_SHAPE entity instead of a
PRODUCT_DEFINITION.

Byte assertions:
  count_entity_def(b'NEXT_ASSEMBLY_USAGE_OCCURRENCE') >= 1 and contains(b'PRODUCT_DEFINITION_SHAPE')
  contains(b'NEXT_ASSEMBLY_USAGE_OCCURRENCE')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad078",
    defect=(
        "type-confusion: NAUO child slot references PRODUCT_DEFINITION_SHAPE "
        "instead of PRODUCT_DEFINITION; schema-strict reader rejects, "
        "permissive reader casts across vtables; "
        "kernel must warn and resolve PDS→PD silently; "
        "Mantis 0025167 (G016); R049; See also Ad030; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Attack payload: NEXT_ASSEMBLY_USAGE_OCCURRENCE whose related (child) slot
# references a PRODUCT_DEFINITION_SHAPE instead of a PRODUCT_DEFINITION.
#
# A minimal assembly chain:
#   PRODUCT → PRODUCT_DEFINITION_FORMATION → PRODUCT_DEFINITION (parent PD)
#   PRODUCT_DEFINITION_SHAPE (child PDS) — this is the mis-typed select
#   NEXT_ASSEMBLY_USAGE_OCCURRENCE(parent PD, child PDS)
#
# The product chain placed by add_product_chain uses IDs 9000+; we emit
# the attack entities after that block.

prod_a = f._emit_raw("PRODUCT('part_a','part_a','',())")
prod_def_form_a = f._emit_raw(
    f"PRODUCT_DEFINITION_FORMATION('','',#{prod_a.eid})"
)
# Parent is a proper PRODUCT_DEFINITION.
pd_parent = f._emit_raw(
    f"PRODUCT_DEFINITION('parent','',#{prod_def_form_a.eid},#9003)"
)

prod_b = f._emit_raw("PRODUCT('part_b','part_b','',())")
prod_def_form_b = f._emit_raw(
    f"PRODUCT_DEFINITION_FORMATION('','',#{prod_b.eid})"
)
pd_child_base = f._emit_raw(
    f"PRODUCT_DEFINITION('child_pd','',#{prod_def_form_b.eid},#9003)"
)
# The mis-typed child: a PRODUCT_DEFINITION_SHAPE that wraps the PD.
# Satisfies: contains(b'PRODUCT_DEFINITION_SHAPE')
pds_child = f._emit_raw(
    f"PRODUCT_DEFINITION_SHAPE('','',#{pd_child_base.eid})"
)

# NAUO with parent=PD (correct) and related=PDS (mis-typed).
# Satisfies: count_entity_def(b'NEXT_ASSEMBLY_USAGE_OCCURRENCE') >= 1
#            contains(b'NEXT_ASSEMBLY_USAGE_OCCURRENCE')
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('nauo_mistype','','',#{pd_parent.eid},#{pds_child.eid},$)"
)
