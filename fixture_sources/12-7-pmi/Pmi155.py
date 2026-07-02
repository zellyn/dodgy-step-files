"""Pmi155 — AP242 Ed.3 data-equivalence assertion+inspection pair (E13 + E14) dropped by Ed.2/AP214 readers.

Catalog claim: STEP AP242 Edition 3 file with a QA-provenance record:
a `DATA_EQUIVALENCE_CRITERION_ASSESSMENT_ASSOCIATION('deca_1',...)`
asserting that this file's simplified representation is equivalent to
a full CAD model under specific criteria, plus a
`DATA_EQUIVALENCE_CRITERION_INSPECTION_ASSOCIATION('deci_1',...)`
recording that the equivalence has been inspected and passed.

Ed.3 readers expose both records; Ed.2 readers drop them; QA workflows
that would consume the equivalence claim silently receive nothing.

The file header declares the AP242 Ed.3 OID (`{1 0 10303 442 4 1 4}`)
with schema name `AUTOMOTIVE_DESIGN`.

Expected:
- Geometry loads under any reader (single planar face carrier).
- Under AP242 Ed.3 readers, both DATA_EQUIVALENCE_CRITERION_*_ASSOCIATION
  entities resolve; QA-provenance records exposed.
- Under AP242 Ed.2 / AP214 readers, both association entities produce
  a `Void` transfer status: the face still loads but the equivalence
  assertion and inspection provenance are silently absent.

Source: https://www.steptools.com/docs/stp_aim/notes_ap242e3.html (AP242
Ed.3 21-new-entities list — `DATA_EQUIVALENCE_CRITERION_ASSESSMENT_ASSOCIATION`
and `DATA_EQUIVALENCE_CRITERION_INSPECTION_ASSOCIATION` §4.4, merged from
E13+E14). B4 wave-8 DEF-ZZ. Confidence: MEDIUM — accept-live-oracle.

Byte assertions:
  contains(b'DATA_EQUIVALENCE_CRITERION_ASSESSMENT_ASSOCIATION')
  contains(b'DATA_EQUIVALENCE_CRITERION_INSPECTION_ASSOCIATION')
  contains(b'10303 442 4 1 4')
Tier-3: shape_null == False
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi155",
    schema="AP242",  # base; header overridden below to Ed.3 OID
    defect=(
        "AP242 Ed.3 file: single-face planar 10x10 mm carrier; two Ed.3 "
        "QA-provenance entities: DATA_EQUIVALENCE_CRITERION_ASSESSMENT_ASSOCIATION"
        "('deca_1',...) asserts that this file's simplified representation is "
        "equivalent to a full CAD model under specified criteria, plus "
        "DATA_EQUIVALENCE_CRITERION_INSPECTION_ASSOCIATION('deci_1',...) records "
        "that the equivalence claim has been inspected and passed (AP242 Ed.3 "
        "§4.4, two of 21 new Ed.3 entities in the data-equivalence family, "
        "merged from E13+E14); header OID = {1 0 10303 442 4 1 4}; Ed.3 readers "
        "expose both records via QA-provenance API; Ed.2 / AP214 readers produce "
        "Void transfer status on both — the face still loads but the equivalence "
        "assertion and inspection provenance are silently absent; QA workflows "
        "that would consume the equivalence claim silently receive nothing; "
        "edition-boundary drop; steptools notes_ap242e3.html; single-face shell "
        "— OCC yields shape(1)"
    ),
)

# ── Override header to AP242 Ed.3 OID with AUTOMOTIVE_DESIGN schema name ─────
_HDR = (
    "HEADER;\n"
    f"FILE_DESCRIPTION(('{f.catalog_id}'),'2;1');\n"
    f"FILE_NAME('{f.catalog_id}.stp','{f.timestamp}',(''),(''),"
    f"'cad-research-suite','','');\n"
    "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 442 4 1 4 }'));\n"
    "ENDSEC;"
)
f._render_header = lambda: _HDR

# ── Single planar ADVANCED_FACE (10×10 mm patch in the XY plane) ──────────────
S = 10.0

plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
plane = f.plane(plc, name="pmi155_plane")

p00 = f.cartesian_point((0.0, 0.0, 0.0))
p10 = f.cartesian_point((S,   0.0, 0.0))
p11 = f.cartesian_point((S,   S,   0.0))
p01 = f.cartesian_point((0.0, S,   0.0))
loop = f.closed_polyline_loop([p00, p10, p11, p01])
fob  = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane, name="pmi155_face")

shell = f.open_shell([face], name="pmi155_shell")
sbsm  = f.shell_based_surface_model([shell], name="pmi155_sbsm")
f.add_product_chain(sbsm)

# ── SHAPE_ASPECT anchor for the face (QA-provenance host) ────────────────────
shape_aspect = f._emit_raw(
    f"SHAPE_ASPECT('face_aspect','simplified-representation host',#9055,.F.)"
)

# ── Descriptive-representation-item recording the equivalence criteria ───────
criteria = f._emit_raw(
    "DESCRIPTIVE_REPRESENTATION_ITEM('equivalence_criteria',"
    "'geometric tolerance 0.01 mm; topology preserved; PMI count matches')"
)

# ── AP242 Ed.3 DATA_EQUIVALENCE_CRITERION_ASSESSMENT_ASSOCIATION (E13) ───────
# Per AP242 Ed.3 §4.4: this entity asserts that a simplified representation
# is equivalent to a full CAD model under a set of specified criteria.
# Attributes per Ed.3: (name, description, criteria, assessed_representation).
# Byte assertion: contains(b'DATA_EQUIVALENCE_CRITERION_ASSESSMENT_ASSOCIATION')
# Ed.2 / AP214 readers produce Void transfer status on this entity.
deca = f._emit_raw(
    f"DATA_EQUIVALENCE_CRITERION_ASSESSMENT_ASSOCIATION('deca_1',"
    f"'simplified representation is equivalent to full CAD model',"
    f"#{criteria.eid},#{shape_aspect.eid})"
)

# ── AP242 Ed.3 DATA_EQUIVALENCE_CRITERION_INSPECTION_ASSOCIATION (E14) ───────
# Per AP242 Ed.3 §4.4: this entity records that the equivalence assertion
# has been inspected and passed a QA gate. Attributes per Ed.3:
# (name, description, assessed_association, inspection_result).
# Byte assertion: contains(b'DATA_EQUIVALENCE_CRITERION_INSPECTION_ASSOCIATION')
# Ed.2 / AP214 readers produce Void transfer status on this entity too.
inspection_result = f._emit_raw(
    "DESCRIPTIVE_REPRESENTATION_ITEM('inspection_result',"
    "'PASSED; inspector=jsmith; 2026-06-30')"
)
deci = f._emit_raw(
    f"DATA_EQUIVALENCE_CRITERION_INSPECTION_ASSOCIATION('deci_1',"
    f"'equivalence claim inspected and passed',"
    f"#{deca.eid},#{inspection_result.eid})"
)

# ── Anchor the QA-provenance chain to the product ────────────────────────────
prop_def = f._emit_raw(
    f"PROPERTY_DEFINITION('pmi155_equivalence_provenance',"
    f"'data-equivalence assertion + inspection',#9055)"
)
prov_rep = f._emit_raw(
    f"REPRESENTATION('equivalence_prov_rep',(#{deca.eid},#{deci.eid},"
    f"#{criteria.eid},#{inspection_result.eid},#{shape_aspect.eid}),#9060)"
)
f._emit_raw(
    f"PROPERTY_DEFINITION_REPRESENTATION(#{prop_def.eid},#{prov_rep.eid})"
)
