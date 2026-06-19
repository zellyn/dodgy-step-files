"""Gp008 — Pcurve oscillations producing wire-intersector corruption.

Catalog claim: a pcurve produced by projecting a 3D curve onto a host
surface oscillates at high frequency; the projector lacks adaptive
sampling. A subsequent wire self-intersection check mis-detects the
oscillations as crossings and corrupts wire topology.

Fixture (rebuilt 2026-06-19 per Sonnet verify): the host MUST be a
B_SPLINE_SURFACE_WITH_KNOTS — the catalog's specific defect class is
non-adaptive projection onto a NURBS surface; projecting onto a flat
PLANE is trivial and doesn't demonstrate the claim. The 3D edge runs
near a curved boundary of the host; the resulting 2D pcurve is a
B-spline whose control polygon oscillates in V (alternating large /
small displacements), plausibly the output of a fixed-step projector
that under-samples the surface curvature near the boundary.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gp008",
             defect="pcurve oscillations on B_SPLINE_SURFACE_WITH_KNOTS host (non-adaptive projection)")


def cp(*coords):
    return f.cartesian_point(coords)


# B_SPLINE_SURFACE_WITH_KNOTS host — 4x4 control net, bi-degree 2.
# The v=0 row has bumps in z that an adaptive projector would catch
# but a fixed-step one would alias to oscillations in pcurve space.
net = [
    [cp(0.0, 0.0, 0.0),  cp(1.0, 0.0, 0.4),  cp(2.0, 0.0, 0.4),  cp(3.0, 0.0, 0.0)],
    [cp(0.0, 0.3, 0.0),  cp(1.0, 0.3, 0.8),  cp(2.0, 0.3, 0.8),  cp(3.0, 0.3, 0.0)],
    [cp(0.0, 0.7, 0.0),  cp(1.0, 0.7, 0.5),  cp(2.0, 0.7, 0.5),  cp(3.0, 0.7, 0.0)],
    [cp(0.0, 1.0, 0.0),  cp(1.0, 1.0, 0.0),  cp(2.0, 1.0, 0.0),  cp(3.0, 1.0, 0.0)],
]
flat_rows = ["(" + ",".join(f"#{p.eid}" for p in row) + ")" for row in net]
cp_grid = "(" + ",".join(flat_rows) + ")"
host_surface = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('host_nurbs',2,2,{cp_grid},"
    f".UNSPECIFIED.,.F.,.F.,.F.,(3,1,3),(3,1,3),(0.0,0.5,1.0),(0.0,0.5,1.0),.UNSPECIFIED.)"
)

# 3D edge runs near the curved v=0 boundary of the surface.
p0 = cp(0.5, 0.05, 0.15)
p1 = cp(2.5, 0.05, 0.15)
v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
dir3d = f.direction((1.0, 0.0, 0.0))
vec3d = f.vector(dir3d, 2.0)
curve_3d = f.line(p0, vec3d)

# Oscillating 2D pcurve: 13 control points whose V values alternate with
# growing amplitude, producing 11+ sign changes of the second derivative.
# Plausibly the output of a fixed-step projector that aliases the host's
# subtle curvature in the v<0.5 region into high-frequency oscillation.
osc_pts = [
    f.cartesian_point((0.17, 0.20)),
    f.cartesian_point((0.22, 0.50)),
    f.cartesian_point((0.27, 0.15)),
    f.cartesian_point((0.33, 0.55)),
    f.cartesian_point((0.39, 0.12)),
    f.cartesian_point((0.45, 0.58)),
    f.cartesian_point((0.51, 0.10)),
    f.cartesian_point((0.57, 0.60)),
    f.cartesian_point((0.63, 0.13)),
    f.cartesian_point((0.69, 0.56)),
    f.cartesian_point((0.75, 0.17)),
    f.cartesian_point((0.81, 0.50)),
    f.cartesian_point((0.83, 0.22)),
]
osc_refs = ",".join(f"#{p.eid}" for p in osc_pts)
# Degree-3 B-spline; n=13 control points → 13+3+1=17 knot multiplicity entries.
# Open uniform knots clamped at endpoints (mults 4,4) with 9 interior simple knots.
pcurve_basis = f._emit_raw(
    f"B_SPLINE_CURVE_WITH_KNOTS('osc_pcurve',3,({osc_refs}),"
    f".UNSPECIFIED.,.F.,.F.,(4,1,1,1,1,1,1,1,1,1,4),"
    f"(0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0),.UNSPECIFIED.)"
)

prc = f._emit_raw(
    "(GEOMETRIC_REPRESENTATION_CONTEXT(2)PARAMETRIC_REPRESENTATION_CONTEXT()"
    "REPRESENTATION_CONTEXT('UV','2D'))"
)
defrep = f._emit_raw(
    f"DEFINITIONAL_REPRESENTATION('osc_pcurve_def',(#{pcurve_basis.eid}),#{prc.eid})"
)
pcurve = f._emit_raw(f"PCURVE('uv_curve',#{host_surface.eid},#{defrep.eid})")

surface_curve = f._emit_raw(
    f"SURFACE_CURVE('edge_with_osc_pcurve',#{curve_3d.eid},"
    f"(#{pcurve.eid}),.PCURVE_S1.)"
)
edge = f._emit_raw(
    f"EDGE_CURVE('osc_edge',#{v0.eid},#{v1.eid},#{surface_curve.eid},.T.)"
)

# PRODUCT chain so the fixture loads as a real shape.
loop = f.edge_loop([f.oriented_edge(edge, True)])
fob = f.face_outer_bound(loop)
face = f._emit_raw(
    f"ADVANCED_FACE('face_on_nurbs',(#{fob.eid}),#{host_surface.eid},.T.)"
)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
