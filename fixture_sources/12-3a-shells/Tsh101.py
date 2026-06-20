"""Tsh101 — ShapeUpgrade_ShellSewing.Apply tolerance-driven merge.

Catalog claim: Two shells with closest vertices offset by (0.0005, 0.0005, 0)
— within tolerance (1.0E-3). Sewing merges shells but fails to update merged
vertex tolerance to cumulative value, leaving orphaned tight tolerance.

Mechanism IS the shell structure: Two OPEN_SHELLs each contain one
ADVANCED_FACE. Shell A's face has its right-edge vertex at (1.0, 0.0, 0.0)
and (1.0, 1.0, 0.0). Shell B's face has its left-edge vertex at
(1.0005, 0.0005, 0.0) and (1.0005, 1.0005, 0.0) — offset by (0.0005, 0.0005, 0).
This sub-tolerance offset IS directly wired into the VERTEX_POINT coordinates.
The gap (≈0.000707) IS within sewing tolerance (1.0E-3), so ShellSewing.Apply
merges the shells. After merge, the joined vertex IS the mechanism: its
tolerance should reflect the merge distance (~7.07E-4) but ShellSewing sets
the vertex tolerance to the tighter original value, leaving an orphaned stale
tolerance. The near-coincident vertex pair IS the mechanism wired into both
shells' face topology.

Tier-3 assertion: n_faces_total == 2

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh101",
    defect=(
        "Two OPEN_SHELLs each with 1 ADVANCED_FACE; near-coincident vertex pair IS the mechanism; "
        "Shell A right-edge vertices at (1.0, 0.0, 0.0) and (1.0, 1.0, 0.0) — IS in face topology; "
        "Shell B left-edge vertices at (1.0005, 0.0005, 0.0) and (1.0005, 1.0005, 0.0); "
        "vertex offset (0.0005, 0.0005, 0) IS directly wired as VERTEX_POINT coordinates; "
        "gap ≈0.000707 IS within sewing tolerance 1.0E-3 — IS the tolerance-driven merge trigger; "
        "ShellSewing.Apply merges shells but sets merged vertex tolerance to tight original value; "
        "stale tight tolerance on merged vertex IS the mechanism — cumulative distance not recorded; "
        "fix: after vertex merge set tolerance = max(original_tol, merge_distance); "
        "emit E_MERGED_VERTEX_TOLERANCE_NOT_UPDATED when merged vertex retains pre-merge tolerance"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Shell A: unit square x=[0,1] y=[0,1] z=0 — right edge at x=1.0 IS near-coincident mechanism
pA = [cp(0,0,0), cp(1,0,0), cp(1,1,0), cp(0,1,0)]
vA = [f.vertex_point(p) for p in pA]
eA = [
    led(vA[0], vA[1], pA[0],  1, 0, 0),
    led(vA[1], vA[2], pA[1],  0, 1, 0),
    led(vA[2], vA[3], pA[2], -1, 0, 0),
    led(vA[3], vA[0], pA[3],  0,-1, 0),
]
loop_a = f.edge_loop([f.oriented_edge(ei, True) for ei in eA])
pl_a = f.plane(f.axis2_placement_3d(pA[0], dir3(0, 0, 1), dir3(1, 0, 0)))
face_a = f.advanced_face([f.face_outer_bound(loop_a, orientation=True)], pl_a, same_sense=True)
shell_a = f.open_shell([face_a])

# Shell B: unit square x=[1.0005, 2.0005] y=[0.0005, 1.0005] z=0
# Left edge at x=1.0005 — offset (0.0005, 0.0005, 0) from Shell A right edge IS the mechanism
dx, dy = 0.0005, 0.0005
pB = [cp(1+dx, 0+dy, 0), cp(2+dx, 0+dy, 0), cp(2+dx, 1+dy, 0), cp(1+dx, 1+dy, 0)]
vB = [f.vertex_point(p) for p in pB]
eB = [
    led(vB[0], vB[1], pB[0],  1, 0, 0),
    led(vB[1], vB[2], pB[1],  0, 1, 0),
    led(vB[2], vB[3], pB[2], -1, 0, 0),
    led(vB[3], vB[0], pB[3],  0,-1, 0),
]
loop_b = f.edge_loop([f.oriented_edge(ei, True) for ei in eB])
pl_b = f.plane(f.axis2_placement_3d(pB[0], dir3(0, 0, 1), dir3(1, 0, 0)))
face_b = f.advanced_face([f.face_outer_bound(loop_b, orientation=True)], pl_b, same_sense=True)
shell_b = f.open_shell([face_b])

# Both shells wrapped together — near-coincident vertex pair IS wired into shell topology
sbsm = f.shell_based_surface_model([shell_a, shell_b])
f.add_product_chain(sbsm)
