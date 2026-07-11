"""Ls054 — Empty complex (subsuper) instance `#1=();` (zero constituent records).

Catalog claim: a complex (subsuper / combined-entity) instance is written as a
parenthesized list of simple records, e.g. `#1=(A(...)B(...))`. ruststep's
`subsuper_record` (`many0(simple_record)`) accepts an EMPTY list `()`, i.e. a
complex instance with ZERO constituent records. A complex instance must
combine at least one (really at least two) simple records; the empty form is
meaningless.

Distinct from Ls013 (`PRODUCT()` — keyword present, no attributes): here there
is no keyword at all, just `()`.

Reproducer recipe:
  #1=();                              -- empty complex instance
  #3=GEOMETRIC_SET('gs',(#1,#2));     -- #1 is reachable (referenced)

Byte assertions:
  contains(b'#1=();')
  matches(rb'#\d+=\(\)\s*;')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a

Pattern-mined from ricosjp/ruststep data.rs::subsuper_record (Apache-2.0/MIT
— pattern only, no bytes copied).
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ls054",
    defect=(
        "empty complex (subsuper) instance with zero constituent records; "
        "a complex / combined-entity instance is a parenthesized list of simple "
        "records, but the fixture writes #1=() with an EMPTY list; "
        "a many0-style parser accepts the empty form even though a complex "
        "instance must combine at least one (really at least two) simple records; "
        "the empty complex #1 is reachable — referenced as a GEOMETRIC_SET item; "
        "distinct from Ls013 (PRODUCT() has a keyword and no attributes); here "
        "there is no keyword at all, just (); "
        "expected kernel behavior: reject an empty complex instance; the lexer "
        "may accept () as a zero-record list but the semantic layer must reject; "
        "see also Ls013; "
        "synonyms: empty subsuper instance, complex entity with no records, "
        "keyword-less empty parens instance, zero-record combined entity, "
        "STEP empty complex #1=(); "
        "the empty complex instance is the defect carrier"
    ),
)


def _render_empty_complex() -> str:
    header = f._render_header()
    return (
        "ISO-10303-21;\n"
        f"/* {f.catalog_id}: {f.defect} */\n"
        f"{header}\n"
        "DATA;\n"
        "/* Defect: a subsuper (complex) instance with ZERO constituent simple\n"
        "   records. A complex instance must combine >=1 (really >=2) records. */\n"
        "#1=();\n"
        "#2=CARTESIAN_POINT('p',(0.,0.,0.));\n"
        "/* #1 (empty complex) is reachable: referenced as a GEOMETRIC_SET item. */\n"
        "#3=GEOMETRIC_SET('gs',(#1,#2));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


f.render = _render_empty_complex  # type: ignore[method-assign]
