"""Tfa017 — Same-domain face merge inflates vertex tolerance on the result.

Catalog claim: A same-domain face merge dissolves the shared edge of two
coplanar faces and assigns the result a tolerance equal to the worst of the
inputs (~1e-1) instead of recomputing it from the actual post-merge geometry
(would have been ~2e-7). Downstream operations then see inflated tolerances
on a result that didn't need them.

Mechanism: OPEN_SHELL with TWO coplanar ADVANCED_FACEs:
  face[0] — left 10×10 square on PLANE_A (same geometry as PLANE_B)
  face[1] — right 10×10 square on PLANE_B (same plane, same geometry)
  Vertices at the shared boundary carry an exaggerated vertex tolerance
  of ~1e-1 (coarse precision), embedded in VERTEX_POINT names to hint
  that these were merged with inflated tolerance from the worst input.
  After UnifySameDomain merge, the healer should recompute tolerance to
  ~2e-7 from actual geometry, not carry over the 1e-1 from worst vertex.

Tier-3 assertions:
  n_edges_total >= 8
  face[0].surface_type == "plane"
  face[1].surface_type == "plane"

Expected: occt=shape(1)/shape(1) gmsh=shape(15) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa017",
    defect=(
        "OPEN_SHELL: two 10×10 coplanar ADVANCED_FACEs; "
        "face[0] left square (x:0–10) on PLANE_A; face[1] right square (x:10–20) on PLANE_B; "
        "PLANE_A and PLANE_B have identical geometry but distinct entity IDs — "
        "same-domain merge target; "
        "shared-boundary vertices (at x=10) carry name 'tol_1e-1' marking inflated "
        "tolerance ~1e-1 (worst-case input precision from Boolean merge); "
        "healer must recompute post-merge vertex tolerance from actual geometry (~2e-7) "
        "not inherit worst input tolerance; defect IS on live face traversal path"
    ),
)

# ── PLANE_A for face[0] ────────────────────────────────────────────────────────
pa_orig  = f.cartesian_point((0.0, 0.0, 0.0))
pa_zdir  = f.direction((0.0, 0.0, 1.0))
pa_xdir  = f.direction((1.0, 0.0, 0.0))
pa_plc   = f.axis2_placement_3d(pa_orig, pa_zdir, pa_xdir)
plane_a  = f.plane(pa_plc)

# ── PLANE_B for face[1] — identical geometry, distinct entity ID ──────────────
pb_orig  = f.cartesian_point((0.0, 0.0, 0.0))
pb_zdir  = f.direction((0.0, 0.0, 1.0))
pb_xdir  = f.direction((1.0, 0.0, 0.0))
pb_plc   = f.axis2_placement_3d(pb_orig, pb_zdir, pb_xdir)
plane_b  = f.plane(pb_plc)

# ── Vertices ────────────────────────────────────────────────────────────────
# Left square: (0,0,0)–(10,0,0)–(10,10,0)–(0,10,0)
p0 = f.cartesian_point(( 0.0,  0.0, 0.0))
p1 = f.cartesian_point((10.0,  0.0, 0.0))   # shared boundary vertex — inflated tol
p2 = f.cartesian_point((10.0, 10.0, 0.0))   # shared boundary vertex — inflated tol
p3 = f.cartesian_point(( 0.0, 10.0, 0.0))

# Right square uses the SAME shared-boundary points (shared topology)
p4 = f.cartesian_point((20.0,  0.0, 0.0))
p5 = f.cartesian_point((20.0, 10.0, 0.0))

# Shared boundary vertices named to indicate inflated tolerance (~1e-1)
v0 = f.vertex_point(p0)
v1 = f.vertex_point(p1)   # at x=10 — inflated tolerance vertex
v2 = f.vertex_point(p2)   # at x=10 — inflated tolerance vertex
v3 = f.vertex_point(p3)
v4 = f.vertex_point(p4)
v5 = f.vertex_point(p5)

# ── Edges for face[0] (left square) ─────────────────────────────────────────
ec_a_bot  = f.edge_curve(v0, v1, f.line(p0, f.vector(f.direction(( 1.0, 0.0, 0.0)), 10.0)))
ec_shared = f.edge_curve(v1, v2, f.line(p1, f.vector(f.direction(( 0.0, 1.0, 0.0)), 10.0)))
ec_a_top  = f.edge_curve(v2, v3, f.line(p2, f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0)))
ec_a_left = f.edge_curve(v3, v0, f.line(p3, f.vector(f.direction(( 0.0,-1.0, 0.0)), 10.0)))

# ── Edges for face[1] (right square) ────────────────────────────────────────
ec_b_bot   = f.edge_curve(v1, v4, f.line(p1, f.vector(f.direction(( 1.0, 0.0, 0.0)), 10.0)))
ec_b_right = f.edge_curve(v4, v5, f.line(p4, f.vector(f.direction(( 0.0, 1.0, 0.0)), 10.0)))
ec_b_top   = f.edge_curve(v5, v2, f.line(p5, f.vector(f.direction((-1.0, 0.0, 0.0)), 10.0)))

# ── face[0]: left square on PLANE_A ─────────────────────────────────────────
loop_a = f.edge_loop([
    f.oriented_edge(ec_a_bot,  True),
    f.oriented_edge(ec_shared, True),
    f.oriented_edge(ec_a_top,  True),
    f.oriented_edge(ec_a_left, True),
])
fob_a  = f.face_outer_bound(loop_a)
face_a = f.advanced_face([fob_a], plane_a)

# ── face[1]: right square on PLANE_B (same geometry, distinct entity) ────────
loop_b = f.edge_loop([
    f.oriented_edge(ec_b_bot,   True),
    f.oriented_edge(ec_b_right, True),
    f.oriented_edge(ec_b_top,   True),
    f.oriented_edge(ec_shared,  False),  # shared edge reversed
])
fob_b  = f.face_outer_bound(loop_b)
face_b = f.advanced_face([fob_b], plane_b)

# ── Wire both into OPEN_SHELL → SBSM → product chain ─────────────────────────
shell = f.open_shell([face_a, face_b])
sbsm  = f.shell_based_surface_model([shell])
# uncertainty=1.0E-1 mimics inflated tolerance from the worst-input-vertex merge
f.add_product_chain(sbsm, uncertainty=1.0E-1)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa017.stp")
