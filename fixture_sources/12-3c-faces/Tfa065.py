"""Tfa065 — Healed face uses inflated tolerance instead of original.

Catalog claim: A face whose constituent edges have native tolerance ~1e-7
goes through a healing pass that inflates the face-level tolerance to ~1e-1
to absorb a single localised gap. The bloated tolerance then contaminates
all downstream operations on the face.

Mechanism: OPEN_SHELL with TWO faces:
  face[0] (defective): ADVANCED_FACE on a PLANE with four edges. Three edges
    are exactly connected (tolerance 1e-7). The fourth edge has a 1e-3 gap
    between its start vertex and the previous edge's end vertex. After healing,
    the face tolerance is inflated to ~1e-1 (far above the worst gap of 1e-3).
    The defect is the gap: vertex v3_end at (0.0, 100.0+1e-3, 0.0) starts the
    last edge instead of (0.0, 100.0, 0.0) — a 1e-3 gap.
  face[1] (reference): valid 100×100 plane at z=-10 ensuring shape(1).

The face heals (OCC inflates tolerance); loads as shape(1).

Tier-3 assertions:
  n_edges_total >= 4
  face[0].surface_type == "plane"
  n_vertices_total >= 8

Expected: occt=shape(1)/shape(1) gmsh=shape(9) ifc=schema_n/a
"""
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa065",
    defect=(
        "OPEN_SHELL: face[0] on PLANE at z=0; "
        "outer EDGE_LOOP: three good edges (tol~1e-7); "
        "fourth edge starts at (0.0, 100.001, 0.0) — 1e-3 gap from prev edge end (0.0, 100.0, 0.0); "
        "healer inflates face-level tolerance to ~1e-1 to absorb 1e-3 gap "
        "(orders of magnitude above measured max deviation); "
        "ShapeUpgrade_UnifySameDomain tolerance pollution condition; "
        "face[1] valid 100x100 plane at z=-10 ensures shape(1); "
        "defect IS on live OPEN_SHELL traversal path"
    ),
)

GAP = 1e-3  # gap between v2 end and v3 start

# ── face[0]: rectangular face with one gapped vertex ──────────────────────────
# Wire: (0,0) → (100,0) → (100,100) → gap! → (0,100.001) → (0,0)
# The gap is between edge[1] end at (100,100,0) and edge[2] start at (100,100,0)
# (those are fine), but edge[2] end is (0,100,0) and edge[3] start is (0,100+GAP,0).

p0 = f.cartesian_point((  0.0,         0.0, 0.0))   # BL
p1 = f.cartesian_point((100.0,         0.0, 0.0))   # BR
p2 = f.cartesian_point((100.0,       100.0, 0.0))   # TR
p3 = f.cartesian_point((  0.0,       100.0, 0.0))   # TL — good end of edge[2]
p3g = f.cartesian_point(( 0.0, 100.0+GAP,  0.0))   # TL with GAP — start of edge[3] (DEFECT)

v0  = f.vertex_point(p0)
v1  = f.vertex_point(p1)
v2  = f.vertex_point(p2)
v3  = f.vertex_point(p3)   # edge[2] ends here
v3g = f.vertex_point(p3g)  # edge[3] starts here — 1e-3 gap from v3

import math as _math
L30g = _math.sqrt((0.0-0.0)**2 + (100.0+GAP)**2)

ec0 = f.edge_curve(v0,  v1,  f.line(p0,  f.vector(f.direction(( 1.0, 0.0, 0.0)), 100.0)))
ec1 = f.edge_curve(v1,  v2,  f.line(p1,  f.vector(f.direction(( 0.0, 1.0, 0.0)), 100.0)))
ec2 = f.edge_curve(v2,  v3,  f.line(p2,  f.vector(f.direction((-1.0, 0.0, 0.0)), 100.0)))
# edge[3]: starts at v3g (1e-3 above v3) — the localised gap
ec3 = f.edge_curve(v3g, v0,  f.line(p3g, f.vector(f.direction(( 0.0,-1.0, 0.0)), L30g)))

defect_loop = f.edge_loop([
    f.oriented_edge(ec0, True),
    f.oriented_edge(ec1, True),
    f.oriented_edge(ec2, True),
    f.oriented_edge(ec3, True),
])

pl0_orig = f.cartesian_point((0.0, 0.0, 0.0))
plane0   = f.plane(f.axis2_placement_3d(
    pl0_orig, f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0))
))
face0 = f.advanced_face([f.face_outer_bound(defect_loop)], plane0)

# ── face[1]: valid 100×100 reference plane at z=-10 ───────────────────────────
r0 = f.cartesian_point((  0.0,   0.0, -10.0))
r1 = f.cartesian_point((100.0,   0.0, -10.0))
r2 = f.cartesian_point((100.0, 100.0, -10.0))
r3 = f.cartesian_point((  0.0, 100.0, -10.0))

rv0 = f.vertex_point(r0); rv1 = f.vertex_point(r1)
rv2 = f.vertex_point(r2); rv3 = f.vertex_point(r3)

re0 = f.edge_curve(rv0, rv1, f.line(r0, f.vector(f.direction(( 1.0, 0.0, 0.0)), 100.0)))
re1 = f.edge_curve(rv1, rv2, f.line(r1, f.vector(f.direction(( 0.0, 1.0, 0.0)), 100.0)))
re2 = f.edge_curve(rv2, rv3, f.line(r2, f.vector(f.direction((-1.0, 0.0, 0.0)), 100.0)))
re3 = f.edge_curve(rv3, rv0, f.line(r3, f.vector(f.direction(( 0.0,-1.0, 0.0)), 100.0)))

ref_loop = f.edge_loop([
    f.oriented_edge(re0, True), f.oriented_edge(re1, True),
    f.oriented_edge(re2, True), f.oriented_edge(re3, True),
])
plane1 = f.plane(f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, -10.0)), f.direction((0.0, 0.0, 1.0)), f.direction((1.0, 0.0, 0.0))
))
face1 = f.advanced_face([f.face_outer_bound(ref_loop)], plane1)

# ── OPEN_SHELL ────────────────────────────────────────────────────────────────
shell = f.open_shell([face0, face1])
sbsm  = f.shell_based_surface_model([shell])
f.add_product_chain(sbsm)
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa065.stp")
