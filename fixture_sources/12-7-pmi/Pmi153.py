"""Pmi153 — AP242 Ed.3 `APLL_POINT` and `APLL_POINT_WITH_SURFACE` leader-endpoint types dropped by Ed.2/AP214 readers.

Catalog claim: STEP AP242 Edition 3 file with a minimal cube
`MANIFOLD_SOLID_BREP` (6-face 10×10×10 mm) where an
`ANNOTATION_PLACEHOLDER_LEADER_LINE` (as in Pmi148) has its endpoint
chain declared using the Ed.3 endpoint-typing entities:
  (a) `APLL_POINT('apll_pt_free',(x,y,z))` — a plain leader endpoint
      in free space (the callout end);
  (b) `APLL_POINT_WITH_SURFACE('apll_pt_on_face',(x,y,z),#face_top)` —
      a leader endpoint tied to a specific `ADVANCED_FACE` (the target
      end, so the endpoint's geometric position is constrained to lie
      on that face).

The `ANNOTATION_PLACEHOLDER_LEADER_LINE` (Pmi148's entity) is present
too and references these endpoint entities so the leader-line's
endpoint types are recoverable.

The file header declares the AP242 Ed.3 OID (`{1 0 10303 442 4 1 4}`)
with schema name `AUTOMOTIVE_DESIGN`.

Expected:
- Geometry loads under any reader (cube MANIFOLD_SOLID_BREP with 6 faces).
- Under AP242 Ed.3 readers, both `APLL_POINT` and
  `APLL_POINT_WITH_SURFACE` resolve and the endpoint chain of the
  leader line is exposed with proper typing (which endpoint is free,
  which is face-constrained).
- Under AP242 Ed.2 / AP214 readers, BOTH endpoint entity types produce
  `Void` transfer status: the endpoint entities are silently dropped;
  if the leader-line container entity itself somehow survived, it
  would have orphan endpoint references pointing at nothing.

Source: https://www.steptools.com/docs/stp_aim/notes_ap242e3.html (AP242
Ed.3 21-new-entities list — `APLL_POINT` and `APLL_POINT_WITH_SURFACE`
§4.5). B4 wave-8 DEF-TT. Confidence: HIGH — entities are precisely
named in the Ed.3 EXPRESS.

Byte assertions:
  contains(b'APLL_POINT_WITH_SURFACE')
  contains(b'APLL_POINT')
  contains(b'ANNOTATION_PLACEHOLDER_LEADER_LINE')
  contains(b'10303 442 4 1 4')
  contains(b'MANIFOLD_SOLID_BREP')
Tier-3: shape_null == False
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi153",
    schema="AP242",  # base; header overridden below to Ed.3 OID
    defect=(
        "AP242 Ed.3 file: cube MANIFOLD_SOLID_BREP (10x10x10 mm) plus an "
        "ANNOTATION_PLACEHOLDER_LEADER_LINE (Pmi148's entity) whose endpoint "
        "chain is declared with the Ed.3 endpoint-typing entities: "
        "(a) APLL_POINT (plain free-space leader endpoint at the callout end) "
        "and (b) APLL_POINT_WITH_SURFACE (endpoint tied to a specific "
        "ADVANCED_FACE — target end, geometrically constrained to lie on "
        "the top face); AP242 Ed.3 §4.5 leader-line family, two of 21 new "
        "Ed.3 entities; header OID = {1 0 10303 442 4 1 4}; Ed.3 readers "
        "resolve both endpoint types and expose the endpoint chain with "
        "proper typing; Ed.2 / AP214 readers produce Void transfer status "
        "on both endpoint entities — the endpoint types are silently dropped, "
        "leaving the leader-line container (if it survived) with orphan "
        "endpoint references; edition-boundary drop; steptools "
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
face_yp = make_plane_face((0,S,0), (0,1,0), (1,0,0),
                           [(0,S,0),(S,S,0),(S,S,S),(0,S,S)])
face_yn = make_plane_face((0,0,0), (0,-1,0), (0,0,1),
                           [(0,0,0),(0,0,S),(S,0,S),(S,0,0)])
# The +Z face is the top face — the surface-constrained endpoint's host.
face_zp = make_plane_face((0,0,S), (0,0,1), (1,0,0),
                           [(0,0,S),(0,S,S),(S,S,S),(S,0,S)])
face_zn = make_plane_face((0,0,0), (0,0,-1), (-1,0,0),
                           [(0,0,0),(S,0,0),(S,S,0),(0,S,0)])

all_faces = [face_xp, face_xn, face_yp, face_yn, face_zp, face_zn]
face_refs = ",".join(f"#{fa.eid}" for fa in all_faces)
shell = f._emit_raw(f"CLOSED_SHELL('pmi153_shell',({face_refs}))")
msb   = f._emit_raw(f"MANIFOLD_SOLID_BREP('pmi153_cube',#{shell.eid})")
f.add_product_chain(msb, mode="brep_shape")

# ── SHAPE_ASPECT anchoring the top face (the leader's target reference) ──────
face_top_sa = f._emit_raw(
    f"SHAPE_ASPECT('top_face','placeholder leader target face',#9055,.F.)"
)

# ── ANNOTATION_PLACEHOLDER: an unfilled callout slot at (15, 0, 5) ───────────
# The placeholder callout body — same as Pmi148 — that owns the leader line.
placeholder_pt = f.cartesian_point((15.0, 0.0, 5.0))
placeholder = f._emit_raw(
    f"ANNOTATION_PLACEHOLDER('pl_callout','unfilled callout slot',"
    f"#{placeholder_pt.eid})"
)

# ── AP242 Ed.3 APLL_POINT — plain free-space leader endpoint (callout end) ───
# Per AP242 Ed.3 §4.5: APLL_POINT declares a leader-line endpoint at a
# specific 3D coordinate with no surface binding.
# Attributes per Ed.3: (name, coordinates).
# Byte assertion: contains(b'APLL_POINT')
# This entity does NOT exist in AP242 Ed.2 or earlier schemas — Ed.2 / AP214
# readers produce a Void transfer status on this entity.
apll_free = f._emit_raw(
    f"APLL_POINT('apll_pt_free',(15.0,0.0,5.0))"
)

# ── AP242 Ed.3 APLL_POINT_WITH_SURFACE — endpoint tied to a face ─────────────
# Per AP242 Ed.3 §4.5: APLL_POINT_WITH_SURFACE declares a leader-line
# endpoint whose 3D position is constrained to lie on a specific host face
# (an ADVANCED_FACE or equivalent surface-bearing entity).
# Attributes per Ed.3: (name, coordinates, host_surface).
# Byte assertion: contains(b'APLL_POINT_WITH_SURFACE')
# This entity does NOT exist in AP242 Ed.2 or earlier schemas — Ed.2 / AP214
# readers produce a Void transfer status on this entity.
apll_on_face = f._emit_raw(
    f"APLL_POINT_WITH_SURFACE('apll_pt_on_face',(5.0,5.0,{S}),#{face_zp.eid})"
)

# ── AP242 Ed.3 ANNOTATION_PLACEHOLDER_LEADER_LINE using the typed endpoints ──
# Same entity as Pmi148 but with the endpoint chain provided via the Ed.3
# APLL_POINT / APLL_POINT_WITH_SURFACE entities. In Ed.3 the leader line
# entity's leader_line_geometry (fourth attr) can be a list of typed
# endpoint entities that specify the polyline geometry with per-endpoint
# surface constraints.
# Byte assertion: contains(b'ANNOTATION_PLACEHOLDER_LEADER_LINE')
leader = f._emit_raw(
    f"ANNOTATION_PLACEHOLDER_LEADER_LINE('pl_leader_typed_endpoints',"
    f"#{placeholder.eid},#{face_top_sa.eid},"
    f"(#{apll_free.eid},#{apll_on_face.eid}))"
)

# ── Tie the placeholder + typed-endpoint leader chain into PMI representation ─
prop_def = f._emit_raw(
    f"PROPERTY_DEFINITION('pmi_apll_endpoints',"
    f"'APLL_POINT + APLL_POINT_WITH_SURFACE typed endpoint chain',#9055)"
)
apll_rep = f._emit_raw(
    f"REPRESENTATION('apll_endpoint_rep',(#{placeholder.eid},"
    f"#{leader.eid},#{apll_free.eid},#{apll_on_face.eid},"
    f"#{face_top_sa.eid}),#9060)"
)
f._emit_raw(
    f"PROPERTY_DEFINITION_REPRESENTATION(#{prop_def.eid},#{apll_rep.eid})"
)
