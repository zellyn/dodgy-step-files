"""Gn030 — Flat 3D curve as p-curve (instead of 2D PCURVE).

Catalog claim: A SURFACE_CURVE's associated_geometry uses a 3D curve (rather
than a 2D pcurve) on a flat PLANE; mathematically valid but trips importers
that hardcode the 2D form. Surprisingly common in Parasolid-origin files.

OCC behavior: heal and accept. Expected: occt=shape(1).

STEP mechanism (literal):
  - ADVANCED_FACE bounded by a PLANE (flat at Z=0).
  - EDGE_CURVE uses a SURFACE_CURVE whose associated_geometry is a 3D LINE
    (all three coordinates X,Y,Z with Z=0) lying in the host PLANE,
    instead of the expected PCURVE with a 2D LINE.
  - The 3D curve is geometrically consistent with the plane (Z=0 throughout)
    but is stored in 3D form, not the 2D parametric form that importers expect.
  - No C-1 break: Gn030 is expected to heal and load successfully (tier-3: load=="ok").

Mechanism vs driver:
  - CATALOG MECHANISM: SURFACE_CURVE associated_geometry is a 3D LINE (not PCURVE);
    the LINE lies in the host PLANE (Z=0) — Parasolid-style 3D-curve-in-pcurve-slot.
    Importers hardcoded for 2D pcurve form trip here; compliant kernels must heal.
  - No C-1 driver (expected outcome: load == ok).
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn030",
    defect=(
        "SURFACE_CURVE associated_geometry is a 3D LINE in the host PLANE (Z=0) "
        "instead of a 2D PCURVE; Parasolid-origin style; 3D curve geometrically "
        "consistent with PLANE surface but stored in 3D form not 2D parametric; "
        "importers hardcoded for 2D pcurve form trip; compliant kernels must heal "
        "by deriving the parameter curve from the 3D curve + host surface"
    ),
)

# ── HOST SURFACE: flat PLANE at Z=0 ──────────────────────────────────────────
plane_origin = f.cartesian_point((0.0, 0.0, 0.0))
plane_normal = f.direction((0.0, 0.0, 1.0))
plane_ref    = f.direction((1.0, 0.0, 0.0))
plane_ax2 = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('plane_ax',#{plane_origin.eid},#{plane_normal.eid},#{plane_ref.eid})"
)
surf = f._emit_raw(f"PLANE('flat_plane',#{plane_ax2.eid})")

# ── Parametric context (for reference only — we deliberately avoid it for the ──
# ── defect edges, using 3D LINEs in the SURFACE_CURVE instead) ───────────────
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Face corners (simple 4x4 square in Z=0 plane)
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((4.0, 0.0, 0.0))
p_c = f.cartesian_point((4.0, 4.0, 0.0))
p_d = f.cartesian_point((0.0, 4.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)
v_c = f.vertex_point(p_c)
v_d = f.vertex_point(p_d)


def mk_edge_3d_curve_as_pcurve(vs, ve, p3_start, dir3d, length):
    """Build EDGE_CURVE via SURFACE_CURVE with a 3D LINE in associated_geometry.

    This is the Gn030 defect pattern: the associated_geometry slot holds a 3D
    LINE (three coordinates, Z=0) instead of a PCURVE with a 2D LINE.
    The LINE lies in the host PLANE so it is geometrically consistent —
    but importers expecting a 2D pcurve form may trip.
    """
    # 3D edge line
    p3e = f.cartesian_point(p3_start)
    d3e = f.direction(dir3d)
    v3  = f.vector(d3e, length)
    l3  = f.line(p3e, v3)

    # 3D "pcurve" line — same 3D line geometry (Z=0 throughout) used in place of 2D pcurve.
    # This is the defect: a 3D LINE in the associated_geometry slot.
    p3_pc = f.cartesian_point(p3_start)   # 3D start point (X, Y, Z=0)
    d3_pc = f.direction(dir3d)            # 3D direction (Z component = 0)
    v3_pc = f.vector(d3_pc, length)
    l3_pc = f.line(p3_pc, v3_pc)          # 3D LINE used where 2D PCURVE expected

    # SURFACE_CURVE: edge_curve_3d + list containing the 3D LINE (not PCURVE)
    # .PCURVE_S1. annotation present — but geometry is a 3D LINE not a PCURVE entity.
    sc = f._emit_raw(
        f"SURFACE_CURVE('sc_3d_as_pc',#{l3.eid},(#{l3_pc.eid}),.PCURVE_S1.)"
    )
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")


# All four edges use the 3D-curve-as-pcurve pattern (the Gn030 defect)
e_bot   = mk_edge_3d_curve_as_pcurve(v_a, v_b, (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 4.0)
e_right = mk_edge_3d_curve_as_pcurve(v_b, v_c, (4.0, 0.0, 0.0), (0.0, 1.0, 0.0), 4.0)
e_top   = mk_edge_3d_curve_as_pcurve(v_c, v_d, (4.0, 4.0, 0.0), (-1.0, 0.0, 0.0), 4.0)
e_left  = mk_edge_3d_curve_as_pcurve(v_d, v_a, (0.0, 4.0, 0.0), (0.0, -1.0, 0.0), 4.0)

loop = f.edge_loop([
    f.oriented_edge(e_bot,   True),
    f.oriented_edge(e_right, True),
    f.oriented_edge(e_top,   True),
    f.oriented_edge(e_left,  True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
