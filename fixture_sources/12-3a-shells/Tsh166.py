"""Tsh166 — ShapeUpgrade_ShellSewing.Apply face-with-same-base.

Catalog claim: Sewing input has two faces sharing the same underlying surface
entity (PLANE reference). Apply doesn't detect duplication and produces
overlapping output faces. Tests surface identity checking.

Mechanism IS the shell structure: TWO ADVANCED_FACEs both referencing the
SAME PLANE entity IS wired into one OPEN_SHELL. Face0 and Face1 share an
identical PLANE (same AXIS2_PLACEMENT_3D, same entity ID) but each face
has its own distinct EDGE_LOOP and vertex set. The shared surface reference
IS the duplication that ShellSewing.Apply fails to detect. Both faces
occupy the same geometric region (identical unit square, z=0) but ARE two
distinct ADVANCED_FACE entries in the shell topology. The duplicated-plane
OPEN_SHELL IS the minimal structure that exposes surface identity blindness.

Tier-3 assertion: n_faces_total == 2

live oracle: occt=shape(1)/shape(1) gmsh=shape(10) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh166",
    defect=(
        "TWO ADVANCED_FACEs sharing ONE PLANE entity in OPEN_SHELL — "
        "IS the same-base duplication mechanism; "
        "plane_shared IS one PLANE with AXIS2_PLACEMENT_3D at origin, normal +z — "
        "IS the single surface entity referenced by BOTH faces; "
        "Face0 IS wired with loop0 (own vertex set v00a..v11a) referencing plane_shared; "
        "Face1 IS wired with loop1 (own vertex set v00b..v11b) referencing plane_shared; "
        "both faces occupy identical unit square region [0,1]x[0,1] at z=0; "
        "shared PLANE entity pointer IS the identity that Apply() should detect; "
        "ShellSewing.Apply compares geometric coincidence, not entity identity; "
        "surface identity blindness IS the defect: duplicate face survives sewing; "
        "output OPEN_SHELL retains two overlapping faces — IS the defect manifestation; "
        "fix: compare surface entity IDs before sewing; deduplicate co-located faces; "
        "emit E_SEWING_DUPLICATE_SURFACE when two faces share same underlying surface"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# One shared PLANE entity — IS the same-base identity
p_origin = cp(0, 0, 0)
plane_shared = f.plane(f.axis2_placement_3d(p_origin, dir3(0, 0, 1), dir3(1, 0, 0)))

# Face0 — own vertex/edge set, references plane_shared
p00a = cp(0,0,0); p10a = cp(1,0,0); p11a = cp(1,1,0); p01a = cp(0,1,0)
v00a = f.vertex_point(p00a); v10a = f.vertex_point(p10a)
v11a = f.vertex_point(p11a); v01a = f.vertex_point(p01a)
e0_bot   = led(v00a, v10a, p00a,  1, 0, 0)
e0_right = led(v10a, v11a, p10a,  0, 1, 0)
e0_top   = led(v01a, v11a, p01a,  1, 0, 0)
e0_left  = led(v00a, v01a, p00a,  0, 1, 0)
loop0 = f.edge_loop([
    f.oriented_edge(e0_bot,   True),
    f.oriented_edge(e0_right, True),
    f.oriented_edge(e0_top,   False),
    f.oriented_edge(e0_left,  False),
])
face0 = f.advanced_face([f.face_outer_bound(loop0, orientation=True)], plane_shared, same_sense=True)

# Face1 — own vertex/edge set, references the SAME plane_shared entity
p00b = cp(0,0,0); p10b = cp(1,0,0); p11b = cp(1,1,0); p01b = cp(0,1,0)
v00b = f.vertex_point(p00b); v10b = f.vertex_point(p10b)
v11b = f.vertex_point(p11b); v01b = f.vertex_point(p01b)
e1_bot   = led(v00b, v10b, p00b,  1, 0, 0)
e1_right = led(v10b, v11b, p10b,  0, 1, 0)
e1_top   = led(v01b, v11b, p01b,  1, 0, 0)
e1_left  = led(v00b, v01b, p00b,  0, 1, 0)
loop1 = f.edge_loop([
    f.oriented_edge(e1_bot,   True),
    f.oriented_edge(e1_right, True),
    f.oriented_edge(e1_top,   False),
    f.oriented_edge(e1_left,  False),
])
# plane_shared reused — IS the same-base identity defect trigger
face1 = f.advanced_face([f.face_outer_bound(loop1, orientation=True)], plane_shared, same_sense=True)

# OPEN_SHELL with two faces on same underlying PLANE — IS the mechanism
shell = f.open_shell([face0, face1])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
