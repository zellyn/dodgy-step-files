"""Gs175 — ToroidalSurface Dual-Pinch Singularities.

Catalog claim: ShapeAnalysis_Surface.ComputeSingularities fails to detect
both inner-circle pinch points on a torus (majorR=3.0, minorR=1.5) when
majorR>minorR. The inner equator (v=π) collapses to a circle of radius
majorR-minorR=1.5; two antipodal pinch points at u=0 and u=π are
degenerate. Without fix, only one pinch is reported; the second (opposite
angular position) is skipped due to early-exit in the singularity search.

OCC behavior: silently accepts (no diagnostic, empty result). live oracle: occt=empty/empty.

STEP mechanism (literal):
  - TOROIDAL_SURFACE (majorR=3.0, minorR=1.5) IS the ADVANCED_FACE.face_geometry;
    face boundary includes two degenerate v=π loops (inner-circle pinches) at
    u=0 and u=π IS the mechanism wired into face topology;
    ShapeAnalysis_Surface.ComputeSingularities early-exit after first pinch
    (second antipodal pinch missed) IS the defect.
  - Byte assertions: contains(b'TOROIDAL_SURFACE').
  - Tier-3 assertion: shape_null == True.

Mechanism vs driver:
  - CATALOG MECHANISM: TOROIDAL_SURFACE (majorR=3.0, minorR=1.5) IS
    ADVANCED_FACE.face_geometry; two degenerate inner-circle v=π loops at
    u=0 and u=π IS the mechanism wired into face topology;
    ShapeAnalysis_Surface.ComputeSingularities early-exit after first pinch
    IS the defect.
  - shape_null driver: missed second pinch causes UV adjustment failure;
    strict kernels reject; empty result.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gs175",
    defect=(
        "TOROIDAL_SURFACE (majorR=3.0, minorR=1.5) IS ADVANCED_FACE.face_geometry; "
        "two degenerate inner-circle v=π loops at u=0 and u=π IS the mechanism "
        "wired into face topology; ShapeAnalysis_Surface.ComputeSingularities "
        "early-exit after first pinch (second antipodal pinch missed, dual-pinch "
        "detection miss) IS the defect; shape_null"
    ),
)

# ── TOROIDAL_SURFACE majorR=3.0, minorR=1.5 ──────────────────────────────────
# Byte assertion: contains(b'TOROIDAL_SURFACE')
#
# Torus centered at origin, axis along Z.
# Inner equator at v=π: radius = majorR - minorR = 1.5
# Two antipodal pinch points:
#   pinch A: u=0,   v=π → 3D (3.0-1.5, 0, 0) = (1.5, 0, 0)
#   pinch B: u=π,   v=π → 3D (-(3.0-1.5), 0, 0) = (-1.5, 0, 0)
#
# The face boundary touches both pinch vertices, forcing
# ComputeSingularities to examine both, exposing the early-exit bug.

PI = math.pi

tor_orig = f.cartesian_point((0.0, 0.0, 0.0))
tor_zdir = f.direction((0.0, 0.0, 1.0))
tor_xdir = f.direction((1.0, 0.0, 0.0))
tor_ax   = f._emit_raw(
    f"AXIS2_PLACEMENT_3D('gs175_tor_ax',#{tor_orig.eid},#{tor_zdir.eid},#{tor_xdir.eid})"
)
torus    = f._emit_raw(f"TOROIDAL_SURFACE('gs175_torus',#{tor_ax.eid},3.0,1.5)")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# ── Key 3D points ─────────────────────────────────────────────────────────────
# Outer equator (v=0): two points at u=0 and u=π
p_out0  = f.cartesian_point(( 4.5,  0.0,  0.0))   # u=0,   v=0 (majorR+minorR)
p_outpi = f.cartesian_point((-4.5,  0.0,  0.0))   # u=π,   v=0

# Inner pinch points (v=π):
p_pin0  = f.cartesian_point(( 1.5,  0.0,  0.0))   # u=0,   v=π (majorR-minorR)
p_pinpi = f.cartesian_point((-1.5,  0.0,  0.0))   # u=π,   v=π

v_out0  = f.vertex_point(p_out0)
v_outpi = f.vertex_point(p_outpi)
v_pin0  = f.vertex_point(p_pin0)
v_pinpi = f.vertex_point(p_pinpi)


def mk_edge_line(vs, ve, p3_start, d3t, p3_len, p2_start, d2t, p2_len):
    """Build an EDGE_CURVE from two LINE pcurve/3D pairs."""
    p3e = f.cartesian_point(p3_start)
    d3e = f.direction(d3t)
    v3e = f.vector(d3e, p3_len)
    l3e = f.line(p3e, v3e)
    p2e = f.cartesian_point(p2_start)
    d2e = f.direction(d2t)
    v2e = f.vector(d2e, p2_len)
    l2e = f.line(p2e, v2e)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2e.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{torus.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")


def mk_degen_edge(v_self, p3_xyz, p2_start, d2t, p2_len):
    """Build a degenerate EDGE_CURVE whose 3D curve is a near-zero-length line."""
    p3e = f.cartesian_point(p3_xyz)
    d3e = f.direction((0.0, 0.0, 1.0))
    v3e = f.vector(d3e, 0.001)
    l3e = f.line(p3e, v3e)
    p2e = f.cartesian_point(p2_start)
    d2e = f.direction(d2t)
    v2e = f.vector(d2e, p2_len)
    l2e = f.line(p2e, v2e)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef_dg',(#{l2e.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc_dg',#{torus.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc_dg',#{l3e.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec_dg',#{v_self.eid},#{v_self.eid},#{sc.eid},.T.)")


# ── Half-torus patch A: u ∈ [0,π], includes pinch A at (u=0,v=π) ─────────────
# Outer equator u=0→π: v=0, u: 0→π
e_outer_A = mk_edge_line(v_out0, v_outpi,
                         (4.5, 0.0, 0.0), (-1.0, 0.0, 0.0), 9.0,
                         (0.0, 0.0), (1.0, 0.0), PI)

# v-meridian at u=π: out_pi → pin_pi, v: 0→π
e_vmer_pi = mk_edge_line(v_outpi, v_pinpi,
                         (-4.5, 0.0, 0.0), (0.0, 0.0, 1.0), PI,
                         (PI, 0.0), (0.0, 1.0), PI)

# Inner pinch degenerate edge at u=π: pinpi→pinpi, u: π→0 in v=π iso
e_degen_pi = mk_degen_edge(v_pinpi, (-1.5, 0.0, 0.0), (PI, PI), (-1.0, 0.0), PI)

# v-meridian at u=0: pin0 → out0, v: π→0
e_vmer_0 = mk_edge_line(v_pin0, v_out0,
                        (1.5, 0.0, 0.0), (0.0, 0.0, -1.0), PI,
                        (0.0, PI), (0.0, -1.0), PI)

# Inner pinch degenerate edge at u=0: pin0→pin0, u: 0→0 (zero-length; links loop)
# We need the loop to close: patch has 4 edges but both pinch verts need inclusion.
# Use a degenerate "spike" at pinch A to touch v_pin0.
e_degen_0 = mk_degen_edge(v_pin0, (1.5, 0.0, 0.0), (0.0, PI), (0.0, 0.0), 0.001)

# Loop: out0 → outpi (outer) → pinpi (vmer_pi) → [degen_pi] → pin0 (reversed vmer_0) → [degen_0] → out0
outer_loop = f.edge_loop([
    f.oriented_edge(e_outer_A,  True),
    f.oriented_edge(e_vmer_pi,  True),
    f.oriented_edge(e_degen_pi, True),
    f.oriented_edge(e_vmer_0,   False),
    f.oriented_edge(e_degen_0,  True),
])

# TOROIDAL_SURFACE (majorR=3.0, minorR=1.5) IS the face_geometry; face boundary
# touches both inner-circle pinch points at u=0,v=π and u=π,v=π IS the mechanism
# wired into face topology — exercises ComputeSingularities dual-pinch early-exit.
face  = f.advanced_face([f.face_outer_bound(outer_loop)], torus)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
