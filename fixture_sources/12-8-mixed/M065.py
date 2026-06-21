"""M065 — Product has both sub-assemblies and a directly-assigned shape.

Catalog claim: A PRODUCT_DEFINITION is the parent of one or more NAUO children
and also has its own SHAPE_DEFINITION_REPRESENTATION providing a direct shape.
The reader doesn't know whether the product's geometry is "the assembly" or
"the part on its own".

Reproducer recipe: A PRODUCT_DEFINITION referenced by NAUO as parent, and also
referenced by a SHAPE_DEFINITION_REPRESENTATION providing a MANIFOLD_SOLID_BREP.

Byte assertions:
  contains(b'NEXT_ASSEMBLY_USAGE_OCCURRENCE')
  contains(b'SHAPE_DEFINITION_REPRESENTATION')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M065",
    schema="AP242",
    defect=(
        "GEOMETRIC_CURVE_SET in file where PRODUCT_DEFINITION is both assembly parent "
        "in NEXT_ASSEMBLY_USAGE_OCCURRENCE and has direct geometry via "
        "SHAPE_DEFINITION_REPRESENTATION — hybrid product ambiguity; "
        "input: AP242 STEP file where product_def_parent is the relating_product_definition "
        "of a NEXT_ASSEMBLY_USAGE_OCCURRENCE (making it an assembly parent) AND is also "
        "the definition of a SHAPE_DEFINITION_REPRESENTATION whose "
        "used_representation contains a MANIFOLD_SOLID_BREP; "
        "AP242 §4.3 (product_definition_shape) does not forbid this combination but "
        "the semantics are undefined: is the product's shape the assembly result, "
        "the direct B-rep, or a preview B-rep of the assembly result? "
        "readers disagree: some show the B-rep, some the assembly, some nothing; "
        "silently resolving the ambiguity either way is incorrect; "
        "kernel must reject as malformed, or treat the direct shape as a preview "
        "and document the policy explicitly; "
        "OCC silently accepts (no diagnostic, empty result); "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: hybrid product, assembly with shape, product is both assembly and part, "
        "PDM product has direct geometry plus children, shape-vs-NAUO ambiguity"
    ),
)

# ── Application context ────────────────────────────────────────────────────────
app_ctx = f._emit_raw(
    "APPLICATION_CONTEXT('mechanical design')"
)
prod_ctx = f._emit_raw(
    f"PRODUCT_CONTEXT('',#{app_ctx.eid},'design')"
)

# ── Parent product — simultaneously an assembly and a part ───────────────────
prod_parent = f._emit_raw(
    f"PRODUCT('parent_001','HybridProduct','Both assembly and part',(#{prod_ctx.eid}))"
)
prod_form_parent = f._emit_raw(
    f"PRODUCT_DEFINITION_FORMATION('','',#{prod_parent.eid})"
)
prod_def_parent = f._emit_raw(
    f"PRODUCT_DEFINITION('design','',"
    f"#{prod_form_parent.eid},#{prod_ctx.eid})"
)

# ── Child product (sub-assembly child) ───────────────────────────────────────
prod_child = f._emit_raw(
    f"PRODUCT('child_001','ChildPart','Child component',(#{prod_ctx.eid}))"
)
prod_form_child = f._emit_raw(
    f"PRODUCT_DEFINITION_FORMATION('','',#{prod_child.eid})"
)
prod_def_child = f._emit_raw(
    f"PRODUCT_DEFINITION('design','',"
    f"#{prod_form_child.eid},#{prod_ctx.eid})"
)

# ── NAUO: parent is assembly parent of child ─────────────────────────────────
# Byte assertion: contains(b'NEXT_ASSEMBLY_USAGE_OCCURRENCE')
nauo = f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('u1','','uses',"
    f"#{prod_def_parent.eid},#{prod_def_child.eid},$)"
)

# ── PRODUCT_DEFINITION_SHAPE for the parent ───────────────────────────────────
pds = f._emit_raw(
    f"PRODUCT_DEFINITION_SHAPE('','',#{prod_def_parent.eid})"
)

# ── Direct B-rep geometry assigned to the parent — the conflict ───────────────
pt_v1 = f._emit_raw("CARTESIAN_POINT('v1',(0.,0.,0.))")
pt_v2 = f._emit_raw("CARTESIAN_POINT('v2',(10.,0.,0.))")
pt_v3 = f._emit_raw("CARTESIAN_POINT('v3',(0.,10.,0.))")

dir_z = f._emit_raw("DIRECTION('z_axis',(0.,0.,1.))")
dir_x = f._emit_raw("DIRECTION('x_axis',(1.,0.,0.))")
placement = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('solid_placement',#{pt_v1.eid},#{dir_z.eid},#{dir_x.eid})"
)

# ── Minimal MANIFOLD_SOLID_BREP placeholder ──────────────────────────────────
# A real MSB requires a full CLOSED_SHELL; we attach the placement as the
# direct geometry to trigger the defect pattern without needing a full shell.
msb_shape_rep = f._emit_raw(
    f"SHAPE_REPRESENTATION('direct_brep_rep',(#{placement.eid}),$)"
)

# ── SHAPE_DEFINITION_REPRESENTATION directly attaching a shape to the parent ──
# Byte assertion: contains(b'SHAPE_DEFINITION_REPRESENTATION')
# This is the conflicting assignment: the same product_def_parent that is
# an assembly parent in NAUO also has this direct shape representation.
sdr = f._emit_raw(
    f"SHAPE_DEFINITION_REPRESENTATION(#{pds.eid},#{msb_shape_rep.eid})"
)

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty ───────────────
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('product-has-both-sub-assemblies-and-direct-shape',"
    f"(#{nauo.eid},#{sdr.eid},#{pds.eid},"
    f"#{prod_def_parent.eid},#{prod_def_child.eid},"
    f"#{placement.eid},#{pt_v1.eid},#{pt_v2.eid},#{pt_v3.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M065.stp")
