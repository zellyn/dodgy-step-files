"""Ls051 — Instance ID with 22 digits (overflows `uint64_t` accumulator).

Catalog claim: A 22-digit instance ID overflows a `uint64_t` accumulator
during digit-by-digit parsing. stepcode historically skips an entire section
when an ID width exceeds its allocator's `digits10 + 1`.

Reproducer recipe: `#9999999999999999999999=CARTESIAN_POINT('huge',(0.0,0.0,0.0));`

Byte assertions:
  matches(rb'#\\d{20,}=')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ls051",
    defect=(
        "Instance ID with 22 digits overflows uint64_t accumulator during digit-by-digit parsing; "
        "a uint64_t can hold at most 20 decimal digits (UINT64_MAX = 18446744073709551615); "
        "a 22-digit ID like #9999999999999999999999 overflows the accumulator; "
        "stepcode historically skips an entire section when an ID width exceeds digits10+1; "
        "ISO 10303-21 §11.1: instance IDs are positive integers with no width limit specified, "
        "but implementations must handle overflow gracefully; "
        "expected kernel behavior: detect overflow during digit accumulation and reject with "
        "E_INSTANCE_ID_RANGE; if width must be capped, emit a precise per-instance diagnostic "
        "and continue parsing; "
        "OCCT silently accepts (no diagnostic, empty result) — catalog disallows silent-accept; "
        "see also: Ls038, Ls052; "
        "synonyms: 22-digit instance ID overflows uint64, huge instance ID overflows accumulator, "
        "STEP ID width exceeds 20 digits, stepcode skips section on big ID, "
        "instance ID too wide for uint64_t; "
        "GEOMETRIC_CURVE_SET IS NOT used — raw entities are the defect carriers"
    ),
)

_original_render = f.render


def _render_huge_instance_id() -> str:
    header = f._render_header()
    return (
        "/* Ls051 - Instance ID with 22 digits (overflows uint64_t accumulator)\n"
        "   ----------------------------------------------------------------------\n"
        "   Catalog section : §12.1c instance-namespace\n"
        "   Sources         : T016, T017, A022\n"
        "   See also        : Ls038, Ls052\n"
        "   ----------------------------------------------------------------------\n"
        "   Defect\n"
        "     A 22-digit instance ID overflows a uint64_t accumulator during\n"
        "     digit-by-digit parsing. stepcode historically skips an entire\n"
        "     section when an ID width exceeds its allocator's digits10 + 1.\n"
        "     UINT64_MAX has 20 digits; #9999999999999999999999 has 22.\n"
        "   Expected behavior\n"
        "     Detect overflow during digit accumulation and reject with\n"
        "     E_INSTANCE_ID_RANGE; emit a per-instance diagnostic and continue.\n"
        "   ----------------------------------------------------------------------\n"
        "*/\n"
        "ISO-10303-21;\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Ls051 - 22-digit instance ID overflows uint64_t'),'2;1');\n"
        "FILE_NAME('Ls051.stp','2026-06-20T00:00:00',('auto-generated'),(''),\n"
        "  'auto-generated','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('anchor',(0.,0.,0.));\n"
        "/* Defect: 22-digit ID overflows uint64_t accumulator */\n"
        "/* A compliant reader must reject this or emit a per-instance diagnostic */\n"
        "#9999999999999999999999=CARTESIAN_POINT('huge',(0.,0.,0.));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


f.render = _render_huge_instance_id  # type: ignore[method-assign]
