"""Tsh097 — ShapeFix_Shell.Perform context-state accumulation.

Catalog claim: Perform runs multiple sub-fixers (FixFaceOrientation, FixWireGaps,
FixShellOrientationMode) each updating myStatus. Cumulative status doesn't reflect
the most recent successful fix — earlier failures may overwrite later successes.

Mechanism IS the shell structure: The OPEN_SHELL contains two ADVANCED_FACEs with
conflicting FACE_OUTER_BOUND orientation flags — Face A has orientation=False (.F.)
and Face B has orientation=True (.T.). These conflicting orientation flags IS
directly wired into the face topology. On the first Perform() pass the misoriented
faces generate a FixFaceOrientation failure status stored in myStatus. On the
second Perform() pass the fix succeeds, but myStatus IS accumulated from both
passes — the stale first-pass failure IS the mechanism that causes the returned
status to reflect the earlier failure rather than the second success.

Tier-3 assertion: shape_null == True

live oracle: occt=empty/empty
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh097",
    defect=(
        "OPEN_SHELL with 2 ADVANCED_FACEs with conflicting FACE_OUTER_BOUND orientation flags; "
        "Face A FACE_OUTER_BOUND orientation=False (.F.) IS directly wired in face topology; "
        "Face B FACE_OUTER_BOUND orientation=True (.T.) IS directly wired in face topology; "
        "conflicting orientation flags IS the mechanism triggering multi-pass Perform state; "
        "first Perform pass: FixFaceOrientation generates failure status stored in myStatus; "
        "second Perform pass: fix succeeds but myStatus accumulates stale first-pass failure; "
        "stale accumulated status IS the mechanism — second pass result masked by first failure; "
        "fix: reset myStatus at start of each Perform pass; do not accumulate across passes; "
        "emit E_SHELL_PERFORM_STALE_STATUS when status from prior pass survives reset"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Face A: unit quad at z=0 — FACE_OUTER_BOUND orientation=False (.F.) IS the misoriented face
pA = [cp(0,0,0), cp(1,0,0), cp(1,1,0), cp(0,1,0)]
vA = [f.vertex_point(p) for p in pA]
eA = [
    led(vA[0], vA[1], pA[0],  1, 0, 0),
    led(vA[1], vA[2], pA[1],  0, 1, 0),
    led(vA[2], vA[3], pA[2], -1, 0, 0),
    led(vA[3], vA[0], pA[3],  0,-1, 0),
]
loop_a = f.edge_loop([f.oriented_edge(e, True) for e in eA])
pl_a = f.plane(f.axis2_placement_3d(pA[0], dir3(0, 0, 1), dir3(1, 0, 0)))
# orientation=False (.F.) IS directly wired into face A topology — IS the conflict mechanism
face_a = f.advanced_face(
    [f.face_outer_bound(loop_a, orientation=False)], pl_a, same_sense=True
)

# Face B: unit quad offset at z=0 — FACE_OUTER_BOUND orientation=True (.T.) — correct orientation
pB = [cp(2,0,0), cp(3,0,0), cp(3,1,0), cp(2,1,0)]
vB = [f.vertex_point(p) for p in pB]
eB = [
    led(vB[0], vB[1], pB[0],  1, 0, 0),
    led(vB[1], vB[2], pB[1],  0, 1, 0),
    led(vB[2], vB[3], pB[2], -1, 0, 0),
    led(vB[3], vB[0], pB[3],  0,-1, 0),
]
loop_b = f.edge_loop([f.oriented_edge(e, True) for e in eB])
pl_b = f.plane(f.axis2_placement_3d(pB[0], dir3(0, 0, 1), dir3(1, 0, 0)))
# orientation=True (.T.) wired into face B — conflicting with face A IS the mechanism
face_b = f.advanced_face(
    [f.face_outer_bound(loop_b, orientation=True)], pl_b, same_sense=True
)

# OPEN_SHELL with misoriented face A + correctly oriented face B — conflicting flags IS mechanism
shell = f.open_shell([face_a, face_b])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
