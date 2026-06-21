"""Wr050 — Geometry coordinate values doubled on export (writer applies scale and unit-conversion both).

Catalog claim: a part the user dimensioned as 20 mm outer round-trips as 40 mm — every
coordinate doubled. The writer applies both the source-document scale (which was already
1.0) and the export-unit conversion factor in series instead of choosing one path. The
output STEP carries doubled coordinates in a context that still claims millimetres.
Bug-reporter language: "outer diameter 20mm exports as 40mm", "model is 2x bigger after
export", "stl and step both wrong size".

Reproducer recipe: STEP cube authored as 20 mm side; emit CARTESIAN_POINT coordinates
of (40.0, 40.0, 40.0) with LENGTH_UNIT declaring SI MILLI METRE.

Byte assertions:
  contains(b'40.0') and contains(b'MILLI')
  contains(b'CARTESIAN_POINT')

Tier-3: load == "ok"
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Wr050",
    defect=(
        "geometry coordinate values doubled on export (writer applies scale and unit-conversion both); "
        "input: part dimensioned as a 20 mm cube; writer applies both the source-document scale "
        "(which was already 1.0) AND the export-unit conversion factor — composed in series "
        "instead of choosing one path; output STEP carries 40.0 coordinates in a context "
        "that still claims MILLI METRE; re-import produces a 40 mm cube (2× too large); "
        "produced by FreeCAD (FreeCAD #17729) when both a Draft Scale operation and a unit "
        "conversion are in the pipeline; writer composes them in series — applies document "
        "scale as if it were a coordinate-space transform on top of the unit conversion; "
        "distinct from Wr035 (1000× factor) and Wr044 (inch label only) by the specific 2× factor; "
        "expected kernel behavior: writer composes the Placement-and-unit pipeline once; "
        "refuses to chain document-scale into unit-conversion; emits a self-test that round-trips "
        "a known-volume primitive before writing user data; "
        "see also: Wr035, U015, Wr044; "
        "synonyms: STEP export doubles all coordinates, 20mm becomes 40mm on import, "
        "two-times scale factor on STEP export, writer applies scale twice"
    ),
)


def _render_wr050() -> str:
    """Render a Part-21 where a 20 mm cube's coordinates are emitted doubled as 40.0."""
    return (
        "ISO-10303-21;\n"
        "/* Wr050: geometry coordinate values doubled on export */\n"
        "/* FreeCAD #17729: writer applied both document scale (1.0) and unit conversion */\n"
        "/* factor in series — two-pass pipeline doubles every coordinate value */\n"
        "/* 20 mm cube → coordinates 40.0 in a context still claiming MILLI METRE */\n"
        "/* Receivers load a 40 mm cube (2× the producer's 20 mm intent) */\n"
        "HEADER;\n"
        "FILE_DESCRIPTION(('Wr050: coordinate values doubled by scale+unit-conversion both'),'2;1');\n"
        "FILE_NAME('Wr050.stp','2026-06-20T00:00:00',(''),(''),'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "/* DEFECT: coordinates are 40.0 — double the 20 mm original — but unit is MILLI METRE */\n"
        "/* Source was a 20 mm cube; correct coordinates would be (20.0, 20.0, 20.0) in mm */\n"
        "/* Writer composed document-scale (1.0) into unit-conversion, applying the factor twice */\n"
        "#1=CARTESIAN_POINT('origin',(0.,0.,0.));\n"
        "#2=CARTESIAN_POINT('corner-x',(40.0,0.,0.));\n"
        "#3=CARTESIAN_POINT('corner-y',(0.,40.0,0.));\n"
        "#4=CARTESIAN_POINT('corner-z',(0.,0.,40.0));\n"
        "#5=CARTESIAN_POINT('corner-xyz',(40.0,40.0,40.0));\n"
        "#6=DIRECTION('xdir',(1.,0.,0.));\n"
        "#7=DIRECTION('zdir',(0.,0.,1.));\n"
        "/* DEFECT: MILLI METRE declared; 40.0 values should be 20.0 for a 20 mm cube */\n"
        "#8=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.));\n"
        "#9=GEOMETRIC_CURVE_SET('doubled-coords-20mm-cube',(#1,#2,#3,#4,#5));\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


def _write_wr050(path) -> None:
    Path(path).write_text(_render_wr050())


f.render = _render_wr050  # type: ignore[method-assign]
f.write = _write_wr050    # type: ignore[method-assign]
