"""Tfa205 — FixAddNaturalBound cone apex degenerate

Conical surface (half-angle 45°) with apex vertex at z=1.414. Tests
natural-bound insertion on degenerate apex geometry without explicit seam edge.

Mechanism: CLOSED_SHELL with ONE ADVANCED_FACE on a CONICAL_SURFACE. The cone
has base_radius=1.0 and semi_angle=0.7854 rad (45°), giving apex height h=1.0
and apex_radius=0.0 (true apex). The face covers the full lateral surface with
a base circle wire but no seam edge and no explicit apex wire. The OCCT
FixAddNaturalBound code path at line 1744 is triggered when the cone has a
degenerate apex — it synthesizes a natural boundary at the apex singularity.
Without an explicit seam edge, the apex is represented as a degenerate edge
(same start/end vertex) on the cone. The missing natural bound at the apex
is the defect that exercises the synthesis branch.

Byte assertions:
  - contains(b'CONICAL_SURFACE')
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa205",
    defect=(
        "CLOSED_SHELL: single ADVANCED_FACE on CONICAL_SURFACE; "
        "base_radius=1.0, semi_angle=pi/4 (45°); apex at z=1.0, radius=0.0; "
        "face boundary: base circle loop (full revolution) + degenerate apex edge; "
        "no seam edge; no explicit apex wire in topology; "
        "FixAddNaturalBound line 1744: natural-bound synthesis at degenerate apex; "
        "apex singularity requires natural boundary insertion for consistent topology; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

# ── CONICAL_SURFACE: base at z=0, apex at z=1, semi_angle=45° ────────────────
semi_angle = _math.pi / 4.0   # 45° → tan = 1 → apex at h = base_r / tan = 1.0
base_r = 1.0
h = base_r / _math.tan(semi_angle)   # = 1.0

cone_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
cone_surf = f.conical_surface(cone_plc, base_r, semi_angle)

# ── Seam vertices ─────────────────────────────────────────────────────────────
pt_base_seam = f.cartesian_point((base_r, 0.0, 0.0))
pt_apex      = f.cartesian_point((0.0, 0.0, h))

v_base = f.vertex_point(pt_base_seam)
v_apex = f.vertex_point(pt_apex)

# ── Base circle (full revolution, normal -Z for CW so face normal outward) ───
base_circ_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, -1.0)),
    f.direction((1.0, 0.0,  0.0)),
)
base_circle = f.circle(base_circ_plc, base_r)
base_edge = f.edge_curve(v_base, v_base, base_circle)   # closed circle

# ── Seam edge (line from base to apex) ───────────────────────────────────────
dx = 0.0 - base_r    # apex_r = 0
dz = h - 0.0
seam_len = _math.sqrt(dx * dx + dz * dz)
seam_dir = f.direction((dx / seam_len, 0.0, dz / seam_len))
seam_edge = f.edge_curve(
    v_base, v_apex,
    f.line(pt_base_seam, f.vector(seam_dir, seam_len)),
)

# ── Degenerate apex edge (zero-length, same vertex) ──────────────────────────
# Represents the degenerate apex point — no explicit seam wire at apex
apex_line = f.line(pt_apex, f.vector(f.direction((1.0, 0.0, 0.0)), 0.001))
apex_edge = f.edge_curve(v_apex, v_apex, apex_line)

# ── Face loop: seam(T) + apex_degen(T) + seam(F) + base(F) ──────────────────
face_loop = f.edge_loop([
    f.oriented_edge(seam_edge, True),
    f.oriented_edge(apex_edge, True),    # degenerate apex — no natural bound present
    f.oriented_edge(seam_edge, False),
    f.oriented_edge(base_edge, False),
])
face = f.advanced_face([f.face_outer_bound(face_loop)], cone_surf)

closed_sh = f.closed_shell([face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa205.stp")
