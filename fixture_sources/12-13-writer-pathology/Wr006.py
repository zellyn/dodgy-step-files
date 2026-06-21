"""Wr006 — Floating-point precision degradation on round-trip.

Catalog claim: Coordinates that were entered as exact rationals or simple
decimals (1.0, 1.5, 0.25) appear in the emitted file as nearly-but-not-exactly
the original (1.4999999999998, 0.25000000000004) because the writer stored them
in single-precision (float32) internally but emitted double-precision strings,
or used printf("%.15g") on values that had drifted due to prior arithmetic.

Reproducer recipe: a CARTESIAN_POINT with coordinates
`(1.4999999999998,2.5000000000003,0.99999999999996)` claiming to represent
`(1.5, 2.5, 1.0)`.

Byte assertions:
  matches(rb'\\d\\.\\d{12,}')
  matches(rb'\\.999999')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Wr006",
    defect=(
        "Floating-point precision degradation on round-trip; "
        "coordinates that were entered as exact rationals or simple decimals "
        "(1.0, 1.5, 0.25) appear in the emitted file as nearly-but-not-exactly "
        "the original (1.4999999999998, 0.25000000000004); "
        "writers that store coordinates in single-precision (float32) internally "
        "but emit double-precision strings, or use printf(\"%.15g\") on values "
        "that were 1.5 represented as 1.4999999999998 due to prior arithmetic; "
        "the defect is invisible per-value but accumulates across round-trips: "
        "a vertex stamped from STEP-to-kernel-to-STEP-to-kernel drifts microns per cycle; "
        "discoverable only by comparing pre- and post-round-trip files; "
        "expected kernel behavior: heal and accept; "
        "normalize internal storage to sufficient precision to preserve the input "
        "on round-trip within the spec REAL precision; "
        "synonyms: coordinate 1.5 became 1.4999999999998 after re-export, "
        "precision lost on round-trip, model creeps after every save"
    ),
)


def _render_fp_precision_degradation() -> str:
    """Return a Part-21 string with near-integer coordinates (precision-degraded)."""
    return (
        "ISO-10303-21;\n"
        "/* Wr006: floating-point precision degradation — near-integer coordinates */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Wr006 - floating-point precision degradation on round-trip'),'2;1');\n"
        "FILE_NAME('Wr006.stp','2026-06-20T00:00:00',('auto-generated'),(''),\n"
        "  'auto-generated','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* Defect: coordinates are slightly off their intended exact values */\n"
        "/* Intended (1.5, 2.5, 1.0) but emitted with float32 round-trip drift */\n"
        "#1=CARTESIAN_POINT('drifted-pt',(1.4999999999998,2.5000000000003,0.99999999999996));\n"
        "/* Additional near-zero coordinate to show the pattern */\n"
        "#2=CARTESIAN_POINT('near-zero',(0.00000000000002,0.49999999999998,0.25000000000004));\n"
        "#3=GEOMETRIC_CURVE_SET('precision-degraded',(#1,#2));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_fp_precision_degradation(path) -> None:
    Path(path).write_bytes(_render_fp_precision_degradation().encode("utf-8"))


f.render = _render_fp_precision_degradation  # type: ignore[method-assign]
f.write = _write_fp_precision_degradation  # type: ignore[method-assign]
