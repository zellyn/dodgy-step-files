"""Tfa214 — ShapeFix_Face.FixMissingSeam.degenerate-wire-consolidation

B-spline surface with degenerate EDGE_LOOP (all edges ~0.001 mm, same
endpoints). Tests degenerate-wire-consolidation path that collapses short
edges into single vertex before seam synthesis.

Mechanism: CLOSED_SHELL with ONE ADVANCED_FACE on a B_SPLINE_SURFACE_WITH_KNOTS.
The B-spline is a flat degree-1 unit-square patch. The face outer boundary is a
quad EDGE_LOOP whose edges have length ~0.001 mm — all four edges are ~0.001 mm
long and share nearly coincident vertices at (0.5, 0.5, 0). The OCCT
ShapeFix_Face.FixMissingSeam code path at line 1872 measures the edge lengths of
the wire, detects that all edges are below the degeneracy threshold (~0.001 mm),
and consolidates the wire to a minimal representation (single vertex or point-
based correction) rather than attempting seam synthesis on the collapsed geometry.

Byte assertions:
  - contains(b'B_SPLINE_SURFACE_WITH_KNOTS')
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa214",
    defect=(
        "CLOSED_SHELL: single ADVANCED_FACE on B_SPLINE_SURFACE_WITH_KNOTS; "
        "flat unit-square patch (degree 1, 2×2 control net); "
        "degenerate EDGE_LOOP: 4 micro-edges each ~0.001 mm, all vertices at (0.5,0.5,0); "
        "FixMissingSeam line 1872: degenerate-wire-consolidation detects sub-threshold lengths; "
        "collapses wire to minimal vertex representation before seam synthesis; "
        "prevents spurious seam synthesis on collapsed geometry; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

# ── B_SPLINE_SURFACE_WITH_KNOTS: flat unit square ─────────────────────────────
cp00 = f.cartesian_point((0.0, 0.0, 0.0))
cp01 = f.cartesian_point((0.0, 1.0, 0.0))
cp10 = f.cartesian_point((1.0, 0.0, 0.0))
cp11 = f.cartesian_point((1.0, 1.0, 0.0))

bspline_surf = f.b_spline_surface_with_knots(
    1, 1,
    [[cp00, cp01], [cp10, cp11]],
    [2, 2], [2, 2],
    [0.0, 1.0], [0.0, 1.0],
    surface_form="UNSPECIFIED",
    u_closed=False,
    v_closed=False,
    self_intersect=False,
)

# ── Degenerate EDGE_LOOP: 4 micro-edges ~0.001 mm, all nearly at (0.5, 0.5, 0)
# Vertices form a tiny square side = 0.001 mm centered at (0.5, 0.5, 0)
s = 0.001   # 0.001 mm — below OCCT degeneracy threshold
cx, cy = 0.5, 0.5

mp_ll = f.cartesian_point((cx,       cy,       0.0))
mp_lr = f.cartesian_point((cx + s,   cy,       0.0))
mp_ur = f.cartesian_point((cx + s,   cy + s,   0.0))
mp_ul = f.cartesian_point((cx,       cy + s,   0.0))

mv_ll = f.vertex_point(mp_ll)
mv_lr = f.vertex_point(mp_lr)
mv_ur = f.vertex_point(mp_ur)
mv_ul = f.vertex_point(mp_ul)

me_bot = f.edge_curve(mv_ll, mv_lr, f.line(mp_ll, f.vector(f.direction(( 1.0, 0.0, 0.0)), s)))
me_rgt = f.edge_curve(mv_lr, mv_ur, f.line(mp_lr, f.vector(f.direction(( 0.0, 1.0, 0.0)), s)))
me_top = f.edge_curve(mv_ur, mv_ul, f.line(mp_ur, f.vector(f.direction((-1.0, 0.0, 0.0)), s)))
me_lft = f.edge_curve(mv_ul, mv_ll, f.line(mp_ul, f.vector(f.direction(( 0.0,-1.0, 0.0)), s)))

micro_loop = f.edge_loop([
    f.oriented_edge(me_bot, True),
    f.oriented_edge(me_rgt, True),
    f.oriented_edge(me_top, True),
    f.oriented_edge(me_lft, True),
])
face = f.advanced_face([f.face_outer_bound(micro_loop)], bspline_surf)

closed_sh = f.closed_shell([face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa214.stp")
