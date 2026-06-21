"""P012 — STEP-XML (.stpx) and compressed (.stpz) variants unsupported.

Catalog claim: STEP-XML (.stpx, AP242 XML form) and gzip-compressed STEP
(.stpz) are emitted by some commercial tools (PTC Creo, Siemens NX) but only
plain ISO-10303-21 is parsed by most kernels.

The defect: a STEP file that references an external .stpz / .stpx variant via
DOCUMENT_FILE entity and a EXTERNALLY_DEFINED_ITEM, simulating a compound STEP
package that expects the kernel to decompress/parse the XML form.
A robust kernel must recognize and handle the variant or reject with
E_UNSUPPORTED_VARIANT diagnostic; silently returning empty is the bug.

Byte assertions:
  contains(b'.stpz') or contains(b'.stpx') or contains(b'application/x-stepz')
  contains(b'DOCUMENT_FILE')

Tier-3 assertion: shape_null == True

Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="P012",
    defect=(
        "DOCUMENT_FILE entity references 'assembly_model.stpz' (gzip-compressed STEP) "
        "and 'annotation_view.stpx' (STEP-XML AP242 form); "
        "EXTERNALLY_DEFINED_ITEM pointing to stpz/stpx variants; "
        "kernel must decompress/parse or reject with E_UNSUPPORTED_VARIANT; "
        "silently returning empty with no diagnostic is the bug; "
        "NEXT_ASSEMBLY_USAGE_OCCURRENCE scaffolding for §12.6 lint; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
    schema="AP242",
)

# ── Minimal geometry payload ──────────────────────────────────────────────────
origin_pt = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin_pt.eid}))")
f.add_product_chain(gcs)

# ── DOCUMENT entities referencing .stpz and .stpx external variants ──────────
# DOCUMENT_TYPE: declares the type of external document.
doc_type = f._emit_raw(
    "DOCUMENT_TYPE('STEP_compressed')"
)

# DOCUMENT: the external compressed STEP variant.
doc_stpz = f._emit_raw(
    f"DOCUMENT('stpz_doc','assembly_model.stpz','gzip-compressed STEP AP242',#{doc_type.eid})"
)

# DOCUMENT_FILE: names the actual file — byte assertion hits on b'.stpz'.
doc_file_stpz = f._emit_raw(
    f"DOCUMENT_FILE('assembly_model.stpz',#{doc_stpz.eid},'application/x-stepz')"
)

# A second DOCUMENT_FILE for the .stpx (XML) variant.
doc_type_xml = f._emit_raw(
    "DOCUMENT_TYPE('STEP_XML')"
)
doc_stpx = f._emit_raw(
    f"DOCUMENT('stpx_doc','annotation_view.stpx','AP242 XML form',#{doc_type_xml.eid})"
)
doc_file_stpx = f._emit_raw(
    f"DOCUMENT_FILE('annotation_view.stpx',#{doc_stpx.eid},'application/step+xml')"
)

# DOCUMENT_REFERENCE links the external docs back to the product definition.
# Uses #9004 (the product_definition from add_product_chain).
doc_ref_stpz = f._emit_raw(
    f"DOCUMENT_REFERENCE(#{doc_file_stpz.eid},#9004,'compressed_step_ref')"
)
doc_ref_stpx = f._emit_raw(
    f"DOCUMENT_REFERENCE(#{doc_file_stpx.eid},#9004,'xml_step_ref')"
)

# EXTERNALLY_DEFINED_ITEM: the item that lives in the external .stpz/.stpx.
ext_def_stpz = f._emit_raw(
    f"EXTERNALLY_DEFINED_ITEM('main_assembly',#{doc_file_stpz.eid})"
)
ext_def_stpx = f._emit_raw(
    f"EXTERNALLY_DEFINED_ITEM('annotation_view',#{doc_file_stpx.eid})"
)

# ── NAUO scaffolding for §12.6 assembly-presence lint ────────────────────────
sub_pdc = f._emit_raw("PRODUCT_CONTEXT('sub',#9000,'mechanical')")
sub_prod = f._emit_raw(
    f"PRODUCT('StepVariant','StepVariant','',(#{sub_pdc.eid}))"
)
sub_pdf = f._emit_raw(f"PRODUCT_DEFINITION_FORMATION('','',#{sub_prod.eid})")
sub_pdef = f._emit_raw(
    f"PRODUCT_DEFINITION('design','',#{sub_pdf.eid},#9003)"
)
f._emit_raw(
    f"NEXT_ASSEMBLY_USAGE_OCCURRENCE("
    f"'1','step_variant_instance','',#9004,#{sub_pdef.eid},$)"
)
