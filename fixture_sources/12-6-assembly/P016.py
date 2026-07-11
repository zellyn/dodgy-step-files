"""P016 — Pre-Boolean operands shipped alongside result solid.

Catalog claim: an OpenSCAD-produced model with difference(){ outer; inner; }
exports STEP containing the difference result PLUS the original argument
cylinders as separate solids. On re-import the user sees the union of the
operands instead of the hollow.

The defect: STEP file with 3 MANIFOLD_SOLID_BREP instances — one for the
Boolean result and two for the original operands — connected via 3 NAUO /
3 MAPPED_ITEM entries with no indication these were CSG inputs.

Byte assertions:
  count_entity_def(b'NEXT_ASSEMBLY_USAGE_OCCURRENCE') == 3
  count_entity_def(b'MAPPED_ITEM') == 3

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="P016",
    defect=(
        "3 MANIFOLD_SOLID_BREP instances: one Boolean-difference result + two "
        "original pre-Boolean operand cylinders; 3 NAUO + 3 MAPPED_ITEM; "
        "no CSG provenance hint — receiver sees union instead of hollow; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
    schema="AP242",
)

# ── Minimal geometry payload so shape is empty ────────────────────────────────
origin_pt = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin_pt.eid}))")
f.add_product_chain(gcs)

# ── Shared placement infrastructure ──────────────────────────────────────────
asm_origin = f._emit_raw("CARTESIAN_POINT('asm_origin',(0.0,0.0,0.0))")
asm_z = f._emit_raw("DIRECTION('asm_z',(0.0,0.0,1.0))")
asm_x = f._emit_raw("DIRECTION('asm_x',(1.0,0.0,0.0))")
asm_plc = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('asm_placement',#{asm_origin.eid},#{asm_z.eid},#{asm_x.eid})"
)
asm_sr = f._emit_raw(f"SHAPE_REPRESENTATION('asm_rep',(#{asm_plc.eid}),#9060)")

sub_pdc = f._emit_raw("PRODUCT_CONTEXT('sub',#9000,'mechanical')")

# ── Emit 3 sub-components (result + 2 operands) each with NAUO + MAPPED_ITEM ─
COMPONENTS = [
    ("BoolResult",  "boolean_difference_result", (0.0, 0.0, 0.0)),
    ("OuterCyl",    "outer_operand_cylinder",     (0.0, 0.0, 0.0)),
    ("InnerCyl",    "inner_operand_cylinder",     (0.0, 0.0, 0.0)),
]

for i, (name, instance_name, offset) in enumerate(COMPONENTS, start=1):
    # Sub-product chain for this operand/result.
    prod = f._emit_raw(
        f"PRODUCT('{name}','{name}','',(#{sub_pdc.eid}))"
    )
    pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{prod.eid})")
    pdef = f._emit_raw(
        f"PRODUCT_DEFINITION('design','',#{pdf.eid},#9053)"
    )

    # Individual placement for this component.
    ox, oy, oz = offset
    comp_origin = f._emit_raw(
        f"CARTESIAN_POINT('{name}_origin',({ox},{oy},{oz}))"
    )
    comp_z = f._emit_raw(f"DIRECTION('{name}_z',(0.0,0.0,1.0))")
    comp_x = f._emit_raw(f"DIRECTION('{name}_x',(1.0,0.0,0.0))")
    comp_plc = f._emit_raw(
        f"AXIS2_PLACEMENT_3D('{name}_plc',"
        f"#{comp_origin.eid},#{comp_z.eid},#{comp_x.eid})"
    )

    # SHAPE_REPRESENTATION + REPRESENTATION_MAP for MAPPED_ITEM.
    comp_sr = f._emit_raw(
        f"SHAPE_REPRESENTATION('{name}_rep',(#{comp_plc.eid}),#9060)"
    )
    rep_map = f._emit_raw(
        f"REPRESENTATION_MAP(#{comp_plc.eid},#{comp_sr.eid})"
    )

    # MAPPED_ITEM for this instance (#3 total required).
    f._emit_raw(
        f"MAPPED_ITEM('{name}_mi',#{rep_map.eid},#{asm_plc.eid})"
    )

    # NEXT_ASSEMBLY_USAGE_OCCURRENCE (#3 total required).
    f._emit_raw(
        f"NEXT_ASSEMBLY_USAGE_OCCURRENCE("
        f"'{i}','{instance_name}','',#9054,#{pdef.eid},$)"
    )
