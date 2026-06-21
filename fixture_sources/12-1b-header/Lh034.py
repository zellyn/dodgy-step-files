"""Lh034 — REFERENCE section pointing at unresolvable external anchor.

Catalog claim: Edition-3 ANCHOR / REFERENCE / SIGNATURE sections support
cross-file linking. A REFERENCE entry names an external instance via a URI plus
#anchor_name; the other end (a separate file) must publish that anchor in its
ANCHOR section. When the receiver imports a file with REFERENCE to an
unresolvable target (companion file missing, anchor name misspelt, URI scheme
unsupported), the kernel must report the unresolvable reference with a precise
diagnostic naming the URI and anchor; allow the rest of the file to load with a
placeholder if the implementer's policy is partial-load, otherwise reject
deterministically.
Bug-reporter language: "REFERENCE section unresolvable anchor", "external anchor
not found", "STEP REFERENCE points at missing file", "URI anchor in REFERENCE
unresolved", "broken cross-file STEP link".

Reproducer recipe:
  REFERENCE section listing <file:companion-file.stp#missing_anchor> and
  <https://example.invalid/no-such-file.stp#also_missing>.

Byte assertions:
  contains(b'REFERENCE;') and (contains(b'companion-file.stp#missing_anchor')
    or contains(b'no-such-file.stp#also_missing'))
  contains(b'companion-file.stp') or contains(b'companion.stp')
    or contains(b'no-such-file.stp')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Lh034",
    defect=(
        "REFERENCE section pointing at unresolvable external anchor; "
        "input: REFERENCE section lists <file:companion-file.stp#missing_anchor> and "
        "<https://example.invalid/no-such-file.stp#also_missing>; "
        "Edition-3 ANCHOR / REFERENCE / SIGNATURE sections support cross-file linking; "
        "a REFERENCE entry names an external instance via a URI plus #anchor_name; "
        "the other end must publish that anchor in its ANCHOR section; "
        "here the companion file is missing and the anchor name is misspelt; "
        "pure-Python Part-21 validator rejects (reject(E_UNRESOLVED_REFS)); "
        "OCC silently accepts with diagnostic but loads empty result; "
        "expected kernel behavior: report the unresolvable reference with a precise diagnostic "
        "naming the URI and anchor; allow rest of file to load with a placeholder if policy "
        "is partial-load, otherwise reject deterministically; "
        "see also: Lh026, Lh028; "
        "synonyms: REFERENCE section unresolvable anchor, external anchor not found, "
        "STEP REFERENCE points at missing file, URI anchor in REFERENCE unresolved, "
        "broken cross-file STEP link"
    ),
)


def _render_lh034() -> str:
    """Render a Part-21 with REFERENCE entries pointing at unresolvable external anchors."""
    return (
        "ISO-10303-21;\n"
        "/* Lh034: REFERENCE section with unresolvable external anchors */\n"
        "/* ISO 10303-21 Ed.3: REFERENCE entry must resolve against a companion ANCHOR section */\n"
        "/* DEFECT: companion-file.stp does not exist; missing_anchor name is misspelt */\n"
        "/* DEFECT: https://example.invalid/no-such-file.stp is not reachable */\n"
        "/* pure-Python validator rejects (E_UNRESOLVED_REFS); OCC silently accepts empty */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Lh034: REFERENCE section with unresolvable external anchors'),'2;1');\n"
        "FILE_NAME('Lh034.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN'));\n"
        "ENDSEC;\n"
        "REFERENCE;\n"
        "/* DEFECT: companion-file.stp does not exist; #missing_anchor is not published */\n"
        "#10=<file:companion-file.stp#missing_anchor>;\n"
        "/* DEFECT: example.invalid URI is unresolvable; also_missing anchor absent */\n"
        "#11=<https://example.invalid/no-such-file.stp#also_missing>;\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner',(1.,1.,0.));\n"
        "#3=DIRECTION('xdir',(1.,0.,0.));\n"
        "#4=DIRECTION('zdir',(0.,0.,1.));\n"
        "#5=GEOMETRIC_CURVE_SET('broken-crossfile-link-shape',(#1,#2));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_lh034(path) -> None:
    Path(path).write_text(_render_lh034())


f.render = _render_lh034  # type: ignore[method-assign]
f.write = _write_lh034    # type: ignore[method-assign]
