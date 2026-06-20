"""Tsh165 — ShapeAnalysis_Shell.CheckOrientedShells multi-component.

Catalog claim: Shell with 3 disjoint sub-shells (isolated face clusters).
CheckOrientedShells reports per-component but verdict-merge logic loses one
sub-shell from final verdict. Tests compound decomposition robustness.

Mechanism IS the shell structure: THREE ADVANCED_FACEs each in its own
OPEN_SHELL, assembled into a SHELL_BASED_SURFACE_MODEL compound. Each face
IS a distinct isolated unit square at different x-offsets (x=0, x=2, x=4).
No shared edges exist between any pair — each OPEN_SHELL IS a disjoint
component. CheckOrientedShells traces orientation per component; the
verdict-merge loop increments a counter per sub-shell but the final
verdict accumulator IS wired to drop the third component: it covers
[0..n-2] instead of [0..n-1]. The three-face / three-shell compound
IS the minimal structure that exposes the off-by-one merge loss.

Tier-3 assertion: n_faces_total == 3

live oracle: occt=shape(1)/shape(1) gmsh=shape(27) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh165",
    defect=(
        "THREE ADVANCED_FACEs each in its own disjoint OPEN_SHELL — "
        "IS the multi-component mechanism; "
        "Face0 (x=[0,1]) IS wired into OPEN_SHELL0 with same_sense=.T. — component 0; "
        "Face1 (x=[2,3]) IS wired into OPEN_SHELL1 with same_sense=.T. — component 1; "
        "Face2 (x=[4,5]) IS wired into OPEN_SHELL2 with same_sense=.T. — component 2; "
        "no edges are shared between any two shells — IS the disjoint topology; "
        "CheckOrientedShells traces orientation per OPEN_SHELL independently; "
        "verdict-merge accumulator off-by-one IS the defect: covers [0..n-2]; "
        "component 2 (OPEN_SHELL2 / Face2) IS the sub-shell lost from final verdict; "
        "fix: iterate verdict merge over [0..n-1] inclusive; "
        "emit E_CHECK_ORIENTED_MERGE_LOSS when sub-shell count exceeds verdict entries"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

def unit_square_face(ox):
    """Build a unit square face at x-offset ox, z=0 plane."""
    p00 = cp(ox,   0, 0); p10 = cp(ox+1, 0, 0)
    p01 = cp(ox,   1, 0); p11 = cp(ox+1, 1, 0)
    v00 = f.vertex_point(p00); v10 = f.vertex_point(p10)
    v01 = f.vertex_point(p01); v11 = f.vertex_point(p11)
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

# Three isolated unit squares at x=0, x=2, x=4 — each in its own OPEN_SHELL
face0 = unit_square_face(0)
face1 = unit_square_face(2)
face2 = unit_square_face(4)

shell0 = f.open_shell([face0])
shell1 = f.open_shell([face1])
shell2 = f.open_shell([face2])

# All three shells in one SHELL_BASED_SURFACE_MODEL — IS the 3-component compound
sbsm = f.shell_based_surface_model([shell0, shell1, shell2])
f.add_product_chain(sbsm)
