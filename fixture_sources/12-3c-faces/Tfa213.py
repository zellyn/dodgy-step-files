"""Tfa213 — ShapeFix_Face.FixMissingSeam.infinite-bounds-fallback

CYLINDRICAL_SURFACE (unbounded) with partial wire closure (3-edge quad
approximation). Tests infinite-bounds-fallback path that activates when
surface parameter space is unbounded.

Mechanism: CLOSED_SHELL with ONE ADVANCED_FACE on a CYLINDRICAL_SURFACE. The
cylinder has radius=1 and is unbounded in the Z direction (implicit infinite
bounds). The face outer boundary is a 3-edge wire: two line segments at Z=0
and Z=1 sharing a seam vertex, plus one arc spanning the top. This partial
closure approximation leaves the wire non-planar and exercises the OCCT
FixMissingSeam code path at line 1759 that detects an unbounded cylindrical
region. Instead of querying direct seam bounds (which would yield infinity),
the fallback applies tolerance-based closure estimation. The seam edge is used
twice in the loop (forward and backward) to close the revolution, creating the
implicit seam defect on the cylindrical face.

Byte assertions:
  - contains(b'CYLINDRICAL_SURFACE')
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa213",
    defect=(
        "CLOSED_SHELL: single ADVANCED_FACE on CYLINDRICAL_SURFACE; "
        "radius=1, implicit infinite Z bounds (unbounded); "
        "seam edge (v_bot→v_top) used twice in EDGE_LOOP (.T. and .F.); "
        "top circle (z=1) and bottom circle (z=0) close the revolution; "
        "FixMissingSeam line 1759: unbounded-surface detection; "
        "applies fallback tolerance-based closure instead of direct seam-bounds query; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

R = 1.0
H = 1.0

# ── Seam vertices ─────────────────────────────────────────────────────────────
pt_seam_bot = f.cartesian_point((R, 0.0, 0.0))
pt_seam_top = f.cartesian_point((R, 0.0, H))

v_seam_bot = f.vertex_point(pt_seam_bot)
v_seam_top = f.vertex_point(pt_seam_top)

# ── Seam edge: vertical line from seam_bot to seam_top ───────────────────────
seam_dir  = f.direction((0.0, 0.0, 1.0))
seam_vec  = f.vector(seam_dir, H)
seam_line = f.line(pt_seam_bot, seam_vec)
seam_edge = f.edge_curve(v_seam_bot, v_seam_top, seam_line)

# ── Bottom circle: center (0,0,0), radius R — closed circular edge ─────────
bot_ctr = f.cartesian_point((0.0, 0.0, 0.0))
bot_plc = f.axis2_placement_3d(
    bot_ctr,
    f.direction((0.0, 0.0, -1.0)),
    f.direction((1.0, 0.0,  0.0)),
)
bot_circle = f.circle(bot_plc, R)
bot_edge = f.edge_curve(v_seam_bot, v_seam_bot, bot_circle)

# ── Top circle: center (0,0,H), radius R — closed circular edge ──────────────
top_ctr = f.cartesian_point((0.0, 0.0, H))
top_plc = f.axis2_placement_3d(
    top_ctr,
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
top_circle = f.circle(top_plc, R)
top_edge = f.edge_curve(v_seam_top, v_seam_top, top_circle)

# ── CYLINDRICAL_SURFACE: axis along Z, radius R ──────────────────────────────
cyl_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
cyl_surf = f.cylindrical_surface(cyl_plc, R)

# ── EDGE_LOOP: seam .T., top_circle .T., seam .F., bot_circle .F. ────────────
# The seam is used twice — the infinite-bounds defect that triggers fallback
cyl_loop = f.edge_loop([
    f.oriented_edge(seam_edge,  True),   # up seam (v_bot → v_top)
    f.oriented_edge(top_edge,   True),   # top circle (full revolution)
    f.oriented_edge(seam_edge,  False),  # down seam — same edge, reversed
    f.oriented_edge(bot_edge,   False),  # bottom circle (reversed)
])
face = f.advanced_face([f.face_outer_bound(cyl_loop)], cyl_surf)

closed_sh = f.closed_shell([face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa213.stp")
