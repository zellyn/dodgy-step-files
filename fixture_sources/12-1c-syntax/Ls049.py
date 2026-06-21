"""Ls049 — Boolean attribute given bare `TRUE` (no dots).

Catalog claim: `EDGE_CURVE.same_sense` is a BOOLEAN encoded as the dotted enum
`.T.` or `.F.`. A writer that emits the bare keyword `TRUE` (no dots) drops the
enum-token framing required by ISO 10303-21.

Reproducer recipe: `EDGE_CURVE('',#12,#13,#14,TRUE);` — bare `TRUE` token at the
BOOLEAN slot.

Byte assertions:
  matches(rb',\\s*TRUE\\)')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ls049",
    defect=(
        "Boolean attribute given bare TRUE (no dots) at EDGE_CURVE.same_sense slot; "
        "EDGE_CURVE.same_sense is a BOOLEAN encoded as the dotted enum .T. or .F.; "
        "a writer that emits the bare keyword TRUE (no dots) "
        "drops the enum-token framing required by ISO 10303-21; "
        "ISO 10303-21 §11.1.6.4: BOOLEAN literals are .T. and .F. only; "
        "the bare keyword TRUE is not a valid Part-21 token in this position; "
        "distinct from Ls034 in that the BOOLEAN slot of EDGE_CURVE "
        "is the canonical same_sense kernel surface, "
        "where the kernel may default to true on read failure rather than rejecting; "
        "expected kernel behavior: strict reject; "
        "lenient mode may default to .T. with a warning; "
        "see also: Ls034, Ls035, Ls050; "
        "synonyms: bare TRUE without dots in STEP, "
        "BOOLEAN written without dot delimiters, "
        "EDGE_CURVE same_sense bare keyword, "
        "TRUE/FALSE without dot framing, "
        "STEP boolean missing enum dots; "
        "GEOMETRIC_CURVE_SET IS NOT used — raw entities are the defect carriers"
    ),
)

_original_render = f.render


def _render_bare_true_boolean() -> str:
    header = f._render_header()
    return (
        "/* Ls049 - Boolean attribute given bare TRUE (no dots)\n"
        "   ----------------------------------------------------------------------\n"
        "   Catalog section : §12.1c enumeration token form\n"
        "   Sources         : Q053, G028\n"
        "   See also        : Ls034, Ls035, Ls050\n"
        "   ----------------------------------------------------------------------\n"
        "   Defect\n"
        "     EDGE_CURVE.same_sense is a BOOLEAN (.T./.F. only). A writer that\n"
        "     emits the bare keyword TRUE (no dots) drops the enum-token framing\n"
        "     required by ISO 10303-21. Distinct from Ls034 in that the BOOLEAN\n"
        "     slot of EDGE_CURVE is the canonical same_sense kernel surface.\n"
        "   Expected behavior\n"
        "     Strict reject; lenient mode may default to .T. with a warning.\n"
        "   ----------------------------------------------------------------------\n"
        "*/\n"
        "ISO-10303-21;\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Ls049 - EDGE_CURVE same_sense given bare TRUE without dots'),'2;1');\n"
        "FILE_NAME('Ls049.stp','2026-06-20T00:00:00',('auto-generated'),(''),\n"
        "  'auto-generated','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('p1',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('p2',(1.,0.,0.));\n"
        "#3=DIRECTION('dir',(1.,0.,0.));\n"
        "#4=VECTOR('v',#3,1.);\n"
        "#5=LINE('l',#1,#4);\n"
        "#6=VERTEX_POINT('v1',#1);\n"
        "#7=VERTEX_POINT('v2',#2);\n"
        "/* Defect: bare TRUE (no dots) at the same_sense BOOLEAN slot */\n"
        "/* Correct form would be: #8=EDGE_CURVE('',#6,#7,#5,.T.); */\n"
        "#8=EDGE_CURVE('',#6,#7,#5,TRUE);\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


f.render = _render_bare_true_boolean  # type: ignore[method-assign]
