"""Pf018 — Memory not released after STEP assembly read (Linux / Docker).

Catalog claim: reader leaves ~900 MB resident on glibc after reading a
142 MB STEP file even after destructor runs.  Windows VS allocator releases
cleanly; Linux glibc arenas retain.  Indicates fragmentation / arena
retention, but functionally OOMs in containers.

The structural pattern is a multi-product STEP assembly: many PRODUCT /
PRODUCT_DEFINITION / PRODUCT_DEFINITION_FORMATION / NEXT_ASSEMBLY_USAGE_OCCURRENCE
entities arranged in a tree, each with separate SHAPE_REPRESENTATION leaves.
After the destructor frees the C++ objects the glibc arena holds the pages.

The fixture encodes an assembly tree: 5 CARTESIAN_POINT-bearing
SHAPE_REPRESENTATIONs each wrapped in PRODUCT_DEFINITION /
PRODUCT_DEFINITION_FORMATION / PRODUCT entries connected via
NEXT_ASSEMBLY_USAGE_OCCURRENCE.  The multi-product tree is the
input pattern that exercises the arena-retention path.

Byte assertion: count_entity_def(b'CARTESIAN_POINT') >= 5
Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pf018",
    defect=(
        "multi-product assembly tree: 5 PRODUCT leaves + NAUO links; "
        "glibc arena retains ~900 MB resident after destructor; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry anchor: GEOMETRIC_CURVE_SET so OCC yields empty/empty.
anchor = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{anchor.eid}))")
f.add_product_chain(gcs)

# Shared contexts.
app_ctx = f._emit_raw(
    "APPLICATION_CONTEXT('assembly memory leak pattern')"
)
prod_ctx = f._emit_raw(
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
    "REPRESENTATION_CONTEXT('leak_asm','3D')"
)

# 5 leaf products, each with a CARTESIAN_POINT in its SHAPE_REPRESENTATION.
N_LEAVES = 5

leaf_pdef = []
for i in range(N_LEAVES):
    pt     = f.cartesian_point((float(i), 0.0, 0.0))
    sr     = f._emit_raw(
        f"SHAPE_REPRESENTATION('leaf_sr_{i}',(#{pt.eid}),#{repr_ctx.eid})"
    )
    prod   = f._emit_raw(
        f"PRODUCT('leaf_{i}','Leaf {i}','',({mec_ctx.eid}))"
    )
    pdf    = f._emit_raw(
        f"PRODUCT_DEFINITION_FORMATION('','',#{prod.eid})"
    )
    pdef   = f._emit_raw(
        f"PRODUCT_DEFINITION('design','',#{pdf.eid},#{pdef_ctx.eid})"
    )
    # Shape definition + relationship.
    sdr    = f._emit_raw(
        f"SHAPE_DEFINITION_REPRESENTATION("
        f"PRODUCT_DEFINITION_SHAPE('','',#{pdef.eid}),"
        f"#{sr.eid})"
    )
    leaf_pdef.append(pdef)

# Root assembly product.
root_prod = f._emit_raw(
    f"PRODUCT('root_asm','Root Assembly','',({mec_ctx.eid}))"
)
root_pdf  = f._emit_raw(
    f"PRODUCT_DEFINITION_FORMATION('','',#{root_prod.eid})"
)
root_pdef = f._emit_raw(
    f"PRODUCT_DEFINITION('design','',#{root_pdf.eid},#{pdef_ctx.eid})"
)

# NEXT_ASSEMBLY_USAGE_OCCURRENCE links: root → each leaf.
for i, lpdef in enumerate(leaf_pdef):
    f._emit_raw(
        f"NEXT_ASSEMBLY_USAGE_OCCURRENCE("
        f"'nauo_{i}','{i}','',#{root_pdef.eid},#{lpdef.eid},$)"
    )
