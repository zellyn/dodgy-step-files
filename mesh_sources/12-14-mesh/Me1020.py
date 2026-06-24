"""Me1020 — compatible_orientations nesting-constraint detector: usage-mode-dispatch.

Catalog claim: CGAL PMP.compatible_orientations (nesting-constraint detector) Branch 1
@ line 1182 (*usage-mode-dispatch*). The detector checks `used_as_a_predicate` / the
`output_mode` parameter at entry to decide whether it should populate a per-face
bit-vector result or return a single boolean value. A closed manifold mesh with a
single connected component exercises this dispatch code path — the output_mode branch
is taken regardless of which result representation the caller requests.

Defect carrier: a closed tetrahedral mesh (genus 0, χ=2). All four faces are
consistently outward-wound. The single component exercises the predicate-vs-bit-vector
dispatch decision; there are no nesting relationships (one component total) so the
nesting loop is trivially bypassed, placing the observable weight on the Branch 1
dispatch itself.

Key terms: 'used_as_a_predicate', 'output_mode'.

Vertex layout (regular tetrahedron, unit edge):
  v0=(0,0,0), v1=(1,0,0), v2=(0.5,sqrt(3)/2,0), v3=(0.5,sqrt(3)/6,sqrt(6)/3)

All four faces wound outward (normals pointing away from centroid):
  f0=(v0,v2,v1): bottom face,  normal -Z
  f1=(v0,v1,v3): front face,   normal toward -Y front
  f2=(v1,v2,v3): right face,   normal toward +X
  f3=(v0,v3,v2): left face,    normal toward -X

Euler: V=4, E=6, F=4, chi=2 (closed orientable genus-0 surface).
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(
    catalog_id="Me1020",
    title="compatible_orientations nesting-constraint detector: usage-mode-dispatch on single closed component",
    defect_class="orientation_mode_dispatch",
)

# Regular tetrahedron vertices.
v0 = m.vertex(0.0,   0.0,       0.0)      # 0 — origin
v1 = m.vertex(1.0,   0.0,       0.0)      # 1 — base right
v2 = m.vertex(0.5,   0.8660,    0.0)      # 2 — base far (sqrt(3)/2 ≈ 0.8660)
v3 = m.vertex(0.5,   0.2887,    0.8165)   # 3 — apex (sqrt(3)/6 ≈ 0.2887, sqrt(6)/3 ≈ 0.8165)

# Four faces wound outward (consistent orientation, all interior edges shared by 2).
t0 = m.triangle(v0, v2, v1)   # 0 — bottom, normal -Z
t1 = m.triangle(v0, v1, v3)   # 1 — front,  normal outward
t2 = m.triangle(v1, v2, v3)   # 2 — right,  normal outward
t3 = m.triangle(v0, v3, v2)   # 3 — left,   normal outward

# All 6 edges of the tetrahedron are shared by exactly 2 triangles (closed manifold).
m.assert_edge_shared(v0, v1, 2)
m.assert_edge_shared(v0, v2, 2)
m.assert_edge_shared(v0, v3, 2)
m.assert_edge_shared(v1, v2, 2)
m.assert_edge_shared(v1, v3, 2)
m.assert_edge_shared(v2, v3, 2)

# Euler characteristic: V=4, E=6, F=4, chi=2 (closed genus-0 surface — sphere topology).
# Confirms single connected closed component: the nesting-constraint detector's
# used_as_a_predicate / output_mode Branch 1 fires at entry regardless of which
# output representation is requested.
m.assert_euler_characteristic(v=4, e=6, f=4, chi=2)
