"""Ls031 — Forward-slash inside `/* .. */` comment treated as nested-comment open.

Catalog claim: ISO 10303-21 comments do not nest. A naive scanner that re-fires on
inner `/*` (or fails to require both `*` and `/` consecutively for close) desynchronizes
when comments contain Windows paths or URLs.

Reproducer recipe: `/* path C:/foo/bar */` and `/* outer /* inner */ should still be comment */`

Byte assertions:
  contains(b'/* outer /*')
  count(b'/*') >= 2

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ls031",
    defect=(
        "Forward-slash inside /* .. */ comment treated as nested-comment open in STEP file; "
        "ISO 10303-21 comments do not nest; "
        "a naive scanner that re-fires on inner /* "
        "or fails to require both * and / consecutively for close "
        "desynchronizes when comments contain Windows paths or URLs; "
        "defect 1: comment containing a Windows path (C:/foo/bar) "
        "which looks like a nested comment open after the colon; "
        "defect 2: comment containing /* inner */ where the outer comment "
        "should still be open after the inner */ is consumed; "
        "expected kernel behavior: heal and accept — "
        "only */ ends a comment; /* within a comment is literal text; "
        "after the first */ everything else is code; "
        "OCCT silently accepts with diagnostic but loads empty result; "
        "OCC auto-heals a spec-level violation; "
        "synonyms: nested comment in STEP, Windows path inside STEP comment breaks scanner, "
        "URL in STEP comment opens nested comment, /*/ inside STEP comment, "
        "comment nesting confusion; "
        "GEOMETRIC_CURVE_SET IS NOT used — raw entities are the defect carriers"
    ),
)

_original_render = f.render


def _render_nested_comment() -> str:
    header = f._render_header()
    return (
        "/* Ls031 - Forward-slash inside comment treated as nested-comment open\n"
        "   ----------------------------------------------------------------------\n"
        "   Catalog section : §12.1c comments\n"
        "   Sources         : T003, N029\n"
        "   ----------------------------------------------------------------------\n"
        "   Defect\n"
        "     ISO 10303-21 comments do not nest. A naive scanner that re-fires on\n"
        "     inner /* desynchronizes when comments contain Windows paths or URLs.\n"
        "   Expected behavior\n"
        "     Heal and accept: only */ ends a comment; /* within a comment is literal\n"
        "     text. After the first */ everything else is code.\n"
        "   ----------------------------------------------------------------------\n"
        "*/\n"
        "ISO-10303-21;\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Ls031 - nested comment open from slash in comment'),'2;1');\n"
        "FILE_NAME('Ls031.stp','2026-06-20T00:00:00',('auto-generated'),(''),\n"
        "  'auto-generated','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "/* Defect 1: Windows path inside comment -- the C: is NOT a nested comment open */\n"
        "/* source file: C:/models/step/export.stp revision 3 */\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "/* Defect 2: nested /* marker inside comment -- outer /* inner */ still comment */\n"
        "#2=DIRECTION('x',(1.,0.,0.));\n"
        "/* outer /* inner comment here */ this text must still be inside outer */\n"
        "#3=CARTESIAN_POINT('p',(1.,1.,0.));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


f.render = _render_nested_comment  # type: ignore[method-assign]
