"""Ls027 — Legacy SCOPE/ENDSCOPE blocks (Edition 1) and EXPORT lists.

Catalog claim: Edition 1 had inline SCOPE/ENDSCOPE delimiters; Editions 2/3 removed
them but legacy translators still emit them. EXPORT lists also appeared inside ENDSCOPE
in Ed.1. Implementors Issues 001/002 record the disagreement on whether modern processors
must parse SCOPE blocks.

Reproducer recipe:
  DATA;
  #1=PRODUCT(..);
  SCOPE
   #2=..;
  ENDSCOPE;
  ENDSEC;

Byte assertions:
  contains(b'SCOPE') and contains(b'ENDSCOPE')
  count(b'SCOPE') >= 2

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ls027",
    defect=(
        "Legacy SCOPE/ENDSCOPE blocks from Edition 1 present in STEP file; "
        "Edition 1 of ISO 10303-21 had inline SCOPE/ENDSCOPE delimiters; "
        "Editions 2 and 3 removed them but legacy translators still emit them; "
        "EXPORT lists also appeared inside ENDSCOPE in Edition 1; "
        "Implementors Issues 001/002 record the disagreement on whether modern processors "
        "must parse SCOPE blocks; "
        "strict Ed.2/Ed.3 processors must reject the SCOPE keyword as unknown syntax; "
        "lenient processors should skip to matching ENDSCOPE without aborting "
        "and emit a single informational warning per file; "
        "defect 1: SCOPE block wrapping an inner entity (#2) after outer entity (#1); "
        "defect 2: ENDSCOPE followed by EXPORT list (Ed.1 syntax); "
        "synonyms: legacy SCOPE block in STEP, Edition 1 SCOPE/ENDSCOPE, "
        "EXPORT list in STEP, old-style scope delimiters, Ed.1 scope blocks in modern STEP; "
        "GEOMETRIC_CURVE_SET IS NOT used — raw entities are the defect carriers"
    ),
)

_original_render = f.render


def _render_scope_endscope() -> str:
    header = f._render_header()
    return (
        "/* Ls027 - Legacy SCOPE/ENDSCOPE blocks (Edition 1) and EXPORT lists\n"
        "   ----------------------------------------------------------------------\n"
        "   Catalog section : §12.1c legacy structure\n"
        "   Sources         : Q073, N043 (Implementors Issues 001/002)\n"
        "   ----------------------------------------------------------------------\n"
        "   Defect\n"
        "     Edition 1 had inline SCOPE/ENDSCOPE delimiters; Editions 2/3 removed\n"
        "     them but legacy translators still emit them. EXPORT lists also appeared\n"
        "     inside ENDSCOPE in Ed.1. Implementors Issues 001/002 record the\n"
        "     disagreement on whether modern processors must parse SCOPE blocks.\n"
        "   Expected behavior\n"
        "     Strict Ed.2/Ed.3 reject; lenient skip-to-matching-ENDSCOPE without\n"
        "     aborting; emit a single informational warning per file.\n"
        "   ----------------------------------------------------------------------\n"
        "*/\n"
        "ISO-10303-21;\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Ls027 - legacy SCOPE/ENDSCOPE blocks'),'2;1');\n"
        "FILE_NAME('Ls027.stp','2026-06-20T00:00:00',('auto-generated'),(''),\n"
        "  'auto-generated','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "/* Defect: Edition-1 SCOPE block wrapping an inner entity */\n"
        "SCOPE\n"
        "#2=DIRECTION('x',(1.,0.,0.));\n"
        "ENDSCOPE;\n"
        "#3=CARTESIAN_POINT('p1',(1.,0.,0.));\n"
        "/* Defect: second SCOPE block with EXPORT list (Edition-1 syntax) */\n"
        "SCOPE\n"
        "#4=DIRECTION('z',(0.,0.,1.));\n"
        "ENDSCOPE\n"
        "EXPORT(#4);\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


f.render = _render_scope_endscope  # type: ignore[method-assign]
