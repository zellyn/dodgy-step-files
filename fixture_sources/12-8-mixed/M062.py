"""M062 — SRR reverses the relation defined by NAUO; conflict resolved silently.

Catalog claim: A SHAPE_REPRESENTATION_RELATIONSHIP declares parent→child while
a corresponding NEXT_ASSEMBLY_USAGE_OCCURRENCE declares child→parent. The reader
silently picks one.

Reproducer recipe: An NAUO declaring A is parent of B, plus an SRR with the
opposite direction.

Byte assertions:
  contains(b'NEXT_ASSEMBLY_USAGE_OCCURRENCE')
  contains(b'SHAPE_REPRESENTATION_RELATIONSHIP')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M062",
    schema="AP242",
    defect=(
        "GEOMETRIC_CURVE_SET in file where NEXT_ASSEMBLY_USAGE_OCCURRENCE declares "
        "product_A as parent of product_B, but SHAPE_REPRESENTATION_RELATIONSHIP "
        "encodes the opposite direction (rep_B→rep_A) — assembly relation conflict; "
        "input: AP242 STEP assembly file with NAUO(relating=product_def_A, "
        "related=product_def_B) and SRR(rep_A=shape_rep_B, rep_B=shape_rep_A), "
        "reversing the parent→child direction established by the NAUO; "
        "AP242 §4.3.2 (assembly_component_usage) requires SRR and NAUO to be "
        "consistent: the SRR.rep_1 must be the representing_item for the NAUO's "
        "relating_product_definition, and SRR.rep_2 for the related; "
        "the conflict means one direction is authoritative and the other is wrong; "
        "readers that trust NAUO will invert the assembly; readers that trust SRR "
        "will produce the same wrong result; silently resolving either way is a bug; "
        "kernel must reject the conflict with a diagnostic; or trust NAUO by convention "
        "and make the choice explicit in a warning; "
        "OCC silently accepts (no diagnostic, empty result); "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: assembly direction conflict, SRR vs NAUO direction mismatch, "
        "parent/child conflict in STEP, assembly relation reversed"
    ),
)

# ── Application context ────────────────────────────────────────────────────────
app_ctx = f._emit_raw(
    "APPLICATION_CONTEXT('mechanical design')"
)
prod_ctx = f._emit_raw(
    f"PRODUCT_CONTEXT('',#{app_ctx.eid},'design')"
)

# ── Product A (the intended parent per NAUO) ──────────────────────────────────
prod_a = f._emit_raw(
    f"PRODUCT('A','Assembly_A','Parent assembly',(#{prod_ctx.eid}))"
)
prod_def_form_a = f._emit_raw(
    f"PRODUCT_DEFINITION_FORMATION('','',#{prod_a.eid})"
)
prod_def_a = f._emit_raw(
    f"PRODUCT_DEFINITION('design','',"
    f"#{prod_def_form_a.eid},#{prod_ctx.eid})"
)

# ── Product B (the intended child per NAUO) ───────────────────────────────────
prod_b = f._emit_raw(
    f"PRODUCT('B','Component_B','Child component',(#{prod_ctx.eid}))"
)
prod_def_form_b = f._emit_raw(
    f"PRODUCT_DEFINITION_FORMATION('','',#{prod_b.eid})"
)
prod_def_b = f._emit_raw(
    f"PRODUCT_DEFINITION('design','',"
    f"#{prod_def_form_b.eid},#{prod_ctx.eid})"
)

# ── NAUO: A is parent (relating), B is child (related) ───────────────────────
# Byte assertion: contains(b'NEXT_ASSEMBLY_USAGE_OCCURRENCE')
nauo = f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('u1','','uses',"
    f"#{prod_def_a.eid},#{prod_def_b.eid},$)"
)

# ── Shape representations for A and B ────────────────────────────────────────
geom_ctx = f._emit_raw(
    "GEOMETRIC_REPRESENTATION_CONTEXT(3)"
)
shape_rep_a = f._emit_raw(
    f"SHAPE_REPRESENTATION('rep_A',(),"
    f"#{geom_ctx.eid})"
)
shape_rep_b = f._emit_raw(
    f"SHAPE_REPRESENTATION('rep_B',(),"
    f"#{geom_ctx.eid})"
)

# ── SRR with REVERSED direction: rep_B→rep_A instead of rep_A→rep_B ──────────
# Byte assertion: contains(b'SHAPE_REPRESENTATION_RELATIONSHIP')
# Defect: NAUO says A is parent; SRR says B's rep contains A's rep (reversed).
srr = f._emit_raw(
    f"SHAPE_REPRESENTATION_RELATIONSHIP('srr_reversed','reversed direction',"
    f"#{shape_rep_b.eid},#{shape_rep_a.eid})"
)

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty ───────────────
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('srr-reverses-nauo-assembly-relation-direction',"
    f"(#{nauo.eid},#{srr.eid},#{shape_rep_a.eid},#{shape_rep_b.eid},"
    f"#{prod_def_a.eid},#{prod_def_b.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M062.stp")
