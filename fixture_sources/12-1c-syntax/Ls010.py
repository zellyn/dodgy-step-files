"""Ls010 — Complex / multiple-inheritance entity record: non-alphabetic leaf ordering.

Catalog claim: Multiple-inheritance entities are encoded as parts
whitespace-separated inside outer parens: `#1=( A() B() C() )`. The
external mapping requires alphabetic leaf order; a writer that emits
leaves in arbitrary order produces a record that compliant readers
should warn about (not reject).

Reproducer recipe:
  #10=( CONVERSION_BASED_UNIT('DEG',#9) NAMED_UNIT(*) PLANE_ANGLE_UNIT() );
  and the same with leaves reordered:
  #20=( PLANE_ANGLE_UNIT() NAMED_UNIT(*) CONVERSION_BASED_UNIT('DEG',#9) );

Byte assertions:
  matches(rb'#\\d+\\s*=\\s*\\(\\s*[A-Z_]+\\(')
  count(b'NAMED_UNIT(*)') >= 1 or contains(b'PLANE_ANGLE_UNIT()')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ls010",
    defect=(
        "Complex entity record with non-alphabetic leaf ordering; "
        "ISO 10303-21 external mapping requires alphabetically ordered leaves "
        "in multiple-inheritance complex entity records: ( A() B() C() ); "
        "a writer that emits leaves in arbitrary order produces a record "
        "that compliant readers must warn about; "
        "defect 1: well-formed alphabetic order: "
        "( CONVERSION_BASED_UNIT('DEG',#9) NAMED_UNIT(*) PLANE_ANGLE_UNIT() ) — "
        "leaves are alphabetic (C before N before P); "
        "defect 2: same leaves reordered non-alphabetically: "
        "( PLANE_ANGLE_UNIT() NAMED_UNIT(*) CONVERSION_BASED_UNIT('DEG',#9) ) — "
        "P before N before C violates the external-mapping alphabetic requirement; "
        "conformant reader must warn on non-alphabetic input but must not reject; "
        "sort internally for dispatch; preserve round-trip order; "
        "OCC silently accepts with no diagnostic and loads empty result; "
        "synonyms: complex entity leaves out of order, "
        "multiple-inheritance leaves not alphabetic, STEP complex record wrong order, "
        "leaf order divergent from external mapping, complex entity ordering error; "
        "GEOMETRIC_CURVE_SET IS NOT used — complex-instance entities are the defect carriers"
    ),
)

_original_render = f.render


def _render_nonalpha_leaves() -> str:
    header = f._render_header()
    return (
        f"ISO-10303-21;\n"
        f"/* {f.catalog_id}: {f.defect} */\n"
        f"{header}\n"
        f"DATA;\n"
        f"/* Reference SI plane-angle unit for the CONVERSION_BASED_UNIT below. */\n"
        f"#9=( NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.) );\n"
        f"/* Well-formed: leaves in alphabetic order (C, N, P). */\n"
        f"#10=( CONVERSION_BASED_UNIT('DEG',#9) NAMED_UNIT(*) PLANE_ANGLE_UNIT() );\n"
        f"/* Defect: same leaves in non-alphabetic order (P, N, C). */\n"
        f"/* ISO 10303-21 external mapping requires alphabetic order. */\n"
        f"#20=( PLANE_ANGLE_UNIT() NAMED_UNIT(*) CONVERSION_BASED_UNIT('DEG',#9) );\n"
        f"ENDSEC;\n"
        f"END-ISO-10303-21;\n"
    )


f.render = _render_nonalpha_leaves  # type: ignore[method-assign]
