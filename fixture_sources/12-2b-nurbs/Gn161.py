"""Gn161 — B-spline surface with asymmetric pole clustering.

Catalog claim: 5x2 NURBS (U-degree 2, V-degree 1); dense U-boundary clustering
at (0.9, 0.95, 1.0) with sparse V direction (2 poles only).
CheckSmallFace boundary-focused IsoStat must detect asymmetric singularities.
Falsifiable: pole-grid boundary scan catches strips missed by interior iteration.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS U-degree=2, V-degree=1, 5 U × 2 V poles.
    U knots (0.0, 0.9, 0.95, 1.0) mults (3,1,1,3) sum=8=5+2+1 ✓.
    V knots (0.0, 1.0) mults (2,2) sum=4=2+1+1 ✓.
    Last 3 U-knots compressed into (0.9,0.95,1.0) → dense boundary clustering.
    V direction has only 2 poles → strip degenerate in V.
    IS the face surface.
  - C-1 DRIVER: asymmetric boundary clustering forces zero-area strip detection
    via IsoStat → shape(1)/shape(1) (live OCC heals).

Mechanism vs driver:
  - CATALOG MECHANISM: 5x2 B_SPLINE_SURFACE_WITH_KNOTS; U-knots (0.0,0.9,0.95,1.0)
    mults (3,1,1,3); dense last 3 intervals (0.9→0.95→1.0); V only 2 poles
    (linear strip); IS face surface.
  - C-1 DRIVER: boundary pole strip singularity + dense V strip → shape(1)/shape(1) (live OCC heals).
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn161",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS U-degree=2 V-degree=1, 5x2 poles; "
        "U knots (0.0,0.9,0.95,1.0) mults (3,1,1,3) sum=8=5+2+1 ✓; "
        "V knots (0.0,1.0) mults (2,2) sum=4=2+1+1 ✓; "
        "dense U-boundary clustering (0.9,0.95,1.0) + V strip (2 poles only); "
        "IS face surface; asymmetric boundary singularity → shape(1)/shape(1) (live OCC heals)"
    ),
)

# ── CATALOG MECHANISM: 5x2 B-spline surface, clustered U-boundary ─────────────
# 5 U-rows × 2 V-cols; U-degree=2, V-degree=1.
# U knots: (0.0,0.9,0.95,1.0) mults (3,1,1,3) sum=8=5+2+1 ✓
# V knots: (0.0,1.0) mults (2,2) sum=4=2+1+1 ✓
# Last 3 U intervals packed into [0.9,1.0] → ill-conditioned boundary strip.
pts = [[f.cartesian_point(p) for p in row] for row in [
    [(0.0,  0.0, 0.0), (0.0,  1.0, 0.0)],   # U=0 (sparse region start)
    [(0.45, 0.0, 0.1), (0.45, 1.0, 0.1)],   # U=1
    [(0.90, 0.0, 0.1), (0.90, 1.0, 0.1)],   # U=2 (clustering begins)
    [(0.95, 0.0, 0.0), (0.95, 1.0, 0.0)],   # U=3 (dense)
    [(1.00, 0.0, 0.0), (1.00, 1.0, 0.0)],   # U=4 (boundary collapse)
]]

grid = ",".join("(" + ",".join(f"#{p.eid}" for p in row) + ")" for row in pts)
surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gn161_asymmetric_cluster',2,1,"
    f"({grid}),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(3,1,1,3),(2,2),"
    f"(0.0,0.9,0.95,1.0),(0.0,1.0),"
    f".UNSPECIFIED.)"
)

# ── Minimal face wiring: surf IS the face surface ─────────────────────────────
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((1.0, 0.0, 0.0))
v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
d  = f.direction((1.0, 0.0, 0.0))
vec = f.vector(d, 1.0)
ln  = f.line(p0, vec)
e0  = f.edge_curve(v0, v1, ln)
loop = f.edge_loop([f.oriented_edge(e0, True)])
face = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
