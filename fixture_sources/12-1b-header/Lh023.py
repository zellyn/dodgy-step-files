"""Lh023 — Whitespace, tab, or comment between `#` and digits of an instance ID.

Catalog claim: stepcode tolerates `# 12 = ENT(..)` and even `# /*c*/ 12 =
ENT(..)`; the IfcOpenShell Lark grammar rejects whitespace between `#` and
digits. ISO 10303-21 §5.6 declares `#NNN` a single token, so spaces inside it
are non-conformant. Treating tab as a separator inside an identifier produces
silent corruption (`#1<TAB>2` becomes `#12`). Kernel must strictly reject
whitespace/comment inside `#NNN`; tolerant readers may accept whitespace between
tokens but never inside identifiers, and must warn rather than silently merge
digits.
Bug-reporter language: "whitespace between # and digits of instance ID", "tab
between hash and number in #ID", "comment inside instance reference", "# 12 with
space in STEP", "stepcode tolerates space inside ID".

Reproducer recipe:
  # 12 = IFCPERSON(..); or # /* note */ 12 = IFCPERSON(..); or #1\\t2 = ...

Byte assertions:
  matches(rb'#\\s+\\d+\\s*=') or matches(rb'#/\\*[^*]*\\*/\\d') or matches(rb'#\\d+\\t\\d')
  matches(rb'#\\s+\\d') or matches(rb'#/\\*')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Lh023",
    defect=(
        "Whitespace between # and digits of an instance ID violates ISO 10303-21 §5.6; "
        "input: DATA section contains '# 12 = CARTESIAN_POINT(..)' with a space between "
        "# and the digit sequence; ISO 10303-21 §5.6 declares #NNN a single token — "
        "spaces inside it are non-conformant; "
        "stepcode tolerates '# 12 = ENT(..)' silently; "
        "IfcOpenShell Lark grammar rejects whitespace between # and digits; "
        "treating tab as a separator inside an identifier produces silent corruption "
        "('#1<TAB>2' merged as '#12'); "
        "OCC silently accepts with diagnostic but loads empty result; "
        "expected kernel behavior: strictly reject whitespace/comment inside #NNN; "
        "tolerant readers may accept whitespace between tokens but never inside identifiers; "
        "warn rather than silently merge digits; "
        "see also: Ls038; "
        "synonyms: whitespace between # and digits of instance ID, tab between hash and number in #ID, "
        "comment inside instance reference, # 12 with space in STEP, stepcode tolerates space inside ID"
    ),
)


def _render_lh023() -> str:
    """Render a Part-21 with whitespace between # and digits: '# 12 = CARTESIAN_POINT(..)'."""
    return (
        "ISO-10303-21;\n"
        "/* Lh023: whitespace between # and instance-ID digits */\n"
        "/* ISO 10303-21 §5.6: #NNN is a single token — no spaces allowed inside */\n"
        "/* DEFECT: '# 12 = CARTESIAN_POINT(..)' has a space between # and 12 */\n"
        "/* stepcode: tolerates space silently; IfcOpenShell: rejects; OCC: empty result */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Lh023: whitespace between # and instance ID digits'),'2;1');\n"
        "FILE_NAME('Lh023.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner',(1.,1.,0.));\n"
        "#3=DIRECTION('xdir',(1.,0.,0.));\n"
        "#4=DIRECTION('zdir',(0.,0.,1.));\n"
        "/* DEFECT: space between # and 12 — non-conformant per ISO 10303-21 §5.6 */\n"
        "# 12=CARTESIAN_POINT('defect-space-in-id',(0.5,0.5,0.));\n"
        "#5=GEOMETRIC_CURVE_SET('whitespace-in-id-shape',(#1,#2));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_lh023(path) -> None:
    Path(path).write_text(_render_lh023())


f.render = _render_lh023  # type: ignore[method-assign]
f.write = _write_lh023    # type: ignore[method-assign]
