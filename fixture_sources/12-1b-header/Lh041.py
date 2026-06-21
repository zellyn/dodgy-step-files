"""Lh041 — REFERENCE section with mixed URI schemes including unsupported schemes.

Catalog claim: Edition-3 REFERENCE entries carry URIs to external resources.
The spec does not constrain the URI scheme. Receivers implement `file://` and
possibly `http(s)://`; uncommon schemes (`urn:`, `ftp:`, custom org-specific)
are typically unsupported. A REFERENCE section mixing several schemes — some
supported, some not — tests the consistency of the decision.
Bug-reporter language: "REFERENCE section mixed URI schemes", "urn: scheme in
STEP REFERENCE unsupported", "STEP REFERENCE includes ftp:", "unknown URI
scheme in REFERENCE", "REFERENCE custom-scheme URI".

Reproducer recipe:
  REFERENCE section with <file:companion.stp#part_a>,
  <https://example.invalid/companion.stp#part_b>,
  <urn:plm:org-acme:doc:12345#assembly>,
  <plmlink:vault://acme/parts/12345#main>.

Byte assertions:
  contains(b'REFERENCE;')
  contains(b'urn:') or contains(b'plmlink:')
  contains(b'file:') or contains(b'https://')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Lh041",
    defect=(
        "REFERENCE section with mixed URI schemes including unsupported schemes; "
        "input: REFERENCE section contains <file:companion.stp#part_a>, "
        "<https://example.invalid/companion.stp#part_b>, "
        "<urn:plm:org-acme:doc:12345#assembly>, <plmlink:vault://acme/parts/12345#main>; "
        "ISO 10303-21 Ed.3 §8: REFERENCE entries carry URIs to external resources; "
        "the spec does not constrain the URI scheme; "
        "receivers implement file:// and possibly http(s)://; "
        "uncommon schemes (urn:, ftp:, custom org-specific) are typically unsupported; "
        "a REFERENCE section mixing several schemes tests consistency of the decision; "
        "pure-Python Part-21 validator rejects (reject(E_UNRESOLVED_REFS)); "
        "OCC silently accepts (load is empty); "
        "expected kernel behavior: classify each URI scheme as supported/unsupported and "
        "report unsupported entries deterministically; do not abort the whole file load "
        "on the first unsupported scheme unless the policy is strict-reject; "
        "see also: Lh034; "
        "synonyms: REFERENCE section mixed URI schemes, urn: scheme in STEP REFERENCE unsupported, "
        "STEP REFERENCE includes ftp:, unknown URI scheme in REFERENCE, REFERENCE custom-scheme URI"
    ),
)


def _render_lh041() -> str:
    """Render a Part-21 with REFERENCE section containing mixed URI schemes."""
    return (
        "ISO-10303-21;\n"
        "/* Lh041: REFERENCE section with mixed URI schemes including unsupported ones */\n"
        "/* ISO 10303-21 Ed.3 §8: REFERENCE entries carry URIs; spec does not constrain scheme */\n"
        "/* DEFECT: urn: and plmlink: schemes are typically unsupported by receivers */\n"
        "/* pure-Python validator rejects (E_UNRESOLVED_REFS); OCC silently accepts empty */\n"
        "/* expected: classify each URI scheme; report unsupported entries deterministically */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Lh041: REFERENCE section with mixed URI schemes'),'2;1');\n"
        "FILE_NAME('Lh041.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN'));\n"
        "ENDSEC;\n"
        "REFERENCE;\n"
        "/* supported scheme: file: */\n"
        "#10=<file:companion.stp#part_a>;\n"
        "/* supported scheme: https: */\n"
        "#11=<https://example.invalid/companion.stp#part_b>;\n"
        "/* DEFECT: unsupported scheme urn: */\n"
        "#12=<urn:plm:org-acme:doc:12345#assembly>;\n"
        "/* DEFECT: unsupported custom scheme plmlink: */\n"
        "#13=<plmlink:vault://acme/parts/12345#main>;\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner',(1.,1.,0.));\n"
        "#3=DIRECTION('xdir',(1.,0.,0.));\n"
        "#4=DIRECTION('zdir',(0.,0.,1.));\n"
        "#5=GEOMETRIC_CURVE_SET('mixed-uri-scheme-shape',(#1,#2));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_lh041(path) -> None:
    Path(path).write_text(_render_lh041())


f.render = _render_lh041  # type: ignore[method-assign]
f.write = _write_lh041    # type: ignore[method-assign]
