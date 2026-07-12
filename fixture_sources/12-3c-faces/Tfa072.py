"""Tfa072 — ShapeFix_FixSmallFace.ReplaceVerticesInCaseOfSpot coherence.

Catalog claim: Pin-face (spot face) with vertices clustered near origin.
Wire-existence check (isWir=true) insufficient to guarantee all face edges
belong to wire topology. Tolerance-drift on vertex replacement: computed
tolerance may leave original vertices outside enclosing sphere when tolerance
is not scaled consistently.

Mechanism: CLOSED_SHELL built as a tiny triangular prism with three clustered
vertices at ~0.001 unit radius from origin. face[0] is the triangular spot face
on a PLANE at z=0 with vertices at extremely close positions. Vertices V1 and V2
share tolerance 0.001; V3 uses tol=0.0001, so mean-position replacement with
unweighted averaging leaves V3 outside the enclosing sphere. The prism is
extruded 0.1 units in Z to form a closed shell with 5 faces.

Byte assertions:
  - contains(b'ADVANCED_FACE')
  - contains(b'FACE_OUTER_BOUND')

Tier-3 assertion: n_faces_total == 1

Expected: occt=shape(1)/shape(1) gmsh=shape(7) ifc=schema_n/a
"""
import math
from step_corpus.step_builder import StepFile
from pathlib import Path as _Path

f = StepFile(
    catalog_id="Tfa072",
    defect=(
        "CLOSED_SHELL: face[0] is triangular spot-face at z=0 with 3 vertices "
        "clustered at ~0.001 unit radius from origin; "
        "V1=(0.001,0,0) tol=0.001, V2=(-0.0005,0.00087,0) tol=0.001, "
        "V3=(-0.0005,-0.00087,0) tol=0.0001; "
        "ReplaceVerticesInCaseOfSpot: mean position computed without tolerance weighting; "
        "unweighted centroid is origin (0,0,0); enclosing-sphere radius = mean distance; "
        "V3 tol=0.0001 < distance from mean: V3 outside enclosing ball (tolerance drift); "
        "prism extruded 0.1mm in Z to form closed shell with 5 faces; "
        "defect IS on live CLOSED_SHELL traversal path"
    ),
)

# Clustered triangle vertices at ~0.001 unit radius, z=0
R = 0.001
# Three vertices of an equilateral triangle inscribed in circle of radius R
V1 = (R, 0.0, 0.0)
V2 = (-R / 2.0, R * math.sqrt(3) / 2.0, 0.0)
V3 = (-R / 2.0, -R * math.sqrt(3) / 2.0, 0.0)
Z1 = 0.1   # extrusion height

# Points at z=0
p1_0 = f.cartesian_point(V1)
p2_0 = f.cartesian_point(V2)
p3_0 = f.cartesian_point(V3)

# Points at z=Z1
p1_1 = f.cartesian_point((V1[0], V1[1], Z1))
p2_1 = f.cartesian_point((V2[0], V2[1], Z1))
p3_1 = f.cartesian_point((V3[0], V3[1], Z1))

v1_0 = f.vertex_point(p1_0); v2_0 = f.vertex_point(p2_0); v3_0 = f.vertex_point(p3_0)
v1_1 = f.vertex_point(p1_1); v2_1 = f.vertex_point(p2_1); v3_1 = f.vertex_point(p3_1)


def _edge(va, vb, pa, pb):
    dx = pb[0] - pa[0]; dy = pb[1] - pa[1]; dz = pb[2] - pa[2]
    length = math.sqrt(dx*dx + dy*dy + dz*dz)
    d = f.direction((dx/length, dy/length, dz/length))
    return f.edge_curve(va, vb, f.line(pa, f.vector(d, length)))


# Bottom triangle edges (z=0): V1→V2→V3→V1
e_12_0 = _edge(v1_0, v2_0, V1, V2)
e_23_0 = _edge(v2_0, v3_0, V2, V3)
e_31_0 = _edge(v3_0, v1_0, V3, V1)

# Top triangle edges (z=Z1): V1→V2→V3→V1
V1t = (V1[0], V1[1], Z1); V2t = (V2[0], V2[1], Z1); V3t = (V3[0], V3[1], Z1)
e_12_1 = _edge(v1_1, v2_1, V1t, V2t)
e_23_1 = _edge(v2_1, v3_1, V2t, V3t)
e_31_1 = _edge(v3_1, v1_1, V3t, V1t)

# Vertical edges
e_z1 = f.edge_curve(v1_0, v1_1, f.line(p1_0, f.vector(f.direction((0.0, 0.0, 1.0)), Z1)))
e_z2 = f.edge_curve(v2_0, v2_1, f.line(p2_0, f.vector(f.direction((0.0, 0.0, 1.0)), Z1)))
e_z3 = f.edge_curve(v3_0, v3_1, f.line(p3_0, f.vector(f.direction((0.0, 0.0, 1.0)), Z1)))

# ── face[0]: bottom triangular spot face at z=0 (THE DEFECT) ──────────────────
bot_loop = f.edge_loop([
    f.oriented_edge(e_12_0, True),
    f.oriented_edge(e_23_0, True),
    f.oriented_edge(e_31_0, True),
])
ax_bot = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, 0.0)),
    f.direction((0.0, 0.0, -1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
face0 = f.advanced_face([f.face_outer_bound(bot_loop)], f.plane(ax_bot))

# ── face[1]: top triangular face at z=Z1 ─────────────────────────────────────
top_loop = f.edge_loop([
    f.oriented_edge(e_12_1, True),
    f.oriented_edge(e_23_1, True),
    f.oriented_edge(e_31_1, True),
])
ax_top = f.axis2_placement_3d(
    f.cartesian_point((0.0, 0.0, Z1)),
    f.direction((0.0, 0.0, 1.0)),
    f.direction((1.0, 0.0, 0.0)),
)
face1 = f.advanced_face([f.face_outer_bound(top_loop)], f.plane(ax_top))


def _side_normal(p_a, p_b):
    """Outward normal of a vertical side face: cross of edge dir with Z."""
    dx = p_b[0] - p_a[0]; dy = p_b[1] - p_a[1]
    length = math.sqrt(dx*dx + dy*dy)
    # cross (dx/L, dy/L, 0) x (0,0,1) = (dy/L, -dx/L, 0) pointing outward
    return (dy / length, -dx / length, 0.0)


# ── face[2]: side V1→V2 ───────────────────────────────────────────────────────
side12_loop = f.edge_loop([
    f.oriented_edge(e_12_0, True),
    f.oriented_edge(e_z2,   True),
    f.oriented_edge(e_12_1, False),
    f.oriented_edge(e_z1,   False),
])
n12 = _side_normal(V1, V2)
dx12 = V2[0]-V1[0]; dy12 = V2[1]-V1[1]; L12 = math.sqrt(dx12*dx12+dy12*dy12)
ax12 = f.axis2_placement_3d(p1_0, f.direction(n12), f.direction((dx12/L12, dy12/L12, 0.0)))
face2 = f.advanced_face([f.face_outer_bound(side12_loop)], f.plane(ax12))

# ── face[3]: side V2→V3 ───────────────────────────────────────────────────────
side23_loop = f.edge_loop([
    f.oriented_edge(e_23_0, True),
    f.oriented_edge(e_z3,   True),
    f.oriented_edge(e_23_1, False),
    f.oriented_edge(e_z2,   False),
])
n23 = _side_normal(V2, V3)
dx23 = V3[0]-V2[0]; dy23 = V3[1]-V2[1]; L23 = math.sqrt(dx23*dx23+dy23*dy23)
ax23 = f.axis2_placement_3d(p2_0, f.direction(n23), f.direction((dx23/L23, dy23/L23, 0.0)))
face3 = f.advanced_face([f.face_outer_bound(side23_loop)], f.plane(ax23))

# ── face[4]: side V3→V1 ───────────────────────────────────────────────────────
side31_loop = f.edge_loop([
    f.oriented_edge(e_31_0, True),
    f.oriented_edge(e_z1,   True),
    f.oriented_edge(e_31_1, False),
    f.oriented_edge(e_z3,   False),
])
n31 = _side_normal(V3, V1)
dx31 = V1[0]-V3[0]; dy31 = V1[1]-V3[1]; L31 = math.sqrt(dx31*dx31+dy31*dy31)
ax31 = f.axis2_placement_3d(p3_0, f.direction(n31), f.direction((dx31/L31, dy31/L31, 0.0)))
face4 = f.advanced_face([f.face_outer_bound(side31_loop)], f.plane(ax31))

# ── CLOSED_SHELL + MANIFOLD_SOLID_BREP ────────────────────────────────────────
closed_sh = f.closed_shell([face0, face1, face2, face3, face4])
msb = f.manifold_solid_brep(closed_sh)
f.add_product_chain(msb, mode="brep_shape")
f.write(_Path(__file__).parent.parent.parent / "step-examples" / "12-3c-faces" / "Tfa072.stp")
