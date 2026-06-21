"""Ls038 — Instance ID `#0` (must be positive non-zero).

Catalog claim: ISO 10303-21 requires positive non-zero instance IDs. `#0` is invalid.

Reproducer recipe: #0=CARTESIAN_POINT('origin',(0.,0.,0.));

Byte assertions:
  contains(b'#0=')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ls038",
    defect=(
        "Instance ID #0 used — ISO 10303-21 requires positive non-zero instance IDs; "
        "#0 is explicitly invalid per the standard; "
        "ISO 10303-21 §11.1: entity instance names are positive integers (#1 and above); "
        "zero is not a positive integer; "
        "expected kernel behavior: reject #0 with E_INSTANCE_ID_RANGE; "
        "continue parsing the remainder of the section rather than aborting; "
        "defect: DATA section contains #0=CARTESIAN_POINT(..) and #0 referenced from #3; "
        "back-references to #0 from valid entities become dangling after rejection; "
        "OCCT silently accepts (no diagnostic, empty result); "
        "see also: Lh023, Ls051, Ls052; "
        "synonyms: instance ID #0 invalid, STEP entity numbered zero, "
        "zero instance ID rejected, #0 as definition or reference, "
        "non-positive STEP instance ID; "
        "GEOMETRIC_CURVE_SET IS NOT used — raw entities are the defect carriers"
    ),
)

_original_render = f.render


def _render_zero_instance_id() -> str:
    header = f._render_header()
    return (
        "/* Ls038 - Instance ID #0 (must be positive non-zero)\n"
        "   ----------------------------------------------------------------------\n"
        "   Catalog section : §12.1c instance-namespace\n"
        "   Sources         : T016, T017, A022\n"
        "   See also        : Lh023, Ls051, Ls052\n"
        "   ----------------------------------------------------------------------\n"
        "   Defect\n"
        "     ISO 10303-21 §11.1 requires positive non-zero instance IDs.\n"
        "     #0 is invalid: zero is not a positive integer.\n"
        "   Expected behavior\n"
        "     Reject #0 with E_INSTANCE_ID_RANGE; continue parsing the remainder\n"
        "     of the section rather than skipping it.\n"
        "   ----------------------------------------------------------------------\n"
        "*/\n"
        "ISO-10303-21;\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Ls038 - instance ID #0 is invalid'),'2;1');\n"
        "FILE_NAME('Ls038.stp','2026-06-20T00:00:00',('auto-generated'),(''),\n"
        "  'auto-generated','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Defect: #0 is an invalid instance ID (must be >= 1 per §11.1) */\n"
        "#0=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#1=DIRECTION('x',(1.,0.,0.));\n"
        "#2=VECTOR('v',#1,1.);\n"
        "/* Back-reference to invalid #0 -- becomes dangling after rejection */\n"
        "#3=LINE('l',#0,#2);\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


f.render = _render_zero_instance_id  # type: ignore[method-assign]
