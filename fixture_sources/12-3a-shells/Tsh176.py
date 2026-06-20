"""Tsh176 — ShapeUpgrade_ShellSewing.Apply with-coincident-but-different-orientation.

Catalog claim: Two shells with coincident faces in opposite orientations;
Apply doesn't detect orientation conflict and produces overlapping output.

Mechanism IS the shell structure: TWO ADVANCED_FACEs with IDENTICAL vertex
positions but OPPOSITE face orientations are each wired into their own
OPEN_SHELL in a SHELL_BASED_SURFACE_MODEL. face_pos IS a unit square
[0,1]x[0,1] on Z=0 with normal +Z (same_sense=True). face_neg IS the
identical unit square with ALL edges reversed, giving normal -Z
(same_sense=False on same plane). Both faces share NO edge entity —
face_pos and face_neg have their own independent EDGE_CURVEs at the same
geometric positions. shell_pos (containing face_pos) and shell_neg
(containing face_neg) are geometrically coincident but topologically
separate. Apply() sews by proximity — edges of face_pos and face_neg are
coincident, so Apply() merges them into one shell. The output IS
geometrically degenerate: a face with no net area (positive and negative
cancel). The orientation conflict IS not detected before merging — IS the
defect.

Tier-3 assertion: shape_null == True

live oracle: occt=empty/empty gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh176",
    defect=(
        "TWO ADVANCED_FACEs with IDENTICAL geometry but OPPOSITE orientations in TWO OPEN_SHELLs — "
        "IS the coincident-opposite-orientation mechanism; "
        "face_pos IS unit square x=[0,1] y=[0,1] z=0, same_sense=True, normal +Z — wired into shell_pos; "
        "face_neg IS unit square x=[0,1] y=[0,1] z=0, same_sense=False, normal -Z — wired into shell_neg; "
        "face_pos and face_neg have SEPARATE EDGE_CURVE entities at IDENTICAL geometric positions; "
        "shell_pos and shell_neg are geometrically coincident — IS the sewing trigger; "
        "Apply() sews coincident edges across shells, merging face_pos and face_neg; "
        "orientation conflict (+Z vs -Z) IS not detected before merging; "
        "output IS geometrically degenerate — positive and negative orientations cancel; "
        "fix: detect opposite-orientation face pairs before sewing; "
        "emit E_SEWING_ORIENTATION_CONFLICT when coincident faces have opposite normals"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# face_pos: unit square [0,1]x[0,1] on Z=0 with normal +Z (same_sense=True)
# CCW traversal viewed from +Z: (0,0)→(1,0)→(1,1)→(0,1)→(0,0)
pp00 = cp(0, 0, 0); pp10 = cp(1, 0, 0); pp11 = cp(1, 1, 0); pp01 = cp(0, 1, 0)
vp00 = f.vertex_point(pp00); vp10 = f.vertex_point(pp10)
vp11 = f.vertex_point(pp11); vp01 = f.vertex_point(pp01)
ep_bot   = led(vp00, vp10, pp00,  1, 0, 0)
ep_right = led(vp10, vp11, pp10,  0, 1, 0)
ep_top   = led(vp01, vp11, pp01,  1, 0, 0)
ep_left  = led(vp00, vp01, pp00,  0, 1, 0)
loop_pos = f.edge_loop([
    f.oriented_edge(ep_bot,   True),
    f.oriented_edge(ep_right, True),
    f.oriented_edge(ep_top,   False),
    f.oriented_edge(ep_left,  False),
])
plane_pos = f.plane(f.axis2_placement_3d(pp00, dir3(0, 0, 1), dir3(1, 0, 0)))
face_pos = f.advanced_face([f.face_outer_bound(loop_pos, orientation=True)], plane_pos, same_sense=True)

# shell_pos: OPEN_SHELL with face_pos (+Z normal) — IS first coincident shell
shell_pos = f.open_shell([face_pos])

# face_neg: IDENTICAL square [0,1]x[0,1] on Z=0 with normal -Z
# CW traversal viewed from +Z gives -Z normal: (0,0)→(0,1)→(1,1)→(1,0)→(0,0)
# Implemented as same_sense=False on +Z plane — gives effective normal -Z
# Uses SEPARATE edge entities at same geometric positions — IS the coincidence
qn00 = cp(0, 0, 0); qn10 = cp(1, 0, 0); qn11 = cp(1, 1, 0); qn01 = cp(0, 1, 0)
vn00 = f.vertex_point(qn00); vn10 = f.vertex_point(qn10)
vn11 = f.vertex_point(qn11); vn01 = f.vertex_point(qn01)
# CW: (0,0)→(0,1)→(1,1)→(1,0)→(0,0) for -Z outward normal with same_sense=False
en_left  = led(vn00, vn01, qn00,  0, 1, 0)   # (0,0)→(0,1)
en_top   = led(vn01, vn11, qn01,  1, 0, 0)   # (0,1)→(1,1)
en_right = led(vn10, vn11, qn10,  0, 1, 0)   # (1,0)→(1,1) — reversed in loop
en_bot   = led(vn00, vn10, qn00,  1, 0, 0)   # (0,0)→(1,0) — reversed in loop
loop_neg = f.edge_loop([
    f.oriented_edge(en_left,  True),
    f.oriented_edge(en_top,   True),
    f.oriented_edge(en_right, False),   # (1,1)→(1,0)
    f.oriented_edge(en_bot,   False),   # (1,0)→(0,0)
])
# same plane +Z but same_sense=False — gives face normal -Z — IS the opposite orientation
plane_neg = f.plane(f.axis2_placement_3d(qn00, dir3(0, 0, 1), dir3(1, 0, 0)))
face_neg = f.advanced_face([f.face_outer_bound(loop_neg, orientation=True)], plane_neg, same_sense=False)

# shell_neg: OPEN_SHELL with face_neg (-Z normal) — IS the coincident opposite-orientation shell
shell_neg = f.open_shell([face_neg])

# SHELL_BASED_SURFACE_MODEL with both shells — shell_pos and shell_neg ARE geometrically coincident
# Apply() merges them; orientation conflict IS not detected — IS the defect
sbsm = f.shell_based_surface_model([shell_pos, shell_neg])
f.add_product_chain(sbsm)
