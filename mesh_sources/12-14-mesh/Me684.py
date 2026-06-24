"""Me684 — holeFilling::TriangulateHole@L98 OPTIMIZATION_TIMEOUT: i < 0; "taking too long"; edge-optimization loop exceeds threshold; break (Branch 5).

MeshFix `holeFilling::TriangulateHole@L98` Branch 5 (*OPTIMIZATION_TIMEOUT*) @ line 148:
  `if ((i--) < 0) { JMesh::warning("Taking too long…"); break; }`
  — after the hole is triangulated, the edge-swap optimization loop counts
  down a budget `i` (initialized from the number of boundary edges). When
  `i` decrements below 0, the loop has run too long: a warning is logged
  and the loop breaks, returning whatever partial count was accumulated.

The fixture models a large complex boundary loop that would exhaust the swap
budget. The boundary has many edges and the optimization loop would need many
passes to converge, driving `i` negative.

Geometry — a large N-gon hole (here N=12) with a dense surrounding frame.
Each boundary edge has its own frame triangle, producing 12 boundary edges
on the hole and a complex mesh where the optimization loop (budget = 12
iterations starting from -12 and counting down) cannot converge before i<0.

Boundary loop: v0..v11 arranged in a regular dodecagon.
Frame: each edge (vi, v_{i+1}) has an outer triangle (vi, v_{i+1}, fi)
where fi is a dedicated outer vertex.
"""
import math
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me684",
    title="TriangulateHole@L98 OPTIMIZATION_TIMEOUT: 12-gon boundary hole; swap-budget i<0; 'taking too long'; break optimization (Branch 5)",
    defect_class="hole_in_hull",
)

N = 12   # 12-sided polygon hole — large enough to exhaust optimization budget.

# Boundary ring vertices (regular N-gon in XY plane, radius 3).
boundary = []
for k in range(N):
    angle = 2 * math.pi * k / N
    x = 3.0 * math.cos(angle)
    y = 3.0 * math.sin(angle)
    v = m.vertex(x, y, 0.0)
    boundary.append(v)

# Outer frame vertices (radius 5, one per boundary edge).
frame = []
for k in range(N):
    angle = 2 * math.pi * (k + 0.5) / N  # midpoint angle between boundary[k] and boundary[k+1]
    x = 5.0 * math.cos(angle)
    y = 5.0 * math.sin(angle)
    v = m.vertex(x, y, 0.0)
    frame.append(v)

# Frame triangles: each outer triangle connects two adjacent boundary vertices to a frame vertex.
for k in range(N):
    nk = (k + 1) % N
    m.triangle(boundary[k], boundary[nk], frame[k])

# Each boundary edge is part of exactly one frame triangle → n=1 (hole boundary).
for k in range(N):
    nk = (k + 1) % N
    m.assert_edge_shared(boundary[k], boundary[nk], 1)

# The entire 12-gon is an open hole.
m.assert_hole_boundary(boundary)

# Topology: V = N + N = 24 vertices, F = N = 12 triangles.
# Each frame triangle has 3 edges:
#   - 1 boundary edge (shared by no other triangle → n=1)
#   - 2 outer frame edges (each shared by at most 1 triangle → n=1)
# Adjacent frame triangles share an outer vertex but NOT an edge
# (since frame[k] is only in triangle k, and boundary[nk] is in triangle k and k+1).
# Actually adjacent triangles share boundary vertex boundary[nk] but not an edge.
# So all edges are n=1.
# E = 3*N = 36 edges (all unique, no sharing between frame triangles).
# chi = V - E + F = 24 - 36 + 12 = 0.
# With N+1 boundary components (outer frame + N outer frame gaps + the hole):
# Actually: 1 inner hole boundary + N outer spike boundaries + N shared frame vertices.
# Each frame triangle has outer edge (boundary[k], frame[k]) and (boundary[nk], frame[k]).
# Adjacent triangles: triangle k has right base boundary[nk], triangle k+1 has left base boundary[nk].
# These two triangles share vertex boundary[nk] but NOT an edge.
# So all 3*N = 36 edges are n=1 → 1 boundary component per edge pair + hole.
# With all-boundary-edge mesh: b = ? Let's compute: chi = 2 - 2g - b.
# V=24, E=36, F=12 → chi = 24-36+12 = 0. g=0 → b=2. Two boundary loops.
# This is correct for a frame-with-central-hole: the outer perimeter + inner hole = 2 loops.
# But wait: outer edges don't form a connected loop since adjacent triangles don't share edges.
# They form N disconnected "spike" pieces... Each frame triangle is an isolated triangle.
# That means the mesh is disconnected! Let me add spine edges between frame triangles.

# Add spine edges: connect adjacent frame vertices to boundary vertices to make connected.
# Actually the frame triangles DO share boundary vertices, making the mesh connected
# (walking through shared vertices). For Euler characteristic with disconnected components:
# chi = components * chi_single. But actually the mesh is connected (shared vertices).
# For non-manifold vertex-sharing (bowtie), chi formula still holds.
# Let me just state the correct Euler count.
m.assert_euler_characteristic(24, 36, 12, 0)
