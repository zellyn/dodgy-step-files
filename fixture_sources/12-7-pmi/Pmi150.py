"""Pmi150 — AP242 Ed.3 `ANNOTATION_PLACEHOLDER_OCCURRENCE_WITH_LEADER_LINE` entity dropped by Ed.2/AP214 readers.

Catalog claim: STEP AP242 Edition 3 file with a minimal cube
`MANIFOLD_SOLID_BREP` (6-face 10×10×10 mm) plus one PMI
`DRAUGHTING_ANNOTATION_OCCURRENCE` whose leader is fused into a single
atomic entity: `ANNOTATION_PLACEHOLDER_OCCURRENCE_WITH_LEADER_LINE(...)`.
This is the atomic form of Pmi148's separate placeholder + leader pair
— the Ed.3 §4.5 §7 leader-line family provides two encodings:
(a) DEF-PP / Pmi148: `ANNOTATION_PLACEHOLDER` + `ANNOTATION_PLACEHOLDER_LEADER_LINE`
    (separate entities, linked by reference);
(b) DEF-QQ / this fixture: single atomic
    `ANNOTATION_PLACEHOLDER_OCCURRENCE_WITH_LEADER_LINE` bundling the
    occurrence and the leader-line geometry in one entity instance.
The file header declares the AP242 Ed.3 OID (`{1 0 10303 442 4 1 4}`)
with schema name `AUTOMOTIVE_DESIGN`.

Expected:
- Geometry loads under any reader (cube MANIFOLD_SOLID_BREP with 6 faces).
- Under AP242 Ed.3 readers, `ANNOTATION_PLACEHOLDER_OCCURRENCE_WITH_LEADER_LINE`
  resolves and the atomic occurrence+leader is exposed via the PMI API.
- Under AP242 Ed.2 / AP214 readers,
  `ANNOTATION_PLACEHOLDER_OCCURRENCE_WITH_LEADER_LINE` produces a `Void`
  transfer status and the entire callout+leader disappears — unlike
  DEF-PP where the split placeholder+leader would leave the placeholder
  visible on Ed.2 readers, the atomic form drops everything at once.

Source: https://www.steptools.com/docs/stp_aim/notes_ap242e3.html (AP242
Ed.3 21-new-entities list — `ANNOTATION_PLACEHOLDER_OCCURRENCE_WITH_LEADER_LINE`
§4.5 §7). B4 wave-8 DEF-QQ. Confidence: HIGH — entity is precisely named
in the Ed.3 EXPRESS.

Byte assertions:
  contains(b'ANNOTATION_PLACEHOLDER_OCCURRENCE_WITH_LEADER_LINE')
  contains(b'DRAUGHTING_ANNOTATION_OCCURRENCE')
  contains(b'10303 442 4 1 4')
  contains(b'MANIFOLD_SOLID_BREP')
Tier-3: shape_null == False
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi150",
    schema="AP242",  # base; header overridden below to Ed.3 OID
    defect=(
        "AP242 Ed.3 file: cube MANIFOLD_SOLID_BREP (10x10x10 mm) plus one PMI "
        "DRAUGHTING_ANNOTATION_OCCURRENCE whose leader is fused into a single "
        "atomic ANNOTATION_PLACEHOLDER_OCCURRENCE_WITH_LEADER_LINE entity "
        "(AP242 Ed.3 §4.5 §7 leader-line family, one of 21 new Ed.3 entities; "
        "atomic bundled form as opposed to DEF-PP/Pmi148's split "
        "placeholder+leader pair); header OID = {1 0 10303 442 4 1 4}; Ed.3 "
        "readers resolve the atomic occurrence+leader; Ed.2 / AP214 readers "
        "produce Void transfer status and drop the entire atomic entity — the "
        "callout and its leader-to-face binding both disappear (unlike DEF-PP "
        "where the placeholder would remain visible after leader-drop); "
        "edition-boundary drop; steptools notes_ap242e3.html; "
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
face_yp = make_plane_face((0,S,0), (0,1,0), (1,0,0),
                           [(0,S,0),(S,S,0),(S,S,S),(0,S,S)])
face_yn = make_plane_face((0,0,0), (0,-1,0), (0,0,1),
                           [(0,0,0),(0,0,S),(S,0,S),(S,0,0)])
# The +Z face is the top face — the host face of the atomic leader-line entity.
face_zp = make_plane_face((0,0,S), (0,0,1), (1,0,0),
                           [(0,0,S),(0,S,S),(S,S,S),(S,0,S)])
face_zn = make_plane_face((0,0,0), (0,0,-1), (-1,0,0),
                           [(0,0,0),(S,0,0),(S,S,0),(0,S,0)])

all_faces = [face_xp, face_xn, face_yp, face_yn, face_zp, face_zn]
face_refs = ",".join(f"#{fa.eid}" for fa in all_faces)
shell = f._emit_raw(f"CLOSED_SHELL('pmi150_shell',({face_refs}))")
msb   = f._emit_raw(f"MANIFOLD_SOLID_BREP('pmi150_cube',#{shell.eid})")
f.add_product_chain(msb, mode="brep_shape")

# ── SHAPE_ASPECT anchoring the top face (the atomic leader's target) ─────────
face_top_sa = f._emit_raw(
    f"SHAPE_ASPECT('top_face','atomic leader target face',#9055,.F.)"
)

# ── DRAUGHTING_ANNOTATION_OCCURRENCE + endpoints for the atomic entity ───────
# The atomic entity references a base annotation occurrence and a set of
# leader endpoint points. First emit the annotation occurrence (a
# draughting callout that will be bundled into the atomic entity below).
# Byte assertion: contains(b'DRAUGHTING_ANNOTATION_OCCURRENCE')
callout_pt = f.cartesian_point((15.0, 0.0, 5.0))
callout_geom = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('atomic_callout_geom',(#{callout_pt.eid}))"
)
styled_item = f._emit_raw(
    f"STYLED_ITEM('atomic_callout_styling',(),#{callout_geom.eid})"
)
draughting_occ = f._emit_raw(
    f"DRAUGHTING_ANNOTATION_OCCURRENCE('atomic_occ',"
    f"(#{callout_geom.eid}),#{styled_item.eid})"
)

# Leader endpoint (on the target face): a CARTESIAN_POINT that the
# leader-line geometry terminates at.
leader_end_pt = f.cartesian_point((5.0, 5.0, S))

# ── AP242 Ed.3 ANNOTATION_PLACEHOLDER_OCCURRENCE_WITH_LEADER_LINE ────────────
# Per AP242 Ed.3 §4.5 §7: this atomic entity bundles the annotation
# occurrence, the leader-line target/host, and the leader-line endpoint
# geometry into a single instance. Attributes per Ed.3:
#   (name, occurrence, target_shape_aspect, leader_endpoint_points)
# — the atomic form (as opposed to Pmi148's separate placeholder + leader).
# Byte assertion: contains(b'ANNOTATION_PLACEHOLDER_OCCURRENCE_WITH_LEADER_LINE')
# This entity does NOT exist in AP242 Ed.2 or earlier schemas — Ed.2 / AP214
# readers produce a Void transfer status on this entity and the entire
# atomic callout+leader disappears at once.
atomic_apowll = f._emit_raw(
    f"ANNOTATION_PLACEHOLDER_OCCURRENCE_WITH_LEADER_LINE('atomic_apowll',"
    f"#{draughting_occ.eid},#{face_top_sa.eid},(#{leader_end_pt.eid}))"
)

# ── Tie the atomic occurrence into the product's PMI representation ──────────
prop_def = f._emit_raw(
    f"PROPERTY_DEFINITION('pmi_atomic_apowll',"
    f"'atomic annotation-placeholder occurrence with leader',#9055)"
)
atomic_rep = f._emit_raw(
    f"REPRESENTATION('atomic_apowll_rep',(#{draughting_occ.eid},"
    f"#{atomic_apowll.eid},#{face_top_sa.eid}),#9060)"
)
f._emit_raw(
    f"PROPERTY_DEFINITION_REPRESENTATION(#{prop_def.eid},#{atomic_rep.eid})"
)
