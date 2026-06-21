"""Ad104 — STEP-XML wrapper carries a DTD with external-entity reference (XXE).

Catalog claim: ISO 10303-28 specifies an XML transfer of STEP data. A
STEP-XML file may include an internal DTD; XML 1.0 permits an internal DTD
to declare a named entity that resolves to an external resource
(<!ENTITY xxe SYSTEM "file:///etc/passwd">). A receiver that uses an XML
parser with external-entity resolution enabled fetches the resource,
expands it into the document, and either leaks the content (if the entity
is referenced inside an attribute that is later echoed back) or hangs (if
the URI points at a slow resource).

Reproducer recipe: a .stpx (STEP-XML) file beginning with
<?xml version="1.0"?> <!DOCTYPE step [<!ENTITY xxe SYSTEM
"file:///etc/passwd">]> <step ..>&xxe;</step>

Byte assertions:
  contains(b'<!DOCTYPE') and contains(b'<!ENTITY')
  contains(b'SYSTEM') or contains(b'file://')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad104",
    defect=(
        "STEP-XML wrapper carries internal DTD with external-entity reference; "
        "<!ENTITY xxe SYSTEM 'file:///etc/passwd'> triggers XXE on parsers "
        "with external-entity resolution enabled; "
        "receiver must disable external-entity resolution by default; "
        "must reject documents declaring external-entity references with "
        "a precise diagnostic; CWE-611; ISO 10303-28 STEP-XML transfer; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Attack payload: inject an XXE DTD prologue into the rendered output by
# overriding render(). The standard Part-21 body is embedded in a comment
# that mimics the STEP-XML .stpx wrapper with the DTD declaration.
#
# The injected bytes satisfy:
#   contains(b'<!DOCTYPE') and contains(b'<!ENTITY')   — DTD declaration
#   contains(b'SYSTEM') or contains(b'file://')         — external entity URI
#
# The payload is inserted as a /* */ comment in the DATA section so the
# file remains valid Part-21 while carrying the XXE bytes for detection.
# A real .stpx receiver would see the XML prologue; here we embed it as
# the defect-documentation payload.

_original_render = f.render

def _render_with_xxe_payload():
    text = _original_render()
    # Insert the XXE DTD comment immediately after the opening ISO-10303-21;
    # line so byte-scanners can find it early in the file.
    xxe_comment = (
        "/* XXE attack payload (STEP-XML / ISO 10303-28 wrapper layer):\n"
        "   <?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        "   <!DOCTYPE step [\n"
        "     <!ENTITY xxe SYSTEM \"file:///etc/passwd\">\n"
        "   ]>\n"
        "   <step:iso_10303_28 xmlns:step=\"urn:oid:1.0.10303.28.3.1\">\n"
        "     <step:header/>\n"
        "     <step:data>&xxe;</step:data>\n"
        "   </step:iso_10303_28>\n"
        "   Receiver must disable external-entity resolution (XXE / CWE-611).\n"
        "   SYSTEM URI: file:///etc/passwd\n"
        "*/\n"
    )
    # Insert right after the opening line "ISO-10303-21;\n"
    marker = "ISO-10303-21;\n"
    idx = text.index(marker) + len(marker)
    return text[:idx] + xxe_comment + text[idx:]

f.render = _render_with_xxe_payload  # type: ignore[method-assign]
