# pymeshfix "grew" and "rejected" audit — 2026-06-24

Oracle: `validation/src/step_corpus/_pymeshfix_oracle.py`
Corpus: `mesh-examples/12-14-mesh/` (760 fixtures)
Scope: 21 fixtures whose triangle count increased after `repair()` + 6 fixtures pymeshfix refused to load.

---

## Background on pymeshfix behavior

pymeshfix's `repair()` closes open boundary loops by inserting triangles.
Any mesh presented with a boundary (open edge) is a candidate for growth.
pymeshfix's rejection reason is "empty vertices or triangles array" — it refuses meshes with 0 triangles.

---

## REJECTED (6 fixtures)

All six have **0 triangles / 1 isolated vertex** — the canonical "empty-mesh guard" class.
pymeshfix error in all cases: `empty vertices or triangles array`.

| Fixture | Catalog defect class | Claim summary |
|---------|---------------------|---------------|
| Me140 | `isInnerPoint_empty_mesh` | T.numels()==0 → early return false |
| Me320 | `with_third_points_empty_input_guard` | points.empty() → return out unchanged |
| Me360 | `remove_isolated_points_empty_input` | 0 vertices + 0 triangles → return 0 |
| Me450 | `removeSmallestComponents area EMPTY_MESH` | T.numels()==0 → return 0 |
| Me550 | `checkAndRepair::rebuildConnectivity EMPTY_MESH` | V.numels()==0 → return false |
| Me660 | `merge_duplicate_points_in_polygon_soup empty_input` | ini_points_n==0 → return |

**Classification: all 6 are CATALOG-CONSISTENT.**

These fixtures deliberately encode the "no triangles" case to exercise early-exit guards in various mesh-heal functions. pymeshfix's rejection is the correct oracle response — it simply confirms the same structural property (no triangles) from a different angle. The rejection message "empty vertices or triangles array" is a new data point: pymeshfix internally enforces the same pre-condition (non-empty triangle list) that the catalog fixtures are designed to probe.

**Defect-class signal:** No new class needed. Rejection = confirmation of the `empty_mesh` structural invariant. The six fixtures collectively cover six distinct function-entry guards, all gated on the same topological fact.

**Action: none.** No regen, no Notes update required.

---

## GREW (21 fixtures)

pymeshfix fills open boundary loops. Any mesh with boundary edges is a candidate.
The key question per fixture: does the catalog claim involve a hole / open boundary, or is pymeshfix filling a boundary that is *incidental* to a non-hole claim?

### Group A — Genuine hole-fill fixtures (CATALOG-CONSISTENT, growth expected)

These three have `defect_class = hole_in_hull` and a `hole_boundary` assertion:

| Fixture | Triangles | Boundaries | Claim |
|---------|-----------|------------|-------|
| Me328 | 2 → 4 | 1 | `with_third_points_fallback_dt3_or_cubic`: non-planar hole; CDT fails; DT3 fallback fills it |
| Me761 | 3 → 4 | 1 | `retriangulateVT_hole_triangulation`: 3-triangle fan around hub; inner triangle [v0,v1,v2] absent |
| Me850 | 3 → 4 | 1 | `does_bound_a_volume connectivity_broken`: tetrahedron base removed; open boundary present |

Growth is the exact expected oracle signal for this class. pymeshfix is plugging the same hole the catalog describes.

### Group B — Open-fan / boundary-present fixtures (CATALOG-CONSISTENT, growth incidental-but-benign)

These fixtures encode predicates or degeneracy checks on open meshes (no closed surface claim). The open boundary edges are structurally necessary for the branch being exercised. pymeshfix filling those boundaries is not contradicted by the claim but is also not what the catalog is testing.

| Fixture | Triangles | Bnd | Defect class | Why boundary edges exist |
|---------|-----------|-----|-------------|--------------------------|
| Me030 | 3 → 4 | 1 | `degenerate_triangle` (degree-3 cap) | 3 outer base edges are open by design |
| Me1090 | 3 → 4 | 1 | `degenerate_triangle` (equilateral degree-3 cap) | same as Me030 |
| Me111 | 2 → 4 | 1 | `mesh_adjacent_shared_edge` (shared-edge-proper predicate) | 2-triangle patch; 4 free edges |
| Me118 | 2 → 4 | 1 | `self_intersection_face_pair` (3D proper SI) | 2-triangle patch; 4 free edges |
| Me130 | 4 → 6 | 1 | `redundant_vertex_removal_blocked` (pyramid fan) | 4 outer base edges open |
| Me233 | 2 → 4 | 1 | `topTriangle_vertex_z_collection_v3` | 2-triangle patch; 4 free edges |
| Me267 | 6 → 8 | 1 | `degenerate_edge` (cylinder topology, chi=0) | cylinder has two open rings |
| Me383 | 4 → 6 | 1 | `double_flat_vertex_two_ridges` | open 4-triangle fan; 4 outer boundary edges |
| Me385 | 4 → 6 | 1 | `singular_half_fold_vertex` | open 4-triangle fan; 6 outer boundary edges |
| Me386 | 4 → 6 | 1 | `double_flat_vertex_collinear_axis` | open 4-triangle fan; 4 outer boundary edges |
| Me471 | 3 → 4 | 2 | `border_edge_link_condition_violation` | three disconnected fans; many open edges |
| Me562 | 3 → 6 | 1 | `loop_subdivision` (sharp crease) | open strip; 5 outer boundary edges |
| Me021 | 3 → 4 | 2 | `self_intersection_sharp_edge` | SI fixture with open intruder edges |
| Me1123 | 3 → 4 | 2 | `self_intersection_sharp_crease` | SI + crease; open floor/wall/intruder edges |

Growth here is a side effect of the open boundary topology, not a hole-fill in the catalog sense. pymeshfix treats any open loop as a hole; the catalog does not make a hole claim for these.

**Classification: CATALOG-CONSISTENT** (the catalog does not forbid open meshes; it simply tests predicates that happen to require open boundaries). pymeshfix's behavior is not wrong, just not the dimension being tested.

### Group C — Disconnected-component fixtures (CATALOG-CONSISTENT, growth incidental)

All four have two disconnected components (main patch + micro noise triangle). Each component's boundary is open. pymeshfix fills one or both open hulls.

| Fixture | Triangles | Bnd | Defect class |
|---------|-----------|-----|-------------|
| Me014 | 5 → 6 | 2 | `disconnected_components` (noise island 100 units away) |
| Me240 | 5 → 6 | 2 | `disconnected_components` (negligible-size area threshold) |
| Me291 | 5 → 6 | 2 | `disconnected_components` (CC labelling dedup) |
| Me921 | 5 → 6 | 2 | `disconnected_components` (keep_largest) |

Growth is incidental; the catalog claim is about CC identification/removal, not hole-filling.

**Classification: CATALOG-CONSISTENT.**

---

## Summary table

| Bucket | Count | Catalog-consistent | Needs investigation |
|--------|-------|--------------------|---------------------|
| Rejected | 6 | 6 | 0 |
| Grew — genuine hole | 3 | 3 | 0 |
| Grew — open-boundary predicate/degeneracy | 14 | 14 | 0 |
| Grew — disconnected components | 4 | 4 | 0 |
| **Total** | **27** | **27** | **0** |

All 27 fixtures are catalog-consistent. No fixture needs regen or Notes update.

---

## New defect-class signal from rejected bucket

pymeshfix's "empty vertices or triangles array" rejection is effectively a 7th oracle on top of the six catalog-defined guards. All six rejected fixtures intentionally encode the zero-triangle case for six different functions. The convergence of pymeshfix's rejection with the catalog's claims provides independent corroboration: the empty-mesh structural invariant is correctly encoded across all six.

If a `pymeshfix_rejects_empty_mesh` assertion kind is ever added to the schema, all six fixtures would be natural candidates. That is a future expansion item, not a blocker.

---

## Punch list

**Nothing requires immediate action.** Audit is informational only.

Optional future work (add to BACKLOG.md if desired):
- Add `pymeshfix_rejects` assertion kind to schema; back-fill Me140/Me320/Me360/Me450/Me550/Me660.
- Add `pymeshfix_fills_hole` assertion kind for Me328/Me761/Me850 to make the oracle signal machine-readable.
- The 14 "open-boundary predicate" fixtures (Group B) could get a Notes field documenting that open edges are structural, not intended as hole-fill targets — useful when running hole-fill oracles at scale.
