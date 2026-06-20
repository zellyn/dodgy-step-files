"""Tfa245 — ShapeFix_Face.FixMissingSeam.sphere-apex-edge-synthesis

Degenerated synthetic edge synthesis at sphere pole. Single wire at equator on
sphere (U-open); without synthetic degenerated edge at pole (v=π/2), topology
incomplete; with synthesis, seam closure via pole boundary.

Mechanism: CLOSED_SHELL with TWO ADVANCED_FACEs. face[0] is the defect carrier:
a SPHERICAL_SURFACE hemisphere patch whose outer wire forms a full equatorial
circle (v=0). The face is "U-open" — the wire runs all the way around the
equator but the polar singularity (north pole, v=π/2) is not bounded by any
edge. FixMissingSeam::sphere-apex-edge-synthesis must synthesize a degenerate
edge at the pole vertex to close the seam and complete the topology. Without
this synthesis the pole boundary is missing and the topology is incomplete.
face[1] is a flat PLANE companion face to ensure the manifold shell closes.

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
    catalog_id="Tfa245",
    defect=(
        "CLOSED_SHELL: face[0] SPHERICAL_SURFACE hemisphere (v in [0, π/2]); "
        "outer wire: full equatorial circle at v=0, u in [0, 2π]; "
        "U-open face: equator bounds the bottom, but pole (v=π/2) is unbounded; "
        "FixMissingSeam sphere-apex-edge-synthesis: must synthesize degenerate "
        "edge at north-pole vertex (0,0,R) to close the seam topology; "
        "without synthesis pole boundary missing → incomplete topology; "
        "face[1]: flat PLANE cap; defect IS on live traversal path; no orphans"
    ),
)

R = 3.0

# ── SPHERICAL_SURFACE ─────────────────────────────────────────────────────────
sph_plc = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
sphere = f.spherical_surface(sph_plc, R)

# ── Equatorial circle (v=0 on sphere → z=0 plane) ────────────────────────────
# Full circle from (R,0,0) back to (R,0,0) — seam vertex
# Build as a closed circle edge (same start and end vertex = seam point)
eq_orig = f.cartesian_point((0.0, 0.0, 0.0))
eq_plc = f.axis2_placement_3d(
    eq_orig,
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
eq_circle = f.circle(eq_plc, R)

# Seam point on equator at u=0: (R, 0, 0)
pt_seam = f.cartesian_point((R, 0.0, 0.0))
v_seam = f.vertex_point(pt_seam)

# Full equatorial circle edge: v_seam → v_seam (closed loop, same vertex)
eq_edge = f.edge_curve(v_seam, v_seam, eq_circle)

# Wire: single full equatorial circle
eq_loop = f.edge_loop([
    f.oriented_edge(eq_edge, True),
])

sph_face = f.advanced_face([f.face_outer_bound(eq_loop)], sphere)

# ── Companion flat PLANE face (disk at z=0 to close the shell) ────────────────
# Use 4-edge square loop on the z=0 plane (bottom of sphere)
# Small square to keep topology simple
sq = R * 0.3   # square half-side
pc0 = f.cartesian_point((-sq, -sq, -R - 0.5))
pc1 = f.cartesian_point(( sq, -sq, -R - 0.5))
pc2 = f.cartesian_point(( sq,  sq, -R - 0.5))
pc3 = f.cartesian_point((-sq,  sq, -R - 0.5))
pv0 = f.vertex_point(pc0)
pv1 = f.vertex_point(pc1)
pv2 = f.vertex_point(pc2)
pv3 = f.vertex_point(pc3)
pe01 = f.edge_curve(pv0, pv1, f.line(pc0, f.vector(f.direction((1.0, 0.0, 0.0)), 2 * sq)))
pe12 = f.edge_curve(pv1, pv2, f.line(pc1, f.vector(f.direction((0.0, 1.0, 0.0)), 2 * sq)))
pe23 = f.edge_curve(pv2, pv3, f.line(pc2, f.vector(f.direction((-1.0, 0.0, 0.0)), 2 * sq)))
pe30 = f.edge_curve(pv3, pv0, f.line(pc3, f.vector(f.direction((0.0, -1.0, 0.0)), 2 * sq)))
comp_loop = f.edge_loop([
    f.oriented_edge(pe01, True),
    f.oriented_edge(pe12, True),
    f.oriented_edge(pe23, True),
    f.oriented_edge(pe30, True),
])
comp_plc = f.axis2_placement_3d(
    pc0, f.direction((0.0, 0.0, -1.0)), f.direction((1.0, 0.0, 0.0))
)
comp_face = f.advanced_face([f.face_outer_bound(comp_loop)], f.plane(comp_plc))

# ── CLOSED_SHELL → MANIFOLD_SOLID_BREP ────────────────────────────────────────
closed_sh = f.closed_shell([sph_face, comp_face])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa245.stp")
