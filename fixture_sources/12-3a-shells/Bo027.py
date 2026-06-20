"""Bo027 — Per-vertex normals supplied for a triangulated face are inconsistent
across smooth edges.

Catalog claim: A triangulated face (AP242 ed.2 TRIANGULATED_FACE) declares
per-node normals, and at a smooth-edge node shared with the neighbour face, the
two faces' per-node normals point in noticeably different directions.

Mechanism IS the COMPLEX_TRIANGULATED_FACE shell topology: two adjacent
COMPLEX_TRIANGULATED_FACE entities sharing a node (#N at origin) form an
OPEN_SHELL inside a SHELL_BASED_SURFACE_MODEL. FaceA reports normal (0,0,1)
at #N; FaceB reports (0.7,0,0.7) at #N — the normal mismatch IS wired into
the per-vertex normal data of the two face entities, which are wired into the
OPEN_SHELL shell topology.

Byte assertions:
  - contains(b'COMPLEX_TRIANGULATED_FACE')
  - contains(b'COORDINATES_LIST')
  - declared_schema == b'AP242_MANAGED_MODEL_BASED_3D_ENGINEERING_MIM_LF { 1 0 10303 442 1 1 4 }'

Tier-3 assertion: shape_null == True
live oracle: occt=shape(1)/shape(1)/empty
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Bo027",
    defect=(
        "Two COMPLEX_TRIANGULATED_FACEs sharing node at origin: faceA normal (0,0,1), "
        "faceB normal (0.7,0,0.7) at same node — inconsistent per-vertex normals "
        "IS wired into shell/face topology; OCCT silently drops (empty result); "
        "catalog asks for heal or reject"
    ),
)

# ── Patch FILE_SCHEMA to AP242 MIM_LF (required by declared_schema byte assertion) ──
def _ap242_header(self):
    return (
        "HEADER;\n"
        f"FILE_DESCRIPTION(('{self.catalog_id}'),'2;1');\n"
        f"FILE_NAME('{self.catalog_id}.stp','{self.timestamp}',(''),(''),"
        f"'cad-research-suite','','');\n"
        "FILE_SCHEMA(('AP242_MANAGED_MODEL_BASED_3D_ENGINEERING_MIM_LF "
        "{ 1 0 10303 442 1 1 4 }'));\n"
        "ENDSEC;"
    )

import types
f._render_header = types.MethodType(_ap242_header, f)

# ── CATALOG MECHANISM: COMPLEX_TRIANGULATED_FACE with inconsistent normals ────
#
# FaceA: one triangle in the XY plane (z=0)
#   Nodes: N0=(0,0,0), N1=(1,0,0), N2=(0,1,0)
#   Per-node normals: all (0,0,1)
#   Shared node with FaceB: N0 at (0,0,0), normal reported as (0,0,1)
#
# FaceB: one triangle tilted 45° (in XZ plane)
#   Nodes: N0=(0,0,0) [shared], N3=(1,0,0), N4=(0,0,1)
#   Per-node normals: N0 normal reported as (0.7,0,0.7) — differs from FaceA!
#
# The mismatch at N0 IS the defect — inconsistent normals across the smooth edge.

# ── COORDINATES_LIST for faceA (byte assertion target) ────────────────────────
coords_a = f._emit_raw(
    "COORDINATES_LIST('faceA_coords',3,"
    "((0.,0.,0.),(1.,0.,0.),(0.,1.,0.)))"
)
# FaceA normals: (0,0,1) for all three nodes
normals_a = f._emit_raw(
    "COORDINATES_LIST('faceA_normals',3,"
    "((0.,0.,1.),(0.,0.,1.),(0.,0.,1.)))"
)

# COMPLEX_TRIANGULATED_FACE(name, coords, triangles, normals_flag, normals)
# triangles: 0-based index triplets for the one triangle (0,1,2)
face_a = f._emit_raw(
    f"COMPLEX_TRIANGULATED_FACE('faceA',#{coords_a.eid},"
    f"((0,1,2)),.T.,#{normals_a.eid})"
)

# ── COORDINATES_LIST for faceB ────────────────────────────────────────────────
coords_b = f._emit_raw(
    "COORDINATES_LIST('faceB_coords',3,"
    "((0.,0.,0.),(1.,0.,0.),(0.,0.,1.)))"
)
# FaceB normals: shared node normal (0.7,0,0.7) — inconsistent with faceA's (0,0,1)
normals_b = f._emit_raw(
    "COORDINATES_LIST('faceB_normals',3,"
    "((0.7071067811865476,0.,0.7071067811865476),"
    "(0.7071067811865476,0.,0.7071067811865476),"
    "(0.7071067811865476,0.,0.7071067811865476)))"
)

# COMPLEX_TRIANGULATED_FACE for faceB — normal at shared node differs from faceA
face_b = f._emit_raw(
    f"COMPLEX_TRIANGULATED_FACE('faceB',#{coords_b.eid},"
    f"((0,1,2)),.T.,#{normals_b.eid})"
)

# ── Wire both faces into an OPEN_SHELL → SHELL_BASED_SURFACE_MODEL ────────────
# Byte: COMPLEX_TRIANGULATED_FACE (already emitted above)
# The inconsistent-normal defect IS wired: both faces share node at (0,0,0)
# inside the same shell structure.
shell = f._emit_raw(
    f"OPEN_SHELL('bo027_shell',(#{face_a.eid},#{face_b.eid}))"
)
sbsm = f._emit_raw(
    f"SHELL_BASED_SURFACE_MODEL('bo027',(#{shell.eid}))"
)

f.add_product_chain(sbsm)
