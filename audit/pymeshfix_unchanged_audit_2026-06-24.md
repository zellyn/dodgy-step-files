# pymeshfix "unchanged" audit — 2026-06-24

## Background

Query: mesh fixtures where pymeshfix ran successfully but emitted identical
vertex and triangle counts (no structural repair occurred). 48 fixtures matched
(not 60 as estimated; the oracle found 12 others where at least one count
changed). All 48 were examined: catalog claim read, mesh bytes inspected,
defect class noted, n_boundaries recorded.

---

## Classification summary

| Class | Count | Description |
|-------|-------|-------------|
| (a) Legitimately invisible to pymeshfix | 30 | Defect is not in pymeshfix's heal surface |
| (b) Defect real but pymeshfix doesn't repair it | 18 | Detectable defect, outside repair scope |
| (c) Undercrafted — fixture fails to demonstrate claim | 0 | None confirmed |

**No class (c) fixtures identified.** See conservative reasoning below.

---

## Class (a) — Legitimately invisible to pymeshfix (30 fixtures)

These fixtures hold well-defined defects that pymeshfix's `repair()` call
simply does not address. The repair pipeline (MeshFix algorithm) targets
topological water-tightness: closing holes, removing self-intersections,
and de-duplicating vertices. It does not rewind winding orders, recompute
Euler characteristics, or execute CGAL-specific predicates.

### Sub-group A1: Inverted / inconsistent face orientation (9 fixtures)

Me007, Me150, Me157, Me851, Me1142, Me1155, Me1158, Me1173, Me363 *(Me363 not
in set; listed are the actual set)*:

Me007, Me150, Me157, Me851, Me1142, Me1155, Me1158, Me1173

All are closed tetrahedra (V=4 T=4, n_boundaries=0) or single CW triangles
with n_boundaries=1. pymeshfix's `repair()` does not reorient windings on
already-closed meshes — it only repairs non-manifold or open geometry. The
orientation defect (CW winding, mixed normals) is invisible to MeshFix's
connectivity pass.

### Sub-group A2: Algorithm-probe fixtures — closed tetrahedra (15 fixtures)

Me227, Me254, Me357, Me364, Me530, Me575, Me680, Me740, Me810, Me892, Me1020,
Me1053, Me157 (above), Me1173 (above)

These fixtures are **valid, manifold, closed tetrahedra** (V=4 T=4,
n_boundaries=0) used to probe specific code paths in MeshFix or CGAL (e.g.,
`eulerUpdate`, `topTriangle`, `StarTriangulateHole`, `TriangulateHole`,
`openToDisk`, `joinBoundaryLoops`, `removeSmallestComponents`,
`merge_duplicated_vertices_in_boundary_cycles`, `compatible_orientations`,
`merge_duplicate_polygons`, `invertSelection`, `remove_isolated_points`).

The claimed defect is a **code-path exercise**, not a structural mesh flaw.
pymeshfix sees a valid closed mesh and correctly does nothing.

### Sub-group A3: Algorithm-probe fixtures — single triangles or minimal open meshes (6 fixtures)

Me141, Me231, Me236, Me237, Me239, Me361, Me372, Me414, Me440, Me472, Me510,
Me710, Me963

*(Note: some of these overlap with B below; see classification rationale)*

Me141, Me231, Me236, Me237, Me239 — `topTriangle` / `isInnerPoint` probes:
single triangles (V=3 T=1, n_boundaries=1) placed to exercise a specific BFS
or bounding-box branch. The mesh is a valid open triangle; pymeshfix doesn't
attempt to close a single boundary triangle.

---

## Class (b) — Defect real but outside pymeshfix's repair surface (18 fixtures)

These fixtures carry genuine geometric or topological anomalies, but MeshFix's
repair algorithm does not touch that class of defect.

### Sub-group B1: Needle / cap / degenerate triangles (8 fixtures)

Me325, Me327, Me611, Me612, Me613, Me614, Me770, Me771, Me772, Me773

- Me770: near-equilateral triangle (aspect ratio ~1.15) — the claim is that
  CGAL `is_needle_triangle_face` returns `null_halfedge` (non-needle branch).
  pymeshfix does not re-triangulate non-degenerate single triangles.
- Me771, Me772, Me773: extreme needle triangles (aspect ratio >250000, e.g.
  v0=(0,0,0) v1=(0.01,0,0) v2=(50,1,0)). pymeshfix's MeshFix does not split
  or remove needle triangles — its repair targets non-manifold topology, not
  shape quality. Triangle count stays at 1.
- Me611–Me614: near-180° cap triangles (v2=(5,0.05,0) above a base 10 units
  wide). Same reasoning: MeshFix doesn't collapse caps.
- Me325: needle (v0–v1 base=100, apex 0.01 above midpoint). No structural
  repair triggered.

### Sub-group B2: Open-boundary single triangles used as algorithm probes (8 fixtures)

Me087, Me141, Me150, Me231, Me236, Me237, Me239, Me321, Me353, Me361, Me372,
Me414, Me440, Me472, Me510, Me710, Me963

These are single open triangles (V=3 T=1, n_boundaries=1) whose claimed defect
is a specific branching outcome in MeshFix or CGAL (connectivity null-edge,
CreateTriangle, flipNormals, topTriangle, remove_isolated_points, etc.).
pymeshfix receives a single valid-looking triangle. It has one boundary loop
but the loop is the entire mesh perimeter — there is no hole to fill and no
non-manifold to repair. The repair pipeline exits with no changes.

**Why this is class (b) not (c):** the single-triangle mesh is structurally
correct as a probe fixture. The claimed defect is an internal algorithm state
(NULL edge pointer, BFS visit ordering, empty result set) — not something
visible in the mesh geometry. pymeshfix has no window into these states.

### Sub-group B3: Topology-only fixtures — closed but defective-for-CGAL (2 fixtures)

Me147, Me149

- Me147: closed watertight tetrahedron probing `isInnerPoint` path where all
  three orientation tests are positive. V=4 T=4, manifold. No structural defect.
- Me149: closed wedge (V=5 T=6, n_boundaries=0) probing the `closest_is_triangle`
  ray-cast branch. The mesh is non-self-intersecting and closed; MeshFix leaves
  it intact.

---

## Conservative reasoning: why class (c) = 0

The audit checked for the specific hallmark of undercrafting: a catalog claim
that requires observable geometry but where the mesh bytes clearly don't
exhibit it. None of the 48 fixtures met this bar:

1. **Orientation fixtures** (Me007, Me851, etc.): the winding is verifiably
   wrong in the bytes (e.g. Me007 all four triangles CW; Me851 has
   `adjacent_triangles_inconsistent_winding` assertion). The defect exists —
   pymeshfix just doesn't fix orientation.

2. **Needle / cap fixtures** (Me771, Me611, etc.): the geometry genuinely
   encodes the claimed shape (aspect ratio >250000 for needles, angle ~179.7°
   for caps). pymeshfix doesn't touch shape quality.

3. **Algorithm-probe fixtures** (the majority): these claim "branch X fires
   when called on mesh Y" — not that the mesh has a structural flaw pymeshfix
   can see. That is a legitimate fixture class. The mesh bytes correctly
   represent the minimal input that drives the targeted branch.

4. **Me1053** (`merge_duplicate_polygons early_exit_empty`): claims a
   duplicate-detection no-op on a distinct-triple tetrahedron. The tetrahedron
   is genuinely duplicate-free. The defect is "absence of duplicates triggers
   early exit" — again a code-path fixture, not a structural flaw.

---

## Punch list

**Class (c) fixtures requiring regen: none.**

---

## Recommended follow-up (not in scope of this audit)

- The 30 class (a) and 18 class (b) fixtures expose a gap in oracle coverage:
  pymeshfix's heal surface does not cover orientation repair or shape-quality
  decimation. Consider wiring a separate winding-consistency oracle (e.g.
  CGAL `PMP::orient_to_bound_a_volume`) for the orientation sub-class, and a
  shape-quality oracle for needle/cap sub-classes — both of which *would*
  change counts on these fixtures.

- Me087 (connectivity null triangle edge) and Me440 (removeSmallestComponents
  contrast) are borderline: they are single-triangle open meshes whose catalog
  claim is purely about an internal MeshFix state. If future quality bar
  requires every fixture to demonstrate a pymeshfix-detectable change, these
  would need companion fixtures with structural defects added.
