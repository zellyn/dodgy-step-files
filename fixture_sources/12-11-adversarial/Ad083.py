"""Ad083 — Multiple PRODUCTs share the same name; only NEXT_ASSEMBLY_USAGE_OCCURRENCE id disambiguates.

Catalog claim: multiple child PRODUCT instances share the same name attribute
across distinct PRODUCT_DEFINITION chains — for example three boards each named
'R0402' — and only the NEXT_ASSEMBLY_USAGE_OCCURRENCE id slot ('R1', 'R2', 'R3')
disambiguates them. KiCad-style sources reuse one PRODUCT for many NAUOs;
receiver dictionaries keyed on name instead of NAUO id collide and drop siblings.

Reproducer recipe: three PRODUCT entities all named 'R0402', each with its own
PRODUCT_DEFINITION chain, linked to a parent via three separate
NEXT_ASSEMBLY_USAGE_OCCURRENCEs with ids 'R1', 'R2', 'R3'.

Byte assertions:
  count_entity_def(b'NEXT_ASSEMBLY_USAGE_OCCURRENCE') >= 3
  count(b"'R") >= 3 or count_entity_def(b'NEXT_ASSEMBLY_USAGE_OCCURRENCE') >= 3

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad083",
    defect=(
        "multiple PRODUCT instances share the same name 'R0402'; "
        "only NEXT_ASSEMBLY_USAGE_OCCURRENCE id ('R1','R2','R3') disambiguates; "
        "receivers keyed on name instead of NAUO id collide and drop siblings; "
        "KiCad/CadQuery assembly flat-load label collision; "
        "CadQuery #1962; I021; I077; R057; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Attack payload: assembly with a parent product and three child products all
# named 'R0402', each linked by a separate NAUO with distinct id slots.
#
# Parent product chain
prod_parent = f._emit_raw("PRODUCT('Assembly','Assembly','',())")
pdf_parent = f._emit_raw(
    f"PRODUCT_DEFINITION_FORMATION('','',#{prod_parent.eid})"
)
pd_parent = f._emit_raw(
    f"PRODUCT_DEFINITION('','',#{pdf_parent.eid},#9003)"
)

# Three children all named 'R0402', disambiguated only by NAUO id.
# Satisfies: count(b"'R") >= 3
for nauo_id in ("R1", "R2", "R3"):
    prod_child = f._emit_raw("PRODUCT('R0402','R0402','',())")
    pdf_child = f._emit_raw(
        f"PRODUCT_DEFINITION_FORMATION('','',#{prod_child.eid})"
    )
    pd_child = f._emit_raw(
        f"PRODUCT_DEFINITION('','',#{pdf_child.eid},#9003)"
    )
    # Satisfies: count_entity_def(b'NEXT_ASSEMBLY_USAGE_OCCURRENCE') >= 3
    f._emit_raw(
        f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('{nauo_id}','','',#{pd_parent.eid},#{pd_child.eid},$)"
    )
