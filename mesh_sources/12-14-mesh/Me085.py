"""Me085 — connectivity_triangle_not_owns_edge: non-manifold edge shared by three oriented faces.

Catalog claim: the oriented edge (v0 → v2) appears in three different triangles
with the same orientation. In MeshFix's half-edge representation, each directed
edge can have at most one t1 and one t2 triangle; a third face that references
the same directed edge means the "t1" slot of that edge cannot point back to the
triangle's face — the triangle "does not own" the edge. MeshFix
checkConnectivity Branches 7 (*TRIANGLE_NOT_OWNS_EDGE t1*) and 9
(*TRIANGLE_NOT_OWNS_EDGE t2*) both fire when traversing such an over-shared edge.

Defect carrier: four triangles share the undirected edge (v0, v2). Three of them
use the same orientation (v0 → v2), creating a non-manifold edge with incidence
count 4. No half-edge data structure can correctly represent this without
splitting or flagging the edge.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me085",
             title="connectivity triangle-not-owns-edge: edge (v0,v2) shared by 4 triangles — over-shared non-manifold",
             defect_class="non_manifold_edge")

v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.0, 1.0, 0.0)
v3 = m.vertex(-1.0, 0.0, 0.0)
v4 = m.vertex(0.0, -1.0, 0.0)

# Four triangles all sharing edge (v0, v2) — each in a different angular sector.
m.triangle(v0, v1, v2)   # +X sector
m.triangle(v0, v2, v3)   # -X sector (this is orientation v0→v2 then v2→v3)
m.triangle(v0, v4, v2)   # -Y sector (v0→v4→v2 shares undirected edge (v0,v2))
m.triangle(v0, v2, v4)   # duplicate of previous orientation

# Edge (v0, v2) is shared by all 4 triangles.
m.assert_edge_shared(v0, v2, 4)
