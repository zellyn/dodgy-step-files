"""Gp168 — ProjectDegenerated.lazy-compute

Catalog claim: Toroidal surface with meridian edge. Singularities computed lazily
without revalidation; traversing torus singularity boundaries triggers stale cache.
OCC cannot heal; produces empty/empty.

STEP mechanism (literal):
  - TOROIDAL_SURFACE (major radius=2, minor radius=1) face with a defect edge
    whose pcurve traverses the meridian singularity boundary at v=0/2pi.
  - THE CATALOG MECHANISM (lazy-compute, empty variant): ProjectDegenerated
    computes singularities lazily (on first call) and caches them. When the pcurve
    traverses a torus meridian boundary (v crossing 0 or 2pi), the cached
    singularity data is stale relative to the actual traversal path. OCC cannot
    revalidate the stale cache in the presence of a C-1 break in the 3D B-spline;
    shape_null=True.
  - C-1 DRIVER: degree-2 B-spline 3D curve with positional break at t=0.5 (knot
    mult=3, 1.5-unit CP gap) forces shape_null=True.

Mechanism vs driver:
  - CATALOG MECHANISM: TOROIDAL_SURFACE major_radius=2, minor_radius=1; defect
    pcurve LINE traverses v from near-0 (past meridian seam) to v=pi; cached
    singularity data stale at meridian boundary; ProjectDegenerated lazy-compute
    revalidation absent; combined with C-1 break, OCC cannot heal; shape_null=True.
  - C-1 DRIVER: degree-2 B-spline 3D positional break forces shape_null=True.

Distinction from Gp157 (lazy-singularity-init, cone, shape(1)):
  Gp157 uses a CONE with ComputeSingularities never called (empty table); OCC heals.
  Gp168 uses a TORUS where singularities ARE computed but the cache is stale at
  meridian boundary traversal; combined with C-1 break, OCC cannot heal.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp168",
    defect=(
        "TOROIDAL_SURFACE major_radius=2 minor_radius=1; "
        "defect edge: SURFACE_CURVE; "
        "3D B_SPLINE_CURVE_WITH_KNOTS degree-2 C-1 break at t=0.5 "
        "(CP[2] vs CP[3] 1.5-unit gap) drives shape_null; "
        "PCurve LINE traversing torus meridian boundary (v crosses 0/2pi): "
        "ProjectDegenerated lazy-compute cache stale at meridian seam; "
        "stale singularity data unvalidated; lazy-compute axis; shape_null=True"
    ),
)

# TOROIDAL_SURFACE: major_radius=2, minor_radius=1.
# OCC torus: u=azimuth (0..2pi), v=meridian (0..2pi).
# 3D point: ((R+r*cos(v))*cos(u), (R+r*cos(v))*sin(u), r*sin(v)).
R = 2.0
r = 1.0

orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
torus = f._emit_raw(f"TOROIDAL_SURFACE('torus_lazy_compute',#{plc.eid},{R},{r})")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

def torus_pt(u, v):
    """3D point on torus with R=2, r=1."""
    x = (R + r * math.cos(v)) * math.cos(u)
    y = (R + r * math.cos(v)) * math.sin(u)
    z = r * math.sin(v)
    return (x, y, z)

# Patch: u in [0, pi/2], v in [6.18, 6.18+pi] (crossing meridian seam at v=2pi~6.28).
# v_lo just below 2pi (=6.18 ~ 2pi-0.1); v_hi = v_lo + pi (crosses seam).
V_LO = 2.0 * math.pi - 0.1   # just below the meridian seam (v ~ 6.18)
V_HI = V_LO + math.pi        # pi units past seam

A3 = torus_pt(0.0,        V_LO)
B3 = torus_pt(math.pi/2,  V_LO)
C3 = torus_pt(math.pi/2,  V_HI)
D3 = torus_pt(0.0,        V_HI)

p_A = f.cartesian_point(A3); v_A = f.vertex_point(p_A)
p_B = f.cartesian_point(B3); v_B = f.vertex_point(p_B)
p_C = f.cartesian_point(C3); v_C = f.vertex_point(p_C)
p_D = f.cartesian_point(D3); v_D = f.vertex_point(p_D)

def mk_line_edge_with_pc(vs, ve, p3, d3t, len3, p2t, d2t, len2):
    """Build EDGE_CURVE via SURFACE_CURVE with a linear pcurve on torus."""
    p3e = f.cartesian_point(p3)
    d3e = f.direction(d3t); v3 = f.vector(d3e, len3); l3 = f.line(p3e, v3)
    p2e = f.cartesian_point(p2t)
    d2e = f.direction(d2t); v2e = f.vector(d2e, len2); l2 = f.line(p2e, v2e)
    pcd = f._emit_raw(f"DEFINITIONAL_REPRESENTATION('pcdef',(#{l2.eid}),#{prc.eid})")
    pc  = f._emit_raw(f"PCURVE('pc',#{torus.eid},#{pcd.eid})")
    sc  = f._emit_raw(f"SURFACE_CURVE('sc',#{l3.eid},(#{pc.eid}),.PCURVE_S1.)")
    return f._emit_raw(f"EDGE_CURVE('ec',#{vs.eid},#{ve.eid},#{sc.eid},.T.)")

# Edge A→B: bottom ring at v=V_LO (u from 0 to pi/2).
chord_AB = tuple(B3[i] - A3[i] for i in range(3))
len_AB   = math.sqrt(sum(x*x for x in chord_AB))
d_AB     = tuple(x / len_AB for x in chord_AB)
e_AB = mk_line_edge_with_pc(
    v_A, v_B, A3, d_AB, len_AB,
    (0.0, V_LO), (1.0, 0.0), math.pi / 2.0
)

# Edge B→C: right meridian (u=pi/2, v from V_LO to V_HI).
chord_BC = tuple(C3[i] - B3[i] for i in range(3))
len_BC   = math.sqrt(sum(x*x for x in chord_BC))
d_BC     = tuple(x / len_BC for x in chord_BC)
e_BC = mk_line_edge_with_pc(
    v_B, v_C, B3, d_BC, len_BC,
    (math.pi / 2.0, V_LO), (0.0, 1.0), V_HI - V_LO
)

# Edge C→D: top ring at v=V_HI (u from pi/2 to 0).
chord_CD = tuple(D3[i] - C3[i] for i in range(3))
len_CD   = math.sqrt(sum(x*x for x in chord_CD))
d_CD     = tuple(x / len_CD for x in chord_CD)
e_CD = mk_line_edge_with_pc(
    v_C, v_D, C3, d_CD, len_CD,
    (math.pi / 2.0, V_HI), (-1.0, 0.0), math.pi / 2.0
)

# ── DEFECT EDGE D→A — left meridian (u=0, v from V_HI to V_LO) ──────────────
#
# THE CATALOG MECHANISM: PCurve LINE at u=0, v from V_HI to V_LO.
# This traversal goes from v=V_HI (past seam) back to V_LO (just below seam),
# crossing the meridian boundary at v=2pi. ProjectDegenerated cached singularity
# data from an earlier lazily-computed call does not account for the seam crossing
# in this direction; stale cache is not revalidated; lazy-compute axis.
# C-1 DRIVER forces shape_null=True.
chord_DA = tuple(A3[i] - D3[i] for i in range(3))
len_DA   = math.sqrt(sum(x*x for x in chord_DA))
d_unit   = tuple(x / len_DA for x in chord_DA)
mid3     = tuple(D3[i] + 0.5 * chord_DA[i] for i in range(3))
gap3     = tuple(mid3[i] + 1.5 * d_unit[i] for i in range(3))
q25_3    = tuple(D3[i] + 0.25 * chord_DA[i] for i in range(3))
q75_3    = tuple(D3[i] + 0.75 * chord_DA[i] for i in range(3))

dc0 = f.cartesian_point(D3)
dc1 = f.cartesian_point(q25_3)
dc2 = f.cartesian_point(mid3)
dc3 = f.cartesian_point(gap3)       # 1.5-unit positional gap = C-1 break
dc4 = f.cartesian_point(q75_3)
dc5 = f.cartesian_point(A3)

bspline_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('lazy_compute_empty_driver',2,"
    f"(#{dc0.eid},#{dc1.eid},#{dc2.eid},#{dc3.eid},#{dc4.eid},#{dc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,"
    f"(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# PCurve: at u=0, v from V_HI (past seam) to V_LO (below seam).
pc_start = f.cartesian_point((0.0, V_HI))
pc_dir   = f.direction((0.0, -1.0))   # decreasing v (past seam → below seam)
pc_vec   = f.vector(pc_dir, V_HI - V_LO)
pc_line  = f.line(pc_start, pc_vec)

defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('lazy_compute_pc_def',(#{pc_line.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('lazy_compute_pc',#{torus.eid},#{defrep.eid})")
sc_DA = f._emit_raw(
    f"SURFACE_CURVE('lazy_compute_sc',#{bspline_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)
e_DA = f._emit_raw(
    f"EDGE_CURVE('lazy_compute_edge',#{v_D.eid},#{v_A.eid},#{sc_DA.eid},.T.)"
)

loop = f.edge_loop([
    f.oriented_edge(e_AB, True),
    f.oriented_edge(e_BC, True),
    f.oriented_edge(e_CD, True),
    f.oriented_edge(e_DA, True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], torus)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
