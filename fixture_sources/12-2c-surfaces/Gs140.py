"""Gs140 — ShapeAnalysis_Surface.IsVClosed Bezier pole-coincidence shortcut.

Catalog claim: IsVClosed() optimizes Bezier closure via knot-boundary check
but misses an edge case — first and last V-columns coincide spatially while
the parametric representation is not actually closed, so the shortcut
declares closure incorrectly.

Demonstration: degree-3-U × degree-3-V Bezier surface (4×4 control grid,
implicit knots). Row V=0 and row V=3 are spatially identical, so the
pole-coincidence shortcut sees closure. But the intermediate rows curve
through different Z values on the way around, so the surface is NOT a true
closed surface — derivative continuity at the seam is missing.
"""
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Gs140",
             defect="IsVClosed Bezier pole-coincidence shortcut")

# 4×4 Bezier control grid (degree 3×3, implicit knots).
# Row V=0 and row V=3 use the SAME X,Y,Z values — spatial coincidence —
# but rows V=1, V=2 lift in Z to make the surface non-trivial. The
# pole-coincidence shortcut in IsVClosed flags this as V-closed even
# though derivative continuity isn't enforced at the seam.
shared_row = [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0),
              (2.0, 0.0, 0.0), (3.0, 0.0, 0.0)]
v1_row = [(0.0, 1.0, 0.5), (1.0, 1.0, 1.5),
          (2.0, 1.0, 1.2), (3.0, 1.0, 0.5)]
v2_row = [(0.0, 2.0, 0.5), (1.0, 2.0, -0.5),
          (2.0, 2.0, -0.2), (3.0, 2.0, 0.5)]

rows = [shared_row, v1_row, v2_row, shared_row]
pts = [[f.cartesian_point(p) for p in row] for row in rows]

# Use _emit_raw for B_SPLINE_SURFACE with implicit-knot (Bezier) form.
# Nested list (LIST OF LIST OF CARTESIAN_POINT) is what STEP requires.
nested = ",".join("(" + ",".join(f"#{p.eid}" for p in row) + ")" for row in pts)
surf = f._emit_raw(
    f"B_SPLINE_SURFACE(3,3,({nested}),.UNSPECIFIED.,.F.,.F.,.F.)"
)

# Wrap surface in a minimal advanced_face so the fixture is consumable.
# Single dummy face boundary referencing the surface domain corners.
p0 = f.cartesian_point((0.0, 0.0, 0.0))
p1 = f.cartesian_point((3.0, 0.0, 0.0))
v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)
d = f.direction((1.0, 0.0, 0.0))
vec = f.vector(d, 3.0)
ln = f.line(p0, vec)
e0 = f.edge_curve(v0, v1, ln)
loop = f.edge_loop([f.oriented_edge(e0, True)])
face = f.advanced_face([f.face_outer_bound(loop)], surf)
shell = f.open_shell([face])
sbsm = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
