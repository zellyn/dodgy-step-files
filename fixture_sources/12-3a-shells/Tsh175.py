"""Tsh175 — ShapeAnalysis_Shell.CheckOrientedShells with-self-touching-shell.

Catalog claim: Shell where two faces touch at a single point (not edge);
CheckOrientedShells uses edge-only adjacency and misses the touch.

Mechanism IS the shell structure: TWO ADVANCED_FACEs sharing exactly ONE
VERTEX_POINT with no shared EDGE_CURVE are wired into an OPEN_SHELL. face_a
IS a unit square [0,1]x[0,1] on Z=0 and face_b IS a unit square [1,2]x[1,2]
on Z=0. Both faces share the corner vertex at (1,1,0) — vertex v11 IS the
single shared VERTEX_POINT entity referenced by both face edge loops. There
IS no shared EDGE_CURVE between them — only the vertex contact at (1,1). The
two faces have consistent +Z orientation but ARE in the same OPEN_SHELL.
CheckOrientedShells propagates orientation via shared EDGE_CURVEs only; the
vertex-only contact at v11 IS not an edge, so propagation cannot cross. The
orientation mismatch at the vertex contact IS missed — IS the defect.
shape_null IS True because the shell contains a non-manifold vertex touch.

Tier-3 assertion: shape_null == True

live oracle: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh175",
    defect=(
        "TWO ADVANCED_FACEs sharing ONE VERTEX_POINT, no shared EDGE_CURVE — IS the self-touching mechanism; "
        "face_a IS a unit square x=[0,1] y=[0,1] z=0 — wired into OPEN_SHELL; "
        "face_b IS a unit square x=[1,2] y=[1,2] z=0 — wired into OPEN_SHELL; "
        "v11 IS the single shared VERTEX_POINT at (1,1,0) — IS the vertex-only contact; "
        "face_a corner uses v11 at (1,1,0) — face_b corner also uses v11 — same entity; "
        "no EDGE_CURVE IS shared between face_a and face_b — IS absence of edge adjacency; "
        "CheckOrientedShells propagates via shared EDGE_CURVEs only; "
        "vertex-only contact at v11 IS not traversed by edge-based propagation; "
        "orientation mismatch at vertex touch IS not detected — IS the defect; "
        "shell IS non-manifold at v11 due to vertex-only face contact; "
        "fix: check vertex-level adjacency in addition to edge adjacency; "
        "emit E_CHECK_ORIENTED_VERTEX_TOUCH_MISSED when vertex contact skipped"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Shared vertex at (1,1,0) — IS the single point of contact between both faces
p11 = cp(1, 1, 0)
v11 = f.vertex_point(p11)   # ONE shared VERTEX_POINT entity — IS the touch point

# face_a: unit square x=[0,1] y=[0,1] z=0
# corners: (0,0,0), (1,0,0), (1,1,0)=v11, (0,1,0)
pa00 = cp(0, 0, 0); pa10 = cp(1, 0, 0); pa01 = cp(0, 1, 0)
va00 = f.vertex_point(pa00); va10 = f.vertex_point(pa10); va01 = f.vertex_point(pa01)
# v11 IS shared — used as top-right corner of face_a
ea_bot   = led(va00, va10, pa00,  1, 0, 0)   # (0,0)→(1,0)
ea_right = led(va10, v11,  pa10,  0, 1, 0)   # (1,0)→(1,1) — arrives at shared v11
ea_top   = led(va01, v11,  pa01,  1, 0, 0)   # (0,1)→(1,1) — arrives at shared v11
ea_left  = led(va00, va01, pa00,  0, 1, 0)   # (0,0)→(0,1)
loop_a = f.edge_loop([
    f.oriented_edge(ea_bot,   True),
    f.oriented_edge(ea_right, True),
    f.oriented_edge(ea_top,   False),  # reversed: (1,1)→(0,1)
    f.oriented_edge(ea_left,  False),  # reversed: (0,1)→(0,0)
])
plane_a = f.plane(f.axis2_placement_3d(pa00, dir3(0, 0, 1), dir3(1, 0, 0)))
face_a = f.advanced_face([f.face_outer_bound(loop_a, orientation=True)], plane_a, same_sense=True)

# face_b: unit square x=[1,2] y=[1,2] z=0
# corners: (1,1,0)=v11, (2,1,0), (2,2,0), (1,2,0)
pb10 = cp(2, 1, 0); pb11 = cp(2, 2, 0); pb01 = cp(1, 2, 0)
vb10 = f.vertex_point(pb10); vb11 = f.vertex_point(pb11); vb01 = f.vertex_point(pb01)
# v11 IS shared — used as bottom-left corner of face_b
eb_bot   = led(v11,  vb10, p11,   1, 0, 0)   # (1,1)→(2,1) — departs from shared v11
eb_right = led(vb10, vb11, pb10,  0, 1, 0)   # (2,1)→(2,2)
eb_top   = led(vb01, vb11, pb01,  1, 0, 0)   # (1,2)→(2,2)
eb_left  = led(v11,  vb01, p11,   0, 1, 0)   # (1,1)→(1,2) — departs from shared v11
loop_b = f.edge_loop([
    f.oriented_edge(eb_bot,   True),
    f.oriented_edge(eb_right, True),
    f.oriented_edge(eb_top,   False),  # reversed: (2,2)→(1,2)
    f.oriented_edge(eb_left,  False),  # reversed: (1,2)→(1,1)
])
plane_b = f.plane(f.axis2_placement_3d(p11, dir3(0, 0, 1), dir3(1, 0, 0)))
face_b = f.advanced_face([f.face_outer_bound(loop_b, orientation=True)], plane_b, same_sense=True)

# OPEN_SHELL: two faces touching at single vertex v11 only — IS the self-touching mechanism
# No shared EDGE_CURVE — only shared VERTEX_POINT v11 — IS the edge-adjacency gap
shell = f.open_shell([face_a, face_b])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
