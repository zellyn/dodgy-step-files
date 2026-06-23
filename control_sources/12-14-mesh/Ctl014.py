"""Ctl014 — Clean planar grid mesh (negative control for §12-14-mesh).

A 3x3 grid of unit squares, each split into 2 right triangles.
18 triangles total, 16 vertices, all edges shared by exactly 2 triangles
(interior) or 1 triangle (boundary — which is fine for an open surface).
No degenerate triangles, no near-coincident vertices.

No assertions are added — the absence of defect assertions is itself the
negative control signal.
"""
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
sys.path.insert(0, str(_HERE.parents[3] / "validation" / "src"))

from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Ctl014",
    title="clean planar 3x3 grid mesh — 18 manifold triangles, no defects",
    defect_class="none",
)

N = 4  # N x N vertices forming (N-1) x (N-1) grid of quads
# Vertices: (i, j, 0) for i,j in 0..N-1
idx = {}
for j in range(N):
    for i in range(N):
        idx[(i, j)] = m.vertex(float(i), float(j), 0.0)

# Each quad split into 2 triangles (lower-left + upper-right)
for j in range(N - 1):
    for i in range(N - 1):
        a = idx[(i,   j  )]
        b = idx[(i+1, j  )]
        c = idx[(i+1, j+1)]
        d = idx[(i,   j+1)]
        m.triangle(a, b, d)  # lower-left triangle
        m.triangle(b, c, d)  # upper-right triangle

# No defect assertions — clean mesh
