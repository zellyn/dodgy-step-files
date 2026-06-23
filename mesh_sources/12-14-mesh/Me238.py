"""Me238 — topTriangle_fallback_reference_edge: fe==NULL → use hv->e0 as fallback.

MeshFix `Basic_TMesh.topTriangle` Branch 9 (*fallback_reference_edge*) @ line 1726:
  'if (fe == NULL) fe = hv->e0' — no edge was selected by slope comparison;
  use the highest vertex's default reference edge e0 as fallback.

Branch 9 fires when all edges incident on hv are either not in elist, have zero
length, or — in the case where hv is isolated from the rest of the component by
all-horizontal edges — yield a slope of zero that is never strictly less than the
current running minimum (which starts at some positive value). Practically, fe
remains NULL if hv's only incident edges in elist are horizontal (opposite vertex
z == hv.z), making the slope = 0 for all candidates but the initial Ms is also 0,
so Branch 8 never fires with strict '<'.

Wait — the simplest way to trigger fe==NULL is: hv has NO edges in elist that
pass Branch 7 (i.e., no edges in elist are incident on hv). This happens when hv
is only an interior vertex connected to other interior vertices that were not yet
in elist when Branch 7 runs.

For a mesh builder fixture the cleanest approach: hv is the apex of a triangle
whose two base edges do NOT include hv (so those base edges fail Branch 7), and
the two edges from hv to the base vertices DO pass Branch 7 — but wait, those
WOULD pass Branch 7.

The actual trigger: SLOPE condition. If all candidate edges have a slope of exactly
0 (hv and opposite vertex at same z), Branch 8's strict '<' never fires, so fe
stays NULL. Ms is initialized to a large positive value, so slope=0 would fire
Branch 8.

Actually the only way fe=NULL is if NO edges pass Branch 7 at all (hv has no
edges in elist). This requires hv to be a vertex with no incident edges in the
collected elist. But every edge in elist is an edge of some triangle in the BFS,
and hv is a vertex of some BFS triangle, so at least the two edges adjacent to hv
within that triangle are in elist.

Correct trigger: all edges incident on hv have length==0 (degenerate). A triangle
with a degenerate edge (zero-length edge from hv to a coincident vertex) means the
edge fails 'e->length() != 0' in Branch 7 → fe stays NULL.

Geometry: apex v2=hv at (1,0,2); but v1 is coincident with v2 (zero-length edge):
  v0=(0,0,0), v1=(1,0,2), v2=(1,0,2)   — v1 == v2 (zero-length edge (v1,v2))
  t0=(v0,v1,v2)  — degenerate triangle (zero area, zero-length edge)

hv=v2 (or v1, same position). The only edge in elist incident on hv=v2 is (v1,v2),
which has length=0 → Branch 7 rejects it. (v0,v2) also has v2 but length≠0; it
WOULD pass Branch 7 and trigger Branch 8. So this doesn't work cleanly.

Practical alternative for Branch 9: single vertex mesh with no triangles? No.

Best representable trigger: use a completely flat triangle where all three vertices
have the SAME z-coordinate (z=0). Then hv can be any vertex (MeshFix picks
arbitrarily among ties). All edges incident on hv have slope = (0 - 0)/L = 0.
Ms is initialized to a large positive constant, so 0 < Ms → Branch 8 DOES fire.
This means Branch 9 cannot fire for a flat triangle.

Correct analysis: Branch 9 fires ONLY when fe is still NULL after the elist scan.
This happens only if NO edge in elist satisfies both conditions in Branch 7. The
only way Branch 7 fails for all edges is if hv has no incident edges in elist.

Since hv is the highest-z vertex and it must be in some triangle (otherwise it
wouldn't be in vlist), and that triangle's edges are in elist, at least one edge
incident on hv is in elist with nonzero length (unless the triangle is degenerate).

Fixture: use a degenerate flat (zero-area) triangle where hv is coincident with
another vertex. The edge (v1,v2) has length=0 and the edge (v0,v2) passes Branch 7
— so Branch 9 still won't fire.

The only scenario that works: hv has no incident edges in elist except zero-length
ones. This requires: two coincident vertices at the top; both edges from hv to
non-apex go to the same point (zero-length).

Revised geometry:
  v0=(0,0,0), v1=(0,0,0), v2=(1,0,2)   — v0 == v1 (degenerate base)
  t0=(v0,v1,v2)
  hv=v2 (z=2). Edges: (v0,v1) length=0 (base, NOT incident on hv → fails B7);
  (v0,v2) length=sqrt(1+4)≈2.24, incident on hv → passes B7 (slope=(2-0)/2.24≈0.89).
  Still Branch 9 doesn't fire.

To make Branch 9 fire: need hv to connect ONLY to coincident-with-itself vertices.
  v0=(1,0,2), v1=(1,0,2), v2=(0,0,0)
  hv=v0 (z=2). Edges incident on hv=v0: (v0,v1) length=0 (fails B7), (v0,v2)
  length=sqrt(1+4)≈2.24 (passes B7). Still passes.

The only geometrically representable scenario where NO edge incident on hv passes
Branch 7 is when hv itself is degenerate (coincident with ALL its neighbors).
That means all incident edges have zero length. With a triangle (v0,v1,v2) where
hv=v0 and v0 coincides with both v1 AND v2, we get:
  (v0,v1): length=0 → fails B7
  (v0,v2): length=0 → fails B7
  (v1,v2): not incident on hv=v0 → fails B7

So NO edge passes Branch 7 → fe=NULL → Branch 9 fires.

Geometry:
  v0=(1,0,2), v1=(1,0,2), v2=(1,0,2)   — all coincident at (1,0,2)
  t0=(v0,v1,v2)   — fully degenerate; zero area; all edges zero-length.
  hv=any vertex (all z=2). fe=NULL after elist scan. Branch 9: fe=hv->e0.
"""
from step_corpus.mesh_builder import MeshFile

m = MeshFile(catalog_id="Me238",
             title="topTriangle_fallback_reference_edge: fully degenerate triangle forces fe=NULL; Branch 9 uses hv->e0",
             defect_class="topTriangle_fallback_reference_edge")

# All three vertices at the same location — fully degenerate triangle.
v0 = m.vertex(1.0, 0.0, 2.0)   # 0
v1 = m.vertex(1.0, 0.0, 2.0)   # 1 — coincident with v0
v2 = m.vertex(1.0, 0.0, 2.0)   # 2 — coincident with v0 and v1

t0 = m.triangle(v0, v1, v2)   # 0 — fully degenerate

# All edges have zero length (coincident vertices).
m.assert_vertex_pair_distance_lt(v0, v1, 1e-9)   # zero-length
m.assert_vertex_pair_distance_lt(v1, v2, 1e-9)   # zero-length
m.assert_vertex_pair_distance_lt(v0, v2, 1e-9)   # zero-length

# Triangle has zero area.
m.assert_triangle_area_lt(t0, 1e-9)
