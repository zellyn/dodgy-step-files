"""Pmi140 — OCCT V8 PROPERTY_DEFINITION string metadata invisible to V7 readers.

Catalog claim: a STEP AP214 file with a valid geometry (minimal cube
MANIFOLD_SOLID_BREP) and a PROPERTY_DEFINITION + PROPERTY_DEFINITION_REPRESENTATION
+ DESCRIPTIVE_REPRESENTATION_ITEM chain encoding a string metadata attribute
(material = 'Aluminum 6061'). The geometry loads correctly under any reader;
the DESCRIPTIVE_REPRESENTATION_ITEM string value is readable under OCCT V8+
via UserDefinedAttributes API but silently unavailable under V7.x readers
(no error, metadata just missing).

This is a version-bound historical-fix demonstration: local OCCT may or may
not expose the metadata via UserDefinedAttributes depending on installed version.
The fixture documents the entity chain class.

Source: OCCT V8.0.0 issue #634 (OCCT GitHub release notes)
B4 wave-5 DEF-O. Confidence: HIGH — entity chain precisely specified in AP214.

Byte assertions:
  contains(b'PROPERTY_DEFINITION')
  contains(b'PROPERTY_DEFINITION_REPRESENTATION')
  contains(b'DESCRIPTIVE_REPRESENTATION_ITEM')
  contains(b'Aluminum 6061')
Tier-3: shape_null == False (geometry loads OK regardless of metadata visibility)
Expected: verify with live oracle
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi140",
    defect=(
        "PROPERTY_DEFINITION + PROPERTY_DEFINITION_REPRESENTATION + "
        "DESCRIPTIVE_REPRESENTATION_ITEM chain encodes material='Aluminum 6061'; "
        "geometry (MANIFOLD_SOLID_BREP cube) loads correctly under any reader; "
        "metadata readable under OCCT V8+ UserDefinedAttributes API but silently "
        "absent under V7.x (no error); historical-fix demonstration (OCCT issue #634); "
        "MANIFOLD_SOLID_BREP IS model entity — OCC yields shape(1)"
    ),
)

# ── Minimal cube MANIFOLD_SOLID_BREP (10×10×10 mm) ───────────────────────────
# Six faces: ±X, ±Y, ±Z planes.

def make_plane_face(origin, zdir_t, xdir_t, r, points_ccw):
    """Emit a planar ADVANCED_FACE with a rectangular EDGE_LOOP.

    origin, zdir_t, xdir_t define the plane placement (plane normal = zdir_t).
    r is unused (kept for signature symmetry).
    points_ccw is a list of 4 (x,y,z) tuples in CCW order (winding outward).
    """
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

S = 10.0  # cube side length

face_xp = make_plane_face(  # +X face (x=10)
    (S, 0, 0), (1, 0, 0), (0, 0, 1),
    None,
    [(S, 0, 0), (S, 0, S), (S, S, S), (S, S, 0)],
)
face_xn = make_plane_face(  # -X face (x=0)
    (0, 0, 0), (-1, 0, 0), (0, 0, -1),
    None,
    [(0, 0, 0), (0, S, 0), (0, S, S), (0, 0, S)],
)
face_yp = make_plane_face(  # +Y face (y=10)
    (0, S, 0), (0, 1, 0), (1, 0, 0),
    None,
    [(0, S, 0), (S, S, 0), (S, S, S), (0, S, S)],
)
face_yn = make_plane_face(  # -Y face (y=0)
    (0, 0, 0), (0, -1, 0), (0, 0, 1),
    None,
    [(0, 0, 0), (0, 0, S), (S, 0, S), (S, 0, 0)],
)
face_zp = make_plane_face(  # +Z face (z=10)
    (0, 0, S), (0, 0, 1), (1, 0, 0),
    None,
    [(0, 0, S), (0, S, S), (S, S, S), (S, 0, S)],
)
face_zn = make_plane_face(  # -Z face (z=0)
    (0, 0, 0), (0, 0, -1), (-1, 0, 0),
    None,
    [(0, 0, 0), (S, 0, 0), (S, S, 0), (0, S, 0)],
)

all_faces = [face_xp, face_xn, face_yp, face_yn, face_zp, face_zn]
face_refs = ",".join(f"#{fa.eid}" for fa in all_faces)
shell = f._emit_raw(f"CLOSED_SHELL('pmi140_shell',({face_refs}))")
msb   = f._emit_raw(f"MANIFOLD_SOLID_BREP('pmi140_cube',#{shell.eid})")
f.add_product_chain(msb, mode="brep_shape")

# ── PROPERTY_DEFINITION metadata chain ───────────────────────────────────────
# #9055 = PRODUCT_DEFINITION_SHAPE (emitted by add_product_chain above)
# The chain: PROPERTY_DEFINITION → PROPERTY_DEFINITION_REPRESENTATION →
#            REPRESENTATION → DESCRIPTIVE_REPRESENTATION_ITEM

# DESCRIPTIVE_REPRESENTATION_ITEM carries the material string
# Byte assertion: contains(b'Aluminum 6061')
dri = f._emit_raw(
    "DESCRIPTIVE_REPRESENTATION_ITEM('material','Aluminum 6061')"
)

# REPRESENTATION wrapping the DRI — needs the geometric context ref (#9060)
prop_rep = f._emit_raw(
    f"REPRESENTATION('material_properties',(#{dri.eid}),#9060)"
)

# PROPERTY_DEFINITION linking the metadata to the product shape
# Byte assertion: contains(b'PROPERTY_DEFINITION')
prop_def = f._emit_raw(
    f"PROPERTY_DEFINITION('material','material name attribute',#9055)"
)

# PROPERTY_DEFINITION_REPRESENTATION wiring the definition to its rep
# Byte assertion: contains(b'PROPERTY_DEFINITION_REPRESENTATION')
f._emit_raw(
    f"PROPERTY_DEFINITION_REPRESENTATION(#{prop_def.eid},#{prop_rep.eid})"
)
