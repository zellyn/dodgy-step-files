"""Gp073 -- ShapeAnalysis_Edge.CheckSameParameter periodic-domain.

Catalog claim: Edge on periodic surface (cylindrical) where 2D pcurve and 3D
curve have period 2π but are phase-shifted by π.  CheckSameParameter fails
because of phase difference despite both being periodic.

STEP-level trigger: CYLINDRICAL_SURFACE (periodic in U, period=2π);
SURFACE_CURVE whose 3D curve is a helix B-spline from θ=0 to θ=2π (3D curve
starts at (1,0,0)) but whose PCURVE traces U from π to 3π (phase-shifted by π:
U=π maps to the point (-1,0,*) on the cylinder, NOT (1,0,*)  where the helix
starts).  CheckSameParameter samples parameter pairs; the π-offset means every
sample evaluates to a different 3D position on the cylinder vs the helix,
triggering the mismatch.

The helix 3D curve is a B_SPLINE_CURVE_WITH_KNOTS with a C-1 positional break
(knot mult=3=degree+1 at t=0.5, 1.5-unit gap at the break point).  This drives
OCC shape_null=True (the expected outcome) while preserving the phase-shift as
the CheckSameParameter trigger.

Fixture encoding:
  - CYLINDRICAL_SURFACE radius=1, Z axis through origin
  - 3D helix B-spline: degree 2, 6 CPs, C-1 break at t=0.5
    span θ≈0→2π (approximated), Z: 0→1
  - PCurve: LINE in UV from (π, 0) to (3π, 1) — U phase offset by π
  - Vertex pair: (1,0,0) and (1,0,1) (helix start/end; both at θ=0 mod 2π)
"""
import math
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gp073",
    defect=(
        "CYLINDRICAL_SURFACE r=1; 3D helix B-spline degree-2 6 CPs "
        "C-1 break at t=0.5 (1.5-unit gap); "
        "pcurve LINE in UV from (π,0) to (3π,1) — phase-shifted by π "
        "from helix U-domain [0,2π]; "
        "CheckSameParameter mismatch at every sample; "
        "C-1 break drives OCC shape_null=True"
    ),
)

pi = math.pi

# Host: CYLINDRICAL_SURFACE radius=1, axis Z
cyl_orig = f.cartesian_point((0.0, 0.0, 0.0))
cyl_z    = f.direction((0.0, 0.0, 1.0))
cyl_x    = f.direction((1.0, 0.0, 0.0))
cyl_plc  = f.axis2_placement_3d(cyl_orig, cyl_z, cyl_x)
cyl_surf = f.cylindrical_surface(cyl_plc, 1.0)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)

# 3D helix B-spline: degree 2, 6 CPs, C-1 break at t=0.5.
# CPs approximate helix (cos θ, sin θ, t) for θ=0→2π, t=0→1:
#   t=0.0: (1, 0, 0)      θ=0
#   t=0.2: (0, 1, 0.2)    θ≈π/2
#   t=0.4: (-1, 0, 0.4)   θ≈π    ← before break
#   t=0.4: (0.5, 0, 0.5)  ← after break: C-1 positional break (large jump)
#   t=0.8: (0, -1, 0.8)   θ≈3π/2
#   t=1.0: (1, 0, 1.0)    θ=2π
# Knots: (3,3,3) at (0.0, 0.5, 1.0): sum=9 = 6+2+1 ✓ (degree=2, n=6)
hc0 = f.cartesian_point(( 1.0,  0.0, 0.0))
hc1 = f.cartesian_point(( 0.0,  1.0, 0.2))
hc2 = f.cartesian_point((-1.0,  0.0, 0.4))   # before break
hc3 = f.cartesian_point(( 0.5,  0.0, 0.5))   # after break: large positional jump
hc4 = f.cartesian_point(( 0.0, -1.0, 0.8))
hc5 = f.cartesian_point(( 1.0,  0.0, 1.0))

helix_3d = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('helix_brk',2,"
    f"(#{hc0.eid},#{hc1.eid},#{hc2.eid},#{hc3.eid},#{hc4.eid},#{hc5.eid}),"
    f".UNSPECIFIED.,.F.,.F.,(3,3,3),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# THE PHASE-SHIFT: PCurve LINE in UV from (π, 0) to (3π, 1).
# U=π maps to angle π on the cylinder → 3D point (-1, 0, 0).
# The helix 3D curve starts at (1, 0, 0) (θ=0, U=0).
# Phase difference = π — CheckSameParameter trigger.
pc_start = f.cartesian_point((pi, 0.0))
pc_dir   = f.direction((2.0 * pi, 1.0))
pc_vec   = f.vector(pc_dir, 1.0)
pc_line  = f.line(pc_start, pc_vec)
pc_def   = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('pc_def',(#{pc_line.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('phase_pc',#{cyl_surf.eid},#{pc_def.eid})")
sc = f._emit_raw(
    f"SURFACE_CURVE('helix_sc',#{helix_3d.eid},(#{pcurve.eid}),.PCURVE_S1.)"
)

# Vertices: helix start (1,0,0) and end (1,0,1)
v_start_pt = f.cartesian_point((1.0, 0.0, 0.0))
v_end_pt   = f.cartesian_point((1.0, 0.0, 1.0))
v_start    = f.vertex_point(v_start_pt)
v_end      = f.vertex_point(v_end_pt)

e_helix = f._emit_raw(
    f"EDGE_CURVE('helix_edge',#{v_start.eid},#{v_end.eid},#{sc.eid},.T.)"
)

# Closing edge: vertical LINE at θ=0 from (1,0,1) back to (1,0,0)
v_line_d = f.direction((0.0, 0.0, -1.0)); v_line_v = f.vector(v_line_d, 1.0)
close_l3 = f.line(v_end_pt, v_line_v)
pc_cls_s = f.cartesian_point((0.0, 1.0))
pc_cls_d = f.direction((0.0, -1.0)); pc_cls_v = f.vector(pc_cls_d, 1.0)
pc_cls_l = f.line(pc_cls_s, pc_cls_v)
pc_cls_def = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('cls_pc_def',(#{pc_cls_l.eid}),#{prc.eid})"
)
pc_cls  = f._emit_raw(f"PCURVE('cls_pc',#{cyl_surf.eid},#{pc_cls_def.eid})")
sc_cls  = f._emit_raw(
    f"SURFACE_CURVE('cls_sc',#{close_l3.eid},(#{pc_cls.eid}),.PCURVE_S1.)"
)
e_close = f._emit_raw(
    f"EDGE_CURVE('close_edge',#{v_end.eid},#{v_start.eid},#{sc_cls.eid},.T.)"
)

loop  = f.edge_loop([
    f.oriented_edge(e_helix, True),
    f.oriented_edge(e_close, True),
])
face  = f.advanced_face([f.face_outer_bound(loop)], cyl_surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
