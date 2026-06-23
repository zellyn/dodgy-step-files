"""Ctl013 — Clean closed icosahedron mesh (negative control for §12-14-mesh).

A regular icosahedron has 12 vertices, 20 triangular faces, and 30 edges.
Every edge is shared by exactly 2 triangles (manifold).  No degenerate
triangles, no near-coincident vertices, no holes.

No assertions are added — the absence of defect assertions is itself the
negative control signal.  The test harness checks that _mesh_oracle
reports zero failures (no assertions to check means no assertion can fail).
"""
import sys
import math
from pathlib import Path

_HERE = Path(__file__).resolve()
sys.path.insert(0, str(_HERE.parents[3] / "validation" / "src"))

from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Ctl013",
    title="clean closed icosahedron — 20 manifold triangles, no defects",
    defect_class="none",
)

# Regular icosahedron vertices (unit circumradius)
phi = (1.0 + math.sqrt(5.0)) / 2.0  # golden ratio

# 12 vertices of a regular icosahedron
raw = [
    (-1,  phi,  0), ( 1,  phi,  0), (-1, -phi,  0), ( 1, -phi,  0),
    ( 0, -1,  phi), ( 0,  1,  phi), ( 0, -1, -phi), ( 0,  1, -phi),
    ( phi,  0, -1), ( phi,  0,  1), (-phi,  0, -1), (-phi,  0,  1),
]

scale = 1.0 / math.sqrt(1.0 + phi * phi)
for x, y, z in raw:
    m.vertex(x * scale, y * scale, z * scale)

# 20 faces of a regular icosahedron (consistent CCW winding from outside)
faces = [
    (0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11),
    (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
    (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9),
    (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1),
]

for i0, i1, i2 in faces:
    m.triangle(i0, i1, i2)

# No defect assertions — clean mesh, nothing to assert
