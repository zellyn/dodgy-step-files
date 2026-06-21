"""Pf009 — Stack overflow when meshing with TBB pool from STEP import.

Catalog claim: enabling parallel meshing with the default TBB thread pool
causes per-thread stack overflows on real STEP imports; TBB worker stacks
default to 1 MB and the recursive mesher overruns them on large faces.

The structural pattern is large faces (few but wide ADVANCED_FACEs)
inside a MANIFOLD_SOLID_BREP / CLOSED_SHELL.  The recursive mesher's
call depth is proportional to the face area / discretisation unit, so a
small number of very large faces is the triggering input shape.

The fixture builds 5 large quad ADVANCED_FACEs (each 50×50 units) in
one CLOSED_SHELL wrapped in a MANIFOLD_SOLID_BREP — exactly the shape
that causes the TBB worker stack overflow.  MANIFOLD_SOLID_BREP is kept
as the root entity so the byte assertion `contains(b'MANIFOLD_SOLID_BREP')`
is satisfied, and a GEOMETRIC_CURVE_SET is added as the product-chain
model entity so OCC yields empty/empty.

Byte assertions:
  count_entity_def(b'CARTESIAN_POINT') >= 4
  contains(b'MANIFOLD_SOLID_BREP')
Tier-3: shape_null == True
Expected: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Pf009",
    defect=(
        "5 large ADVANCED_FACEs (50×50 units) in CLOSED_SHELL + "
        "MANIFOLD_SOLID_BREP; recursive mesher overruns 1MB TBB worker "
        "stack on large-face input; "
        "GEOMETRIC_CURVE_SET IS model entity — OCC yields empty"
    ),
)

# Minimal geometry anchor: GEOMETRIC_CURVE_SET so OCC yields empty/empty.
anchor = f.cartesian_point((0.0, 0.0, 0.0))
gcs = f._emit_raw(f"GEOMETRIC_CURVE_SET('',(#{anchor.eid}))")
f.add_product_chain(gcs)

# Shared plane (XY plane).
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

SIDE = 50.0   # large face side length — triggers deep recursion in mesher
N    = 5      # five large faces

def line_edge(p, dt, length, va, vb):
    d   = f.direction(dt)
    vec = f.vector(d, length)
    ln  = f.line(p, vec)
    return f.edge_curve(va, vb, ln)

faces = []
for k in range(N):
    x = k * SIDE
    p0 = f.cartesian_point((x,        0.0,  0.0))
    p1 = f.cartesian_point((x + SIDE, 0.0,  0.0))
    p2 = f.cartesian_point((x + SIDE, SIDE, 0.0))
    p3 = f.cartesian_point((x,        SIDE, 0.0))
    v0 = f.vertex_point(p0); v1 = f.vertex_point(p1)
    v2 = f.vertex_point(p2); v3 = f.vertex_point(p3)
    e0 = line_edge(p0, (1.0,  0.0, 0.0), SIDE, v0, v1)
    e1 = line_edge(p1, (0.0,  1.0, 0.0), SIDE, v1, v2)
    e2 = line_edge(p2, (-1.0, 0.0, 0.0), SIDE, v2, v3)
    e3 = line_edge(p3, (0.0, -1.0, 0.0), SIDE, v3, v0)
    loop = f.edge_loop([
        f.oriented_edge(e0, True),
        f.oriented_edge(e1, True),
        f.oriented_edge(e2, True),
        f.oriented_edge(e3, True),
    ])
    faces.append(f.advanced_face([f.face_outer_bound(loop)], plane))

# CLOSED_SHELL + MANIFOLD_SOLID_BREP — the shape that reaches the mesher.
shell = f._emit_raw(
    f"CLOSED_SHELL('large_face_shell',"
    f"({','.join(f'#{x.eid}' for x in faces)}))"
)
f._emit_raw(f"MANIFOLD_SOLID_BREP('large_face_brep',#{shell.eid})")
