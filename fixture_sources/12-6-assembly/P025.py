"""P025 — Body name overwritten by last-operation label on export.

Catalog claim: STEP write populates PRODUCT.name and
NEXT_ASSEMBLY_USAGE_OCCURRENCE.name from the last operation's label rather
than the body's label. Round-trip loses body names.

The defect: STEP file where PRODUCT_DEFINITION chain has a name shadowed by
a sub-feature label (e.g., "Pocket" instead of "MyPart_Body"). A kernel must
heal and accept, maintaining a stable mapping of body name to STEP product
name across round-trip; silent empty result is the bug.

Byte assertions:
  count_entity_def(b'NEXT_ASSEMBLY_USAGE_OCCURRENCE') >= 2
  contains(b'MAPPED_ITEM')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="P025",
    defect=(
        "PRODUCT.name and NAUO.name populated from last-operation label not body label; "
        "PRODUCT entities carry names like 'Pocket' and 'Chamfer' — internal feature labels; "
        "body label 'MyPart_Body' / 'MyPart_Base' is absent from PRODUCT chain; "
        "round-trip loses correct body names; kernel must heal and preserve body-to-product mapping; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
    schema="AP242",
)

# ── Minimal geometry payload so shape is empty ────────────────────────────────
origin_pt = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin_pt.eid}))")
f.add_product_chain(gcs)

# ── Shared infrastructure ─────────────────────────────────────────────────────
asm_origin = f._emit_raw("CARTESIAN_POINT('asm_origin',(0.0,0.0,0.0))")
asm_z = f._emit_raw("DIRECTION('asm_z',(0.0,0.0,1.0))")
asm_x = f._emit_raw("DIRECTION('asm_x',(1.0,0.0,0.0))")
asm_plc = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('asm_plc',#{asm_origin.eid},#{asm_z.eid},#{asm_x.eid})"
)
sub_pdc = f._emit_raw("PRODUCT_CONTEXT('sub',#9000,'mechanical')")

# Root product: named correctly as the document assembly.
root_prod = f._emit_raw(
    f"PRODUCT('MyDocument','MyDocument','Document root',(#{sub_pdc.eid}))"
)
root_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{root_prod.eid})")
root_pdef = f._emit_raw(
    f"PRODUCT_DEFINITION('design','',#{root_pdf.eid},#9003)"
)

# ── The defect: two body products whose names are last-operation labels. ───────
# Body 1: actual name should be "MyPart_Body" but was overwritten by "Pocket".
body1_prod = f._emit_raw(
    f"PRODUCT('Pocket','Pocket','body_label_should_be_MyPart_Body',(#{sub_pdc.eid}))"
)
body1_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{body1_prod.eid})")
body1_pdef = f._emit_raw(
    f"PRODUCT_DEFINITION('design','',#{body1_pdf.eid},#9003)"
)
body1_sr = f._emit_raw(
    f"SHAPE_REPRESENTATION('body1_rep',(#{asm_plc.eid}),#9010)"
)
body1_rm = f._emit_raw(f"REPRESENTATION_MAP(#{asm_plc.eid},#{body1_sr.eid})")
body1_inst_orig = f._emit_raw("CARTESIAN_POINT('body1_inst_orig',(0.0,0.0,0.0))")
body1_inst_z = f._emit_raw("DIRECTION('body1_inst_z',(0.0,0.0,1.0))")
body1_inst_x = f._emit_raw("DIRECTION('body1_inst_x',(1.0,0.0,0.0))")
body1_inst_plc = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('body1_inst_plc',"
    f"#{body1_inst_orig.eid},#{body1_inst_z.eid},#{body1_inst_x.eid})"
)
# MAPPED_ITEM satisfies contains(b'MAPPED_ITEM').
f._emit_raw(f"MAPPED_ITEM('body1_mi',#{body1_rm.eid},#{body1_inst_plc.eid})")
# NAUO #1: name also shows the last-operation label "Pocket" not the body name.
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE("
    f"'1','Pocket','',#{root_pdef.eid},#{body1_pdef.eid},$)"
)

# Body 2: actual name should be "MyPart_Base" but was overwritten by "Chamfer".
body2_prod = f._emit_raw(
    f"PRODUCT('Chamfer','Chamfer','body_label_should_be_MyPart_Base',(#{sub_pdc.eid}))"
)
body2_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{body2_prod.eid})")
body2_pdef = f._emit_raw(
    f"PRODUCT_DEFINITION('design','',#{body2_pdf.eid},#9003)"
)
body2_sr = f._emit_raw(
    f"SHAPE_REPRESENTATION('body2_rep',(#{asm_plc.eid}),#9010)"
)
body2_rm = f._emit_raw(f"REPRESENTATION_MAP(#{asm_plc.eid},#{body2_sr.eid})")
body2_inst_orig = f._emit_raw("CARTESIAN_POINT('body2_inst_orig',(10.0,0.0,0.0))")
body2_inst_z = f._emit_raw("DIRECTION('body2_inst_z',(0.0,0.0,1.0))")
body2_inst_x = f._emit_raw("DIRECTION('body2_inst_x',(1.0,0.0,0.0))")
body2_inst_plc = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('body2_inst_plc',"
    f"#{body2_inst_orig.eid},#{body2_inst_z.eid},#{body2_inst_x.eid})"
)
f._emit_raw(f"MAPPED_ITEM('body2_mi',#{body2_rm.eid},#{body2_inst_plc.eid})")
# NAUO #2: satisfies count_entity_def(b'NEXT_ASSEMBLY_USAGE_OCCURRENCE') >= 2.
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE("
    f"'2','Chamfer','',#{root_pdef.eid},#{body2_pdef.eid},$)"
)
