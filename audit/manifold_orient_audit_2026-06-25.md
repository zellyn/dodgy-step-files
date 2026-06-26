# Manifold + Orientation Flip Audit — 2026-06-25

Fixtures where pyvista reports `is_manifold=True` AND `n_orientation_flipped > 0`.
Risk: catalog claims a topology defect but the fixture's only observable defect
is triangle winding / normal orientation.

## Verdict summary

| Verdict | Count |
|---|---|
| CORRECT_CATALOG | 14 |
| MIXED_DEFECT | 2 |
| MISLEADING_MECHANISM | 0 |

All 16 fixtures are closed manifolds (pyvista `is_manifold=True`). None have a
topology claim in the catalog that is contradicted by the mesh being purely
orientation-wrong. The "flipped triangles" signal is a pyvista auto-orient
artefact that fires on meshes with consistent but globally-inward normals, on
two-component meshes where the inner shell is wound inward-by-design, or on
self-intersecting meshes where pyvista's greedy orient pass gets confused. In
every case the catalog either (a) already names orientation/normals as the
defect, (b) names a code-path trigger that is unrelated to mesh topology
(cache invalidation, null-check guard, no-op path), or (c) correctly names
self-intersection as the primary defect with orientation as a secondary signal.

---

## Per-fixture table

| ID | Catalog title (short) | Claimed mechanism (1 line) | pyvista manifold / flips | pymeshfix result | Verdict |
|---|---|---|---|---|---|
| Me149 | isInnerPoint_closest_is_triangle | Ray hits triangle interior; return sign(normal.x) — orientation of the hit face determines inside/outside | True / 6 of 6 | unchanged (5V,6T→5V,6T) | CORRECT_CATALOG |
| Me357 | CreateTriangle_topology_invalidation | Adding 4th triangle to close shell triggers dirty-flag assignment d_boundaries=d_handles=d_shells=1 | True / 4 of 4 | unchanged (4V,4T→4V,4T) | CORRECT_CATALOG |
| Me530 | joinBoundaryLoops NULL_VERTEX_INPUT | Closed mesh: all vertices interior → isOnBoundary() false → returns NULL | True / 2 of 4 | unchanged (4V,4T→4V,4T) | CORRECT_CATALOG |
| Me575 | invertSelection global_invert | t0==NULL → FOREACHTRIANGLE flips VISITED bit on all triangles | True / 2 of 4 | unchanged (4V,4T→4V,4T) | CORRECT_CATALOG |
| Me713 | removeVertices topology_invalidation | Isolated v4 removed; non-zero removal count fires d_boundaries=d_handles=d_shells=1 | True / 2 of 4 | shrunk (5V,4T→4V,4T; isolated v removed) | CORRECT_CATALOG |
| Me852 | does_bound_a_volume self_intersection | XY/XZ crossing fans share only v0; interior overlap along X-axis; does_self_intersect=true | True / 6 of 8 | shrunk (6V,8T→4V,4T) | MIXED_DEFECT |
| Me892 | merge_duplicated_vertices closed_mesh_noop | Closed tetrahedron: extract_boundary_cycles returns empty; for-loop never executes | True / 4 of 4 | unchanged (4V,4T→4V,4T) | CORRECT_CATALOG |
| Me930 | PMP.orient z-extremum-selection | Two closed tetras at different Z; high-Z component updates ref_cc_id (Branch 1) | True / 8 of 8 | shrunk (8V,8T→4V,4T) | CORRECT_CATALOG |
| Me931 | PMP.orient self-intersection-component-skip | Both components processed; cc_to_handle empties; any=false; loop-break fires (Branch 2) | True / 8 of 8 | shrunk (8V,8T→4V,4T) | CORRECT_CATALOG |
| Me932 | PMP.orient self-intersecting-pair-detection | Component B (t4 pierced by t5); does_self_intersect=true; self_intersecting_cc.insert() fires | True / 11 of 12 | shrunk heavily (10V,12T→3V,1T) | MIXED_DEFECT |
| Me933 | PMP.orient orientation-assignment-by-nesting | Inner tetra ON_BOUNDED_SIDE of outer; orient_to_bound_a_volume assigns inward orientation | True / 8 of 8 | shrunk (8V,8T→4V,4T) | CORRECT_CATALOG |
| Me1140 | volume_connected_components self_intersection_detection | Cap faces (z=1 vs y=1 planes) cross with no shared vertex; does_self_intersect fires (Branch 1) | True / 2 of 8 | shrunk (6V,8T→5V,6T) | CORRECT_CATALOG |
| Me1142 | volume_connected_components orientation_consistency | One CW-wound face; is_outward_oriented fails; orientation_error flagged (Branch 3) | True / 1 of 4 | unchanged (4V,4T→4V,4T) | CORRECT_CATALOG |
| Me1156 | PMP.orient nesting_depth_parity | Inner CC depth=1 (odd) → orient_inward; outer CC depth=0 → orient_outward (Branch 2) | True / 8 of 8 | shrunk (8V,8T→4V,4T) | CORRECT_CATALOG |
| Me1159 | PMP.orient_to_bound_a_volume nesting_depth_calculation | Ray-casting intersection parity determines inner CC nesting depth (Branch 2) | True / 8 of 8 | shrunk (8V,8T→4V,4T) | CORRECT_CATALOG |
| Me1160 | PMP.orient_to_bound_a_volume parent_child_orientation_rule | Inner CC depth=1 flipped opposite to outer parent shell (Branch 3) | True / 8 of 8 | shrunk (8V,8T→4V,4T) | CORRECT_CATALOG |

---

## Detailed notes per fixture

### Fixtures with verdict CORRECT_CATALOG

**Me149** — The mechanism explicitly involves the *sign* of a face normal's X-component
(`return closest_triangle->getVector().x > 0`). The 6/6 flip signal means the entire
closed wedge is wound inward-consistently; pyvista's auto-orient pass flips all faces.
That is the correct test vehicle: you need a closed mesh where the closest ray-crossing
hits a triangle interior and the normal X-component carries the inside/outside decision.
Catalog title already names "sign(normal.x)" — orientation is the mechanism. No change
needed.

**Me357** — The catalog mechanism is a topology *cache* invalidation (dirty flags), not a
structural mesh defect. The fixture is a geometrically perfect closed tetrahedron; the
4/4 flip signal just means the whole mesh happens to be wound CW-consistently. The
"defect" the catalog tests is an internal MeshFix code path (flag dirtying), not any
mesh property. pymeshfix is unchanged. No misleading claim.

**Me530** — Closed tetrahedron as vehicle for the `isOnBoundary()` null-guard. The 2/4 flip
signal is incidental. Catalog makes no topology claim; it correctly says "all vertices
interior → no boundary → returns NULL". No change needed.

**Me575** — Closed tetrahedron for the global selection-toggle path (t0==NULL). The
FOREACHTRIANGLE flip is about VISITED bits, not winding. Catalog makes no topology claim.
No change needed.

**Me713** — Closed tetrahedron + isolated vertex. pymeshfix removes the isolated vertex
(5V,4T→4V,4T) as expected. The 2/4 flip is on the tetrahedron faces; the isolated vertex
at (10,10,10) is the defect. Catalog correctly identifies `isolated_vertex`. No change.

**Me852** — Self-intersecting closed manifold (XY/XZ crossing fans). Catalog correctly
identifies `self_intersection` as the primary mechanism. The 6/8 flip signal is pyvista
being confused by the self-intersecting geometry (auto-orient can't resolve crossing
faces). pymeshfix shrinks it significantly (repairs SI by removing faces). Catalog
already says "does_self_intersect fires". See MIXED_DEFECT note below for the SI+orient
nuance — but the catalog claim is not wrong.

**Me892** — Valid closed tetrahedron for the `merge_duplicated_vertices_in_boundary_cycles`
no-op path. The 4/4 flip signal means the tetrahedron is consistently wound CW. pymeshfix
is unchanged (closed manifold, no topological issues to fix). Catalog makes no topology
defect claim; the mechanism is a no-op code path. No change needed.

**Me930** — Two-component mesh (`inverted_normals` defect_class; catalog sub-class
`inverted_normals/orient-z-extremum`). The 8/8 flip signal means both tetrahedra are
wound CW (consistently inverted). pymeshfix collapses the two components into one
tetrahedron (4V,4T) — it treats the second component as a duplicate/redundant shell.
Catalog correctly names z-extremum selection as the mechanism for orientation reference
assignment. No topology defect claim. No change needed.

**Me931** — Two-component mesh (`disconnected_components` defect_class; catalog sub-class
`orient-loop-exit`). The 8/8 flip signal means both clean tetrahedra are wound CW.
pymeshfix again collapses to one component. Catalog mechanism is "cc_to_handle empties;
loop breaks" — a loop-termination path. No structural topology defect claimed. No change.

**Me932** — Two-component mesh with genuine self-intersection in component B. The 11/12
flip signal reflects pyvista's confusion navigating the crossing faces. pymeshfix
collapses catastrophically (10V,12T→3V,1T) trying to repair the SI. Catalog correctly
identifies SI detection as the mechanism. See MIXED_DEFECT notes.

**Me933** — Two nested tetrahedra (`inverted_normals`; catalog sub-class `orient-nesting`).
The 8/8 flip signal means both components are wound CW-inward. pymeshfix collapses to
one component (removes inner). Catalog correctly identifies the nesting orientation
assignment mechanism. No change needed.

**Me1140** — Self-intersecting closed manifold (crossing cap faces in orthogonal planes).
Only 2/8 triangles flip — the SI pair confuses pyvista's auto-orient. pymeshfix shrinks
it slightly (removes the SI pair). Catalog correctly identifies `self_intersection` as
the primary mechanism for `volume_connected_components`. No misleading topology claim.

**Me1142** — Closed tetrahedron with one CW-wound face. This is textbook
`inconsistent_face_orientation`. The 1/4 flip signal (only one triangle flip needed) is
consistent with one bad face. pymeshfix is unchanged (already reports the right topology;
it cannot detect orientation errors). Catalog explicitly mentions "one CW-wound face;
is_outward_oriented fails; orientation_error flagged". PERFECT match. No change.

**Me1156** — Two nested closed tetrahedra (`inverted_normals/orient-nesting-depth-parity`).
The 8/8 flip signal means both components are wound inward. pymeshfix collapses to one
tetrahedron (treats inner as redundant). Catalog explicitly describes depth-parity
orientation assignment. No misleading claim.

**Me1159** — Two nested tetrahedra (`inverted_normals/orient-to-bound-a-volume-nesting-depth`).
Same pattern as Me1156. Catalog explicitly describes ray-casting nesting depth
computation. No misleading claim.

**Me1160** — Two nested tetrahedra (`inverted_normals/orient-to-bound-a-volume-parent-child`).
Same pattern. Catalog explicitly describes the parent-child orientation flip. No misleading
claim.

---

### Fixtures with verdict MIXED_DEFECT

**Me852** — `does_bound_a_volume self_intersection`

Primary defect: **geometric self-intersection** (XY-plane fan crosses XZ-plane fan).
Secondary signal: pyvista reports 6/8 triangles flipped; the auto-orient pass gets
confused by the crossing geometry and cannot find a consistent outward orientation.
pymeshfix heavily modifies the mesh (6V,8T→4V,4T), indicating it resolves the SI by
removing the problematic faces.

The catalog correctly identifies SI as the mechanism. The orientation flip is a
consequence of the SI geometry, not an independent defect. The catalog could optionally
add a note:

> "Note: pyvista auto-orient reports 6/8 triangles flipped — artifact of self-intersecting
> geometry confusing the winding propagation pass; not an independent orientation defect."

No rewrite required; adding the note is optional.

**Me932** — `PMP.orient self-intersecting-pair-detection`

Primary defect: **geometric self-intersection** in component B (t4 pierced by t5).
Secondary signal: pyvista reports 11/12 triangles flipped; the auto-orient pass is
severely disrupted by the piercing faces. pymeshfix catastrophically collapses the mesh
(10V,12T→3V,1T).

Same situation as Me852 — catalog correctly identifies SI detection as the mechanism.
The orientation flips are a consequence of the SI. The catalog could add:

> "Note: pyvista auto-orient reports 11/12 triangles flipped — the piercing face pair
> disrupts normal propagation; orientation flip is secondary to the SI defect."

No rewrite required.

---

## Proposed catalog edits

**None required.** All 16 catalog entries accurately describe the primary defect or
code-path mechanism of their fixture. No entry claims a topology defect (non-manifold
edge, hole, duplicate triangle) while the fixture's only actual defect is triangle
winding.

The two MIXED_DEFECT fixtures (Me852, Me932) could receive optional informational notes
about the secondary pyvista orientation-flip artefact, but no mechanism rewrite is
warranted.

---

## Methodology notes

- pyvista oracle: `run_pyvista()` from `step_corpus._pyvista_oracle`; `n_orientation_flipped`
  counts triangles that vtkPolyDataNormals auto-orient would flip.
- pymeshfix oracle: `python -m step_corpus._pymeshfix_oracle --json`; "unchanged" = same
  V and T counts; "shrunk" = fewer V or T; "grew" = more V or T (none observed here).
- Catalog sub-class and defect_class read from STEP_PROBLEM_CATALOG.md and source `.py`
  files respectively.
- No changes made to STEP_PROBLEM_CATALOG.md, fixture sources, or fixture JSON files.
