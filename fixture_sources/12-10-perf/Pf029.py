"""Pf029 — TDocStd_Document creation aborts process under VSCode server runtime.

Catalog claim: TDocStd_Document('STEP') triggers process abort under
code-server / extension-host runtimes when reading a multi-level assembly.
Symptom of resource / signal-handling assumptions that fail at scale.

The structural pattern is a multi-level assembly STEP file: PRODUCT entities
connected via NEXT_ASSEMBLY_USAGE_OCCURRENCE in at least two levels of nesting
(grandparent → parent → child), which is the input that triggers the
TDocStd_Document abort when resource or signal limits apply.  The file also
needs CARTESIAN_POINT entities (byte assertion >= 1) and must contain
NEXT_ASSEMBLY_USAGE_OCCURRENCE (byte assertion).

GEOMETRIC_CURVE_SET is the product-chain model entity so OCC yields
empty/empty.

Byte assertion: count_entity_def(b'CARTESIAN_POINT') >= 1
Byte assertion: contains(b'NEXT_ASSEMBLY_USAGE_OCCURRENCE')
Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pf029",
    defect=(
        "multi-level assembly: grandparent→parent→child NAUO tree (2-level nesting); "
        "TDocStd_Document creation aborts process under code-server / extension-host "
        "runtimes due to resource/signal-handling assumptions; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry anchor: GEOMETRIC_CURVE_SET so OCC yields empty/empty.
anchor = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{anchor.eid}))")
f.add_product_chain(gcs)

# Shared contexts for the assembly tree.
app_ctx = f._emit_raw(
    "APPLICATION_CONTEXT('multi-level assembly abort pattern')"
)
f._emit_raw(
    f"APPLICATION_PROTOCOL_DEFINITION('international standard',"
    f"'automotive_design',2000,#{app_ctx.eid})"
)
mec_ctx = f._emit_raw(
    f"PRODUCT_CONTEXT('',#{app_ctx.eid},'mechanical')"
)
pdef_ctx = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT('part definition',#{app_ctx.eid},'design')"
)
repr_ctx = f._emit_raw(
    "REPRESENTATION_CONTEXT('nauo_asm','3D')"
)

def make_product(label, x_offset):
    """Create a minimal PRODUCT_DEFINITION with a CARTESIAN_POINT."""
    pt   = f.cartesian_point((x_offset, 0.0, 0.0))
    sr   = f._emit_raw(
        f"SHAPE_REPRESENTATION('{label}_sr',(#{pt.eid}),#{repr_ctx.eid})"
    )
    prod = f._emit_raw(
        f"PRODUCT('{label}','{label}','',({mec_ctx.eid}))"
    )
    pdf  = f._emit_raw(
        f"PRODUCT_DEFINITION_FORMATION('','',#{prod.eid})"
    )
    pdef = f._emit_raw(
        f"PRODUCT_DEFINITION('design','',#{pdf.eid},#{pdef_ctx.eid})"
    )
    f._emit_raw(
        f"SHAPE_DEFINITION_REPRESENTATION("
        f"PRODUCT_DEFINITION_SHAPE('','',#{pdef.eid}),"
        f"#{sr.eid})"
    )
    return pdef

# Three-level tree: grandparent → two parents → two children each.
child_a  = make_product("child_a",  1.0)
child_b  = make_product("child_b",  2.0)
child_c  = make_product("child_c",  3.0)
child_d  = make_product("child_d",  4.0)
parent_1 = make_product("parent_1", 5.0)
parent_2 = make_product("parent_2", 6.0)
gp       = make_product("grandparent", 7.0)

# Level 1: grandparent → parents.
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('nauo_gp1','1','',#{gp.eid},#{parent_1.eid},$)"
)
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('nauo_gp2','2','',#{gp.eid},#{parent_2.eid},$)"
)
# Level 2: parent_1 → children a, b.
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('nauo_p1a','1','',#{parent_1.eid},#{child_a.eid},$)"
)
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('nauo_p1b','2','',#{parent_1.eid},#{child_b.eid},$)"
)
# Level 2: parent_2 → children c, d.
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('nauo_p2c','1','',#{parent_2.eid},#{child_c.eid},$)"
)
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('nauo_p2d','2','',#{parent_2.eid},#{child_d.eid},$)"
)
