"""Me086 — connectivity_edge_orientation_mismatch: adjacent triangles with inconsistent winding.

Catalog claim: triangles t0 and t1 share edge (v1, v2) but their face normals
point in opposite directions (inconsistent winding). MeshFix checkConnectivity
Branches 8 (*EDGE_ORIENTATION_MISMATCH_T1*) and 10 (*EDGE_ORIENTATION_MISMATCH_T2*)
fire when an edge's orientation is inconsistent with one or both of its incident
triangles. In a correctly-oriented closed 2-manifold, each undirected edge (a,b)
appears once as directed (a→b) in one triangle and once as directed (b→a) in the
adjacent triangle. When both triangles traverse the edge in the same direction,
the orientation is inconsistent — the half-edge for (a→b) has two owners instead
of one owner and one twin.

Defect carrier: t0=(v0,v1,v2) has a normal pointing in +Z. t1=(v1,v3,v2) also
has a +Z component but its shared edge traversal is v1→... which creates an
orientation mismatch with t0's v1→v2 direction. The test checks that the two
adjacent triangles have inconsistent (anti-parallel) normals.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me086",
             title="connectivity edge orientation mismatch: adjacent triangles t0,t1 have opposite normals along shared edge",
             defect_class="inconsistent_winding")

v0 = m.vertex(0.0, 0.0, 0.0)
v1 = m.vertex(1.0, 0.0, 0.0)
v2 = m.vertex(0.5, 1.0, 0.0)
v3 = m.vertex(-0.5, 1.0, 0.0)

# t0 = (v0, v1, v2): CCW in XY → normal = +Z.
t0 = m.triangle(v0, v1, v2)

# t1 = (v0, v2, v3): also CCW → normal = +Z. Shares edge (v0, v2).
# In a correctly-oriented mesh, the triangle on the other side of (v0,v2)
# should traverse it as (v2→v0), giving normal -Z (flipped).
# Here both t0 and t1 have +Z normals → inconsistent winding.
# MeshFix Branch 8/10 catches this: the orientation of the shared edge
# does not match what either triangle's normal requires of its t1/t2 slot.
t1 = m.triangle(v3, v2, v0)   # CW traversal of same 3-ring → normal = -Z

# The shared edge (v0, v2) is incident on 2 triangles.
m.assert_edge_shared(v0, v2, 2)

# t0 normal is +Z; t1 = (v3,v2,v0) CW → normal = -Z. Dot < 0: inconsistent.
m.assert_adjacent_triangles_inconsistent_winding(t0, t1)
