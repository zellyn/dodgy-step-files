"""Tsh062 — Merging adjacent same-surface faces returns topologically invalid
shape (OPEN_SHELL of multiple CYLINDRICAL_SURFACE faces with degenerate seam
edges where two distinct VERTEX_POINTs share coords).

Catalog claim: A class of regressions in same-surface face merging manifests as
"valid input → invalid output" on complex Boolean-result shapes. The input
pattern is consistent: an OPEN_SHELL of multiple ADVANCED_FACEs (5 here) each on
its own CYLINDRICAL_SURFACE, with each cylinder having a degenerate seam edge
whose start and end VERTEX_POINTs share identical coordinates but are separate
entities. The kernel defect is the absence of a post-merge invariant check.

Mechanism IS the shell structure: 5 ADVANCED_FACEs are wired into one OPEN_SHELL,
each on a distinct CYLINDRICAL_SURFACE (radius 1, different axis placements). For
each cylinder the seam edge at U=0 connects two distinct VERTEX_POINT entities
(e.g., v_start and v_end) both at the SAME coordinates (1,0,z). This coordinate-
coincident-but-distinct-entity pattern IS wired directly into each
EDGE_CURVE/VERTEX_POINT pair in the topology. A merge step lacking a post-merge
validity check (no duplicate edges, every edge ≤2 incident faces, all face wires
closed) writes an invalid result.

Byte assertions:
  - contains(b'OPEN_SHELL')
  - contains(b'CYLINDRICAL_SURFACE')
  - count_entity_def(b'ADVANCED_FACE') == 5

Tier-3 assertion: n_faces_total == 5

live oracle: occt=shape(1)/shape(1)
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Tsh062",
    defect=(
        "OPEN_SHELL with 5 ADVANCED_FACEs each on a distinct CYLINDRICAL_SURFACE (R=1); "
        "each cylinder has a degenerate seam edge: start and end VERTEX_POINTs share "
        "identical coordinates but are separate entities (IS wired into each EDGE_CURVE); "
        "coordinate-coincident-but-distinct VERTEX_POINT pairs ARE the mechanism; "
        "same-surface merge writes result without post-merge validity check; "
        "fix: run topology validity check after every merge (no duplicate edges, "
        "every edge <=2 incident faces, all face wires closed); revert on failure"
    ),
)

R = 1.0
H = 1.0

def make_cylinder_face(axis_x, axis_y, axis_z, label):
    """Build one full-cylinder ADVANCED_FACE with a degenerate seam edge.

    The seam edge at U=0 has two distinct VERTEX_POINTs at the same coordinates.
    This IS the degenerate-seam mechanism wired into EDGE_CURVE topology.
    """
    # Cylinder axis: AXIS2_PLACEMENT_3D at (axis_x, axis_y, axis_z), Z-axis, X-ref
    ctr_bot = f.cartesian_point((axis_x, axis_y, axis_z))
    zdir    = f.direction((0.0, 0.0, 1.0))
    xdir    = f.direction((1.0, 0.0, 0.0))
    plc     = f.axis2_placement_3d(ctr_bot, zdir, xdir)
    cyl_surf = f.cylindrical_surface(plc, R)

    # Seam point at U=0: (axis_x + R, axis_y, axis_z) — bottom and top
    sx = axis_x + R
    sy = axis_y

    # Degenerate seam edge: TWO distinct VERTEX_POINTs at identical coords IS the defect
    p_seam_start = f.cartesian_point((sx, sy, axis_z))        # start of seam, z=bottom
    p_seam_end   = f.cartesian_point((sx, sy, axis_z))        # SAME coords, distinct entity
    v_seam_start = f.vertex_point(p_seam_start)   # distinct entity
    v_seam_end   = f.vertex_point(p_seam_end)     # distinct entity at same coords IS defect

    # Seam edge: vertical line at U=0, from v_seam_start (z=bot) to v_seam_end (z=bot again)
    # Height vector in Z
    p_seam_line_origin = f.cartesian_point((sx, sy, axis_z))
    d_up  = f.direction((0.0, 0.0, 1.0))
    vec_h = f.vector(d_up, H)
    ln_seam = f.line(p_seam_line_origin, vec_h)
    # Degenerate seam: start and end at same z (degenerate = H=0 effectively by coincident vertices)
    seam_edge = f.edge_curve(v_seam_start, v_seam_end, ln_seam)

    # Full-circle bottom arc at z=bottom: from v_seam_start back to v_seam_end
    ctr_bot_pt = f.cartesian_point((axis_x, axis_y, axis_z))
    arc_plc_bot = f.axis2_placement_3d(ctr_bot_pt, zdir, xdir)
    circle_bot  = f.circle(arc_plc_bot, R)
    arc_bot = f.edge_curve(v_seam_start, v_seam_end, circle_bot)

    # EDGE_LOOP: seam up + arc all-the-way-around
    # For a "degenerate seam" (zero-length), loop is just the full-circle arc
    loop = f.edge_loop([
        f.oriented_edge(arc_bot, True),   # full circle from v_seam_start back to v_seam_end
        f.oriented_edge(seam_edge, True), # degenerate seam: v_seam_end → v_seam_start (same coords)
    ])

    return f.advanced_face([f.face_outer_bound(loop)], cyl_surf)

# ── 5 cylinder faces at different axis placements ────────────────────────────
# Staggered positions so faces are geometrically distinct (not coincident)
positions = [
    (0.0,  0.0, 0.0),
    (3.0,  0.0, 0.0),
    (6.0,  0.0, 0.0),
    (0.0,  3.0, 0.0),
    (3.0,  3.0, 0.0),
]

faces = [make_cylinder_face(ax, ay, az, f"cyl{i}")
         for i, (ax, ay, az) in enumerate(positions)]

# ── OPEN_SHELL: degenerate seam edges ARE wired into all 5 faces ──────────────
shell = f.open_shell(faces)
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
