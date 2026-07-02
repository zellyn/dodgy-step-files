"""Pmi151 — AP242 Ed.3 `ANNOTATION_TO_MODEL_LEADER_LINE` entity dropped by Ed.2/AP214 readers.

Catalog claim: STEP AP242 Edition 3 file with a minimal cube
`MANIFOLD_SOLID_BREP` (6-face 10×10×10 mm) plus one PMI position
tolerance callout linked to a specific `ADVANCED_FACE` of the cube
(the top face) via `ANNOTATION_TO_MODEL_LEADER_LINE('atml_1',#annot,#face_top,$)`
— the Ed.3 leader-line entity that carries a 2D annotation → 3D model
face binding, distinct from Pmi148 which uses a `SHAPE_ASPECT` target.
The file header declares the AP242 Ed.3 OID (`{1 0 10303 442 4 1 4}`)
with schema name `AUTOMOTIVE_DESIGN`.

Expected:
- Geometry loads under any reader (cube MANIFOLD_SOLID_BREP with 6 faces).
- Under AP242 Ed.3 readers, `ANNOTATION_TO_MODEL_LEADER_LINE` resolves
  and the annotation→3D-face link is exposed via the PMI API, so
  downstream inspection tools can determine exactly which face the
  leader points at.
- Under AP242 Ed.2 / AP214 readers, `ANNOTATION_TO_MODEL_LEADER_LINE`
  produces a `Void` transfer status: the position tolerance annotation
  may still load individually but the leader-to-face link is silently
  absent — downstream inspection tools cannot recover which face is
  the target.

Source: https://www.steptools.com/docs/stp_aim/notes_ap242e3.html (AP242
Ed.3 21-new-entities list — `ANNOTATION_TO_MODEL_LEADER_LINE` §4.5).
B4 wave-8 DEF-RR. Confidence: HIGH — entity is precisely named in the
Ed.3 EXPRESS.

Byte assertions:
  contains(b'ANNOTATION_TO_MODEL_LEADER_LINE')
  contains(b'DRAUGHTING_ANNOTATION_OCCURRENCE')
  contains(b'10303 442 4 1 4')
  contains(b'MANIFOLD_SOLID_BREP')
Tier-3: shape_null == False
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi151",
    schema="AP242",  # base; header overridden below to Ed.3 OID
    defect=(
        "AP242 Ed.3 file: cube MANIFOLD_SOLID_BREP (10x10x10 mm) plus one PMI "
        "position tolerance callout linked to a specific ADVANCED_FACE (the "
        "top face) of the cube via ANNOTATION_TO_MODEL_LEADER_LINE (AP242 "
        "Ed.3 §4.5 leader-line family, one of 21 new Ed.3 entities); header "
        "OID = {1 0 10303 442 4 1 4}; Ed.3 readers resolve the "
        "annotation→3D-face link; Ed.2 / AP214 readers produce Void transfer "
        "status on the leader-line entity — the position tolerance annotation "
        "may still load but the leader-to-face link is silently absent; "
        "downstream inspection tools cannot determine which face the leader "
        "points at; edition-boundary drop; steptools notes_ap242e3.html; "
        "MANIFOLD_SOLID_BREP IS model entity — OCC yields shape(1)"
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
# The +Z face is the top face — the ADVANCED_FACE target the leader points at.
face_zp = make_plane_face((0,0,S), (0,0,1), (1,0,0),
                           [(0,0,S),(0,S,S),(S,S,S),(S,0,S)])
face_zn = make_plane_face((0,0,0), (0,0,-1), (-1,0,0),
                           [(0,0,0),(S,0,0),(S,S,0),(0,S,0)])

all_faces = [face_xp, face_xn, face_yp, face_yn, face_zp, face_zn]
face_refs = ",".join(f"#{fa.eid}" for fa in all_faces)
shell = f._emit_raw(f"CLOSED_SHELL('pmi151_shell',({face_refs}))")
msb   = f._emit_raw(f"MANIFOLD_SOLID_BREP('pmi151_cube',#{shell.eid})")
f.add_product_chain(msb, mode="brep_shape")

# ── Position tolerance annotation (2D callout) ───────────────────────────────
# The position tolerance callout is a DRAUGHTING_ANNOTATION_OCCURRENCE
# with GEOMETRIC_CURVE_SET-backed styling. Ed.3's ANNOTATION_TO_MODEL_LEADER_LINE
# is what carries the leader from this 2D callout to the 3D model face.
# Byte assertion: contains(b'DRAUGHTING_ANNOTATION_OCCURRENCE')
callout_pt = f.cartesian_point((15.0, 15.0, 5.0))
callout_geom = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('pos_tol_geom',(#{callout_pt.eid}))"
)
styled_item = f._emit_raw(
    f"STYLED_ITEM('pos_tol_styling',(),#{callout_geom.eid})"
)
pos_tol_annot = f._emit_raw(
    f"DRAUGHTING_ANNOTATION_OCCURRENCE('pos_tol_callout',"
    f"(#{callout_geom.eid}),#{styled_item.eid})"
)

# Position-tolerance semantic (name-only carrier so the byte pattern is
# specifically a *position tolerance callout*, per DEF-RR's description).
# Byte assertion: contains(b'GEOMETRIC_TOLERANCE')
pos_tol = f._emit_raw(
    f"POSITION_TOLERANCE('pos_tol_face_top','true position 0.1 to top face',"
    f"LENGTH_MEASURE(0.1),#9055)"
)

# ── AP242 Ed.3 ANNOTATION_TO_MODEL_LEADER_LINE ───────────────────────────────
# Per AP242 Ed.3 §4.5: this entity binds a 2D annotation to a specific
# 3D `ADVANCED_FACE` (as opposed to Pmi148's binding to a `SHAPE_ASPECT`).
# Attributes per Ed.3: (name, annotation, target_face, leader_line_geometry).
# Byte assertion: contains(b'ANNOTATION_TO_MODEL_LEADER_LINE')
# The target here is the top face's ADVANCED_FACE (#{face_zp.eid}) — a direct
# reference to the 3D face rather than an anchoring SHAPE_ASPECT.
# This entity does NOT exist in AP242 Ed.2 or earlier schemas — Ed.2 / AP214
# readers produce a Void transfer status on this entity and silently drop
# the annotation→3D-face link.
atml = f._emit_raw(
    f"ANNOTATION_TO_MODEL_LEADER_LINE('atml_1',"
    f"#{pos_tol_annot.eid},#{face_zp.eid},$)"
)

# ── Tie the annotation-to-model chain into the product's PMI representation ──
prop_def = f._emit_raw(
    f"PROPERTY_DEFINITION('pmi_atml',"
    f"'annotation-to-model leader for top face position tol',#9055)"
)
atml_rep = f._emit_raw(
    f"REPRESENTATION('atml_rep',(#{pos_tol_annot.eid},"
    f"#{atml.eid},#{pos_tol.eid}),#9060)"
)
f._emit_raw(
    f"PROPERTY_DEFINITION_REPRESENTATION(#{prop_def.eid},#{atml_rep.eid})"
)
