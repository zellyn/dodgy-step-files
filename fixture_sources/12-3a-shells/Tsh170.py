"""Tsh170 — ShapeAnalysis_Shell.CheckOrientedShells with-zero-tolerance.

Catalog claim: Adjacent faces with exact edge coincidence. CheckOrientedShells
(tolerance=0) produces ambiguous match verdicts; adjacent-face orientation
propagation undefined.

Mechanism IS the shell structure: TWO ADVANCED_FACEs sharing ONE EDGE_CURVE
at exact coincidence (x=1) IS wired into an OPEN_SHELL. The shared edge
e_seam IS the same EDGE_CURVE entity referenced by both face loops — no
geometric approximation, exact coincidence at tolerance=0. face_left covers
x=[0,1] and face_right covers x=[1,2]; their shared boundary IS e_seam at x=1.
At tolerance=0 CheckOrientedShells must decide whether co-located edge endpoints
count as "matched"; the exact-zero comparison path IS the ambiguous branch.
Orientation propagation across e_seam IS undefined when the match predicate
uses strict equality: floating-point exact-zero tolerance IS the defect trigger.

Tier-3 assertion: n_faces_total == 2

live oracle: occt=shape(1)/shape(1) gmsh=shape(15) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh170",
    defect=(
        "TWO ADVANCED_FACEs sharing ONE EDGE_CURVE at exact coincidence in OPEN_SHELL — "
        "IS the zero-tolerance orientation mechanism; "
        "e_seam IS one EDGE_CURVE at x=1, y=[0,1] — IS the shared exact-coincidence edge; "
        "face_left IS wired with loop_left (x=[0,1]) — e_seam traversed forward (v10->v11); "
        "face_right IS wired with loop_right (x=[1,2]) — e_seam traversed reversed (v11->v10); "
        "shared edge entity IS identical — zero geometric gap, exact coincidence; "
        "CheckOrientedShells(tolerance=0) invokes strict-equality match predicate; "
        "exact-zero path IS the ambiguous branch: match == True but also boundary == exact; "
        "orientation propagation from face_left to face_right via e_seam IS undefined; "
        "both faces ARE correctly oriented (same_sense=.T.) — defect is in propagation logic; "
        "fix: use epsilon > 0 for edge match; emit E_CHECK_ORIENTED_ZERO_TOL_AMBIGUOUS; "
        "when tolerance=0 and exact-coincidence edge found, propagation result IS undefined"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Vertices for two unit squares sharing seam at x=1
p00 = cp(0, 0, 0); p10 = cp(1, 0, 0); p20 = cp(2, 0, 0)
p01 = cp(0, 1, 0); p11 = cp(1, 1, 0); p21 = cp(2, 1, 0)

v00 = f.vertex_point(p00); v10 = f.vertex_point(p10); v20 = f.vertex_point(p20)
v01 = f.vertex_point(p01); v11 = f.vertex_point(p11); v21 = f.vertex_point(p21)

# face_left private edges (x=[0,1])
e_l_bot  = led(v00, v10, p00,  1, 0, 0)
e_l_left = led(v00, v01, p00,  0, 1, 0)
e_l_top  = led(v01, v11, p01,  1, 0, 0)

# Shared seam edge at x=1 — IS the exact-coincidence edge, zero gap
e_seam = led(v10, v11, p10,  0, 1, 0)  # v10->v11 is canonical direction

# face_right private edges (x=[1,2])
e_r_bot   = led(v10, v20, p10,  1, 0, 0)
e_r_right = led(v20, v21, p20,  0, 1, 0)
e_r_top   = led(v11, v21, p11,  1, 0, 0)

# Plane for both faces (z=0, normal +z)
plane = f.plane(f.axis2_placement_3d(p00, dir3(0, 0, 1), dir3(1, 0, 0)))

# face_left: x=[0,1], correctly oriented, seam traversed forward
loop_left = f.edge_loop([
    f.oriented_edge(e_l_bot,  True),
    f.oriented_edge(e_seam,   True),   # v10->v11 forward — seam right boundary
    f.oriented_edge(e_l_top,  False),
    f.oriented_edge(e_l_left, False),
])
face_left = f.advanced_face([f.face_outer_bound(loop_left, orientation=True)], plane, same_sense=True)

# face_right: x=[1,2], correctly oriented, seam traversed reversed
loop_right = f.edge_loop([
    f.oriented_edge(e_r_bot,   True),
    f.oriented_edge(e_r_right, True),
    f.oriented_edge(e_r_top,   False),
    f.oriented_edge(e_seam,    False),  # v11->v10 reversed — seam left boundary
])
face_right = f.advanced_face([f.face_outer_bound(loop_right, orientation=True)], plane, same_sense=True)

# OPEN_SHELL: two faces sharing one edge at exact coincidence — IS the zero-tolerance mechanism
shell = f.open_shell([face_left, face_right])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
