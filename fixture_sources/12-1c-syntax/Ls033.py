"""Ls033 — Whitespace handling: tab/CR/LF/FF as token separators or ignored chars.

Catalog claim: ISO 10303-21 §5.2 says LF, CR, TAB, FF are ignored characters;
§5.6 says only SPACE, comments, and print directives separate tokens. Real-world
parsers tolerate any ASCII whitespace as a separator. The critical defect is
embedded whitespace inside `#NNN` references (between `#` and digits).

Reproducer recipe: `# 12 = CARTESIAN_POINT(..)` — space between # and instance digits.

Byte assertions:
  matches(rb'#\s+\d') or matches(rb'\t')
  matches(rb'#\s+\d')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ls033",
    defect=(
        "Whitespace handling defects: tab/CR/LF/FF as token separators or ignored chars; "
        "ISO 10303-21 §5.2 says LF, CR, TAB, FF are ignored characters; "
        "§5.6 says only SPACE, comments, and print directives separate tokens; "
        "strict reading: #1\\t=\\tCARTESIAN_POINT(..) after tab-removal becomes "
        "#1=CARTESIAN_POINT(..) which is fine, "
        "but # 12 = ENTITY(..) has whitespace inside the instance-ID reference "
        "which is a defect because # followed by space followed by digits "
        "could be mistaken for #12 after whitespace collapsing; "
        "defect 1: whitespace (space) between # and the instance number digits "
        "in a definition: # 1=CARTESIAN_POINT(..) — embedded whitespace inside #N; "
        "defect 2: TAB characters used as token separators throughout the DATA section; "
        "real-world parsers tolerate any ASCII whitespace as a separator but strict "
        "readers must reject embedded whitespace inside the #N token; "
        "see also: Le028; "
        "synonyms: tab as STEP token separator, FF as token separator, "
        "tab between # and =, ignored char inside STEP token, "
        "whitespace handling in STEP scanner; "
        "GEOMETRIC_CURVE_SET IS NOT used — raw entities are the defect carriers"
    ),
)

_original_render = f.render


def _render_whitespace_defects() -> str:
    header = f._render_header()
    return (
        "/* Ls033 - Whitespace handling: tab/CR/LF/FF as token separators\n"
        "   ----------------------------------------------------------------------\n"
        "   Catalog section : §12.1c whitespace\n"
        "   Sources         : T031, T032, T037, N030, N031\n"
        "   See also        : Le028\n"
        "   ----------------------------------------------------------------------\n"
        "   Defect\n"
        "     ISO 10303-21 §5.2: LF, CR, TAB, FF are ignored characters.\n"
        "     §5.6: only SPACE, comments, and print directives separate tokens.\n"
        "     Critical defect: embedded whitespace inside #NNN reference\n"
        "     (between # and digits) — this changes what the tokenizer reads.\n"
        "     Defect 1: space between # and instance number: # 1=...\n"
        "     Defect 2: TAB characters used as token separators.\n"
        "   Expected behavior\n"
        "     Reject embedded whitespace inside #N (between # and digits);\n"
        "     treat any ASCII whitespace as separator elsewhere.\n"
        "   ----------------------------------------------------------------------\n"
        "*/\n"
        "ISO-10303-21;\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Ls033 - whitespace inside instance-ID and TAB separators'),'2;1');\n"
        "FILE_NAME('Ls033.stp','2026-06-20T00:00:00',('auto-generated'),(''),\n"
        "  'auto-generated','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Defect 1: space between # and instance number -- # 1 is NOT #1 per §5.6 */\n"
        "# 1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "/* Defect 2: TAB characters used as token separators throughout */\n"
        "#2\t=\tCARTESIAN_POINT('p1',(1.,0.,0.));\n"
        "#3\t=\tDIRECTION('x',(1.,0.,0.));\n"
        "/* Defect 3: space inside back-reference -- # 1 as argument */\n"
        "#4=VECTOR('v',# 3,1.);\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


f.render = _render_whitespace_defects  # type: ignore[method-assign]
