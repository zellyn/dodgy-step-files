"""M060 — External reference resolves to the same file as the main file.

Catalog claim: An assembly references an external STEP file via a
DOCUMENT_FILE link, but the resolved path equals the main file's path.
The reader recurses into itself.

Reproducer recipe: A DOCUMENT_FILE whose id points back at the file's own
filename ('M060.stp').

Byte assertions:
  contains(b'DOCUMENT_FILE')
  contains(b"'M060.stp'")

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M060",
    schema="AP242",
    defect=(
        "GEOMETRIC_CURVE_SET in file with DOCUMENT_FILE whose id points back at "
        "the main file's own name ('M060.stp') — external reference self-loop; "
        "input: AP242 STEP file where DOCUMENT_FILE references a path equal to the "
        "file's own filename, causing a reader that resolves external references to "
        "recurse into itself; "
        "the self-reference creates an infinite-recursion or cycle-detection scenario; "
        "conformant readers must detect the identity and skip with a warning, or treat "
        "as a no-op reference; silently following the link is a bug (infinite loop or "
        "stack overflow); "
        "OCC silently accepts (no diagnostic, empty result); "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: STEP self-reference loop, external reference loops, "
        "external file is same as main, DOCUMENT_FILE points to self"
    ),
)

# ── Application context ────────────────────────────────────────────────────────
app_ctx = f._emit_raw(
    "APPLICATION_CONTEXT('mechanical design')"
)

# ── DOCUMENT_FILE pointing back at the main file — the defect ─────────────────
# Byte assertions:
#   contains(b'DOCUMENT_FILE')
#   contains(b"'M060.stp'")
# The 'id' attribute encodes the filename; a resolver following this link
# opens 'M060.stp' — the very file it is currently parsing.
doc_file = f._emit_raw(
    "DOCUMENT_FILE('M060.stp','self-referencing external link',"
    f"#{app_ctx.eid},'step_physical_file')"
)

# ── DOCUMENT entity that wraps the DOCUMENT_FILE ──────────────────────────────
document = f._emit_raw(
    f"DOCUMENT('doc_001','Self-reference document','',(#{doc_file.eid}))"
)

# ── DOCUMENT_REFERENCE links the document back into this file ─────────────────
# This is the mechanism by which assembly readers follow external links.
doc_ref = f._emit_raw(
    f"DOCUMENT_REFERENCE(#{document.eid},#{doc_file.eid},'self-ref-link')"
)

# ── Minimal geometry for the GEOMETRIC_CURVE_SET ─────────────────────────────
origin = f._emit_raw("CARTESIAN_POINT('origin',(0.,0.,0.))")
dir_z = f._emit_raw("DIRECTION('z_axis',(0.,0.,1.))")
dir_x = f._emit_raw("DIRECTION('x_axis',(1.,0.,0.))")
placement = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('ref_placement',#{origin.eid},#{dir_z.eid},#{dir_x.eid})"
)
line_dir = f._emit_raw("DIRECTION('line_dir',(1.,0.,0.))")
line_vec = f._emit_raw(f"VECTOR(#{line_dir.eid},10.)")
line = f._emit_raw(f"LINE('ref_edge',#{origin.eid},#{line_vec.eid})")

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty ───────────────
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('external-reference-self-loop-document-file',"
    f"(#{doc_file.eid},#{document.eid},#{doc_ref.eid},"
    f"#{line.eid},#{placement.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M060.stp")
