"""Pmi164 — Single shared COORDINATES_LIST for a whole TESSELLATED_SHELL, 1-based integer indices [VALID-BUT-HARD].

Catalog claim: AP242 tessellated geometry packs all vertices of a shell into a
single shared `coordinates_list` (the AP242 point holder — `cartesian_point_list_3d`
is the AP203/214 name) and lets every `triangulated_face` index that ONE array
with 1-based integer index lists, rather than owning a per-face list or naming
individual `cartesian_point` entities. A kernel built around per-point entities,
or one that assumes a per-face list, or one that treats the indices as 0-based,
mis-indexes or drops faces. Distinct from M004 (per-face lists → watertightness
lost); here a single shared 1-based-indexed list is the correct packed form.

Pattern-mined from the NIST MBE-PMI FTC-08 tessellated AP242 test file and the
MBx-IF Tessellated-3D-Geometry Recommended Practice (public-domain / describe-only
— pattern only, no bytes copied).

Byte assertions:
  count_entity_def(b'COORDINATES_LIST') == 1
  count_entity_def(b'TRIANGULATED_FACE') == 6
  contains(b'TESSELLATED_SHELL')

Tier-3: shape_null == False, n_vertices_total == 0 (mirrors M004 tessellated load)
Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a  (provisional)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pmi164",
    schema="AP242",
    defect=(
        "single shared COORDINATES_LIST (8 cube corners) indexed by six "
        "TRIANGULATED_FACEs using 1-based integer index lists, wrapped in one "
        "TESSELLATED_SHELL; packed-array + 1-based indexing form; "
        "per-point / per-face-list / 0-based readers mis-index or drop faces; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty vertices"
    ),
)

# ── One shared COORDINATES_LIST: 8 cube corners (1-based index space) ─────────
#   1=(0,0,0) 2=(1,0,0) 3=(1,1,0) 4=(0,1,0) 5=(0,0,1) 6=(1,0,1) 7=(1,1,1) 8=(0,1,1)
coords = f._emit_raw(
    "COORDINATES_LIST('shared_cube_coords',8,"
    "((0.,0.,0.),(1.,0.,0.),(1.,1.,0.),(0.,1.,0.),"
    "(0.,0.,1.),(1.,0.,1.),(1.,1.,1.),(0.,1.,1.)))"
)

# ── Six faces, each indexing the SAME list with 1-based triangle indices ──────
#   TRIANGULATED_FACE(name, coordinates, pnindex, normals, triangles)
def tri_face(name, tris):
    tri_lit = ",".join(f"({a},{b},{c})" for (a, b, c) in tris)
    return f._emit_raw(
        f"TRIANGULATED_FACE('{name}',#{coords.eid},$,$,({tri_lit}))"
    )

faces = [
    tri_face("bottom", [(1, 2, 3), (1, 3, 4)]),   # z=0
    tri_face("top",    [(5, 6, 7), (5, 7, 8)]),   # z=1
    tri_face("front",  [(1, 2, 6), (1, 6, 5)]),   # y=0
    tri_face("back",   [(4, 3, 7), (4, 7, 8)]),   # y=1
    tri_face("left",   [(1, 4, 8), (1, 8, 5)]),   # x=0
    tri_face("right",  [(2, 3, 7), (2, 7, 6)]),   # x=1
]

# ── One TESSELLATED_SHELL over all six faces (no topological link) ────────────
tess_shell = f._emit_raw(
    "TESSELLATED_SHELL('shared_list_shell',("
    + ",".join(f"#{fc.eid}" for fc in faces)
    + "),$)"
)

# ── GEOMETRIC_CURVE_SET IS the model entity — OCC yields empty (as in M004) ───
gcs = f._emit_raw(
    f"GEOMETRIC_CURVE_SET('shared-coordinates-list-tessellation',(#{tess_shell.eid}))"
)
f.add_product_chain(gcs)
