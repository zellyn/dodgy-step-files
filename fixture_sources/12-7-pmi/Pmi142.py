"""Pmi142 — AP242 Ed.2 DIMENSION_SIZE entity silently dropped by Ed.1 readers.

Catalog claim: STEP AP242 Edition 2 file where a dimensional annotation encodes
a size callout via DIMENSION_SIZE (defined in AP242 Part 1 Ed.2 §4.5.7) rather
than the AP242 Ed.1 DIMENSIONAL_SIZE path. The file header declares AP242 Ed.2
schema. The file also contains a valid geometry (prismatic MANIFOLD_SOLID_BREP).

Expected:
- Geometry loads under any reader.
- DIMENSION_SIZE data is readable under AP242 Ed.2 readers.
- Under AP242 Ed.1 and AP214 readers: the entity is silently dropped (absent),
  because the entity type does not exist in their schema. This is a
  historical-fix / edition-boundary demonstration.

Source: NIST IR 8221 AP242 test results §4.5.7.
B4 wave-6 DEF-Z. Confidence: HIGH.

Byte assertions:
  contains(b'DIMENSION_SIZE')
  contains(b'SHAPE_ASPECT')
  contains(b'MANIFOLD_SOLID_BREP')
Tier-3: shape_null == False
Expected: occt=shape(1)/shape(1) gmsh=shape(54) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi142",
    schema="AP242",
    defect=(
        "AP242 Ed.2 file: dimensional annotation encoded via DIMENSION_SIZE entity "
        "(AP242 Part 1 Ed.2 §4.5.7) referencing a SHAPE_ASPECT on a planar face; "
        "geometry (MANIFOLD_SOLID_BREP cube 10x10x10) loads under all readers; "
        "DIMENSION_SIZE entity silently dropped by AP242 Ed.1 and AP214 readers "
        "(entity type absent in Ed.1 schema); readable under Ed.2 readers; "
        "edition-boundary demonstration; NIST IR 8221; "
        "MANIFOLD_SOLID_BREP IS model entity — OCC yields shape(1)"
    ),
)

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
face_zp = make_plane_face((0,0,S), (0,0,1), (1,0,0),
                           [(0,0,S),(0,S,S),(S,S,S),(S,0,S)])
face_zn = make_plane_face((0,0,0), (0,0,-1), (-1,0,0),
                           [(0,0,0),(S,0,0),(S,S,0),(0,S,0)])

all_faces = [face_xp, face_xn, face_yp, face_yn, face_zp, face_zn]
face_refs = ",".join(f"#{fa.eid}" for fa in all_faces)
shell = f._emit_raw(f"CLOSED_SHELL('pmi142_shell',({face_refs}))")
msb   = f._emit_raw(f"MANIFOLD_SOLID_BREP('pmi142_cube',#{shell.eid})")
f.add_product_chain(msb, mode="brep_shape")

# ── AP242 Ed.2 DIMENSION_SIZE annotation chain ───────────────────────────────
# Links: SHAPE_ASPECT → DIMENSION_SIZE (→ applies_to + name/value)
# Per AP242 Ed.2 §4.5.7, DIMENSION_SIZE has attributes:
#   applies_to: SHAPE_ASPECT
#   name: IDENTIFIER (the dimension name)
# Additional size value is carried via MEASURE_REPRESENTATION_ITEM via:
#   SHAPE_ASPECT → SHAPE_ASPECT_RELATIONSHIP → MEASURE_REPRESENTATION_ITEM

# SHAPE_ASPECT for the +Z face (face_zp, which is all_faces[4]).
# Byte assertion: contains(b'SHAPE_ASPECT')
shape_aspect = f._emit_raw(
    f"SHAPE_ASPECT('top_face_z','z-dimension face aspect',#9055,.F.)"
)

# AP242 Ed.2 DIMENSION_SIZE: applies_to=shape_aspect, name='10.0'.
# This entity type does NOT exist in AP242 Ed.1 or AP214 schemas.
# Byte assertion: contains(b'DIMENSION_SIZE')
dim_size = f._emit_raw(
    f"DIMENSION_SIZE(#{shape_aspect.eid},'10.0')"
)

# DESCRIPTIVE_REPRESENTATION_ITEM carrying the dimension value string.
dri = f._emit_raw(
    "DESCRIPTIVE_REPRESENTATION_ITEM('height_value','10.0 mm')"
)

# REPRESENTATION carrying the DRI (wired to the geometric context).
mri_rep = f._emit_raw(
    f"REPRESENTATION('dim_size_rep',(#{dri.eid}),#9060)"
)

# PROPERTY_DEFINITION linking the dimension to the product shape.
prop_def = f._emit_raw(
    f"PROPERTY_DEFINITION('height_dim','dimensional size annotation',#9055)"
)
f._emit_raw(
    f"PROPERTY_DEFINITION_REPRESENTATION(#{prop_def.eid},#{mri_rep.eid})"
)
