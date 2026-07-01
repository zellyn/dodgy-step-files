"""Gp171 — Full-circle CIRCLE EDGE_CURVE with two near-coincident but distinct VERTEX_POINTs.

Catalog claim: STEP file with a planar face bounded by a single ORIENTED_EDGE whose
basis is a CIRCLE (radius=5.0) with edge_start and edge_end as two distinct
VERTEX_POINT entities separated by ~1e-8 m (within or at the UNCERTAINTY_MEASURE_WITH_UNIT
= 1e-7 tolerance). The circle's 3D endpoints are parametrically at theta=0 and
theta=2*pi - epsilon (near-but-not-exactly 2*pi apart). Some readers collapse the
two vertices into one (treating the edge as a closed loop); others preserve both
vertices and produce a wire with a near-zero-length free edge at the closure point.

Source: OCCT MANTIS 0027634.
B4 wave-6 DEF-DD. Confidence: HIGH.

Byte assertions:
  contains(b'CIRCLE')
  count_entity_def(b'VERTEX_POINT') >= 2
  contains(b'FACE_OUTER_BOUND')
Tier-3: shape_null == False
Expected: occt=shape(1)/shape(1) gmsh=shape(3) ifc=schema_n/a
"""
import math
from step_corpus.step_builder import StepFile

# Near-coincident vertex gap: 1e-8 m (below UNCERTAINTY_MEASURE_WITH_UNIT = 1e-7).
# The circle has radius 5.0. At theta = 2*pi - delta, the arc endpoint is:
#   x = 5*cos(delta) ~ 5*(1 - delta^2/2) ~ 5.0
#   y = 5*sin(-delta) ~ -5*delta
# For gap d in 3D: d ~ 5*delta => delta = d / 5
RADIUS = 5.0
GAP = 1e-8  # 3D gap between edge_start and edge_end
DELTA = GAP / RADIUS  # angular offset so endpoints are 1e-8 apart

f = StepFile(
    catalog_id="Gp171",
    defect=(
        "PLANE face with single CIRCLE EDGE_CURVE (radius=5.0); edge_start = "
        "VERTEX_POINT at (5.0,0.0,0.0); edge_end = distinct VERTEX_POINT at "
        "(5.0,-1e-8,0.0) (gap=1e-8 < UNCERTAINTY=1e-7); circle endpoints at "
        "theta=0 and theta=2pi-2e-9 rad; near-coincident vertices create near-zero "
        "free edge at closure — readers may collapse to one vertex (treating loop as "
        "closed) or preserve both (zero-length free edge); OCCT MANTIS 0027634; "
        "SHELL_BASED_SURFACE_MODEL IS model entity"
    ),
)

# PLANE at z=0 (normal = +Z).
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc  = f.axis2_placement_3d(orig, zdir, xdir)
surf = f.plane(plc)

# UV parametric context for pcurves.
prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Circle geometry: center at origin, radius 5.0, axis in +Z.
circle_center = f.cartesian_point((0.0, 0.0, 0.0))
circle_zdir   = f.direction((0.0, 0.0, 1.0))
circle_xdir   = f.direction((1.0, 0.0, 0.0))
circle_ax     = f.axis2_placement_3d(circle_center, circle_zdir, circle_xdir)
circle_3d     = f._emit_raw(f"CIRCLE('full_circle',#{circle_ax.eid},{RADIUS})")

# THE DEFECT: two distinct VERTEX_POINTs separated by GAP = 1e-8 m.
# edge_start: at theta=0 → (5, 0, 0)
# edge_end:   at theta=2*pi - DELTA ≈ (5*cos(DELTA), -5*sin(DELTA), 0)
# ≈ (5.0, -GAP, 0) since sin(DELTA) ≈ DELTA for tiny DELTA.
p_start = f.cartesian_point((RADIUS, 0.0, 0.0))
end_x   = RADIUS * math.cos(DELTA)
end_y   = -RADIUS * math.sin(DELTA)   # negative: arc goes CW from 0 to -DELTA
p_end   = f.cartesian_point((end_x, end_y, 0.0))

v_start = f.vertex_point(p_start)   # VERTEX_POINT #1
v_end   = f.vertex_point(p_end)     # VERTEX_POINT #2  (near-coincident with #1)

# Pcurve on the PLANE for the circle.
# On a PLANE (x,y,z) with normal +Z and x-axis +X, the 2D parameter (u,v)
# maps to 3D as (u,v,0). The circle in 2D UV is a circle of radius 5 at (0,0).
# We encode it as the CIRCLE itself — referencing the same circle geometry
# on the plane in definitional 2D context.
pc_center_2d = f.cartesian_point((0.0, 0.0))
pc_xdir_2d   = f.direction((1.0, 0.0))
pc_ax2d      = f._emit_raw(
    f"AXIS2_PLACEMENT_2D('',#{pc_center_2d.eid},#{pc_xdir_2d.eid})"
)
pc_circle_2d = f._emit_raw(f"CIRCLE('pc_circle_2d',#{pc_ax2d.eid},{RADIUS})")
pc_def       = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_circle_def',(#{pc_circle_2d.eid}),#{prc.eid})"
)
pcurve       = f._emit_raw(
    f"PCURVE('full_circle_pc',#{surf.eid},#{pc_def.eid})"
)

# SURFACE_CURVE wrapping the 3D circle and its pcurve.
sc = f._emit_raw(
    f"SURFACE_CURVE('full_circle_sc',#{circle_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

# EDGE_CURVE: edge_start != edge_end (the defect — two distinct near-coincident vertices).
ec = f._emit_raw(
    f"EDGE_CURVE('full_circle_ec',#{v_start.eid},#{v_end.eid},#{sc.eid},.T.)"
)

# Single ORIENTED_EDGE in the face loop.
loop = f.edge_loop([f.oriented_edge(ec, True)])
face = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
