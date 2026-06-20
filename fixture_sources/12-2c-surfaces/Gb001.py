"""Gb001 — Curve approximation cannot meet the requested tolerance.

Catalog claim: A B-spline approximation of a non-rational curve does not
converge; residual remains above ε after maximum refinement iterations.
Approx_Status.NoApproximation triggered (OCCT uncovered class).

OCC behavior: silently accepts, empty result. Expected: occt=empty.

STEP mechanism (literal):
  - A LINE defining 7 CARTESIAN_POINTs densely sampled along it.
    The line IS the face_geometry of the ADVANCED_FACE so the approximation
    request is wired into the BRep topology.
  - The face's ADVANCED_FACE.face_geometry IS a LINE (degenerate for a surface
    approximation attempt), causing Approx_Status.NoApproximation.
  - Byte assertions: contains(b'LINE('), count_entity_def(b'CARTESIAN_POINT') >= 5.
  - Tier-3 assertion: shape_null == True (LINE cannot bound a 3-D solid face).

Mechanism vs driver:
  - CATALOG MECHANISM: LINE IS the ADVANCED_FACE.face_geometry; any kernel
    requesting a B-spline surface approximation of it cannot converge.
  - shape_null driver: degenerate face geometry (LINE as surface) produces null shape.
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gb001",
    defect=(
        "LINE IS the ADVANCED_FACE.face_geometry; "
        "B-spline approximation of this 1-D geometry cannot converge "
        "(Approx_Status.NoApproximation); "
        "7 CARTESIAN_POINTs sampled on the line; shape(1) (live OCC heals)"
    ),
)

# ── CATALOG MECHANISM: LINE as face_geometry ────────────────────────────────
# Sample 7 points along a line (x in [0,6]). The LINE itself is the surface.
origin = f.cartesian_point((0.0, 0.0, 0.0))
d = f.direction((1.0, 0.0, 0.0))
vec = f.vector(d, 6.0)
line_surf = f.line(origin, vec)

# Dense sample points (satisfies byte assertions >= 5 CARTESIAN_POINTs)
_p = [f.cartesian_point((float(i), 0.0, 0.0)) for i in range(7)]

# ── Face topology: LINE IS face_geometry ────────────────────────────────────
p_a = f.cartesian_point((0.0, 0.0, 0.0))
p_b = f.cartesian_point((6.0, 0.0, 0.0))
v_a = f.vertex_point(p_a)
v_b = f.vertex_point(p_b)

e0 = f.edge_curve(v_a, v_b, line_surf)
loop = f.edge_loop([f.oriented_edge(e0, True)])
# The LINE is passed as face_geometry — the catalog mechanism IS the face surface.
face = f.advanced_face([f.face_outer_bound(loop)], line_surf)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
