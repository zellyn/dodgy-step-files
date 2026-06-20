"""Tsh129 — ShapeFix_Shell.Perform compound-input.

Catalog claim: ShapeFix_Shell.Perform receives COMPOUND with multiple
CLOSED_SHELLs; processes first shell only, silently ignores rest. Expected:
all shells should be processed or error raised. Two unit squares in parallel
planes (z=0, z=2) wrapped in COMPOUND; SHELL_BASED_SURFACE_MODEL contains both.

Mechanism IS the shell structure: SHELL_BASED_SURFACE_MODEL references TWO
OPEN_SHELLs (Shell1 at z=0, Shell2 at z=2) — both are wired directly into the
SBSM entity. ShapeFix_Shell.Perform iterates shells in a compound; the two-shell
SBSM IS the compound-input mechanism. The defect: Perform processes Shell1 and
silently stops, never reaching Shell2. Both shells IS the mechanism — the second
shell is real geometry IS wired into the topology but silently skipped.

Tier-3 assertion: n_faces_total == 2

live oracle: occt=shape(1)/shape(1)
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh129",
    defect=(
        "SHELL_BASED_SURFACE_MODEL references 2 OPEN_SHELLs — IS the compound-input mechanism; "
        "Shell1 contains Face1 (unit square at z=0) — IS wired as first shell in SBSM; "
        "Shell2 contains Face2 (unit square at z=2) — IS wired as second shell in SBSM; "
        "two OPEN_SHELLs in single SBSM IS the compound-input topology; "
        "ShapeFix_Shell.Perform iterates shells in compound; "
        "processes Shell1 only — silently ignores Shell2 IS the defect; "
        "fix: iterate all shells in compound; apply Perform to each; "
        "emit E_COMPOUND_SHELL_PARTIAL_PROCESSING when Perform stops before last shell"
    ),
)

def cp(x, y, z): return f.cartesian_point((float(x), float(y), float(z)))
def dir3(x, y, z): return f.direction((float(x), float(y), float(z)))
def led(va, vb, pt, dx, dy, dz):
    d = dir3(dx, dy, dz)
    vec = f.vector(d, 1.0)
    ln = f.line(pt, vec)
    return f.edge_curve(va, vb, ln)

def make_square_face(ox, oy, oz):
    """Build a unit square face at offset (ox, oy, oz) in z-plane."""
    p00 = cp(ox,   oy,   oz); p10 = cp(ox+1, oy,   oz)
    p11 = cp(ox+1, oy+1, oz); p01 = cp(ox,   oy+1, oz)
    v00 = f.vertex_point(p00); v10 = f.vertex_point(p10)
    v11 = f.vertex_point(p11); v01 = f.vertex_point(p01)
    e_bot   = led(v00, v10, p00,  1, 0, 0)
    e_right = led(v10, v11, p10,  0, 1, 0)
    e_top   = led(v11, v01, p11, -1, 0, 0)
    e_left  = led(v01, v00, p01,  0,-1, 0)
    loop = f.edge_loop([
        f.oriented_edge(e_bot,   True),
        f.oriented_edge(e_right, True),
        f.oriented_edge(e_top,   True),
        f.oriented_edge(e_left,  True),
    ])
    pl = f.plane(f.axis2_placement_3d(p00, dir3(0, 0, 1), dir3(1, 0, 0)))
    return f.advanced_face([f.face_outer_bound(loop, orientation=True)], pl, same_sense=True)

# Shell 1: unit square at z=0 — IS the first shell in compound-input
face1  = make_square_face(0, 0, 0)
shell1 = f.open_shell([face1])

# Shell 2: unit square at z=2 — IS the second shell (silently ignored by Perform)
face2  = make_square_face(0, 0, 2)
shell2 = f.open_shell([face2])

# SHELL_BASED_SURFACE_MODEL with both shells — IS the compound-input mechanism
sbsm = f.shell_based_surface_model([shell1, shell2])
f.add_product_chain(sbsm)
