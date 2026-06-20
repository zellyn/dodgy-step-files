"""Gn163 — B-spline surface with degenerate patch from split.

Catalog claim: 3x3 NURBS (U-degree 2, V-degree 2); middle U-row poles
near-identical (1.5, 1.5, 0.01). SplitSurface produces zero-area or empty patches.
Falsifiable: patch validation rejects degenerate outputs from split operations.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS U-degree=2, V-degree=2, 3 U × 3 V poles.
    Middle U-row (U=1): all poles compressed to (1.5, *, 0.01) — near-identical
    X and Z, only Y varies. This collapses the middle row into a near-line,
    making both sub-patches (U<1 and U>1) degenerate / zero-area after split.
    U knots (0.0, 1.0) mults (3,3) sum=6=3+2+1 ✓.
    V knots (0.0, 1.0) mults (3,3) sum=6=3+2+1 ✓.
    IS the face surface.
  - C-1 DRIVER: near-degenerate middle row produces zero-area sub-patches
    from SplitSurface → shape(1)/shape(1) (live OCC heals).

Mechanism vs driver:
  - CATALOG MECHANISM: 3x3 B_SPLINE_SURFACE_WITH_KNOTS; middle U-row poles
    near-identical (1.5,*,0.01) → degenerate midpoint row; IS face surface.
  - C-1 DRIVER: SplitSurface produces zero-area patches → shape(1)/shape(1) (live OCC heals);
    live oracle: shape(1)/shape(1).
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn163",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS U-degree=2 V-degree=2, 3x3 poles; "
        "middle U-row poles near-identical (1.5,*,0.01) → near-degenerate row; "
        "U knots (0.0,1.0) mults (3,3) sum=6=3+2+1 ✓; "
        "V knots (0.0,1.0) mults (3,3) sum=6=3+2+1 ✓; "
        "IS face surface; SplitSurface produces zero-area patches → shape(1)/shape(1) (live OCC heals)"
    ),
)

# ── CATALOG MECHANISM: 3x3 B-spline surface, degenerate middle U-row ──────────
# 3 U-rows × 3 V-cols; U-degree=2, V-degree=2.
# U knots: (0.0,1.0) mults (3,3) sum=6=3+2+1 ✓
# V knots: (0.0,1.0) mults (3,3) sum=6=3+2+1 ✓
# Middle U-row: X=1.5, Z=0.01 (near-identical across V) → collapsed strip.
pts = [[f.cartesian_point(p) for p in row] for row in [
    [(0.0, 0.0, 0.0), (0.0, 1.5, 0.0), (0.0, 3.0, 0.0)],         # U=0 normal
    [(1.5, 0.0, 0.01), (1.5, 1.5, 0.01), (1.5, 3.0, 0.01)],      # U=1 NEAR-DEGENERATE
    [(3.0, 0.0, 0.0), (3.0, 1.5, 0.0), (3.0, 3.0, 0.0)],         # U=2 normal
]]

grid = ",".join("(" + ",".join(f"#{p.eid}" for p in row) + ")" for row in pts)
surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gn163_degenerate_mid',2,2,"
    f"({grid}),"
    f".UNSPECIFIED.,.F.,.F.,.F.,"
    f"(3,3),(3,3),"
    f"(0.0,1.0),(0.0,1.0),"
    f".UNSPECIFIED.)"
)

# ── Minimal face wiring: surf IS the face surface ─────────────────────────────
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((3.0, 0.0, 0.0))
v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
d  = f.direction((1.0, 0.0, 0.0))
vec = f.vector(d, 3.0)
ln  = f.line(p0, vec)
e0  = f.edge_curve(v0, v1, ln)
loop = f.edge_loop([f.oriented_edge(e0, True)])
face = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
