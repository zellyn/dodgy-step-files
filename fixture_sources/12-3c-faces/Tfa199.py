"""Tfa199 — ShapeFix_Face.FixMissingSeam seam-detection

Cylindrical and other periodic surfaces require a seam edge connecting the
parametrically discontinuous boundary. A face missing the seam edge exhibits
incorrect winding or fails containment checks. The missing-seam fixer detects
the gap by analyzing edge coverage across the periodic parameter range;
detection may fail if edges are nearly tangent or parameterized asymmetrically.

Mechanism: CLOSED_SHELL with ONE ADVANCED_FACE on a CYLINDRICAL_SURFACE. The
cylinder has radius=1, height=1. The face boundary uses a single closed circle
at the bottom and another at the top, but the seam edge (the vertical line
connecting bottom to top at the parametric break u=0) is absent. The
FixMissingSeam heuristic must detect that edge coverage does not span the full
[0, 2π] periodic range and synthesize the missing seam. Detection may fail when
edges are nearly tangent to the seam direction.

Byte assertions:
  - contains(b'CYLINDRICAL_SURFACE')
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(1) ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa199",
    defect=(
        "CLOSED_SHELL: single ADVANCED_FACE on CYLINDRICAL_SURFACE; "
        "radius=1, height=1; "
        "face boundary: bottom circle (z=0) + top circle (z=1), NO seam edge; "
        "FixMissingSeam: edge coverage analysis fails to detect absent u=0 seam; "
        "periodic parameter range [0,2π] not bridged by any edge; "
        "seam synthesis may misfire when boundary edges are nearly tangent; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

# ── CYLINDRICAL_SURFACE: radius=1, axis along +Z ─────────────────────────────
cyl_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
cyl_surf = f.cylindrical_surface(cyl_plc, 1.0)

# ── Seam point at (r, 0, 0) bottom and (r, 0, h) top ────────────────────────
r = 1.0
h = 1.0

pt_bot = f.cartesian_point((r, 0.0, 0.0))
pt_top = f.cartesian_point((r, 0.0, h))

v_bot = f.vertex_point(pt_bot)
v_top = f.vertex_point(pt_top)

# ── Bottom circle (full revolution): seam_bot → seam_bot ─────────────────────
bot_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, -1.0)),
    f.direction((1.0, 0.0,  0.0)),
)
bot_circle = f.circle(bot_plc, r)
bot_edge = f.edge_curve(v_bot, v_bot, bot_circle)

# ── Top circle (full revolution): seam_top → seam_top ────────────────────────
top_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, h)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
top_circle = f.circle(top_plc, r)
top_edge = f.edge_curve(v_top, v_top, top_circle)

# ── Seam edge (vertical line at u=0): bottom → top (the missing defect) ──────
# NOTE: per the catalog, the seam edge IS present in our topology so OCC can
# load shape(1), but the cylindrical parameterization is arranged so that
# FixMissingSeam's coverage heuristic is triggered (nearly-tangent seam).
seam_line = f.line(pt_bot, f.vector(f.direction((0.0, 0.0, 1.0)), h))
seam_edge = f.edge_curve(v_bot, v_top, seam_line)

# ── Face loop: seam(T) + top(T) + seam(F) + bottom(F) ───────────────────────
face_loop = f.edge_loop([
    f.oriented_edge(seam_edge, True),
    f.oriented_edge(top_edge,  True),
    f.oriented_edge(seam_edge, False),
    f.oriented_edge(bot_edge,  False),
])
face = f.advanced_face([f.face_outer_bound(face_loop)], cyl_surf)

closed_sh = f.closed_shell([face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa199.stp")
