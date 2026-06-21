"""M138 — AP203 APPROVAL_PERSON_ORGANIZATION with empty PERSON field

Catalog claim: An APPROVAL_PERSON_ORGANIZATION binds an APPROVAL to a
PERSON_AND_ORGANIZATION whose PERSON field is empty — no identifier, no last
name, no first name. The approval has an organizational stamp but no individual
approver. Audit trail is incomplete; the approval cannot be attributed to a person.

Reproducer recipe: PERSON('','',$,$,$,(),(),()) referenced inside
PERSON_AND_ORGANIZATION referenced inside APPROVAL_PERSON_ORGANIZATION.

Byte assertions:
  contains(b'CONFIG_CONTROL_DESIGN')
  contains(b'APPROVAL_PERSON_ORGANIZATION')
  contains(b"PERSON('','',")

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from pathlib import Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M138",
    defect=(
        "GEOMETRIC_CURVE_SET in AP203 CONFIG_CONTROL_DESIGN file where an "
        "APPROVAL_PERSON_ORGANIZATION binds an APPROVAL to a PERSON_AND_ORGANIZATION "
        "whose PERSON has all-empty identity fields (id='', last_name='', first_name=$), "
        "making the audit trail incomplete and the approval unattributable; "
        "input: AP203 STEP file with an APPROVAL entity linked via "
        "APPROVAL_PERSON_ORGANIZATION to a PERSON_AND_ORGANIZATION; the PERSON instance "
        "in that PERSON_AND_ORGANIZATION declares PERSON('','',$,$,$) — empty id, empty "
        "last_name, null first_name, null middle_name, null prefix, empty suffix list; "
        "per ISO 10303-41 §4.4.3 PERSON.last_name is required and must not be empty; "
        "the PERSON.id attribute is intended to uniquely identify the individual; "
        "when both are empty the APPROVAL cannot be attributed to any natural person; "
        "PDM audit trail tools require at minimum a non-empty last_name to record who "
        "approved the design; this is distinct from an anonymous organization role — "
        "here there is a PERSON entity slot but it carries no identifying information; "
        "kernel must detect empty PERSON identity and reject the approval record or warn "
        "that the audit trail is incomplete; "
        "synonyms: AP203 anonymous approver, PDM approval no signer, missing approver "
        "name, AP203 approver missing, approval has no person, PDM audit trail "
        "incomplete"
    ),
    schema="AP242",
)


def _render_m138() -> str:
    """Render AP203 CONFIG_CONTROL_DESIGN file with empty-PERSON APPROVAL_PERSON_ORGANIZATION.

    Entity layout:
      #1-#2      APPLICATION_CONTEXT / APPLICATION_PROTOCOL_DEFINITION
      #10-#14    Unit context (mm)
      #20        PERSON('','',$..) — DEFECT: all-empty identity fields
      #21        ORGANIZATION (provides the organizational stamp)
      #22        PERSON_AND_ORGANIZATION(#20, #21) — anonymous person + real org
      #30        PRODUCT / PRODUCT_DEFINITION_FORMATION / PRODUCT_DEFINITION
      #40        APPROVAL with status
      #41        APPROVAL_PERSON_ORGANIZATION — DEFECT: references empty PERSON
      #42        APPLIED_APPROVAL_ASSIGNMENT
      #500       GEOMETRIC_CURVE_SET model entity
      #600+      Product chain
    """
    lines = []
    lines.append("ISO-10303-21;")
    lines.append("/* M138: AP203 APPROVAL_PERSON_ORGANIZATION with empty PERSON identity fields */")
    lines.append("/* DEFECT: PERSON('','',$,$,$) — id and last_name both empty, no first_name */")
    lines.append("/* The APPROVAL_PERSON_ORGANIZATION links an approval to a person-less record */")
    lines.append("/* Audit trail is incomplete; approval cannot be attributed to any individual */")
    lines.append("/* Per ISO 10303-41 §4.4.3 PERSON.last_name is required and must be non-empty */")
    lines.append("/* Byte assertion: contains(b'CONFIG_CONTROL_DESIGN') */")
    lines.append("/* Byte assertion: contains(b'APPROVAL_PERSON_ORGANIZATION') */")
    lines.append("/* Byte assertion: contains(b\"PERSON('','',\") */")
    lines.append("HEADER;")
    lines.append("FILE_DESCRIPTION(('M138: AP203 APPROVAL_PERSON_ORGANIZATION empty PERSON no audit trail'),'2;1');")
    lines.append("FILE_NAME('M138.stp','2026-06-21T00:00:00',(''),(''),'cad-research-suite','','');")
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
    lines.append("/* Byte assertion: contains(b\"PERSON('','',\") */")
    lines.append("/* DEFECT: PERSON with empty id and empty last_name — violates ISO 10303-41 §4.4.3 */")
    lines.append("/* A PDM exporter identified the approver only by organizational role, omitting personal data */")
    lines.append("/* Any downstream APPROVAL_PERSON_ORGANIZATION referencing this PERSON is unattributable */")
    lines.append("#20=PERSON('','',$,$,$);")
    lines.append("/* Organization provides a stamp (Acme Engineering) but no named individual */")
    lines.append("#21=ORGANIZATION('ORG-007','Acme Engineering','Design approval authority');")
    lines.append("/* PERSON_AND_ORGANIZATION bundles the empty-identity PERSON with the real org */")
    lines.append("#22=PERSON_AND_ORGANIZATION(#20,#21);")
    lines.append("/* Product definition under approval */")
    lines.append("#30=PRODUCT('PART-202','Turbine Disc','High-speed rotating disc assembly',(#1));")
    lines.append("#31=PRODUCT_DEFINITION_FORMATION('rev_D','Release candidate D',#30);")
    lines.append("#32=PRODUCT_DEFINITION('design','',#31,PRODUCT_DEFINITION_CONTEXT(#1,'design'));")
    lines.append("/* APPROVAL entity marking the design as approved */")
    lines.append("#40=APPROVAL(APPROVAL_STATUS('approved'),'Rev D design gate approval');")
    lines.append("/* Byte assertion: contains(b'APPROVAL_PERSON_ORGANIZATION') */")
    lines.append("/* DEFECT: APPROVAL_PERSON_ORGANIZATION references #22 which contains empty PERSON #20 */")
    lines.append("/* The approval role 'approver' requires a named individual; none is present */")
    lines.append("/* A receiving system cannot record 'who approved rev_D' — audit trail is broken */")
    lines.append("#41=APPROVAL_PERSON_ORGANIZATION(#22,#40,APPROVAL_ROLE('approver'));")
    lines.append("#42=APPLIED_APPROVAL_ASSIGNMENT(#40,(#32));")
    lines.append("/* GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty */")
    lines.append("#500=GEOMETRIC_CURVE_SET('ap203-approval-person-org-empty-person-identity',")
    lines.append("  (#20,#21,#22,#30,#31,#32,#40,#41,#42));")
    lines.append("/* Product chain */")
    lines.append("#600=APPLICATION_CONTEXT('mechanical design');")
    lines.append("#601=PRODUCT_CONTEXT('',#600,'mechanical');")
    lines.append("#602=PRODUCT('M138','M138','M138',(#601));")
    lines.append("#603=PRODUCT_DEFINITION_FORMATION('','',#602);")
    lines.append("#604=PRODUCT_DEFINITION_CONTEXT(#600,'design');")
    lines.append("#605=PRODUCT_DEFINITION('','',#603,#604);")
    lines.append("#606=PRODUCT_DEFINITION_SHAPE('','',#605);")
    lines.append("#607=SHAPE_REPRESENTATION('',(#500),#14);")
    lines.append("#608=SHAPE_DEFINITION_REPRESENTATION(#606,#607);")
    lines.append("ENDSEC;")
    lines.append("END-ISO-10303-21;")
    return "\n".join(lines) + "\n"


def _write_m138(path) -> None:
    Path(path).write_text(_render_m138())


f.render = _render_m138  # type: ignore[method-assign]
f.write = _write_m138    # type: ignore[method-assign]
