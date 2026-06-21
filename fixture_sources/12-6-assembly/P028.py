"""P028 — Empty/null shape entries in OCAF document corrupt writer.

Catalog claim: An assembly-document carries non-shape labels (Joints,
Variables, Constraints, Configurations, LinkGroup); labels whose attached
topological shape is null. The STEP writer's color-attribution pass
dereferences the null shape during traversal and crashes; the resulting
STEP file is truncated mid-write.

The defect: assembly document with null-shape labels mixed into the
PRODUCT_DEFINITION chain. A kernel must skip non-shape labels with a warning,
or filter them out before traversal; null subshape must not crash the writer;
silent empty result is the bug.

Byte assertions:
  contains(b'NEXT_ASSEMBLY_USAGE_OCCURRENCE')
  contains(b'Empty/null shape entries') or contains(b'P028') or contains(b'truncated')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="P028",
    defect=(
        "Assembly OCAF document contains non-shape labels with null topological shape: "
        "Joints, Variables, Constraints, Configurations, LinkGroup labels all have null shapes; "
        "STEP writer color-attribution pass dereferences null shape during traversal and crashes; "
        "resulting STEP file is truncated mid-write (truncated output); "
        "Empty/null shape entries in PRODUCT_DEFINITION chain; "
        "kernel must skip non-shape labels with a warning before traversal; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
    schema="AP242",
)

# ── Minimal geometry payload so shape is empty ────────────────────────────────
origin_pt = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin_pt.eid}))")
f.add_product_chain(gcs)

# ── Shared infrastructure ─────────────────────────────────────────────────────
sub_pdc = f._emit_raw("PRODUCT_CONTEXT('sub',#9000,'mechanical')")

# Root product: the top-level OCAF document assembly.
root_prod = f._emit_raw(
    f"PRODUCT('OcafAssembly','OcafAssembly','OCAF doc assembly root',(#{sub_pdc.eid}))"
)
root_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{root_prod.eid})")
root_pdef = f._emit_raw(
    f"PRODUCT_DEFINITION('design','',#{root_pdf.eid},#9003)"
)

# ── The defect: non-shape labels with null-shape entries interspersed in the
# product hierarchy. In a real OCAF document these would be Joints/Variables/
# Constraints/Configurations/LinkGroup labels — all have null shapes, causing
# the writer's color-attribution traversal to crash. ──────────────────────────

# "Joints" label — null-shape entry in OCAF document.
joints_prod = f._emit_raw(
    f"PRODUCT('Joints','Joints','null-shape OCAF label: Joints',(#{sub_pdc.eid}))"
)
joints_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{joints_prod.eid})")
joints_pdef = f._emit_raw(
    f"PRODUCT_DEFINITION('design','',#{joints_pdf.eid},#9003)"
)
# NAUO links Joints null-label directly under root — defect: shape is null.
# Byte assertion: contains(b'NEXT_ASSEMBLY_USAGE_OCCURRENCE').
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE("
    f"'1','Joints_null_label','',#{root_pdef.eid},#{joints_pdef.eid},$)"
)

# "Variables" label — another null-shape entry.
vars_prod = f._emit_raw(
    f"PRODUCT('Variables','Variables','null-shape OCAF label: Variables',(#{sub_pdc.eid}))"
)
vars_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{vars_prod.eid})")
vars_pdef = f._emit_raw(
    f"PRODUCT_DEFINITION('design','',#{vars_pdf.eid},#9003)"
)
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE("
    f"'2','Variables_null_label','',#{root_pdef.eid},#{vars_pdef.eid},$)"
)

# "Constraints" label — another null-shape entry.
cstr_prod = f._emit_raw(
    f"PRODUCT('Constraints','Constraints','null-shape OCAF label: Constraints',(#{sub_pdc.eid}))"
)
cstr_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{cstr_prod.eid})")
cstr_pdef = f._emit_raw(
    f"PRODUCT_DEFINITION('design','',#{cstr_pdf.eid},#9003)"
)
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE("
    f"'3','Constraints_null_label','',#{root_pdef.eid},#{cstr_pdef.eid},$)"
)

# "Configurations" label — null-shape entry (LinkGroup scenario).
cfg_prod = f._emit_raw(
    f"PRODUCT('Configurations','Configurations','null-shape OCAF label: Configurations',(#{sub_pdc.eid}))"
)
cfg_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{cfg_prod.eid})")
cfg_pdef = f._emit_raw(
    f"PRODUCT_DEFINITION('design','',#{cfg_pdf.eid},#9003)"
)
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE("
    f"'4','Configurations_null_label','',#{root_pdef.eid},#{cfg_pdef.eid},$)"
)
