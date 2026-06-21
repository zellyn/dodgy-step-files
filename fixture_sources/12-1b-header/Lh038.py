"""Lh038 — `FILE_POPULATION` header record naming an unterminated population set.

Catalog claim: Edition-3 FILE_POPULATION records declare a 'population' (a
named subset of instances) whose closure is determined by a separate marker or
by section boundary. When the marker is missing or misspelt, instances appear
to belong to multiple populations or to none. Consumers diverge on whether to
treat the open population as covering the whole DATA section or to discard the
population designation.
Bug-reporter language: "FILE_POPULATION unterminated", "STEP population set
without close marker", "FILE_POPULATION missing terminator", "instances belong
to no population", "ambiguous FILE_POPULATION boundary".

Reproducer recipe:
  HEADER contains FILE_POPULATION('release_a','version-1','release-baseline');
  with no closing record.

Byte assertions:
  contains(b'FILE_POPULATION(')
  contains(b'release_a')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Lh038",
    defect=(
        "FILE_POPULATION header record naming an unterminated population set; "
        "input: HEADER contains FILE_POPULATION('release_a','version-1','release-baseline') "
        "with no closing record to bound the population; "
        "ISO 10303-21 Ed.3 §6.3: FILE_POPULATION records declare a named subset of instances "
        "whose closure is determined by a separate marker or by section boundary; "
        "when the marker is missing or misspelt, instances appear to belong to multiple "
        "populations or to none; "
        "consumers diverge on whether to treat open population as covering the whole DATA "
        "section or to discard the population designation; "
        "OCC silently accepts the unterminated FILE_POPULATION record with no diagnostic; "
        "expected kernel behavior: parse FILE_POPULATION metadata and either apply the named "
        "population to the entire DATA section deterministically or reject the unterminated "
        "population with a diagnostic; do not silently apply to an arbitrary subset; "
        "see also: Lh016; "
        "synonyms: FILE_POPULATION unterminated, STEP population set without close marker, "
        "FILE_POPULATION missing terminator, instances belong to no population, "
        "ambiguous FILE_POPULATION boundary"
    ),
)


def _render_lh038() -> str:
    """Render a Part-21 with unterminated FILE_POPULATION in the HEADER section."""
    return (
        "ISO-10303-21;\n"
        "/* Lh038: FILE_POPULATION header record without closing population marker */\n"
        "/* ISO 10303-21 Ed.3 §6.3: FILE_POPULATION must have a corresponding close marker */\n"
        "/* DEFECT: FILE_POPULATION('release_a',...) has no terminator/close marker */\n"
        "/* instances appear to belong to population 'release_a' or to none; */\n"
        "/* OCC silently accepts with no diagnostic; expected: reject or require deterministic apply */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Lh038: FILE_POPULATION without close marker'),'2;1');\n"
        "FILE_NAME('Lh038.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN'));\n"
        "FILE_POPULATION('release_a','version-1','release-baseline');\n"
        "/* DEFECT: no closing/terminating record for the population 'release_a' */\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner',(1.,1.,0.));\n"
        "#3=DIRECTION('xdir',(1.,0.,0.));\n"
        "#4=DIRECTION('zdir',(0.,0.,1.));\n"
        "#5=GEOMETRIC_CURVE_SET('unterminated-population-shape',(#1,#2));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_lh038(path) -> None:
    Path(path).write_text(_render_lh038())


f.render = _render_lh038  # type: ignore[method-assign]
f.write = _write_lh038    # type: ignore[method-assign]
