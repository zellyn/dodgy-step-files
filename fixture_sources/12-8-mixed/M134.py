"""M134 — AP203 two distinct PERSON entities share the same id.

Catalog claim: Two PERSON instances declare the same identifier (e.g. 'jdoe')
yet have different last names ('Doe' vs 'Doppelganger'). PERSON.id is intended
to uniquely identify the individual across the design pool; this collision makes
downstream APPROVAL_PERSON_ORGANIZATION references ambiguous.

Reproducer recipe: PERSON('jdoe','Doe','John',..) and
PERSON('jdoe','Doppelganger','Jane',..) in the same file.

Byte assertions:
  contains(b'CONFIG_CONTROL_DESIGN')
  count_entity_def(b'PERSON') >= 2
  contains(b"PERSON('jdoe',")

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M134",
    defect=(
        "GEOMETRIC_CURVE_SET in AP203 CONFIG_CONTROL_DESIGN file where two "
        "PERSON entities share the same id 'jdoe' but have different last names "
        "('Doe' vs 'Doppelganger'), creating an identifier collision that makes "
        "APPROVAL_PERSON_ORGANIZATION references ambiguous; "
        "input: AP203 STEP file with two PERSON instances both declaring id='jdoe': "
        "one is PERSON('jdoe','Doe','John',..) and the other is "
        "PERSON('jdoe','Doppelganger','Jane',..); per ISO 10303-41 the PERSON.id "
        "attribute is intended to uniquely identify an individual within the design "
        "pool — no two PERSON entities should share the same id; when an "
        "APPROVAL_PERSON_ORGANIZATION entity references 'jdoe' the receiver cannot "
        "determine which of the two individuals performed or approved the design "
        "action; PDM audit trails, approval workflows, and access control lists all "
        "depend on PERSON uniqueness; "
        "kernel must detect duplicate PERSON.id and reject or warn; "
        "auto-rename is out of scope for the kernel; "
        "synonyms: AP203 PERSON id collision, two people same identifier, "
        "PDM approver ambiguous, AP203 person ID conflict, PDM identifier collision, "
        "approver disambiguation, PERSON identifier duplicate, "
        "AP203 person uniqueness violation"
    ),
    schema="AP242",
)


def _render_m134() -> str:
    """Render AP203 CONFIG_CONTROL_DESIGN file with two PERSON entities sharing id 'jdoe'.

    Entity layout:
      #1-#2      APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14    Unit context (mm)
      #20        PERSON('jdoe','Doe','John',..) — first person with id 'jdoe'
      #21        PERSON('jdoe','Doppelganger','Jane',..) — DEFECT: duplicate id
      #22        ORGANIZATION entity (company)
      #23-#24    PERSON_AND_ORGANIZATION for each PERSON
      #30-#32    PRODUCT / PRODUCT_DEFINITION_FORMATION / PRODUCT_DEFINITION
      #40        APPROVAL entity
      #41        APPROVAL_PERSON_ORGANIZATION — ambiguous which 'jdoe' approved
      #500       GEOMETRIC_CURVE_SET model entity
      #600+      Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M134: AP203 two distinct PERSON entities share the same id 'jdoe' */")
    lines.append("/* DEFECT: two PERSON instances both have id='jdoe' but different last names */")
    lines.append("/* APPROVAL_PERSON_ORGANIZATION cannot determine which individual approved */")
    lines.append("/* Per ISO 10303-41 PERSON.id must be unique within the design pool */")
    lines.append("/* Byte assertion: contains(b'CONFIG_CONTROL_DESIGN') */")
    lines.append("/* Byte assertion: count_entity_def(b'PERSON') >= 2 */")
    lines.append("/* Byte assertion: contains(b\"PERSON('jdoe',\") */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M134: AP203 PERSON id collision — two people share id jdoe'),'2;1');")
    lines.append("FILE_NAME('M134.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Byte assertion: count_entity_def(b'PERSON') >= 2 */")
    lines.append("/* First PERSON with id 'jdoe' — imported from design-team database */")
    lines.append("/* Byte assertion: contains(b\"PERSON('jdoe',\") */")
    lines.append("#20=PERSON('jdoe','Doe','John',$,$,$);")
    lines.append("/* DEFECT: second PERSON also has id 'jdoe' — imported from approval database */")
    lines.append("/* Different last name 'Doppelganger' proves these are distinct individuals */")
    lines.append("/* A valid file would use distinct ids such as 'jdoe' and 'jdopple' *)   ")
    lines.append("#21=PERSON('jdoe','Doppelganger','Jane',$,$,$);")
    lines.append("/* Shared organization for both persons */")
    lines.append("#22=ORGANIZATION('ORG-001','Acme Engineering','Mechanical design division');")
    lines.append("#23=PERSON_AND_ORGANIZATION(#20,#22);")
    lines.append("#24=PERSON_AND_ORGANIZATION(#21,#22);")
    lines.append("/* Product under review */")
    lines.append("#30=PRODUCT('PART-088','Gear Housing','Precision gear enclosure',(#1));")
    lines.append("#31=PRODUCT_DEFINITION_FORMATION('rev_B','Engineering change rev B',#30);")
    lines.append("#32=PRODUCT_DEFINITION('design','',#31,PRODUCT_DEFINITION_CONTEXT(#1,'design'));")
    lines.append("/* APPROVAL entity for the rev_B design review */")
    lines.append("#40=APPROVAL(APPROVAL_STATUS('approved'),'Rev B design approval');")
    lines.append("#42=APPLIED_APPROVAL_ASSIGNMENT(#40,(#32));")
    lines.append("/* DEFECT: APPROVAL_PERSON_ORGANIZATION refers to #23 (person 'jdoe' = John Doe) */")
    lines.append("/* but #24 also exists with the same id 'jdoe' (Jane Doppelganger) */")
    lines.append("/* The approval record is ambiguous: which 'jdoe' signed off on rev_B? */")
    lines.append("#41=APPROVAL_PERSON_ORGANIZATION(#23,#40,APPROVAL_ROLE('approver'));")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#500=GEOMETRIC_CURVE_SET('ap203-person-id-collision-jdoe',")
    lines.append("  (#20,#21,#22,#23,#24,#30,#31,#32,#40,#41,#42));")
    lines.append("/* Product chain */")
    lines.append("#600=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#601=PRODUCT_CONTEXT('',#600,'mechanical');")
    lines.append("#602=PRODUCT('M134','M134','M134',(#601));")
    lines.append("#603=PRODUCT_DEFINITION_FORMATION('','',#602);")
    lines.append("#604=PRODUCT_DEFINITION_CONTEXT(#600,'design');")
    lines.append("#605=PRODUCT_DEFINITION('','',#603,#604);")
    lines.append("#606=PRODUCT_DEFINITION_SHAPE('','',#605);")
    lines.append("#607=SHAPE_REPRESENTATION('',(#500),#14);")
    lines.append("#608=SHAPE_DEFINITION_REPRESENTATION(#606,#607);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m134(path) -> None:
    Path(path).write_text(_render_m134())


f.render = _render_m134  # type: ignore[method-assign]
f.write = _write_m134    # type: ignore[method-assign]
