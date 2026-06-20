"""Gn159 — B-spline surface with collapsed U-boundary pole (pin-face singularity).

Catalog claim: 4x3 NURBS surface (U-degree 2, V-degree 2); last U-row poles all
at (3.0,1.5,0.0). CheckPin detects singularity; FixPinFace unimplemented.
Falsifiable: pin-face repair must flatten degenerate boundary edge.

STEP mechanism (literal):
  - B_SPLINE_SURFACE_WITH_KNOTS U-degree=2, V-degree=2, 4 U × 3 V poles.
    Last U-row: all poles collapsed to (3.0, 1.5, 0.0) → degenerate boundary.
    U knots (0.0, 1.0) mults (3,3) sum=6=4+2 ✓.
    V knots (0.0, 1.0) mults (3,3) sum=6=3+2+1=6 ✓.
    IS the face surface.
  - C-1 DRIVER: collapsed pole row → pin-face singularity; FixPinFace
    unimplemented → shape(1)/shape(1) (live OCC heals).

Mechanism vs driver:
  - CATALOG MECHANISM: 4x3 B_SPLINE_SURFACE_WITH_KNOTS with all last-U-row
    poles collapsed to single point (3.0,1.5,0.0); IS face surface.
  - C-1 DRIVER: pin-face boundary singularity; FixPinFace not available
    → shape(1)/shape(1) (live OCC heals); live oracle: shape(1)/shape(1).
"""
from step_corpus.step_builder import StepFile

f = StepFile(
    catalog_id="Gn159",
    defect=(
        "B_SPLINE_SURFACE_WITH_KNOTS U-degree=2 V-degree=2, 4x3 poles; "
        "last U-row all collapsed to (3.0,1.5,0.0) → pin-face singularity; "
        "U knots (0.0,1.0) mults (3,3) sum=6 ✓; V knots (0.0,1.0) mults (3,3) sum=6 ✓; "
        "IS face surface; FixPinFace unimplemented → shape(1)/shape(1) (live OCC heals)"
    ),
)

# ── CATALOG MECHANISM: 4x3 B-spline surface, last U-row collapsed ─────────────
# 4 U-rows × 3 V-cols; U-degree=2, V-degree=2.
# U knots: (0.0,1.0) mults (3,3) → sum=6=4+2 ✓  (clamped, 4 poles U)
# V knots: (0.0,1.0) mults (3,3) → sum=6=3+2+1=6 ✓ (clamped, 3 poles V)
# Row 0..2 normal; row 3 all collapsed to (3.0,1.5,0.0).
pts = [[f.cartesian_point(p) for p in row] for row in [
    [(0.0, 0.0, 0.0), (0.0, 1.5, 0.0), (0.0, 3.0, 0.0)],   # U=0
    [(1.0, 0.0, 0.2), (1.0, 1.5, 0.4), (1.0, 3.0, 0.2)],   # U=1
    [(2.0, 0.0, 0.1), (2.0, 1.5, 0.3), (2.0, 3.0, 0.1)],   # U=2
    [(3.0, 1.5, 0.0), (3.0, 1.5, 0.0), (3.0, 1.5, 0.0)],   # U=3 COLLAPSED
]]

grid = ",".join("(" + ",".join(f"#{p.eid}" for p in row) + ")" for row in pts)
surf = f._emit_raw(
    f"B_SPLINE_SURFACE_WITH_KNOTS('gn159_pin_face',2,2,"
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
