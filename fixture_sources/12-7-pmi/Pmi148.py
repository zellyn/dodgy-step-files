"""Pmi148 — AP242 Ed.3 `ANNOTATION_PLACEHOLDER_LEADER_LINE` entity dropped by Ed.2/AP214 readers.

Catalog claim: STEP AP242 Edition 3 file with a minimal cube
`MANIFOLD_SOLID_BREP` (6-face 10×10×10 mm) plus one PMI
`ANNOTATION_PLACEHOLDER` (an unfilled callout slot at world position
`(15, 0, 5)`) linked to a top-face `SHAPE_ASPECT` via
`ANNOTATION_PLACEHOLDER_LEADER_LINE('pl_leader',#placeholder,#face_top_sa,$)`
— a new AP242 Ed.3 entity that carries a leader line running from an
unfilled placeholder-callout to a specific host face. The file header
declares the AP242 Ed.3 OID (`{1 0 10303 442 4 1 4}`) with schema name
`AUTOMOTIVE_DESIGN`.

Expected:
- Geometry loads under any reader (cube MANIFOLD_SOLID_BREP with 6 faces).
- Under AP242 Ed.3 readers, `ANNOTATION_PLACEHOLDER_LEADER_LINE`
  resolves and the placeholder+leader pair is exposed via the PMI API.
- Under AP242 Ed.2 / AP214 readers, `ANNOTATION_PLACEHOLDER_LEADER_LINE`
  produces a `Void` transfer status: the `ANNOTATION_PLACEHOLDER` may
  still load individually but the leader-to-face link is silently absent.

Source: https://www.steptools.com/docs/stp_aim/notes_ap242e3.html (AP242
Ed.3 21-new-entities list — `ANNOTATION_PLACEHOLDER_LEADER_LINE` §4.5).
B4 wave-8 DEF-PP. Confidence: HIGH — entity is precisely named in the
Ed.3 EXPRESS.

Byte assertions:
  contains(b'ANNOTATION_PLACEHOLDER_LEADER_LINE')
  contains(b'ANNOTATION_PLACEHOLDER')
  contains(b'10303 442 4 1 4')
  contains(b'MANIFOLD_SOLID_BREP')
Tier-3: shape_null == False
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi148",
    schema="AP242",  # base; header overridden below to Ed.3 OID
    defect=(
        "AP242 Ed.3 file: cube MANIFOLD_SOLID_BREP (10x10x10 mm) plus one PMI "
        "ANNOTATION_PLACEHOLDER (unfilled callout slot at (15, 0, 5)) linked "
        "to the top face's SHAPE_ASPECT via ANNOTATION_PLACEHOLDER_LEADER_LINE "
        "(AP242 Ed.3 §4.5 leader-line family, one of 21 new Ed.3 entities); "
        "header OID = {1 0 10303 442 4 1 4}; Ed.3 readers resolve the "
        "placeholder+leader pair; Ed.2 / AP214 readers produce Void transfer "
        "status on the leader-line entity — the placeholder callout may still "
        "load but the leader-to-face link is silently absent; edition-boundary "
        "drop; steptools notes_ap242e3.html; MANIFOLD_SOLID_BREP IS model "
        "entity — OCC yields shape(1)"
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
face_yp = make_plane_face((0,S,0), (0,1,0), (S,0,0),
                           [(0,S,0),(S,S,0),(S,S,S),(0,S,S)])
face_yn = make_plane_face((0,0,0), (0,-1,0), (0,0,1),
                           [(0,0,0),(0,0,S),(S,0,S),(S,0,0)])
# The +Z face is the top face — the host face of the leader line.
face_zp = make_plane_face((0,0,S), (0,0,1), (1,0,0),
                           [(0,0,S),(0,S,S),(S,S,S),(S,0,S)])
face_zn = make_plane_face((0,0,0), (0,0,-1), (-1,0,0),
                           [(0,0,0),(S,0,0),(S,S,0),(0,S,0)])

all_faces = [face_xp, face_xn, face_yp, face_yn, face_zp, face_zn]
face_refs = ",".join(f"#{fa.eid}" for fa in all_faces)
shell = f._emit_raw(f"CLOSED_SHELL('pmi148_shell',({face_refs}))")
msb   = f._emit_raw(f"MANIFOLD_SOLID_BREP('pmi148_cube',#{shell.eid})")
f.add_product_chain(msb, mode="brep_shape")

# ── SHAPE_ASPECT anchoring the top face (the leader's target) ────────────────
# Byte assertion: contains(b'SHAPE_ASPECT') (present via PMI regex, also OK).
face_top_sa = f._emit_raw(
    f"SHAPE_ASPECT('top_face','placeholder leader target face',#9055,.F.)"
)

# ── ANNOTATION_PLACEHOLDER: an unfilled callout slot at (15, 0, 5) ────────────
# The placeholder acts as a "reserved" callout that will be filled by a later
# authoring step. In AP242 Ed.3, ANNOTATION_PLACEHOLDER is a
# DRAUGHTING_CALLOUT specialization that carries no content yet.
# Byte assertion: contains(b'ANNOTATION_PLACEHOLDER')
placeholder_pt = f.cartesian_point((15.0, 0.0, 5.0))
placeholder = f._emit_raw(
    f"ANNOTATION_PLACEHOLDER('pl_callout','unfilled callout slot',"
    f"#{placeholder_pt.eid})"
)

# ── AP242 Ed.3 ANNOTATION_PLACEHOLDER_LEADER_LINE ────────────────────────────
# Per AP242 Ed.3 §4.5: this entity attaches a leader line from an
# ANNOTATION_PLACEHOLDER to a target SHAPE_ASPECT (or other host).
# Attributes per Ed.3: (name, placeholder, target, leader_line_geometry).
# Byte assertion: contains(b'ANNOTATION_PLACEHOLDER_LEADER_LINE')
# This entity does NOT exist in AP242 Ed.2 or earlier schemas — Ed.2 / AP214
# readers produce a Void transfer status on this entity and silently drop the
# placeholder-to-face leader link.
leader = f._emit_raw(
    f"ANNOTATION_PLACEHOLDER_LEADER_LINE('pl_leader',"
    f"#{placeholder.eid},#{face_top_sa.eid},$)"
)

# ── Tie the placeholder+leader chain into the product's PMI representation ────
prop_def = f._emit_raw(
    f"PROPERTY_DEFINITION('pmi_placeholder','placeholder callout with leader',#9055)"
)
placeholder_rep = f._emit_raw(
    f"REPRESENTATION('placeholder_rep',(#{placeholder.eid},#{leader.eid},"
    f"#{face_top_sa.eid}),#9060)"
)
f._emit_raw(
    f"PROPERTY_DEFINITION_REPRESENTATION(#{prop_def.eid},#{placeholder_rep.eid})"
)
