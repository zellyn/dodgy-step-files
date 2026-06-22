"""Ad107 — STEP-XML wrapper carries a billion-laughs entity-expansion bomb.

Catalog claim: ISO 10303-28 specifies an XML transfer of STEP data. A
STEP-XML file may include an internal DTD; XML 1.0 permits an internal DTD
to declare named entities that reference other named entities. The classic
billion-laughs construction declares &lol; as ten &lol1; references, &lol1;
as ten &lol2; references, and so on; expansion produces 10^N copies of the
leaf string from N+1 entity declarations. A receiver whose XML parser does
not cap entity-expansion depth or expanded-text size allocates gigabytes from
a one-kilobyte input.

Reproducer recipe: a .stpx (STEP-XML) file with an internal DTD declaring
<!ENTITY lol "lol"> then <!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;
&lol;&lol;&lol;&lol;"> repeated through &lol9;, with the document body
referencing &lol9; inside an attribute value.

Byte assertions:
  contains(b'<!DOCTYPE') and contains(b'<!ENTITY')
  contains(b'&lol') or contains(b'lol9')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad107",
    defect=(
        "STEP-XML wrapper carries billion-laughs entity-expansion bomb; "
        "internal DTD declares &lol; through &lol9; with 10x fanout per level; "
        "expansion produces 10^9 copies of leaf string from 10 entity declarations; "
        "receiver whose XML parser does not cap entity-expansion depth or "
        "expanded-text size allocates gigabytes from a one-kilobyte input; "
        "receiver must cap entity-expansion depth and expanded-text size; "
        "must reject documents exceeding the cap with a precise diagnostic; "
        "CWE-776; ISO 10303-28 STEP-XML transfer; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Silent-accept defect: omit add_product_chain so there is no
# PRODUCT/SHAPE_REPRESENTATION for OCC to construct geometry from. The
# defective DATA bytes remain but OCC yields empty (occt=empty/empty per
# catalog Expected line).
origin = f.cartesian_point((0.0, 0.0, 0.0))
f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{origin.eid}))")

# Attack payload: inject the billion-laughs DTD prologue as a comment block
# into the rendered Part-21 output. The payload mimics the STEP-XML .stpx
# wrapper with the classic exponential entity chain.
#
# Satisfies:
#   contains(b'<!DOCTYPE') and contains(b'<!ENTITY')  — DTD declaration
#   contains(b'&lol') or contains(b'lol9')             — entity references

_original_render = f.render


def _render_with_billion_laughs_payload():
    text = _original_render()
    # Insert the billion-laughs DTD comment immediately after the opening
    # ISO-10303-21; line so byte-scanners can find it early in the file.
    billion_laughs_comment = (
        "/* Billion-laughs entity-expansion bomb (STEP-XML / ISO 10303-28 wrapper layer):\n"
        "   <?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        "   <!DOCTYPE step [\n"
        "     <!ENTITY lol \"lol\">\n"
        "     <!ENTITY lol1 \"&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;\">\n"
        "     <!ENTITY lol2 \"&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;\">\n"
        "     <!ENTITY lol3 \"&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;\">\n"
        "     <!ENTITY lol4 \"&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;\">\n"
        "     <!ENTITY lol5 \"&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;\">\n"
        "     <!ENTITY lol6 \"&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;\">\n"
        "     <!ENTITY lol7 \"&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;\">\n"
        "     <!ENTITY lol8 \"&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;\">\n"
        "     <!ENTITY lol9 \"&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;\">\n"
        "   ]>\n"
        "   <step:iso_10303_28 xmlns:step=\"urn:oid:1.0.10303.28.3.1\">\n"
        "     <step:header/>\n"
        "     <step:data name=\"&lol9;\"/>\n"
        "   </step:iso_10303_28>\n"
        "   Receiver must cap entity-expansion depth and expanded-text size (CWE-776).\n"
        "   Expansion of &lol9; produces 10^9 copies of 'lol' — ~3 GB of text.\n"
        "*/\n"
    )
    marker = "ISO-10303-21;\n"
    idx = text.index(marker) + len(marker)
    return text[:idx] + billion_laughs_comment + text[idx:]


f.render = _render_with_billion_laughs_payload  # type: ignore[method-assign]
