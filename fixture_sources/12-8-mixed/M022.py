"""M022 — STL-derived tessellated_solid / triangulated_face ignored by importers.

Catalog claim: BRL-CAD's step-g and many other readers ignore tessellated_solid,
triangulated_face, complex_triangulated_surface_set; only B-rep paths are consumed.
Files containing only mesh entities appear empty.

Reproducer recipe: AP242 file using TRIANGULATED_FACE and
COMPLEX_TRIANGULATED_SURFACE_SET with no MANIFOLD_SOLID_BREP entity.

Byte assertions:
  contains(b'COMPLEX_TRIANGULATED_SURFACE_SET')
  contains(b'stl_origin_cube')
  count_entity_def(b'MANIFOLD_SOLID_BREP') == 0

Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="M022",
    schema="AP242",
    defect=(
        "GEOMETRIC_CURVE_SET containing COMPLEX_TRIANGULATED_SURFACE_SET 'stl_origin_cube' "
        "with no MANIFOLD_SOLID_BREP in the file; "
        "input: AP242 STEP file produced from STL conversion using only mesh entities "
        "(TRIANGULATED_FACE, COMPLEX_TRIANGULATED_SURFACE_SET); "
        "BRL-CAD step-g and B-rep-only readers silently drop all mesh entities — "
        "file appears empty because no MANIFOLD_SOLID_BREP path exists; "
        "kernel must import as mesh object or convert to lightweight surface; "
        "must never silently drop; "
        "OCC silently produces empty results (BRep path consumes nothing); "
        "GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty; "
        "synonyms: mesh-only AP242 appears empty, STL-derived tessellation ignored, "
        "triangulated_face skipped by importer, B-rep-only reader drops mesh entities, "
        "BRL-CAD step-g ignores tessellated solid and triangulated face entities"
    ),
)

# ── Mesh-only cube: 6 faces x 2 triangles each = 12 triangles ────────────────
# A unit cube at origin: 8 vertices, 6 TRIANGULATED_FACEs, wrapped in
# COMPLEX_TRIANGULATED_SURFACE_SET.
# Byte assertion: contains(b'stl_origin_cube') — name on COMPLEX_TRIANGULATED_SURFACE_SET
# Byte assertion: count_entity_def(b'MANIFOLD_SOLID_BREP') == 0 — no BRep present

cube_coords = f._emit_raw(
    "COORDINATES_LIST('cube_verts',3,"
    "((0.,0.,0.),(1.,0.,0.),(1.,1.,0.),(0.,1.,0.),"
    "(0.,0.,1.),(1.,0.,1.),(1.,1.,1.),(0.,1.,1.)))"
)

# Bottom face (z=0): verts 0,1,2,3
face_bottom = f._emit_raw(
    f"TRIANGULATED_FACE('cube_bottom',#{cube_coords.eid},$,"
    f"((.FALSE.,.FALSE.,.FALSE.,.FALSE.)),((0,1,2),(0,2,3)))"
)

# Top face (z=1): verts 4,5,6,7
face_top = f._emit_raw(
    f"TRIANGULATED_FACE('cube_top',#{cube_coords.eid},$,"
    f"((.FALSE.,.FALSE.,.FALSE.,.FALSE.)),((4,6,5),(4,7,6)))"
)

# Front face (y=0): verts 0,1,5,4
face_front = f._emit_raw(
    f"TRIANGULATED_FACE('cube_front',#{cube_coords.eid},$,"
    f"((.FALSE.,.FALSE.,.FALSE.,.FALSE.)),((0,1,5),(0,5,4)))"
)

# Back face (y=1): verts 3,2,6,7
face_back = f._emit_raw(
    f"TRIANGULATED_FACE('cube_back',#{cube_coords.eid},$,"
    f"((.FALSE.,.FALSE.,.FALSE.,.FALSE.)),((3,6,2),(3,7,6)))"
)

# Left face (x=0): verts 0,3,7,4
face_left = f._emit_raw(
    f"TRIANGULATED_FACE('cube_left',#{cube_coords.eid},$,"
    f"((.FALSE.,.FALSE.,.FALSE.,.FALSE.)),((0,3,7),(0,7,4)))"
)

# Right face (x=1): verts 1,2,6,5
face_right = f._emit_raw(
    f"TRIANGULATED_FACE('cube_right',#{cube_coords.eid},$,"
    f"((.FALSE.,.FALSE.,.FALSE.,.FALSE.)),((1,6,2),(1,5,6)))"
)

# COMPLEX_TRIANGULATED_SURFACE_SET: wraps all 6 faces — byte assertion target
# Byte assertion: contains(b'COMPLEX_TRIANGULATED_SURFACE_SET')
ctss = f._emit_raw(
    f"COMPLEX_TRIANGULATED_SURFACE_SET('stl_origin_cube',"
    f"(#{face_bottom.eid},#{face_top.eid},#{face_front.eid},"
    f"#{face_back.eid},#{face_left.eid},#{face_right.eid}))"
)

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty ───────────────
# No MANIFOLD_SOLID_BREP is present in this file — B-rep-only readers drop everything.
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('stl-derived-mesh-only-no-brep',(#{ctss.eid}))"
)
f.add_product_chain(gcs)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M022.stp")
