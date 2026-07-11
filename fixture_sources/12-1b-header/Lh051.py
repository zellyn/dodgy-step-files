"""Lh051 — Leading-zero instance-name aliasing collision (`#1` and `#01`).

Catalog claim: ISO 10303-21 §6.4.4.3 NOTE 2 states that leading zeros in an
entity-instance name are not significant — `#1` and `#01` denote the SAME
instance. A file that defines both silently aliases them; a reference to
`#01` resolves to whichever definition won. Independent parsers that
normalize the name to an integer (e.g. ruststep parses `#001` into `u64`)
collapse the two, while byte-diff and lax readers miss the collision.

Distinct from Lh022 (byte-identical duplicate `#N`): this is duplication
AFTER leading-zero normalization.

Reproducer recipe:
  #1=CARTESIAN_POINT('p1',(0.,0.,0.));
  #01=DIRECTION('d1',(1.,0.,0.));   -- #01 normalizes to name 1, aliases #1
  #2=VECTOR('v',#01,1.);

Byte assertions:
  contains(b'#1=CARTESIAN_POINT')
  contains(b'#01=DIRECTION')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a

Pattern-mined from ricosjp/ruststep token.rs::entity_instance_name
(Apache-2.0/MIT — pattern only, no bytes copied).
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Lh051",
    defect=(
        "leading-zero instance-name aliasing collision; "
        "ISO 10303-21 6.4.4.3 NOTE 2: leading zeros in an entity-instance name "
        "are not significant, so #1 and #01 denote the SAME instance; "
        "the file defines #1 as a CARTESIAN_POINT and #01 as a DIRECTION, which "
        "normalize to the same name 1 and silently alias; #2 references #01, "
        "resolving to whichever definition won; "
        "independent parsers that normalize the name to an integer collapse the "
        "two while byte-diff and lax readers miss the collision; "
        "distinct from Lh022 (byte-identical duplicate); this is duplication "
        "after leading-zero normalization; "
        "expected kernel behavior: reject with E_DUPLICATE_INSTANCE_ID after "
        "leading-zero normalization; never silently overwrite"
    ),
)


def _render_leading_zero_alias() -> str:
    header = f._render_header()
    return (
        "ISO-10303-21;\n"
        f"/* {f.catalog_id}: {f.defect} */\n"
        f"{header}\n"
        "DATA;\n"
        "/* ISO 10303-21 6.4.4.3 NOTE 2: leading zeros in an instance name are\n"
        "   NOT significant; #1 and #01 denote the SAME instance. */\n"
        "#1=CARTESIAN_POINT('p1',(0.,0.,0.));\n"
        "/* Defect: #01 normalizes to name 1 and silently aliases #1 above. */\n"
        "#01=DIRECTION('d1',(1.,0.,0.));\n"
        "/* #2 references #01, which after normalization is the same name as #1. */\n"
        "#2=VECTOR('v',#01,1.);\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


f.render = _render_leading_zero_alias  # type: ignore[method-assign]
