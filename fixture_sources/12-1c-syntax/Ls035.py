"""Ls035 — Boolean attribute given `.U.` (LOGICAL UNKNOWN at BOOLEAN slot).

Catalog claim: EDGE_CURVE.same_sense is a BOOLEAN (.T./.F.). Passing .U.
(the LOGICAL UNKNOWN value) at this slot conflates LOGICAL with BOOLEAN. Some
readers default to true, leaving an uninitialised bool that produces non-
deterministic edge direction.

Reproducer recipe: EDGE_CURVE('',#12,#13,#14,.U.); — .U. in the BOOLEAN same_sense slot.

Byte assertions:
  contains(b'.U.')
  matches(rb',\.U\.\)')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ls035",
    defect=(
        "Boolean attribute given .U. (LOGICAL UNKNOWN at BOOLEAN slot); "
        "EDGE_CURVE.same_sense is a BOOLEAN attribute accepting only .T. or .F.; "
        "passing .U. (the LOGICAL UNKNOWN value) conflates the LOGICAL type with BOOLEAN; "
        "some readers default to true, leaving an uninitialised bool "
        "that produces non-deterministic edge direction; "
        "regression on gcc 4.9 noted in OCCT 0029944; "
        "expected kernel behavior: reject the value or default to .T. with an explicit warning; "
        "never leave the BOOLEAN uninitialised; "
        "the defect: EDGE_CURVE entity with .U. in the same_sense (BOOLEAN) attribute slot; "
        "see also: Ad044, Ls034, Ls049, Ls050; "
        "synonyms: dot-U at BOOLEAN slot, LOGICAL value in BOOLEAN attribute, "
        "same_sense given .U., STEP boolean given UNKNOWN, uninitialised bool from .U.; "
        "GEOMETRIC_CURVE_SET IS NOT used — raw entities are the defect carriers"
    ),
)

_original_render = f.render


def _render_u_in_boolean() -> str:
    header = f._render_header()
    return (
        "/* Ls035 - Boolean attribute given .U. (LOGICAL UNKNOWN at BOOLEAN slot)\n"
        "   ----------------------------------------------------------------------\n"
        "   Catalog section : §12.1c enumeration token form\n"
        "   Sources         : Q053, G028\n"
        "   See also        : Ad044, Ls034, Ls049, Ls050\n"
        "   ----------------------------------------------------------------------\n"
        "   Defect\n"
        "     EDGE_CURVE.same_sense is BOOLEAN (.T./.F. only). Passing .U.\n"
        "     (LOGICAL UNKNOWN) conflates LOGICAL with BOOLEAN. Some readers\n"
        "     default to true, leaving an uninitialised bool; non-deterministic\n"
        "     edge direction results. OCCT 0029944 (gcc 4.9 regression).\n"
        "   Expected behavior\n"
        "     Reject .U. at a BOOLEAN slot; or default to .T. with explicit warning;\n"
        "     never leave the BOOLEAN uninitialised.\n"
        "   ----------------------------------------------------------------------\n"
        "*/\n"
        "ISO-10303-21;\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Ls035 - .U. LOGICAL UNKNOWN in BOOLEAN same_sense slot'),'2;1');\n"
        "FILE_NAME('Ls035.stp','2026-06-20T00:00:00',('auto-generated'),(''),\n"
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
        "/* Defect: .U. in the same_sense BOOLEAN slot of EDGE_CURVE */\n"
        "#8=EDGE_CURVE('',#6,#7,#5,.U.);\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


f.render = _render_u_in_boolean  # type: ignore[method-assign]
