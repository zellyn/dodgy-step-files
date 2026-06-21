"""M129 — AP203 new revision references parent not in change-history chain.

Catalog claim: A PRODUCT_DEFINITION_FORMATION (e.g. rev_C) is linked to a
parent (rev_A) via PRODUCT_DEFINITION_RELATIONSHIP, but an intermediate
revision (rev_B) exists in the file with no inbound or outbound relationship.
The engineering-change-history chain skips a revision.

Reproducer recipe: three PRODUCT_DEFINITION_FORMATIONs rev_A, rev_B, rev_C;
one PRODUCT_DEFINITION_RELATIONSHIP linking rev_C to rev_A; rev_B unreferenced.

Byte assertions:
  contains(b'CONFIG_CONTROL_DESIGN')
  count_entity_def(b'PRODUCT_DEFINITION_FORMATION') >= 3
  contains(b'PRODUCT_DEFINITION_RELATIONSHIP')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M129",
    defect=(
        "GEOMETRIC_CURVE_SET in AP203 CONFIG_CONTROL_DESIGN file where a "
        "PRODUCT_DEFINITION_FORMATION (rev_C) references rev_A as its parent via "
        "PRODUCT_DEFINITION_RELATIONSHIP, skipping an intermediate revision rev_B "
        "that exists in the file with no relationship links; "
        "input: AP203 STEP file with three PRODUCT_DEFINITION_FORMATION entities "
        "rev_A, rev_B, and rev_C for the same product; a single "
        "PRODUCT_DEFINITION_RELATIONSHIP links rev_C directly to rev_A as if rev_A "
        "were its immediate predecessor; rev_B has no inbound PRODUCT_DEFINITION_RELATIONSHIP "
        "(it was never derived from a predecessor) and no outbound one (nothing was "
        "derived from it), making it an orphan revision in the change-history graph; "
        "per ISO 10303-203 §4.3 product revision relationships, the engineering change "
        "order (ECO) chain must form a connected directed path through all intermediate "
        "revisions; an orphan revision breaks the change history so that rev_B changes "
        "cannot be traced, audited, or rolled back as part of the release history; "
        "kernel must detect orphan revisions in the change history and warn or reject "
        "if a revision is unreachable from the change-history graph; "
        "synonyms: ECO chain skip, PDM revision orphan, AP203 change history gap, "
        "AP203 ECO skips a revision, engineering change chain broken, "
        "revision derived from wrong parent, PDM revision history has a gap"
    ),
    schema="AP242",
)


def _render_m129() -> str:
    """Render AP203 CONFIG_CONTROL_DESIGN file with orphan intermediate revision.

    Entity layout:
      #1-#2      APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14    Unit context (mm)
      #30        PRODUCT
      #31        PRODUCT_DEFINITION_FORMATION rev_A (initial release)
      #32        PRODUCT_DEFINITION_FORMATION rev_B (ORPHAN — no relationships)
      #33        PRODUCT_DEFINITION_FORMATION rev_C (skips to rev_A as parent)
      #40        PRODUCT_DEFINITION_RELATIONSHIP linking rev_C -> rev_A — DEFECT: skips rev_B
      #500       GEOMETRIC_CURVE_SET model entity
      #600+      Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M129: AP203 new revision references parent not in change-history chain */")
    lines.append("/* DEFECT: rev_C links to rev_A via PRODUCT_DEFINITION_RELATIONSHIP; rev_B is orphaned */")
    lines.append("/* rev_B has no inbound or outbound relationship — change-history chain is broken */")
    lines.append("/* Per AP203 §4.3 ECO chain must be a connected path through all intermediate revisions */")
    lines.append("/* Byte assertion: contains(b'CONFIG_CONTROL_DESIGN') */")
    lines.append("/* Byte assertion: count_entity_def(b'PRODUCT_DEFINITION_FORMATION') >= 3 */")
    lines.append("/* Byte assertion: contains(b'PRODUCT_DEFINITION_RELATIONSHIP') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M129: AP203 revision change-history chain skips intermediate revision'),'2;1');")
    lines.append("FILE_NAME('M129.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
    lines.append("/* Byte assertion: contains(b'CONFIG_CONTROL_DESIGN') */")
    lines.append("FILE_SCHEMA(('CONFIG_CONTROL_DESIGN { 1 0 10303 203 1 0 0 }'));")
    lines.append("ENDSEC;")
    lines.append("DATA;")
    lines.append("#1=APPLICATION_CONTEXT('configuration controlled 3D designs of mechanical parts and assemblies');")
    lines.append("#2=APPLICATION_PROTOCOL_DEFINITION('international standard',")
    lines.append("  'config_control_design',1994,#1);")
    lines.append("/* Standard unit context (mm) */")
    lines.append("#10=(LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(.MILLI.,.METRE.));")
    lines.append("#11=(NAMED_UNIT(*)PLANE_ANGLE_UNIT()SI_UNIT($,.RADIAN.));")
    lines.append("#12=(NAMED_UNIT(*)SI_UNIT($,.STERADIAN.)SOLID_ANGLE_UNIT());")
    lines.append("#13=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.001),#10,")
    lines.append("  'distance_accuracy_value','maximum model space distance between geometric entities');")
    lines.append("#14=(GEOMETRIC_REPRESENTATION_CONTEXT(3)")
    lines.append("  GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#13))")
    lines.append("  GLOBAL_UNIT_ASSIGNED_CONTEXT((#10,#11,#12))")
    lines.append("  REPRESENTATION_CONTEXT('ctx','3D'));")
    lines.append("/* The product for which three revisions exist */")
    lines.append("#30=PRODUCT('PART-001','Actuator Housing','Pneumatic actuator housing',(#1));")
    lines.append("/* Byte assertion: count_entity_def(b'PRODUCT_DEFINITION_FORMATION') >= 3 */")
    lines.append("/* Three revisions: rev_A (initial), rev_B (orphan), rev_C (skips to rev_A) */")
    lines.append("#31=PRODUCT_DEFINITION_FORMATION('rev_A','Initial engineering release',#30);")
    lines.append("/* DEFECT: rev_B is an orphan — no PRODUCT_DEFINITION_RELATIONSHIP references it */")
    lines.append("/* It has no predecessor link (was it branched? re-worked?) and no successor link */")
    lines.append("/* A valid change chain: rev_A -> rev_B -> rev_C would require two relationships */")
    lines.append("#32=PRODUCT_DEFINITION_FORMATION('rev_B','Intermediate ECO (orphaned)',#30);")
    lines.append("#33=PRODUCT_DEFINITION_FORMATION('rev_C','Production release derived from rev_A',#30);")
    lines.append("/* Byte assertion: contains(b'PRODUCT_DEFINITION_RELATIONSHIP') */")
    lines.append("/* DEFECT: relates rev_C directly to rev_A, skipping rev_B entirely */")
    lines.append("/* A correct ECO chain would link: #40 rev_B->rev_A, #41 rev_C->rev_B */")
    lines.append("#40=PRODUCT_DEFINITION_RELATIONSHIP('eco_chain','ECO: rev_C from rev_A',")
    lines.append("  $,#33,#31);")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#500=GEOMETRIC_CURVE_SET('ap203-revision-change-history-chain-skips-intermediate',")
    lines.append("  (#31,#32,#33,#40));")
    lines.append("/* Product chain */")
    lines.append("#600=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#601=PRODUCT_CONTEXT('',#600,'mechanical');")
    lines.append("#602=PRODUCT('M129','M129','M129',(#601));")
    lines.append("#603=PRODUCT_DEFINITION_FORMATION('','',#602);")
    lines.append("#604=PRODUCT_DEFINITION_CONTEXT(#600,'design');")
    lines.append("#605=PRODUCT_DEFINITION('','',#603,#604);")
    lines.append("#606=PRODUCT_DEFINITION_SHAPE('','',#605);")
    lines.append("#607=SHAPE_REPRESENTATION('',(#500),#14);")
    lines.append("#608=SHAPE_DEFINITION_REPRESENTATION(#606,#607);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m129(path) -> None:
    Path(path).write_text(_render_m129())


f.render = _render_m129  # type: ignore[method-assign]
f.write = _write_m129    # type: ignore[method-assign]
