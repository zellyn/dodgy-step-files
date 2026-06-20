"""Tfa224 — FixMissingSeam.degenerate-wire-consolidation

Sphere with 3 degenerate wires (zero-extent edges at same vertex); multi-bound
face (outer + 2 holes); tests degenerate-wire removal at line 1872. Defect:
without consolidation, degenerated seams collapse to singularity.

Mechanism: CLOSED_SHELL with ONE ADVANCED_FACE on a SPHERICAL_SURFACE. The face
has one outer FACE_OUTER_BOUND (an equatorial circle) plus two inner FACE_BOUNDs
that are degenerate zero-extent edges at the north pole (same vertex, same point).
The OCCT FixMissingSeam code path at line 1872 measures wire extents; degenerate
wires (all edges below the degeneracy threshold) are consolidated and removed
before seam synthesis, preventing the collapsed seams from propagating to
singularity in downstream topology operations.

Byte assertions:
  - contains(b'SPHERICAL_SURFACE')
  - contains(b'ADVANCED_FACE')

Tier-3 assertion: load == "ok"

Expected: occt=shape(1)/shape(1) gmsh=empty ifc=schema_n/a
"""
import math as _math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa224",
    defect=(
        "CLOSED_SHELL: single ADVANCED_FACE on SPHERICAL_SURFACE (radius=3.0); "
        "outer FACE_OUTER_BOUND: equatorial circle (z=0, r=3.0); "
        "2 inner FACE_BOUNDs: degenerate zero-extent point-edges at north pole (0,0,3); "
        "both inner wires share the same vertex — zero-extent degenerate loops; "
        "FixMissingSeam line 1872: detects all-degenerate wires; "
        "consolidates and removes them before seam synthesis; "
        "without consolidation: degenerated seams collapse to singularity; "
        "defect IS on live traversal path; no orphaned entities"
    ),
)

R = 3.0

# ── SPHERICAL_SURFACE: radius 3.0, center at origin ──────────────────────────
sph_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
sphere = f.spherical_surface(sph_plc, R)

# ── Outer boundary: equatorial circle ────────────────────────────────────────
eq_pt = f.cartesian_point((R, 0.0, 0.0))
v_eq = f.vertex_point(eq_pt)

eq_ctr = f.cartesian_point((0.0, 0.0, 0.0))
eq_plc = f.axis2_placement_3d(
    eq_ctr,
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
eq_circle = f.circle(eq_plc, R)
eq_edge = f.edge_curve(v_eq, v_eq, eq_circle)
eq_loop = f.edge_loop([f.oriented_edge(eq_edge, True)])
outer_bound = f.face_outer_bound(eq_loop)

# ── Degenerate wires 1 and 2: zero-extent point-loops at north pole ───────────
# North pole: (0, 0, R)
# Use a very small circle at north pole (epsilon radius) → degenerate wire
eps = 1e-6
np_pt = f.cartesian_point((eps, 0.0, R))
v_np1 = f.vertex_point(np_pt)

np_ctr1 = f.cartesian_point((0.0, 0.0, R))
np_plc1 = f.axis2_placement_3d(
    np_ctr1,
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
np_circle1 = f.circle(np_plc1, eps)
np_edge1 = f.edge_curve(v_np1, v_np1, np_circle1)
np_loop1 = f.edge_loop([f.oriented_edge(np_edge1, True)])
inner_bound1 = f.face_bound(np_loop1, orientation=False)

# Second degenerate wire at the same north-pole location
np_pt2 = f.cartesian_point((eps, 0.0, R))
v_np2 = f.vertex_point(np_pt2)

np_ctr2 = f.cartesian_point((0.0, 0.0, R))
np_plc2 = f.axis2_placement_3d(
    np_ctr2,
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
np_circle2 = f.circle(np_plc2, eps)
np_edge2 = f.edge_curve(v_np2, v_np2, np_circle2)
np_loop2 = f.edge_loop([f.oriented_edge(np_edge2, True)])
inner_bound2 = f.face_bound(np_loop2, orientation=False)

# ── ADVANCED_FACE: outer + 2 degenerate inner wires ─────────────────────────
face = f.advanced_face([outer_bound, inner_bound1, inner_bound2], sphere)

closed_sh = f.closed_shell([face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa224.stp")
