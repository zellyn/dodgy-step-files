"""Pmi065 — DDP / EER cross-file PMI references break on repackaging.

Catalog claim: AP242 supports referencing geometric elements in a separate
Part 21 file via COMPONENT_PATH_SHAPE_ASPECT / External Element Reference /
DDP linking. When the package is repacked or split, the references break.
Additionally, of_shape must anchor to the root product_definition; mid-tree
anchors are wrong.

Reproducer recipe: DDP archive where assembly-level PMI references a face in
part_3.stp via COMPONENT_PATH_SHAPE_ASPECT; DOCUMENT_FILE entities represent
the referenced part files; 3 PRODUCT entities (assembly + 2 parts).

Byte assertions:
  contains(b'COMPONENT_PATH_SHAPE_ASPECT')
  contains(b'DOCUMENT_FILE')
  count_entity_def(b'PRODUCT') == 3

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi065",
    defect=(
        "COMPONENT_PATH_SHAPE_ASPECT references a shape aspect in an external "
        "DOCUMENT_FILE (part_3.stp); when the DDP archive is repacked or "
        "part_3.stp is renamed the cross-file PMI reference breaks silently; "
        "additionally the of_shape attribute anchors to an intermediate assembly "
        "product_definition rather than the root, violating the AP242 invariant "
        "that of_shape must reference the root product_definition; "
        "receivers must reject when cross-file refs do not resolve; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry wrapped in GCS so OCC returns empty.
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)
# add_product_chain IDs: #9055=PRODUCT_DEFINITION_SHAPE, PRODUCT is #9001

# ── Two additional PRODUCTs (parts) to reach count_entity_def == 3 ────────────
app_ctx_ref = f._emit_raw("APPLICATION_CONTEXT('mechanical design')")
prod_ctx2 = f._emit_raw(
    f"PRODUCT_CONTEXT(#{app_ctx_ref.eid},'mechanical','')"
)
product2 = f._emit_raw(
    f"PRODUCT('part_2','part_2','',(#{prod_ctx2.eid}))"
)
prod_def_form2 = f._emit_raw(
    f"PRODUCT_DEFINITION_FORMATION('','',#{product2.eid})"
)
prod_def_ctx2 = f._emit_raw(
    f"PRODUCT_DEFINITION_CONTEXT(#{app_ctx_ref.eid},'design','')"
)
prod_def2 = f._emit_raw(
    f"PRODUCT_DEFINITION('','',#{prod_def_form2.eid},#{prod_def_ctx2.eid})"
)

product3 = f._emit_raw(
    f"PRODUCT('part_3','part_3','',(#{prod_ctx2.eid}))"
)
prod_def_form3 = f._emit_raw(
    f"PRODUCT_DEFINITION_FORMATION('','',#{product3.eid})"
)
prod_def3 = f._emit_raw(
    f"PRODUCT_DEFINITION('','',#{prod_def_form3.eid},#{prod_def_ctx2.eid})"
)

# ── DOCUMENT_FILE entities representing the referenced part files ──────────────
doc2 = f._emit_raw("DOCUMENT('part2_doc','part_2.stp','Part 2 external file')")
doc_file2 = f._emit_raw(
    f"DOCUMENT_FILE(#{doc2.eid},'part_2.stp')"
)
doc3 = f._emit_raw("DOCUMENT('part3_doc','part_3.stp','Part 3 external file')")
doc_file3 = f._emit_raw(
    f"DOCUMENT_FILE(#{doc3.eid},'part_3.stp')"
)

# ── Shape aspect in the assembly (the PMI anchor) ─────────────────────────────
assy_aspect = f._emit_raw(
    "SHAPE_ASPECT('assy_face_ref','assembly face reference',#9055,.T.)"
)

# ── Shape aspect representing the external face in part_3 ─────────────────────
# of_shape points to prod_def2 (intermediate assembly), not the root — the defect.
part3_pds = f._emit_raw(
    f"PRODUCT_DEFINITION_SHAPE('','',#{prod_def2.eid})"
)
external_aspect = f._emit_raw(
    f"SHAPE_ASPECT('face_47','external face 47',#{part3_pds.eid},.T.)"
)

# ── COMPONENT_PATH_SHAPE_ASPECT linking assembly PMI to external face ──────────
# Defect: the path crosses a broken DDP link and of_shape anchors mid-tree.
f._emit_raw(
    f"COMPONENT_PATH_SHAPE_ASPECT('cross_file_ref','cross-file PMI ref',"
    f"#{assy_aspect.eid},(#{external_aspect.eid}))"
)
