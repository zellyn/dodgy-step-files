"""Ls050 — Boolean attribute given long-form `.UNKNOWN.`

Catalog claim: `EDGE_CURVE.same_sense` is a BOOLEAN (`.T.`/`.F.`). Passing
`.UNKNOWN.` (the long-form LOGICAL three-state value) is structurally identical
to `.U.` but uses the long token, exercising readers that special-case `.U.`
while accepting `.UNKNOWN.` through a different parser path.

Reproducer recipe: `EDGE_CURVE('',#12,#13,#14,.UNKNOWN.);`

Byte assertions:
  contains(b'.UNKNOWN.')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ls050",
    defect=(
        "Boolean attribute given long-form .UNKNOWN. at EDGE_CURVE.same_sense slot; "
        "EDGE_CURVE.same_sense is a BOOLEAN (.T./.F. only); "
        "passing .UNKNOWN. (the long-form LOGICAL three-state value) is structurally identical "
        "to .U. but uses the long token, exercising readers that special-case .U. "
        "while accepting .UNKNOWN. through a different parser path; "
        "ISO 10303-21: BOOLEAN literals are .T. and .F. only; "
        ".UNKNOWN. is a LOGICAL value not valid at a BOOLEAN slot; "
        "expected kernel behavior: reject the value at the BOOLEAN slot; "
        "never leave the bool uninitialised; "
        "OCCT silently accepts (no diagnostic, empty result) — catalog disallows silent-accept; "
        "see also: Ad044, Ls034, Ls035, Ls049; "
        "synonyms: STEP boolean given .UNKNOWN., long-form UNKNOWN at BOOLEAN slot, "
        "LOGICAL UNKNOWN long form, STEP same_sense .UNKNOWN., "
        "three-state value at BOOLEAN attribute; "
        "GEOMETRIC_CURVE_SET IS NOT used — raw entities are the defect carriers"
    ),
)

_original_render = f.render


def _render_unknown_boolean() -> str:
    header = f._render_header()
    return (
        "/* Ls050 - Boolean attribute given long-form .UNKNOWN.\n"
        "   ----------------------------------------------------------------------\n"
        "   Catalog section : §12.1c enumeration token form\n"
        "   Sources         : Q053, G028\n"
        "   See also        : Ad044, Ls034, Ls035, Ls049\n"
        "   ----------------------------------------------------------------------\n"
        "   Defect\n"
        "     EDGE_CURVE.same_sense is a BOOLEAN (.T./.F. only). Passing\n"
        "     .UNKNOWN. (the long-form LOGICAL three-state value) is structurally\n"
        "     identical to .U. but uses the long token, exercising readers that\n"
        "     special-case .U. while accepting .UNKNOWN. through a different\n"
        "     parser path. BOOLEAN slots do not admit a three-state LOGICAL.\n"
        "   Expected behavior\n"
        "     Reject the value at the BOOLEAN slot; never leave the bool uninitialised.\n"
        "   ----------------------------------------------------------------------\n"
        "*/\n"
        "ISO-10303-21;\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Ls050 - EDGE_CURVE same_sense given long-form .UNKNOWN.'),'2;1');\n"
        "FILE_NAME('Ls050.stp','2026-06-20T00:00:00',('auto-generated'),(''),\n"
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
        "/* Defect: .UNKNOWN. (LOGICAL long-form) at the same_sense BOOLEAN slot */\n"
        "/* Correct form would be: #8=EDGE_CURVE('',#6,#7,#5,.T.); */\n"
        "#8=EDGE_CURVE('',#6,#7,#5,.UNKNOWN.);\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


f.render = _render_unknown_boolean  # type: ignore[method-assign]
