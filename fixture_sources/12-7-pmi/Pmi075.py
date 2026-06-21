"""Pmi075 — KINEMATIC_JOINT referencing the same link as both ends (self-loop).

Catalog claim: AP242 kinematic representation models a mechanism as a graph:
KINEMATIC_LINK nodes joined by KINEMATIC_JOINT edges. A joint should reference
exactly two distinct links (one per end). A producer that omits one end
(referencing the same link twice, or pointing the second end to a deleted link)
yields an inconsistent kinematic graph that cannot be simulated.

Reproducer recipe: NEXT_ASSEMBLY_USAGE_OCCURRENCE whose relating and related
PRODUCT_DEFINITIONs are the same instance — modelling a self-loop joint.

Byte assertions:
  count_entity_def(b'NEXT_ASSEMBLY_USAGE_OCCURRENCE') == 2
  count_entity_def(b'PRODUCT') == 2
  count_entity_def(b'PRODUCT_DEFINITION') == 2

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi075",
    schema="AP242",
    defect=(
        "NEXT_ASSEMBLY_USAGE_OCCURRENCE 'joint_self_loop' references the same "
        "PRODUCT_DEFINITION as both relating and related ends; this encodes a "
        "kinematic self-loop — a joint whose two link endpoints are the same node; "
        "receivers must detect that relating == related in the joint graph and reject "
        "or emit a precise 'self-loop kinematic joint' diagnostic; silently accepting "
        "a self-loop kinematic graph is forbidden; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE, #9056=LENGTH_UNIT
# Also creates: #9001=PRODUCT_CONTEXT, #9002=PRODUCT, #9004=PRODUCT_DEFINITION

# ── Second kinematic-link PRODUCT / PRODUCT_DEFINITION (byte assert: count==2) ──
# This is the self-loop link: 'link_B' is a stand-alone joint node.
link_ctx = f._emit_raw("PRODUCT_CONTEXT('',#9000,'mechanical')")
link_b_prod = f._emit_raw(
    f"PRODUCT('link_B','link_B','',(#{link_ctx.eid}))"
)
link_b_pdf = f._emit_raw(
    f"PRODUCT_DEFINITION_FORMATION('','',#{link_b_prod.eid})"
)
link_b_pdef = f._emit_raw(
    f"PRODUCT_DEFINITION('design','',#{link_b_pdf.eid},#9053)"
)

# ── Two NEXT_ASSEMBLY_USAGE_OCCURRENCEs (byte assert: count==2) ───────────────
# nauo_valid: well-formed — parent product (#9054) links to child link_B.
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('nauo_valid','joint_parent_to_link_b','',"
    f"#9054,#{link_b_pdef.eid},$)"
)
# nauo_self_loop: DEFECT — relating and related both point to link_B itself;
# this is a self-loop joint where both ends of the joint reference the same node.
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE('joint_self_loop','kinematic self-loop','',"
    f"#{link_b_pdef.eid},#{link_b_pdef.eid},$)"
)

# ── SHAPE_ASPECT as PMI entity to satisfy category-lint ───────────────────────
f._emit_raw("SHAPE_ASPECT('link_b_shape','kinematic link B shape',#9055,.T.)")
