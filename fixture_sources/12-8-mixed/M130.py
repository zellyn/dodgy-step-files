"""M130 — AP203 assembly classified at lower security level than its components.

Catalog claim: A parent PRODUCT carries SECURITY_CLASSIFICATION_LEVEL('unclassified')
but a child component used in a NEXT_ASSEMBLY_USAGE_OCCURRENCE carries 'confidential'.
Aggregating a classified child into an unclassified parent inverts the security
clearance hierarchy.

Reproducer recipe: parent PRODUCT with SECURITY_CLASSIFICATION_LEVEL('unclassified');
child with SECURITY_CLASSIFICATION_LEVEL('confidential'); both linked through
CC_DESIGN_SECURITY_CLASSIFICATION.

Byte assertions:
  contains(b'CONFIG_CONTROL_DESIGN')
  count_entity_def(b'SECURITY_CLASSIFICATION') >= 2
  contains(b'CC_DESIGN_SECURITY_CLASSIFICATION')

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M130",
    defect=(
        "GEOMETRIC_CURVE_SET in AP203 CONFIG_CONTROL_DESIGN file where a parent "
        "PRODUCT carries SECURITY_CLASSIFICATION_LEVEL('unclassified') but a child "
        "component used in a NEXT_ASSEMBLY_USAGE_OCCURRENCE carries "
        "SECURITY_CLASSIFICATION_LEVEL('confidential'), inverting the security "
        "clearance hierarchy; "
        "input: AP203 STEP file with two PRODUCT entities — an assembly (parent) and "
        "a component (child) — where the child is linked into the parent via "
        "NEXT_ASSEMBLY_USAGE_OCCURRENCE; the parent assembly is tagged 'unclassified' "
        "via CC_DESIGN_SECURITY_CLASSIFICATION but the child component is tagged "
        "'confidential'; per ISO 10303-203 §5.5 security classification must be "
        "monotone from leaf to root — no child may have a higher classification level "
        "than its parent assembly; because the assembly is unclassified, anyone "
        "permitted to read the assembly file gains visibility of the confidential child; "
        "kernel must validate classification monotonicity from leaves to root and "
        "reject or warn if any child exceeds the parent's level; "
        "synonyms: AP203 clearance inversion, ITAR/EAR hierarchy violation, "
        "classified child unclassified parent, AP203 security classification inversion, "
        "PDM access-control violation, security classification hierarchy broken, "
        "child confidential in unclassified parent"
    ),
    schema="AP242",
)


def _render_m130() -> str:
    """Render AP203 CONFIG_CONTROL_DESIGN file with security classification inversion.

    Entity layout:
      #1-#2      APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14    Unit context (mm)
      #20-#22    Parent assembly product/formation/definition (unclassified)
      #30-#32    Child component product/formation/definition (confidential)
      #40        NEXT_ASSEMBLY_USAGE_OCCURRENCE linking child into parent
      #50-#51    SECURITY_CLASSIFICATION entities (unclassified / confidential)
      #52-#53    CC_DESIGN_SECURITY_CLASSIFICATION assignments — DEFECT: inversion
      #500       GEOMETRIC_CURVE_SET model entity
      #600+      Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M130: AP203 assembly classified at lower security level than its components */")
    lines.append("/* DEFECT: parent assembly is 'unclassified'; child component is 'confidential' */")
    lines.append("/* Per AP203 §5.5 security must be monotone: child level <= parent level */")
    lines.append("/* Anyone reading the unclassified assembly gains access to the confidential child */")
    lines.append("/* Byte assertion: contains(b'CONFIG_CONTROL_DESIGN') */")
    lines.append("/* Byte assertion: count_entity_def(b'SECURITY_CLASSIFICATION') >= 2 */")
    lines.append("/* Byte assertion: contains(b'CC_DESIGN_SECURITY_CLASSIFICATION') */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M130: AP203 security classification inversion — unclassified parent, confidential child'),'2;1');")
    lines.append("FILE_NAME('M130.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Parent assembly product — will be classified 'unclassified' */")
    lines.append("#20=PRODUCT('ASSY-001','Actuator Assembly','Top-level assembly',(#1));")
    lines.append("#21=PRODUCT_DEFINITION_FORMATION('rev_A','',#20);")
    lines.append("#22=PRODUCT_DEFINITION('design','',#21,PRODUCT_DEFINITION_CONTEXT(#1,'design'));")
    lines.append("/* Child component product — will be classified 'confidential' */")
    lines.append("#30=PRODUCT('PART-007','Classified Valve','Restricted flow control valve',(#1));")
    lines.append("#31=PRODUCT_DEFINITION_FORMATION('rev_A','',#30);")
    lines.append("#32=PRODUCT_DEFINITION('design','',#31,PRODUCT_DEFINITION_CONTEXT(#1,'design'));")
    lines.append("/* NEXT_ASSEMBLY_USAGE_OCCURRENCE links child into parent assembly */")
    lines.append("#40=NEXT_ASSEMBLY_USAGE_OCCURRENCE('nauo_1','valve in assembly','',")
    lines.append("  #22,#32,$);")
    lines.append("/* Byte assertion: count_entity_def(b'SECURITY_CLASSIFICATION') >= 2 */")
    lines.append("/* SECURITY_CLASSIFICATION for parent: 'unclassified' */")
    lines.append("#50=SECURITY_CLASSIFICATION('assembly clearance','unclassified assembly',")
    lines.append("  SECURITY_CLASSIFICATION_LEVEL('unclassified'));")
    lines.append("/* SECURITY_CLASSIFICATION for child: 'confidential' — higher than parent: DEFECT */")
    lines.append("#51=SECURITY_CLASSIFICATION('part clearance','confidential valve component',")
    lines.append("  SECURITY_CLASSIFICATION_LEVEL('confidential'));")
    lines.append("/* Byte assertion: contains(b'CC_DESIGN_SECURITY_CLASSIFICATION') */")
    lines.append("/* CC_DESIGN_SECURITY_CLASSIFICATION assigns clearance to parent assembly */")
    lines.append("#52=CC_DESIGN_SECURITY_CLASSIFICATION(#50,(#22));")
    lines.append("/* DEFECT: child component gets 'confidential' while parent is 'unclassified' */")
    lines.append("/* Per AP203 §5.5 this inverts the monotonicity requirement */")
    lines.append("#53=CC_DESIGN_SECURITY_CLASSIFICATION(#51,(#32));")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#500=GEOMETRIC_CURVE_SET('ap203-security-classification-inversion',")
    lines.append("  (#22,#32,#40,#50,#51,#52,#53));")
    lines.append("/* Product chain */")
    lines.append("#600=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#601=PRODUCT_CONTEXT('',#600,'mechanical');")
    lines.append("#602=PRODUCT('M130','M130','M130',(#601));")
    lines.append("#603=PRODUCT_DEFINITION_FORMATION('','',#602);")
    lines.append("#604=PRODUCT_DEFINITION_CONTEXT(#600,'design');")
    lines.append("#605=PRODUCT_DEFINITION('','',#603,#604);")
    lines.append("#606=PRODUCT_DEFINITION_SHAPE('','',#605);")
    lines.append("#607=SHAPE_REPRESENTATION('',(#500),#14);")
    lines.append("#608=SHAPE_DEFINITION_REPRESENTATION(#606,#607);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m130(path) -> None:
    Path(path).write_text(_render_m130())


f.render = _render_m130  # type: ignore[method-assign]
f.write = _write_m130    # type: ignore[method-assign]
