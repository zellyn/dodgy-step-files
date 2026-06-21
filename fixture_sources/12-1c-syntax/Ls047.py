"""Ls047 — Complex / multiple-inheritance entity record: leaves separated by commas.

Catalog claim: The Part-21 grammar requires the leaves of a complex entity record
(`#1=( A() B() C() )`) to be separated by whitespace, not commas. A writer that
emits commas (carrying habit from argument lists) produces a token that a strict
reader must reject.

Reproducer recipe:
  `#10=( CONVERSION_BASED_UNIT('DEG',#9), NAMED_UNIT(*), PLANE_ANGLE_UNIT() );`
  — commas between leaves.

Byte assertions:
  matches(rb'#\\d+\\s*=\\s*\\(\\s*[A-Z_]+\\([^)]*\\),\\s*[A-Z_]+')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ls047",
    defect=(
        "Complex entity record leaves separated by commas instead of whitespace; "
        "ISO 10303-21 complex entity instances use external mapping: "
        "#N=( LEAF_A(...) LEAF_B(...) LEAF_C(...) ) "
        "where the leaves are separated by whitespace only, not commas; "
        "a writer carrying habit from argument lists emits commas between leaves, "
        "producing a token that a strict reader must reject; "
        "the grammar production for complex-entity is unambiguous: "
        "leaf records are juxtaposed with whitespace separation; "
        "commas belong inside a leaf's argument list, not between leaves; "
        "defect: CONVERSION_BASED_UNIT('DEG',#9), NAMED_UNIT(*), PLANE_ANGLE_UNIT() "
        "uses commas between the three leaves of the complex unit entity; "
        "expected kernel behavior: reject comma-separated leaves in strict mode; "
        "lenient mode may accept-with-warning; "
        "see also: Ls010, Ls048; "
        "synonyms: complex entity leaves separated by commas, "
        "multiple-inheritance leaves with comma separators, "
        "STEP complex record uses commas not whitespace, "
        "comma in complex entity rejected, complex entity grammar violation; "
        "GEOMETRIC_CURVE_SET IS NOT used — raw entities are the defect carriers"
    ),
)

_original_render = f.render


def _render_comma_separated_leaves() -> str:
    header = f._render_header()
    return (
        "/* Ls047 - Complex entity record: leaves separated by commas (not whitespace)\n"
        "   ----------------------------------------------------------------------\n"
        "   Catalog section : §12.1c complex entity instances\n"
        "   Sources         : T025, Q046, G088, N032\n"
        "   See also        : Ls010, Ls048\n"
        "   ----------------------------------------------------------------------\n"
        "   Defect\n"
        "     ISO 10303-21 complex entity leaves must be whitespace-separated:\n"
        "       #N=( LEAF_A(..) LEAF_B(..) LEAF_C(..) )\n"
        "     A writer using commas between leaves (habit from argument lists)\n"
        "     produces a token that a strict reader must reject.\n"
        "   Expected behavior\n"
        "     Reject comma-separated leaves in strict mode;\n"
        "     lenient mode may accept-with-warning.\n"
        "   ----------------------------------------------------------------------\n"
        "*/\n"
        "ISO-10303-21;\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Ls047 - complex entity leaves separated by commas'),'2;1');\n"
        "FILE_NAME('Ls047.stp','2026-06-20T00:00:00',('auto-generated'),(''),\n"
        "  'auto-generated','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=LENGTH_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.0),#2);\n"
        "#2=( NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.) );\n"
        "/* Correct reference for context */\n"
        "#9=( NAMED_UNIT(*) SI_UNIT(.MILLI.,.RADIAN.) );\n"
        "/* Defect: commas between complex-entity leaves (should be whitespace only) */\n"
        "#10=( CONVERSION_BASED_UNIT('DEG',#9), NAMED_UNIT(*), PLANE_ANGLE_UNIT() );\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


f.render = _render_comma_separated_leaves  # type: ignore[method-assign]
