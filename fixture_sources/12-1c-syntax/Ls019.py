"""Ls019 — Missing closing `)` of an aggregate (paren imbalance).

Catalog claim: A truncated coordinate list like `((1.,2.,3.),(4.,5.,6.)` (one `)` short)
causes scanners to walk past the `;` of the next instance. Common when nested aggregates
contain empty inner lists (`(())` vs `()`).

Reproducer recipe: #1=IFCPOLYLINE((#2,#3,#4); #5=..

Byte assertions:
  matches(rb'IFCPOLYLINE\\(\\(#\\d+,#\\d+,#\\d+\\);')
  matches(rb'\\(#\\d+,#\\d+,#\\d+\\);')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ls019",
    defect=(
        "Missing closing parenthesis of an aggregate causes paren imbalance in STEP file; "
        "a truncated coordinate list like ((1.,2.,3.),(4.,5.,6.) with one ) short "
        "causes scanners to walk past the ; of the next instance; "
        "common when nested aggregates contain empty inner lists or truncated coordinate lists; "
        "ISO 10303-21 requires every open paren to have a matching close paren "
        "before the instance-terminating semicolon; "
        "strict reader must track paren depth per instance "
        "and on ; at depth > 0 reject with unbalanced parentheses naming the unmatched open paren; "
        "defect: IFCPOLYLINE with an outer aggregate opened but not closed "
        "so the semicolon terminates at depth=1; "
        "cross-oracle: pure-Python Part-21 validator rejects (E_PAREN_UNBALANCED); "
        "OCCT silently accepts (load is empty); "
        "OCC auto-heals a spec-level violation; "
        "synonyms: missing closing paren in STEP aggregate, paren imbalance in STEP, "
        "unbalanced parens in coordinate list, truncated nested aggregate, "
        "STEP aggregate closes wrong number of parens; "
        "GEOMETRIC_CURVE_SET IS NOT used — raw entities are the defect carriers"
    ),
)

_original_render = f.render


def _render_paren_imbalance() -> str:
    header = f._render_header()
    return (
        "/* Ls019 - Missing closing ) of an aggregate (paren imbalance)\n"
        "   ----------------------------------------------------------------------\n"
        "   Catalog section : §12.1c punctuation\n"
        "   Sources         : T043, N050\n"
        "   ----------------------------------------------------------------------\n"
        "   Defect\n"
        "     A truncated coordinate list like ((1.,2.,3.),(4.,5.,6.) (one ) short)\n"
        "     causes scanners to walk past the ; of the next instance. Common when\n"
        "     nested aggregates contain empty inner lists (()) vs ().\n"
        "   Expected behavior\n"
        "     Track paren depth per instance; on ; at depth>0, reject with\n"
        "     'unbalanced parentheses' naming the unmatched open paren.\n"
        "   ----------------------------------------------------------------------\n"
        "*/\n"
        "ISO-10303-21;\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Ls019 - missing closing paren in aggregate'),'2;1');\n"
        "FILE_NAME('Ls019.stp','2026-06-20T00:00:00',('auto-generated'),(''),\n"
        "  'auto-generated','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('p1',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('p2',(1.,0.,0.));\n"
        "#3=CARTESIAN_POINT('p3',(1.,1.,0.));\n"
        "/* Defect: outer aggregate opened but never closed before semicolon (depth=1 at ;) */\n"
        "#4=IFCPOLYLINE((#1,#2,#3);\n"
        "#5=DIRECTION('x',(1.,0.,0.));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


f.render = _render_paren_imbalance  # type: ignore[method-assign]
