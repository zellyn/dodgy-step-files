"""Me812 — StarTriangulateHole_barycenter_computation: 5-vertex boundary loop;
accumulator np = np + (*v) iterates all boundary vertices; barycenter divided
by count; new vertex inserted at mean position.

MeshFix `Basic_TMesh.StarTriangulateHole` Branch 3 (*BARYCENTER_COMPUTATION*) @ line 66:
  for (v = e->v1; ...; v = ...) { np = np + (*v); np_count++; }
  np /= np_count;
  After the boundary loop is collected (Branch 2), StarTriangulateHole sums
  every boundary vertex position (np = np + (*v)) and divides by the count
  to compute the hole's barycenter.  A new vertex is inserted at np and fan
  triangles are created from each boundary edge to np.

Geometry: two concentric pentagons (outer ring R=3, inner ring R=1) connected
by 10 triangles (2 per "trapezoid" sector).  The inner pentagon is hollow —
no triangles fill it — giving a 5-vertex / 5-edge boundary loop (i0..i4).
StarTriangulateHole called on any inner boundary edge executes np = np + (*v)
exactly 5 times before dividing by 5 to place the barycenter.

  outer vertices (R=3): o0=(3,0,0), o1=(0.927,2.853,0), ... (5 equally spaced)
  inner vertices (R=1): i0=(1,0,0), i1=(0.309,0.951,0), ... (5 equally spaced)

  10 triangles: for each k in 0..4:
    ta=(ok, o(k+1), i(k+1))   tb=(ok, i(k+1), ik)

  Inner boundary loop: i0-i1-i2-i3-i4-i0 (5 edges, all n=1).
  All outer rim edges: n=1 (boundary of outer ring).
  Straight spokes ok-ik: n=2 (shared by adjacent sectors).

Euler: V=10, E=20, F=10, chi=0 (annular mesh with two boundary components).
"""
import math
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me812",
    title="StarTriangulateHole_barycenter_computation: 5-vertex hole; np=np+(*v) accumulates 5 boundary vertices for barycenter (Branch 3)",
    defect_class="star_triangulate_hole_barycenter_computation",
)

N = 5
OUTER_R = 3.0
INNER_R = 1.0

# Outer ring: o0..o4
outer = []
for k in range(N):
    angle = 2 * math.pi * k / N
    outer.append(m.vertex(round(OUTER_R * math.cos(angle), 6),
                          round(OUTER_R * math.sin(angle), 6),
                          0.0))

# Inner ring: i0..i4 — the 5-vertex boundary of the hole
inner = []
for k in range(N):
    angle = 2 * math.pi * k / N
    inner.append(m.vertex(round(INNER_R * math.cos(angle), 6),
                          round(INNER_R * math.sin(angle), 6),
                          0.0))

# 10 triangles: 2 per "trapezoid" sector
for k in range(N):
    ok  = outer[k]
    ok1 = outer[(k + 1) % N]
    ik  = inner[k]
    ik1 = inner[(k + 1) % N]
    m.triangle(ok, ok1, ik1)   # outer triangle
    m.triangle(ok, ik1, ik)    # inner triangle

# All inner edges are boundary (no triangle fills the inner pentagon).
for k in range(N):
    m.assert_edge_shared(inner[k], inner[(k + 1) % N], 1)

# All inner-to-outer spoke edges are shared by 2 triangles.
for k in range(N):
    m.assert_edge_shared(inner[k], outer[k], 2)

# All outer rim edges are shared by 1 triangle each (boundary of outer ring).
for k in range(N):
    m.assert_edge_shared(outer[k], outer[(k + 1) % N], 1)

# Euler: V=10, E=20, F=10, chi=0
# (annular surface with two boundary components: inner pentagon + outer pentagon)
m.assert_euler_characteristic(v=10, e=20, f=10, chi=0)
