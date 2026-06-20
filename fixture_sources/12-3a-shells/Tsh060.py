"""Tsh060 — Same-surface face merge runs quadratically across disjoint shells.

Catalog claim: A compound containing N independent shells is processed for
adjacent same-surface face merging; algorithmic complexity is O(N²) in face
count across all shells because candidate-pair iteration runs over the whole
compound rather than per-shell. For N=100 shells with ~20 faces each, runtime
is hours. Fixture uses 8 disjoint single-face OPEN_SHELLs.

Mechanism IS the shell structure: exactly 8 disjoint OPEN_SHELLs, each
containing exactly one unit-square ADVANCED_FACE on a PLANE, are placed as
independent shells in a SHELL_BASED_SURFACE_MODEL. The N-independent-shells
compound IS wired directly into the topology. A same-surface merge that iterates
all-pairs across disconnected shells (rather than restricting to pairs sharing an
edge) exposes the quadratic pathology. No faces share edges or vertices — the
disjointness IS the mechanism.

Byte assertions:
  - count_entity_def(b'OPEN_SHELL') == 8
  - count_entity_def(b'ADVANCED_FACE') == 8

Tier-3 assertion: shape_null == True

live oracle: occt=empty/empty
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh060",
    defect=(
        "SHELL_BASED_SURFACE_MODEL with 8 disjoint OPEN_SHELLs each containing one ADVANCED_FACE; "
        "8 independent shells IS wired into SHELL_BASED_SURFACE_MODEL as disjoint compound; "
        "no shared edges or vertices between shells (disjointness IS the mechanism); "
        "same-surface merge iterates all-pairs across compound rather than per-shell; "
        "O(N^2) candidate-pair iteration exposes quadratic complexity; "
        "fix: restrict candidate pairs to faces sharing an edge (connectivity grouping)"
    ),
)

def make_unit_face(x_offset, y_offset):
    """Build one unit-square ADVANCED_FACE at (x_offset, y_offset, 0) on a PLANE."""
    x0, y0 = float(x_offset), float(y_offset)
    x1, y1 = x0 + 1.0, y0 + 1.0

    p00 = f.cartesian_point((x0, y0, 0.0))
    p10 = f.cartesian_point((x1, y0, 0.0))
    p11 = f.cartesian_point((x1, y1, 0.0))
    p01 = f.cartesian_point((x0, y1, 0.0))

    v00 = f.vertex_point(p00)
    v10 = f.vertex_point(p10)
    v11 = f.vertex_point(p11)
    v01 = f.vertex_point(p01)

    def line_edge(va, vb, ps, dx, dy, dz):
        d = f.direction((float(dx), float(dy), float(dz)))
        vec = f.vector(d, 1.0)
        ln = f.line(ps, vec)
        return f.edge_curve(va, vb, ln)

    e_bot = line_edge(v00, v10, p00,  1, 0, 0)
    e_rgt = line_edge(v10, v11, p10,  0, 1, 0)
    e_top = line_edge(v11, v01, p11, -1, 0, 0)
    e_lft = line_edge(v01, v00, p01,  0,-1, 0)

    loop = f.edge_loop([
        f.oriented_edge(e_bot, True),
        f.oriented_edge(e_rgt, True),
        f.oriented_edge(e_top, True),
        f.oriented_edge(e_lft, True),
    ])

    orig = f.cartesian_point((x0, y0, 0.0))
    zdir = f.direction((0.0, 0.0, 1.0))
    xdir = f.direction((1.0, 0.0, 0.0))
    plc  = f.axis2_placement_3d(orig, zdir, xdir)
    plane = f.plane(plc)

    return f.advanced_face([f.face_outer_bound(loop)], plane)

# ── 8 disjoint unit-square faces on a 4×2 grid (3-unit spacing = no shared edges) ──
# Spacing of 3 units ensures no two faces share vertices or edges (IS the mechanism).
positions = [
    (0, 0), (3, 0), (6, 0), (9, 0),
    (0, 3), (3, 3), (6, 3), (9, 3),
]

shells = []
for (xi, yi) in positions:
    face = make_unit_face(xi, yi)
    shell = f.open_shell([face])   # each face in its own OPEN_SHELL
    shells.append(shell)

# ── SHELL_BASED_SURFACE_MODEL: 8 disjoint shells IS the compound topology ─────
sbsm = f.shell_based_surface_model(shells)
f.add_product_chain(sbsm)
