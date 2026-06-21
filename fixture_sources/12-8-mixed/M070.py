"""M070 — STL writer does not respect existing triangulation.

Catalog claim: An STL writer is invoked on a shape that already has an
attached triangulation. The writer ignores the existing mesh and
re-tessellates from B-rep using default deflection, losing the user's
carefully-tuned mesh.

Reproducer recipe: Shape with an attached TESSELLATED_SHAPE_REPRESENTATION
(pre-computed triangulation from a prior BRepMesh_IncrementalMesh call with
custom deflection); write to STL → writer discards it and re-tessellates.

The fixture uses AP242 tessellation entities (TESSELLATED_SHAPE_REPRESENTATION,
TRIANGULATED_FACE, COORDINATES_LIST) under an AP214 header — this schema-vs-
vocabulary mismatch is intentional and listed in EXEMPT_SCHEMA_MISMATCH.

Tier-3 assertions:
  n_edges_total >= 4
  face[0].surface_type == "plane"
  n_vertices_total >= 8

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from pathlib import Path as _Path
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="M070",
    schema="AP214",
    defect=(
        "STL writer does not respect existing triangulation; "
        "input: AP214 STEP file (OCCT MANTIS#0025357 pattern) where an "
        "ADVANCED_FACE has a pre-computed TESSELLATED_SHAPE_REPRESENTATION "
        "attached (from BRepMesh_IncrementalMesh with custom deflection); "
        "STL writer ignores the existing triangulation and re-tessellates "
        "from B-rep using default deflection; user's carefully-tuned mesh is lost; "
        "AP242 tessellation entities used under AP214 header (schema-vs-vocabulary "
        "mismatch is the defect mechanism — listed in EXEMPT_SCHEMA_MISMATCH); "
        "kernel must reuse any existing triangulation unless explicitly told to remesh; "
        "never silently re-tessellate; "
        "synonyms: STL writer ignores triangulation, user mesh re-tessellated, "
        "tuned mesh lost on STL export, writer recomputes deflection, "
        "STL writer ignores attached triangulation"
    ),
)

# ── B-rep: a unit square planar face ──────────────────────────────────────────
# Tier-3: face[0].surface_type == "plane", n_edges_total >= 4, n_vertices_total >= 8

# Face placement and plane
origin = f.cartesian_point((0.0, 0.0, 0.0))
dz = f.direction((0.0, 0.0, 1.0))
dx = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(origin, dz, dx)
plane = f.plane(plc)

# 4 corner points
p00 = f.cartesian_point((0.0, 0.0, 0.0))
p10 = f.cartesian_point((1.0, 0.0, 0.0))
p11 = f.cartesian_point((1.0, 1.0, 0.0))
p01 = f.cartesian_point((0.0, 1.0, 0.0))

v00 = f.vertex_point(p00)
v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11)
v01 = f.vertex_point(p01)

# 4 edges
dx_dir = f.direction((1.0, 0.0, 0.0))
dy_dir = f.direction((0.0, 1.0, 0.0))
dxn    = f.direction((-1.0, 0.0, 0.0))
dyn    = f.direction((0.0, -1.0, 0.0))

vx = f.vector(dx_dir, 1.0)
vy = f.vector(dy_dir, 1.0)
vxn = f.vector(dxn, 1.0)
vyn = f.vector(dyn, 1.0)

line_bot   = f.line(p00, vx)
line_right = f.line(p10, vy)
line_top   = f.line(p11, vxn)
line_left  = f.line(p01, vyn)

e_bot   = f.edge_curve(v00, v10, line_bot)
e_right = f.edge_curve(v10, v11, line_right)
e_top   = f.edge_curve(v11, v01, line_top)
e_left  = f.edge_curve(v01, v00, line_left)

loop = f.edge_loop([
    f.oriented_edge(e_bot,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_left,  True),
])
fob  = f.face_outer_bound(loop)
face = f.advanced_face([fob], plane, name="quad")

# OPEN_SHELL wrap (sheet body — closure_intent: sheet)
shell = f.open_shell([face], name="wrap_shell")
sbsm  = f.shell_based_surface_model([shell], name="wrap_sbsm")

# Product chain with MANIFOLD_SURFACE_SHAPE_REPRESENTATION
f.add_product_chain(sbsm, mode="surface_shape")

# ── Pre-computed user triangulation — AP242 entities under AP214 header ────────
# DEFECT: the STL writer ignores this and re-tessellates from B-rep.
# The schema-vocabulary mismatch (AP242 tess entities in AP214 file) is intentional.
coords = f._emit_raw(
    "COORDINATES_LIST('mesh_coords',4,"
    "((0.0,0.0,0.0),(1.0,0.0,0.0),(1.0,1.0,0.0),(0.0,1.0,0.0)))"
)
# TRIANGULATED_FACE: 2 triangles from the quad diagonal (1-based indices)
tri_face = f._emit_raw(
    f"TRIANGULATED_FACE('mesh_face',(),{coords.ref()},$,(1,2,3,1,3,4),())"
)
# TESSELLATED_SHAPE_REPRESENTATION — AP242 entity (schema-mismatch: under AP214 header)
# References APPLICATION_CONTEXT #9000 directly
tess_rep = f._emit_raw(
    f"TESSELLATED_SHAPE_REPRESENTATION('mesh_rep',({tri_face.ref()}),#9000)"
)

f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-8-mixed" / "M070.stp")
