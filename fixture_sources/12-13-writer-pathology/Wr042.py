"""Wr042 — Inconsistent end-of-record terminator: ';\\n' and ';\\r\\n' mixed in same file.

Catalog claim: records inside a single DATA section terminate with mixed ;\\n and ;\\r\\n
line endings. The spec is silent on line-ending conformance; tools that line-count for
diagnostics report inconsistent line numbers, content-hash caches see the file as
different on each export, and editors display the file as binary.
Bug-reporter language: "STEP file mixed newlines per record",
"diff of exports is full of line-ending changes".

Reproducer recipe: a DATA section where alternate records terminate with ;\\n and ;\\r\\n —
for example #1=APPLICATION_CONTEXT(...);\\ n followed by #2=PRODUCT_CONTEXT(...);\\r\\n.

Byte assertions:
  contains(b';\\r\\n') and contains(b';\\n')
  count(b'\\r\\n') >= 1 and count(b'\\n') >= 5

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=process_signal
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Wr042",
    defect=(
        "inconsistent end-of-record terminator: ;LF and ;CRLF mixed in same file; "
        "input: DATA section records alternate between ;LF and ;CRLF terminators — "
        "one pass used a buffered text stream (LF) and another pass used a Windows "
        "line-ending logger (CRLF), interleaved within the same DATA section; "
        "spec is silent on line-ending conformance (whitespace is whitespace) but "
        "line-counting diagnostics report inconsistent line numbers, content-hash caches "
        "see the file as different on each export, and editors display the file as binary; "
        "produced by multi-pass writers where different passes use different newline conventions; "
        "expected kernel behavior: parsers must accept (whitespace tolerance); "
        "writers should emit deterministic per-file line endings; normaliser is simplest fix; "
        "synonyms: STEP file mixed newlines per record, diff of exports is full of "
        "line-ending changes, writer outputs CRLF then LF inconsistently"
    ),
)


def _render_wr042() -> str:
    """Render a Part-21 with mixed ;LF and ;CRLF line terminators.

    Returns a plain string with \\r\\n for CRLF records; write() encodes to raw bytes
    to preserve the exact byte sequence. The string form is the source of truth for
    the fixture source check; the bytes written to disk are the source of truth for
    byte assertions.
    """
    # Alternate between LF-only and CRLF terminators per record.
    # CRLF records use \r\n; LF records use \n.
    return (
        "ISO-10303-21;\n"
        "/* Wr042: inconsistent line terminators: ;LF and ;CRLF mixed in DATA section */\n"
        "/* Alternate records use LF and CRLF terminators (two-pass writer bug) */\n"
        "/* Parser accepts both; byte-hash tools and editors see inconsistency */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Wr042: mixed line endings per record'),'2;1');\n"
        "FILE_NAME('Wr042.stp','2026-06-17T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* DEFECT: alternating ;LF and ;CRLF terminators within the DATA section */\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\r\n"
        "#2=CARTESIAN_POINT('px',(1.,0.,0.));\n"
        "#3=CARTESIAN_POINT('py',(0.,1.,0.));\r\n"
        "#4=CARTESIAN_POINT('pz',(0.,0.,1.));\n"
        "#5=DIRECTION('xdir',(1.,0.,0.));\r\n"
        "#6=DIRECTION('zdir',(0.,0.,1.));\n"
        "#7=GEOMETRIC_CURVE_SET('mixed-eol-shape',(#1,#2,#3,#4));\r\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_wr042(path) -> None:
    # Encode to bytes directly to preserve the mixed CRLF/LF exactly.
    Path(path).write_bytes(_render_wr042().encode("utf-8"))


f.render = _render_wr042   # type: ignore[method-assign]
f.write = _write_wr042     # type: ignore[method-assign]
