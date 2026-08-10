"""Ls057 — EXPRESS-style `--` line comment in a Part-21 body swallows the entity that follows it.

Catalog claim: ISO 10303-21 §6.3 defines exactly one comment form for the
exchange (Part-21) file — the block comment `/* ... */`. The double-hyphen
`--` end-of-line comment is EXPRESS (Part-11 / `.exp` schema) syntax and is
NOT valid in a Part-21 exchange file. A reader that reuses an EXPRESS lexer
for its Part-21 tokenizer (a common shortcut) treats `--` as a line comment
and silently swallows the rest of that physical line — including a live
entity instance and its terminating `;`. A conforming Part-21 reader instead
sees `--` as two consecutive minus tokens, i.e. a lexical error.

This is a cross-reader conformance trap for a NEW kernel: keep EXPRESS
`--` comment handling out of the Part-21 lexer, or a real entity on the same
line vanishes with no diagnostic. Pattern-mined from ricosjp/ruststep #71
(bare `--` tail comment mis-scopes the following content) — Apache-2.0/MIT,
pattern only, no bytes copied. Sibling of Ls056 (also ruststep-derived,
block-comment non-nesting).

Byte assertions:
  contains(b'-- EXPRESS line comment')
  matches(rb"--[^\\n]*CARTESIAN_POINT\\('swallowed'")

Tier-3: load == "ok"
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ls057",
    defect=(
        "an EXPRESS double-hyphen line comment appears in the Part-21 DATA "
        "section; ISO 10303-21 6.3 permits only slash-star block comments, so "
        "-- is not a valid Part-21 comment; a reader that reuses an EXPRESS "
        "lexer treats -- as an end-of-line comment and swallows the rest of "
        "that physical line, including a live CARTESIAN_POINT entity and its "
        "terminating semicolon, with no diagnostic; a conforming reader sees "
        "-- as two minus tokens and a lexical error; expected kernel behavior: "
        "reject the double-hyphen as invalid Part-21 punctuation, or at minimum "
        "never let EXPRESS line-comment handling drop a real entity silently; "
        "synonyms: double-hyphen comment in STEP, EXPRESS line comment in "
        "Part-21, dash-dash comment swallows entity, end-of-line comment "
        "exchange file, EXPRESS lexer leaks into Part-21; the double-hyphen and "
        "the swallowed CARTESIAN_POINT are the defect carriers"
    ),
)


def _render_dashdash_comment() -> str:
    header = f._render_header()
    return (
        "ISO-10303-21;\n"
        f"/* {f.catalog_id}: {f.defect} */\n"
        f"{header}\n"
        "DATA;\n"
        "#1=DIRECTION('d',(1.,0.,0.));\n"
        "-- EXPRESS line comment (illegal in Part-21); an EXPRESS-lexer reader "
        "swallows the rest of this line: #2=CARTESIAN_POINT('swallowed',(0.,0.,0.));\n"
        "#3=DIRECTION('after',(0.,1.,0.));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


f.render = _render_dashdash_comment  # type: ignore[method-assign]
