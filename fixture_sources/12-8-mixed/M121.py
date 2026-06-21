"""M121 — AP209 time-history loadcase with non-monotonically increasing time vector.

Catalog claim: A time-varying force is encoded as a paired list of (time,
amplitude) tuples whose time component is not monotonically increasing;
e.g., [(0,0), (1,5), (0.5,3), (2,7)]. A transient solver using these as
time-stamped loads either overshoots, walks backwards in time, or fails
to interpolate.

Reproducer recipe: A list of paired (REAL, REAL) describing time and load
amplitude where the time series goes 0.0, 1.0, 0.5, 2.0.

Byte assertions:
  contains(b'STRUCTURAL_ANALYSIS_DESIGN')
  contains(b'NODE_WITH_FORCE')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M121",
    defect=(
        "GEOMETRIC_CURVE_SET containing AP209 time-history loadcase with a "
        "NODE_WITH_FORCE time-amplitude series where the time vector is not "
        "monotonically increasing (0.0, 1.0, 0.5, 2.0); "
        "input: AP209 STEP file where a transient loadcase encodes a time-varying "
        "nodal force as a list of (time, amplitude) pairs in the order "
        "(0.0,0.0), (1.0,5.0), (0.5,3.0), (2.0,7.0); the time values are "
        "0.0 → 1.0 → 0.5 → 2.0, which is non-monotonic (0.5 < 1.0 is a regression); "
        "per ISO 10303-209 §9 time-history representation invariants, the time "
        "component of each (time, amplitude) pair must be strictly monotonically "
        "increasing so that the load curve defines a single-valued function of time; "
        "a transient solver reading the pairs in file order uses the regression "
        "t=0.5 after t=1.0 to either step backwards in time (causing instability), "
        "skip the out-of-order sample (silently dropping load), or fail with a "
        "timestep error; interpolation between t=1.0 and t=0.5 produces negative "
        "delta-t which most integrators treat as division-by-zero; "
        "kernel must sort by time and warn, or reject as malformed; "
        "synonyms: AP209 non-monotonic time, transient load order wrong, "
        "time series unsorted, AP209 time vector out of order, FEM transient load "
        "timestamps wrong, time history not monotonic, AP209 time-amplitude pairs "
        "out of sequence"
    ),
    schema="AP242",
)


def _render_m121() -> str:
    """Render AP209 file with non-monotonic time-history load vector.

    Uses STRUCTURAL_ANALYSIS_DESIGN schema. Entity layout:
      #1-#2      APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14    Unit context (mm)
      #100       CARTESIAN_POINT for loaded node
      #110       NODE entity
      #200       NODE_WITH_FORCE with time-amplitude table — DEFECT: time non-monotonic
      #300       NODE_GROUP
      #310       FEA_MODEL
      #400       LOAD_GROUP collecting the defective load
      #500       GEOMETRIC_CURVE_SET model entity
      #600+      Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M121: AP209 time-history loadcase with non-monotonically increasing time vector */")
    lines.append("/* DEFECT: time-amplitude pairs ordered (0.0,0), (1.0,5), (0.5,3), (2.0,7) */")
    lines.append("/* Time regresses from 1.0 to 0.5 — non-monotonic; transient solver breaks */")
    lines.append("/* Per AP209 §9, time component of each pair must be strictly monotonically increasing */")
    lines.append("/* Byte assertion: contains(b'STRUCTURAL_ANALYSIS_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'NODE_WITH_FORCE') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M121: AP209 time-history load with non-monotonic time vector'),'2;1');")
    lines.append("FILE_NAME('M121.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
    lines.append("/* Byte assertion: contains(b'STRUCTURAL_ANALYSIS_DESIGN') */")
    lines.append("FILE_SCHEMA(('STRUCTURAL_ANALYSIS_DESIGN { 1 0 10303 209 1 0 0 }'));")
    lines.append("ENDSEC;")
    lines.append("DATA;")
    lines.append("#1=APPLICATION_CONTEXT('structural_analysis_design');")
    lines.append("#2=APPLICATION_PROTOCOL_DEFINITION('international standard',")
    lines.append("  'structural_analysis_design',2001,#1);")
    lines.append("/* Standard unit context (mm) */")
    lines.append("#10=(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.));")
    lines.append("#11=(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.));")
    lines.append("#12=(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT());")
    lines.append("#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#10,")
    lines.append("  'distance_accuracy_value','maximum model space distance between geometric entities');")
    lines.append("#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3)")
    lines.append("  GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))")
    lines.append("  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12))")
    lines.append("  REPRESENTATION_CONTEXT('fea','3D'));")
    lines.append("/* Single loaded node */")
    lines.append("#100=CARTESIAN_POINT('loaded_node',(25.0,0.0,0.0));")
    lines.append("#110=NODE('transient_load_node',(#100),$);")
    lines.append("/* Byte assertion: contains(b'NODE_WITH_FORCE') */")
    lines.append("/* DEFECT: time-amplitude table is non-monotonic in the time column */")
    lines.append("/* Pair 1: t=0.0, F=0.0  (valid start) */")
    lines.append("/* Pair 2: t=1.0, F=5.0  (valid: 1.0 > 0.0) */")
    lines.append("/* Pair 3: t=0.5, F=3.0  (DEFECT: 0.5 < 1.0, time regression) */")
    lines.append("/* Pair 4: t=2.0, F=7.0  (valid: 2.0 > 0.5, but path already broken) */")
    lines.append("/* A monotonic series would be: (0.0,0.0),(0.5,3.0),(1.0,5.0),(2.0,7.0) */")
    lines.append("#200=NODE_WITH_FORCE('transient_load','time_history',#110,")
    lines.append("  ((0.0,0.0),(1.0,5.0),(0.5,3.0),(2.0,7.0)),")
    lines.append("  (1000.0,0.0,0.0),$);")
    lines.append("#300=NODE_GROUP('loaded_nodes',(#110),$);")
    lines.append("#310=FEA_MODEL('transient_model',$,'',(#300),(),());")
    lines.append("#400=LOAD_GROUP('time_history_loads',(#200),$);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#500=GEOMETRIC_CURVE_SET('ap209-time-history-load-non-monotonic-time-vector',")
    lines.append("  (#110,#200,#310,#400));")
    lines.append("/* Product chain */")
    lines.append("#600=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#601=PRODUCT_CONTEXT('',#600,'mechanical');")
    lines.append("#602=PRODUCT('M121','M121','M121',(#601));")
    lines.append("#603=PRODUCT_DEFINITION_FORMATION('','',#602);")
    lines.append("#604=PRODUCT_DEFINITION_CONTEXT(#600,'design');")
    lines.append("#605=PRODUCT_DEFINITION('','',#603,#604);")
    lines.append("#606=PRODUCT_DEFINITION_SHAPE('','',#605);")
    lines.append("#607=SHAPE_REPRESENTATION('',(#500),#14);")
    lines.append("#608=SHAPE_DEFINITION_REPRESENTATION(#606,#607);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m121(path) -> None:
    Path(path).write_text(_render_m121())


f.render = _render_m121  # type: ignore[method-assign]
f.write = _write_m121    # type: ignore[method-assign]
