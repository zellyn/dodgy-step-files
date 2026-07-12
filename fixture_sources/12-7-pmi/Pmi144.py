"""Pmi144 — AP242 Ed.3 `ANNOTATION_TO_ANNOTATION_LEADER_LINE` entity dropped by Ed.2 readers.

Catalog claim: STEP AP242 Edition 3 file with two PMI annotation callouts — a
position tolerance frame and a datum feature label — linked by an
`ANNOTATION_TO_ANNOTATION_LEADER_LINE` entity newly introduced in AP242 Ed.3.
The file header declares the AP242 Ed.3 OID (`{1 0 10303 442 4 1 4}`) with the
schema name written literally as `AUTOMOTIVE_DESIGN` (a hybrid header pattern
observed in Ed.3 exports from Ed.2-based writers upgraded to the newer OID).
The file also contains a minimal cube `MANIFOLD_SOLID_BREP` so the geometry
loads under all readers.

Expected:
- Geometry loads under any reader.
- Under AP242 Ed.3 readers, the leader-line entity resolves and the two
  annotations are linked.
- Under AP242 Ed.2 / AP214 readers, `ANNOTATION_TO_ANNOTATION_LEADER_LINE`
  produces a `Void` transfer status: both annotations still load individually
  but the linking entity is silently absent.

Source: https://www.steptools.com/docs/stp_aim/notes_ap242e3.html (AP242 Ed.3
21-new-entities list, `ANNOTATION_TO_ANNOTATION_LEADER_LINE` §4.4). B4 wave-7
DEF-II. Confidence: HIGH — entity name is precisely defined; Ed.3 schema OID
is well-documented.

Byte assertions:
  contains(b'ANNOTATION_TO_ANNOTATION_LEADER_LINE')
  contains(b'ANNOTATION_OCCURRENCE')
  contains(b'10303 442 4 1 4')
  contains(b'MANIFOLD_SOLID_BREP')
Tier-3: shape_null == False
Expected: occt=shape(1)/shape(1) gmsh=shape(54) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi144",
    schema="AP242",  # base; header overridden below to Ed.3 OID
    defect=(
        "AP242 Ed.3 file: two PMI annotation callouts (position tolerance frame + "
        "datum feature label) linked by an ANNOTATION_TO_ANNOTATION_LEADER_LINE "
        "entity (AP242 Ed.3 §4.4, one of 21 new Ed.3 entities); header OID = "
        "{1 0 10303 442 4 1 4}; minimal cube MANIFOLD_SOLID_BREP for geometry; "
        "Ed.3 readers resolve the leader-line link between the two annotations; "
        "Ed.2 / AP214 readers produce Void transfer status on the leader-line "
        "entity — both annotations still load, but the linking entity is silently "
        "absent; edition-boundary drop; steptools notes_ap242e3.html; "
        "MANIFOLD_SOLID_BREP IS model entity — OCC yields shape(1)"
    ),
)

# ── Override header to AP242 Ed.3 OID with AUTOMOTIVE_DESIGN schema name ─────
# The task requires the exact FILE_SCHEMA string:
#   AUTOMOTIVE_DESIGN { 1 0 10303 442 4 1 4 }
# — a hybrid where the schema name is written as AUTOMOTIVE_DESIGN but the
# object identifier is the AP242 Ed.3 OID (last digit '4' = Ed.3).
_HDR = (
    "HEADER;\n"
    f"FILE_DESCRIPTION(('{f.catalog_id}'),'2;1');\n"
    f"FILE_NAME('{f.catalog_id}.stp','{f.timestamp}',(''),(''),"
    f"'cad-research-suite','','');\n"
    "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 442 4 1 4 }'));\n"
    "ENDSEC;"
)
f._render_header = lambda: _HDR

# ── Minimal cube MANIFOLD_SOLID_BREP (10×10×10) ──────────────────────────────
def make_plane_face(origin, zdir_t, xdir_t, points_ccw):
    plc   = f.axis2_placement_3d(
        f.cartesian_point(origin),
        f.direction(zdir_t),
        f.direction(xdir_t),
    )
    plane = f.plane(plc)
    pts   = [f.cartesian_point(p) for p in points_ccw]
    loop  = f.closed_polyline_loop(pts)
    fob   = f.face_outer_bound(loop)
    return f.advanced_face([fob], plane)

S = 10.0

face_xp = make_plane_face((S,0,0), (1,0,0), (0,0,1),
                           [(S,0,0),(S,0,S),(S,S,S),(S,S,0)])
face_xn = make_plane_face((0,0,0), (-1,0,0), (0,0,-1),
                           [(0,0,0),(0,S,0),(0,S,S),(0,0,S)])
face_yp = make_plane_face((0,S,0), (0,1,0), (1,0,0),
                           [(0,S,0),(S,S,0),(S,S,S),(0,S,S)])
face_yn = make_plane_face((0,0,0), (0,-1,0), (0,0,1),
                           [(0,0,0),(0,0,S),(S,0,S),(S,0,0)])
face_zp = make_plane_face((0,0,S), (0,0,1), (1,0,0),
                           [(0,0,S),(0,S,S),(S,S,S),(S,0,S)])
face_zn = make_plane_face((0,0,0), (0,0,-1), (-1,0,0),
                           [(0,0,0),(S,0,0),(S,S,0),(0,S,0)])

all_faces = [face_xp, face_xn, face_yp, face_yn, face_zp, face_zn]
face_refs = ",".join(f"#{fa.eid}" for fa in all_faces)
shell = f._emit_raw(f"CLOSED_SHELL('pmi144_shell',({face_refs}))")
msb   = f._emit_raw(f"MANIFOLD_SOLID_BREP('pmi144_cube',#{shell.eid})")
f.add_product_chain(msb, mode="brep_shape")

# ── Two annotation occurrences and the AP242 Ed.3 leader-line entity ────────
# The two annotations:
#   ANNOT_A: a position tolerance frame at (5,5,S+2) (drafting text callout).
#   ANNOT_B: a datum feature label at (S+2,5,S/2)   (datum-target text callout).
# Both are wrapped as DRAUGHTING_ANNOTATION_OCCURRENCE with placeholder
# DESCRIPTIVE_REPRESENTATION_ITEM content (the fixture's focus is the linking
# entity, not the annotation rendering).

# SHAPE_ASPECT anchor for the top face (annotation A applies here)
shape_aspect_a = f._emit_raw(
    f"SHAPE_ASPECT('top_face','position tolerance host',#9055,.F.)"
)
# SHAPE_ASPECT anchor for the +X face (annotation B applies here)
shape_aspect_b = f._emit_raw(
    f"SHAPE_ASPECT('xp_face','datum feature host',#9055,.F.)"
)

# DESCRIPTIVE_REPRESENTATION_ITEM for the position tolerance text
dri_a = f._emit_raw(
    "DESCRIPTIVE_REPRESENTATION_ITEM('position_tol','POS 0.05 A B C')"
)
# DESCRIPTIVE_REPRESENTATION_ITEM for the datum feature text
dri_b = f._emit_raw(
    "DESCRIPTIVE_REPRESENTATION_ITEM('datum_feature','DATUM A')"
)

# ANNOTATION_OCCURRENCE A (position tolerance frame callout)
# Byte assertion: contains(b'ANNOTATION_OCCURRENCE')
annot_a = f._emit_raw(
    f"ANNOTATION_OCCURRENCE('pos_tol_frame',$,#{dri_a.eid})"
)
# ANNOTATION_OCCURRENCE B (datum feature label callout)
annot_b = f._emit_raw(
    f"ANNOTATION_OCCURRENCE('datum_label',$,#{dri_b.eid})"
)

# ── AP242 Ed.3 ANNOTATION_TO_ANNOTATION_LEADER_LINE entity ────────────────────
# Per AP242 Ed.3 §4.4: this entity links two ANNOTATION_OCCURRENCEs via a
# leader-line construct. Its attributes are (name, source_annotation,
# target_annotation, leader_line_representation) — the last is optional.
# Byte assertion: contains(b'ANNOTATION_TO_ANNOTATION_LEADER_LINE')
# This entity does NOT exist in AP242 Ed.2 or earlier schemas — Ed.2 / AP214
# readers produce a Void transfer status on this entity and silently drop the
# annotation-to-annotation link.
f._emit_raw(
    f"ANNOTATION_TO_ANNOTATION_LEADER_LINE('pos_tol_to_datum_leader',"
    f"#{annot_a.eid},#{annot_b.eid},$)"
)

# PROPERTY_DEFINITION and PROPERTY_DEFINITION_REPRESENTATION anchor the
# annotation chain to the product shape (per AP242 PMI presentation practice).
prop_def = f._emit_raw(
    f"PROPERTY_DEFINITION('pmi_leader','annotation leader link',#9055)"
)
annot_rep = f._emit_raw(
    f"REPRESENTATION('annot_leader_rep',(#{annot_a.eid},#{annot_b.eid}),#9060)"
)
f._emit_raw(
    f"PROPERTY_DEFINITION_REPRESENTATION(#{prop_def.eid},#{annot_rep.eid})"
)
