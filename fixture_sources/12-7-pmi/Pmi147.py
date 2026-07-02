"""Pmi147 — AP242 Ed.3 `GEOMETRY_BASED_ITEM_WITHIN_REPRESENTATION` per-item geometry reference dropped by Ed.2 readers.

Catalog claim: STEP AP242 Edition 3 file with a cube `MANIFOLD_SOLID_BREP` and
a position tolerance applied to a specific face (F1 = the +Z face of the cube).
The link between the tolerance annotation and the specific target face is
expressed via a `GEOMETRY_BASED_ITEM_WITHIN_REPRESENTATION` entity — a new
AP242 Ed.3 entity that identifies a `REPRESENTATION_ITEM` (here, the
`ADVANCED_FACE` F1) within its containing `MANIFOLD_SURFACE_SHAPE_REPRESENTATION`
context. The file header declares the AP242 Ed.3 OID
(`{1 0 10303 442 4 1 4}`) with schema name `AUTOMOTIVE_DESIGN`.

Expected:
- Geometry loads under any reader (cube MANIFOLD_SOLID_BREP with 6 faces).
- Under AP242 Ed.3 readers, `GEOMETRY_BASED_ITEM_WITHIN_REPRESENTATION`
  identifies F1 within the shape representation and the position tolerance
  annotation is correctly linked to F1.
- Under AP242 Ed.2 / AP214 readers, the Ed.3-only entity produces a Void
  transfer status: the position tolerance annotation still loads but no
  target-face link can be recovered — downstream tools cannot determine which
  face the tolerance applies to.

Source: https://www.steptools.com/docs/stp_aim/notes_ap242e3.html (AP242 Ed.3
21-new-entities list — `GEOMETRY_BASED_ITEM_WITHIN_REPRESENTATION` §4.4). B4
wave-7 DEF-OO. Confidence: MEDIUM — accept-live-oracle. Ed.3 entity's exact
semantic is defined only in Ed.3; OCCT drops the Ed.3 entity and loads the
geometry as if AP214. That IS the defect.

Byte assertions:
  contains(b'GEOMETRY_BASED_ITEM_WITHIN_REPRESENTATION')
  contains(b'10303 442 4 1 4')
  contains(b'MANIFOLD_SOLID_BREP')
  contains(b'ADVANCED_FACE')
Tier-3: shape_null == False
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi147",
    schema="AP242",  # base; header overridden below to Ed.3 OID
    defect=(
        "AP242 Ed.3 file: cube MANIFOLD_SOLID_BREP (10x10x10 mm) with a "
        "position tolerance applied to a specific face F1 (+Z face) via a "
        "GEOMETRY_BASED_ITEM_WITHIN_REPRESENTATION entity (AP242 Ed.3 §4.4, "
        "one of 21 new Ed.3 entities); header OID = {1 0 10303 442 4 1 4}; "
        "GEOMETRY_BASED_ITEM_WITHIN_REPRESENTATION identifies F1 within the "
        "MANIFOLD_SURFACE_SHAPE_REPRESENTATION context; Ed.3 readers link the "
        "position tolerance to F1; Ed.2 / AP214 readers drop the entity "
        "silently — the annotation still loads but the target-face link is "
        "absent; edition-boundary drop; steptools notes_ap242e3.html; "
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
# F1 — the +Z face — the target of the position tolerance
face_zp = make_plane_face((0,0,S), (0,0,1), (1,0,0),
                           [(0,0,S),(0,S,S),(S,S,S),(S,0,S)])
face_zn = make_plane_face((0,0,0), (0,0,-1), (-1,0,0),
                           [(0,0,0),(S,0,0),(S,S,0),(0,S,0)])

all_faces = [face_xp, face_xn, face_yp, face_yn, face_zp, face_zn]
face_refs = ",".join(f"#{fa.eid}" for fa in all_faces)
shell = f._emit_raw(f"CLOSED_SHELL('pmi147_shell',({face_refs}))")
msb   = f._emit_raw(f"MANIFOLD_SOLID_BREP('pmi147_cube',#{shell.eid})")
f.add_product_chain(msb, mode="brep_shape")

# ── Shape-representation container (MANIFOLD_SURFACE_SHAPE_REPRESENTATION) ────
# The Ed.3 GEOMETRY_BASED_ITEM_WITHIN_REPRESENTATION entity identifies a
# REPRESENTATION_ITEM (F1) as belonging to a specific REPRESENTATION context.
# We emit a MANIFOLD_SURFACE_SHAPE_REPRESENTATION explicitly so the
# per-item geometry-based reference has a resolvable container.
face_refs_list = ",".join(f"#{fa.eid}" for fa in all_faces)
mssr = f._emit_raw(
    f"MANIFOLD_SURFACE_SHAPE_REPRESENTATION('pmi147_mssr',"
    f"({face_refs_list}),#9060)"
)

# ── Position tolerance annotation targeting F1 (+Z face) ──────────────────────
# SHAPE_ASPECT anchor for F1 (the annotation's semantic host)
shape_aspect_f1 = f._emit_raw(
    f"SHAPE_ASPECT('face_F1','position tolerance host face',#9055,.F.)"
)
# DESCRIPTIVE_REPRESENTATION_ITEM for the position tolerance text
dri = f._emit_raw(
    "DESCRIPTIVE_REPRESENTATION_ITEM('position_tol','POS 0.05 A B C')"
)
# ANNOTATION_OCCURRENCE for the position tolerance callout
annot = f._emit_raw(
    f"ANNOTATION_OCCURRENCE('pos_tol_F1',$,#{dri.eid})"
)

# ── AP242 Ed.3 GEOMETRY_BASED_ITEM_WITHIN_REPRESENTATION ─────────────────────
# Per AP242 Ed.3 §4.4: identifies a specific REPRESENTATION_ITEM (here F1)
# within a REPRESENTATION context (here the MANIFOLD_SURFACE_SHAPE_REPRESENTATION).
# Attributes per Ed.3: (name, item, representation)
# Byte assertion: contains(b'GEOMETRY_BASED_ITEM_WITHIN_REPRESENTATION')
# This entity does NOT exist in AP242 Ed.2 or earlier schemas.
geom_based_item = f._emit_raw(
    f"GEOMETRY_BASED_ITEM_WITHIN_REPRESENTATION('F1_in_mssr',"
    f"#{face_zp.eid},#{mssr.eid})"
)

# ── Tie the position tolerance annotation to F1 via the geometry-based-item ──
# In AP242 Ed.3, the tolerance→face link travels:
#   ANNOTATION → GEOMETRY_BASED_ITEM_WITHIN_REPRESENTATION → face.
# Emit a REPRESENTATION that collects (annotation, geom-based-item, shape_aspect)
# so the linkage is discoverable via the standard property-definition pathway.
prop_def = f._emit_raw(
    f"PROPERTY_DEFINITION('pos_tol_on_F1','position tolerance on face F1',#9055)"
)
pos_tol_rep = f._emit_raw(
    f"REPRESENTATION('pos_tol_rep',(#{annot.eid},#{geom_based_item.eid},"
    f"#{shape_aspect_f1.eid}),#9060)"
)
f._emit_raw(
    f"PROPERTY_DEFINITION_REPRESENTATION(#{prop_def.eid},#{pos_tol_rep.eid})"
)
