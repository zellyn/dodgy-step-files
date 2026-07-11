"""Ls056 — Non-nesting comment illusion; inner opener leaves a stray closer.

Catalog claim: ISO 10303-21 §6.3 block comments do NOT nest. In
`/* a /* b */ tail */` the comment closes at the FIRST star-slash, so the
inner slash-star is not an opener — it is comment text. Whatever follows the
first closer is LIVE token stream, and the final star-slash is a stray,
unmatched closer (a lexical error). An author who tries to comment out an
entity but nests a second opener inside will have that entity LEAK back into
the parse.

Reproducer recipe:
  /* a /* b */ #2=CARTESIAN_POINT('leaked',(0.,0.,0.)); */
  -- comment = "/* a /* b */"; the CARTESIAN_POINT leaks; trailing "*/" is stray

Byte assertions:
  contains(b'/* a /* b */')
  matches(rb";\s*\*/")
  matches(rb"CARTESIAN_POINT\('leaked'")

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a

Pattern-mined from ricosjp/ruststep combinator.rs::comment (non-nesting)
(Apache-2.0/MIT — pattern only, no bytes copied).
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ls056",
    defect=(
        "non-nesting comment illusion leaves a stray closer and a leaked entity; "
        "ISO 10303-21 6.3 block comments do NOT nest, so in a slash-star opener "
        "that contains a second slash-star, the comment closes at the FIRST "
        "star-slash; the inner opener is just comment text; "
        "the author tried to comment out a CARTESIAN_POINT but nested a second "
        "opener inside, so the CARTESIAN_POINT LEAKS back into the token stream "
        "and the trailing star-slash is a stray, unmatched closer; "
        "expected kernel behavior: treat comments as non-nesting per the spec and "
        "reject the stray closer; document the non-nesting rule clearly; "
        "synonyms: nested comment illusion, comments do not nest, stray star-slash, "
        "leaked entity from comment, unmatched comment closer, "
        "double star-slash after entity; "
        "the stray closer and leaked CARTESIAN_POINT are the defect carriers"
    ),
)


def _render_stray_comment_closer() -> str:
    header = f._render_header()
    return (
        "ISO-10303-21;\n"
        f"/* {f.catalog_id}: {f.defect} */\n"
        f"{header}\n"
        "DATA;\n"
        "#1=DIRECTION('d',(1.,0.,0.));\n"
        "/* Defect: the author tried to comment out an entity but nested a second\n"
        "   comment opener inside. Part-21 comments do NOT nest (ISO 10303-21 6.3):\n"
        "   the comment closes at the FIRST closer, so the CARTESIAN_POINT below\n"
        "   LEAKS back into the token stream and a stray closer follows it. */\n"
        "/* a /* b */ #2=CARTESIAN_POINT('leaked',(0.,0.,0.)); */\n"
        "#3=DIRECTION('after',(0.,1.,0.));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


f.render = _render_stray_comment_closer  # type: ignore[method-assign]
