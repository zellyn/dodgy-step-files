"""Pmi152 — AP242 Ed.3 `AUXILIARY_LEADER_LINE` (secondary leader for symmetric-feature callout) dropped by Ed.2/AP214 readers.

Catalog claim: STEP AP242 Edition 3 file with a minimal cube
`MANIFOLD_SOLID_BREP` (6-face 10×10×10 mm) plus one PMI symmetric-feature
position tolerance callout with TWO leaders: (a) a primary
`ANNOTATION_TO_MODEL_LEADER_LINE` pointing at the top face, and (b) a
secondary `AUXILIARY_LEADER_LINE('aux_leader',#annot,#face_symm,$)`
pointing at the mirror feature (the bottom face — the symmetric
counterpart). The Ed.3 `AUXILIARY_LEADER_LINE` entity is a secondary
leader that branches from a primary leader to add a second callout
target (typical use: a single GD&T frame that applies to two mirror
features at once, indicated by primary + auxiliary leaders).

The file header declares the AP242 Ed.3 OID (`{1 0 10303 442 4 1 4}`)
with schema name `AUTOMOTIVE_DESIGN`.

Expected:
- Geometry loads under any reader (cube MANIFOLD_SOLID_BREP with 6 faces).
- Under AP242 Ed.3 readers, BOTH leaders resolve — the callout shows
  as applying to both the top face (primary leader) and the bottom face
  (auxiliary leader).
- Under AP242 Ed.2 / AP214 readers, `AUXILIARY_LEADER_LINE` produces
  a `Void` transfer status: the imported callout appears with only
  the primary leader (silently missing the symmetric-feature indication).
  Downstream inspection tools will apply the tolerance only to the top
  face and skip the mirror feature.

Source: https://www.steptools.com/docs/stp_aim/notes_ap242e3.html (AP242
Ed.3 21-new-entities list — `AUXILIARY_LEADER_LINE` §4.5). B4 wave-8
DEF-SS. Confidence: HIGH — entity is precisely named in the Ed.3 EXPRESS.

Byte assertions:
  contains(b'AUXILIARY_LEADER_LINE')
  contains(b'ANNOTATION_TO_MODEL_LEADER_LINE')
  contains(b'10303 442 4 1 4')
  contains(b'MANIFOLD_SOLID_BREP')
Tier-3: shape_null == False
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi152",
    schema="AP242",  # base; header overridden below to Ed.3 OID
    defect=(
        "AP242 Ed.3 file: cube MANIFOLD_SOLID_BREP (10x10x10 mm) plus a PMI "
        "symmetric-feature position tolerance callout with TWO leaders: "
        "(a) primary ANNOTATION_TO_MODEL_LEADER_LINE pointing at the top "
        "face, and (b) secondary AUXILIARY_LEADER_LINE pointing at the "
        "mirror bottom face (AP242 Ed.3 §4.5 leader-line family, one of 21 "
        "new Ed.3 entities); header OID = {1 0 10303 442 4 1 4}; Ed.3 "
        "readers resolve both leaders — the callout applies to both faces; "
        "Ed.2 / AP214 readers produce Void transfer status on the auxiliary "
        "leader — the imported callout has only the primary leader and the "
        "symmetric-feature indication is silently lost; downstream inspection "
        "tools skip the mirror feature; edition-boundary drop; steptools "
        "notes_ap242e3.html; MANIFOLD_SOLID_BREP IS model entity — OCC "
        "yields shape(1)"
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
# The +Z face is the top face — primary leader target.
face_zp = make_plane_face((0,0,S), (0,0,1), (1,0,0),
                           [(0,0,S),(0,S,S),(S,S,S),(S,0,S)])
# The −Z face is the bottom face — auxiliary (symmetric mirror) leader target.
face_zn = make_plane_face((0,0,0), (0,0,-1), (-1,0,0),
                           [(0,0,0),(S,0,0),(S,S,0),(0,S,0)])

all_faces = [face_xp, face_xn, face_yp, face_yn, face_zp, face_zn]
face_refs = ",".join(f"#{fa.eid}" for fa in all_faces)
shell = f._emit_raw(f"CLOSED_SHELL('pmi152_shell',({face_refs}))")
msb   = f._emit_raw(f"MANIFOLD_SOLID_BREP('pmi152_cube',#{shell.eid})")
f.add_product_chain(msb, mode="brep_shape")

# ── Symmetric-feature position tolerance callout (single annotation) ─────────
# One DRAUGHTING_ANNOTATION_OCCURRENCE that applies to BOTH the top face
# (primary leader) and the bottom face (auxiliary leader).
callout_pt = f.cartesian_point((15.0, 5.0, 5.0))
callout_geom = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('symm_pos_tol_geom',(#{callout_pt.eid}))"
)
styled_item = f._emit_raw(
    f"STYLED_ITEM('symm_pos_tol_styling',(),#{callout_geom.eid})"
)
symm_pos_tol_annot = f._emit_raw(
    f"DRAUGHTING_ANNOTATION_OCCURRENCE('symm_pos_tol_callout',"
    f"(#{callout_geom.eid}),#{styled_item.eid})"
)

# The single position tolerance semantic — applies to both mirror features.
pos_tol = f._emit_raw(
    f"POSITION_TOLERANCE('symm_pos_tol','symmetric position 0.2 to top+bottom',"
    f"LENGTH_MEASURE(0.2),#9055)"
)

# ── Primary leader: ANNOTATION_TO_MODEL_LEADER_LINE → top face ───────────────
# Byte assertion: contains(b'ANNOTATION_TO_MODEL_LEADER_LINE')
primary_leader = f._emit_raw(
    f"ANNOTATION_TO_MODEL_LEADER_LINE('primary_top_leader',"
    f"#{symm_pos_tol_annot.eid},#{face_zp.eid},$)"
)

# ── AP242 Ed.3 AUXILIARY_LEADER_LINE — secondary leader → bottom face ────────
# Per AP242 Ed.3 §4.5: this entity represents a secondary leader branching
# from a primary leader (or callout) to add a second target, used for
# symmetric-feature callouts where a single GD&T frame applies to two
# features at once. Attributes per Ed.3:
#   (name, annotation, target_shape_aspect_or_face, leader_line_geometry).
# Byte assertion: contains(b'AUXILIARY_LEADER_LINE')
# This entity does NOT exist in AP242 Ed.2 or earlier schemas — Ed.2 / AP214
# readers produce a Void transfer status on this entity and silently drop
# the auxiliary leader, leaving the imported callout with only the primary
# leader (symmetric-feature indication silently lost).
aux_leader = f._emit_raw(
    f"AUXILIARY_LEADER_LINE('aux_leader',"
    f"#{symm_pos_tol_annot.eid},#{face_zn.eid},$)"
)

# ── Tie the primary+auxiliary chain into the product's PMI representation ────
prop_def = f._emit_raw(
    f"PROPERTY_DEFINITION('pmi_symm_leader',"
    f"'symmetric-feature callout with primary + auxiliary leaders',#9055)"
)
symm_rep = f._emit_raw(
    f"REPRESENTATION('symm_leader_rep',(#{symm_pos_tol_annot.eid},"
    f"#{primary_leader.eid},#{aux_leader.eid},#{pos_tol.eid}),#9060)"
)
f._emit_raw(
    f"PROPERTY_DEFINITION_REPRESENTATION(#{prop_def.eid},#{symm_rep.eid})"
)
