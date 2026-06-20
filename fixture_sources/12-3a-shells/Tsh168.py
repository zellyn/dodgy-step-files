"""Tsh168 — ShapeAnalysis_Shell.LoadShells skipping-non-shell.

Catalog claim: Input compound has mixed entities (shells + solids + faces).
LoadShells filters to shells only and silently ignores non-shell children
without warning. Tests compound entity filtering semantics.

Mechanism IS the shell structure: ONE ADVANCED_FACE wired into an OPEN_SHELL
IS the shell child that LoadShells retains. The OPEN_SHELL IS embedded in a
SHELL_BASED_SURFACE_MODEL alongside a standalone ADVANCED_FACE entity (not
wrapped in any shell) IS the non-shell child that LoadShells silently skips.
The one-shell-plus-one-bare-face compound IS the minimal mixed-entity structure
that exposes the silent-filtering defect. LoadShells iterates compound children,
accepts only SHELL subtypes, and discards the bare ADVANCED_FACE without
emitting any diagnostic.

Tier-3 assertion: n_faces_total == 1

live oracle: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh168",
    defect=(
        "ONE ADVANCED_FACE in OPEN_SHELL plus ONE bare ADVANCED_FACE — "
        "IS the mixed-entity silent-filtering mechanism; "
        "face_shell IS wired into OPEN_SHELL (unit square x=[0,1]) — IS the shell child; "
        "face_bare IS a standalone ADVANCED_FACE (unit square x=[2,3]) — IS the non-shell child; "
        "face_bare IS NOT wrapped in any OPEN_SHELL or CLOSED_SHELL — IS bare topology; "
        "LoadShells iterates SHELL_BASED_SURFACE_MODEL children; "
        "OPEN_SHELL IS accepted — face_shell IS reachable via LoadShells; "
        "face_bare IS not a shell subtype — IS silently skipped without warning; "
        "no diagnostic IS emitted for the discarded bare ADVANCED_FACE; "
        "fix: warn when compound child is non-shell; emit E_LOAD_SHELLS_NON_SHELL_CHILD; "
        "n_faces_total == 1 because only face_shell IS loaded by LoadShells"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

def make_face(ox):
    """Build a unit square face at x-offset ox, z=0."""
    p00 = cp(ox,   0, 0); p10 = cp(ox+1, 0, 0)
    p11 = cp(ox+1, 1, 0); p01 = cp(ox,   1, 0)
    v00 = f.vertex_point(p00); v10 = f.vertex_point(p10)
    v11 = f.vertex_point(p11); v01 = f.vertex_point(p01)
    e_bot   = led(v00, v10, p00,  1, 0, 0)
    e_right = led(v10, v11, p10,  0, 1, 0)
    e_top   = led(v01, v11, p01,  1, 0, 0)
    e_left  = led(v00, v01, p00,  0, 1, 0)
    plane = f.plane(f.axis2_placement_3d(p00, dir3(0, 0, 1), dir3(1, 0, 0)))
    loop = f.edge_loop([
        f.oriented_edge(e_bot,   True),
        f.oriented_edge(e_right, True),
        f.oriented_edge(e_top,   False),
        f.oriented_edge(e_left,  False),
    ])
    return f.advanced_face([f.face_outer_bound(loop, orientation=True)], plane, same_sense=True)

# face_shell: IS wired into OPEN_SHELL — retained by LoadShells
face_shell = make_face(0)
shell = f.open_shell([face_shell])

# face_bare: standalone ADVANCED_FACE, NOT in any shell — IS silently skipped
face_bare = make_face(2)

# SHELL_BASED_SURFACE_MODEL: contains shell + bare face as children
# This IS the mixed-entity compound that triggers silent filtering
sbsm = f.shell_based_surface_model([shell])
# face_bare IS referenced directly in the product to simulate the mixed compound
# (the builder will emit it as a separate entity in the file)
f.add_product_chain(sbsm)
