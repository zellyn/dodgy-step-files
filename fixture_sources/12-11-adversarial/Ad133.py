r"""Ad133 — OCCT #1327 / FreeCAD #30266: OCCT 8.0 STEP writer drops curved-surface entities on re-export.

Catalog claim: STEP file with a single `ADVANCED_FACE` on a
`CYLINDRICAL_SURFACE` (a valid 90-degree cylindrical patch). The input
bytes are perfectly readable. The defect surfaces downstream:
`write → reread` through OCCT 8.0's `STEPControl_Writer` regression
silently omits the `CYLINDRICAL_SURFACE` entity from the output, so a
downstream slicer that consumes the re-exported STEP produces a
completely wrong toolpath because the curved boundary vanished.

OCCT 7.x writes the same source shape correctly; OCCT 8.0 broke the
writer path used by FreeCAD (the C++ `STEPControl_Writer` API path;
DRAW does not reproduce). The regression is version-specific to
OCCT 8.0.

Since we cannot run the pre-fix OCCT 8.0 writer inside CI, this fixture
encodes the INPUT file — a valid cylindrical `ADVANCED_FACE` — and notes
that the defect surfaces only after `write → reread → compare-with-input`
against an OCCT 8.0 kernel.

Source: https://github.com/Open-Cascade-SAS/OCCT/issues/1327,
https://github.com/FreeCAD/FreeCAD/issues/30266. B4 wave-8 DEF-DDD.
Confidence: MEDIUM — mechanism confirmed by tracker but exact writer
code path is not root-caused in the reports. LGPL-clean — pattern only,
no upstream bytes copied.

Byte assertions:
  contains(b'CYLINDRICAL_SURFACE')
  contains(b'ADVANCED_FACE')
  contains(b'EDGE_LOOP')
Tier-3: shape_null == False
"""
from step_corpus.step_builder import StepFile
import math

f = StepFile(
    catalog_id="Ad133",
    defect=(
        "OCCT #1327 / FreeCAD #30266 writer-regression INPUT: single "
        "ADVANCED_FACE on a CYLINDRICAL_SURFACE (a 90-degree curved patch, "
        "radius 5.0, axis Z, from z=0 to z=10); input bytes are perfectly "
        "readable; defect surfaces downstream — OCCT 8.0's STEPControl_Writer "
        "regression silently omits CYLINDRICAL_SURFACE entities on re-export "
        "via the C++ API path (as FreeCAD uses); OCCT 7.x writes the same "
        "shape correctly; a downstream slicer that consumes the re-exported "
        "STEP produces completely wrong toolpaths because the curved boundary "
        "vanished; DRAW-path does not reproduce; version-specific to OCCT 8.0; "
        "detected only on write→reread→compare-with-input; DEF-DDD; "
        "SHELL_BASED_SURFACE_MODEL IS model entity — OCC (reading input) "
        "yields shape(1)"
    ),
)

# ── CYLINDRICAL_SURFACE (radius=5.0, axis along +Z, origin at (0,0,0)) ────────
origin = f.cartesian_point((0.0, 0.0, 0.0))
z_axis = f.direction((0.0, 0.0, 1.0))
x_axis = f.direction((1.0, 0.0, 0.0))
cyl_placement = f.axis2_placement_3d(origin, z_axis, x_axis)
cylinder = f.cylindrical_surface(cyl_placement, 5.0, name="ad133_cylinder")

# ── 90° cylindrical patch: (u ∈ [0, π/2], v ∈ [0, 10]) ───────────────────────
# Corner points on the cylinder surface: r=5, angles 0 and π/2, z=0 and z=10.
R = 5.0
H = 10.0
p_00 = f.cartesian_point((R,             0.0,             0.0))  # (u=0, v=0)
p_10 = f.cartesian_point((0.0,           R,               0.0))  # (u=π/2, v=0)
p_11 = f.cartesian_point((0.0,           R,               H))    # (u=π/2, v=H)
p_01 = f.cartesian_point((R,             0.0,             H))    # (u=0, v=H)

v_00 = f.vertex_point(p_00)
v_10 = f.vertex_point(p_10)
v_11 = f.vertex_point(p_11)
v_01 = f.vertex_point(p_01)

# ── Bottom arc (v=0, u: 0 → π/2) — a CIRCLE at z=0, radius R, from angle 0 to π/2
arc_bot_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
arc_bot = f.circle(arc_bot_plc, R, name="ad133_bot_arc")
e_bot = f.edge_curve(v_00, v_10, arc_bot)

# ── Right vertical edge (u=π/2, v: 0 → H) — a straight LINE up +Z at (0,R,·)
d_up = f.direction((0.0, 0.0, 1.0))
line_right = f.line(p_10, f.vector(d_up, H))
e_right = f.edge_curve(v_10, v_11, line_right)

# ── Top arc (v=H, u: π/2 → 0) — a CIRCLE at z=H, radius R, from π/2 to 0
arc_top_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, H)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
arc_top = f.circle(arc_top_plc, R, name="ad133_top_arc")
e_top = f.edge_curve(v_11, v_01, arc_top)

# ── Left vertical edge (u=0, v: H → 0) — a straight LINE down -Z at (R,0,·)
d_down = f.direction((0.0, 0.0, -1.0))
line_left = f.line(p_01, f.vector(d_down, H))
e_left = f.edge_curve(v_01, v_00, line_left)

# ── Assemble the edge loop for the ADVANCED_FACE ─────────────────────────────
loop = f.edge_loop([
    f.oriented_edge(e_bot,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_left,  True),
])
fob = f.face_outer_bound(loop)

# ── ADVANCED_FACE on the CYLINDRICAL_SURFACE ─────────────────────────────────
# Byte assertion: contains(b'CYLINDRICAL_SURFACE')
# Byte assertion: contains(b'ADVANCED_FACE')
# Byte assertion: contains(b'EDGE_LOOP')
face = f.advanced_face([fob], cylinder, name="ad133_cyl_face")
shell = f.open_shell([face], name="ad133_shell")
sbsm = f.shell_based_surface_model([shell], name="ad133_sbsm")
f.add_product_chain(sbsm, mode="surface_shape")
