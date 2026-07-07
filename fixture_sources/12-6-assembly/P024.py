"""P024 — Flattened sub-assembly hierarchy after merge.

Catalog claim: Two STEP assembly files merged in a tree and re-exported emit
NEXT_ASSEMBLY_USAGE_OCCURRENCE chains that don't preserve the original product
hierarchy; receiver shows flattened/scrambled tree.

The defect: STEP assembly with PRODUCT_DEFINITION_USAGE graph that drops one
or more layers of sub-assembly grouping. A kernel must heal and accept,
preserving the original sub-assembly hierarchy across round-trip; silent empty
result is the bug.

Byte assertions:
  count_entity_def(b'NEXT_ASSEMBLY_USAGE_OCCURRENCE') >= 2
  count_entity_def(b'MAPPED_ITEM') == 2

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="P024",
    defect=(
        "NEXT_ASSEMBLY_USAGE_OCCURRENCE chain flattened after assembly merge; "
        "two assembly files merged in a tree and re-exported lose sub-assembly grouping; "
        "PRODUCT_DEFINITION_USAGE graph drops a hierarchy layer; "
        "receiver shows flattened/scrambled tree instead of nested sub-assembly; "
        "2 NAUO + 2 MAPPED_ITEM all pointing to parent without intermediate grouping; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
    schema="AP242",
)

# ── Minimal geometry payload so shape is empty ────────────────────────────────
origin_pt = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin_pt.eid}))")
f.add_product_chain(gcs)

# ── Shared assembly infrastructure ────────────────────────────────────────────
asm_origin = f._emit_raw("CARTESIAN_POINT('asm_origin',(0.0,0.0,0.0))")
asm_z = f._emit_raw("DIRECTION('asm_z',(0.0,0.0,1.0))")
asm_x = f._emit_raw("DIRECTION('asm_x',(1.0,0.0,0.0))")
asm_plc = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('asm_plc',#{asm_origin.eid},#{asm_z.eid},#{asm_x.eid})"
)

sub_pdc = f._emit_raw("PRODUCT_CONTEXT('sub',#9000,'mechanical')")

# ── The defect: two leaf components NAUOd directly to a single root, skipping
# the intermediate sub-assembly product that was lost in the merge. ────────────
# A correct hierarchy would be: Root -> SubAsm -> Leaf1, Leaf2.
# After flattening: Root -> Leaf1, Root -> Leaf2 (SubAsm layer gone).

# Root product (the top-level assembly, kept minimal as a reference).
root_prod = f._emit_raw(
    f"PRODUCT('RootAsm','RootAsm','Assembly root',(#{sub_pdc.eid}))"
)
root_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{root_prod.eid})")
root_pdef = f._emit_raw(
    f"PRODUCT_DEFINITION('design','',#{root_pdf.eid},#9053)"
)

# Leaf component 1 — should live inside a sub-assembly, but merge dropped that layer.
leaf1_prod = f._emit_raw(
    f"PRODUCT('LeafPart1','LeafPart1','First leaf (orphaned by merge)',(#{sub_pdc.eid}))"
)
leaf1_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{leaf1_prod.eid})")
leaf1_pdef = f._emit_raw(
    f"PRODUCT_DEFINITION('design','',#{leaf1_pdf.eid},#9053)"
)
leaf1_sr = f._emit_raw(
    f"SHAPE_REPRESENTATION('leaf1_rep',(#{asm_plc.eid}),#9060)"
)
leaf1_rm = f._emit_raw(f"REPRESENTATION_MAP(#{asm_plc.eid},#{leaf1_sr.eid})")
leaf1_inst_orig = f._emit_raw("CARTESIAN_POINT('leaf1_inst_orig',(0.0,0.0,0.0))")
leaf1_inst_z = f._emit_raw("DIRECTION('leaf1_inst_z',(0.0,0.0,1.0))")
leaf1_inst_x = f._emit_raw("DIRECTION('leaf1_inst_x',(1.0,0.0,0.0))")
leaf1_inst_plc = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('leaf1_inst_plc',"
    f"#{leaf1_inst_orig.eid},#{leaf1_inst_z.eid},#{leaf1_inst_x.eid})"
)
# MAPPED_ITEM #1 — count_entity_def(b'MAPPED_ITEM') == 2
f._emit_raw(f"MAPPED_ITEM('leaf1_mi',#{leaf1_rm.eid},#{leaf1_inst_plc.eid})")
# NEXT_ASSEMBLY_USAGE_OCCURRENCE #1 — links leaf directly to root (hierarchy lost).
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE("
    f"'1','leaf1_flat_instance','',#{root_pdef.eid},#{leaf1_pdef.eid},$)"
)

# Leaf component 2 — also flattened directly under root.
leaf2_prod = f._emit_raw(
    f"PRODUCT('LeafPart2','LeafPart2','Second leaf (orphaned by merge)',(#{sub_pdc.eid}))"
)
leaf2_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{leaf2_prod.eid})")
leaf2_pdef = f._emit_raw(
    f"PRODUCT_DEFINITION('design','',#{leaf2_pdf.eid},#9053)"
)
leaf2_sr = f._emit_raw(
    f"SHAPE_REPRESENTATION('leaf2_rep',(#{asm_plc.eid}),#9060)"
)
leaf2_rm = f._emit_raw(f"REPRESENTATION_MAP(#{asm_plc.eid},#{leaf2_sr.eid})")
leaf2_inst_orig = f._emit_raw("CARTESIAN_POINT('leaf2_inst_orig',(5.0,0.0,0.0))")
leaf2_inst_z = f._emit_raw("DIRECTION('leaf2_inst_z',(0.0,0.0,1.0))")
leaf2_inst_x = f._emit_raw("DIRECTION('leaf2_inst_x',(1.0,0.0,0.0))")
leaf2_inst_plc = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('leaf2_inst_plc',"
    f"#{leaf2_inst_orig.eid},#{leaf2_inst_z.eid},#{leaf2_inst_x.eid})"
)
# MAPPED_ITEM #2 — satisfies count_entity_def(b'MAPPED_ITEM') == 2.
f._emit_raw(f"MAPPED_ITEM('leaf2_mi',#{leaf2_rm.eid},#{leaf2_inst_plc.eid})")
# NEXT_ASSEMBLY_USAGE_OCCURRENCE #2 — satisfies count_entity_def >= 2.
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE("
    f"'2','leaf2_flat_instance','',#{root_pdef.eid},#{leaf2_pdef.eid},$)"
)
