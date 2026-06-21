"""Ls052 — Instance ID just past `UINT64_MAX` wraps to a low-numbered ID.

Catalog claim: `UINT64_MAX` is 18446744073709551615. The ID
18446744073709551617 is two greater and wraps modulo 2^64 to 1, which
collides with the low-numbered `#1` namespace and may enable type confusion
if the reader does not validate before storing.

Reproducer recipe: `#18446744073709551617=AXIS2_PLACEMENT_3D('wrap',#1,$,$);`

Byte assertions:
  contains(b'#18446744073709551617=')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ls052",
    defect=(
        "Instance ID just past UINT64_MAX wraps to a low-numbered ID; "
        "UINT64_MAX is 18446744073709551615; "
        "the ID 18446744073709551617 is two greater and wraps modulo 2^64 to 1, "
        "which collides with the low-numbered #1 namespace; "
        "may enable type confusion if the reader does not validate before storing; "
        "a CARTESIAN_POINT at #1 already exists; the wrapped ID aliases it; "
        "expected kernel behavior: detect overflow during digit accumulation and reject "
        "with E_INSTANCE_ID_RANGE; never silently wrap; "
        "OCCT silently accepts (no diagnostic, empty result) — catalog disallows silent-accept; "
        "kernel-bug witnessed: receivers enforcing the spec must reject (or surface a diagnostic); "
        "see also: Ls038, Ls051; "
        "synonyms: instance ID wraps to low number, ID past UINT64_MAX collides with #1, "
        "modular wrap on STEP instance ID, STEP ID overflow type confusion, "
        "huge ID wraps to small ID; "
        "GEOMETRIC_CURVE_SET IS NOT used — raw entities are the defect carriers"
    ),
)

_original_render = f.render


def _render_wraparound_instance_id() -> str:
    header = f._render_header()
    return (
        "/* Ls052 - Instance ID just past UINT64_MAX wraps to a low-numbered ID\n"
        "   ----------------------------------------------------------------------\n"
        "   Catalog section : §12.1c instance-namespace\n"
        "   Sources         : T016, T017, A022\n"
        "   See also        : Ls038, Ls051\n"
        "   ----------------------------------------------------------------------\n"
        "   Defect\n"
        "     UINT64_MAX is 18446744073709551615. The ID 18446744073709551617\n"
        "     is two greater and wraps modulo 2^64 to 1, which collides with\n"
        "     the low-numbered #1 namespace and may enable type confusion if\n"
        "     the reader does not validate before storing.\n"
        "   Expected behavior\n"
        "     Detect overflow during digit accumulation and reject with\n"
        "     E_INSTANCE_ID_RANGE; never silently wrap.\n"
        "   ----------------------------------------------------------------------\n"
        "*/\n"
        "ISO-10303-21;\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Ls052 - instance ID UINT64_MAX+2 wraps to #1'),'2;1');\n"
        "FILE_NAME('Ls052.stp','2026-06-20T00:00:00',('auto-generated'),(''),\n"
        "  'auto-generated','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* #1 is a legitimate CARTESIAN_POINT */\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "/* Defect: UINT64_MAX+2 = 18446744073709551617; wraps mod 2^64 to 1 */\n"
        "/* A silent wrap aliases this entity onto #1, causing type confusion */\n"
        "#18446744073709551617=AXIS2_PLACEMENT_3D('wrap',#1,$,$);\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


f.render = _render_wraparound_instance_id  # type: ignore[method-assign]
