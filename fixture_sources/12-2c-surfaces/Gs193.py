"""Gs193 — Fusion 360 → Creo circular chamfer: single 360° CONICAL_SURFACE with internal seam edge.

Catalog claim: STEP file matching Autodesk Fusion 360's output pattern
for a circular chamfer (a hole-edge chamfer on a plate). Fusion emits the
chamfer as one `ADVANCED_FACE` on a `CONICAL_SURFACE` covering the full
360° angular extent — the seam is represented by a single internal
`EDGE_CURVE` on the periodic boundary, referenced from the
`FACE_OUTER_BOUND`'s `EDGE_LOOP` twice (once forward, once reversed)
so the loop closes topologically on the periodic surface.

Source: https://community.ptc.com/t5/3D-Part-Assembly-Design/Circular-chamfer-import-faulty/td-p/27769
(PTC community post 27769 — MartinHanak's expert diagnosis). B4 wave-8
DEF-EEE. LGPL-clean — pattern only, no upstream bytes copied.

Mechanism: this is a producer-consumer convention mismatch. The single
360° periodic-conical-face encoding is topologically valid (the face
wraps around the seam via the internal edge referenced twice). Receivers
that require periodic surfaces to be split at 180° into two half-faces
cannot process the single-face encoding. Reported outcomes:
  - SolidWorks / FreeCAD / Rhino / ZW3D — accept.
  - PTC Creo Parametric — drops the chamfer with
    `CONICAL_SURFACE not processed`.

Byte assertions:
  contains(b'CONICAL_SURFACE')
  count_entity_def(b'ADVANCED_FACE') == 1
  count_entity_def(b'CONICAL_SURFACE') == 1
Tier-3 assertion: n_faces_total == 1
Expected: occt=shape(1)/shape(1) gmsh=shape(1) ifc=schema_n/a
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs193",
    defect=(
        "One ADVANCED_FACE on a CONICAL_SURFACE covering the full 360° angular "
        "extent (a circular chamfer on a hole+plate joint per Fusion 360's "
        "export convention), with the seam represented as a single internal "
        "EDGE_CURVE on the periodic boundary referenced twice from the "
        "FACE_OUTER_BOUND's EDGE_LOOP (once forward, once reversed); "
        "topologically valid on the periodic surface but breaks receivers that "
        "require periodic surfaces to be split at 180° into two half-faces; "
        "SolidWorks/FreeCAD/Rhino/ZW3D accept, PTC Creo Parametric drops the "
        "chamfer with 'CONICAL_SURFACE not processed'; producer-consumer "
        "convention mismatch; PTC community #27769 DEF-EEE; "
        "OCC accepts — yields shape(1)/shape(1) with one conical face"
    ),
)

# ── CONICAL_SURFACE — the chamfer surface, apex above, opens downward ─────────
# Chamfer geometry: a 45° cone tapering from radius 5 (top of hole rim) to
# radius 8 (chamfer outer edge on the plate top face). Half-angle 45°, apex
# above the plate; the chamfer face lives at v ∈ [v_lo, v_hi] on the cone
# where v_lo maps to the smaller radius and v_hi to the larger.
#
# CONICAL_SURFACE parameterization (STEP AP242):
#   position: axis2_placement_3d with origin at apex, +Z along axis
#   radius: R0 — the radius at the placement origin (v=0 reference)
#   semi_angle: half-angle of the cone
# We place the apex at z = z_apex above the plate and use the STEP
# CONICAL_SURFACE convention where positive v extends in the +Z direction
# with radius R0 at v=0.
HALF_ANGLE = math.pi / 4.0  # 45° chamfer
R0 = 6.5                     # reference radius at placement origin
TWO_PI = 2.0 * math.pi

cone_orig = f.cartesian_point((0.0, 0.0, 0.0))
cone_zdir = f.direction((0.0, 0.0, 1.0))
cone_xdir = f.direction((1.0, 0.0, 0.0))
cone_ax   = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs193_cone_ax',#{cone_orig.eid},"
    f"#{cone_zdir.eid},#{cone_xdir.eid})"
)
# Byte assertion: contains(b'CONICAL_SURFACE')
# Byte assertion: count_entity_def(b'CONICAL_SURFACE') == 1
cone = f._emit_raw(
    f"CONICAL_SURFACE('gs193_chamfer',#{cone_ax.eid},{R0:.10f},"
    f"{HALF_ANGLE:.10f})"
)

# ── Parametric context for pcurves on the cone ───────────────────────────────
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Seam vertices at the periodic boundary u=0 / u=2π ────────────────────────
# The seam edge runs from v=v_lo to v=v_hi at u=0 (equivalently u=2π on the
# periodic surface). Both vertices sit at the same 3D locations regardless of
# whether we approach from u=0 or u=2π.
V_LO = -1.5   # smaller-radius end of chamfer
V_HI =  1.5   # larger-radius end of chamfer

cos_ha = math.cos(HALF_ANGLE)
sin_ha = math.sin(HALF_ANGLE)

def cone_pt(u, v):
    # STEP CONICAL_SURFACE parameterization:
    #   r(u,v) = R0 + v * sin(ha)   [radius at parameter v]
    #   x = r * cos(u), y = r * sin(u), z = v * cos(ha)
    # (Using the STEP convention where cos_ha and sin_ha may be swapped for
    #  slant-height vs. axial-height; the exact metric doesn't matter for the
    #  entity presence — only that the face is topologically wired.)
    r = R0 + v * sin_ha
    return (r * math.cos(u), r * math.sin(u), v * cos_ha)

# Seam vertices at u=0
p_seam_lo = f.cartesian_point(cone_pt(0.0, V_LO))
p_seam_hi = f.cartesian_point(cone_pt(0.0, V_HI))
v_seam_lo = f.vertex_point(p_seam_lo)
v_seam_hi = f.vertex_point(p_seam_hi)

# ── The seam EDGE_CURVE: an internal edge at u=0 (=u=2π) on the periodic cone ─
# Geometry: a straight line in 3D from (R_lo, 0, V_LO*cos_ha) to (R_hi, 0,
# V_HI*cos_ha) — a slant-height ruling of the cone at u=0.
# pcurve: a straight line in UV from (0, V_LO) to (0, V_HI).
seam_3d_start = cone_pt(0.0, V_LO)
seam_3d_end   = cone_pt(0.0, V_HI)
sd3 = f.direction((
    seam_3d_end[0] - seam_3d_start[0],
    seam_3d_end[1] - seam_3d_start[1],
    seam_3d_end[2] - seam_3d_start[2],
))
seam_len_3d = math.sqrt(
    (seam_3d_end[0] - seam_3d_start[0]) ** 2
    + (seam_3d_end[1] - seam_3d_start[1]) ** 2
    + (seam_3d_end[2] - seam_3d_start[2]) ** 2
)
sp3 = f.cartesian_point(seam_3d_start)
sv3 = f.vector(sd3, seam_len_3d)
sl3 = f.line(sp3, sv3)

sp2 = f.cartesian_point((0.0, V_LO))
sd2 = f.direction((0.0, 1.0))
sv2 = f.vector(sd2, V_HI - V_LO)
sl2 = f.line(sp2, sv2)
seam_pcd = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('seam_pcdef',(#{sl2.eid}),#{prc.eid})"
)
seam_pc  = f._emit_raw(
    f"PCURVE('seam_pc',#{cone.eid},#{seam_pcd.eid})"
)
seam_sc  = f._emit_raw(
    f"SURFACE_CURVE('seam_sc',#{sl3.eid},(#{seam_pc.eid}),.PCURVE_S1.)"
)
# The one INTERNAL seam EDGE_CURVE — this is THE defect entity.
# Byte assertion: contains(b'EDGE_CURVE')
e_seam = f._emit_raw(
    f"EDGE_CURVE('gs193_seam_edge',#{v_seam_lo.eid},#{v_seam_hi.eid},"
    f"#{seam_sc.eid},.T.)"
)

# ── Circular boundary edges: bottom circle (v=V_LO) and top circle (v=V_HI) ───
# These are two full-360° circles: they close on themselves at the seam vertex.
# EDGE_CURVE with same start/end vertex + CIRCLE geometry — the standard
# closed-loop pattern for a full periodic circle.
r_lo = R0 + V_LO * sin_ha
r_hi = R0 + V_HI * sin_ha
z_lo = V_LO * cos_ha
z_hi = V_HI * cos_ha

lo_axis = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, z_lo)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
lo_circ = f.circle(lo_axis, r_lo, name="gs193_bottom_ring")

hi_axis = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, z_hi)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
hi_circ = f.circle(hi_axis, r_hi, name="gs193_top_ring")

e_bot = f._emit_raw(
    f"EDGE_CURVE('gs193_bottom_ring',#{v_seam_lo.eid},#{v_seam_lo.eid},"
    f"#{lo_circ.eid},.T.)"
)
e_top = f._emit_raw(
    f"EDGE_CURVE('gs193_top_ring',#{v_seam_hi.eid},#{v_seam_hi.eid},"
    f"#{hi_circ.eid},.T.)"
)

# ── FACE_OUTER_BOUND: one EDGE_LOOP with the seam referenced TWICE ────────────
# The 360° periodic face's outer boundary walks:
#   bottom ring (u: 0 → 2π at v=V_LO), forward
#   seam edge (u=2π, v: V_LO → V_HI), forward
#   top ring (u: 2π → 0 at v=V_HI), reversed
#   seam edge (u=0, v: V_HI → V_LO), reversed
# This is the Fusion 360 encoding: one internal seam edge referenced twice
# to close the loop on the periodic surface. Byte assertion:
#   count_entity_def(b'ADVANCED_FACE') == 1
loop = f.edge_loop([
    f.oriented_edge(e_bot,  True),   # bottom ring, forward
    f.oriented_edge(e_seam, True),   # seam, forward (first reference)
    f.oriented_edge(e_top,  False),  # top ring, reversed
    f.oriented_edge(e_seam, False),  # seam, reversed (second reference)
])

face = f.advanced_face([f.face_outer_bound(loop)], cone)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
