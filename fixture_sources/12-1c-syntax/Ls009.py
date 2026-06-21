"""Ls009 — Integer literal with hex/octal forms.

Catalog claim: Spec permits leading zeros and a leading sign on INTEGER
but no `0x` hex or interpretation of leading zero as octal. Some tools
emit `0x10` or interpret `010` as octal-8.

Reproducer recipe: #1=POSITIVE_INTEGER_VALUE(0x10);

Byte assertions:
  contains(b'0x10') or contains(b'0X10') or matches(rb'POSITIVE_INTEGER_VALUE\\(010\\)')
  contains(b'0X') or contains(b'0x10')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ls009",
    defect=(
        "Integer literal with hex or octal prefix in STEP file; "
        "ISO 10303-21 spec permits leading zeros and a leading sign on INTEGER "
        "but does not permit 0x hex prefix or octal interpretation of leading zero; "
        "some tools emit 0x10 for hexadecimal 16 or rely on octal 010 meaning 8; "
        "defect: POSITIVE_INTEGER_VALUE with 0x10 — C-style hex literal "
        "that a conforming reader must reject; "
        "also a second entity uses 0X10 (uppercase X variant) to cover "
        "both common hex-prefix forms; "
        "OCC silently accepts with diagnostic but loads empty result — "
        "receivers enforcing the spec must reject this fixture; "
        "synonyms: hex literal in STEP integer, 0x10 in STEP, "
        "octal interpretation of 010, STEP integer with 0x prefix, "
        "non-decimal integer literal; "
        "GEOMETRIC_CURVE_SET IS NOT used — raw entity is the defect carrier"
    ),
)

_original_render = f.render


def _render_hex_integer() -> str:
    header = f._render_header()
    return (
        f"ISO-10303-21;\n"
        f"/* {f.catalog_id}: {f.defect} */\n"
        f"{header}\n"
        f"DATA;\n"
        f"/* Defect: C-style hex literal 0x10 in integer parameter slot. */\n"
        f"/* ISO 10303-21 permits only decimal digits (plus optional leading sign). */\n"
        f"/* 0x prefix (C/C++ hex) is not valid Part-21 INTEGER syntax. */\n"
        f"#1=POSITIVE_INTEGER_VALUE(0x10);\n"
        f"#2=POSITIVE_INTEGER_VALUE(0X10);\n"
        f"ENDSEC;\n"
        f"END-ISO-10303-21;\n"
    )


f.render = _render_hex_integer  # type: ignore[method-assign]
