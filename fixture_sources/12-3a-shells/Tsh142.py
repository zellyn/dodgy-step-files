"""Tsh142 — ShapeFix_Shell.Perform overlapping-faces.

Catalog claim: Shell with two faces that overlap on a sub-region. Perform
doesn't detect overlap and resulting shell has tangled topology. Expected:
Perform should detect overlap and either split or reject the input.
Geometry: Two overlapping rectangles on same plane with partial intersection.

Mechanism IS the shell structure: TWO ADVANCED_FACEs on the same z=0 PLANE
where Face1 (x=[0,2], y=[0,1]) and Face2 (x=[1,3], y=[0,1]) share the
overlap region x=[1,2] — each face has its own independent EDGE_LOOP with
no shared EDGE_CURVEs. The overlapping geometry IS wired into both EDGE_LOOPs
as separate independent edges at the same coordinates. The independent-edge
overlap IS the mechanism: ShapeFix_Shell.Perform processes each face
independently without cross-checking for geometric overlap.

Tier-3 assertion: load == "ok"

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh142",
    defect=(
        "TWO ADVANCED_FACEs on z=0 PLANE with overlapping geometry — IS the mechanism; "
        "Face1 x=[0,2] y=[0,1] has 4 independent EDGE_CURVEs wired into its EDGE_LOOP; "
        "Face2 x=[1,3] y=[0,1] has 4 independent EDGE_CURVEs wired into its EDGE_LOOP; "
        "overlap region x=[1,2] y=[0,1] IS covered by both faces with no shared edges; "
        "independent EDGE_LOOPs with overlapping geometry IS the mechanism wired into topology; "
        "ShapeFix_Shell.Perform processes faces independently — no cross-face overlap detection; "
        "fix: intersect face boundaries before Perform; detect shared sub-region; "
        "emit E_FACE_OVERLAP_DETECTED when shell faces share geometric sub-region"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

def mk_plane_z0(ox, oy):
    orig = f.cartesian_point((ox, oy, 0.0))
    return f.plane(f.axis2_placement_3d(orig, dir3(0, 0, 1), dir3(1, 0, 0)))

def make_rect_face(x0, x1, y0, y1):
    """Build a rectangle face at z=0 with independent edges (no sharing)."""
    p00 = cp(x0, y0, 0); p10 = cp(x1, y0, 0)
    p11 = cp(x1, y1, 0); p01 = cp(x0, y1, 0)
    v00 = f.vertex_point(p00); v10 = f.vertex_point(p10)
    v11 = f.vertex_point(p11); v01 = f.vertex_point(p01)
    e_bot   = led(v00, v10, p00,  1, 0, 0)
    e_right = led(v10, v11, p10,  0, 1, 0)
    e_top   = led(v11, v01, p11, -1, 0, 0)
    e_left  = led(v01, v00, p01,  0, -1, 0)
    loop = f.edge_loop([
        f.oriented_edge(e_bot,   True),
        f.oriented_edge(e_right, True),
        f.oriented_edge(e_top,   True),
        f.oriented_edge(e_left,  True),
    ])
    plane = mk_plane_z0(x0, y0)
    return f.advanced_face([f.face_outer_bound(loop, orientation=True)], plane, same_sense=True)

# Face1: x=[0,2], y=[0,1] — IS the left overlapping face wired into topology
face1 = make_rect_face(0, 2, 0, 1)

# Face2: x=[1,3], y=[0,1] — IS the right overlapping face (x=[1,2] overlaps Face1)
face2 = make_rect_face(1, 3, 0, 1)

# OPEN_SHELL: two overlapping faces with no shared edges — IS the overlap mechanism
shell = f.open_shell([face1, face2])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
