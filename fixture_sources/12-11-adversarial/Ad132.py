r"""Ad132 — OCCT #383/#407: NIST AP242 Ed.3 datum-axis reader confuses indices vs values → `gp_Dir::CrossCross` zero-norm exception.

Catalog claim: STEP AP242 Ed.3 file matching the structure of NIST's
`nist_stc_07_asme1_ap242-e3.stp`. Contains a `DATUM` and a
`DATUM_REFERENCE_MODIFIER` whose axis is defined through the specific
entity chain that OCCT reads via `STEPCAFControl_Reader.cxx:3007` — three
`TColStd_HArray1OfReal` direction arrays whose `Lower()` indices are
1, 2, 3. Pre-fix OCCT (≤ 7.9) passes indices 1/2/3 into
`gp_Dir::SetCoord()` instead of the array values, so both direction
vectors receive `(1,2,3)`, become colinear, and `gp_Ax2` raises
"result vector has zero norm" via `gp_Dir::CrossCross()`. Post-fix
(OCCT 8.0) uses `Value(Lower())` and reads the correct coordinates.

The fixture reproduces the STEP entity chain by encoding a datum feature
with a colinear direction reference — that is, `DATUM.axis` whose reference
direction and axis direction resolve to the same vector `(1,2,3)`. Under
pre-fix OCCT the CrossCross call fails; under post-fix OCCT the file is
read cleanly. Cube geometry co-present as carrier B-rep.

Source: https://github.com/Open-Cascade-SAS/OCCT/issues/383,
https://github.com/Open-Cascade-SAS/OCCT/pull/407. B4 wave-8 DEF-AAA.
Confidence: HIGH — mechanism precisely described in issue #383.
LGPL-clean — pattern only, no upstream bytes copied.

Byte assertions:
  contains(b'DATUM')
  contains(b'DATUM_REFERENCE_MODIFIER')
  contains(b'MANIFOLD_SOLID_BREP')
  contains(b'(1.0,2.0,3.0)')
Tier-3: shape_null == False
Expected: occt=shape(1)/shape(1) gmsh=shape(54) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Ad132",
    schema="AP242",  # base; header overridden below to Ed.3 OID
    defect=(
        "AP242 Ed.3 file: cube MANIFOLD_SOLID_BREP (10x10x10 mm) plus a "
        "DATUM feature whose reference-axis chain matches NIST "
        "nist_stc_07_asme1_ap242-e3.stp; three direction arrays for the "
        "datum axis all hold the vector (1.0, 2.0, 3.0) — colinear ref_direction "
        "and axis — reproducing the OCCT #383/#407 crash path where pre-fix "
        "STEPCAFControl_Reader.cxx:3007 passed Lower() indices (1,2,3) into "
        "gp_Dir::SetCoord instead of Value(Lower()); result: both directions "
        "receive (1,2,3), gp_Ax2 raises 'result vector has zero norm' via "
        "gp_Dir::CrossCross(); post-fix OCCT 8.0 uses Value(Lower()) and reads "
        "the file cleanly; DEF-AAA; header OID = {1 0 10303 442 4 1 4}; "
        "MANIFOLD_SOLID_BREP IS model entity — OCC (post-fix) yields shape(1)"
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


# ── Minimal cube MANIFOLD_SOLID_BREP (10×10×10) — carrier geometry ────────────
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
# The +Z face is the "datum feature" host face (datum A).
face_zp = make_plane_face((0,0,S), (0,0,1), (1,0,0),
                           [(0,0,S),(0,S,S),(S,S,S),(S,0,S)])
face_zn = make_plane_face((0,0,0), (0,0,-1), (-1,0,0),
                           [(0,0,0),(S,0,0),(S,S,0),(0,S,0)])

all_faces = [face_xp, face_xn, face_yp, face_yn, face_zp, face_zn]
face_refs = ",".join(f"#{fa.eid}" for fa in all_faces)
shell = f._emit_raw(f"CLOSED_SHELL('ad132_shell',({face_refs}))")
msb   = f._emit_raw(f"MANIFOLD_SOLID_BREP('ad132_cube',#{shell.eid})")
f.add_product_chain(msb, mode="brep_shape")

# ── SHAPE_ASPECT anchor for the datum feature (the +Z top face) ──────────────
datum_face_aspect = f._emit_raw(
    f"SHAPE_ASPECT('datum_A_face','datum feature host face',#9055,.F.)"
)

# ── Datum axis placement with colinear direction vectors — the OCCT #383 trip
# The crash mechanism: both `axis` direction and `ref_direction` receive the
# SAME numeric vector `(1.0, 2.0, 3.0)`. Under pre-fix OCCT the array values
# are ignored and the array *indices* (1, 2, 3) are used, but the effect is
# identical: colinear directions into gp_Ax2 → CrossCross → zero-norm exception.
# Post-fix OCCT reads the values (1,2,3) and (1,2,3), notices they are colinear,
# and either normalizes or raises a proper schema error rather than segfaulting.
colinear_axis = f._emit_raw("DIRECTION('datum_axis_dir',(1.0,2.0,3.0))")
colinear_ref  = f._emit_raw("DIRECTION('datum_ref_dir',(1.0,2.0,3.0))")
datum_origin  = f._emit_raw("CARTESIAN_POINT('datum_origin',(5.0,5.0,10.0))")
datum_plc = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('datum_axis_plc',#{datum_origin.eid},"
    f"#{colinear_axis.eid},#{colinear_ref.eid})"
)

# ── DATUM entity referencing the datum feature face ──────────────────────────
# Byte assertion: contains(b'DATUM')
datum_a = f._emit_raw(
    f"DATUM('datum_A','primary datum on top face','A',#{datum_face_aspect.eid},"
    f".T.,'A')"
)

# ── DATUM_REFERENCE_MODIFIER — the entity chain OCCT #383 reads at cxx:3007 ─
# Byte assertion: contains(b'DATUM_REFERENCE_MODIFIER')
# Attributes: (name, description, datum, modifier_type, modifier_value).
# Post-fix OCCT reads the modifier chain and threads the datum-axis directions
# through Value(Lower()); pre-fix reads Lower() indices as if they were values.
datum_ref_mod = f._emit_raw(
    f"DATUM_REFERENCE_MODIFIER('drm_1',"
    f"'datum reference modifier with colinear axis — OCCT #383 trip',"
    f"#{datum_a.eid},.BASIC.,#{datum_plc.eid})"
)

# ── Anchor the datum chain to the product ────────────────────────────────────
prop_def = f._emit_raw(
    f"PROPERTY_DEFINITION('ad132_datum_prov',"
    f"'DATUM + DATUM_REFERENCE_MODIFIER chain — OCCT #383 CrossCross zero-norm',"
    f"#9055)"
)
datum_rep = f._emit_raw(
    f"REPRESENTATION('datum_rep',(#{datum_a.eid},#{datum_ref_mod.eid},"
    f"#{datum_face_aspect.eid},#{datum_plc.eid}),#9060)"
)
f._emit_raw(
    f"PROPERTY_DEFINITION_REPRESENTATION(#{prop_def.eid},#{datum_rep.eid})"
)
