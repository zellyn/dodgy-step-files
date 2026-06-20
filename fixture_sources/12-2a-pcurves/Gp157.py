"""Gp157 — ShapeAnalysis_Surface.ProjectDegenerated lazy-singularity-init

Catalog claim: Projector proceeds without triggering ComputeSingularities.
Degenerate edge-points near apex project incorrectly; singularity loci
undetected. Cone surface with edge approaching apex singularity at u=0.

STEP mechanism (literal):
  - CONICAL_SURFACE (half-angle 30 deg, radius 1) face with a defect edge
    whose pcurve approaches the cone apex (u=0, the singular locus).
  - THE CATALOG MECHANISM (lazy-singularity-init): ShapeAnalysis_Surface::
    ProjectDegenerated calls the projector without first calling
    ComputeSingularities. The singularity data structure is therefore empty
    when ProjectDegenerated tests for degenerate loci. Edge-points near the
    apex (where the cone's metric collapses: 3D point radius → 0) project
    incorrectly because the singularity is not pre-registered. OCC heals
    the resulting edge and produces shape(1)/shape(1).
  - 3D curve: a clean LINE approaching the cone apex. Geometry is valid and
    loadable.
  - NO C-1 break (Archetype B: OCC silently heals, expected shape(1)/shape(1)).

Mechanism vs driver:
  - CATALOG MECHANISM: CONICAL_SURFACE apex at u=0; PCurve approaches u=0
    line (apex singularity); ComputeSingularities not called before
    ProjectDegenerated; singularity loci empty; projection incorrect near apex;
    lazy-singularity-init axis; OCC heals silently.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp157",
    defect=(
        "CONICAL_SURFACE half_angle=30deg radius=1; apex at u=0 (singular locus); "
        "defect edge: SURFACE_CURVE; "
        "3D LINE from near-apex (0.05,0,0.087) to base (0.5,0,0.866) (clean, loadable); "
        "PCurve LINE in UV at u=0 from v=1.0 down to v=0.05 (approaching apex); "
        "ShapeAnalysis_Surface::ProjectDegenerated called without prior "
        "ComputeSingularities; singularity loci at u=0 unregistered; "
        "near-apex points project incorrectly; lazy-singularity-init axis; "
        "OCC heals; shape(1)/shape(1)"
    ),
)

# CONICAL_SURFACE: half-angle=30deg (~0.5236 rad), radius=1 at v=0,
# apex at origin (u=0 in OCC cone parametrisation means v=0 on the base circle).
# OCC cone: u = azimuth (0..2pi), v = height from base. Apex at v=-R/tan(alpha).
# For semi-angle 30deg and radius 1: apex_v = -1/tan(30deg) = -sqrt(3) ~ -1.732.
# We use a simpler arrangement: place the cone with the apex explicitly at v < 0.
# To keep geometry loadable, use a standard upright cone with apex in positive Z.
# STEP CONICAL_SURFACE: placement defines apex position, axis=Z, X along u=0.
# Semi_angle=pi/6; at height h from apex: radius = h*tan(pi/6).
import math
HALF_ANGLE = math.pi / 6.0   # 30 degrees

orig  = f.cartesian_point((0.0, 0.0, 0.0))   # cone apex at origin
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
# CONICAL_SURFACE(name, position, radius_at_zero, semi_angle)
# In STEP: CONICAL_SURFACE has radius at v=0 (which is the apex when radius=0).
# Use radius=0.0 to place apex at the origin (v=0 is apex).
cone = f._emit_raw(
    f"CONICAL_SURFACE('cone_apex_singularity',#{plc.eid},0.0,{HALF_ANGLE})"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# OCC cone parametrisation with radius=0 at v=0 (apex):
# 3D point at (u, v) = (cos(u)*v*tan(alpha), sin(u)*v*tan(alpha), v)
# tan(pi/6) = 1/sqrt(3) ~ 0.5774
tan_a = math.tan(HALF_ANGLE)

# Choose corners for a rectangular patch on the cone:
# Use u in [0, pi/2], v in [0.05, 1.0] (avoid exact apex at v=0)
# 3D corner at (u=0, v=v0): (v0*tan_a, 0, v0)
# 3D corner at (u=pi/2, v=v0): (0, v0*tan_a, v0)
v_lo = 0.05  # near-apex but not at apex
v_hi = 1.0

def cone_pt(u_rad, v_h):
    x = math.cos(u_rad) * v_h * tan_a
    y = math.sin(u_rad) * v_h * tan_a
    z = v_h
    return (x, y, z)

A = cone_pt(0.0,          v_lo)  # (u=0,    v=v_lo) — near apex
B = cone_pt(math.pi/2.0,  v_lo)  # (u=pi/2, v=v_lo) — near apex
C = cone_pt(math.pi/2.0,  v_hi)  # (u=pi/2, v=v_hi) — base
D = cone_pt(0.0,          v_hi)  # (u=0,    v=v_hi) — base

p_A = f.cartesian_point(A); v_A = f.vertex_point(p_A)
p_B = f.cartesian_point(B); v_B = f.vertex_point(p_B)
p_C = f.cartesian_point(C); v_C = f.vertex_point(p_C)
p_D = f.cartesian_point(D); v_D = f.vertex_point(p_D)

def mk_line_edge_with_pc(vs, ve, p3, d3, len3, p2, d2, len2):
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3); v3 = f.vector(d3e, len3); l3 = f.line(p3e, v3)
    p2e = f.cartesian_point(p2)
    d2e = f.direction(d2); v2e = f.vector(d2e, len2); l2 = f.line(p2e, v2e)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{cone.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# Bottom edge A→B (near-apex arc; near-constant v=v_lo, u=0→pi/2).
# 3D: chord from A to B; UV: u from 0 to pi/2, v=v_lo (constant).
chord_AB = tuple(B[i]-A[i] for i in range(3))
len_AB = math.sqrt(sum(x*x for x in chord_AB))
d_AB = tuple(x/len_AB for x in chord_AB)
e_AB = mk_line_edge_with_pc(
    v_A, v_B,
    A, d_AB, len_AB,
    (0.0, v_lo), (1.0, 0.0), math.pi/2.0
)

# Right edge B→C (along u=pi/2, v=v_lo→v_hi).
chord_BC = tuple(C[i]-B[i] for i in range(3))
len_BC = math.sqrt(sum(x*x for x in chord_BC))
d_BC = tuple(x/len_BC for x in chord_BC)
e_BC = mk_line_edge_with_pc(
    v_B, v_C,
    B, d_BC, len_BC,
    (math.pi/2.0, v_lo), (0.0, 1.0), v_hi - v_lo
)

# Top edge C→D (base arc at v=v_hi, u=pi/2→0).
chord_CD = tuple(D[i]-C[i] for i in range(3))
len_CD = math.sqrt(sum(x*x for x in chord_CD))
d_CD = tuple(x/len_CD for x in chord_CD)
e_CD = mk_line_edge_with_pc(
    v_C, v_D,
    C, d_CD, len_CD,
    (math.pi/2.0, v_hi), (-1.0, 0.0), math.pi/2.0
)

# ── DEFECT EDGE D→A — left edge (along u=0, v=v_hi→v_lo) ──────────────────────
#
# THE CATALOG MECHANISM: PCurve LINE along u=0 (apex singularity line for cone).
# At u=0, v→0: 3D point → apex (0,0,0). ComputeSingularities would register
# u=0 as a singularity locus. Without it, ProjectDegenerated's singularity
# table is empty; near-apex projections at the D→A edge (v=1→0.05 along u=0)
# are handled incorrectly. OCC heals the resulting shape.
# NO C-1 break: Archetype B, clean 3D geometry.
chord_DA = tuple(A[i]-D[i] for i in range(3))
len_DA = math.sqrt(sum(x*x for x in chord_DA))
d_DA = tuple(x/len_DA for x in chord_DA)

line_3d_DA = f.cartesian_point(D)
line_dir_DA = f.direction(d_DA)
line_vec_DA = f.vector(line_dir_DA, len_DA)
line_3d_geom = f.line(line_3d_DA, line_vec_DA)

# PCurve: LINE along u=0 from v=v_hi down to v=v_lo (approaching apex).
# This is the singular line; ComputeSingularities would note u=0 as degenerate.
pc2_start = f.cartesian_point((0.0, v_hi))
pc2_dir   = f.direction((0.0, -1.0))   # decreasing v (heading toward apex)
pc2_vec   = f.vector(pc2_dir, v_hi - v_lo)
pc2_line  = f.line(pc2_start, pc2_vec)

defrep_DA = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('lazy_sing_pc_def',(#{pc2_line.eid}),#{prc.eid})"
)
pcurve_DA = f._emit_raw(f"PCURVE('lazy_sing_pc',#{cone.eid},#{defrep_DA.eid})")
sc_DA = f._emit_raw(
    f"SURFACE_CURVE('lazy_sing_sc',#{line_3d_geom.eid},(#{pcurve_DA.eid}),.PCURVE_S1.)"
)
e_DA = f._emit_raw(
    f"EDGE_CURVE('lazy_sing_edge',#{v_D.eid},#{v_A.eid},#{sc_DA.eid},.T.)"
)

loop = f.edge_loop([
    f.oriented_edge(e_AB, True),
    f.oriented_edge(e_BC, True),
    f.oriented_edge(e_CD, True),
    f.oriented_edge(e_DA, True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], cone)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
