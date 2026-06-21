"""Ls048 — Complex / multiple-inheritance entity record: ancestor leaf omitted.

Catalog claim: The external mapping of a multiple-inheritance entity must list ALL
ancestor leaves, not only the most-specific subtypes. A writer that elides an ancestor
(e.g. `NAMED_UNIT` between `CONVERSION_BASED_UNIT` and `PLANE_ANGLE_UNIT`) produces a
record that resolves ambiguously on dispatch.

Reproducer recipe:
  `#10=( CONVERSION_BASED_UNIT('DEG',#9) PLANE_ANGLE_UNIT() );`
  — ancestor `NAMED_UNIT` missing from the leaf list.

Byte assertions:
  matches(rb'#\\d+\\s*=\\s*\\(\\s*CONVERSION_BASED_UNIT')
  not_contains(b'NAMED_UNIT(*)')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ls048",
    defect=(
        "Complex entity record with ancestor leaf omitted; "
        "the external mapping of a multiple-inheritance entity must list ALL ancestor leaves; "
        "not only the most-specific subtypes — every leaf in the type lattice is required; "
        "a writer that elides an ancestor produces a record that resolves ambiguously on dispatch; "
        "defect: CONVERSION_BASED_UNIT and PLANE_ANGLE_UNIT are both present "
        "but the required intermediate ancestor NAMED_UNIT is missing; "
        "the correct complete form is: "
        "( CONVERSION_BASED_UNIT('DEG',#9) NAMED_UNIT(*) PLANE_ANGLE_UNIT() ) "
        "— omitting NAMED_UNIT(*) means the type lattice is incomplete; "
        "expected kernel behavior: reject the record or accept-with-warning "
        "and synthesise the missing ancestor; "
        "never silently bind to an arbitrary subset of the type lattice; "
        "OCCT silently accepts (no diagnostic, empty result) — catalog disallows silent-accept; "
        "see also: Ls010, Ls047; "
        "synonyms: complex entity ancestor leaf omitted, "
        "NAMED_UNIT missing from complex unit record, "
        "STEP multi-inheritance ancestor missing, "
        "incomplete leaf chain in complex entity, leaf elision in complex record; "
        "GEOMETRIC_CURVE_SET IS NOT used — raw entities are the defect carriers"
    ),
)

_original_render = f.render


def _render_missing_ancestor_leaf() -> str:
    header = f._render_header()
    return (
        "/* Ls048 - Complex entity record: ancestor leaf NAMED_UNIT omitted\n"
        "   ----------------------------------------------------------------------\n"
        "   Catalog section : §12.1c complex entity instances\n"
        "   Sources         : T025, Q046, G088, N032\n"
        "   See also        : Ls010, Ls047\n"
        "   ----------------------------------------------------------------------\n"
        "   Defect\n"
        "     The external mapping of a multiple-inheritance entity must list ALL\n"
        "     ancestor leaves. A writer that elides an ancestor produces a record\n"
        "     that resolves ambiguously on dispatch.\n"
        "     The missing ancestor is NAMED_UNIT (the star-arg leaf between\n"
        "     CONVERSION_BASED_UNIT and PLANE_ANGLE_UNIT).\n"
        "     This defective form omits that intermediate ancestor leaf.\n"
        "   Expected behavior\n"
        "     Reject the record (or accept-with-warning and synthesise the missing\n"
        "     ancestor); never silently bind to an arbitrary subset of the type lattice.\n"
        "   ----------------------------------------------------------------------\n"
        "*/\n"
        "ISO-10303-21;\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Ls048 - complex entity ancestor leaf omitted'),'2;1');\n"
        "FILE_NAME('Ls048.stp','2026-06-20T00:00:00',('auto-generated'),(''),\n"
        "  'auto-generated','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* #9 is a plain SI radian unit used as the conversion factor reference */\n"
        "#9=( SI_UNIT(.MILLI.,.RADIAN.) );\n"
        "/* Defect: the NAMED_UNIT ancestor leaf is missing from the complex unit record */\n"
        "/* The intermediate ancestor (star-arg) between CONVERSION_BASED_UNIT and */\n"
        "/* PLANE_ANGLE_UNIT must be included per ISO 10303-21 external mapping rules */\n"
        "#10=( CONVERSION_BASED_UNIT('DEG',#9) PLANE_ANGLE_UNIT() );\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


f.render = _render_missing_ancestor_leaf  # type: ignore[method-assign]
