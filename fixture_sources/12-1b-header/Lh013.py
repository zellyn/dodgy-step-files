"""Lh013 — Non-deterministic / build-time timestamp pollution.

Catalog claim: Producer pulls the FILE_NAME timestamp from the system clock rather than
honoring a user-supplied datetime. Breaks reproducible builds (e.g. AUR packagers,
CI artefact comparisons, downstream LibrePCB content hashes).
Bug-reporter language: "non-deterministic STEP build timestamp",
"system-clock timestamp pollutes FILE_NAME", "reproducible build broken by STEP timestamp",
"different timestamps each export", "CI artefact differs only by STEP date".

Reproducer recipe: export_step(b, "box.step", timestamp=t) and confirm FILE_NAME's
timestamp matches t.

Byte assertions:
  contains(b'FILE_NAME')
  contains(b'FILE_SCHEMA')
  contains(b'HEADER;')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Lh013",
    defect=(
        "Non-deterministic build-time timestamp pollution in FILE_NAME; "
        "input: FILE_NAME timestamp attribute records the system clock at export time "
        "rather than a user-supplied or epoch-pinned datetime, here '2024-08-15T09:23:47'; "
        "provenance tier: runtime-only; bytes alone cannot demonstrate non-determinism; "
        "the defect is that the timestamp was generated from the system clock rather than "
        "a user-supplied parameter; demonstrating this requires comparing two writer "
        "invocations (or a writer-with-explicit-timestamp behavioral test), not a static file; "
        "breaks reproducible builds: AUR packagers, CI artefact comparisons, and downstream "
        "LibrePCB content-hash checks all fail because every export produces a different file "
        "even when the geometry is identical; "
        "produced by build123d export_step and CadQuery (#1396) when no explicit timestamp "
        "is passed to the exporter; "
        "expected kernel behavior: writer must honor an explicit timestamp parameter when given; "
        "default to current time only when absent; "
        "this fixture captures the static artefact pattern: a well-formed header whose "
        "timestamp value originated from an unconstrained system clock call; "
        "see also: Lh011; "
        "synonyms: non-deterministic STEP build timestamp, system-clock timestamp pollutes "
        "FILE_NAME, reproducible build broken by STEP timestamp, different timestamps each "
        "export, CI artefact differs only by STEP date"
    ),
)


def _render_lh013() -> str:
    """Render a Part-21 that demonstrates a system-clock-sourced timestamp in FILE_NAME.

    The defect is structural (non-determinism across exports) rather than a parse error.
    This static fixture represents one snapshot from such a build — a file whose timestamp
    is known to have come from the system clock rather than a user-supplied value.
    """
    return (
        "ISO-10303-21;\n"
        "/* Lh013: FILE_NAME timestamp sourced from system clock (non-deterministic) */\n"
        "/* ISO 10303-21 §8: timestamp should be user-supplied for reproducible builds */\n"
        "/* DEFECT: '2024-08-15T09:23:47' was written by the system clock at export time */\n"
        "/* Each export of the same geometry produces a different file hash */\n"
        "/* Breaks: AUR packaging, CI artefact comparison, LibrePCB content hashes */\n"
        "/* Produced by: build123d export_step, CadQuery (#1396) without explicit timestamp */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Lh013: non-deterministic build-time timestamp in FILE_NAME'),'2;1');\n"
        "/* DEFECT: timestamp below was taken from the system clock, not a user parameter */\n"
        "FILE_NAME('Lh013.stp','2024-08-15T09:23:47',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner',(1.,1.,0.));\n"
        "#3=DIRECTION('xdir',(1.,0.,0.));\n"
        "#4=DIRECTION('zdir',(0.,0.,1.));\n"
        "#5=GEOMETRIC_CURVE_SET('nondeterministic-timestamp-shape',(#1,#2));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_lh013(path) -> None:
    Path(path).write_text(_render_lh013())


f.render = _render_lh013  # type: ignore[method-assign]
f.write = _write_lh013    # type: ignore[method-assign]
