"""Gp005 — Pcurve with single-pole apex on sphere/cone (singularity).

Catalog claim: Projecting a 3D curve through the singular pole of a cone
apex produces an indeterminate UV path. Surface-surface intersection and
face translation routines misbehave near the singularity.

Fixture: CONICAL_SURFACE (semi-angle 30°) with an outer loop that touches
the cone apex (0,0,0). The apex is a true UV singularity: all U values map
to V=0. An edge runs from the apex along a generator line. No degenerate
edge marks the singularity, which causes UV projection ambiguity.
"""
from math import pi, sin, cos
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gp005",
             defect="pcurve with single-pole apex on cone singularity")

# Conical surface: apex at origin, semi-angle 30° = 0.5235987756 rad
orig = f.cartesian_point((0.0, 0.0, 0.0))
zdir = f.direction((0.0, 0.0, 1.0))
xdir = f.direction((1.0, 0.0, 0.0))
plc = f.axis2_placement_3d(orig, zdir, xdir)
cone_semi_angle = 0.5235987756  # 30 degrees in radians
cone = f._emit_raw(f"CONICAL_SURFACE('cone',#{plc.eid},0.0,{cone_semi_angle})")

# Apex vertex at (0,0,0) - the singularity (V=0 for all U)
apex_pt = f.cartesian_point((0.0, 0.0, 0.0))
apex_vert = f.vertex_point(apex_pt)

# Off-apex vertex at distance 5 along a generator
# At V=5: r = 5*sin(30°) = 2.5, z = 5*cos(30°) ≈ 4.33
off_apex_pt = f.cartesian_point((2.5, 0.0, 4.330127))
off_apex_vert = f.vertex_point(off_apex_pt)

# 3D curve: line from apex (0,0,0) along generator at U=0
# Direction along cone: (sin(30°), 0, cos(30°)) = (0.5, 0, 0.866025)
curve_dir = f.direction((0.5, 0.0, 0.866025))
curve_vec = f.vector(curve_dir, 5.0)
line3d = f.line(apex_pt, curve_vec)

# DEFECT: 2D pcurve from (u=0, v=0) to (u=0, v=5)
# V=0 is the singular apex pole; all U map to same 3D point.
# This indeterminate UV path causes singularity handling failures.
uv_start = f.cartesian_point((0.0, 0.0))
uv_dir = f.direction((0.0, 1.0))
uv_vec = f.vector(uv_dir, 5.0)
line2d = f.line(uv_start, uv_vec)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('','2D'))"
)
defrep = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('',(#{line2d.eid}),#{prc.eid})")
pcurve = f._emit_raw(f"PCURVE('',#{cone.eid},#{defrep.eid})")
surface_curve = f._emit_raw(
    f"SURFACE_CURVE('',#{line3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
edge = f._emit_raw(
    f"EDGE_CURVE('',#{apex_vert.eid},#{off_apex_vert.eid},#{surface_curve.eid},.T.)"
)

# Build the face and shell for the PRODUCT chain
loop = f.edge_loop([f.oriented_edge(edge, True)])
face = f.advanced_face([f.face_outer_bound(loop)], cone)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
