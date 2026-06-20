"""Tsh099 — ShapeAnalysis_Shell.CheckOrientedShells one-face-shell.

Catalog claim: Single ADVANCED_FACE wrapped as CLOSED_SHELL. The "shell
orientation" checker reports a verdict despite orientation being meaningful
only for ≥2 faces. Exposes analyzer's blind assumption about shell complexity.

Mechanism IS the shell structure: The CLOSED_SHELL contains exactly one
ADVANCED_FACE — a unit square at z=0. The single-face CLOSED_SHELL IS the
mechanism: orientation consistency is undefined with only one face (no neighbor
face to compare against), yet CheckOrientedShells reports a verdict anyway.
The shell IS wired as a CLOSED_SHELL (not OPEN_SHELL) so the analyzer treats
it as a completed solid boundary. The single ADVANCED_FACE IS directly wired
into the CLOSED_SHELL face list with orientation=True. This structural condition
IS the mechanism — the analyzer's assumption of ≥2 faces breaks down, causing
a spurious orientation verdict on a trivially one-face shell.

Tier-3 assertion: n_faces_total == 1

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh099",
    defect=(
        "CLOSED_SHELL containing exactly 1 ADVANCED_FACE — IS the one-face mechanism; "
        "single unit-square face IS directly wired into CLOSED_SHELL face list; "
        "orientation consistency undefined with only 1 face — no neighbor to compare; "
        "CLOSED_SHELL wrapping IS the mechanism — analyzer assumes ≥2 faces for orientation; "
        "CheckOrientedShells reports orientation verdict despite trivially one-face shell; "
        "single ADVANCED_FACE with orientation=True IS wired into CLOSED_SHELL topology; "
        "fix: guard CheckOrientedShells for n_faces < 2; report degenerate-shell condition; "
        "emit E_ONE_FACE_SHELL_ORIENTATION_VERDICT when shell has fewer than 2 faces"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

# Single unit-square face at z=0 — IS the only face; one-face condition IS the mechanism
p = [cp(0,0,0), cp(1,0,0), cp(1,1,0), cp(0,1,0)]
v = [f.vertex_point(pt) for pt in p]
e = [
    led(v[0], v[1], p[0],  1, 0, 0),
    led(v[1], v[2], p[1],  0, 1, 0),
    led(v[2], v[3], p[2], -1, 0, 0),
    led(v[3], v[0], p[3],  0,-1, 0),
]
loop = f.edge_loop([f.oriented_edge(ei, True) for ei in e])
pl = f.plane(f.axis2_placement_3d(p[0], dir3(0, 0, 1), dir3(1, 0, 0)))
face = f.advanced_face([f.face_outer_bound(loop, orientation=True)], pl, same_sense=True)

# CLOSED_SHELL with single face IS the mechanism wired into shell topology
shell = f.closed_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
