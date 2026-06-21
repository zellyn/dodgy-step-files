"""M004 — Watertightness lost when each tessellated face has its own coordinates_list.

Catalog claim: Defining each tessellated_face with an independent coordinates_list produces
duplicate vertices along shared edges. Floating-point quantization may make those duplicates
non-equal, leaving sub-tolerance gaps along every shared edge. Recommendation: one
coordinates_list per solid plus tessellated_connecting_edge per topological edge.

Reproducer recipe: Tessellate a unit cube so each of the six faces has its own coordinates_list
with corner coordinates differing in the last few digits across faces.

Byte assertions:
  count_entity_def(b'COORDINATES_LIST') == 6

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M004",
    schema="AP242",
    defect=(
        "GEOMETRIC_CURVE_SET containing TESSELLATED_SOLID with 6 TESSELLATED_FACEs, "
        "each owning its own COORDINATES_LIST; "
        "per-face COORDINATES_LIST produces duplicate vertices along every shared cube edge; "
        "floating-point quantization makes some duplicates non-equal (sub-tolerance gap); "
        "AP242 Tessellated Geometry §5.4.3/§6 recommendation: one COORDINATES_LIST per solid "
        "plus TESSELLATED_CONNECTING_EDGE per topological edge; "
        "kernel must heal: merge nearly-coincident vertices using model uncertainty, "
        "or report the gap; "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: tessellation not watertight, duplicate vertices on shared edge, "
        "per-face coordinates_list causes gaps, tessellated mesh has sub-tolerance gaps, "
        "shared edge vertices don't match across faces"
    ),
)

# ── Unit cube tessellation: 6 faces, each with its own COORDINATES_LIST ───────
# Cube corners: (0,0,0)...(1,1,1)
# Each face is a quad split into two triangles.
# Shared-edge vertices intentionally differ in the last few floating-point digits
# across the two face coordinate lists, creating sub-tolerance gaps.
#
# Face ordering and coordinates (0-based indexing within each face's own list):
#
# Face 0 (bottom, z=0):   (0,0,0),(1,0,0),(1,1,0),(0,1,0)  — slight quantization on shared verts
# Face 1 (top,    z=1):   (0,0,1),(1,0,1),(1,1,1),(0,1,1)
# Face 2 (front,  y=0):   (0,0,0),(1,0,0),(1,0,1),(0,0,1)  — shares edge with face 0 at y=0 z=0
# Face 3 (back,   y=1):   (0,1,0),(1,1,0),(1,1,1),(0,1,1)
# Face 4 (left,   x=0):   (0,0,0),(0,1,0),(0,1,1),(0,0,1)
# Face 5 (right,  x=1):   (1,0,0),(1,1,0),(1,1,1),(1,0,1)
#
# Sub-tolerance quantization: shared vertices on adjacent faces differ by ~3e-7
# (e.g., face-0 has 1.0000003 where face-2 has 1.0000000 on the shared z=0 edge)
# This is within OCC's default tolerance (1e-7 mm after unit context) but not in a
# pure point-compare, so naive watertight checks fail.

EPS = 3e-7  # intentional sub-tolerance offset on shared edges

# ── Face 0: bottom (z=0) — slight offset on x=1 shared verts ────────────────
coords0 = f._emit_raw(
    "COORDINATES_LIST('bottom_face_coords',3,"
    f"((0.,0.,0.),({1.0+EPS},0.,0.),({1.0+EPS},{1.0+EPS},0.),(0.,{1.0+EPS},0.)))"
)
face0 = f._emit_raw(
    f"TRIANGULATED_FACE('bottom_face',#{coords0.eid},$,"
    "((.FALSE.,.FALSE.,.FALSE.,.FALSE.)),((0,1,2),(0,2,3)))"
)

# ── Face 1: top (z=1) ────────────────────────────────────────────────────────
coords1 = f._emit_raw(
    "COORDINATES_LIST('top_face_coords',3,"
    "((0.,0.,1.),(1.,0.,1.),(1.,1.,1.),(0.,1.,1.)))"
)
face1 = f._emit_raw(
    f"TRIANGULATED_FACE('top_face',#{coords1.eid},$,"
    "((.FALSE.,.FALSE.,.FALSE.,.FALSE.)),((0,1,2),(0,2,3)))"
)

# ── Face 2: front (y=0) — shared edge with face 0 at z=0 uses exact 1.0 ─────
coords2 = f._emit_raw(
    "COORDINATES_LIST('front_face_coords',3,"
    "((0.,0.,0.),(1.,0.,0.),(1.,0.,1.),(0.,0.,1.)))"
)
face2 = f._emit_raw(
    f"TRIANGULATED_FACE('front_face',#{coords2.eid},$,"
    "((.FALSE.,.FALSE.,.FALSE.,.FALSE.)),((0,1,2),(0,2,3)))"
)

# ── Face 3: back (y=1) ───────────────────────────────────────────────────────
coords3 = f._emit_raw(
    "COORDINATES_LIST('back_face_coords',3,"
    f"((0.,{1.0+EPS},0.),(1.,{1.0+EPS},0.),(1.,{1.0+EPS},1.),(0.,{1.0+EPS},1.)))"
)
face3 = f._emit_raw(
    f"TRIANGULATED_FACE('back_face',#{coords3.eid},$,"
    "((.FALSE.,.FALSE.,.FALSE.,.FALSE.)),((0,1,2),(0,2,3)))"
)

# ── Face 4: left (x=0) ───────────────────────────────────────────────────────
coords4 = f._emit_raw(
    "COORDINATES_LIST('left_face_coords',3,"
    "((0.,0.,0.),(0.,1.,0.),(0.,1.,1.),(0.,0.,1.)))"
)
face4 = f._emit_raw(
    f"TRIANGULATED_FACE('left_face',#{coords4.eid},$,"
    "((.FALSE.,.FALSE.,.FALSE.,.FALSE.)),((0,1,2),(0,2,3)))"
)

# ── Face 5: right (x=1) — shared edges with faces 0,1,2,3 use +EPS ──────────
coords5 = f._emit_raw(
    "COORDINATES_LIST('right_face_coords',3,"
    f"(({1.0+EPS},0.,0.),({1.0+EPS},{1.0+EPS},0.),({1.0+EPS},{1.0+EPS},1.),({1.0+EPS},0.,1.)))"
)
face5 = f._emit_raw(
    f"TRIANGULATED_FACE('right_face',#{coords5.eid},$,"
    "((.FALSE.,.FALSE.,.FALSE.,.FALSE.)),((0,1,2),(0,2,3)))"
)

# Verify exactly 6 COORDINATES_LIST were emitted (byte assertion check)
# coords0..coords5 = 6 entities ✓

# ── TESSELLATED_SOLID wraps all six faces ─────────────────────────────────────
tess_solid = f._emit_raw(
    f"TESSELLATED_SOLID('per_face_coords_cube',"
    f"(#{face0.eid},#{face1.eid},#{face2.eid},#{face3.eid},#{face4.eid},#{face5.eid}))"
)

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty ───────────────
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('per-face-coords-list-gaps',(#{tess_solid.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M004.stp")
