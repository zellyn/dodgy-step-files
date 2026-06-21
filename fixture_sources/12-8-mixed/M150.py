"""M150 — AP210 differential-pair traces have > 5 % length mismatch

Catalog claim: A paired-trace net (e.g. USB_DP / USB_DM) declares one
conductor of length 50.0 mm and the other of length 56.0 mm (12 %
skew). High-speed differential signaling tolerates only a small
fraction (typically < 5 %) of length mismatch; the pair fails timing
closure.

Reproducer recipe: two CONDUCTOR_TRACK_PROFILE entries with
LENGTH_MEASURE(50.0) and LENGTH_MEASURE(56.0) linked under a single
NETWORK.

Byte assertions:
  contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN')
  count_entity_def(b'CONDUCTOR_TRACK_PROFILE') >= 2
  contains(b'NETWORK')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M150",
    defect=(
        "GEOMETRIC_CURVE_SET in AP210 ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN "
        "file where two CONDUCTOR_TRACK_PROFILE entities in a differential pair have a "
        "length skew of 12 % (50.0 mm vs 56.0 mm), exceeding the 5 % high-speed tolerance; "
        "input: AP210 STEP file containing a NETWORK 'USB_DIFF' grouping two conductors: "
        "CONDUCTOR_TRACK_PROFILE 'USB_DP' with LENGTH_MEASURE(50.0) — the positive USB data trace; "
        "CONDUCTOR_TRACK_PROFILE 'USB_DM' with LENGTH_MEASURE(56.0) — the negative USB data trace; "
        "the length difference of 6.0 mm is 12 % of the shorter trace; "
        "high-speed differential signaling (USB 2.0, LVDS) tolerates only a few percent skew; "
        "at 480 Mbit/s the 6 mm mismatch introduces a delay skew of approx 41 ps, "
        "which is 2 % of the unit interval and causes inter-symbol interference; "
        "the pair fails timing closure and bit-error-rate tests; "
        "per ISO 10303-210 §7 network electrical attributes must be validated for length matching; "
        "kernel must validate length matching for declared differential pairs and warn or reject "
        "if skew exceeds tolerance; "
        "synonyms: AP210 diff pair length skew, USB differential pair mismatched, "
        "ECAD high-speed length tolerance, differential pair skew, PCB length mismatch, "
        "AP210 USB pair too far apart"
    ),
    schema="AP242",
)


def _render_m150() -> str:
    """Render AP210 file with USB differential pair having 12% length skew.

    Entity layout:
      #1-#2     APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14   Unit context (mm)
      #100      CONDUCTOR_TRACK_PROFILE 'USB_DP' — 50.0 mm positive trace
      #101      CONDUCTOR_TRACK_PROFILE 'USB_DM' — 56.0 mm negative trace  (DEFECT: 12% skew)
      #200      NETWORK 'USB_DIFF' grouping both conductors
      #300      GEOMETRIC_CURVE_SET model entity
      #400+     Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M150: AP210 differential-pair traces have > 5% length mismatch */")
    lines.append("/* DEFECT: USB_DP=50.0mm, USB_DM=56.0mm — 12% length skew exceeds 5% tolerance */")
    lines.append("/* High-speed differential signaling (USB 2.0) requires < 5% length skew */")
    lines.append("/* 6mm mismatch at 480Mbit/s introduces ~41ps skew, causing ISI and BER failures */")
    lines.append("/* Per ISO 10303-210 §7 network electrical attributes must be validated */")
    lines.append("/* Byte assertion: contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN') */")
    lines.append("/* Byte assertion: count_entity_def(b'CONDUCTOR_TRACK_PROFILE') >= 2 */")
    lines.append("/* Byte assertion: contains(b'NETWORK') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M150: AP210 USB diff-pair length skew 12%'),'2;1');")
    lines.append("FILE_NAME('M150.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
    lines.append("/* Byte assertion: contains(b'ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN') */")
    lines.append("FILE_SCHEMA(('ELECTRONIC_ASSEMBLY_INTERCONNECT_AND_PACKAGING_DESIGN { 1 0 10303 210 3 1 0 }'));")
    lines.append("ENDSEC;")
    lines.append("DATA;")
    lines.append("#1=APPLICATION_CONTEXT('electronic_assembly_interconnect_and_packaging_design');")
    lines.append("#2=APPLICATION_PROTOCOL_DEFINITION('international standard',")
    lines.append("  'electronic_assembly_interconnect_and_packaging_design',2014,#1);")
    lines.append("/* Standard unit context (mm) */")
    lines.append("#10=(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.));")
    lines.append("#11=(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.));")
    lines.append("#12=(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT());")
    lines.append("#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#10,")
    lines.append("  'distance_accuracy_value','maximum model space distance between geometric entities');")
    lines.append("#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3)")
    lines.append("  GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))")
    lines.append("  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12))")
    lines.append("  REPRESENTATION_CONTEXT('pcb','3D'));")
    lines.append("/* Byte assertion: count_entity_def(b'CONDUCTOR_TRACK_PROFILE') >= 2 */")
    lines.append("/* USB_DP positive trace: 50.0 mm — reference length for the pair */")
    lines.append("#100=CONDUCTOR_TRACK_PROFILE('USB_DP',LENGTH_MEASURE(50.0),$,$);")
    lines.append("/* DEFECT: USB_DM negative trace: 56.0 mm — 12% longer than USB_DP */")
    lines.append("/* length skew = (56.0 - 50.0) / 50.0 = 12% >> 5% allowed for USB 2.0 */")
    lines.append("#101=CONDUCTOR_TRACK_PROFILE('USB_DM',LENGTH_MEASURE(56.0),$,$);")
    lines.append("/* Byte assertion: contains(b'NETWORK') */")
    lines.append("/* NETWORK 'USB_DIFF' groups both conductors as a differential pair */")
    lines.append("#200=NETWORK('USB_DIFF',(#100,#101));")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#300=GEOMETRIC_CURVE_SET('ap210-differential-pair-length-skew-usb-dp-dm',")
    lines.append("  (#100,#101,#200));")
    lines.append("/* Product chain */")
    lines.append("#400=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#401=PRODUCT_CONTEXT('',#400,'mechanical');")
    lines.append("#402=PRODUCT('M150','M150','M150',(#401));")
    lines.append("#403=PRODUCT_DEFINITION_FORMATION('','',#402);")
    lines.append("#404=PRODUCT_DEFINITION_CONTEXT(#400,'design');")
    lines.append("#405=PRODUCT_DEFINITION('','',#403,#404);")
    lines.append("#406=PRODUCT_DEFINITION_SHAPE('','',#405);")
    lines.append("#407=SHAPE_REPRESENTATION('',(#300),#14);")
    lines.append("#408=SHAPE_DEFINITION_REPRESENTATION(#406,#407);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m150(path) -> None:
    Path(path).write_text(_render_m150())


f.render = _render_m150  # type: ignore[method-assign]
f.write = _write_m150    # type: ignore[method-assign]
