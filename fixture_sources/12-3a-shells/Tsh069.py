"""Tsh069 — CheckOrientedShells Normal-Flip Detection.

Catalog claim: Two ADVANCED_FACEs share a base rectangle but with reversed normal
orientation (one +Z, one -Z). The shared edge makes the shell appear non-manifold.
ShapeAnalysis_Shell.CheckOrientedShells at line 142 detects normal-flip inconsistency
across adjacent faces in the shell.

Mechanism IS the shell structure: 3 ADVANCED_FACEs are wired into one OPEN_SHELL.
Face A (unit square, normal +Z) and Face B (same unit square domain, normal -Z via
orientation flag False on ADVANCED_FACE) share the same EDGE_CURVE entities forming
their boundary. The opposing normal IS wired directly into the face/shell topology via
the ADVANCED_FACE same_sense flag: Face A has same_sense=.T., Face B has same_sense=.F.
A third neutral face (Face C, different domain, normal +Z) provides a well-formed
reference. CheckOrientedShells at line 142 sees the normal-flip between A and B across
the shared boundary and flags the orientation conflict.

Byte assertions: (none explicit in catalog)

Tier-3 assertion: n_faces_total == 3

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh069",
    defect=(
        "OPEN_SHELL with 3 ADVANCED_FACEs; "
        "Face A (unit square at z=0, same_sense=.T.) and "
        "Face B (same unit square, same_sense=.F.) share boundary EDGE_CURVEs; "
        "opposing same_sense flags on coplanar faces sharing boundary IS the mechanism; "
        "normal-flip inconsistency IS directly wired into ADVANCED_FACE topology; "
        "CheckOrientedShells at line 142 detects normal-flip across shared boundary; "
        "fix: kernel should detect faces with opposing normals on shared edges and "
        "flag the shell as non-manifold or require reorientation"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Shared plane z=0, normal +Z reference
orig = cp(0,0,0); zdir = dir3(0,0,1); xdir = dir3(1,0,0)
plc = f.axis2_placement_3d(orig, zdir, xdir)
plane = f.plane(plc)

# Shared boundary of unit square (0,0)→(1,0)→(1,1)→(0,1)
p00 = cp(0,0,0); p10 = cp(1,0,0); p11 = cp(1,1,0); p01 = cp(0,1,0)
v00 = f.vertex_point(p00); v10 = f.vertex_point(p10)
v11 = f.vertex_point(p11); v01 = f.vertex_point(p01)

# Shared EDGE_CURVE entities — both Face A and Face B use these same edges
eA0 = led(v00, v10, p00,  1, 0, 0)   # bottom
eA1 = led(v10, v11, p10,  0, 1, 0)   # right
eA2 = led(v11, v01, p11, -1, 0, 0)   # top
eA3 = led(v01, v00, p01,  0,-1, 0)   # left

loopA = f.edge_loop([f.oriented_edge(eA0,True), f.oriented_edge(eA1,True),
                     f.oriented_edge(eA2,True), f.oriented_edge(eA3,True)])

# Face A: same_sense = True → outward normal +Z
face_A = f.advanced_face([f.face_outer_bound(loopA)], plane, same_sense=True)

# Face B: same_sense = False → outward normal -Z (NORMAL-FLIP — IS the mechanism)
# Same edge loop (reversed winding for -Z face)
loopB = f.edge_loop([f.oriented_edge(eA0,False), f.oriented_edge(eA3,False),
                     f.oriented_edge(eA2,False), f.oriented_edge(eA1,False)])
face_B = f.advanced_face([f.face_outer_bound(loopB)], plane, same_sense=False)

# Face C: independent unit square at x=2..3 (well-formed, normal +Z)
p20 = cp(2,0,0); p30 = cp(3,0,0); p31 = cp(3,1,0); p21 = cp(2,1,0)
v20 = f.vertex_point(p20); v30 = f.vertex_point(p30)
v31 = f.vertex_point(p31); v21 = f.vertex_point(p21)
eC0 = led(v20, v30, p20,  1, 0, 0)
eC1 = led(v30, v31, p30,  0, 1, 0)
eC2 = led(v31, v21, p31, -1, 0, 0)
eC3 = led(v21, v20, p21,  0,-1, 0)
loopC = f.edge_loop([f.oriented_edge(eC0,True), f.oriented_edge(eC1,True),
                     f.oriented_edge(eC2,True), f.oriented_edge(eC3,True)])
orig_c = cp(2,0,0)
plc_c = f.axis2_placement_3d(orig_c, dir3(0,0,1), dir3(1,0,0))
plane_c = f.plane(plc_c)
face_C = f.advanced_face([f.face_outer_bound(loopC)], plane_c, same_sense=True)

# OPEN_SHELL: normal-flip between Face A and Face B IS wired into topology
shell = f.open_shell([face_A, face_B, face_C])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
