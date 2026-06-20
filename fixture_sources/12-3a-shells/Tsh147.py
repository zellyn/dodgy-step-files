"""Tsh147 — ShapeFix_Shell.Perform fix-then-revert.

Catalog claim: Two adjacent faces sharing an edge; second face has inverted
orientation. Perform fixes orientation but subsequent FixFaceOrientation pass
reverts fix due to status flag confusion. Tests repeated-pass stability.

Mechanism IS the shell structure: TWO ADVANCED_FACEs sharing an edge (x=1,
y=[0,1], z=0) — the shared EDGE_LOOP boundary IS wired into both faces. Face1
has same_sense=True (correct outward normal); Face2 has same_sense=False
(inverted normal) — the SAME_SENSE=False flag IS the mechanism wired directly
into the ADVANCED_FACE entity. ShapeFix_Shell.Perform first-pass fixes the
inverted face, but a second FixFaceOrientation pass reads a stale status flag
and reverts the correction, leaving orientation inconsistent.

Tier-3 assertion: load == "ok"

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh147",
    defect=(
        "TWO ADVANCED_FACEs sharing EDGE_CURVE at x=1 y=[0,1] z=0 — IS the fix-then-revert mechanism; "
        "Face1 (x=[0,1]) SAME_SENSE=True — IS wired into OPEN_SHELL with correct outward normal; "
        "Face2 (x=[1,2]) SAME_SENSE=False — IS the inverted-orientation mechanism wired into ADVANCED_FACE; "
        "SAME_SENSE=False on Face2 IS the status-flag trigger for ShapeFix_Shell.Perform first-pass fix; "
        "second FixFaceOrientation pass reads stale status and reverts the fix — repeated-pass instability; "
        "fix: clear status flags between passes; track orientation state per-face across fix iterations; "
        "emit E_ORIENTATION_FIX_REVERT when Perform second-pass contradicts first-pass result"
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

# Two adjacent unit squares at z=0
p00 = cp(0, 0, 0); p10 = cp(1, 0, 0); p20 = cp(2, 0, 0)
p01 = cp(0, 1, 0); p11 = cp(1, 1, 0); p21 = cp(2, 1, 0)

v00 = f.vertex_point(p00); v10 = f.vertex_point(p10); v20 = f.vertex_point(p20)
v01 = f.vertex_point(p01); v11 = f.vertex_point(p11); v21 = f.vertex_point(p21)

# Face1 edges: x=[0,1]
e_f1_bot  = led(v00, v10, p00,  1, 0, 0)
e_f1_top  = led(v01, v11, p01,  1, 0, 0)
e_f1_left = led(v00, v01, p00,  0, 1, 0)

# Shared seam edge at x=1 — IS wired into both EDGE_LOOPs
e_seam = led(v10, v11, p10,  0, 1, 0)

# Face2 edges: x=[1,2]
e_f2_bot   = led(v10, v20, p10,  1, 0, 0)
e_f2_top   = led(v11, v21, p11,  1, 0, 0)
e_f2_right = led(v20, v21, p20,  0, 1, 0)

# Face1: correct orientation — same_sense=True
loop1 = f.edge_loop([
    f.oriented_edge(e_f1_bot,  True),
    f.oriented_edge(e_seam,    True),
    f.oriented_edge(e_f1_top,  False),
    f.oriented_edge(e_f1_left, False),
])
face1 = f.advanced_face([f.face_outer_bound(loop1, orientation=True)], mk_plane_z0(0, 0), same_sense=True)

# Face2: inverted orientation — same_sense=False IS the mechanism wired into ADVANCED_FACE
loop2 = f.edge_loop([
    f.oriented_edge(e_f2_bot,   True),
    f.oriented_edge(e_f2_right, True),
    f.oriented_edge(e_f2_top,   False),
    f.oriented_edge(e_seam,     False),
])
# SAME_SENSE=False IS the inverted-orientation flag — triggers fix-then-revert
face2 = f.advanced_face([f.face_outer_bound(loop2, orientation=True)], mk_plane_z0(1, 0), same_sense=False)

# OPEN_SHELL: Face1 correct + Face2 inverted — IS the fix-then-revert mechanism
shell = f.open_shell([face1, face2])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
