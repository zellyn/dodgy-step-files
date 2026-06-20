"""Tsh167 — ShapeFix_Shell.FixFaceOrientation with-empty-loop.

Catalog claim: Shell with one face whose outer loop is empty (zero edges).
FixFaceOrientation produces arbitrary orientation for degenerate face.
Tests boundary validation in orientation fix.

Mechanism IS the shell structure: TWO ADVANCED_FACEs wired into an OPEN_SHELL —
face_deg has an EDGE_LOOP with zero oriented-edge entries (empty loop) IS the
degenerate face; face_good is a normal unit-square face with a fully wired
EDGE_LOOP. The empty EDGE_LOOP on face_deg IS wired as the FACE_OUTER_BOUND of
face_deg — it IS a structurally valid STEP reference (non-null loop entity)
but contains no ORIENTED_EDGEs. FixFaceOrientation needs boundary traversal
to determine outward normal; the empty loop provides no traversal data, so
orientation assignment IS arbitrary. The two-face shell with one empty-loop
face IS the minimal structure that exposes the boundary validation gap.

Tier-3 assertion: n_faces_total == 2

live oracle: occt=shape(1)/shape(1) gmsh=shape(10) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh167",
    defect=(
        "TWO ADVANCED_FACEs in OPEN_SHELL — IS the empty-loop orientation mechanism; "
        "face_deg IS wired with EDGE_LOOP containing zero ORIENTED_EDGEs — IS empty loop; "
        "empty EDGE_LOOP IS wired as FACE_OUTER_BOUND of face_deg — structurally valid ref; "
        "face_good IS wired with loop_good (4 oriented edges, unit square [0,1]x[0,1]); "
        "face_deg plane IS at x=[1,2] (adjacent to face_good at x=[0,1]); "
        "FixFaceOrientation traverses outer loop to determine outward normal direction; "
        "empty loop has no traversal data — orientation assignment IS arbitrary; "
        "face_deg same_sense IS set .T. but empty loop cannot confirm/deny it; "
        "fix: validate EDGE_LOOP is non-empty before orientation traversal; "
        "emit E_FIX_FACE_ORIENT_EMPTY_LOOP when outer loop has zero edges"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# face_good: unit square [0,1]x[0,1] at z=0, fully wired loop
p00 = cp(0, 0, 0); p10 = cp(1, 0, 0); p11 = cp(1, 1, 0); p01 = cp(0, 1, 0)
v00 = f.vertex_point(p00); v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11); v01 = f.vertex_point(p01)
e_bot   = led(v00, v10, p00,  1, 0, 0)
e_right = led(v10, v11, p10,  0, 1, 0)
e_top   = led(v01, v11, p01,  1, 0, 0)
e_left  = led(v00, v01, p00,  0, 1, 0)
loop_good = f.edge_loop([
    f.oriented_edge(e_bot,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   False),
    f.oriented_edge(e_left,  False),
])
plane_good = f.plane(f.axis2_placement_3d(p00, dir3(0, 0, 1), dir3(1, 0, 0)))
face_good = f.advanced_face([f.face_outer_bound(loop_good, orientation=True)], plane_good, same_sense=True)

# face_deg: adjacent unit square [1,2]x[0,1] at z=0, EMPTY EDGE_LOOP — IS the mechanism
p10d = cp(1, 0, 0); p20d = cp(2, 0, 0)  # reference point for plane
plane_deg = f.plane(f.axis2_placement_3d(p10d, dir3(0, 0, 1), dir3(1, 0, 0)))
# Empty edge_loop: zero oriented-edge entries — IS the degenerate outer boundary
loop_empty = f.edge_loop([])  # no edges — IS the empty loop
face_deg = f.advanced_face([f.face_outer_bound(loop_empty, orientation=True)], plane_deg, same_sense=True)

# OPEN_SHELL: good face + degenerate empty-loop face — IS the mechanism
shell = f.open_shell([face_good, face_deg])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
