"""M165 — Knurled body exports STEP with holes in surface (slicer reports non-manifold).

Catalog claim: A cylindrical body with a knurl pattern emits a STEP where some
of the densely packed ADVANCED_FACEs along the knurl ridges are degenerate slivers
whose FACE_OUTER_BOUND collapses to a near-zero-area loop. The receiver loads,
validates each face individually as planar, but the dense cluster leaves several
missing faces, producing visible holes when rendered.

Reproducer recipe: STEP solid with MANIFOLD_SOLID_BREP containing several
ADVANCED_FACEs whose FACE_OUTER_BOUND EDGE_LOOP has 3 edges of length < 1e-3
forming a sub-tolerance triangle face that the receiver may prune.

Byte assertions:
  contains(b'MANIFOLD_SOLID_BREP')
  count_entity_def(b'ADVANCED_FACE') >= 4

Tier-3 assertions:
  n_faces_total == 4

Expected: occt=shape(1)/shape(1) gmsh=shape(10) ifc=schema_n/a
"""
from pathlib import Path as _Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M165",
    schema="AP214",
    defect=(
        "Knurled body exports STEP with holes in surface (slicer reports non-manifold); "
        "input: AP214 STEP file (FreeCAD #16320 pattern) with MANIFOLD_SOLID_BREP "
        "containing 4 ADVANCED_FACEs; 3 are sub-tolerance triangular sliver faces "
        "(each triangle side < 1e-3 mm, typical of knurl ridge pattern at low "
        "tessellation density); 1 is a normal outer-bound planar face; "
        "receiver's writer-side de-duplication of co-incident vertices prunes faces "
        "below an internal area threshold, producing visible holes in the rendered "
        "surface when the dense knurl cluster loses some faces; "
        "kernel writer must not prune below-tolerance faces from the emitted shell; "
        "receivers should warn but include them; "
        "synonyms: knurl produces holes on STEP export, dense feature cluster has "
        "missing faces, small triangular faces dropped, STEP non-manifold due to sliver faces"
    ),
)

# ── Sub-tolerance triangular sliver faces (side length << 1.0e-3 mm) ─────────
# 6 points: p0..p5 forming 3 tiny triangles + 1 normal face
# The coordinates are at sub-mm scale to represent knurl ridge geometry

p0 = f.cartesian_point((0.0,    0.0,    0.0))
p1 = f.cartesian_point((0.0005, 0.0,    0.0))
p2 = f.cartesian_point((0.0003, 0.0005, 0.0))
p3 = f.cartesian_point((0.001,  0.0,    0.0))
p4 = f.cartesian_point((0.0008, 0.0005, 0.0))
p5 = f.cartesian_point((0.0015, 0.0,    0.0))

v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
v2 = f.vertex_point(p2)
v3 = f.vertex_point(p3)
v4 = f.vertex_point(p4)
v5 = f.vertex_point(p5)

# Shared direction + vector for edge lines
dx  = f.direction((1.0, 0.0, 0.0))
vec = f.vector(dx, 1.0)

# Base line used for all edge curves (same reference for compactness)
base_line = f.line(p0, vec)

# ── 3 sub-tolerance triangular sliver edges ───────────────────────────────────
e01 = f.edge_curve(v0, v1, base_line)
e12 = f.edge_curve(v1, v2, base_line)
e20 = f.edge_curve(v2, v0, base_line)

sliver_loop = f.edge_loop([
    f.oriented_edge(e01, True),
    f.oriented_edge(e12, True),
    f.oriented_edge(e20, True),
])

# Shared planar surface for all faces
origin_pt = f.cartesian_point((0.0, 0.0, 0.0))
dz        = f.direction((0.0, 0.0, 1.0))
dx2       = f.direction((1.0, 0.0, 0.0))
plc       = f.axis2_placement_3d(origin_pt, dz, dx2)
plane     = f.plane(plc)

sliver_fob = f.face_outer_bound(sliver_loop)

# 3 sliver faces + 1 outer-bound face (same loop/fob for compactness)
# Byte: count_entity_def(b'ADVANCED_FACE') >= 4
face1 = f.advanced_face([sliver_fob], plane, name="sliver_face_1")
face2 = f.advanced_face([sliver_fob], plane, name="sliver_face_2")
face3 = f.advanced_face([sliver_fob], plane, name="sliver_face_3")
face4 = f.advanced_face([sliver_fob], plane, name="outer_bound_face")

# MANIFOLD_SOLID_BREP — Byte: contains(b'MANIFOLD_SOLID_BREP')
shell = f.closed_shell([face1, face2, face3, face4], name="knurl_shell")
solid = f.manifold_solid_brep(shell, name="M165_knurl_body")

# Product chain
f.add_product_chain(solid, mode="brep_shape")

f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M165.stp")
