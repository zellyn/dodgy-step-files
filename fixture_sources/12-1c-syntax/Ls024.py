"""Ls024 — Tail garbage after end marker.

Catalog claim: Material appearing after `END-ISO-10303-21;`; appended log lines,
multiple concatenated files, or stray `DATA;ENDSEC;` blocks. Greedy regex parsers
may match across boundaries.

Reproducer recipe: `END-ISO-10303-21;\n<garbage bytes>` or
`..ENDSEC;DATA;ENDSEC;DATA;..END-ISO-10303-21;`

Byte assertions:
  matches(rb'(?s)END-ISO-10303-21;.+\\S')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ls024",
    defect=(
        "Tail garbage after end marker in STEP file; "
        "material appearing after END-ISO-10303-21; such as appended log lines "
        "or multiple concatenated files or stray DATA;ENDSEC; blocks; "
        "greedy regex parsers may match across the end-marker boundary; "
        "ISO 10303-21 specifies that END-ISO-10303-21; is the final token in the file; "
        "kernels must stop reading at the first end marker "
        "and treat trailing bytes as a warning to discard; "
        "must reject a second DATA; block appearing at top level after the end marker; "
        "cross-oracle: pure-Python Part-21 validator rejects (E_NO_CLOSE); "
        "OCCT silently accepts (load is empty); "
        "OCC auto-heals a spec-level violation; "
        "synonyms: garbage after STEP end marker, log lines after END-ISO-10303-21, "
        "concatenated STEP files, data after STEP terminator, stray DATA after end marker; "
        "GEOMETRIC_CURVE_SET IS NOT used — raw entities are the defect carriers"
    ),
)

_original_render = f.render


def _render_tail_garbage() -> str:
    header = f._render_header()
    return (
        "/* Ls024 - Tail garbage after end marker\n"
        "   ----------------------------------------------------------------------\n"
        "   Catalog section : §12.1c structural / framing\n"
        "   Sources         : A025, N002 (notes)\n"
        "   See also        : Ad080\n"
        "   ----------------------------------------------------------------------\n"
        "   Defect\n"
        "     Material appearing after END-ISO-10303-21;: appended log lines,\n"
        "     concatenated STEP files, or stray DATA;ENDSEC; blocks. Greedy regex\n"
        "     parsers may match across the boundary.\n"
        "   Expected behavior\n"
        "     Stop reading at the first end marker; treat trailing bytes as a\n"
        "     warning and discard. Reject a second DATA; block at top level.\n"
        "   ----------------------------------------------------------------------\n"
        "*/\n"
        "ISO-10303-21;\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Ls024 - tail garbage after end marker'),'2;1');\n"
        "FILE_NAME('Ls024.stp','2026-06-20T00:00:00',('auto-generated'),(''),\n"
        "  'auto-generated','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=DIRECTION('x',(1.,0.,0.));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
        "/* Defect: everything below this line is tail garbage after the end marker */\n"
        "Export completed at 2026-06-20T00:00:00Z\n"
        "Total entities: 2\n"
        "DATA;\n"
        "#100=CARTESIAN_POINT('stray',(9.,9.,9.));\n"
        "ENDSEC;\n"
    )


f.render = _render_tail_garbage  # type: ignore[method-assign]
