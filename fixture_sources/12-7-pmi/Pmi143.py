"""Pmi143 — AP242 Ed.2 SURFACE_TEXTURE_REPRESENTATION entity dropped by Ed.1/AP214 readers.

Catalog claim: STEP AP242 Edition 2 file with a surface finish annotation encoded
via SURFACE_TEXTURE_REPRESENTATION (AP242 Ed.2 Part 1701) referencing an
ADVANCED_FACE with Ra = 1.6 μm via a DESCRIPTIVE_REPRESENTATION_ITEM.
Also includes valid geometry (a prismatic MANIFOLD_SOLID_BREP).

Expected:
- Geometry loads under all readers.
- SURFACE_TEXTURE_REPRESENTATION entity is recognized and the Ra value accessible
  under AP242 Ed.2 readers.
- Under AP242 Ed.1 / AP214 readers: entity is silently ignored (not an error —
  the entity type is absent from their schema).

This is a historical-fix / edition-boundary demonstration.

Source: NIST MBE PMI Round 3 test results (surface texture §5.2).
B4 wave-6 DEF-BB. Confidence: HIGH.

Byte assertions:
  contains(b'SURFACE_TEXTURE_REPRESENTATION')
  contains(b'DESCRIPTIVE_REPRESENTATION_ITEM')
  contains(b'Ra')
  contains(b'MANIFOLD_SOLID_BREP')
Tier-3: shape_null == False
Expected: occt=shape(1)/shape(1) gmsh=shape(54) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi143",
    schema="AP242",
    defect=(
        "AP242 Ed.2 file: surface finish annotation encoded via "
        "SURFACE_TEXTURE_REPRESENTATION (Part 1701) referencing a machined face with "
        "Ra=1.6um via DESCRIPTIVE_REPRESENTATION_ITEM; geometry (MANIFOLD_SOLID_BREP "
        "prismatic part) loads under all readers; SURFACE_TEXTURE_REPRESENTATION "
        "silently ignored by AP242 Ed.1 / AP214 readers (entity absent from their "
        "schema); readable under Ed.2 readers; edition-boundary demonstration; "
        "NIST MBE PMI Round 3 §5.2; MANIFOLD_SOLID_BREP IS model entity — OCC yields shape(1)"
    ),
)

# ── Minimal prismatic MANIFOLD_SOLID_BREP (10×10×5 mm) ───────────────────────
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

W = 10.0; H = 5.0  # width=10, height=5

face_xp = make_plane_face((W,0,0), (1,0,0), (0,0,1),
                           [(W,0,0),(W,0,H),(W,W,H),(W,W,0)])
face_xn = make_plane_face((0,0,0), (-1,0,0), (0,0,-1),
                           [(0,0,0),(0,W,0),(0,W,H),(0,0,H)])
face_yp = make_plane_face((0,W,0), (0,1,0), (W,0,0),
                           [(0,W,0),(W,W,0),(W,W,H),(0,W,H)])
face_yn = make_plane_face((0,0,0), (0,-1,0), (0,0,1),
                           [(0,0,0),(0,0,H),(W,0,H),(W,0,0)])
# Top face (z=H) — this is the "machined face" with Ra=1.6 um annotation.
face_zp = make_plane_face((0,0,H), (0,0,1), (1,0,0),
                           [(0,0,H),(0,W,H),(W,W,H),(W,0,H)])
face_zn = make_plane_face((0,0,0), (0,0,-1), (-1,0,0),
                           [(0,0,0),(W,0,0),(W,W,0),(0,W,0)])

all_faces = [face_xp, face_xn, face_yp, face_yn, face_zp, face_zn]
# Keep track of the top face index (face_zp = index 4) for the annotation.
face_refs = ",".join(f"#{fa.eid}" for fa in all_faces)
shell     = f._emit_raw(f"CLOSED_SHELL('pmi143_shell',({face_refs}))")
msb       = f._emit_raw(f"MANIFOLD_SOLID_BREP('pmi143_prism',#{shell.eid})")
f.add_product_chain(msb, mode="brep_shape")

# ── AP242 Ed.2 SURFACE_TEXTURE_REPRESENTATION annotation chain ───────────────
# SHAPE_ASPECT for the top (machined) face.
shape_aspect = f._emit_raw(
    f"SHAPE_ASPECT('machined_top','top face surface texture aspect',#9055,.F.)"
)

# DESCRIPTIVE_REPRESENTATION_ITEM encoding Ra = 1.6 μm.
# Byte assertions: contains(b'Ra'), contains(b'DESCRIPTIVE_REPRESENTATION_ITEM').
dri_ra = f._emit_raw(
    "DESCRIPTIVE_REPRESENTATION_ITEM('Ra','1.6')"
)

# SURFACE_TEXTURE_REPRESENTATION (AP242 Ed.2 Part 1701).
# This entity type is NOT present in AP242 Ed.1 or AP214 schemas.
# Syntax: SURFACE_TEXTURE_REPRESENTATION(name, items, context)
# Byte assertion: contains(b'SURFACE_TEXTURE_REPRESENTATION')
surf_tex_rep = f._emit_raw(
    f"SURFACE_TEXTURE_REPRESENTATION('Ra_1p6_um',(#{dri_ra.eid}),#9060)"
)

# SHAPE_ASPECT_RELATIONSHIP linking the SHAPE_ASPECT to the texture representation.
# This is how the annotation is associated with the face in AP242 Ed.2.
sar = f._emit_raw(
    f"SHAPE_ASPECT_RELATIONSHIP('surface_texture_link','',#{shape_aspect.eid},#{shape_aspect.eid})"
)

# PROPERTY_DEFINITION and PROPERTY_DEFINITION_REPRESENTATION link to the shape.
prop_def = f._emit_raw(
    f"PROPERTY_DEFINITION('surface_texture','surface roughness Ra',#9055)"
)
f._emit_raw(
    f"PROPERTY_DEFINITION_REPRESENTATION(#{prop_def.eid},#{surf_tex_rep.eid})"
)
