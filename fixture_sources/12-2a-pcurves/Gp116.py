"""Gp116 — Sphere pole singularity in pcurve.

Catalog claim: ShapeAnalysis_Edge.CheckCurve3dWithPCurve fails when pcurve
passes through sphere pole (UV v=+π/2) where the metric collapses. Sampling
uses NaN comparisons that can fail.

STEP mechanism (literal):
  - SPHERICAL_SURFACE (radius=1) face with a defect edge wrapped in
    SURFACE_CURVE.
  - THE CATALOG MECHANISM: The pcurve is a LINE in UV that passes through the
    north pole at v=+π/2 (i.e. U=anything, V=+π/2). At the pole the sphere
    metric collapses: the entire circle U∈[0,2π] at V=π/2 maps to the single
    3D point (0,0,1). CheckCurve3dWithPCurve samples the pcurve uniformly and
    evaluates 3D positions; at the pole sample point the 3D evaluation yields
    (0,0,1) regardless of the U value, so the forward 3D→UV inversion is
    undefined. Sampling uses NaN comparisons in the degeneracy check that can
    silently pass. OCC heals and produces shape(1)/shape(1).
  - 3D curve: a clean LINE running from the sphere equator to the north pole
    along the meridian u=0. Geometry is valid and loadable.
  - NO C-1 break (Archetype B: OCC silently heals, expected shape(1)/shape(1)).

Mechanism vs driver:
  - CATALOG MECHANISM: pcurve LINE passes through sphere north pole (v=π/2);
    metric collapses; CheckCurve3dWithPCurve NaN sampling; OCC heals silently.
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp116",
    defect=(
        "SPHERICAL_SURFACE radius=1; defect edge: SURFACE_CURVE; 3D LINE on "
        "meridian u=0 from equator (1,0,0) to north pole (0,0,1); PCurve LINE "
        "in UV from (0.0, 0.0) direction (0.0,1.0) to pole at v=pi/2; "
        "sphere metric collapses at pole: entire U circle maps to single 3D point; "
        "CheckCurve3dWithPCurve NaN in UV inversion at pole; OCC heals; "
        "shape(1)/shape(1)"
    ),
)

# SPHERICAL_SURFACE: radius=1, center=origin, axis=Z
orig  = f.cartesian_point((0.0, 0.0, 0.0))
zdir  = f.direction((0.0, 0.0, 1.0))
xdir  = f.direction((1.0, 0.0, 0.0))
plc   = f.axis2_placement_3d(orig, zdir, xdir)
sphere = f._emit_raw(f"SPHERICAL_SURFACE('unit_sphere',#{plc.eid},1.0)")

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# Face: a spherical patch spanning u∈[0, π/2], v∈[0, π/2].
# Corners in 3D:
#   A = (1,0,0)   (u=0,   v=0)
#   B = (0,1,0)   (u=π/2, v=0)
#   C = (0,0,1)   (u=any, v=π/2) — the north pole (singular)
# We form a triangular spherical patch with one degenerate edge at the pole.
# But to stay rectangular: add a second point at (u=π/2, v=π/2) which is also
# the north pole — we use a rectangular patch with v_c == v_d == north pole.
# Simpler: 4-edge loop with v_c and v_d coinciding at the pole.
# Use a quadrilateral with A=(1,0,0), B=(0,1,0), C_pole=(0,0,1), D_pole=(0,0,1).
# This degenerates to a triangle, but STEP allows it.

# 3D corner points
p_A = f.cartesian_point((1.0, 0.0, 0.0))   # u=0,    v=0
p_B = f.cartesian_point((0.0, 1.0, 0.0))   # u=pi/2, v=0
p_C = f.cartesian_point((0.0, 0.0, 1.0))   # north pole (degenerate)
p_D = f.cartesian_point((0.0, 0.0, 1.0))   # north pole again

v_A = f.vertex_point(p_A)
v_B = f.vertex_point(p_B)
v_C = f.vertex_point(p_C)
v_D = f.vertex_point(p_D)

# ── DEFECT EDGE A→C (meridian u=0, v from 0 to π/2): passes through pole ──────
# THE CATALOG MECHANISM: PCurve is LINE in UV from (0.0, 0.0) to (0.0, π/2).
# At v=π/2 the sphere metric collapses; CheckCurve3dWithPCurve NaN at pole.
# 3D: straight LINE from (1,0,0) to (0,0,1) along the u=0 meridian.
# The 3D "line" is the chord — on a unit sphere this is the straight-line chord,
# which OCC heals to the geodesic arc. Length = sqrt(2).
chord_len = math.sqrt(2.0)
chord_d   = f.direction((-1.0/chord_len, 0.0, 1.0/chord_len))
chord_v   = f.vector(chord_d, chord_len)
chord_3d  = f.line(p_A, chord_v)

# PCurve LINE in UV: (u=0, v=0) → (u=0, v=π/2) — passes through pole
pc_start_AC = f.cartesian_point((0.0, 0.0))
pc_dir_AC   = f.direction((0.0, 1.0))
pc_vec_AC   = f.vector(pc_dir_AC, math.pi / 2.0)
pc_line_AC  = f.line(pc_start_AC, pc_vec_AC)
defrep_AC = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pole_pc_def',(#{pc_line_AC.eid}),#{prc.eid})"
)
pcurve_AC = f._emit_raw(f"PCURVE('pole_pc',#{sphere.eid},#{defrep_AC.eid})")
sc_AC = f._emit_raw(
    f"SURFACE_CURVE('pole_sc',#{chord_3d.eid},(#{pcurve_AC.eid}),.PCURVE_S1.)"
)
e_AC = f._emit_raw(
    f"EDGE_CURVE('pole_edge',#{v_A.eid},#{v_C.eid},#{sc_AC.eid},.T.)"
)

# ── Clean edge B→D (meridian u=π/2, v from 0 to π/2) ─────────────────────────
# 3D: chord from (0,1,0) to (0,0,1)
chord_BD_len = math.sqrt(2.0)
chord_BD_d   = f.direction((0.0, -1.0/chord_BD_len, 1.0/chord_BD_len))
chord_BD_v   = f.vector(chord_BD_d, chord_BD_len)
chord_BD_3d  = f.line(p_B, chord_BD_v)

pc_start_BD = f.cartesian_point((math.pi / 2.0, 0.0))
pc_dir_BD   = f.direction((0.0, 1.0))
pc_vec_BD   = f.vector(pc_dir_BD, math.pi / 2.0)
pc_line_BD  = f.line(pc_start_BD, pc_vec_BD)
defrep_BD = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('right_spoke_pc_def',(#{pc_line_BD.eid}),#{prc.eid})"
)
pcurve_BD = f._emit_raw(f"PCURVE('right_spoke_pc',#{sphere.eid},#{defrep_BD.eid})")
sc_BD = f._emit_raw(
    f"SURFACE_CURVE('right_spoke_sc',#{chord_BD_3d.eid},(#{pcurve_BD.eid}),.PCURVE_S1.)"
)
e_BD = f._emit_raw(
    f"EDGE_CURVE('right_spoke_edge',#{v_B.eid},#{v_D.eid},#{sc_BD.eid},.T.)"
)

# ── Clean equator edge A→B (v=0, u from 0 to π/2) ────────────────────────────
# 3D: CIRCLE on sphere equator (v=0 plane), radius=1
eq_ctr   = f.cartesian_point((0.0, 0.0, 0.0))
eq_ax    = f.axis2_placement_3d(eq_ctr, zdir, xdir)
eq_circ  = f._emit_raw(f"CIRCLE('equator_circ',#{eq_ax.eid},1.0)")
# arc from u=0 to u=π/2
eq_trim  = f._emit_raw(
    f"TRIMMED_CURVE('eq_arc',#{eq_circ.eid},"
    f"(PARAMETER_VALUE(0.0)),(PARAMETER_VALUE({math.pi/2.0})),.T.,.PARAMETER.)"
)
# pcurve for equator: horizontal line in UV (v=0 fixed, u from 0 to π/2)
pc_eq_start = f.cartesian_point((0.0, 0.0))
pc_eq_dir   = f.direction((1.0, 0.0))
pc_eq_vec   = f.vector(pc_eq_dir, math.pi / 2.0)
pc_eq_line  = f.line(pc_eq_start, pc_eq_vec)
defrep_eq = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('equator_pc_def',(#{pc_eq_line.eid}),#{prc.eid})"
)
pcurve_eq = f._emit_raw(f"PCURVE('equator_pc',#{sphere.eid},#{defrep_eq.eid})")
sc_eq = f._emit_raw(
    f"SURFACE_CURVE('equator_sc',#{eq_trim.eid},(#{pcurve_eq.eid}),.PCURVE_S1.)"
)
e_AB = f._emit_raw(
    f"EDGE_CURVE('equator_edge',#{v_A.eid},#{v_B.eid},#{sc_eq.eid},.T.)"
)

# ── Degenerate top edge C→D (both are north pole — zero-length) ───────────────
# At the pole both C and D are the same 3D point; zero-length edge.
pole_pt_3d = f.cartesian_point((0.0, 0.0, 1.0))
pole_dir   = f.direction((1.0, 0.0, 0.0))
pole_vec   = f.vector(pole_dir, 1.0e-7)
pole_line  = f.line(pole_pt_3d, pole_vec)

pc_pole_start = f.cartesian_point((0.0, math.pi / 2.0))
pc_pole_dir   = f.direction((1.0, 0.0))
pc_pole_vec   = f.vector(pc_pole_dir, math.pi / 2.0)
pc_pole_line  = f.line(pc_pole_start, pc_pole_vec)
defrep_pole = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pole_top_pc_def',(#{pc_pole_line.eid}),#{prc.eid})"
)
pcurve_pole = f._emit_raw(f"PCURVE('pole_top_pc',#{sphere.eid},#{defrep_pole.eid})")
sc_pole = f._emit_raw(
    f"SURFACE_CURVE('pole_top_sc',#{pole_line.eid},(#{pcurve_pole.eid}),.PCURVE_S1.)"
)
e_CD = f._emit_raw(
    f"EDGE_CURVE('pole_top_edge',#{v_C.eid},#{v_D.eid},#{sc_pole.eid},.T.)"
)

# Loop: equator A→B (fwd), B→D spoke (fwd), pole top D→C (rev), C→A spoke (rev)
loop = f.edge_loop([
    f.oriented_edge(e_AB, True),
    f.oriented_edge(e_BD, True),
    f.oriented_edge(e_CD, False),
    f.oriented_edge(e_AC, False),
])
face  = f.advanced_face([f.face_outer_bound(loop)], sphere)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
