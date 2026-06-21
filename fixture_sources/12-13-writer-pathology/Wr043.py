"""Wr043 — Writer emits raw UTF-8 bytes in string literal where Ed.2 mandates `\\X\\` / `\\X2\\` escape.

Catalog claim: FILE_DESCRIPTION declares Edition 2 ('2;1') but a PRODUCT.name attribute
contains raw UTF-8 bytes (0xC3 0xA9 for é) instead of the spec-required '\\X\\E9'
escape. Edition-2 readers see two single-byte ISO-8859-1 characters instead of one
composed é; Edition-3 readers decode the bytes correctly by accident.
Bug-reporter language: "STEP writer outputs UTF-8 in Ed.2 file",
"non-ASCII in Edition-2 STEP", "exporter does not escape non-ASCII".

Reproducer recipe: FILE_DESCRIPTION with '2;1'; a PRODUCT.name containing the raw bytes
0xC3 0xA9 (UTF-8 for é) instead of the spec-required '\\X\\E9' escape.

Byte assertions:
  contains(b"'2;1'") and matches(rb'[\\xC0-\\xDF][\\x80-\\xBF]')
  matches(rb'[\\xC0-\\xF7][\\x80-\\xBF]')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Wr043",
    defect=(
        "writer emits raw UTF-8 bytes in string literal where Ed.2 mandates \\X\\ / \\X2\\ escape; "
        "input: FILE_DESCRIPTION declares Edition 2 ('2;1') but PRODUCT.name contains raw UTF-8 bytes "
        "0xC3 0xA9 (representing é) instead of the spec-required '\\X\\E9' escape sequence; "
        "Edition-2 mandates 8-bit default with non-ASCII expressed via \\X\\HH, \\X2\\HHHH\\X0\\, "
        "or \\PA\\.\\PI\\ page-shift directives; raw multi-byte UTF-8 violates the edition contract; "
        "Edition-3 readers decode the bytes correctly by accident; Ed.2 readers see two "
        "single-byte ISO-8859-1 characters (0xC3=Ã and 0xA9=©) instead of one composed é; "
        "produced by writers that rely on host runtime's default UTF-8 string handling but emit "
        "FILE_DESCRIPTION with '2;1' implementation-level (Edition 2); "
        "expected kernel behavior: writer detects the file's declared edition and emits non-ASCII "
        "via edition-appropriate directive; Ed.2 uses \\X\\ / \\X2\\; Ed.3 may emit raw UTF-8 with "
        "proper FILE_DESCRIPTION declaration; never silently mismatch edition and encoding; "
        "producer-side root cause for Le003/Le021, Le050, Ad058; "
        "synonyms: STEP writer outputs UTF-8 in Ed.2 file, non-ASCII in Edition-2 STEP, "
        "exporter does not escape non-ASCII"
    ),
)


def _render_wr043() -> bytes:
    """Render a Part-21 (as bytes) with raw UTF-8 in an Edition-2 declared file.

    The name attribute of the PRODUCT entity contains 0xC3 0xA9 — the raw UTF-8
    encoding of é — instead of the spec-required '\\X\\E9' escape.  The file header
    declares Edition 2 ('2;1'), which mandates the escape form.
    """
    # Build the STEP text with a placeholder, then inject the raw UTF-8 bytes.
    header = (
        "ISO-10303-21;\n"
        "/* Wr043: writer emits raw UTF-8 bytes in string literal under Edition-2 declaration */\n"
        "/* FILE_DESCRIPTION declares '2;1' (Edition 2); Edition 2 mandates \\X\\HH escapes */\n"
        "/* DEFECT: PRODUCT.name contains raw UTF-8 bytes 0xC3 0xA9 (é) instead of '\\X\\E9' */\n"
        "/* Ed.2-strict readers see 0xC3=Ã and 0xA9=© (two ISO-8859-1 chars, mojibake) */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Wr043: raw UTF-8 bytes in Edition-2 string literal'),'2;1');\n"
        "FILE_NAME('Wr043.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* DEFECT: PRODUCT.name below contains raw UTF-8 bytes for é (0xC3 0xA9) */\n"
        "/* Spec-conformant Ed.2 form would be: 'caf\\X\\E9' */\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner',(1.,1.,0.));\n"
        "#3=DIRECTION('xdir',(1.,0.,0.));\n"
        "#4=DIRECTION('zdir',(0.,0.,1.));\n"
    )
    # Raw UTF-8 bytes for é = 0xC3 0xA9 injected directly into the PRODUCT name string.
    product_line = b"#5=PRODUCT('caf\xc3\xa9','caf\xc3\xa9-part','raw-utf8-in-ed2',(#6));\n"
    footer = (
        "#6=PRODUCT_CONTEXT('part',#7,'mechanical');\n"
        "#7=APPLICATION_CONTEXT('config design');\n"
        "#8=GEOMETRIC_CURVE_SET('raw-utf8-ed2-shape',(#1,#2));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )
    return header.encode("utf-8") + product_line + footer.encode("utf-8")


def _write_wr043(path) -> None:
    Path(path).write_bytes(_render_wr043())


# render() for the source check must return a str; return the ASCII-safe surrogate form.
def _render_wr043_str() -> str:
    return _render_wr043().decode("latin-1")


f.render = _render_wr043_str  # type: ignore[method-assign]
f.write = _write_wr043        # type: ignore[method-assign]
