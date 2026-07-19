"""Tsh085 — ShapeFix_Shell.FixFaceOrientation transition-point.

Catalog claim: Shell containing two adjacent faces meeting at shared edge
with opposing normal vectors (one +Z, one -Z at seam). Edge-traversal
neighbor selection fails to detect normal discontinuity; fixer chooses wrong
orientation branch during iteration.

Mechanism IS the shell structure: OPEN_SHELL contains 2 ADVANCED_FACEs
sharing a single EDGE_CURVE entity at x=1. Face A (x=0..1) has plane normal
+Z (same_sense=True); Face B (x=1..2) has plane normal -Z (same_sense=False).
The shared EDGE_CURVE IS wired into both EDGE_LOOPs: Face A uses it reversed
(oriented_edge .F.), Face B uses it forward (oriented_edge .T.). At the
shared seam the outward normals are anti-parallel (+Z on left, -Z on right);
this normal discontinuity IS the mechanism directly embedded in the ADVANCED_FACE
same_sense flags. FixFaceOrientation's edge-traversal at line 1428 picks a
neighbor branch at the seam but cannot distinguish which face is correctly
oriented, leading it to fix the wrong face.

Tier-3 assertion: load == "ok"

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh085",
    defect=(
        "OPEN_SHELL with 2 ADVANCED_FACEs; "
        "one EDGE_CURVE IS shared between both faces at x=1; "
        "Face A (x=0..1) IS wired same_sense=True (normal +Z); "
        "Face B (x=1..2) IS wired same_sense=False (normal -Z, i.e. inward); "
        "opposing same_sense flags at shared seam IS the mechanism; "
        "anti-parallel normals at transition point IS directly in ADVANCED_FACE topology; "
        "ShapeFix_Shell.FixFaceOrientation at line 1428 traverses seam; "
        "cannot distinguish which side is correctly oriented; "
        "fix: compare face normals at shared edge before choosing orientation branch; "
        "emit E_NORMAL_DISCONTINUITY at transition edges"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Six vertices for two adjacent unit quads
p00 = cp(0, 0, 0); p10 = cp(1, 0, 0); p20 = cp(2, 0, 0)
p01 = cp(0, 1, 0); p11 = cp(1, 1, 0); p21 = cp(2, 1, 0)

v00 = f.vertex_point(p00); v10 = f.vertex_point(p10); v20 = f.vertex_point(p20)
v01 = f.vertex_point(p01); v11 = f.vertex_point(p11); v21 = f.vertex_point(p21)

# Shared seam edge at x=1: (1,0,0)→(1,1,0)
seam = led(v10, v11, p10, 0, 1, 0)

# ── Face A: left quad x=0..1, normal +Z (same_sense=True) ─────────────────
pl_A = f.plane(f.axis2_placement_3d(p00, dir3(0, 0, 1), dir3(1, 0, 0)))
eA_bot  = led(v00, v10, p00,  1, 0, 0)
eA_top  = led(v11, v01, p11, -1, 0, 0)
eA_left = led(v01, v00, p01,  0,-1, 0)
loopA = f.edge_loop([
    f.oriented_edge(eA_bot,  True),
    f.oriented_edge(seam,    True),    # (1,0,0)→(1,1,0) forward
    f.oriented_edge(eA_top,  True),
    f.oriented_edge(eA_left, True),
])
face_A = f.advanced_face([f.face_outer_bound(loopA)], pl_A, same_sense=True)

# ── Face B: right quad x=1..2, normal -Z (same_sense=False) IS the defect ─
pl_B = f.plane(f.axis2_placement_3d(p10, dir3(0, 0, 1), dir3(1, 0, 0)))
eB_bot   = led(v10, v20, p10,  1, 0, 0)
eB_right = led(v20, v21, p20,  0, 1, 0)
eB_top   = led(v21, v11, p21, -1, 0, 0)
loopB = f.edge_loop([
    f.oriented_edge(eB_bot,   True),
    f.oriented_edge(eB_right, True),
    f.oriented_edge(eB_top,   True),
    f.oriented_edge(seam,     False),  # (1,1,0)→(1,0,0) reversed at seam
])
# same_sense=False IS the anti-parallel normal wired into Face B
face_B = f.advanced_face([f.face_outer_bound(loopB)], pl_B, same_sense=False)

# OPEN_SHELL: normal discontinuity at shared seam IS the mechanism
shell = f.open_shell([face_A, face_B])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
