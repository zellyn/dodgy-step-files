"""Ls043 — Excessively long entity name / hyphen in identifier.

Catalog claim: Parser copies entity name into a fixed-size identifier buffer;
classic strcpy overflow on very long names. ISO conformance class permits long
names but not unbounded. Embedded `-` (hyphen) in identifiers is also disallowed
(`BS7752-1`).

Reproducer recipe: `#1=AAAA…(64 chars)…(..);` and `#2=BS7752-1(..)`.

Byte assertions:
  matches(rb'#\\d+\\s*=\\s*A{50,}\\(') or matches(rb'#\\d+\\s*=\\s*[A-Z]+-\\d+\\(')
  matches(rb'A{50,}|BS7752-1')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ls043",
    defect=(
        "Excessively long entity name causes fixed-buffer overflow in tokenizer; "
        "parser copies entity name into a fixed-size identifier buffer "
        "— classic strcpy overflow on very long names; "
        "ISO 10303-21 conformance class permits long names but not unbounded; "
        "defect 1: entity name of 64+ uppercase A characters "
        "far exceeds the common fixed-buffer size of 32 or 64 chars; "
        "expected kernel behavior: reject overflow before allocation; "
        "maximum identifier length per ISO conformance class (e.g. 256 chars); "
        "defect 2: embedded hyphen in entity name — BS7752-1 "
        "— ISO identifiers permit only letters, digits, and underscore; "
        "a hyphen is not a valid identifier character per ISO 10303-21 §4.2; "
        "lenient mode may map the hyphen to underscore; "
        "see also: Ls044; "
        "synonyms: very long STEP entity name, fixed-buffer overflow on long name, "
        "hyphen in STEP identifier, BS7752-1 entity name rejected, "
        "STEP entity name with dash; "
        "GEOMETRIC_CURVE_SET IS NOT used — raw entities are the defect carriers"
    ),
)

_original_render = f.render


def _render_long_entity_name() -> str:
    header = f._render_header()
    # 80 A's — well past any 32- or 64-byte fixed buffer
    long_name = "A" * 80
    return (
        "/* Ls043 - Excessively long entity name / hyphen in identifier\n"
        "   ----------------------------------------------------------------------\n"
        "   Catalog section : §12.1c lexical / identifier limits\n"
        "   Sources         : A021, S002\n"
        "   ----------------------------------------------------------------------\n"
        "   Defect\n"
        "     Parser copies entity name into a fixed-size identifier buffer;\n"
        "     classic strcpy overflow. ISO conformance class permits long names\n"
        "     but not unbounded.\n"
        "     Defect 1: entity name is 80 uppercase A's — overflows a 32/64-char buffer.\n"
        "     Defect 2: BS7752-1 — hyphen is not a valid identifier character.\n"
        "   Expected behavior\n"
        "     Reject overflow before allocation (max ~256 chars per ISO);\n"
        "     reject hyphen in identifier; lenient mode may map hyphen to underscore.\n"
        "   ----------------------------------------------------------------------\n"
        "*/\n"
        "ISO-10303-21;\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Ls043 - excessively long entity name and hyphen in identifier'),'2;1');\n"
        "FILE_NAME('Ls043.stp','2026-06-20T00:00:00',('auto-generated'),(''),\n"
        "  'auto-generated','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        f"/* Defect 1: entity name is {len(long_name)} uppercase A characters — fixed-buffer overflow */\n"
        f"#1={long_name}('overflow-test',(0.,0.,0.));\n"
        "/* Defect 2: embedded hyphen in entity name (BS7752-1) */\n"
        "/* ISO 10303-21 §4.2: identifiers use letters, digits, underscore only */\n"
        "#2=BS7752-1('hyphen-name',(1.,0.,0.));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


f.render = _render_long_entity_name  # type: ignore[method-assign]
