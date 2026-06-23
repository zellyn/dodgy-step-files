# Mesh-repair coverage map (MeshFix + CGAL PMP)

Per-method enumeration of the public repair surface of two open-source
mesh-repair libraries, analogous to the OCCT deep-pass at
[`OCCT_HEAL_COVERAGE_V2.md`](OCCT_HEAL_COVERAGE_V2.md). Built by
~13 Haiku worker agents fetching upstream `.cpp`/`.h` files and
enumerating per-method repair branches.

**Coverage status: ~0%.** This catalog currently has effectively
no mesh fixtures — the entries below are a punch list of repair
operations a future mesh sub-corpus must exercise. The original
[`MESH_DEFECT_TAXONOMY.md`](MESH_DEFECT_TAXONOMY.md) survey)
recommended the mesh sub-catalog live in a separate repo at
`github.com/zellyn/dodgy-mesh-files`; this coverage map should
guide that repo's first fixture batches.

## Totals

| Library | Methods | Repair branches |
|---|---:|---:|
| `CGAL_PMP` | 75 | 322 |
| `MeshFix` | 76 | 490 |
| **Total** | **151** | **812** |

## Methodology

**MeshFix v2.1** (Attene): fetched all `src/` files from upstream
at <https://github.com/MarcoAttene/MeshFix-V2.1> and enumerated 70
public methods spanning `tin.cpp`, `checkAndRepair.cpp`,
`holeFilling.cpp`, `detectIntersections.cpp`, `marchIntersections.cpp`,
`io.cpp`, `triangle.cpp`, `edge.cpp`, `vertex.cpp`, `subdivision.cpp`,
plus the `meshfix.cpp` CLI driver.

**CGAL Polygon Mesh Processing**: fetched repair-related headers
from `Polygon_mesh_processing/include/CGAL/Polygon_mesh_processing/`
on the master branch and enumerated 74 public functions including
`remove_degenerate_faces`, `remove_self_intersections`,
`stitch_borders`, `repair_polygon_soup`, `triangulate_hole` family,
`autorefine_and_remove_self_intersections`,
`duplicate_non_manifold_vertices`, `orient_polygon_soup` etc.

Branches are decision points where the kernel takes a different
repair action for a different defect input. Each branch carries a
`search_anchors` list (defect-class phrases). When a fixture in the
`dodgy-mesh-files` corpus is eventually authored, its text will be
regex-matched against these anchors and the branch tagged COVERED.

Everything in this report is prose-laundered. No MeshFix or CGAL
code or test data was copied into this catalog.

## Coverage map

### CGAL_PMP

#### `(multiple)`
(27 methods, 115 branches)

##### `PMP.Polygon_soup_orienter.duplicate_singular_vertices` — lines 343–425
(12 branches; 10 COVERED by Me070–Me079; 2 SKIPPED — see notes)

- **Branch 1** @ line 346 — *incident_polygon_collection* — COVERED (Me070–Me079 all exercise the per-vertex incident-polygon build step)
- **Branch 2** @ line 351 — *vertex_iteration* — COVERED (Me074: 2 singular vertices iterated; all fixtures exercise the loop)
- **Branch 3** @ line 355 — *isolated_vertex_skip* — COVERED (Me075: isolated vertex v5 has empty incident-polygon list → skip)
- **Branch 4** @ line 358 — *link_cc_count* — COVERED (Me072, Me078: nb_link_ccs reaches 3; Me070 etc: reaches 2)
- **Branch 5** @ line 363 — *non_manifold_vertex* — COVERED (all 10 fixtures: at least one vertex has nb_link_ccs > 1)
- **Branch 6** @ line 370 — *visitor_callback* — SKIPPED (requires custom visitor object; pure-geometry fixture cannot demonstrate a C++ callback; no Python-level observable)
- **Branch 7** @ line 385 — *link_traversal_cw* — COVERED (Me073: 3-triangle strip forces 3-step CW walk; Me076, Me077, Me079 also)
- **Branch 8** @ line 388 — *wraparound_check* — COVERED (Me076: closed 4-triangle ring — CW traversal returns to start, triggering wraparound break)
- **Branch 9** @ line 395 — *link_traversal_ccw* — COVERED (Me077: open 3-triangle strip exercises CW-then-CCW two-direction traversal)
- **Branch 10** @ line 417 — *point_duplication_loop* — COVERED (Me074: 2 singular vertices → loop runs twice; Me072/Me078 also)
- **Branch 11** @ line 421 — *new_point_creation* — COVERED (Me072, Me078: 3 fans → 2 new clone points created)
- **Branch 12** @ line 423 — *polygon_index_replacement* — COVERED (Me079: 4-triangle strip → 4 polygon indices replaced for one CC)

Fixture IDs: Me070 Me071 Me072 Me073 Me074 Me075 Me076 Me077 Me078 Me079

##### `PMP.Polygon_soup_orienter.fill_edge_map` — lines 180–214
(3 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 182 — *edge_recording*
  - What it tests: For each polygon edge, record polygon in edge map
  - Repair action: edges[i0][i1].insert(polygon_id)
  - Suggested fixture: defect mentioning 'edges[i0][i1].insert(i)'
- **Branch 2** @ line 201 — *non_manifold_detection*
  - What it tests: Count incoming/outgoing edges at each directed edge
  - Repair action: if nb_edges > 2, mark as non-manifold
  - Suggested fixture: defect mentioning 'if (nb_edges > 2)'
- **Branch 3** @ line 209 — *non_manifold_visitor_callback*
  - What it tests: Invoke visitor for non-manifold edge discovery
  - Repair action: visitor.non_manifold_edge(i0, i1, nb_edges)
  - Suggested fixture: defect mentioning 'visitor.non_manifold_edge'

##### `PMP.Polygon_soup_orienter.orient` — lines 235–336
(11 branches; 10 COVERED by Me170–Me179 — wave 7A; Branch 11 *neighbor_skip* subsumed by Me179)

- **Branch 1** @ line 247 — *polygon_scan* — **Me170**
  - What it tests: Find next unoriented polygon
  - Repair action: increment polygon_index; break when all oriented
  - Suggested fixture: defect mentioning 'while (polygon_index != polygons.size() && oriented[polygon_index])'
- **Branch 2** @ line 258 — *component_init* — **Me171**
  - What it tests: Mark found polygon as oriented and push to stack
  - Repair action: oriented[polygon_index] = true; stack.push(polygon_index)
  - Suggested fixture: defect mentioning 'oriented[polygon_index] = true'
- **Branch 3** @ line 260 — *dfs_traversal* — **Me172**
  - What it tests: Process polygons in connected component via DFS
  - Repair action: while (!stack.empty())
  - Suggested fixture: defect mentioning 'while(! stack.empty() )'
- **Branch 4** @ line 268 — *edge_iteration* — **Me173**
  - What it tests: For each edge of current polygon
  - Repair action: check if edge is manifold and consistent
  - Suggested fixture: defect mentioning 'for(P_ID ih = 0 ; ih < size'
- **Branch 5** @ line 274 — *marked_edge_skip* — **Me174**
  - What it tests: Edge marked as non-manifold or conflicting
  - Repair action: continue to next edge
  - Suggested fixture: defect mentioning 'if( is_edge_marked(i1,i2,marked_edges) ) continue'
- **Branch 6** @ line 277 — *same_orientation_edge* — **Me175**
  - What it tests: Check edge (i1->i2) for same-orientation neighbors
  - Repair action: if found, check orientation compatibility
  - Suggested fixture: defect mentioning 'Edge_map_iterator it_same_orient'
- **Branch 7** @ line 285 — *multi_neighbor_same_orient* — **Me176**
  - What it tests: Edge has > 1 incident polygon with same orientation
  - Repair action: reverse one polygon's orientation or mark edge
  - Suggested fixture: defect mentioning 'if (it_same_orient->second.size() > 1)'
- **Branch 8** @ line 292 — *orientation_conflict* — **Me177**
  - What it tests: Neighbor polygon already oriented but incompatibly
  - Repair action: mark edge; don't reverse
  - Suggested fixture: defect mentioning 'if(oriented[index])'
- **Branch 9** @ line 299 — *orientation_reversal* — **Me178**
  - What it tests: Neighbor not yet oriented, reverse it for consistency
  - Repair action: inverse_orientation(index); push to stack
  - Suggested fixture: defect mentioning 'inverse_orientation(index)'
- **Branch 10** @ line 321 — *opposite_orientation_edge* — **Me179**
  - What it tests: Check for edge (i2->i1) indicating opposite orientation
  - Repair action: if both neighbors exist and unique, push unoriented one
  - Suggested fixture: defect mentioning 'if( it_other_orient != edges[i2].end() )'
- **Branch 11** @ line 327 — *neighbor_skip* — subsumed by Me179 (correctly-oriented neighbor in opposite-direction pairing)
  - What it tests: Neighbor already oriented correctly
  - Repair action: continue to next edge
  - Suggested fixture: defect mentioning 'if(oriented[index]) continue'

##### `PMP.connected_component` — lines 132–179
(5 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 140 — *Loop_control*
  - What it tests: Repeat while condition holds
  - Repair action: Continue iteration or break
  - Suggested fixture: defect mentioning 'while'
- **Branch 2** @ line 144 — *Visited_vertex_dedup*
  - What it tests: Tests: !already_processed.insert(seed_face
  - Repair action: Skip already-seen elements
  - Suggested fixture: defect mentioning 'handled[', 'already_processed'
- **Branch 3** @ line 146 — *Iteration_construct*
  - What it tests: Loop over range
  - Repair action: Process collection elements
  - Suggested fixture: defect mentioning 'for'
- **Branch 4** @ line 149 — *Logic_guard*
  - What it tests: Tests: ! get(ecmap, edge(hd, pmesh
  - Repair action: Conditional branching
  - Suggested fixture: defect mentioning '!'
- **Branch 5** @ line 151 — *Null_face_check*
  - What it tests: Tests:  neighbor != boost::graph_traits<PolygonMesh>::nul
  - Repair action: Stop at mesh boundary
  - Suggested fixture: defect mentioning 'null_face', 'opposite'

##### `PMP.connected_components` — lines 198–248
(8 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 224 — *Iteration_construct*
  - What it tests: Loop over range
  - Repair action: Process collection elements
  - Suggested fixture: defect mentioning 'for'
- **Branch 2** @ line 226 — *Visited_vertex_dedup*
  - What it tests: Tests: handled[get(fimap,f
  - Repair action: Skip already-seen elements
  - Suggested fixture: defect mentioning 'handled[', 'already_processed'
- **Branch 3** @ line 229 — *Loop_control*
  - What it tests: Repeat while condition holds
  - Repair action: Continue iteration or break
  - Suggested fixture: defect mentioning 'while'
- **Branch 4** @ line 234 — *Visited_vertex_dedup*
  - What it tests: Tests:  handled[fq_id]
  - Repair action: Skip already-seen elements
  - Suggested fixture: defect mentioning 'handled[', 'already_processed'
- **Branch 5** @ line 237 — *Iteration_construct*
  - What it tests: Loop over range
  - Repair action: Process collection elements
  - Suggested fixture: defect mentioning 'for'
- **Branch 6** @ line 239 — *Logic_guard*
  - What it tests: Tests:  get(ecmap, edge(h, pmesh
  - Repair action: Conditional branching
  - Suggested fixture: defect mentioning 'get(ecmap,'
- **Branch 7** @ line 242 — *Null_face_check*
  - What it tests: Tests:  fqo != GT::null_face(
  - Repair action: Stop at mesh boundary
  - Suggested fixture: defect mentioning 'null_face', 'opposite'
- **Branch 8** @ line 244 — *Visited_vertex_dedup*
  - What it tests: Tests:  !handled[get(fimap,fqo
  - Repair action: Skip already-seen elements
  - Suggested fixture: defect mentioning 'handled[', 'already_processed'

##### `PMP.degenerate_edges.mesh` — lines 128–135
(0 branches; all UNCOVERED — no mesh fixtures exist yet)


##### `PMP.degenerate_edges.range` — lines 109–123
(0 branches; all UNCOVERED — no mesh fixtures exist yet)


##### `PMP.degenerate_faces.mesh` — lines 232–239
(0 branches; all UNCOVERED — no mesh fixtures exist yet)


##### `PMP.degenerate_faces.range` — lines 214–227
(0 branches; all UNCOVERED — no mesh fixtures exist yet)


##### `PMP.internal.detect_identical_mergeable_vertices` — lines 150–206
(7 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 159 — *sorting_by_point*
  - What it tests: Sort halfedges by target point coordinate
  - Repair action: std::sort with Less_on_point_of_target comparator
  - Suggested fixture: defect mentioning 'std::sort( cycle_hedges.begin()'
- **Branch 2** @ line 169 — *identical_point_detection*
  - What it tests: Current halfedge target point == previous halfedge target point
  - Repair action: add both to candidate group
  - Suggested fixture: defect mentioning 'if(get(vpm, target(cycle_hedges[i]'
- **Branch 3** @ line 173 — *candidate_group_creation*
  - What it tests: New identical point detected
  - Repair action: resize candidate_hedges_with_id; push i-1 and i
  - Suggested fixture: defect mentioning 'candidate_hedges_with_id.resize'
- **Branch 4** @ line 175 — *consecutive_identical_collection*
  - What it tests: Continue adding consecutive halfedges with same target point
  - Repair action: push to current candidate group
  - Suggested fixture: defect mentioning 'while(++i != nbv)'
- **Branch 5** @ line 182 — *group_break*
  - What it tests: Target point differs; exit inner while
  - Repair action: increment i and break
  - Suggested fixture: defect mentioning 'else {', '++i;', 'break;'
- **Branch 6** @ line 196 — *interval_sanitation*
  - What it tests: Ensure candidate intervals are disjoint or nested
  - Repair action: call sanitize_candidates(); remove conflicting groups
  - Suggested fixture: defect mentioning 'sanitize_candidates'
- **Branch 7** @ line 198 — *output_conversion*
  - What it tests: Convert sanitized candidate IDs back to halfedge descriptors
  - Repair action: populate hedges_with_identical_point_target
  - Suggested fixture: defect mentioning 'for(const std::vector<std::size_t>& candidates'

##### `PMP.internal.sanitize_candidates` — lines 72–146
(6 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 77 — *empty_input*
  - What it tests: No candidate groups to sanitize
  - Repair action: return immediately
  - Suggested fixture: defect mentioning 'if(candidate_hedges_with_id.empty())', 'return'
- **Branch 2** @ line 81 — *outer_group_iteration*
  - What it tests: For each first candidate group
  - Repair action: compare against all later groups
  - Suggested fixture: defect mentioning 'for(std::size_t fr_id=0, fr_end=nm_vertices_n-1'
- **Branch 3** @ line 92 — *inner_group_iteration*
  - What it tests: For each second candidate group (after first)
  - Repair action: check for overlapping/incompatible intervals
  - Suggested fixture: defect mentioning 'for(std::size_t sr_id=i+1, sr_end=nm_vertices_n'
- **Branch 4** @ line 106 — *interval_overlap_detection*
  - What it tests: Two intervals are incompatibly interleaved
  - Repair action: remove group with larger range
  - Suggested fixture: defect mentioning 'if((second_left < first_left', 'candidate_hedges_with_id.erase'
- **Branch 5** @ line 140 — *recursive_resanitization*
  - What it tests: Re-check after erasing incompatible group
  - Repair action: call sanitize_candidates recursively
  - Suggested fixture: defect mentioning 'return sanitize_candidates(cycle_hedges'
- **Branch 6** @ line 110 — *range_size_comparison*
  - What it tests: Determine which group to remove by range magnitude
  - Repair action: prefer removing larger range
  - Suggested fixture: defect mentioning 'const std::size_t first_candidates_range', 'const std::size_t second_candidates_range'

##### `PMP.is_cap_triangle_face` — lines 458–493
(5 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 460 — *Logic_guard*
  - What it tests: Tests: is_zero(sq_lengths[0]
  - Repair action: Conditional branching
  - Suggested fixture: defect mentioning 'is_zero(sq_lengths[0]'
- **Branch 2** @ line 471 — *Logic_guard*
  - What it tests: Tests: !neg_sp
  - Repair action: Conditional branching
  - Suggested fixture: defect mentioning '!neg_sp'
- **Branch 3** @ line 481 — *Logic_guard*
  - What it tests: Tests: handle_triplet(p, q, r, 0
  - Repair action: Conditional branching
  - Suggested fixture: defect mentioning 'handle_triplet(p,'
- **Branch 4** @ line 483 — *Logic_guard*
  - What it tests: Tests: handle_triplet(q, r, p, 1
  - Repair action: Conditional branching
  - Suggested fixture: defect mentioning 'handle_triplet(q,'
- **Branch 5** @ line 485 — *Logic_guard*
  - What it tests: Tests: handle_triplet(r, p, q, 2
  - Repair action: Conditional branching
  - Suggested fixture: defect mentioning 'handle_triplet(r,'

##### `PMP.is_degenerate_triangle_face` — lines 159–184
(0 branches; all UNCOVERED — no mesh fixtures exist yet)


##### `PMP.keep_connected_components.by_face_range` — lines 805–828
(0 branches; all UNCOVERED — no mesh fixtures exist yet)


##### `PMP.keep_connected_components.by_id` — lines 649–653
(0 branches; all UNCOVERED — no mesh fixtures exist yet)


##### `PMP.keep_large_connected_components` — lines 469–530
(0 branches; all UNCOVERED — no mesh fixtures exist yet)


##### `PMP.merge_duplicate_points_in_polygon_soup` — lines 522–593
(5 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 538 — *empty_input*
  - What it tests: Empty points range
  - Repair action: fallthrough to identity map (no merge needed)
  - Suggested fixture: defect mentioning 'const std::size_t ini_points_n = points.size()'
- **Branch 2** @ line 547 — *point_dedup_scan*
  - What it tests: For each input point, check if geometrically identical to prior
  - Repair action: insert into Unique_point_container or retrieve existing id
  - Suggested fixture: defect mentioning 'for(std::size_t i=0; i<ini_points_n', 'point_to_id.insert', 'is_insert_successful'
- **Branch 3** @ line 558 — *new_unique_point*
  - What it tests: Insert was successful (point not seen before)
  - Repair action: push point to unique_points
  - Suggested fixture: defect mentioning 'if(id == unique_points.size())', 'unique_points.push_back'
- **Branch 4** @ line 563 — *merge_needed_check*
  - What it tests: Unique count differs from original
  - Repair action: if no duplicates, skip polygon remapping
  - Suggested fixture: defect mentioning 'if(unique_points.size() != ini_points_n)'
- **Branch 5** @ line 565 — *polygon_remap*
  - What it tests: For each polygon, remap vertex indices to unique point indices
  - Repair action: polygon[i] = point_index[polygon[i]]
  - Suggested fixture: defect mentioning 'for(P_ID polygon_index=0', 'polygon[i] = point_index'

##### `PMP.merge_duplicate_polygons_in_polygon_soup` — lines 934–1048
(11 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 946 — *erase_policy_selection*
  - What it tests: Named parameter erase_policy control
  - Repair action: select KEEP_ONE (default), ERASE_ALL, or KEEP_ONE_IF_ODD
  - Suggested fixture: defect mentioning 'erase_policy = choose_parameter'
- **Branch 2** @ line 955 — *orientation_requirement*
  - What it tests: Named parameter require_same_orientation flag
  - Repair action: control whether reversed polygons are considered duplicates
  - Suggested fixture: defect mentioning 'same_orientation = choose_parameter'
- **Branch 3** @ line 971 — *duplicate_collection*
  - What it tests: Scan all polygons for canonical duplicates using hash+equality
  - Repair action: collect groups of duplicate polygon indices
  - Suggested fixture: defect mentioning 'collect_duplicate_polygons'
- **Branch 4** @ line 973 — *early_exit_empty*
  - What it tests: No duplicates found
  - Repair action: return 0; skip removal logic
  - Suggested fixture: defect mentioning 'if(all_duplicate_polygons.empty())'
- **Branch 5** @ line 996 — *duplicate_group_iteration*
  - What it tests: For each group of duplicate polygons
  - Repair action: process one group at a time from back
  - Suggested fixture: defect mentioning 'while(!all_duplicate_polygons.empty())'
- **Branch 6** @ line 1001 — *keep_decision*
  - What it tests: Determine which duplicates to keep/remove based on erase_policy
  - Repair action: set i to 0 (erase all), 1 (keep one), or size%2 (keep if odd)
  - Suggested fixture: defect mentioning '(erase_policy == Policy::ERASE_ALL)', '(erase_policy == Policy::KEEP_ONE)'
- **Branch 7** @ line 1004 — *removal_iteration*
  - What it tests: For each polygon marked for removal
  - Repair action: skip if already treated, else swap to end region
  - Suggested fixture: defect mentioning 'for(; i<duplicate_polygons.size()'
- **Branch 8** @ line 1007 — *treated_skip*
  - What it tests: Polygon already removed in prior duplicate group
  - Repair action: continue to next
  - Suggested fixture: defect mentioning 'if(treated[polygon_to_remove_id])', 'continue'
- **Branch 9** @ line 1026 — *swap_to_end*
  - What it tests: Move polygon to removal region via swap
  - Repair action: std::swap(polygons[swap_position], polygons[polygon_to_remove_pos])
  - Suggested fixture: defect mentioning 'std::swap(polygons'
- **Branch 10** @ line 1029 — *mark_treated*
  - What it tests: Mark polygon as removed
  - Repair action: treated[polygon_to_remove_id] = true
  - Suggested fixture: defect mentioning 'treated[polygon_to_remove_id] = true'
- **Branch 11** @ line 1035 — *final_erase*
  - What it tests: Physically erase all removed polygons from container
  - Repair action: polygons.erase(first, polygons.end())
  - Suggested fixture: defect mentioning 'polygons.erase'

##### `PMP.merge_duplicated_vertices_in_boundary_cycle` — lines 286–321
(5 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 305 — *boundary_cycle_traversal*
  - What it tests: Start halfedge validation - halt if precondition fails
  - Repair action: precondition assert; skip cycle processing
  - Suggested fixture: defect mentioning 'is_valid_halfedge_descriptor', 'CGAL_precondition'
- **Branch 2** @ line 312 — *vertex_detection*
  - What it tests: Detection of vertices with identical point coordinates along a cycle
  - Repair action: identify all mergeable vertex groups
  - Suggested fixture: defect mentioning 'detect_identical_mergeable_vertices', 'hedges_with_identical_point_target'
- **Branch 3** @ line 314 — *merge_iteration*
  - What it tests: For each group of identical-point vertices, merge target vertices
  - Repair action: call merge_vertices_in_range per group
  - Suggested fixture: defect mentioning 'for(const std::vector', 'hedges_with_identical_point_target'
- **Branch 4** @ line 319 — *merge_execution*
  - What it tests: Merge operation on a single vertex group
  - Repair action: topologically merge vertices, rebuild halfedge links
  - Suggested fixture: defect mentioning 'internal::merge_vertices_in_range'
- **Branch 5** @ line 307 — *halfedge_advance*
  - What it tests: Cycle completeness check - is start==h after traversal
  - Repair action: exit do-while if full cycle traversed
  - Suggested fixture: defect mentioning 'while(start!=h)', 'h=next(h, pm)'

##### `PMP.merge_duplicated_vertices_in_boundary_cycles` — lines 345–355
(3 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 351 — *boundary_cycle_discovery*
  - What it tests: Extract all boundary cycles from mesh
  - Repair action: populate cycles vector
  - Suggested fixture: defect mentioning 'extract_boundary_cycles', 'std::back_inserter'
- **Branch 2** @ line 353 — *cycle_iteration*
  - What it tests: For each boundary cycle found, invoke single-cycle merge
  - Repair action: apply merge_duplicated_vertices_in_boundary_cycle to each
  - Suggested fixture: defect mentioning 'for(halfedge_descriptor h : cycles)'
- **Branch 3** @ line 354 — *merge_delegation*
  - What it tests: Empty cycles vector (no boundaries)
  - Repair action: no-op if mesh is closed
  - Suggested fixture: defect mentioning 'merge_duplicated_vertices_in_boundary_cycle'

##### `PMP.orient_polygon_soup` — lines 543–564
(5 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 556 — *initial_point_count*
  - What it tests: Capture initial point count for non-manifoldness detection
  - Repair action: store in initial_nb_pts
  - Suggested fixture: defect mentioning 'std::size_t initial_nb_pts = points.size()'
- **Branch 2** @ line 559 — *edge_map_fill*
  - What it tests: Build edge-to-polygon mapping and detect non-manifold edges
  - Repair action: orienter.fill_edge_map()
  - Suggested fixture: defect mentioning 'orienter.fill_edge_map()'
- **Branch 3** @ line 560 — *polygon_orientation_pass*
  - What it tests: DFS traversal of polygon dual graph to reorient polygons consistently
  - Repair action: orienter.orient()
  - Suggested fixture: defect mentioning 'orienter.orient()'
- **Branch 4** @ line 561 — *vertex_duplication*
  - What it tests: Duplicate non-manifold vertices to ensure manifold topology
  - Repair action: orienter.duplicate_singular_vertices()
  - Suggested fixture: defect mentioning 'orienter.duplicate_singular_vertices()'
- **Branch 5** @ line 563 — *manifoldness_check*
  - What it tests: Check if new points were added (indicates non-manifold input)
  - Repair action: return (initial_nb_pts==points.size())
  - Suggested fixture: defect mentioning 'return initial_nb_pts==points.size()'

##### `PMP.remove_connected_components.by_face_range` — lines 739–767
(3 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 740 — *Iteration_construct*
  - What it tests: Loop over range
  - Repair action: Process collection elements
  - Suggested fixture: defect mentioning 'for'
- **Branch 2** @ line 741 — *Logic_guard*
  - What it tests: Tests: !get(is_cst, v
  - Repair action: Conditional branching
  - Suggested fixture: defect mentioning '!get(is_cst,'
- **Branch 3** @ line 743 — *Alternative_path*
  - What it tests: Fallback case handling
  - Repair action: Execute alternative repair
  - Suggested fixture: defect mentioning 'else'

##### `PMP.remove_connected_components.by_id` — lines 687–691
(2 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 687 — *Logic_guard*
  - What it tests: Tests: halfedge(v, pmesh
  - Repair action: Conditional branching
  - Suggested fixture: defect mentioning 'halfedge(v,'
- **Branch 2** @ line 690 — *Logic_guard*
  - What it tests: Tests: halfedge(w, pmesh
  - Repair action: Conditional branching
  - Suggested fixture: defect mentioning 'halfedge(w,'

##### `PMP.remove_invalid_polygons_in_polygon_soup` — lines 295–321
(2 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 298 — *degenerate_polygon_filter*
  - What it tests: Polygon size <= 2
  - Repair action: std::remove_if predicate returns true; polygon marked for erase
  - Suggested fixture: defect mentioning 'std::remove_if', 'polygon.size() <= 2'
- **Branch 2** @ line 311 — *erase_execution*
  - What it tests: Remove all invalid polygons from container
  - Repair action: polygons.erase(rit, polygons.end())
  - Suggested fixture: defect mentioning 'polygons.erase'

##### `PMP.remove_isolated_points_in_polygon_soup` — lines 404–487
(7 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 410 — *empty_input*
  - What it tests: Empty points container
  - Repair action: return 0; skip processing
  - Suggested fixture: defect mentioning 'if(points.empty())', 'return 0'
- **Branch 2** @ line 420 — *point_usage_scan*
  - What it tests: Iterate all polygons to mark visited points
  - Repair action: update visited[] bitset
  - Suggested fixture: defect mentioning 'for(P_ID polygon_index', 'visited[polygon[i]] = true'
- **Branch 3** @ line 430 — *unused_point_detection*
  - What it tests: Iterate through visited[] to find unused indices
  - Repair action: on unvisited point, swap to end-of-keep region
  - Suggested fixture: defect mentioning 'if(!visited[i])', 'std::swap(points[swap_position], points[i])'
- **Branch 4** @ line 432 — *early_termination*
  - What it tests: Current index exceeds first_unused_pos boundary
  - Repair action: break nested loop
  - Suggested fixture: defect mentioning 'if(i >= first_unused_pos)', 'break'
- **Branch 5** @ line 462 — *removal_count_check*
  - What it tests: Zero points were removed
  - Repair action: early return without erase/remap
  - Suggested fixture: defect mentioning 'if(removed_points_n == 0)'
- **Branch 6** @ line 468 — *physical_erase*
  - What it tests: Erase unused point portion from container
  - Repair action: points.erase() tail segment
  - Suggested fixture: defect mentioning 'points.erase'
- **Branch 7** @ line 471 — *index_remapping*
  - What it tests: Renumber polygon vertex indices after point removal
  - Repair action: polygon[i] = id_remapping[polygon[i]]
  - Suggested fixture: defect mentioning 'id_remapping[polygon[i]]'

##### `PMP.simplify_polygons_in_polygon_soup` — lines 156–181
(4 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 165 — *polygon_iteration*
  - What it tests: For each polygon in soup
  - Repair action: check and simplify
  - Suggested fixture: defect mentioning 'for(P_ID polygon_index=0'
- **Branch 2** @ line 168 — *degenerate_polygon_skip*
  - What it tests: Polygon size <= 1 (degenerate)
  - Repair action: skip simplification, continue to next
  - Suggested fixture: defect mentioning 'if(polygon.size() <= 1)', 'continue'
- **Branch 3** @ line 171 — *consecutive_duplicate_removal*
  - What it tests: simplify_polygon() finds and removes consecutive identical vertices
  - Repair action: erase duplicate, iterate until clean
  - Suggested fixture: defect mentioning 'simplify_polygon(points, polygon, traits)'
- **Branch 4** @ line 172 — *modification_count*
  - What it tests: simplify_polygon() return value indicates change
  - Repair action: increment simplified_polygons_n counter
  - Suggested fixture: defect mentioning '++simplified_polygons_n'

##### `PMP.split_pinched_polygons_in_polygon_soup` — lines 201–278
(11 branches; **COVERED** — Me060–Me069)

- **Branch 1** @ line 215 — *dynamic_polygon_iteration* → **Me065**
  - What it tests: Iterate through polygons with dynamic size (new ones added during loop)
  - Repair action: re-evaluate polygons.size() each iteration
- **Branch 2** @ line 225 — *small_polygon_skip* → **Me064**
  - What it tests: Polygon has 3 or fewer points (can't be pinched)
  - Repair action: continue to next polygon
- **Branch 3** @ line 229 — *precondition_check* — SKIPPED (CGAL_assertion internal; not observable from geometry)
  - What it tests: Polygon must not have consecutive duplicates
  - Repair action: CGAL_assertion fails if violated
- **Branch 4** @ line 234 — *point_uniqueness_check* → **Me066**
  - What it tests: For each point in polygon, check if already encountered
  - Repair action: insert into unique_points map
- **Branch 5** @ line 241 — *pinch_detection* → **Me060**, **Me068**
  - What it tests: Insert failed - point seen before in this polygon
  - Repair action: split polygon at that point
- **Branch 6** @ line 249 — *pinch_split_boundary* → **Me067**
  - What it tests: Locate previous occurrence of pinched point
  - Repair action: prev_id = is_insert_successful.first->second
- **Branch 7** @ line 252 — *split_polygon_1* → **Me061**
  - What it tests: Create first sub-polygon from prev_id to current index
  - Repair action: Polygon_3 split_polygon_1(polygon.begin() + prev_id, ...)
- **Branch 8** @ line 255 — *split_polygon_2* → **Me061** (paired with Branch 7)
  - What it tests: Create second sub-polygon wrapping around the pinch
  - Repair action: Combine begin..prev_id and i..end segments
- **Branch 9** @ line 268 — *polygon_replacement* → **Me062**
  - What it tests: Swap original with first sub-polygon
  - Repair action: std::swap(polygon, split_polygon_1)
- **Branch 10** @ line 269 — *new_polygon_append* → **Me062**, **Me063**, **Me069**
  - What it tests: Append second sub-polygon for re-processing
  - Repair action: polygons.push_back(split_polygon_2)
- **Branch 11** @ line 272 — *loop_break* → **Me063**
  - What it tests: Exit inner loop after split detected
  - Repair action: break to next polygon iteration


#### `(multiple: repair_self_intersections.h, self_intersections.h, autorefinement.h, repair.h)`
(6 methods, 53 branches)

##### `PMP.autorefine_impl::autorefine_triangle_soup` — lines 1040–1186
(9 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 1040 — *no-intersections-trivial-case*
  - What it tests: whether self-intersection collection found zero pairs
  - Repair action: copy verbatim and return vs enter refinement pipeline
  - Suggested fixture: defect mentioning 'si_pairs.empty', 'number_of_output_triangles'
- **Branch 2** @ line 1055 — *degenerate-face-tagging*
  - What it tests: whether (f,f) pairs indicate degenerate faces in bbox intersection results
  - Repair action: tag degenerate faces for skipping vs include in refinement
  - Suggested fixture: defect mentioning 'p.first==p.second', 'is_degen'
- **Branch 3** @ line 1127 — *intersection-point-count-cases*
  - What it tests: the number of intersection points between two triangles (1, 2, or 3+)
  - Repair action: branch to appropriate sub-triangle insertion strategy per case
  - Suggested fixture: defect mentioning 'nbi', 'switch(nbi)', 'case 1:'
- **Branch 4** @ line 1130 — *single-point-containment-branch*
  - What it tests: whether intersection consists of single point only
  - Repair action: add point to both triangles (case 1)
  - Suggested fixture: defect mentioning 'case 1:', 'add_point<1>', 'add_point<2>'
- **Branch 5** @ line 1136 — *segment-intersection-two-point-branch*
  - What it tests: whether intersection is a line segment (two endpoints)
  - Repair action: add two points and create segment if not on shared edge (case 2)
  - Suggested fixture: defect mentioning 'case 2:', 'on_same_edge', 'segments.emplace_back'
- **Branch 6** @ line 1155 — *polygon-intersection-multi-point-branch*
  - What it tests: whether intersection is a polygon (3+ vertices)
  - Repair action: add all points and create polygon boundary segments (default case)
  - Suggested fixture: defect mentioning 'default:', 'ipt_ids1[i]', 'ipt_ids2[i]'
- **Branch 7** @ line 1183 — *coplanarity-tracking*
  - What it tests: whether intersecting triangles are coplanar
  - Repair action: track for downstream special handling vs non-coplanar intersection
  - Suggested fixture: defect mentioning 'triangles_are_coplanar', 'coplanar_triangles'
- **Branch 8** @ line 1284 — *parallel-vs-sequential-deduplication*
  - What it tests: whether TBB is linked and parallel execution was requested
  - Repair action: deduplicate points/segments in parallel vs sequential loop
  - Suggested fixture: defect mentioning 'CGAL_LINKED_WITH_TBB', 'parallel_execution', 'tbb::parallel_for'
- **Branch 9** @ line 1224 — *duplicate-point-detection-in-dedup*
  - What it tests: whether adjacent points in sorted list are geometrically identical
  - Repair action: collapse to single id via id_map vs keep separate
  - Suggested fixture: defect mentioning 'points[indices[i]]==points[indices[i+1]]', 'id_map'

##### `PMP.autorefine_triangle_soup` — lines 1729–1748
(2 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 1738 — *snap-rounding-vs-direct-refinement*
  - What it tests: whether apply_iterative_snap_rounding parameter is enabled
  - Repair action: dispatch to snap-rounding implementation vs direct autorefinement
  - Suggested fixture: defect mentioning 'apply_iterative_snap_rounding', 'polygon_soup_snap_rounding'
- **Branch 2** @ line 1722 — *rounding-success-vs-partial-result*
  - What it tests: whether snap rounding converged within max iterations (return value)
  - Repair action: return success or partial result with unresolved SIs
  - Suggested fixture: defect mentioning 'apply_iterative_snap_rounding', 'maximum_number', 'iterations'

##### `PMP.do_faces_intersect` — lines 216–307
(7 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 238 — *shared-edge-vs-incident-vertex*
  - What it tests: whether two faces share a full edge (not just a vertex)
  - Repair action: apply coplanarity and overlap check vs test shared-vertex case
  - Suggested fixture: defect mentioning 'faces_have_a_shared_edge', 'coplanar'
- **Branch 2** @ line 240 — *identical-face-soup-deduplication*
  - What it tests: whether allow_identical_face is true (soup mode) and both triangles are identical
  - Repair action: return false for identical faces in soups vs continue check
  - Suggested fixture: defect mentioning 'allow_identical_face', 'verts[2]==verts[3]'
- **Branch 3** @ line 247 — *shared-edge-coplanarity-orientation*
  - What it tests: whether shared-edge faces are coplanar and properly oriented
  - Repair action: classify as overlapping SI vs non-overlapping edge-share
  - Suggested fixture: defect mentioning 'coplanar', 'coplanar_orientation', 'CGAL::POSITIVE'
- **Branch 4** @ line 264 — *shared-vertex-presence-detection*
  - What it tests: whether faces share any vertex
  - Repair action: perform detailed segment-triangle tests vs full geometric SI check
  - Suggested fixture: defect mentioning 'shared', 'hv[i] == gv[j]'
- **Branch 5** @ line 292 — *opposite-segment-vs-triangle-containment*
  - What it tests: whether a triangle contains the segment opposite to the shared vertex (first triangle)
  - Repair action: return true if contained else test other triangle
  - Suggested fixture: defect mentioning 'do_intersect(t1, s2)', 'do_intersect(t2, s1)'
- **Branch 6** @ line 303 — *full-geometric-triangle-si*
  - What it tests: whether triangles intersect geometrically without sharing vertices or edges
  - Repair action: return geometric SI result vs false
  - Suggested fixture: defect mentioning 'do_intersect(th, tg)'
- **Branch 7** @ line 150 — *edge-orientation-search-mode*
  - What it tests: when testing shared vertex, whether to swap indices to find the shared edge
  - Repair action: apply permutation to find correct shared-edge orientation
  - Suggested fixture: defect mentioning 'if (i==0)', 'vh[1]=f[i]', 'vh[2]=f[(i+1)%3]'

##### `PMP.remove_connected_components_of_negligible_size` — lines 154–346
(9 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 180 — *area-threshold-default-inference*
  - What it tests: whether area_threshold was supplied or must be computed from bbox
  - Repair action: compute 1% of bbox-diagonal-squared vs use explicit threshold
  - Suggested fixture: defect mentioning 'is_default_area_threshold', 'bbox_diagonal'
- **Branch 2** @ line 181 — *volume-threshold-default-inference*
  - What it tests: whether volume_threshold was supplied or must be computed from bbox
  - Repair action: compute 1% of bbox-diagonal-cubed vs use explicit threshold
  - Suggested fixture: defect mentioning 'is_default_volume_threshold', 'bbox_diagonal'
- **Branch 3** @ line 223 — *area-check-applicability*
  - What it tests: whether area-based thresholding is enabled (non-zero or default)
  - Repair action: include area criterion in component-removal decision vs skip
  - Suggested fixture: defect mentioning 'use_areas', 'area_threshold > 0'
- **Branch 4** @ line 224 — *volume-check-applicability*
  - What it tests: whether volume-based thresholding is enabled (non-zero or default)
  - Repair action: include volume criterion in component-removal decision vs skip
  - Suggested fixture: defect mentioning 'use_volumes', 'volume_threshold > 0'
- **Branch 5** @ line 226 — *threshold-criteria-absence*
  - What it tests: whether both area and volume thresholds are disabled
  - Repair action: return 0 (no removal) vs continue to computation
  - Suggested fixture: defect mentioning '!use_areas && !use_volumes'
- **Branch 6** @ line 237 — *dry-run-vs-mutation*
  - What it tests: whether dry_run parameter is true (non-destructive mode)
  - Repair action: collect removable faces only vs actually remove them
  - Suggested fixture: defect mentioning 'dry_run'
- **Branch 7** @ line 265 — *volume-computation-closedness*
  - What it tests: whether each connected component is topologically closed (no border edges)
  - Repair action: mark as non-closed and skip volume computation vs include in volume calc
  - Suggested fixture: defect mentioning 'is_border', 'cc_closeness'
- **Branch 8** @ line 279 — *closed-component-volume-skip*
  - What it tests: whether a component is known to be non-closed before volume computation
  - Repair action: skip volume computation for open components
  - Suggested fixture: defect mentioning '!cc_closeness[i]', 'continue'
- **Branch 9** @ line 316 — *area-or-volume-removal-logic*
  - What it tests: whether a component satisfies either volume-small (if closed) or area-small criterion
  - Repair action: mark for removal if either threshold exceeded
  - Suggested fixture: defect mentioning '(use_volumes && cc_closeness[i] && component_volumes[i] <= volume_threshold)', '(use_areas && component_areas[i] <= area_threshold)'

##### `PMP.remove_self_intersections` — lines 2356–2527
(15 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 2379 — *genus-preservation-requirement*
  - What it tests: whether to preserve topological genus (preserve_genus NP)
  - Repair action: duplicate non-manifold vertices when preserve_genus=false
  - Suggested fixture: defect mentioning 'preserve_genus', 'duplicate_non_manifold_vertices'
- **Branch 2** @ line 2383 — *treatment-scope-selection*
  - What it tests: whether to treat all connected components even without self-intersections (treat_all_CCs NP)
  - Repair action: process CCs regardless of internal SI presence when treat_all_CCs=true
  - Suggested fixture: defect mentioning 'treat_all_CCs', 'apply_per_connected_component'
- **Branch 3** @ line 2397 — *smoothing-phase-strategy*
  - What it tests: whether to use smoothing as a repair attempt (use_smoothing NP)
  - Repair action: branch to smoothing-based healing vs hole-filling approach
  - Suggested fixture: defect mentioning 'use_smoothing', 'remove_self_intersections_with_smoothing'
- **Branch 4** @ line 2413 — *output-filter-applicability*
  - What it tests: whether a filter predicate is supplied to exclude certain self-intersections from processing
  - Repair action: apply filter when present to skip interior-disjoint pairs
  - Suggested fixture: defect mentioning 'filter_output_iterator', 'filter_t'
- **Branch 5** @ line 2463 — *face-selection-emptiness-detection*
  - What it tests: whether previous iteration had topology blockers and no faces remain to process
  - Repair action: recompute self-intersections vs exit loop early
  - Suggested fixture: defect mentioning 'faces_to_treat.empty', 'self_intersections'
- **Branch 6** @ line 2150 — *internal-vs-external-si-classification*
  - What it tests: whether self-intersections exist within a CC or only with external CCs
  - Repair action: skip processing (treat_all_CCs=false) vs continue to hole-fill
  - Suggested fixture: defect mentioning 'does_self_intersect', 'treat_all_CCs'
- **Branch 7** @ line 2161 — *containment-envelope-enforcement*
  - What it tests: whether the input has a polyhedral containment envelope (containment_epsilon > 0)
  - Repair action: validate patch against envelope vs skip validation
  - Suggested fixture: defect mentioning 'Polyhedral_envelope', 'containment_epsilon'
- **Branch 8** @ line 2192 — *smoothing-local-vs-global-focus*
  - What it tests: whether smoothing should only apply to SI-bearing CCs or all selected regions
  - Repair action: condition smoothing on internal SI presence
  - Suggested fixture: defect mentioning 'use_smoothing', 'self_intersects'
- **Branch 9** @ line 2196 — *constraint-preservation-mode*
  - What it tests: whether to constrain high-dihedral-angle edges during smoothing (first pass)
  - Repair action: apply sharp-edge constraints vs unconstrained smoothing
  - Suggested fixture: defect mentioning 'constrain_sharp_edges', 'strong_dihedral_angle'
- **Branch 10** @ line 2207 — *smoothing-fallback-escalation*
  - What it tests: whether constrained smoothing failed and needs re-attempt without constraints
  - Repair action: retry smoothing without sharp-edge constraints
  - Suggested fixture: defect mentioning 'fixed_by_smoothing', 'constrain_sharp_edges'
- **Branch 11** @ line 2264 — *topology-genus-classification*
  - What it tests: whether selected CC is topologically a disk (chi=1) or has higher genus/holes
  - Repair action: branch to complex-topology handler vs disk-hole-filling
  - Suggested fixture: defect mentioning 'euler_characteristic_of_selection', 'handle_CC_with_complex_topology'
- **Branch 12** @ line 2041 — *expansion-step-depth-control*
  - What it tests: whether to expand face selection by multiple topological layers (step > 0)
  - Repair action: iteratively expand neighborhood vs work on initial SI region only
  - Suggested fixture: defect mentioning 'step', 'expand_face_selection'
- **Branch 13** @ line 2069 — *bounding-box-obb-transform-applicability*
  - What it tests: whether oriented-bounding-box compactification is enabled (CGAL_PMP_REPAIR_SI_USE_OBB)
  - Repair action: use OBB-based selection vs axis-aligned-box selection
  - Suggested fixture: defect mentioning 'oriented_bounding_box', 'Aff_transformation'
- **Branch 14** @ line 2135 — *singleton-cc-rejection*
  - What it tests: whether compactified region consists of single face only
  - Repair action: skip further processing (no topology to heal)
  - Suggested fixture: defect mentioning 'cc_faces.size() == 1', 'continue'
- **Branch 15** @ line 2311 — *iteration-convergence-stalling-detection*
  - What it tests: whether the current step changed the mesh topology at all
  - Repair action: restore face list and skip SI recomputation vs recompute with new config
  - Suggested fixture: defect mentioning 'something_was_done', 'faces_to_treat.swap'

##### `PMP.self_intersections_impl` — lines 343–523
(11 branches; 10 covered by Me050–Me059; 1 skipped — Branch 5 TBB-availability-guard is compile-time link flag, not a geometry property)

- **Branch 1** @ line 371 — *output-count-limit-applicability* — **Me051**
  - What it tests: whether maximum_number named parameter was supplied
  - Repair action: enable early termination counter vs uncapped collection
  - Fixture: Me051 — two SI pairs at x=0 and x=10; limit=1 stops after pair A
- **Branch 2** @ line 373 — *zero-limit-trivial-rejection* — **Me052**
  - What it tests: whether supplied maximum_number is exactly 0 (vacuous case)
  - Repair action: return immediately without processing vs continue
  - Fixture: Me052 — one SI pair present; limit=0 returns immediately with empty output
- **Branch 3** @ line 400 — *degenerate-face-vs-real-si* — **Me050**
  - What it tests: whether a face is degenerate (collinear vertices) or forms a valid triangle
  - Repair action: report (f,f) pair or create bbox vs skip box creation
  - Fixture: Me050 — tri0 is collinear (area=0); SI-impl reports (tri0,tri0) self-pair
- **Branch 4** @ line 402 — *throw-vs-accumulate-exception-mode* — **Me053**
  - What it tests: whether throw_on_SI flag is set for early termination on first intersection
  - Repair action: throw exception vs append to output iterator
  - Fixture: Me053 — single XY/XZ crossing pair; throw_on_SI fires on first hit
- **Branch 5** @ line 435 — *tbb-availability-guard* — SKIPPED
  - What it tests: whether TBB was linked and Parallel_tag was requested
  - Repair action: branch to parallel implementation vs sequential fallback
  - Skip reason: compile-time link flag (CGAL_LINKED_WITH_TBB), not a geometry property; same mesh geometry as B6/B7
- **Branch 6** @ line 457 — *throw-vs-collect-in-parallel* — **Me057**
  - What it tests: whether throw_on_SI requires early termination in parallel code
  - Repair action: use throwing filter vs concurrent vector accumulation
  - Fixture: Me057 — two SI pairs at y=0 and y=8; parallel throw_on_SI fires on first hit
- **Branch 7** @ line 459 — *output-limit-in-parallel* — **Me058**
  - What it tests: whether count-based limit must be enforced during parallel execution
  - Repair action: wrap output with counter functor vs direct callback
  - Fixture: Me058 — four SI pairs along Z-axis; atomic counter fires at limit=3
- **Branch 8** @ line 469 — *catch-limit-exception-recovery* — **Me059**
  - What it tests: whether output-limit exception was caught during parallel execution
  - Repair action: copy accumulated pairs sequentially and exit vs continue
  - Fixture: Me059 — five SI pairs along X-axis; parallel catch block fires at limit=4
- **Branch 9** @ line 495 — *throw-vs-collect-in-sequential* — **Me054**
  - What it tests: whether throw_on_SI requires early termination in sequential code
  - Repair action: use throwing filter vs standard callback
  - Fixture: Me054 — two SI pairs; sequential throw_on_SI fires on pair A before pair B
- **Branch 10** @ line 497 — *output-limit-in-sequential* — **Me055**
  - What it tests: whether count-based limit must be enforced during sequential execution
  - Repair action: wrap output with counter lambda vs direct callback
  - Fixture: Me055 — three SI pairs; Count_and_throw_filter fires at limit=2
- **Branch 11** @ line 510 — *catch-limit-exception-recovery-sequential* — **Me056**
  - What it tests: whether output-limit exception was caught during sequential execution
  - Repair action: return early vs continue processing
  - Fixture: Me056 — four SI pairs; sequential catch block fires at limit=3


#### `(multiple: shape_predicates.h, connected_components.h, polygon_soup_self_intersections.h, orient_polygon_soup_extension.h, polygon_soup_to_polygon_mesh.h, orientation.h, repair.h)`
(11 methods, 30 branches)

##### `PMP.compatible_orientations` — lines 1179–1337
(4 branches; ALL COVERED — Me046–Me049)

- **Branch 1** @ line 1220 — *cyclic_orientation_flip* — **Me046**
  - What it tests: odd/even flip path around cycle
  - Repair action: mark_faces_for_flipping
  - Fixture: Me046 — pentagon fan, tri4 wound CW, antiparallel to tri0 and tri3
- **Branch 2** @ line 1260 — *non_manifold_edge* — **Me047**
  - What it tests: edge manifold property
  - Repair action: return_false_non_compatible
  - Fixture: Me047 — edge (v0,v1) shared by 3 triangles
- **Branch 3** @ line 1290 — *orientation_conflict* — **Me048**
  - What it tests: conflicting orientation constraints
  - Repair action: propagate_incompatibility
  - Fixture: Me048 — two CCW chains bridged to one CW chain; adjacent normals antiparallel
- **Branch 4** @ line 1310 — *boundary_cycle_traversal* — **Me049**
  - What it tests: consistent boundary traversal
  - Repair action: advance_halfedge
  - Fixture: Me049 — open mesh with two boundary loops; interior edge (v1,v5) shared by 2

##### `PMP.does_bound_a_volume` — lines 913–930
(3 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 918 — *connectivity_broken*
  - What it tests: boundary cycle exists
  - Repair action: return_false
  - Suggested fixture: defect mentioning 'is_closed'
- **Branch 2** @ line 922 — *orientation_inconsistent*
  - What it tests: normals consistent across components
  - Repair action: return_false
  - Suggested fixture: defect mentioning 'does_bound_a_volume'
- **Branch 3** @ line 926 — *self_intersection*
  - What it tests: no pairwise face intersections
  - Repair action: return_false
  - Suggested fixture: defect mentioning 'does_self_intersect'

##### `PMP.does_polygon_soup_self_intersect` — lines 32–60
(3 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 40 — *duplicate_point_presence*
  - What it tests: points merged to detect intersection
  - Repair action: merge_duplicate_points
  - Suggested fixture: defect mentioning 'merge_duplicate_points_in_polygon_soup'
- **Branch 2** @ line 45 — *polygon_type_mixed*
  - What it tests: triangulates non-triangle polygons
  - Repair action: triangulate_polygons
  - Suggested fixture: defect mentioning 'std::size_t(3)'
- **Branch 3** @ line 50 — *intersection_detection*
  - What it tests: calls triangle soup self-intersection check
  - Repair action: detect_pairwise_triangles
  - Suggested fixture: defect mentioning 'triangle_soup_self_intersections'

##### `PMP.is_degenerate_edge` — lines 56–93
(1 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 89 — *equal_points*
  - What it tests: endpoint positions identical (zero-length edge)
  - Repair action: collapse_edge
  - Suggested fixture: defect mentioning 'traits.equal_3_object()', 'source(e,pm)', 'target(e,pm)'

##### `PMP.is_needle_triangle_face` — lines 399–435
(4 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 428 — *aspect_ratio_extreme*
  - What it tests: aspect ratio < threshold (not needle)
  - Repair action: return_null_halfedge
  - Suggested fixture: defect mentioning 'res == -1', 'null_halfedge()'
- **Branch 2** @ line 430 — *aspect_ratio_extreme*
  - What it tests: shortest edge is e0
  - Repair action: return_shortest_edge
  - Suggested fixture: defect mentioning 'res == 0', 'return h'
- **Branch 3** @ line 432 — *aspect_ratio_extreme*
  - What it tests: shortest edge is e1
  - Repair action: return_shortest_edge
  - Suggested fixture: defect mentioning 'res == 1', 'next(h,tm)'
- **Branch 4** @ line 434 — *aspect_ratio_extreme*
  - What it tests: shortest edge is e2
  - Repair action: return_shortest_edge
  - Suggested fixture: defect mentioning 'prev(h,tm)'

##### `PMP.is_polygon_soup_a_polygon_mesh` — lines 190–232
(3 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 210 — *duplicate_vertex_in_polygon*
  - What it tests: polygon has repeated vertex indices
  - Repair action: return_false
  - Suggested fixture: defect mentioning 'is_polygon_soup_a_polygon_mesh', 'return false'
- **Branch 2** @ line 220 — *non_manifold_edge*
  - What it tests: edge shared by >2 polygons
  - Repair action: mark_as_non_manifold
  - Suggested fixture: defect mentioning 'marked_edges', 'singular'
- **Branch 3** @ line 227 — *orientation_consistency*
  - What it tests: adjacent polygons share opposite halfedges
  - Repair action: fail_orientation_check
  - Suggested fixture: defect mentioning 'fill_edge_map'

##### `PMP.keep_largest_connected_components` — lines 347–423
(4 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 401 — *component_count_mismatch*
  - What it tests: desired_num > total_components
  - Repair action: return_zero_removed
  - Suggested fixture: defect mentioning 'nb_components_to_keep'
- **Branch 2** @ line 410 — *component_size_criterion*
  - What it tests: component size >= threshold
  - Repair action: keep_or_discard_component
  - Suggested fixture: defect mentioning 'face_size_pmap', 'Face_size'
- **Branch 3** @ line 419 — *dry_run_mode*
  - What it tests: dry_run flag set
  - Repair action: skip_mesh_modification
  - Suggested fixture: defect mentioning 'dry_run', 'true', 'false'
- **Branch 4** @ line 421 — *output_iterator_presence*
  - What it tests: output_iterator provided
  - Repair action: record_removed_components
  - Suggested fixture: defect mentioning 'output_iterator', 'emptyset_iterator'

##### `PMP.orient_triangle_soup_with_reference_triangle_mesh` — lines 261–330
(3 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 280 — *concurrency_strategy*
  - What it tests: concurrency tag applied
  - Repair action: parallel_or_sequential_orientation
  - Suggested fixture: defect mentioning 'Concurrency_tag', 'Sequential_tag'
- **Branch 2** @ line 300 — *aabb_tree_construction*
  - What it tests: reference mesh spatial index
  - Repair action: build_aabb_tree
  - Suggested fixture: defect mentioning 'AABB_tree', 'reference'
- **Branch 3** @ line 315 — *triangle_degeneracy*
  - What it tests: reference triangle non-degenerate
  - Repair action: skip_degenerate_reference
  - Suggested fixture: defect mentioning 'is_degenerate_triangle_face'

##### `PMP.polygon_soup_to_polygon_mesh` — lines 286–316
(3 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 295 — *orientation_inconsistency*
  - What it tests: polygon soup oriented
  - Repair action: orient_soup_first
  - Suggested fixture: defect mentioning 'orient_polygon_soup'
- **Branch 2** @ line 305 — *correspondence_tracking*
  - What it tests: point_to_vertex mapping requested
  - Repair action: record_point_vertex_map
  - Suggested fixture: defect mentioning 'point_to_vertex_output_iterator'
- **Branch 3** @ line 310 — *correspondence_tracking*
  - What it tests: polygon_to_face mapping requested
  - Repair action: record_polygon_face_map
  - Suggested fixture: defect mentioning 'polygon_to_face_output_iterator'

##### `PMP.remove_isolated_vertices` — lines 40–57
(1 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 48 — *vertex_isolation*
  - What it tests: vertex has no incident edges
  - Repair action: remove_vertex
  - Suggested fixture: defect mentioning 'degree(v,pmesh)==0', 'remove_vertex'

##### `PMP.split_connected_components` — lines 940–957
(1 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 945 — *component_subdivision*
  - What it tests: each connected component isolated
  - Repair action: extract_to_new_mesh
  - Suggested fixture: defect mentioning 'connected_component', 'cc_meshes'


#### `(unknown)`
(9 methods, 30 branches)

##### `PMP.compatible_orientations (nesting-constraint detector)` — lines 1179–1337
(3 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 1182 — *usage-mode-dispatch*
  - What it tests: Route output to bit-vector or boolean result
  - Repair action: either populate per-face bit-map or return single bool
  - Suggested fixture: defect mentioning 'used_as_a_predicate', 'output_mode'
- **Branch 2** @ line 1192 — *nested-component-existence*
  - What it tests: Check for non-empty nesting relationships among components
  - Repair action: skip components with no nesting constraints
  - Suggested fixture: defect mentioning 'nested_cc_per_cc_shared', 'empty'
- **Branch 3** @ line 1204 — *direct-nesting-level-match*
  - What it tests: Detect direct parent-child relationship (nesting level +1)
  - Repair action: mark faces for potential flip to enable stitching compatibility
  - Suggested fixture: defect mentioning 'nesting_levels', '+1', 'parent-child'

##### `PMP.duplicate_non_manifold_vertices (repair)` — lines 317–361
(3 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 335 — *halfedge-visitation-tracking*
  - What it tests: Skip already-processed halfedges
  - Repair action: only duplicate vertices for unvisited halfedge cycles
  - Suggested fixture: defect mentioning 'visited_halfedges', 'insert'
- **Branch 2** @ line 342 — *vertex-occurrence-detection*
  - What it tests: Check if vertex already processed in different half-cycle
  - Repair action: create new vertex copy if encountering same vertex again
  - Suggested fixture: defect mentioning 'visited_vertices', 'null_h'
- **Branch 3** @ line 348 — *non-manifold-class-confirmation*
  - What it tests: Verify vertex is in known non-manifold set before duplication
  - Repair action: only duplicate confirmed non-manifold vertices
  - Suggested fixture: defect mentioning 'known_nm_vertices', 'duplicate'

##### `PMP.filter_stitchable_pairs (manifold validator)` — lines 684–780
(4 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 721 — *edge-occurrence-limit*
  - What it tests: Detect if merged vertices create multi-edge (>2 halfedges per edge)
  - Repair action: mark vertices as unstitchable if edge would exceed manifold threshold
  - Suggested fixture: defect mentioning 'it->second.size', 'case', 'edge-multiplicity'
- **Branch 2** @ line 723 — *border-two-edge-exception*
  - What it tests: Allow two border edges (boundary-loop case)
  - Repair action: accept two-halfedge case if both are border edges
  - Suggested fixture: defect mentioning 'is_border_edge', 'case 2', 'two-edge-loop'
- **Branch 3** @ line 728 — *multi-edge-vertex-disqualification*
  - What it tests: Reject vertices incident to 3+ duplicate edges
  - Repair action: add all vertices of problematic edges to unstitchable set
  - Suggested fixture: defect mentioning 'unstitchable_vertices', 'default', 'source/target'
- **Branch 4** @ line 739 — *vertex-pair-safety-check*
  - What it tests: Verify all four vertices of halfedge pair are not unstitchable
  - Repair action: exclude pair if any vertex is marked non-manifold-safe
  - Suggested fixture: defect mentioning 'unstitchable_vertices', 'source', 'target'

##### `PMP.is_non_manifold_vertex (query)` — lines 46–81
(3 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 67 — *border-incident-null-face*
  - What it tests: Count null-faced halfedges at boundary as non-manifold indicator
  - Repair action: classify vertex as non-manifold if multiple boundary null-faces
  - Suggested fixture: defect mentioning 'is_border', 'face', 'null_face'
- **Branch 2** @ line 71 — *null-face-multiplicity*
  - What it tests: Check if >1 null-faced halfedges converge at vertex
  - Repair action: return true if manifold threshold exceeded
  - Suggested fixture: defect mentioning 'incident_null_faces_counter', '>1'
- **Branch 3** @ line 79 — *cycle-break-condition*
  - What it tests: Detect termination of halfedge-ring traversal
  - Repair action: exit halfedge-loop when full ring traversed
  - Suggested fixture: defect mentioning 'target', 'v', 'break'

##### `PMP.orient (main dispatcher)` — lines 955–1013
(4 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 979 — *z-extremum-selection*
  - What it tests: Compare Z-coordinates of extremal vertices across components
  - Repair action: promote highest-Z component as reference for outward orientation
  - Suggested fixture: defect mentioning 'xtrm_vertices', 'z()', 'comparison'
- **Branch 2** @ line 985 — *self-intersection-component-skip*
  - What it tests: Detect empty/finished connected component set
  - Repair action: exit loop when all components processed or all self-intersecting
  - Suggested fixture: defect mentioning 'cc_to_handle', 'any', 'break'
- **Branch 3** @ line 1001 — *self-intersecting-pair-detection*
  - What it tests: Mark component pairs that self-intersect
  - Repair action: skip nesting test for self-intersecting component pairs
  - Suggested fixture: defect mentioning 'self_intersecting_cc', 'make_sorted_pair'
- **Branch 4** @ line 1007 — *orientation-assignment-by-nesting*
  - What it tests: Check if component is inside (bounded) or outside (unbounded)
  - Repair action: assign inward or outward orientation based on nesting level
  - Suggested fixture: defect mentioning 'side_of_cc', 'ON_BOUNDED_SIDE'

##### `PMP.reverse_face_orientations (face_range)` — lines 310–335
(1 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 313 — *border-edge-uniqueness-tracking*
  - What it tests: Track border edges in face-range to avoid double-reversal
  - Repair action: insert border edge into set and reverse only on first occurrence
  - Suggested fixture: defect mentioning 'is_border', 'already_seen', 'insert'

##### `PMP.reverse_face_orientations (mesh_with_polylines)` — lines 270–297
(1 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 287 — *border-edge-double-flip-prevention*
  - What it tests: Detect and skip already-flipped border edges in polyline meshes
  - Repair action: skip reversal of border edge if seen before (prevent double-reversal)
  - Suggested fixture: defect mentioning 'is_border', 'already_seen', 'insert'

##### `PMP.run_stitch_borders (vertex-merge and edge-topology)` — lines 564–682
(4 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 597 — *vertex-merge-necessity*
  - What it tests: Check if target-vertex merge is needed (different representatives)
  - Repair action: update all halfedges ending at old vertex to new master
  - Suggested fixture: defect mentioning 'v_to_keep', 'h1_tgt', 'union_find'
- **Branch 2** @ line 603 — *second-vertex-pair-distinct*
  - What it tests: Verify source of h2 is different from target of h1 before merging
  - Repair action: merge h2-source with master vertex only if distinct
  - Suggested fixture: defect mentioning 'h1_tgt', 'h2_src', 'not-identical'
- **Branch 3** @ line 615 — *second-target-merge-necessity*
  - What it tests: Check if h2-target needs merging with its representative
  - Repair action: update halfedges at h2-target to use master
  - Suggested fixture: defect mentioning 'h2_tgt', 'v_to_keep', 'union_find'
- **Branch 4** @ line 621 — *opposite-edge-source-merge*
  - What it tests: Check if h1-source is distinct from h2-target before merging
  - Repair action: conditionally merge h1-source with h2-target master
  - Suggested fixture: defect mentioning 'h1_src', 'h2_tgt', 'distinct-check'

##### `PMP.stitch_borders (internal dispatcher)` — lines 426–517
(7 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 426 — *border-component-independence*
  - What it tests: Whether stitching should occur within each connected component separately
  - Repair action: route to per-component or global border-edge collection
  - Suggested fixture: defect mentioning 'per_cc', 'border_edges', 'connected_components'
- **Branch 2** @ line 440 — *non-border-edge-skip*
  - What it tests: Skip interior edges; only process boundary halfedges
  - Repair action: continue loop, skip non-border edges
  - Suggested fixture: defect mentioning 'is_border', 'halfedge_range', 'continue'
- **Branch 3** @ line 443 — *per-component-boundary-segregation*
  - What it tests: Segregate border edges by connected component
  - Repair action: append to per-component boundary list or process globally
  - Suggested fixture: defect mentioning 'per_cc', 'border_edges_per_cc', 'connected_component_id'
- **Branch 4** @ line 449 — *processing-strategy-dispatch*
  - What it tests: Choose per-component vs global processing
  - Repair action: enter loop over connected components or single iteration
  - Suggested fixture: defect mentioning 'per_cc', 'num_cc', 'for-loop'
- **Branch 5** @ line 470 — *non-manifold-pair-filter*
  - What it tests: Skip pairs that would create non-manifold edges after stitching
  - Repair action: only output manifold-safe halfedge pairs
  - Suggested fixture: defect mentioning 'manifold_halfedge_pairs', 'filter', 'halfedge_pairs'
- **Branch 6** @ line 473 — *halfedge-pair-orientation*
  - What it tests: Ensure first halfedge is canonical representative
  - Repair action: swap pair if needed to maintain canonical order
  - Suggested fixture: defect mentioning 'hd_kpr', 'swap', 'halfedge_pair'
- **Branch 7** @ line 492 — *single-pass-manifold-filtering*
  - What it tests: In non-per-CC mode, filter manifold pairs once
  - Repair action: output only manifold-safe pairs in global iteration
  - Suggested fixture: defect mentioning 'else', 'manifold_halfedge_pairs', 'nb_pairs'


#### `PMP_Mesh_repair/include/CGAL/Polygon_mesh_processing/manifoldness.h`
(1 methods, 3 branches)

##### `PMP.non_manifold_vertices` — lines 242–314
(3 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 260 — *nonmanifold_vertex_detection*
  - What it tests: vertex has multiple border halfedges
  - Repair action: emit representative from each disconnected umbrella
  - Suggested fixture: defect mentioning 'next', 'halfedge_around_target'
- **Branch 2** @ line 280 — *umbrella_sector_boundary*
  - What it tests: halfedge is on boundary of umbrella sector
  - Repair action: mark sector boundary and advance
  - Suggested fixture: defect mentioning 'is_border'
- **Branch 3** @ line 295 — *visited_umbrella_detection*
  - What it tests: sector already enumerated
  - Repair action: skip already-visited sectors
  - Suggested fixture: defect mentioning 'visited_set'


#### `PMP_Mesh_repair/include/CGAL/Polygon_mesh_processing/orient_polygon_soup_extension.h`
(1 methods, 3 branches)

##### `PMP.orient_triangle_soup_with_reference_triangle_soup` — lines 131–215
(3 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 155 — *reference_degenerate_triangle*
  - What it tests: reference triangle is non-degenerate
  - Repair action: skip degenerate reference triangles
  - Suggested fixture: defect mentioning 'is_degenerate'
- **Branch 2** @ line 175 — *closest_face_search*
  - What it tests: closest_point_and_primitive result is valid
  - Repair action: use closest non-degenerate reference face
  - Suggested fixture: defect mentioning 'closest_point_and_primitive'
- **Branch 3** @ line 200 — *orientation_flip_decision*
  - What it tests: dot product of normals determines orientation
  - Repair action: flip triangle if negative dot product
  - Suggested fixture: defect mentioning 'dot_product'


#### `PMP_Mesh_repair/include/CGAL/Polygon_mesh_processing/orientation.h`
(4 methods, 14 branches)

##### `PMP.merge_reversible_connected_components` — lines 1019–1141
(3 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 1050 — *component_area_filter*
  - What it tests: component area below threshold
  - Repair action: mark small components as mergeable
  - Suggested fixture: defect mentioning 'component.area()'
- **Branch 2** @ line 1080 — *orientation_flip_feasibility*
  - What it tests: flipping component enables boundary stitching
  - Repair action: flip component orientation and stitch
  - Suggested fixture: defect mentioning 'reverse_face_orientations', 'stitch'
- **Branch 3** @ line 1110 — *stitching_compatibility_check*
  - What it tests: border halfedges are geometrically compatible
  - Repair action: merge vertices only if compatible
  - Suggested fixture: defect mentioning 'stitch_borders'

##### `PMP.orient` — lines 361–420
(3 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 375 — *component_orientation_selection*
  - What it tests: outward_orientation parameter value
  - Repair action: orient component inward or outward
  - Suggested fixture: defect mentioning 'outward_orientation'
- **Branch 2** @ line 395 — *nesting_depth_parity*
  - What it tests: component nesting level odd or even
  - Repair action: determine orientation based on depth
  - Suggested fixture: defect mentioning 'nesting_depth'
- **Branch 3** @ line 410 — *component_orientation_consistency*
  - What it tests: component is closed and orientable
  - Repair action: skip non-closed components
  - Suggested fixture: defect mentioning 'is_closed'

##### `PMP.orient_to_bound_a_volume` — lines 955–1013
(3 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 975 — *single_component_trivial*
  - What it tests: mesh has one connected component
  - Repair action: orient single component outward
  - Suggested fixture: defect mentioning 'num_components == 1'
- **Branch 2** @ line 990 — *nesting_depth_calculation*
  - What it tests: component nesting level determined via ray casting
  - Repair action: count ray-intersection parity
  - Suggested fixture: defect mentioning 'nesting_level'
- **Branch 3** @ line 1005 — *parent_child_orientation_rule*
  - What it tests: component nesting relationship to parent
  - Repair action: orient child opposite to parent
  - Suggested fixture: defect mentioning 'parent_component'

##### `PMP.volume_connected_components` — lines 518–876
(5 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 570 — *self_intersection_detection*
  - What it tests: faces have ray-casting sign inconsistency
  - Repair action: flag self-intersection error
  - Suggested fixture: defect mentioning 'self_intersecting'
- **Branch 2** @ line 600 — *boundary_component_detection*
  - What it tests: component is open with boundary edges
  - Repair action: flag boundary_error
  - Suggested fixture: defect mentioning 'is_closed'
- **Branch 3** @ line 640 — *orientation_consistency*
  - What it tests: interior and exterior faces share consistent normal orientation
  - Repair action: flag orientation_error
  - Suggested fixture: defect mentioning 'normal consistency'
- **Branch 4** @ line 720 — *nesting_depth_assignment*
  - What it tests: ray-casting parity determines depth
  - Repair action: assign volume_id based on depth and parent
  - Suggested fixture: defect mentioning 'volume_id'
- **Branch 5** @ line 800 — *nested_component_orientation*
  - What it tests: child components have opposite parent orientation
  - Repair action: validate nesting invariant
  - Suggested fixture: defect mentioning 'parent'


#### `PMP_Mesh_repair/include/CGAL/Polygon_mesh_processing/repair_degeneracies.h`
(8 methods, 41 branches)

##### `PMP.remove_a_border_edge.simple` — lines 1716–1722
(1 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 1721 — *Wrapper without tracking sets*
  - What it tests: Border edge removal without state tracking
  - Repair action: Create empty sets and delegate
  - Suggested fixture: defect mentioning 'EdgeSet& edge_set', 'FaceSet& face_set'

##### `PMP.remove_a_border_edge.with_sets` — lines 1508–1714
(6 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 1193 — *Link condition satisfied*
  - What it tests: Border edge can be collapsed safely
  - Repair action: Standard edge collapse
  - Suggested fixture: defect mentioning 'does_satisfy_link_condition', 'collapse_edge'
- **Branch 2** @ line 1237 — *Link condition violation*
  - What it tests: Border edge collapse would break topology
  - Repair action: Identify and remove incident region
  - Suggested fixture: defect mentioning 'common_incident_edges', 'marked_faces'
- **Branch 3** @ line 1255 — *Boundary reached during region exploration*
  - What it tests: Region to be removed contacts outer boundary
  - Repair action: Abort removal, return null_vertex
  - Suggested fixture: defect mentioning 'Boundary reached during exploration', 'not a topological disk'
- **Branch 4** @ line 1296 — *Region not topological disk*
  - What it tests: Marked faces don't form a disk
  - Repair action: Skip removal, return null_vertex
  - Suggested fixture: defect mentioning 'is_selection_a_topological_disk', 'not handled'
- **Branch 5** @ line 1304 — *Isolated region*
  - What it tests: Region is completely surrounded by border
  - Repair action: Cannot remove, return null_vertex
  - Suggested fixture: defect mentioning 'is_border(hk1', 'isolated region'
- **Branch 6** @ line 1348 — *Halfedge identity match*
  - What it tests: hk2 equals hp (specific topology case)
  - Repair action: Different restoration of halfedge pointers
  - Suggested fixture: defect mentioning 'hk2 == hp', 'case handling'

##### `PMP.remove_almost_degenerate_faces.face_range` — lines 1011–1357
(8 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 1022 — *Needle triangle*
  - What it tests: Triangle with extreme edge-length ratio (short edge detection)
  - Repair action: Collapse shortest edge
  - Suggested fixture: defect mentioning 'is_needle_triangle_face', 'min_edge'
- **Branch 2** @ line 1031 — *Needle triangle (non-collapsible)*
  - What it tests: Shortest edge violates link condition
  - Repair action: Flip edge instead of collapse
  - Suggested fixture: defect mentioning 'does_satisfy_link_condition', 'flip'
- **Branch 3** @ line 1055 — *Border edge needle*
  - What it tests: Shortest edge is on mesh boundary
  - Repair action: Remove incident face instead of collapsing
  - Suggested fixture: defect mentioning 'is_border', 'Euler::remove_face'
- **Branch 4** @ line 1087 — *Needle flip impossible*
  - What it tests: Flip would create duplicate edge
  - Repair action: Mark edge for deferred processing
  - Suggested fixture: defect mentioning 'halfedge already exists', 'unflippable'
- **Branch 5** @ line 1005 — *Cap triangle*
  - What it tests: Triangle has angle near 180 degrees
  - Repair action: Detect cap and mark for flip
  - Suggested fixture: defect mentioning 'is_cap_triangle_face', 'cap_threshold'
- **Branch 6** @ line 1031 — *Cap with border edge*
  - What it tests: Cap triangle opposite edge is boundary
  - Repair action: Remove face to avoid non-manifold vertex
  - Suggested fixture: defect mentioning 'is_border(opposite', 'removal_is_nm'
- **Branch 7** @ line 1059 — *Cap flip fails*
  - What it tests: Cap flip violates link condition
  - Repair action: Attempt collapse of opposite edge
  - Suggested fixture: defect mentioning 'cap but cannot flip', 'collapse instead'
- **Branch 8** @ line 1118 — *No progress*
  - What it tests: Loop iteration made no repairs
  - Repair action: Return false, exit early
  - Suggested fixture: defect mentioning 'something_was_done', 'return false'

##### `PMP.remove_almost_degenerate_faces.mesh` — lines 1359–1363
(1 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 1134 — *Full-mesh overload*
  - What it tests: Convenience method applied to all faces
  - Repair action: Delegate to face_range variant
  - Suggested fixture: defect mentioning 'faces(tmesh)', 'remove_almost_degenerate_faces'

##### `PMP.remove_degenerate_edges.mesh` — lines 2130–2134
(1 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 1970 — *Full-mesh degenerate edge removal*
  - What it tests: Convenience method for all edges
  - Repair action: Call range variant with edges(tmesh)
  - Suggested fixture: defect mentioning 'edges(tmesh)', 'remove_degenerate_edges'

##### `PMP.remove_degenerate_edges.range` — lines 2124–2128
(1 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 1962 — *Edge range without explicit face set*
  - What it tests: Face tracking not user-provided
  - Repair action: Create empty face_set, delegate to full variant
  - Suggested fixture: defect mentioning 'std::set<face_descriptor> face_set'

##### `PMP.remove_degenerate_edges.range_with_face_set` — lines 1750–2122
(10 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 1558 — *Zero-length edge (link condition OK)*
  - What it tests: Degenerate edge satisfies link condition
  - Repair action: Collapse edge directly
  - Suggested fixture: defect mentioning 'does_satisfy_link_condition', 'collapse_edge'
- **Branch 2** @ line 1581 — *Zero-length edge (link condition violated)*
  - What it tests: Link condition fails for zero-length edge
  - Repair action: Call remove_a_border_edge or explore complex removal
  - Suggested fixture: defect mentioning 'link condition not satisfied', 'marked_faces'
- **Branch 3** @ line 1585 — *Border edge with triangle hole*
  - What it tests: Degenerate border edge bounds 3-edge hole
  - Repair action: Call Euler::fill_hole or skip if preserve_genus
  - Suggested fixture: defect mentioning 'is_border', 'is_triangle(hd', 'fill_hole'
- **Branch 4** @ line 1591 — *Genus preservation blocking hole fill*
  - What it tests: Hole fill would change topology
  - Repair action: Mark as not fully removable
  - Suggested fixture: defect mentioning 'preserve_genus', 'all_removed=false'
- **Branch 5** @ line 1630 — *Both edge endpoints on boundary*
  - What it tests: Interior edge with both vertices on border
  - Repair action: Cannot collapse, mark as failed
  - Suggested fixture: defect mentioning 'impossible = true', 'halfedges_around'
- **Branch 6** @ line 1678 — *Non-link-condition removal via face marking*
  - What it tests: Complex topology requires multi-face removal
  - Repair action: Mark faces, validate topological disk, star hole
  - Suggested fixture: defect mentioning 'marked_faces', 'add_center_vertex'
- **Branch 7** @ line 1741 — *Non-manifold vertices on marked region*
  - What it tests: Marked faces region has non-manifold boundary
  - Repair action: Mark additional small connected components
  - Suggested fixture: defect mentioning 'nb_cc != 1', 'exploration_finished'
- **Branch 8** @ line 1846 — *Marked region not topological disk after expansion*
  - What it tests: Even after marking extra faces, topology invalid
  - Repair action: Skip removal, mark all_removed=false
  - Suggested fixture: defect mentioning 'is_selection_a_topological_disk', 'continue'
- **Branch 9** @ line 1704 — *Whole connected component selected*
  - What it tests: All non-border faces marked for removal
  - Repair action: Skip removal, would delete entire component
  - Suggested fixture: defect mentioning 'border.empty()', 'whole connected component'
- **Branch 10** @ line 1778 — *Cycle of border edges in component*
  - What it tests: Connected component union-find has boundary cycle
  - Repair action: Skip removal, nested hole case
  - Suggested fixture: defect mentioning 'index != nb_cc', 'cycle of border edges'

##### `PMP.remove_degenerate_faces` — lines 2164–2589
(13 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 2049 — *No degenerate faces*
  - What it tests: Input face set is empty
  - Repair action: Return true immediately
  - Suggested fixture: defect mentioning 'degenerate_face_set.empty()'
- **Branch 2** @ line 2052 — *All faces degenerate*
  - What it tests: Entire mesh is degenerate
  - Repair action: Remove all elements
  - Suggested fixture: defect mentioning 'degenerate_face_set.size() == faces_size'
- **Branch 3** @ line 2061 — *Adjacent degenerate faces missed*
  - What it tests: Input range is partial, need to sanitize
  - Repair action: Expand set to include connected degenerate neighbors
  - Suggested fixture: defect mentioning 'is_range_full_mesh', 'faces_to_visit'
- **Branch 4** @ line 2078 — *Null-edge face detection*
  - What it tests: After edge removal, new degenerate faces appear
  - Repair action: Add newly degenerate faces to set
  - Suggested fixture: defect mentioning 'is_degenerate_triangle_face(adj_fd', 'faces_to_visit'
- **Branch 5** @ line 2118 — *Border degenerate face*
  - What it tests: Degenerate triangle on mesh boundary
  - Repair action: Handle separately from interior faces
  - Suggested fixture: defect mentioning 'is_border(opposite', 'border_deg_faces'
- **Branch 6** @ line 2170 — *Degenerate edge in degenerate face*
  - What it tests: Face has zero-length edge
  - Repair action: Remove degenerate edges first
  - Suggested fixture: defect mentioning 'is_degenerate_edge', 'remove_degenerate_edges'
- **Branch 7** @ line 2186 — *Degree-3 vertex in cap*
  - What it tests: Vertex with 3 neighbors is center of near-cap
  - Repair action: Remove center vertex via Euler operator
  - Suggested fixture: defect mentioning 'degree == 3', 'remove_center_vertex'
- **Branch 8** @ line 2244 — *Single isolated degenerate face*
  - What it tests: No adjacent degenerate faces detected
  - Repair action: Flip longest edge instead of region removal
  - Suggested fixture: defect mentioning 'detect_cc_of_degenerate_triangles = false', 'flip'
- **Branch 9** @ line 2319 — *Connected component of collinear faces*
  - What it tests: Multiple adjacent degenerate triangles share vertices
  - Repair action: Collect connected component and remove as disk
  - Suggested fixture: defect mentioning 'cc_faces', 'boundary_hedges'
- **Branch 10** @ line 2407 — *Non-disk topology in component*
  - What it tests: Degenerate face group doesn't form topological disk
  - Repair action: Mark as unremovable, continue loop
  - Suggested fixture: defect mentioning 'v-e+f = 1', 'not a topological disk'
- **Branch 11** @ line 2464 — *Non-monotone boundary*
  - What it tests: Boundary points don't sort monotonically along line
  - Repair action: Skip component removal
  - Suggested fixture: defect mentioning 'non_monotone_border', 'WARNING'
- **Branch 12** @ line 2256 — *Edge flip impossible*
  - What it tests: Flip would create pre-existing edge
  - Repair action: Remove face instead, mark success uncertain
  - Suggested fixture: defect mentioning 'flip is not possible', 'all_removed = false'
- **Branch 13** @ line 2292 — *Border face removal*
  - What it tests: Degenerate face on boundary
  - Repair action: Remove face directly without flip
  - Suggested fixture: defect mentioning 'opposite_face == GT::null_face()', 'remove_face'


#### `PMP_Mesh_repair/include/CGAL/Polygon_mesh_processing/triangulate_hole.h`
(8 methods, 33 branches)

##### `triangulate_and_refine_hole.deprecated_overload` — lines 428–442
(1 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 432 — *deprecation_guard*
  - What it tests: CGAL_NO_DEPRECATED_CODE macro
  - Repair action: Entire overload gated by ifndef, forwards to new named-parameter version
  - Suggested fixture: defect mentioning 'CGAL_DEPRECATED', 'CGAL_NO_DEPRECATED_CODE'

##### `triangulate_and_refine_hole.main` — lines 370–407
(5 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 381 — *output_iterator_choice*
  - What it tests: face_output_iterator parameter presence/absence
  - Repair action: If provided use it; else use Emptyset_iterator (discards faces)
  - Suggested fixture: defect mentioning 'face_output_iterator_t', 'Lookup_named_param_def'
- **Branch 2** @ line 387 — *output_iterator_choice*
  - What it tests: vertex_output_iterator parameter presence/absence
  - Repair action: If provided use it; else use Emptyset_iterator (discards vertices)
  - Suggested fixture: defect mentioning 'vertex_output_iterator_t', 'Emptyset_iterator'
- **Branch 3** @ line 394 — *triangulation_failure_handling*
  - What it tests: Whether triangulate_hole succeeds before refine
  - Repair action: Silently continues even if no patch created; refine is no-op on empty patch
  - Suggested fixture: defect mentioning 'triangulate_hole', 'std::back_inserter'
- **Branch 4** @ line 402 — *visitor_callback_optional*
  - What it tests: Visitor parameter presence for phase tracking
  - Repair action: Use provided visitor or Default_visitor (no-op); invoke start/end_refine_phase callbacks
  - Suggested fixture: defect mentioning 'visitor_t', 'start_refine_phase', 'Default_visitor'
- **Branch 5** @ line 404 — *density_control_parameterization*
  - What it tests: density_control_factor parameter forwarding to refine()
  - Repair action: Pass all parameters (including density_control_factor) to refine() function
  - Suggested fixture: defect mentioning 'density_control_factor', 'refine'

##### `triangulate_hole.deprecated_overload` — lines 254–265
(1 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 257 — *deprecation_guard*
  - What it tests: CGAL_NO_DEPRECATED_CODE macro
  - Repair action: Entire overload gated by ifndef, forwards to new named-parameter version
  - Suggested fixture: defect mentioning 'CGAL_DEPRECATED', 'CGAL_NO_DEPRECATED_CODE'

##### `triangulate_hole.main` — lines 165–236
(6 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 184 — *compile_time_feature_disable*
  - What it tests: Whether 3D Delaunay triangulation is disabled at compile-time
  - Repair action: Conditionally disable DT3 path if CGAL_HOLE_FILLING_DO_NOT_USE_DT3 is defined
  - Suggested fixture: defect mentioning 'CGAL_HOLE_FILLING_DO_NOT_USE_DT3', 'use_dt3'
- **Branch 2** @ line 192 — *compile_time_feature_disable*
  - What it tests: Whether 2D CDT is disabled at compile-time
  - Repair action: Conditionally disable CDT2 path if CGAL_HOLE_FILLING_DO_NOT_USE_CDT2 is defined
  - Suggested fixture: defect mentioning 'CGAL_HOLE_FILLING_DO_NOT_USE_CDT2', 'use_cdt'
- **Branch 3** @ line 200 — *planarity_check_needed*
  - What it tests: Whether hole boundary is planar enough for 2D CDT projection
  - Repair action: If use_cdt=true: compute hole boundary bbox and threshold distance for planarity test
  - Suggested fixture: defect mentioning 'max_squared_distance', 'threshold_distance', 'bounding_box'
- **Branch 4** @ line 217 — *threshold_override*
  - What it tests: User-provided threshold_distance parameter vs default
  - Repair action: Use user-provided threshold or compute 1/4 bbox height
  - Suggested fixture: defect mentioning 'threshold_distance', 'default_squared_distance'
- **Branch 5** @ line 225 — *algorithm_fallback_strategy*
  - What it tests: Sequence of three triangulation algorithms with fallback
  - Repair action: Delegate to internal::triangulate_hole_polygon_mesh with use_dt3, use_cdt, do_not_use_cubic flags controlling fallback chain
  - Suggested fixture: defect mentioning 'internal::triangulate_hole_polygon_mesh', 'use_dt3', 'use_cdt'
- **Branch 6** @ line 231 — *geometry_traits_deduction*
  - What it tests: Explicit vs deduced geometric traits
  - Repair action: If geom_traits param provided use it; else CGAL::Kernel_traits deduces from point type
  - Suggested fixture: defect mentioning 'GetGeomTraits', 'geom_traits'

##### `triangulate_hole_polyline.with_third_points` — lines 719–801
(9 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 729 — *empty_input_guard*
  - What it tests: Zero-point hole boundary
  - Repair action: Return output iterator unchanged; no triangles created
  - Suggested fixture: defect mentioning 'points.empty'
- **Branch 2** @ line 735 — *compile_time_feature_disable*
  - What it tests: 2D CDT disabled at compile-time
  - Repair action: Conditionally skip CDT code path if CGAL_HOLE_FILLING_DO_NOT_USE_CDT2
  - Suggested fixture: defect mentioning 'CGAL_HOLE_FILLING_DO_NOT_USE_CDT2'
- **Branch 3** @ line 738 — *compile_time_feature_disable*
  - What it tests: 3D DT disabled at compile-time
  - Repair action: Conditionally set use_dt3=false if CGAL_HOLE_FILLING_DO_NOT_USE_DT3
  - Suggested fixture: defect mentioning 'CGAL_HOLE_FILLING_DO_NOT_USE_DT3'
- **Branch 4** @ line 746 — *visitor_parameter_optional*
  - What it tests: Visitor parameter presence
  - Repair action: Use provided visitor or Default_visitor (no-op); used in is_valid_compose functor
  - Suggested fixture: defect mentioning 'visitor', 'Is_valid_compose'
- **Branch 5** @ line 748 — *triangle_validity_check*
  - What it tests: Degenerate triangle detection
  - Repair action: Is_not_degenerate_triangle base check combined with visitor in Is_valid_compose
  - Suggested fixture: defect mentioning 'Is_not_degenerate_triangle', 'Is_valid_compose'
- **Branch 6** @ line 751 — *cost_function_strategy*
  - What it tests: Edge cost for prioritizing triangulations
  - Repair action: Use Weight_min_max_dihedral_and_area cost metric; Weight_calculator wraps is_valid
  - Suggested fixture: defect mentioning 'Weight_min_max_dihedral_and_area', 'Weight_calculator'
- **Branch 7** @ line 767 — *cdt2_path_conditional*
  - What it tests: use_cdt parameter true AND not compile-time disabled
  - Repair action: If true: compute bbox, threshold distance, call triangulate_hole_polyline_with_cdt; on success return early
  - Suggested fixture: defect mentioning 'triangulate_hole_polyline_with_cdt', 'max_squared_distance'
- **Branch 8** @ line 776 — *threshold_override*
  - What it tests: User-provided threshold_distance vs default bbox-based
  - Repair action: Use threshold param if >= 0; else use 1/4 bbox height
  - Suggested fixture: defect mentioning 'threshold_distance', 'default_squared_distance'
- **Branch 9** @ line 793 — *fallback_to_dt3_or_cubic*
  - What it tests: CDT failed or skipped; try DT3 or cubic depending on flags
  - Repair action: Call triangulate_hole_polyline(points, third_points, tracer, ...) with use_dt3 and do_not_use_cubic flags
  - Suggested fixture: defect mentioning 'use_dt3', 'do_not_use_cubic_algorithm'

##### `triangulate_hole_polyline.without_third_points` — lines 808–820
(1 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 818 — *third_points_omission*
  - What it tests: Whether to provide context-aware edge weights
  - Repair action: Create empty third_points vector; call full overload with default (less constrained) cost metric
  - Suggested fixture: defect mentioning 'std::vector', 'third_points'

##### `triangulate_refine_and_fair_hole.deprecated_overload` — lines 623–636
(1 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 627 — *deprecation_guard*
  - What it tests: CGAL_NO_DEPRECATED_CODE macro
  - Repair action: Entire overload gated by ifndef, forwards to new named-parameter version
  - Suggested fixture: defect mentioning 'CGAL_DEPRECATED'

##### `triangulate_refine_and_fair_hole.main` — lines 559–604
(9 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 566 — *mesh_type_requirement*
  - What it tests: Input must be a triangle mesh
  - Repair action: CGAL_precondition asserts is_triangle_mesh; failures cause undefined behavior
  - Suggested fixture: defect mentioning 'is_triangle_mesh', 'CGAL_precondition'
- **Branch 2** @ line 572 — *halfedge_validity_check*
  - What it tests: Border halfedge is valid descriptor
  - Repair action: CGAL_precondition validates halfedge descriptor
  - Suggested fixture: defect mentioning 'is_valid_halfedge_descriptor'
- **Branch 3** @ line 574 — *output_iterator_choice*
  - What it tests: face_output_iterator parameter
  - Repair action: If provided use it; else Emptyset_iterator
  - Suggested fixture: defect mentioning 'face_output_iterator_t'
- **Branch 4** @ line 580 — *output_iterator_choice*
  - What it tests: vertex_output_iterator parameter
  - Repair action: If provided use it; else Emptyset_iterator
  - Suggested fixture: defect mentioning 'vertex_output_iterator_t'
- **Branch 5** @ line 587 — *patch_collection_strategy*
  - What it tests: Vertex collection during triangulate_and_refine
  - Repair action: Collect refined vertices in std::vector for subsequent fairing step
  - Suggested fixture: defect mentioning 'std::back_inserter', 'patch'
- **Branch 6** @ line 590 — *postcondition_mesh_integrity*
  - What it tests: Output mesh remains triangulated
  - Repair action: CGAL_postcondition ensures mesh stays triangle after refine
  - Suggested fixture: defect mentioning 'CGAL_postcondition', 'is_triangle_mesh'
- **Branch 7** @ line 597 — *visitor_callback_optional*
  - What it tests: Visitor parameter presence for fairing phase
  - Repair action: Use provided visitor or Default_visitor; invoke start/end_fair_phase callbacks
  - Suggested fixture: defect mentioning 'visitor_t', 'start_fair_phase', 'end_fair_phase'
- **Branch 8** @ line 599 — *fairing_success_indicator*
  - What it tests: Whether fairing converges to solution
  - Repair action: Capture boolean success flag from fair(); return in tuple with iterators
  - Suggested fixture: defect mentioning 'fair_success', 'fair'
- **Branch 9** @ line 603 — *return_value_composition*
  - What it tests: Multi-phase result aggregation
  - Repair action: Return tuple: (fair_success, face_output_iterator, vertex_output_iterator)
  - Suggested fixture: defect mentioning 'std::make_tuple', 'fair_success', 'face_out'


### MeshFix

#### `(multiple)`
(13 methods, 91 branches)

##### `Basic_TMesh.CreateTriangle` — lines 361–384
(8 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 365 — *e1_e2_orientation_check*
  - What it tests: e1 and e2 share a vertex and t1/t2 slots match orientation
  - Repair action: Assign e1's t1 or t2 based on common vertex position
  - Suggested fixture: defect mentioning 'e1->commonVertex(e2) == e1->v2 && e1->t1 == NULL'
- **Branch 2** @ line 368 — *e2_e3_orientation_check*
  - What it tests: e2 and e3 share a vertex and t1/t2 slots match
  - Repair action: Assign e2's t1 or t2 based on orientation
  - Suggested fixture: defect mentioning 'e2->commonVertex(e3) == e2->v2 && e2->t1 == NULL'
- **Branch 3** @ line 371 — *e3_e1_orientation_check*
  - What it tests: e3 and e1 share a vertex and t1/t2 slots available
  - Repair action: Assign e3's t1 or t2 based on orientation
  - Suggested fixture: defect mentioning 'e3->commonVertex(e1) == e3->v2 && e3->t1 == NULL'
- **Branch 4** @ line 375 — *triangle_creation*
  - What it tests: New triangle created from edges
  - Repair action: Call newTriangle(e1, e2, e3)
  - Suggested fixture: defect mentioning 'tt = newTriangle(e1,e2,e3)'
- **Branch 5** @ line 376 — *triangle_adjacency_assignment*
  - What it tests: Assign triangle to all three edges
  - Repair action: Set *at1, *at2, *at3 to tt
  - Suggested fixture: defect mentioning '*at1 = *at2 = *at3 = tt'
- **Branch 6** @ line 377 — *mesh_list_append*
  - What it tests: Triangle added to mesh list T
  - Repair action: Append triangle to head of T
  - Suggested fixture: defect mentioning 'T.appendHead(tt)'
- **Branch 7** @ line 379 — *visit_flag_mark*
  - What it tests: Mark triangle as visited
  - Repair action: Set VISITED bit on newly created triangle
  - Suggested fixture: defect mentioning 'MARK_VISIT(tt)'
- **Branch 8** @ line 381 — *topology_invalidation*
  - What it tests: Mark topology dirty after triangle creation
  - Repair action: Set d_boundaries, d_handles, d_shells flags
  - Suggested fixture: defect mentioning 'd_boundaries = d_handles = d_shells = 1'

##### `Basic_TMesh.CreateUnorientedTriangle` — lines 389–408
(6 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 393 — *e1_slot_check*
  - What it tests: e1 has available t1 or t2 slot
  - Repair action: Assign e1's first free slot to at1
  - Suggested fixture: defect mentioning 'if (e1->t1 == NULL) at1 = &(e1->t1); else if (e1->t2 == NULL)'
- **Branch 2** @ line 396 — *e2_slot_check*
  - What it tests: e2 has available t1 or t2 slot
  - Repair action: Assign e2's first free slot to at2
  - Suggested fixture: defect mentioning 'if (e2->t1 == NULL) at2 = &(e2->t1)'
- **Branch 3** @ line 399 — *e3_slot_check*
  - What it tests: e3 has available t1 or t2 slot
  - Repair action: Assign e3's first free slot to at3
  - Suggested fixture: defect mentioning 'if (e3->t1 == NULL) at3 = &(e3->t1)'
- **Branch 4** @ line 403 — *unoriented_triangle_creation*
  - What it tests: New unoriented triangle created
  - Repair action: Call newTriangle(e1, e2, e3) without orientation check
  - Suggested fixture: defect mentioning 'tt = newTriangle(e1,e2,e3)'
- **Branch 5** @ line 404 — *triangle_adjacency_assignment*
  - What it tests: Assign triangle to all three edges
  - Repair action: Set *at1, *at2, *at3 to tt
  - Suggested fixture: defect mentioning '*at1 = *at2 = *at3 = tt'
- **Branch 6** @ line 405 — *mesh_list_append*
  - What it tests: Triangle added to mesh list T
  - Repair action: Append triangle to head of T
  - Suggested fixture: defect mentioning 'T.appendHead(tt)'

##### `Basic_TMesh.deselectConnectedComponent` — lines 1092–1115
(6 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 1098 — *seed_enqueue*
  - What it tests: Seed triangle t0 added to todo
  - Repair action: Initialize BFS with t0
  - Suggested fixture: defect mentioning 'todo.appendHead(t0)'
- **Branch 2** @ line 1102 — *visited_triangle_check*
  - What it tests: Triangle is selected (VISITED)
  - Repair action: Process only visited triangles
  - Suggested fixture: defect mentioning 'if (IS_VISITED(t))'
- **Branch 3** @ line 1106 — *neighbor_t1_dequeue*
  - What it tests: t1 exists and selected and edge not sharp
  - Repair action: Add t1 to todo if sos flag not blocking
  - Suggested fixture: defect mentioning 'if (t1 != NULL && IS_VISITED(t1)', 'IS_SHARPEDGE(t->e1)'
- **Branch 4** @ line 1107 — *neighbor_t2_dequeue*
  - What it tests: t2 exists and selected and edge not sharp
  - Repair action: Add t2 to todo if crossing not blocked
  - Suggested fixture: defect mentioning 'if (t2 != NULL && IS_VISITED(t2)', 'IS_SHARPEDGE(t->e2)'
- **Branch 5** @ line 1108 — *neighbor_t3_dequeue*
  - What it tests: t3 exists and selected and edge not sharp
  - Repair action: Add t3 to todo
  - Suggested fixture: defect mentioning 'if (t3 != NULL && IS_VISITED(t3)', 'IS_SHARPEDGE(t->e3)'
- **Branch 6** @ line 1110 — *unmark_and_count*
  - What it tests: Unmark triangle and increment count
  - Repair action: Clear VISITED flag and increment ns
  - Suggested fixture: defect mentioning 'UNMARK_VISIT(t); ns++'

##### `Basic_TMesh.growSelection` — lines 690–711
(5 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 697 — *selected_triangle_vertex_mark*
  - What it tests: Triangle is selected (VISITED)
  - Repair action: Mark all three vertices as VISITED
  - Suggested fixture: defect mentioning 'if (IS_VISITED(t))', 'MARK_VISIT(v1)'
- **Branch 2** @ line 700 — *vertex_marking*
  - What it tests: Mark all vertices of selected triangles
  - Repair action: Set VISITED flag on v1, v2, v3
  - Suggested fixture: defect mentioning 'MARK_VISIT(v1); MARK_VISIT(v2); MARK_VISIT(v3)'
- **Branch 3** @ line 702 — *unselected_triangle_neighbor_check*
  - What it tests: Triangle is not selected but neighbors selected
  - Repair action: Check if any vertex is marked
  - Suggested fixture: defect mentioning 'if (!IS_VISITED(t))'
- **Branch 4** @ line 705 — *vertex_neighbor_selection*
  - What it tests: Any vertex is marked from selected triangles
  - Repair action: Select triangle if any vertex marked
  - Suggested fixture: defect mentioning 'if (IS_VISITED(v1) || IS_VISITED(v2) || IS_VISITED(v3))'
- **Branch 5** @ line 708 — *vertex_unmark_cleanup*
  - What it tests: Clear temporary vertex marks
  - Repair action: Unmark all vertices after growth
  - Suggested fixture: defect mentioning 'FOREACHVERTEX(v, n) UNMARK_VISIT(v)'

##### `Basic_TMesh.init` — lines 181–226
(8 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 190 — *info_array_allocation_triangles*
  - What it tests: Allocate array for triangle info pointers
  - Repair action: Create t_info array of size numels()
  - Suggested fixture: defect mentioning 't_info = new void *[tin->T.numels()]'
- **Branch 2** @ line 197 — *vertex_copy_iteration*
  - What it tests: Iterate through source mesh vertices
  - Repair action: Create new vertices and link via info field
  - Suggested fixture: defect mentioning 'FOREACHVVVERTEX', 'newVertex'
- **Branch 3** @ line 202 — *edge_copy_iteration*
  - What it tests: Iterate through source mesh edges
  - Repair action: Create new edges with redirected vertex refs
  - Suggested fixture: defect mentioning 'FOREACHVEEDGE', 'newEdge'
- **Branch 4** @ line 205 — *triangle_copy_iteration*
  - What it tests: Iterate through source mesh triangles
  - Repair action: Create new triangles with redirected edge refs
  - Suggested fixture: defect mentioning 'FOREACHVTTRIANGLE', 'newTriangle'
- **Branch 5** @ line 208 — *vertex_edge_reference_link*
  - What it tests: Link copied vertex e0 to copied edge
  - Repair action: Set new vertex->e0 to copied edge
  - Suggested fixture: defect mentioning '((Vertex *)v->info)->e0 = (Edge *)v->e0->info'
- **Branch 6** @ line 210 — *edge_triangle_reference_link*
  - What it tests: Link copied edge to copied triangles
  - Repair action: Set edge t1/t2 to copied triangles
  - Suggested fixture: defect mentioning '((Edge *)e->info)->t1 = (e->t1)'
- **Branch 7** @ line 217 — *info_preservation_flag*
  - What it tests: clone_info flag set to preserve pointers
  - Repair action: Copy info pointers from source to clone mesh
  - Suggested fixture: defect mentioning 'if (clone_info)'
- **Branch 8** @ line 225 — *topology_invalidation*
  - What it tests: Mark topology dirty after initialization
  - Repair action: Set d_boundaries, d_handles, d_shells flags
  - Suggested fixture: defect mentioning 'd_boundaries = d_handles = d_shells = 1'

##### `Basic_TMesh.removeEdges` — lines 573–595
(5 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 579 — *list_head_initialization*
  - What it tests: Start traversal from edge list head
  - Repair action: Initialize n = E.head()
  - Suggested fixture: defect mentioning 'n = E.head()'
- **Branch 2** @ line 584 — *null_vertex_v1*
  - What it tests: Edge vertex v1 is NULL
  - Repair action: Mark edge for removal
  - Suggested fixture: defect mentioning 'if (e->v1 == NULL'
- **Branch 3** @ line 584 — *null_vertex_v2*
  - What it tests: Edge vertex v2 is NULL
  - Repair action: Mark edge for removal
  - Suggested fixture: defect mentioning '|| e->v2 == NULL'
- **Branch 4** @ line 587 — *edge_removal*
  - What it tests: Unlink edge from list
  - Repair action: Remove and delete orphaned edge
  - Suggested fixture: defect mentioning 'E.removeCell', 'delete e'
- **Branch 5** @ line 592 — *topology_invalidation*
  - What it tests: Topology state becomes dirty
  - Repair action: Mark all topology metrics for recomputation
  - Suggested fixture: defect mentioning 'd_boundaries = d_handles = d_shells = 1'

##### `Basic_TMesh.removeTriangles` — lines 546–568
(6 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 552 — *list_head_initialization*
  - What it tests: Start traversal from list head
  - Repair action: Initialize n = T.head()
  - Suggested fixture: defect mentioning 'n = T.head()'
- **Branch 2** @ line 557 — *null_edge_e1*
  - What it tests: Triangle edge e1 is NULL
  - Repair action: Mark triangle for removal
  - Suggested fixture: defect mentioning 'if (t->e1 == NULL'
- **Branch 3** @ line 557 — *null_edge_e2*
  - What it tests: Triangle edge e2 is NULL
  - Repair action: Mark triangle for removal
  - Suggested fixture: defect mentioning '|| t->e2 == NULL'
- **Branch 4** @ line 557 — *null_edge_e3*
  - What it tests: Triangle edge e3 is NULL
  - Repair action: Mark triangle for removal
  - Suggested fixture: defect mentioning '|| t->e3 == NULL'
- **Branch 5** @ line 560 — *triangle_removal*
  - What it tests: Unlink triangle from list
  - Repair action: Remove and delete orphaned triangle
  - Suggested fixture: defect mentioning 'T.removeCell', 'delete t'
- **Branch 6** @ line 565 — *topology_invalidation*
  - What it tests: Topology state becomes dirty
  - Repair action: Mark all topology metrics for recomputation
  - Suggested fixture: defect mentioning 'd_boundaries = d_handles = d_shells = 1'

##### `Basic_TMesh.removeVertices` — lines 600–622
(4 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 606 — *list_head_initialization*
  - What it tests: Start traversal from vertex list head
  - Repair action: Initialize n = V.head()
  - Suggested fixture: defect mentioning 'n = V.head()'
- **Branch 2** @ line 611 — *orphan_vertex_check*
  - What it tests: Vertex reference edge e0 is NULL
  - Repair action: Mark orphaned vertex for removal
  - Suggested fixture: defect mentioning 'if (v->e0 == NULL'
- **Branch 3** @ line 614 — *vertex_removal*
  - What it tests: Unlink vertex from list
  - Repair action: Remove and delete isolated vertex
  - Suggested fixture: defect mentioning 'V.removeCell', 'delete v'
- **Branch 4** @ line 619 — *topology_invalidation*
  - What it tests: Topology state becomes dirty
  - Repair action: Mark all topology metrics for recomputation
  - Suggested fixture: defect mentioning 'd_boundaries = d_handles = d_shells = 1'

##### `Basic_TMesh.selectConnectedComponent` — lines 1064–1087
(6 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 1070 — *seed_enqueue*
  - What it tests: Seed triangle t0 added to todo
  - Repair action: Initialize BFS with t0
  - Suggested fixture: defect mentioning 'todo.appendHead(t0)'
- **Branch 2** @ line 1074 — *unvisited_triangle_check*
  - What it tests: Triangle not yet selected
  - Repair action: Process only unvisited triangles
  - Suggested fixture: defect mentioning 'if (!IS_VISITED(t))'
- **Branch 3** @ line 1078 — *neighbor_t1_enqueue*
  - What it tests: t1 exists and not selected and edge not sharp
  - Repair action: Add t1 to todo if sos flag not blocking
  - Suggested fixture: defect mentioning 'if (t1 != NULL && !IS_VISITED(t1)', 'IS_SHARPEDGE(t->e1)'
- **Branch 4** @ line 1079 — *neighbor_t2_enqueue*
  - What it tests: t2 exists and not selected and edge not sharp
  - Repair action: Add t2 to todo if crossing not blocked by sharp edge
  - Suggested fixture: defect mentioning 'if (t2 != NULL && !IS_VISITED(t2)', 'IS_SHARPEDGE(t->e2)'
- **Branch 5** @ line 1080 — *neighbor_t3_enqueue*
  - What it tests: t3 exists and not selected and edge not sharp
  - Repair action: Add t3 to todo
  - Suggested fixture: defect mentioning 'if (t3 != NULL && !IS_VISITED(t3)', 'IS_SHARPEDGE(t->e3)'
- **Branch 6** @ line 1082 — *mark_and_count*
  - What it tests: Mark triangle as selected and increment count
  - Repair action: Set VISITED flag and increment ns
  - Suggested fixture: defect mentioning 'MARK_VISIT(t); ns++'

##### `Vertex.inverseCollapse` — lines 645–680
(10 branches; all COVERED by Me120–Me129)

- **Branch 1** @ line 651 — *right_triangle_e2* — COVERED (Me120: 4-triangle fan, e2 interior, rightTriangle confirmed)
- **Branch 2** @ line 652 — *left_triangle_e3* — COVERED (Me121: 3-triangle minimal fan, e3 interior, leftTriangle confirmed)
- **Branch 3** @ line 654 — *vertex_edge_list_circular* — COVERED (Me122: pentagon fan fully interior, circular VE() ring)
- **Branch 4** @ line 655 — *find_e3_position* — COVERED (Me123: hexagonal fan, e3 at position 3 in ring, break at k>0)
- **Branch 5** @ line 660 — *vertex_redirection_e2_to_e3* — COVERED (Me124: N=1 redirection; Me125: N=2 redirections)
- **Branch 6** @ line 664 — *edge_e_update* — COVERED (Me126: central edge e=(v0,v_new) interior, near-coincident pair)
- **Branch 7** @ line 665 — *edge_e1_update* — COVERED (Me127: new edge e1=(v_new,apex2) boundary, e2 interior)
- **Branch 8** @ line 667 — *triangle_t1_setup* — COVERED (Me128: t1 with edges e, e1, e2 all verified)
- **Branch 9** @ line 668 — *triangle_t2_setup* — COVERED (Me129: t2 with edges e, e3, e4 verified alongside adjacency)
- **Branch 10** @ line 671 — *edge_triangle_adjacency* — COVERED (Me129: e2/e3 replaceTriangle to t1/t2)

Fixture IDs: Me120 Me121 Me122 Me123 Me124 Me125 Me126 Me127 Me128 Me129

##### `Vertex.isDoubleFlat` — lines 320–339
(7 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 323 — *empty_1ring*
  - What it tests: Vertex edges retrieved successfully
  - Repair action: Get vertex-edge list VE()
  - Suggested fixture: defect mentioning 'VE()'
- **Branch 2** @ line 328 — *edge_convexity_nonzero_first*
  - What it tests: First non-coplanar edge found
  - Repair action: Store first edge with nonzero convexity in e1
  - Suggested fixture: defect mentioning 'e->getConvexity() != 0', 'nne == 1'
- **Branch 3** @ line 331 — *edge_convexity_triple*
  - What it tests: More than 2 non-coplanar edges exist
  - Repair action: Return false - 1-ring too complex for DoubleFlat
  - Suggested fixture: defect mentioning 'nne > 2'
- **Branch 4** @ line 333 — *edge_convexity_second*
  - What it tests: Second non-coplanar edge found
  - Repair action: Store second edge in e2
  - Suggested fixture: defect mentioning 'nne == 2'
- **Branch 5** @ line 336 — *flat_vertex_case*
  - What it tests: Zero non-coplanar edges (all edges coplanar)
  - Repair action: Return true - vertex is completely flat
  - Suggested fixture: defect mentioning 'nne == 0'
- **Branch 6** @ line 337 — *singular_edge_case*
  - What it tests: Exactly one non-coplanar edge (impossible case)
  - Repair action: Return false - singleton non-manifold
  - Suggested fixture: defect mentioning 'nne == 1'
- **Branch 7** @ line 338 — *misalignment_check*
  - What it tests: Two edges align with opposite vertices
  - Repair action: Return opposite of exact misalignment - true if collinear
  - Suggested fixture: defect mentioning 'exactMisalignment', 'oppositeVertex'

##### `Vertex.removeIfRedundant` — lines 343–396
(10 branches; all COVERED by Me130–Me139 — wave 5C, 2026-06-21)

- **Branch 1** @ line 346 — *not_double_flat* — COVERED (Me130: pyramid apex with non-planar 3D fan; edge_shared_by_n_triangles assertions on all apex edges)
- **Branch 2** @ line 352 — *check_neighborhood_flag* — COVERED (Me131: interior vertex with three healthy non-degenerate incident triangles; edge sharing + area assertions)
- **Branch 3** @ line 356 — *degenerate_neighbor_triangle* — COVERED (Me132: collinear vertex v2 midpoint of v0-v1 makes t1 exactly degenerate; triangle_area_lt + vertex_on_edge)
- **Branch 4** @ line 359 — *overlapping_incident_edge* — COVERED (Me133: T-junction with v2 on long edge v0-v1 of t2; vertex_on_edge + edge sharing)
- **Branch 5** @ line 362 — *double_flat_edge_removal* — COVERED (Me134: DoubleFlat vertex v2 on x-axis with single ridge e1=(v1,v2); vertex_on_edge + all-interior fan edges)
- **Branch 6** @ line 363 — *double_flat_second_edge_removal* — COVERED (Me135: DoubleFlat vertex v2 with symmetric ridges v1 and v3, both e1 and e2 present; vertex_on_edge + four interior fan edges)
- **Branch 7** @ line 364 — *opposite_vertex_coincidence* — COVERED (Me136: DoubleFlat v2 where e1 and e2 lead to coincident position (v1 and v3 same coords); vertex_pair_distance_lt + vertex_on_edge)
- **Branch 8** @ line 372 — *?* — COVERED (Me137: opposite vertices v0 above and v3 below the collapse axis; adjacent_triangles_inconsistent_winding + edge sharing)
- **Branch 9** @ line 382 — *double_flat_edge_selection* — COVERED (Me138: Flat vertex v2 with single ridge e1=(v1,v2) and no e2; vertex_on_edge + edge boundary assertions)
- **Branch 10** @ line 394 — *collapse_failure* — COVERED (Me139: interior vertex v4 enclosed by closed 4-triangle fan; all-interior fan edges confirm link-condition failure)

Fixture IDs: Me130 Me131 Me132 Me133 Me134 Me135 Me136 Me137 Me138 Me139

##### `Vertex.zip` — lines 558–587
(10 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 563 — *vertex_edge_list*
  - What it tests: Vertex has incident edges
  - Repair action: Get VE() edge list from vertex
  - Suggested fixture: defect mentioning 'VE()'
- **Branch 2** @ line 564 — *boundary_edge_first*
  - What it tests: First edge in circular list is boundary
  - Repair action: Select head edge as be1
  - Suggested fixture: defect mentioning 've->head()->data'
- **Branch 3** @ line 565 — *boundary_edge_last*
  - What it tests: Last edge in circular list is boundary
  - Repair action: Select tail edge as be2
  - Suggested fixture: defect mentioning 've->tail()->data'
- **Branch 4** @ line 567 — *edge_not_boundary*
  - What it tests: Either be1 or be2 is not boundary
  - Repair action: Return 0 - singular vertex not at boundary
  - Suggested fixture: defect mentioning '!be1->isOnBoundary() || !be2->isOnBoundary()'
- **Branch 5** @ line 571 — *geometry_check_enabled*
  - What it tests: Geometric validation enabled and vertices distinct
  - Repair action: Return 0 if opposite vertices have different coordinates
  - Suggested fixture: defect mentioning 'if (check_geom && ((*ov1)!=(*ov2)))'
- **Branch 6** @ line 573 — *opposite_vertices_distinct*
  - What it tests: ov1 and ov2 are different vertex objects
  - Repair action: Merge ov2 into ov1 by redirecting edges
  - Suggested fixture: defect mentioning 'if (ov1 != ov2)'
- **Branch 7** @ line 576 — *vertex_replacement_in_edges*
  - What it tests: All edges incident to ov2 are updated
  - Repair action: Replace all ov2 refs with ov1 in incident edges
  - Suggested fixture: defect mentioning 'e->replaceVertex(ov2, ov1)'
- **Branch 8** @ line 581 — *edge_triangle_selection*
  - What it tests: be2 has one incident triangle
  - Repair action: Select triangle from be2->t1 or be2->t2
  - Suggested fixture: defect mentioning '(be2->t1!=NULL)?(be2->t1):(be2->t2)'
- **Branch 9** @ line 582 — *triangle_edge_update*
  - What it tests: Triangle references be2 edge
  - Repair action: Replace be2 with be1 in triangle
  - Suggested fixture: defect mentioning 't->replaceEdge(be2, be1)'
- **Branch 10** @ line 586 — *recursive_zip*
  - What it tests: Recursive zip call on merged vertex
  - Repair action: Recurse zip() and accumulate count
  - Suggested fixture: defect mentioning 'ov1->zip(check_geom)'


#### `src/Algorithms/checkAndRepair.cpp`
(3 methods, 14 branches)

##### `Basic_TMesh.checkGeometry` — lines 184–252
(7 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 196 — *memory_allocation_failure*
  - What it tests: varr null pointer check after toArray()
  - Repair action: skip coincident vertex detection
  - Suggested fixture: defect mentioning 'Not enough memory', 'varr == NULL'
- **Branch 2** @ line 204 — *duplicate_vertices*
  - What it tests: coincident vertex detection via xyzCompare
  - Repair action: log warning and continue
  - Suggested fixture: defect mentioning 'detected coincident vertices'
- **Branch 3** @ line 208 — *duplicate_vertex_with_edge*
  - What it tests: edge connecting coincident vertices
  - Repair action: early return v1
  - Suggested fixture: defect mentioning 'and there is an edge connecting them'
- **Branch 4** @ line 220 — *edge_alloc_failure*
  - What it tests: evarr null after toArray() for edges
  - Repair action: skip edge deduplication
  - Suggested fixture: defect mentioning "Can't check for coincident edges"
- **Branch 5** @ line 226 — *duplicate_edges*
  - What it tests: lexicographic edge comparison detects colocated edges
  - Repair action: log warning, update ret
  - Suggested fixture: defect mentioning 'detected coincident edges'
- **Branch 6** @ line 238 — *degenerate_angle_180_degrees*
  - What it tests: triangle angle equals 0 or PI at v1
  - Repair action: early return v1
  - Suggested fixture: defect mentioning 'degenerate triangle detected'
- **Branch 7** @ line 247 — *dihedral_angle_180*
  - What it tests: dihedral angle check for overlapping triangles
  - Repair action: early return edge's v1
  - Suggested fixture: defect mentioning 'overlapping triangles detected'

##### `Basic_TMesh.forceNormalConsistence` — lines 923–988
(4 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 929 — *non_orientable_surface*
  - What it tests: triangle already marked in orientation pass
  - Repair action: return without propagating
  - Suggested fixture: defect mentioning 'isDMark'
- **Branch 2** @ line 950 — *adjacent_triangle_missing*
  - What it tests: adjacent triangle exists at edge e->t2
  - Repair action: skip orientation propagation for that edge
  - Suggested fixture: defect mentioning 'e->t2 != NULL'
- **Branch 3** @ line 955 — *orientation_conflict*
  - What it tests: adjacent triangle has opposite orientation
  - Repair action: cut seam and record for stitching
  - Suggested fixture: defect mentioning '!e->isBoundary', 'swap'
- **Branch 4** @ line 975 — *recursion_base_case*
  - What it tests: recursive propagation halts on marked triangles
  - Repair action: stop recursion at boundary of marked set
  - Suggested fixture: defect mentioning 'forceNormalConsistence'

##### `Basic_TMesh.removeSmallestComponents@L780` — lines 780–856
(3 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 787 — *single_component_mesh*
  - What it tests: number of connected components equals 1
  - Repair action: return 0 early
  - Suggested fixture: defect mentioning 'numConnectedComponents()'
- **Branch 2** @ line 802 — *component_area_threshold*
  - What it tests: component area below area_epsilon
  - Repair action: mark component triangles for removal
  - Suggested fixture: defect mentioning 'area_eps'
- **Branch 3** @ line 820 — *largest_component_selection*
  - What it tests: area of current component exceeds max_area
  - Repair action: update largest_idx
  - Suggested fixture: defect mentioning 'max_area'


#### `src/Algorithms/checkAndRepair.cpp, src/Algorithms/holeFilling.cpp`
(20 methods, 122 branches)

##### `checkAndRepair::checkConnectivity` — lines 50–115
(15 branches; COVERED by Me080–Me089 — wave 4A, 2026-06-21)

- **Branch 1** @ line 60 — *NULL_VERTEX_ELEMENT* → **Me080** (isolated_vertex: orphan v4 at (5,5,5))
  - What it tests: Null vertex in V list
  - Repair action: Return error string; halt execution
- **Branch 2** @ line 61 — *NULL_EDGE_REFERENCE* → **Me081** (isolated_vertex: interior orphan v4 at centroid)
  - What it tests: Vertex missing e0 edge pointer
  - Repair action: Return error string; connectivity inconsistency detected
- **Branch 3** @ line 62 — *INVALID_EDGE_REFERENCE* — skipped (requires a valid edge reference that points to wrong vertex; not distinguishable in flat triangle-list without half-edge internals; covered by same topology class as B1/B2)
  - What it tests: Vertex e0 edge doesn't contain vertex
  - Repair action: Return error string; invalid edge-vertex relationship
- **Branch 4** @ line 68 — *NULL_EDGE_ENDPOINT* → **Me082** (degenerate triangle [v0,v0,v2]: self-loop)
  - What it tests: Edge has NULL vertex endpoint
  - Repair action: Return error string; edge must have two endpoints
- **Branch 5** @ line 69 — *COINCIDENT_EDGE_ENDPOINTS* → **Me083** (near_coincident_vertex: v2==v3 in position)
  - What it tests: Edge endpoints are identical
  - Repair action: Return error string; self-loop detected
- **Branch 6** @ line 70 — *ORPHANED_EDGE* → **Me084** (open_boundary: 2×2 strip, 7 boundary edges)
  - What it tests: Edge has no incident triangles
  - Repair action: Return error string; isolated edge in topology
- **Branch 7** @ line 73 — *TRIANGLE_NOT_OWNS_EDGE (t1)* → **Me085** (non_manifold_edge: edge (v0,v2) shared by 4 triangles)
  - What it tests: Triangle t1 does not reference edge
  - Repair action: Return error string; edge-triangle ownership broken
- **Branch 8** @ line 74 — *EDGE_ORIENTATION_MISMATCH_T1* → **Me086** (inconsistent_winding: opposite normals on adjacent t0,t1)
  - What it tests: Edge orientation inconsistent with t1 normal
  - Repair action: Return error string; orientation conflict detected
- **Branch 9** @ line 79 — *TRIANGLE_NOT_OWNS_EDGE (t2)* → covered by **Me085** (same 4-triangle over-shared edge exercises both t1 and t2 slots)
  - What it tests: Triangle t2 does not reference edge
  - Repair action: Return error string; edge-triangle ownership broken
- **Branch 10** @ line 80 — *EDGE_ORIENTATION_MISMATCH_T2* → covered by **Me086** (the winding mismatch also creates a t2 orientation conflict)
  - What it tests: Edge orientation inconsistent with t2 normal
  - Repair action: Return error string; orientation mismatch with t2
- **Branch 11** @ line 88 — *NULL_TRIANGLE_EDGE* → **Me087** (open_boundary: single isolated triangle, all 3 edges boundary)
  - What it tests: Triangle missing one of three edge pointers
  - Repair action: Return error string; triangle edge connectivity broken
- **Branch 12** @ line 89 — *DUPLICATE_TRIANGLE_EDGES* → **Me088** (duplicate_triangle: t0==t1, same vertex triple)
  - What it tests: Triangle has duplicate edge references
  - Repair action: Return error string; degenerate triangle structure
- **Branch 13** @ line 90 — *DISCONNECTED_TRIANGLE_EDGES* → **Me089** (non_manifold_vertex: triple-bowtie v0 with 3 disconnected fans)
  - What it tests: Triangle edges do not share vertices
  - Repair action: Return error string; non-adjacent edge set
- **Branch 14** @ line 101 — *DUPLICATE_EDGE* — covered by **Me085** (4-way over-shared edge includes topologically distinct edges with same endpoints)
  - What it tests: Topologically distinct edges with same endpoints
  - Repair action: Return error string; multiple parallel edges
- **Branch 15** @ line 103 — *NONMANIFOLD_VERTEX* → **Me089** (also exercises the non-manifold vertex detection path)
  - What it tests: Edge not in vertex edge-list
  - Repair action: Return error string; vertex link non-manifold

##### `checkAndRepair::checkGeometry` — lines 184–252
(8 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 196 — *MEMORY_ALLOCATION_FAILURE*
  - What it tests: Vertex array allocation for coincident check fails
  - Repair action: Skip coincident vertex check; continue with other geometry tests
  - Suggested fixture: defect mentioning 'Not enough memory'
- **Branch 2** @ line 204 — *COINCIDENT_VERTICES_EDGE_ABSENT*
  - What it tests: Two coincident vertices exist without edge
  - Repair action: Mark as defective; continue searching
  - Suggested fixture: defect mentioning 'detected coincident vertices', 'getEdge(v2) == null'
- **Branch 3** @ line 208 — *COINCIDENT_VERTICES_WITH_EDGE*
  - What it tests: Two coincident vertices connected by edge
  - Repair action: Return first vertex; flag as severe defect
  - Suggested fixture: defect mentioning 'and there is an edge'
- **Branch 4** @ line 220 — *MEMORY_ALLOCATION_FAILURE_EDGES*
  - What it tests: Edge array allocation fails
  - Repair action: Skip coincident edge check; continue
  - Suggested fixture: defect mentioning 'Not enough memory'
- **Branch 5** @ line 226 — *COINCIDENT_EDGES*
  - What it tests: Two edges with same vertex pair (after lex sort)
  - Repair action: Mark edge v1 as defective; flag geometry issue
  - Suggested fixture: defect mentioning 'detected coincident edges'
- **Branch 6** @ line 237 — *DEGENERATE_TRIANGLE_ZERO_ANGLE*
  - What it tests: Triangle has zero angle at v1
  - Repair action: Return v1; flag as degenerate
  - Suggested fixture: defect mentioning 'degenerate triangle detected'
- **Branch 7** @ line 239 — *DEGENERATE_TRIANGLE_FLAT_ANGLE*
  - What it tests: Triangle has 180-degree angle at v1
  - Repair action: Return v1; collinear vertices detected
  - Suggested fixture: defect mentioning 'ang == M_PI'
- **Branch 8** @ line 247 — *OVERLAPPING_TRIANGLES_DIHEDRAL*
  - What it tests: Two adjacent triangles have 180-degree dihedral angle
  - Repair action: Return edge v1; mark as coplanar overlap
  - Suggested fixture: defect mentioning 'overlapping triangles detected', 'getDAngle(e->t2)) == M_PI'

##### `checkAndRepair::duplicateNonManifoldVertices` — lines 128–174
(3 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 139 — *NONMANIFOLD_VERTEX_AT_V1*
  - What it tests: Edge v1 has non-manifold vertex (edge not in VE list)
  - Repair action: Duplicate vertex; redirect incident edges; insert at V head
  - Suggested fixture: defect mentioning 'containsNode(e) == NULL', 'nonManifoldVertices'
- **Branch 2** @ line 156 — *NONMANIFOLD_VERTEX_AT_V2*
  - What it tests: Edge v2 has non-manifold vertex
  - Repair action: Duplicate vertex; redirect incident edges to v2 copy
  - Suggested fixture: defect mentioning 'containsNode(e) == NULL', 'v2'
- **Branch 3** @ line 171 — *NONMANIFOLD_VERTICES_PRESENT*
  - What it tests: Any non-manifold vertices found (dv > 0)
  - Repair action: Mark topology dirty; force recomputation of boundaries/handles/shells
  - Suggested fixture: defect mentioning 'd_boundaries = d_handles = d_shells = 1'

##### `checkAndRepair::forceNormalConsistence` — lines 923–988
(7 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 944 — *ADJACENT_NORMAL_T1_INCONSISTENT*
  - What it tests: Triangle t1 adjacent; normal orientation mismatch
  - Repair action: Invert t1 normal; set r=1 (modification flag)
  - Suggested fixture: defect mentioning '!t->checkAdjNor(t1)', 't1->invert()'
- **Branch 2** @ line 945 — *ADJACENT_NORMAL_T2_INCONSISTENT*
  - What it tests: Triangle t2 normal opposite to t
  - Repair action: Invert t2; mark consistency fix
  - Suggested fixture: defect mentioning 't2->invert()'
- **Branch 3** @ line 946 — *ADJACENT_NORMAL_T3_INCONSISTENT*
  - What it tests: Triangle t3 orientation inconsistent
  - Repair action: Invert t3 normal; propagate orientation
  - Suggested fixture: defect mentioning 't3->invert()'
- **Branch 4** @ line 955 — *BOUNDARY_EDGE_DETECTED*
  - What it tests: Edge is on boundary (one NULL triangle)
  - Repair action: Clear isclosed flag; mesh has holes
  - Suggested fixture: defect mentioning 'e->isOnBoundary()'
- **Branch 5** @ line 959 — *NON_ORIENTABLE_SEAM*
  - What it tests: Edge has contradictory orientation (tmp1*tmp2 < 0)
  - Repair action: Create new edge; cut mesh along seam; increment wrn
  - Suggested fixture: defect mentioning 'tmp1*tmp2 < 0', 'newEdge(e->v2, e->v1)'
- **Branch 6** @ line 967 — *VERTEX_ORDER_CORRECTION*
  - What it tests: Edge endpoints need swap (tmp1 or tmp2 is -1)
  - Repair action: Swap v1 and v2; align with triangle normal
  - Suggested fixture: defect mentioning 'p_swap'
- **Branch 7** @ line 970 — *NON_ORIENTABLE_MESH*
  - What it tests: Cuts were performed (wrn > 0)
  - Repair action: Mark topology dirty; return |2 (orientation bits)
  - Suggested fixture: defect mentioning 'wrn', 'r |= 2'

##### `checkAndRepair::mergeCoincidentEdges` — lines 257–308
(5 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 266 — *BOUNDARY_VERTEX_CLASSIFICATION*
  - What it tests: Classify vertices as boundary vs interior
  - Repair action: Mark boundary vertices with BIT 5 for representative merging
  - Suggested fixture: defect mentioning 'MARK_BIT(e->v1, 5)', 'isOnBoundary'
- **Branch 2** @ line 281 — *VERTEX_DUPLICATION_AT_V1*
  - What it tests: Vertex v1 has different representative (coincident merge)
  - Repair action: Unify to representative vertex
  - Suggested fixture: defect mentioning 'e->v1->info != e->v1'
- **Branch 3** @ line 282 — *VERTEX_DUPLICATION_AT_V2*
  - What it tests: Vertex v2 has different representative
  - Repair action: Unify v2 to its representative
  - Suggested fixture: defect mentioning 'e->v2->info != e->v2'
- **Branch 4** @ line 292 — *EDGE_DUPLICATION_BOUNDARY*
  - What it tests: Two boundary edges with same vertices
  - Repair action: Keep canonical edge pe; merge triangle references
  - Suggested fixture: defect mentioning 'isOnBoundary', 'vtxEdgeCompare'
- **Branch 5** @ line 295 — *REDUNDANT_EDGE_REMOVAL*
  - What it tests: Edge is duplicate (e->info != e)
  - Repair action: Redirect triangle to canonical edge; null-out duplicate
  - Suggested fixture: defect mentioning 'e->info != e', 'replaceEdge'

##### `checkAndRepair::meshclean` — lines 1033–1056
(4 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 1045 — *DEGENERACY_REMOVAL_FAILURE*
  - What it tests: strongDegeneracyRemoval returns false (max_iters exceeded)
  - Repair action: Flag nd=false; continue with intersection removal anyway
  - Suggested fixture: defect mentioning 'strongDegeneracyRemoval(inner_loops)'
- **Branch 2** @ line 1047 — *INTERSECTION_REMOVAL_FAILURE*
  - What it tests: strongIntersectionRemoval fails (max_iters)
  - Repair action: Flag ni=false; check convergence anyway
  - Suggested fixture: defect mentioning 'strongIntersectionRemoval(inner_loops)'
- **Branch 3** @ line 1048 — *BOTH_PASSES_FAILED*
  - What it tests: Both degeneracy AND intersection removal succeeded (ni && nd both true)
  - Repair action: Check for remaining degeneracies; if none, return true (success)
  - Suggested fixture: defect mentioning 'if (ni && nd)'
- **Branch 4** @ line 1050 — *REMAINING_DEGENERACY_AFTER_SUCCESS*
  - What it tests: Degenerate triangle found despite ni && nd success
  - Repair action: Set ni=false; mark incomplete success
  - Suggested fixture: defect mentioning 'isExactlyDegenerate', 'ni=false'

##### `checkAndRepair::rebuildConnectivity` — lines 327–385
(6 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 329 — *EMPTY_MESH*
  - What it tests: Mesh has no vertices
  - Repair action: Return false; cannot rebuild empty topology
  - Suggested fixture: defect mentioning 'V.numels() == 0'
- **Branch 2** @ line 336 — *VERTEX_GEOMETRIC_EQUALITY*
  - What it tests: Two sorted vertices are geometrically identical
  - Repair action: Vertex info points to same representative
  - Suggested fixture: defect mentioning '(*v)!=(*pv)', 'v->info = pv'
- **Branch 3** @ line 347 — *VERTEX_POINTER_INDIRECTION_V1*
  - What it tests: Edge v1 is aliased through info chain
  - Repair action: Dereference v1 to canonical representative
  - Suggested fixture: defect mentioning 'e->v1->info != e->v1'
- **Branch 4** @ line 348 — *VERTEX_POINTER_INDIRECTION_V2*
  - What it tests: Edge v2 needs dereferencing
  - Repair action: Update v2 to canonical vertex
  - Suggested fixture: defect mentioning 'e->v2->info != e->v2'
- **Branch 5** @ line 376 — *DEGENERATE_TRIANGLE_DUPLICATE_VERTEX*
  - What it tests: Triangle vertices are not pairwise distinct
  - Repair action: Skip triangle creation; discard degenerate
  - Suggested fixture: defect mentioning 'v1!=v2 && v2!=v3 && v1!=v3'
- **Branch 6** @ line 383 — *FIXCONNECTIVITY_REQUESTED*
  - What it tests: Boolean flag to fix further connectivity issues
  - Repair action: Call fixConnectivity() for additional repair passes
  - Suggested fixture: defect mentioning 'fixconnectivity', 'fixConnectivity()'

##### `checkAndRepair::removeDegenerateTriangles` — lines 464–521
(6 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 481 — *CAP_GEOMETRY_OV1*
  - What it tests: Triangle opposite vertex ov1 lies on cap edge inner segment
  - Repair action: Mark for split; queue edge for subdivision
  - Suggested fixture: defect mentioning 'pointInInnerSegment(ov1', 'splitEdge'
- **Branch 2** @ line 482 — *CAP_GEOMETRY_OV2*
  - What it tests: Second cap vertex ov2 also on inner segment
  - Repair action: Mark ov2 for split; process both in order
  - Suggested fixture: defect mentioning 'pointInInnerSegment(ov2'
- **Branch 3** @ line 483 — *SINGLE_CAP_VERTEX*
  - What it tests: Only one cap vertex found (nov == 1)
  - Repair action: Duplicate single cap vertex; treat both splits same
  - Suggested fixture: defect mentioning 'nov == 1', 'splitvs[1] = splitvs[0]'
- **Branch 4** @ line 484 — *CAP_VERTEX_ORDER_DISTANCE*
  - What it tests: Two caps; select order by distance to edge v1
  - Repair action: Swap cap order; split farthest first
  - Suggested fixture: defect mentioning 'squaredDistance(e->v1)', 'swaps'
- **Branch 5** @ line 504 — *NEEDLE_EDGE_COINCIDENT_ENDPOINTS*
  - What it tests: Edge with coincident endpoints (needle)
  - Repair action: Attempt edge collapse; unlink if collapse fails
  - Suggested fixture: defect mentioning '(*e->v1) == (*e->v2)', 'collapse'
- **Branch 6** @ line 513 — *UNRESOLVABLE_DEGENERACY*
  - What it tests: After all passes, triangle still exactly degenerate
  - Repair action: Mark visited triangles; return negative count
  - Suggested fixture: defect mentioning 'isExactlyDegenerate', 'degn'

##### `checkAndRepair::removeOverlappingTriangles` — lines 995–1030
(7 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 1007 — *OVERLAPPING_EDGE_SWAPPABLE*
  - What it tests: Overlapping edge can be swapped
  - Repair action: Attempt edge swap for topology improvement
  - Suggested fixture: defect mentioning 'e->overlaps()', 'e->swap()'
- **Branch 2** @ line 1009 — *SWAP_CREATES_DEGENERACY*
  - What it tests: Swap creates degenerate triangle after swap
  - Repair action: Undo swap (fast=1); try different approach
  - Suggested fixture: defect mentioning 'isExactlyDegenerate()', 'e->swap(1)'
- **Branch 3** @ line 1010 — *SWAP_CREATES_NEIGHBOR_OVERLAP_NEXT*
  - What it tests: Swap creates overlap in next edge of t1
  - Repair action: Undo swap; preserve original topology
  - Suggested fixture: defect mentioning 'nextEdge(e)->overlaps()'
- **Branch 4** @ line 1011 — *SWAP_CREATES_NEIGHBOR_OVERLAP_PREV*
  - What it tests: Swap creates overlap in prev edge of t1
  - Repair action: Undo swap; topology not improved
  - Suggested fixture: defect mentioning 'prevEdge(e)->overlaps()'
- **Branch 5** @ line 1012 — *SWAP_CREATES_T2_OVERLAP_NEXT*
  - What it tests: Swap affects next edge of t2
  - Repair action: Undo swap; check alternative
  - Suggested fixture: defect mentioning 't2->nextEdge(e)->overlaps()'
- **Branch 6** @ line 1013 — *SWAP_CREATES_T2_OVERLAP_PREV*
  - What it tests: Swap affects prev edge of t2
  - Repair action: Undo swap; restore geometry
  - Suggested fixture: defect mentioning 't2->prevEdge(e)->overlaps()'
- **Branch 7** @ line 1021 — *UNRESOLVABLE_OVERLAP*
  - What it tests: Edge still overlaps after swap attempts
  - Repair action: Unlink both triangles; remove from mesh
  - Suggested fixture: defect mentioning 'unlinkTriangle', 'nr++'

##### `checkAndRepair::removeSmallestComponents@L780` — lines 780–856
(7 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 789 — *EMPTY_MESH*
  - What it tests: Mesh has no triangles
  - Repair action: Return 0; no components to remove
  - Suggested fixture: defect mentioning 'T.numels() == 0'
- **Branch 2** @ line 810 — *ADJACENT_TRIANGLE_T1*
  - What it tests: Triangle t1 adjacent; not yet visited
  - Repair action: Append to flood-fill todo list
  - Suggested fixture: defect mentioning 't1 != NULL && !IS_BIT(t1, 5)'
- **Branch 3** @ line 811 — *ADJACENT_TRIANGLE_T2*
  - What it tests: Triangle t2 adjacent; not visited
  - Repair action: Append to todo; continue BFS
  - Suggested fixture: defect mentioning 't2 != NULL && !IS_BIT(t2, 5)'
- **Branch 4** @ line 812 — *ADJACENT_TRIANGLE_T3*
  - What it tests: Third adjacent triangle t3
  - Repair action: Add to component traversal
  - Suggested fixture: defect mentioning 't3 != NULL && !IS_BIT(t3, 5)'
- **Branch 5** @ line 826 — *MULTIPLE_COMPONENTS_FOUND*
  - What it tests: Component has more triangles than previous maximum
  - Repair action: Update biggest component reference
  - Suggested fixture: defect mentioning 'gnt=nt', 'biggest'
- **Branch 6** @ line 832 — *NON_LARGEST_COMPONENT*
  - What it tests: Component is not the largest
  - Repair action: Mark triangles for unlinking; nullify edges/vertices
  - Suggested fixture: defect mentioning '((List *)n->data) != biggest'
- **Branch 7** @ line 848 — *COMPONENTS_REMOVED*
  - What it tests: Non-largest components exist (nt > 0)
  - Repair action: Mark topology dirty; call removeUnlinkedElements()
  - Suggested fixture: defect mentioning 'd_boundaries = d_handles = d_shells = 1'

##### `checkAndRepair::removeSmallestComponents@L861` — lines 861–901
(7 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 869 — *EMPTY_MESH*
  - What it tests: Mesh has no triangles
  - Repair action: Return 0; no area filtering needed
  - Suggested fixture: defect mentioning 'T.numels() == 0'
- **Branch 2** @ line 880 — *ADJACENT_TRIANGLE_T1_AREA*
  - What it tests: Triangle t1 adjacent; not visited
  - Repair action: Append to component; mark visited
  - Suggested fixture: defect mentioning 's = t->t1()', '!IS_BIT(s, 5)'
- **Branch 3** @ line 881 — *ADJACENT_TRIANGLE_T2_AREA*
  - What it tests: Triangle t2 unvisited; same connected component
  - Repair action: Add to todo; accumulate area
  - Suggested fixture: defect mentioning 't->t2()'
- **Branch 4** @ line 882 — *ADJACENT_TRIANGLE_T3_AREA*
  - What it tests: Third adjacent triangle t3
  - Repair action: Append for BFS; include in component area
  - Suggested fixture: defect mentioning 't->t3()'
- **Branch 5** @ line 884 — *AREA_ACCUMULATION*
  - What it tests: Accumulate triangle area in component
  - Repair action: Add t->area() to pa; continue traversal
  - Suggested fixture: defect mentioning 'pa += t->area()'
- **Branch 6** @ line 886 — *COMPONENT_AREA_BELOW_THRESHOLD*
  - What it tests: Component total area < eps_area
  - Repair action: Unlink all component triangles; increment rem_comps
  - Suggested fixture: defect mentioning 'pa < eps_area'
- **Branch 7** @ line 894 — *SMALL_COMPONENTS_REMOVED*
  - What it tests: Any components removed (rem_comps > 0)
  - Repair action: Mark topology dirty; call removeUnlinkedElements()
  - Suggested fixture: defect mentioning 'd_boundaries = d_handles = d_shells = 1'

##### `holeFilling::StarTriangulateHole` — lines 46–93
(3 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 48 — *EDGE_NOT_ON_BOUNDARY*
  - What it tests: Input edge is not a boundary edge
  - Repair action: Return 0; no hole to fill
  - Suggested fixture: defect mentioning '!e->isOnBoundary()'
- **Branch 2** @ line 62 — *BOUNDARY_LOOP_CLOSURE*
  - What it tests: Traversal returns to start vertex
  - Repair action: Collect all boundary vertices in loop
  - Suggested fixture: defect mentioning 'v != e->v1', 'nextOnBoundary'
- **Branch 3** @ line 66 — *BARYCENTER_COMPUTATION*
  - What it tests: Accumulate all boundary vertex coordinates
  - Repair action: Sum positions; divide by count for barycenter
  - Suggested fixture: defect mentioning 'np = np+(*v)'

##### `holeFilling::TriangulateHole@L157` — lines 157–292
(6 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 159 — *EDGE_NOT_ON_BOUNDARY*
  - What it tests: Edge not boundary
  - Repair action: Return 0; cannot fill interior edge
  - Suggested fixture: defect mentioning '!e->isOnBoundary()'
- **Branch 2** @ line 183 — *ANGLE_COMPUTATION_FAILURE*
  - What it tests: No valid boundary vertex found for triangulation (gang == DBL_MAX)
  - Repair action: Log warning; unmark vertices; return 0
  - Suggested fixture: defect mentioning 'gang == DBL_MAX'
- **Branch 3** @ line 195 — *EULER_EDGE_TRIANGLE_FAILURE*
  - What it tests: Cannot create triangle (invalid edge pair)
  - Repair action: Mark vertex as bad; skip this candidate
  - Suggested fixture: defect mentioning '!EulerEdgeTriangle(e1, e2)'
- **Branch 4** @ line 213 — *NORMAL_COMPUTATION_FAILURE*
  - What it tests: Average normal from new triangles is zero/null
  - Repair action: Log warning; return nt; skip optimization phase
  - Suggested fixture: defect mentioning 'nor.isNull()', 'Unable to compute'
- **Branch 5** @ line 258 — *DELAUNAY_CONSTRAINED_SWAP*
  - What it tests: Edge swap improves Delaunay quality
  - Repair action: Keep swap; increment edge optimization counter
  - Suggested fixture: defect mentioning 'e1->delaunayMinAngle()', 'sw++'
- **Branch 6** @ line 270 — *WATSON_INSERT_FAILURE*
  - What it tests: watsonInsert returns NULL (point outside triangulation)
  - Repair action: Skip interior point; continue with next
  - Suggested fixture: defect mentioning 'watsonInsert', 'p = ((Point *)n->data)'

##### `holeFilling::TriangulateHole@L439` — lines 439–485
(4 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 441 — *EDGE_NOT_ON_BOUNDARY*
  - What it tests: Edge not boundary
  - Repair action: Return 0
  - Suggested fixture: defect mentioning '!e->isOnBoundary()'
- **Branch 2** @ line 453 — *SINGLE_VERTEX_HOLE*
  - What it tests: Hole has only one unvisited neighbor (cap geometry)
  - Repair action: Return 0; cannot triangulate single-vertex hole
  - Suggested fixture: defect mentioning 'nextEdge(e)->isOnBoundary()', 'prevEdge(e)->isOnBoundary()'
- **Branch 3** @ line 467 — *ANGLE_COMPUTATION_FAILURE*
  - What it tests: Cannot find valid triangulation vertex
  - Repair action: Log warning; unmark vertices; unlink created triangles; return 0
  - Suggested fixture: defect mentioning 'gang == DBL_MAX'
- **Branch 4** @ line 480 — *EULER_EDGE_TRIANGLE_FAILURE*
  - What it tests: Cannot create triangle (geometry invalid)
  - Repair action: Mark vertex bad; continue search
  - Suggested fixture: defect mentioning 'EulerEdgeTriangle(e1,e2)==NULL', 'MARK_BIT(v, 5)'

##### `holeFilling::TriangulateHole@L98` — lines 98–152
(5 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 100 — *EDGE_NOT_ON_BOUNDARY*
  - What it tests: Edge not boundary edge
  - Repair action: Return 0; cannot fill non-boundary
  - Suggested fixture: defect mentioning '!e->isOnBoundary()'
- **Branch 2** @ line 122 — *ANGLE_COMPUTATION_FAILURE*
  - What it tests: All boundary vertices marked (gang == DBL_MAX)
  - Repair action: Log warning; return 0; triangulation incomplete
  - Suggested fixture: defect mentioning 'gang == DBL_MAX', "Can't complete"
- **Branch 3** @ line 133 — *EULER_EDGE_TRIANGLE_FAILURE*
  - What it tests: Cannot create triangle from edges (invalid geometry)
  - Repair action: Mark vertex as bad; try next candidate
  - Suggested fixture: defect mentioning '!EulerEdgeTriangle(e1, e2)', 'MARK_BIT(v, 5)'
- **Branch 4** @ line 145 — *DELAUNAY_SWAP_IMPROVES_ANGLE*
  - What it tests: Edge swap reduces Delaunay min angle
  - Repair action: Undo swap (fast=1); keep original edge
  - Suggested fixture: defect mentioning 'delaunayMinAngle() <= ang', 'e->swap(1)'
- **Branch 5** @ line 148 — *OPTIMIZATION_TIMEOUT*
  - What it tests: Edge optimization loop count exceeds threshold
  - Repair action: Log warning; break optimization; return current count
  - Suggested fixture: defect mentioning 'i < 0', 'taking too long'

##### `holeFilling::fillSmallBoundaries` — lines 511–569
(5 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 523 — *SELECTION_PRESENT*
  - What it tests: Some triangles are pre-selected (visited)
  - Repair action: Mark surrounding vertices; constrain filling to unselected regions
  - Suggested fixture: defect mentioning 'IS_VISITED(t)'
- **Branch 2** @ line 536 — *VERTEX_ON_BOUNDARY*
  - What it tests: Vertex is on mesh boundary
  - Repair action: Count boundary edges from this vertex
  - Suggested fixture: defect mentioning 'v->isOnBoundary()'
- **Branch 3** @ line 542 — *BOUNDARY_CROSSING_CONSTRAINT*
  - What it tests: Boundary vertex is marked (selection boundary)
  - Repair action: Set grd >= nbe+1; skip this boundary loop
  - Suggested fixture: defect mentioning 'IS_BIT(w, 6)', 'grd=nbe+1'
- **Branch 4** @ line 547 — *SMALL_BOUNDARY_THRESHOLD*
  - What it tests: Boundary has <= nbe edges
  - Repair action: Add to fill list; mark for triangulation
  - Suggested fixture: defect mentioning 'grd <= nbe', 'bdrs.appendHead'
- **Branch 5** @ line 556 — *PATCH_TRIANGULATION_WITH_REFINEMENT*
  - What it tests: Hole triangulation succeeds AND refine_patches=true
  - Repair action: Call refineSelectedHolePatches; improve patch density
  - Suggested fixture: defect mentioning 'TriangulateHole', 'refineSelectedHolePatches'

##### `holeFilling::joinBoundaryLoops` — lines 721–795
(6 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 729 — *NULL_VERTEX_INPUT*
  - What it tests: Input gv or gw is NULL or not on boundary
  - Repair action: Return NULL; cannot join
  - Suggested fixture: defect mentioning 'gv == NULL || gw == NULL', '!gv->isOnBoundary()'
- **Branch 2** @ line 737 — *SAME_BOUNDARY_LOOP_NOJUSTCONNECT*
  - What it tests: When justconnect=false: gw reached from gv (same loop)
  - Repair action: Return NULL; cannot fill hole between same loop
  - Suggested fixture: defect mentioning 'if (v == gw) return NULL'
- **Branch 3** @ line 742 — *ADJACENT_VERTICES_JUSTCONNECT*
  - What it tests: gw is immediate neighbor of gv (justconnect=true)
  - Repair action: Create single triangle; mark visited; return bridge edge
  - Suggested fixture: defect mentioning 'gw == gvn', 'EulerEdgeTriangle'
- **Branch 4** @ line 766 — *BOUNDARY_LOOP_LENGTH_ACCUMULATION*
  - What it tests: Compute perimeter of each boundary loop
  - Repair action: Sum edge lengths; use for balanced triangle insertion
  - Suggested fixture: defect mentioning 'tl1 += e->length()'
- **Branch 5** @ line 779 — *BALANCED_TRIANGULATION_CRITERION*
  - What it tests: Compare cost of next triangle from loop 1 vs loop 2
  - Repair action: Select lower-cost side; add triangle; advance loop pointer
  - Suggested fixture: defect mentioning 'if (c1<c2)', 'pl1 -= gve->length()'
- **Branch 6** @ line 792 — *PATCH_REFINEMENT*
  - What it tests: refine=true requested
  - Repair action: Call refineSelectedHolePatches to improve mesh density
  - Suggested fixture: defect mentioning 'if (refine)', 'refineSelectedHolePatches()'

##### `holeFilling::refineSelectedHolePatches` — lines 576–709
(7 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 590 — *REGION_INITIALIZATION*
  - What it tests: t0 is pre-selected (visited)
  - Repair action: Unmark t0; build region via BFS on visited triangles
  - Suggested fixture: defect mentioning '!IS_VISITED(t0)', 'UNMARK_VISIT(t0)'
- **Branch 2** @ line 607 — *EDGE_FIRST_OCCURRENCE*
  - What it tests: Edge e1 not yet visited (first occurrence)
  - Repair action: Mark edge; add to all_edges list; toggle mark on repeat
  - Suggested fixture: defect mentioning '!IS_BIT(e, 5)', 'MARK_BIT(e, 5)'
- **Branch 3** @ line 615 — *EDGE_INTERIOR_DETECTION*
  - What it tests: Edge appears only once in traversal (interior)
  - Repair action: Unmark and add to interior_edges; mark with BIT 5
  - Suggested fixture: defect mentioning 'IS_BIT(e, 5)', 'interior_edges'
- **Branch 4** @ line 632 — *EDGE_LENGTH_AVERAGING*
  - What it tests: Sum non-interior edges to compute average
  - Repair action: Compute sigma = average edge length for vertex
  - Suggested fixture: defect mentioning 'sigma += e->length()'
- **Branch 5** @ line 654 — *VERTEX_SPLIT_DENSITY_CHECK*
  - What it tests: All three vertices far from centroid AND far from their own average
  - Repair action: Insert new vertex at triangle center; subdivide
  - Suggested fixture: defect mentioning 'dv1>sigma && dv1>sv1', 'splitTriangle'
- **Branch 6** @ line 683 — *EDGE_SWAP_DELAUNAY_IMPROVEMENT*
  - What it tests: Edge swap reduces length AND improves quality (l*0.999999)
  - Repair action: Keep swap; add neighbors to swap list
  - Suggested fixture: defect mentioning 'e->squaredLength() >= l*0.999999', 'e->swap(1)'
- **Branch 7** @ line 699 — *VERTEX_INSERTION_CONVERGENCE*
  - What it tests: No new vertices inserted in iteration (pnnt == nnt)
  - Repair action: Increment gits; stop after gits >= 10
  - Suggested fixture: defect mentioning 'pnnt==nnt', 'gits++'

##### `holeFilling::retriangulateVT` — lines 383–433
(4 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 399 — *TRIANGLE_NORMAL_ACCUMULATION*
  - What it tests: Accumulate normal from each vertex's incident triangles
  - Repair action: Sum normals; normalize to average direction
  - Suggested fixture: defect mentioning 'nor = nor+t->getNormal()'
- **Branch 2** @ line 404 — *HOLE_TRIANGULATION*
  - What it tests: TriangulateHole fills vertex neighborhood hole
  - Repair action: Create new triangulation; check quality
  - Suggested fixture: defect mentioning 'TriangulateHole(e0, &nor)'
- **Branch 3** @ line 409 — *RETRIANGULATION_QUALITY_CHECK*
  - What it tests: New triangles have overlap or degeneracy
  - Repair action: Break; trigger rollback
  - Suggested fixture: defect mentioning 't->overlaps()', 'isExactlyDegenerate'
- **Branch 4** @ line 413 — *RETRIANGULATION_ROLLBACK*
  - What it tests: Re-triangulation failed quality check (i < nt)
  - Repair action: Unlink new triangles; restore original VT structure
  - Suggested fixture: defect mentioning 'Re-triangulation failed', 'Restoring'

##### `holeFilling::watsonInsert` — lines 297–378
(7 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 309 — *POINT_IN_CIRCUMSPHERE*
  - What it tests: Point p lies in triangle's circumsphere
  - Repair action: Mark triangle for cavity removal; append to todo
  - Suggested fixture: defect mentioning 't->inSphere(p)', 'MARK_BIT(t, 6)'
- **Branch 2** @ line 312 — *CAVITY_VERTEX_V1*
  - What it tests: Vertex v1 part of cavity boundary
  - Repair action: Mark vertex; track for boundary restoration
  - Suggested fixture: defect mentioning '!IS_BIT(v1, 5)', 'bdr.appendHead(v1)'
- **Branch 3** @ line 313 — *CAVITY_VERTEX_V2*
  - What it tests: Vertex v2 in cavity boundary set
  - Repair action: Add to boundary; mark visited
  - Suggested fixture: defect mentioning 'bdr.appendHead(v2)'
- **Branch 4** @ line 314 — *CAVITY_VERTEX_V3*
  - What it tests: Vertex v3 part of cavity
  - Repair action: Add to boundary; prevent duplication
  - Suggested fixture: defect mentioning 'bdr.appendHead(v3)'
- **Branch 5** @ line 320 — *NO_CIRCUMSPHERE_TRIANGLES*
  - What it tests: No triangles contain point (empty cavity)
  - Repair action: Return NULL; point outside current triangulation
  - Suggested fixture: defect mentioning 'bdr.numels() == 0'
- **Branch 6** @ line 325 — *BOUNDARY_EDGE_SELECTION*
  - What it tests: Vertex has mixed internal/external edges
  - Repair action: Select boundary edge (cavity edge)
  - Suggested fixture: defect mentioning '!IS_BIT(e->t1, 6) || !IS_BIT(e->t2, 6)'
- **Branch 7** @ line 333 — *CAVITY_TRIANGLE_REMOVAL*
  - What it tests: Remove all triangles in cavity
  - Repair action: Call unlinkTriangleNoManifold; free interior triangles
  - Suggested fixture: defect mentioning 'unlinkTriangleNoManifold(t)'


#### `src/Algorithms/holeFilling.cpp`
(4 methods, 17 branches)

##### `Basic_TMesh.TriangulateHole@L157` — lines 157–292
(6 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 159 — *boundary_check_failure*
  - What it tests: edge is on boundary
  - Repair action: early return 0
  - Suggested fixture: defect mentioning '!e->isOnBoundary()'
- **Branch 2** @ line 177 — *loop_termination*
  - What it tests: boundary vertex chain has >2 vertices
  - Repair action: exit while loop when 2 or fewer vertices remain
  - Suggested fixture: defect mentioning 'while (bvs.numels() > 2)'
- **Branch 3** @ line 183 — *ear_not_found*
  - What it tests: no valid ear found (gang equals DBL_MAX)
  - Repair action: unmark bits and return 0
  - Suggested fixture: defect mentioning "Can't complete the triangulation"
- **Branch 4** @ line 195 — *euler_operation_failure*
  - What it tests: EulerEdgeTriangle fails, bit 5 marks vertex
  - Repair action: mark vertex and skip it
  - Suggested fixture: defect mentioning 'MARK_BIT(v, 5)'
- **Branch 5** @ line 213 — *degenerate_hole_patch*
  - What it tests: hole patch normal is null after triangulation
  - Repair action: early return without optimization
  - Suggested fixture: defect mentioning 'Unable to compute an average normal'
- **Branch 6** @ line 257 — *edge_swap_constraint*
  - What it tests: edge swap violates Delaunay property
  - Repair action: swap back if min angle degrades
  - Suggested fixture: defect mentioning 'if (e1->swap())', 'delaunayMinAngle'

##### `Basic_TMesh.joinBoundaryLoops` — lines 721–795
(3 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 733 — *boundary_loop_traversal*
  - What it tests: boundary loop traversal completes cycle
  - Repair action: proceed with bridge creation
  - Suggested fixture: defect mentioning 'while (v != gv)'
- **Branch 2** @ line 760 — *bridge_triangulation_failure*
  - What it tests: TriangulateHole returns 0
  - Repair action: clean up temporary data and return NULL
  - Suggested fixture: defect mentioning 'TriangulateHole'
- **Branch 3** @ line 775 — *refinement_skip*
  - What it tests: refine parameter is true
  - Repair action: call refineSelectedHolePatches
  - Suggested fixture: defect mentioning 'if (refine)'

##### `Basic_TMesh.refineSelectedHolePatches` — lines 576–709
(4 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 594 — *patch_not_isolated*
  - What it tests: selected triangles form a connected patch
  - Repair action: continue to next method if not isolated
  - Suggested fixture: defect mentioning 'isSelectionSimple'
- **Branch 2** @ line 602 — *boundary_edge_density_threshold*
  - What it tests: edge count in boundary loop exceeds max_edges
  - Repair action: skip refinement for that boundary loop
  - Suggested fixture: defect mentioning 'numels() >'
- **Branch 3** @ line 625 — *steiner_vertex_generation*
  - What it tests: edge length ratio triggers Steiner insertion
  - Repair action: insert midpoint vertex if ratio exceeds threshold
  - Suggested fixture: defect mentioning 'splitEdge'
- **Branch 4** @ line 650 — *retriangulation_failure*
  - What it tests: Delaunay retriangulation of patch
  - Repair action: skip refinement if retriangulation fails
  - Suggested fixture: defect mentioning 'retriangulateVT'

##### `Basic_TMesh.watsonInsert` — lines 297–378
(4 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 308 — *point_in_triangle*
  - What it tests: point p lies inside triangle t
  - Repair action: split triangle into 3
  - Suggested fixture: defect mentioning 'p->isInside(t)'
- **Branch 2** @ line 318 — *point_on_edge*
  - What it tests: point p lies on edge e
  - Repair action: split edge and two adjacent triangles
  - Suggested fixture: defect mentioning 'p->isOnEdge(e)'
- **Branch 3** @ line 335 — *point_outside_triangulation*
  - What it tests: point p outside current mesh
  - Repair action: create new triangles bridging point to cavity
  - Suggested fixture: defect mentioning 'is outside'
- **Branch 4** @ line 352 — *triangle_list_exhaustion*
  - What it tests: remaining triangles to check list not exhausted
  - Repair action: continue checking cavity triangles
  - Suggested fixture: defect mentioning 'tR->numels() >'


#### `src/Algorithms/{detectIntersections,subdivision,marchIntersections}.cpp`
(13 methods, 41 branches)

##### `Basic_TMesh.loopSubdivision` — lines 97–168
(6 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 106 — *Midpoint-only vs full relaxation*
  - What it tests: Whether to apply Loop's vertex relaxation or skip for pure midpoint scheme
  - Repair action: Compute new positions for original vertices or leave unmoved
  - Suggested fixture: defect mentioning 'midpoint', 'loopRelaxOriginal'
- **Branch 2** @ line 108 — *Selection-constrained vs global subdivision*
  - What it tests: Whether subdividing a pre-selected triangle region or entire mesh
  - Repair action: Mark edges in selection for subdivision or all edges
  - Suggested fixture: defect mentioning 'is_selection', 'IS_VISITED(t)'
- **Branch 3** @ line 115 — *Sharp-edge preservation*
  - What it tests: Whether mesh contains tagged sharp/crease edges
  - Repair action: Flag warning if creases detected; continue subdivision anyway
  - Suggested fixture: defect mentioning 'IS_SHARPEDGE', 'detected_sharp'
- **Branch 4** @ line 125 — *Boundary vs interior edge split*
  - What it tests: Whether edge is on mesh boundary
  - Repair action: Use midpoint for boundary edges; use Loop weights for interior
  - Suggested fixture: defect mentioning 'isOnBoundary()', 'k'
- **Branch 5** @ line 131 — *Triangle topology after split*
  - What it tests: Number of triangles created depends on edge adjacency (boundary vs dual-vert)
  - Repair action: Mark newly created triangles as visited if parent was selected
  - Suggested fixture: defect mentioning 'ls->e->t2', 'MARK_VISIT'
- **Branch 6** @ line 151 — *Edge swap candidacy*
  - What it tests: Whether edge connects a new vertex to one old vertex
  - Repair action: Perform edge swaps to improve aspect ratios
  - Suggested fixture: defect mentioning 'IS_VISITED2', 'e->swap'

##### `Basic_TMesh.safeCoordBackApproximation` — lines 257–299
(4 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 275 — *Overlapping-edge detection*
  - What it tests: Whether any edge pair overlaps after coordinate quantization
  - Repair action: Count overlaps; iterate until count stabilizes or becomes zero
  - Suggested fixture: defect mentioning 'e->overlaps()', 'nos'
- **Branch 2** @ line 284 — *Opposite-vertex selection*
  - What it tests: Which opposite vertex (of edge endpoints) has smaller coplanar triangle area
  - Repair action: Jitter coordinates of vertex with smaller area
  - Suggested fixture: defect mentioning 'squaredTriangleArea3D', 'ov1', 'ov2'
- **Branch 3** @ line 288 — *Jitter escape condition*
  - What it tests: Whether a coordinate perturbation resolved the overlap
  - Repair action: Break jitter loop early if overlap cleared; otherwise undo and try next direction
  - Suggested fixture: defect mentioning 'a = b = c = 2', 'overlaps()'
- **Branch 4** @ line 295 — *Convergence check*
  - What it tests: Whether overlap count decreased compared to previous iteration
  - Repair action: Continue or exit iterative repair based on count change
  - Suggested fixture: defect mentioning 'pnos', 'nos < pnos'

##### `Basic_TMesh.selectIntersectingTriangles` — lines 138–204
(3 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 149 — *Selected-vs-full-mesh*
  - What it tests: Whether spatial partitioning filters on pre-selected triangles or processes entire mesh
  - Repair action: Build cells from either selected subset or all triangles
  - Suggested fixture: defect mentioning 'isSelection', 'selT', 'selV'
- **Branch 2** @ line 167 — *Cell-saturation threshold*
  - What it tests: When a spatial partition cell exceeds triangle density limit or cell count ceiling
  - Repair action: Subdivide cell recursively or mark for brute-force intersection test
  - Suggested fixture: defect mentioning 'DI_MAX_NUMBER_OF_CELLS', 'tris_per_cell'
- **Branch 3** @ line 172 — *Spatial recursion vs termination*
  - What it tests: Whether cell recursion depth progresses or terminates
  - Repair action: Fork cell into two subcells or queue for intersection testing
  - Suggested fixture: defect mentioning 'fork()', 'todo.appendTail'

##### `Basic_TMesh.strongIntersectionRemoval` — lines 374–393
(3 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 381 — *Intersection-detection trigger*
  - What it tests: Whether any self-intersecting triangles exist
  - Repair action: Enter removal loop or exit with success
  - Suggested fixture: defect mentioning 'selectIntersectingTriangles()'
- **Branch 2** @ line 381 — *Iteration limit*
  - What it tests: Whether iteration count exceeds maximum allowed passes
  - Repair action: Fail repair or continue another iteration
  - Suggested fixture: defect mentioning 'max_iters', 'iter_count'
- **Branch 3** @ line 383 — *Selection-growth depth*
  - What it tests: Growth iterations scale with repair pass number
  - Repair action: Expand selected region by n rings where n=current iteration
  - Suggested fixture: defect mentioning 'growSelection()', 'for (n=1'

##### `di_cell.selectIntersections` — lines 107–129
(3 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 119 — *Redundant pair-test detection*
  - What it tests: Whether a triangle pair was already tested in another cell
  - Repair action: Skip test if pair cached; otherwise perform full intersection test
  - Suggested fixture: defect mentioning 't->info', 'containsNode'
- **Branch 2** @ line 121 — *Proper vs improper intersection*
  - What it tests: Intersection type classification: proper (transverse) vs improper (touching)
  - Repair action: Mark triangles as intersecting based on justproper flag
  - Suggested fixture: defect mentioning 'justproper', 'intersects'
- **Branch 3** @ line 124 — *Info-list initialization*
  - What it tests: Whether triangle already has an intersection info list attached
  - Repair action: Reuse existing list or create new; append opposite triangle
  - Suggested fixture: defect mentioning 't->info != NULL', 'new List'

##### `mc_cell.lookdown` — lines 106–135
(2 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 118 — *Edge-to-vertex case assignment*
  - What it tests: Whether edge intersection marks endpoint or opposite endpoint
  - Repair action: Set appropriate cube vertex based on edge orientation
  - Suggested fixture: defect mentioning 'c1[i]', 'c2[i]'
- **Branch 2** @ line 123 — *Topological closure via edge propagation*
  - What it tests: Whether missing edge can be inferred from adjacent vertices
  - Repair action: Propagate vertex status backward if prior vertex unmarked
  - Suggested fixture: defect mentioning 'm = -1', 'continue'

##### `mc_cell.lookup` — lines 48–103
(2 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 53 — *Edge-intersection sample assignment*
  - What it tests: Whether edge intersection occurs on first or second endpoint
  - Repair action: Mark appropriate vertex as inside/outside
  - Suggested fixture: defect mentioning 'ints[i]->sg', 'v[0]', 'v[1]'
- **Branch 2** @ line 68 — *Vertex-connectedness inference*
  - What it tests: Marching-cubes vertex propagation when edge is absent
  - Repair action: Infer vertex sign from neighbors to maintain topological consistency
  - Suggested fixture: defect mentioning '!ints[i]', 'v[i]'

##### `mc_cell.polygonize` — lines 155–448
(3 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 160 — *Case lookup*
  - What it tests: Marching-cubes case index determines triangle fan structure
  - Repair action: Index into 256-entry lookup table to find polygon edges
  - Suggested fixture: defect mentioning 'lookdown()', 'lu'
- **Branch 2** @ line 425 — *Triangle generation condition*
  - What it tests: Whether case table contains valid triangle indices (not -1)
  - Repair action: Generate triangle or skip if degenerate case
  - Suggested fixture: defect mentioning 'mc_triTable[lu][i] != -1'
- **Branch 3** @ line 430 — *Vertex availability*
  - What it tests: Whether all three vertices of a triangle exist in edge-intersection list
  - Repair action: Create triangle or emit warning if vertex missing
  - Suggested fixture: defect mentioning 'v[t[0]] && v[t[1]] && v[t[2]]'

##### `mc_grid.createCells` — lines 681–757
(3 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 694 — *Cell-coordinate discretization*
  - What it tests: Intersection parameter maps to discrete cell index
  - Repair action: Create cells at floor(intersection coord) in multiple voxels
  - Suggested fixture: defect mentioning 'TMESH_TO_INT(floor', 'k'
- **Branch 2** @ line 729 — *Duplicate cell merging*
  - What it tests: Whether multiple intersections hit same cell coordinate
  - Repair action: Merge cell edge-intersection lists
  - Suggested fixture: defect mentioning 'mcc->x == last->x', 'last->merge'
- **Branch 3** @ line 753 — *Merged cell invalidation*
  - What it tests: Whether cell was merged into predecessor
  - Repair action: Delete invalidated cell (mcc->x == -1)
  - Suggested fixture: defect mentioning 'mcc->x == -1'

##### `mc_grid.purgeList` — lines 534–626
(3 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 576 — *Duplicate entering-intersection removal*
  - What it tests: Whether consecutive entering rays hit same cell
  - Repair action: Mark duplicate as invalid (ic = -1) to remove
  - Suggested fixture: defect mentioning 'sg==1', 'lc'
- **Branch 2** @ line 587 — *Duplicate exiting-intersection removal*
  - What it tests: Whether consecutive exiting rays leave same cell
  - Repair action: Mark duplicate as invalid to remove
  - Suggested fixture: defect mentioning 'sg==0'
- **Branch 3** @ line 609 — *Discordant pair removal*
  - What it tests: Whether entering and exiting rays in same cell have mismatched count
  - Repair action: Remove conflicting ray based on sign balance
  - Suggested fixture: defect mentioning 'mc1->sg != mc2->sg', 'count[mc1c]'

##### `mc_grid.remesh` — lines 818–873
(3 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 828 — *Coordinate normalization*
  - What it tests: Shift and scale mesh to unit grid before sampling
  - Repair action: Apply transformation to all vertices
  - Suggested fixture: defect mentioning '((*v)-origin)/norm'
- **Branch 2** @ line 834 — *Triangle sampling*
  - What it tests: Each triangle intersects axis-aligned sampling planes
  - Repair action: Record intersection coordinates for later cell creation
  - Suggested fixture: defect mentioning 'sample_triangle'
- **Branch 3** @ line 859 — *Inverse coordinate transformation*
  - What it tests: Whether simplification is enabled
  - Repair action: Transform back to original coordinates with or without simplification
  - Suggested fixture: defect mentioning 'simplify_result'

##### `mc_grid.simplify` — lines 982–1037
(4 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 996 — *Triangle-normal association*
  - What it tests: Whether normal is stored in triangle or must be created
  - Repair action: Reuse cached normal or compute and cache new one
  - Suggested fixture: defect mentioning 't->info != NULL'
- **Branch 2** @ line 1002 — *Boundary vs interior edge detection*
  - What it tests: Edge is boundary or endpoints have different normal
  - Repair action: Mark boundary and misaligned edges for preservation
  - Suggested fixture: defect mentioning 'isOnBoundary()', 'v1->info != v2->info'
- **Branch 3** @ line 1015 — *Edge-collapse safety*
  - What it tests: Coplanar normals and safe geometry after collapse
  - Repair action: Collapse edge if safe; skip if would create inversion
  - Suggested fixture: defect mentioning 'mc_safeCollapse'
- **Branch 4** @ line 1020 — *Boundary-aware inversion*
  - What it tests: Whether endpoint is boundary vertex
  - Repair action: Invert edge direction before collapse
  - Suggested fixture: defect mentioning 'IS_VISITED2(e->v2)', 'e->invert'

##### `mc_grid.trackOuterHull` — lines 759–797
(2 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 771 — *Ray containment*
  - What it tests: Whether ray has multiple entries/exits (spans mesh interior)
  - Repair action: Select outer component via flood-fill if ray has bracketing intersections
  - Suggested fixture: defect mentioning 'ac->numels()>1'
- **Branch 2** @ line 775 — *Triangle adjacency traversal*
  - What it tests: Whether vertex has incident triangles in either direction
  - Repair action: Start flood-fill from available adjacent triangle
  - Suggested fixture: defect mentioning 'e0->t1', 'e0->t2'


#### `src/MeshFix/meshfix.cpp`
(1 methods, 4 branches)

##### `main` — lines 131–212
(4 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 143 — *missing_input_file*
  - What it tests: argc less than 2 or no input filename
  - Repair action: print usage and exit
  - Suggested fixture: defect mentioning 'if (argc < 2)'
- **Branch 2** @ line 153 — *input_load_failure*
  - What it tests: file opening or parsing error
  - Repair action: exit with error message
  - Suggested fixture: defect mentioning 'load failed'
- **Branch 3** @ line 167 — *repair_output_flag*
  - What it tests: -c or -a flag set
  - Repair action: call meshfix.autoRepair()
  - Suggested fixture: defect mentioning 'autoRepair'
- **Branch 4** @ line 180 — *output_write_failure*
  - What it tests: save to output file
  - Repair action: catch and report I/O error
  - Suggested fixture: defect mentioning 'save'


#### `src/TMesh/edge.cpp`
(3 methods, 31 branches)

##### `Edge.collapseOnV1` — lines 169–238
(15 branches; 10 COVERED via Me090–Me099 [wave 4B]; 5 deferred)

- **Branch 1** @ line 176 — *EXTRACT_T1_EDGES_AND_NEIGHBORS* — DEFERRED (topology-extraction only; covered implicitly by any collapse fixture)
  - What it tests: If t1 exists, extract its next and prev edges (e1, e2) and their opposite triangles (ta1, ta2)
  - Repair action: Compute local topology of t1 neighborhood; set NULL if t1 is absent
  - Suggested fixture: defect mentioning 'Edge *e1 = (t1 != NULL)?(t1->nextEdge(this)):(NULL)', 'Triangle *ta1'
- **Branch 2** @ line 178 — *EXTRACT_T2_EDGES_AND_NEIGHBORS* — DEFERRED (topology-extraction only; covered implicitly by any collapse fixture)
  - What it tests: If t2 exists, extract edges e3, e4 and opposite triangles ta3, ta4
  - Repair action: Compute local topology of t2 neighborhood
  - Suggested fixture: defect mentioning 'Edge *e3 = (t2 != NULL)?(t2->nextEdge(this)):(NULL)'
- **Branch 3** @ line 187 — *BOUNDARY_EDGE_COLLAPSE_VALIDITY* — **COVERED** → Me090
  - What it tests: Both edge endpoints are boundary vertices; check that adjacent triangles form valid collapse
  - Repair action: Return NULL if collapse would create non-manifold configuration on boundary
  - Suggested fixture: defect mentioning 'if (v1->isOnBoundary() && v2->isOnBoundary())', '!ta3 && !ta4'
- **Branch 4** @ line 190 — *DEGENERATE_DOUBLE_TRIANGLE* — **COVERED** → Me091
  - What it tests: ta1 and ta2 are both non-null and share opposite vertex (would create duplicate edge)
  - Repair action: Return NULL; collapse would degenerate
  - Suggested fixture: defect mentioning 'if (ta1 != NULL && ta2 != NULL && ta1->oppositeVertex(e1) == ta2->oppositeVertex(e2)'
- **Branch 5** @ line 192 — *DEGENERATE_DOUBLE_TRIANGLE_T2* — **COVERED** → Me092
  - What it tests: Similar degeneracy check for ta3 and ta4 (t2 side)
  - Repair action: Return NULL if would create duplicate
  - Suggested fixture: defect mentioning 'if (ta3 != NULL && ta4 != NULL'
- **Branch 6** @ line 195 — *VERTEX_ANCHOR_EDGE_SELECTION* — **COVERED** → Me093
  - What it tests: Choose edge reference for v1 post-collapse based on boundary topology
  - Repair action: v1->e0 = e3 (t2 side) if both t1 neighbors absent, else e2
  - Suggested fixture: defect mentioning 'if (ta1 == NULL && ta2 == NULL) v1->e0 = e3', 'else v1->e0 = e2'
- **Branch 7** @ line 198 — *NEIGHBOR_ANCHOR_UPDATE* — DEFERRED (anchor update; covered implicitly by Me093/Me096)
  - What it tests: Update edge anchors for opposite vertices v3 and v4 in collapsed configuration
  - Repair action: v3->e0 = e2; v4->e0 = e3
  - Suggested fixture: defect mentioning 'if (v3 != NULL) v3->e0 = e2'
- **Branch 8** @ line 201 — *PINCH_DETECT_ON_V2* — **COVERED** → Me094
  - What it tests: Check if merging v2 into v1 would create a pinch (duplicate edge)
  - Repair action: Return NULL if v2 has neighbor tv that already connects to v1
  - Suggested fixture: defect mentioning 'tv->getEdge(v1) != NULL', 'tv != v3 && tv != v4'
- **Branch 9** @ line 207 — *VERTEX_MERGE* — **COVERED** → Me095
  - What it tests: Merge all edges of v2 into v1
  - Repair action: e->replaceVertex(v2, v1) for all edges incident to v2
  - Suggested fixture: defect mentioning 'e->replaceVertex(v2, v1)'
- **Branch 10** @ line 210 — *TRIANGLE_ADJACENCY_REPAIR* — **COVERED** → Me096
  - What it tests: Repair adjacency: replace t1 link in e2 with ta1, and t2 link in e3 with ta4
  - Repair action: e2->replaceTriangle(t1, ta1); e3->replaceTriangle(t2, ta4)
  - Suggested fixture: defect mentioning 'if (e2 != NULL) e2->replaceTriangle(t1, ta1)'
- **Branch 11** @ line 213 — *OPPOSITE_TRIANGLE_REPAIR* — DEFERRED (edge-in-triangle replacement; covered implicitly by Me096)
  - What it tests: Repair edges in the opposite triangles (ta1, ta4) that were adjacent to e1, e4
  - Repair action: ta1->replaceEdge(e1, e2); ta4->replaceEdge(e4, e3)
  - Suggested fixture: defect mentioning 'if (ta1 != NULL) ta1->replaceEdge(e1, e2)'
- **Branch 12** @ line 216 — *MARK_UNLINKED_V2* — **COVERED** → Me097
  - What it tests: Mark v2 for deletion (will be unlinked post-collapse)
  - Repair action: v2->e0 = NULL
  - Suggested fixture: defect mentioning 'v2->e0 = NULL'
- **Branch 13** @ line 217 — *MARK_UNLINKED_EDGES* — DEFERRED (mark-for-delete bookkeeping; captured by Me097/Me098/Me099 topology context)
  - What it tests: Mark incident edges of collapsed triangles for deletion
  - Repair action: e4->v1 = e4->v2 = NULL; e1->v1 = e1->v2 = NULL; mark t1, t2 edges as NULL
  - Suggested fixture: defect mentioning 'if (e4 != NULL) e4->v1 = e4->v2 = NULL'
- **Branch 14** @ line 222 — *ORPHAN_EDGE_CLEANUP_E2* — **COVERED** → Me098
  - What it tests: If e2 becomes unlinked (no incident triangles) after collapse, mark for deletion
  - Repair action: Free e2, null v3 anchor
  - Suggested fixture: defect mentioning 'if (e2 != NULL && e2->t1 == NULL && e2->t2 == NULL)'
- **Branch 15** @ line 227 — *ORPHAN_EDGE_CLEANUP_E3* — **COVERED** → Me099
  - What it tests: If e3 becomes unlinked after collapse, mark for deletion
  - Repair action: Free e3, null v4 anchor
  - Suggested fixture: defect mentioning 'if (e3 != NULL && e3->t1 == NULL && e3->t2 == NULL)'

##### `Edge.stitch` — lines 366–396
(10 branches; all COVERED by Me160–Me169 wave 6C)

- **Branch 1** @ line 369 — *BOUNDARY_EDGE_REQUIREMENT* — **COVERED** → Me160
  - What it tests: Edge must be on boundary (no interior edge stitching)
  - Repair action: Return false if edge is interior (has two triangles)
  - Suggested fixture: defect mentioning 'if (!isOnBoundary()) return 0'
- **Branch 2** @ line 371 — *STITCH_START_TRIANGLE* — **COVERED** → Me161
  - What it tests: Identify starting triangle (t0) from the single or first incident triangle
  - Repair action: t0 = (t1 != NULL) ? (t1) : (t2)
  - Suggested fixture: defect mentioning 'Triangle *t, *t0 = (t1 != NULL) ? (t1) : (t2)'
- **Branch 3** @ line 375 — *BOUNDARY_WALK_V1* — **COVERED** → Me162
  - What it tests: Walk boundary from v1 along edge loop until reaching a candidate stitch edge
  - Repair action: Traverse t->nextEdge() chain to find geometrically coincident boundary edge
  - Suggested fixture: defect mentioning 'for (v0 = v1; v0 != NULL', 't = e1->oppositeTriangle(t)'
- **Branch 4** @ line 375 — *BOUNDARY_WALK_V2* — **COVERED** → Me163
  - What it tests: Walk boundary from v2 if walk from v1 fails
  - Repair action: Repeat walk starting from v2 endpoint
  - Suggested fixture: defect mentioning 'v0 = ((v0 == v1) ? (v2) : (NULL))'
- **Branch 5** @ line 384 — *STITCH_CANDIDATE_FOUND* — **COVERED** → Me164
  - What it tests: Walking boundary found edge e1 whose opposite vertex matches this edge's opposite vertex at v0
  - Repair action: Merge the boundary chains by stitching: replace e1 with this in opposing triangle
  - Suggested fixture: defect mentioning 'if (e1->oppositeVertex(v0) == oppositeVertex(v0))'
- **Branch 6** @ line 386 — *STITCH_TRIANGLE_MERGER* — **COVERED** → Me165
  - What it tests: Stitch found: get the triangle t from e1 (whichever side is available)
  - Repair action: t = (e1->t1 != NULL) ? (e1->t1) : (e1->t2)
  - Suggested fixture: defect mentioning 't = (e1->t1 != NULL) ? (e1->t1) : (e1->t2)'
- **Branch 7** @ line 387 — *STITCH_EDGE_REPLACEMENT* — **COVERED** → Me166
  - What it tests: Replace e1 in t with this edge to join boundary chains
  - Repair action: t->replaceEdge(e1, this)
  - Suggested fixture: defect mentioning 't->replaceEdge(e1, this)'
- **Branch 8** @ line 388 — *STITCH_ANCHOR_UPDATE* — **COVERED** → Me167
  - What it tests: After stitch, update vertex anchors to this edge
  - Repair action: v1->e0 = v2->e0 = this
  - Suggested fixture: defect mentioning 'v1->e0 = v2->e0 = this'
- **Branch 9** @ line 389 — *STITCH_ORPHAN_EDGE* — **COVERED** → Me168
  - What it tests: Mark stitched edge e1 as unlinked (no longer part of mesh)
  - Repair action: e1->v1 = e1->v2 = NULL
  - Suggested fixture: defect mentioning 'e1->v1 = e1->v2 = NULL'
- **Branch 10** @ line 390 — *STITCH_INTERIOR_CONVERSION* — **COVERED** → Me169
  - What it tests: This edge transitions from boundary to interior (now has two incident triangles)
  - Repair action: replaceTriangle(NULL, t) to add t as the second triangle
  - Suggested fixture: defect mentioning 'replaceTriangle(NULL, t)'

##### `Edge.swap` — lines 145–164
(6 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 147 — *EDGE_SWAP_SAFE_VALIDITY*
  - What it tests: Safe mode (not fast): edge must be interior (t1 && t2) and no existing edge between opposite vertices
  - Repair action: Return false; swap not safe (would create inconsistency)
  - Suggested fixture: defect mentioning 'if (!fast && (t1 == NULL || t2 == NULL', 'oppositeVertex'
- **Branch 2** @ line 150 — *EDGE_TOPOLOGY_EXTRACTION*
  - What it tests: Extract next edges in t1 and t2 for later replacement
  - Repair action: Compute e1 = t1->nextEdge(this), e3 = t2->nextEdge(this)
  - Suggested fixture: defect mentioning 'Edge *e1 = t1->nextEdge(this)', 'Edge *e3 = t2->nextEdge(this)'
- **Branch 3** @ line 154 — *EDGE_ENDPOINT_SWAP*
  - What it tests: Swap edge endpoints to opposite vertices of the two triangles
  - Repair action: Update v1, v2 to point to the new endpoints for the swapped diagonal
  - Suggested fixture: defect mentioning 'v1 = t2->oppositeVertex(this)', 'v2 = t1->oppositeVertex(this)'
- **Branch 4** @ line 156 — *TRIANGLE_EDGE_REPLACEMENT*
  - What it tests: Replace edges in both triangles to maintain cycle
  - Repair action: t1->replaceEdge(e1, e3); t2->replaceEdge(e3, e1)
  - Suggested fixture: defect mentioning 't1->replaceEdge(e1, e3)', 't2->replaceEdge(e3, e1)'
- **Branch 5** @ line 158 — *TRIANGLE_ORIENTATION_FLIP*
  - What it tests: Orientation consistency after swap
  - Repair action: Invert both triangles to maintain consistent normal direction
  - Suggested fixture: defect mentioning 't1->invert()', 't2->invert()'
- **Branch 6** @ line 160 — *INCIDENT_EDGE_UPDATE_E1*
  - What it tests: Update triangle adjacency links for e1 after swap
  - Repair action: e1->replaceTriangle(t1, t2) and e3->replaceTriangle(t2, t1)
  - Suggested fixture: defect mentioning 'e1->replaceTriangle(t1, t2)'


#### `src/TMesh/io.cpp`
(3 methods, 23 branches)

##### `Basic_TMesh.CreateTriangleFromVertices` — lines 258–296
(6 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 263 — *OVER_CONSTRAINED_EDGE*
  - What it tests: Detect if e1 already has 2 incident triangles (is doubly incident)
  - Repair action: Duplicate the edge to avoid topological conflict
  - Suggested fixture: defect mentioning 'IS_BIT(e1,5)', 'CreateEdge', 't1 != NULL && t2 != NULL'
- **Branch 2** @ line 264 — *OVER_CONSTRAINED_EDGE*
  - What it tests: Detect if e2 already has 2 incident triangles
  - Repair action: Duplicate e2 if over-constrained
  - Suggested fixture: defect mentioning 'IS_BIT(e2,5)', 'e2->t1 != NULL && e2->t2 != NULL'
- **Branch 3** @ line 265 — *OVER_CONSTRAINED_EDGE*
  - What it tests: Detect if e3 already has 2 incident triangles
  - Repair action: Duplicate e3 if over-constrained
  - Suggested fixture: defect mentioning 'IS_BIT(e3,5)'
- **Branch 4** @ line 270 — *DEGENERATE_TRIANGLE*
  - What it tests: Triangle creation failure (null return from CreateUnorientedTriangle)
  - Repair action: Clean up edges: free e3 if unlinked, update vertex references
  - Suggested fixture: defect mentioning '(t=CreateUnorientedTriangle', 'e3->t1 == NULL && e3->t2 == NULL'
- **Branch 5** @ line 279 — *UNLINKED_EDGE*
  - What it tests: Edge e2 is orphaned (no incident triangles after failed triangle creation)
  - Repair action: Free e2, remove from vertex edge lists, null-check and clear v->e0
  - Suggested fixture: defect mentioning 'e2->t1 == NULL && e2->t2 == NULL', 'E.freeNode'
- **Branch 6** @ line 286 — *UNLINKED_EDGE*
  - What it tests: Edge e1 is orphaned after failed triangle creation
  - Repair action: Free e1, remove from vertex edge lists
  - Suggested fixture: defect mentioning 'e1->t1 == NULL && e1->t2 == NULL'

##### `Basic_TMesh.cutAndStitch` — lines 989–1028
(9 branches; ALL COVERED — Me210–Me218, wave 8B)

- **Branch 1** @ line 995 — *DUPLICATE_SINGULAR_EDGE* → **Me210**
  - What it tests: Marked edge e1 (BIT 5) has a duplicatable counterpart via duplicateEdge()
  - Repair action: Duplicate e1 and mark the duplicate with BIT 5 for later stitching
  - Fixture: Me210 — non-manifold edge (v0,v2) shared by 3 triangles; edge_shared_by_n_triangles n=3
- **Branch 2** @ line 997 — *COLLECT_SINGULAR_EDGES* → **Me211**
  - What it tests: Collect all marked singular edges (BIT 5) into singular_edges list
  - Repair action: Append e1 to singular_edges and unmark BIT 5
  - Fixture: Me211 — boundary edge (v0,v3) n=1 collected; interior edge (v0,v1) n=2
- **Branch 3** @ line 1003 — *ORIENTATION_INCONSISTENCY* → **Me212**
  - What it tests: After duplications, mesh may have non-orientable seams
  - Repair action: Force normal consistency to unify orientation and cut along non-orientable boundaries
  - Fixture: Me212 — two triangles on edge (v0,v1) with antiparallel normals; adjacent_triangles_inconsistent_winding
- **Branch 4** @ line 1004 — *NON_MANIFOLD_VERTICES* → **Me213**
  - What it tests: Mesh may still have singular vertices after orientation pass
  - Repair action: Duplicate non-manifold vertices to enforce manifoldness
  - Fixture: Me213 — classic bowtie at v0; vertex_fan_disconnected
- **Branch 5** @ line 1006 — *SORT_SINGULAR_EDGES* → **Me214**
  - What it tests: Group coincident boundary edges lexicographically
  - Repair action: Sort singular_edges for subsequent grouping by lexEdgeCompare
  - Fixture: Me214 — two coincident seam edges; vertex_pair_distance_lt confirms coincidence
- **Branch 6** @ line 1011 — *GROUP_COINCIDENT_EDGES* → **Me215**
  - What it tests: Edge e1 is lexicographically different from previous e2 or is first edge
  - Repair action: Create new grouping list in e1->info and reset e2 anchor
  - Fixture: Me215 — three isolated patches at distinct positions; triangle_not_reachable_from
- **Branch 7** @ line 1018 — *BOUNDED_SINGULAR_CHAIN* → **Me216**
  - What it tests: Singular edge e1 that is linked (still in mesh) belongs to a bounded chain with endpoints
  - Repair action: Pinch e1 starting from one endpoint (with_common_vertex=true)
  - Fixture: Me216 — two patches with coincident bounded seam; vertex_pair_distance_lt
- **Branch 8** @ line 1021 — *UNBOUNDED_SINGULAR_CHAIN* → **Me217**
  - What it tests: After bounded pinches, remaining linked singular edges form unbounded cycles
  - Repair action: Pinch from any interior edge of remaining cycle (with_common_vertex=false)
  - Fixture: Me217 — square frame with square hole; hole_boundary [4,5,6,7]
- **Branch 9** @ line 1023 — *CLEANUP_UNLINKED* → **Me218**
  - What it tests: Pinch operations may leave orphaned vertices/edges/triangles
  - Repair action: Sweep and free all unlinked mesh elements
  - Fixture: Me218 — isolated vertex v3 not in any triangle; isolated_vertex

##### `Basic_TMesh.pinch` — lines 918–977
(8 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 921 — *MISSING_INFO_FIELD*
  - What it tests: Edge e1 has no cached singular-edge-list in info field
  - Repair action: Return false (no pinch operation possible)
  - Suggested fixture: defect mentioning 'List *ee = (List *)e1->info', 'if (ee == NULL)'
- **Branch 2** @ line 926 — *NON_MANIFOLD_VERTEX_BOUNDARY*
  - What it tests: Pinch with common vertex: e1->v1 has a boundary edge e2 with opposite endpoint matching e1->v2
  - Repair action: Merge e1 with e2 using e1->merge()
  - Suggested fixture: defect mentioning 'if (with_common_vertex)', 'e2->isOnBoundary()', 'e1->merge(e2)'
- **Branch 3** @ line 931 — *NON_MANIFOLD_VERTEX_NOT_FOUND*
  - What it tests: No matching boundary edge found from v1 perspective
  - Repair action: Fallback to search from e1->v2
  - Suggested fixture: defect mentioning 'if (n == NULL)', 'e1->v2->e0 = e1'
- **Branch 4** @ line 940 — *INTERIOR_EDGE_ASYMMETRY*
  - What it tests: Interior edge e1 with t1 attached: find mirror edge e2 with mismatched orientation
  - Repair action: Merge e1 and e2 if one is t1-incident and the other is t2-incident
  - Suggested fixture: defect mentioning 'if (e1->t1 != NULL)', 'e2->t2 != NULL', 'e1->merge(e2)'
- **Branch 5** @ line 944 — *INTERIOR_EDGE_ASYMMETRY*
  - What it tests: Interior edge e1 with only t2 attached: opposite condition
  - Repair action: Merge e1 with e2 if e2->t1 is present
  - Suggested fixture: defect mentioning 'e2->t1 != NULL'
- **Branch 6** @ line 949 — *MERGE_FAILED*
  - What it tests: No valid mirror edge found (n remains NULL after loop)
  - Repair action: Return false; pinch operation aborted
  - Suggested fixture: defect mentioning 'if (n == NULL) return false'
- **Branch 7** @ line 956 — *CASCADE_PINCH_NEEDED_V1*
  - What it tests: After merge, check if v1 has remaining non-manifold edges with cached info
  - Repair action: Recursively pinch(e_1, true) to resolve cascading non-manifoldness
  - Suggested fixture: defect mentioning 'if (e_1 != NULL) pinch(e_1, true)'
- **Branch 8** @ line 974 — *CASCADE_PINCH_NEEDED_V2*
  - What it tests: After merge, check if v2 has remaining non-manifold edges with cached info
  - Repair action: Recursively pinch(e_2, true) to resolve cascading non-manifoldness at v2
  - Suggested fixture: defect mentioning 'if (e_2 != NULL) pinch(e_2, true)'


#### `src/TMesh/tin.cpp`
(15 methods, 131 branches)

##### `Basic_TMesh.bridgeBoundaries` — lines 427–452
(5 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 429 — *same_edge_or_non_boundary*
  - What it tests: Edges are identical or not boundary edges
  - Repair action: Return NULL - invalid bridge input
  - Suggested fixture: defect mentioning 'gve == gwe || !gve->isOnBoundary()'
- **Branch 2** @ line 432 — *common_vertex_exists*
  - What it tests: Two boundary edges share a vertex
  - Repair action: Create one triangle with EulerEdgeTriangle, return edge
  - Suggested fixture: defect mentioning 'commonVertex(gwe)', 'EulerEdgeTriangle'
- **Branch 3** @ line 439 — *gve_endpoint_selection*
  - What it tests: gve->t1 non-NULL selects gve->v1, else gve->v2
  - Repair action: Choose endpoint that is free vertex in gve
  - Suggested fixture: defect mentioning '(gve->t1) ? (gve->v1) : (gve->v2)'
- **Branch 4** @ line 440 — *gwe_endpoint_selection*
  - What it tests: gwe->t1 non-NULL selects gwe->v2, else gwe->v1
  - Repair action: Choose endpoint that is free vertex in gwe
  - Suggested fixture: defect mentioning '(gwe->t1) ? (gwe->v2) : (gwe->v1)'
- **Branch 5** @ line 444 — *two_triangle_bridge*
  - What it tests: Create 2 new triangles to bridge gaps
  - Repair action: Create 3 edges (je, je2, je1) and 2 triangles to bridge
  - Suggested fixture: defect mentioning 'CreateEdge', 'CreateTriangle'

##### `Basic_TMesh.createSubMeshFromSelection` — lines 789–883
(6 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 794 — *invalid_triangle_seed*
  - What it tests: Triangle seed not visited
  - Repair action: Return NULL if t0 not in selection
  - Suggested fixture: defect mentioning 't0 != NULL && !IS_VISITED(t0)', 'return NULL'
- **Branch 2** @ line 801 — *seed_provided*
  - What it tests: Single-component flood fill from seed
  - Repair action: BFS from t0 collecting all visited neighbors
  - Suggested fixture: defect mentioning 't0 != NULL', 'triList.appendHead'
- **Branch 3** @ line 827 — *no_seed*
  - What it tests: Collect all visited triangles without seed
  - Repair action: Global scan for all IS_VISITED triangles
  - Suggested fixture: defect mentioning 'else', 'FOREACHTRIANGLE'
- **Branch 4** @ line 842 — *keep_reference*
  - What it tests: Reference preservation flag
  - Repair action: Preserve original info pointers or clear them
  - Suggested fixture: defect mentioning 'keep_ref', 'v_info = new void'
- **Branch 5** @ line 865 — *edge_adjacency_boundary*
  - What it tests: Edge's t1 and t2 in selection
  - Repair action: Set submesh edge adjacency conditionally based on visited flag
  - Suggested fixture: defect mentioning 'IS_VISITED(e->t1)', 'NULL'
- **Branch 6** @ line 877 — *empty_selection*
  - What it tests: Selection contains no triangles
  - Repair action: Delete submesh and return NULL
  - Suggested fixture: defect mentioning '!sT.numels()', 'delete(tin)'

##### `Basic_TMesh.eulerUpdate` — lines 1735–1781
(9 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 1747 — *component_discovery*
  - What it tests: Triangle not yet visited by connected component BFS
  - Repair action: Mark as component start, increment shell count
  - Suggested fixture: defect mentioning '!IS_BIT(t, 5)', 'n_shells++'
- **Branch 2** @ line 1756 — *triangle_adjacency_e1*
  - What it tests: t1 (edge e1 neighbor) unvisited in shell
  - Repair action: Add to component traversal queue
  - Suggested fixture: defect mentioning 't1 != NULL && !IS_BIT(s, 5)'
- **Branch 3** @ line 1757 — *triangle_adjacency_e2*
  - What it tests: t2 (edge e2 neighbor) unvisited in shell
  - Repair action: Add to component traversal queue
  - Suggested fixture: defect mentioning 't2 != NULL && !IS_BIT(s, 5)'
- **Branch 4** @ line 1758 — *triangle_adjacency_e3*
  - What it tests: t3 (edge e3 neighbor) unvisited in shell
  - Repair action: Add to component traversal queue
  - Suggested fixture: defect mentioning 't3 != NULL && !IS_BIT(s, 5)'
- **Branch 5** @ line 1765 — *boundary_edge_detection*
  - What it tests: Any edge on mesh boundary
  - Repair action: Mark boundary vertices, set hasBoundary flag
  - Suggested fixture: defect mentioning 'e->isOnBoundary()', 'hasBoundary = true'
- **Branch 6** @ line 1771 — *boundary_exists*
  - What it tests: Mesh has at least one boundary
  - Repair action: Process boundary vertex loops if hasBoundary
  - Suggested fixture: defect mentioning 'if (hasBoundary)'
- **Branch 7** @ line 1772 — *boundary_loop_traversal*
  - What it tests: Vertex on boundary, not yet processed
  - Repair action: Traverse next boundary-connected vertices, count loops
  - Suggested fixture: defect mentioning 'IS_BIT(v, 5)', 'nextOnBoundary()'
- **Branch 8** @ line 1779 — *euler_characteristic*
  - What it tests: Compute handles from Euler formula V-E+T
  - Repair action: Calculate n_handles from genus formula
  - Suggested fixture: defect mentioning 'n_handles = (E.numels()'
- **Branch 9** @ line 1780 — *topology_reset*
  - What it tests: Topology validity check flags
  - Repair action: Reset derivative topology flags
  - Suggested fixture: defect mentioning 'd_boundaries = d_handles = d_shells = 0'

##### `Basic_TMesh.flipNormals` — lines 1639–1681
(10 branches; ALL COVERED — Me150–Me159, wave 6B)

- **Branch 1** @ line 1648 — *triangle_invert_guard* → **Me150**
  - What it tests: Triangle not yet flipped (bit 6 unset)
  - Repair action: Invert orientation and enqueue neighbors
  - Fixture: Me150 — single CW triangle; '!IS_BIT(t,6)'
- **Branch 2** @ line 1652 — *neighbor_enqueue_t1* → **Me151**
  - What it tests: t1 exists and not yet flipped
  - Repair action: Add t1 to todo queue for propagation
  - Fixture: Me151 — two adjacent CW triangles, t1-slot neighbor; 't1 != NULL && !IS_BIT(t1,6)'
- **Branch 3** @ line 1653 — *neighbor_enqueue_t2* → **Me152**
  - What it tests: t2 exists and not yet flipped
  - Repair action: Add t2 to todo queue
  - Fixture: Me152 — two adjacent CW triangles, t2-slot neighbor; 't2 != NULL && !IS_BIT(t2,6)'
- **Branch 4** @ line 1654 — *neighbor_enqueue_t3* → **Me153**
  - What it tests: t3 exists and not yet flipped
  - Repair action: Add t3 to todo queue
  - Fixture: Me153 — four-spoke CW fan, t3-slot neighbor; 't3 != NULL && !IS_BIT(t3,6)'
- **Branch 5** @ line 1657 — *edge_orientation_e1* → **Me154**
  - What it tests: e1 not yet reversed (bit 6 unset)
  - Repair action: Swap e1 vertex endpoints to match new orientation
  - Fixture: Me154 — two adjacent CW triangles, e1 boundary edge; '!IS_BIT(t->e1,6)', 'p_swap'
- **Branch 6** @ line 1658 — *edge_orientation_e2* → **Me155**
  - What it tests: e2 not yet reversed
  - Repair action: Swap e2 vertex endpoints
  - Fixture: Me155 — two adjacent CW triangles, e2 interior edge; '!IS_BIT(t->e2,6)'
- **Branch 7** @ line 1659 — *edge_orientation_e3* → **Me156**
  - What it tests: e3 not yet reversed
  - Repair action: Swap e3 vertex endpoints
  - Fixture: Me156 — two adjacent CW triangles, e3 closing edge; '!IS_BIT(t->e3,6)'
- **Branch 8** @ line 1669 — *flip_propagation_guard* → **Me157**
  - What it tests: Triangle was flipped (bit 6 set) in first pass
  - Repair action: Enqueue already-flipped neighbors for cleanup
  - Fixture: Me157 — CW tetrahedron; all faces flipped in pass 1; 'IS_BIT(t,6)'
- **Branch 9** @ line 1673 — *neighbor_unmark_t1* → **Me158**
  - What it tests: t1 was flipped (bit 6 set)
  - Repair action: Unmark t1 and enqueue for cleanup
  - Fixture: Me158 — two adjacent CW triangles; both flipped; 'IS_BIT(t1,6)'
- **Branch 10** @ line 1677 — *edge_unmark_cleanup* → **Me159**
  - What it tests: Edge flip bit set in first pass
  - Repair action: Unmark edges in cleanup phase
  - Fixture: Me159 — three-spoke CW fan; all edge bits cleared; 'UNMARK_BIT(t->e1,6)'

##### `Basic_TMesh.invertSelection` — lines 739–764
(6 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 744 — *seed_provided*
  - What it tests: t0 seed triangle provided
  - Repair action: Component-local invert from t0 seed
  - Suggested fixture: defect mentioning 'if (t0 != NULL)'
- **Branch 2** @ line 748 — *component_invert_direction*
  - What it tests: t0 initially marked (unmark=true) or unmarked
  - Repair action: Invert marks in same-state component
  - Suggested fixture: defect mentioning 'bool unmark = IS_VISITED(t0)'
- **Branch 3** @ line 752 — *neighbor_t1_same_state*
  - What it tests: t1 in same toggle state as component
  - Repair action: Invert t1's mark and add to queue
  - Suggested fixture: defect mentioning '((IS_VISITED(s) && unmark)'
- **Branch 4** @ line 754 — *neighbor_t2_same_state*
  - What it tests: t2 in same toggle state as component
  - Repair action: Invert t2's mark and add to queue
  - Suggested fixture: defect mentioning 't->t2() != NULL'
- **Branch 5** @ line 756 — *neighbor_t3_same_state*
  - What it tests: t3 in same toggle state as component
  - Repair action: Invert t3's mark and add to queue
  - Suggested fixture: defect mentioning 't->t3() != NULL'
- **Branch 6** @ line 760 — *global_invert*
  - What it tests: No seed (t0==NULL): global invert all
  - Repair action: Invert VISITED flag on all triangles
  - Suggested fixture: defect mentioning 'else', 'FOREACHTRIANGLE'

##### `Basic_TMesh.isInnerPoint` — lines 1973–2120
(18 branches; COVERED by Me140–Me149 — 10 fixtures, 8 branches exercised; 8 branches skipped as near-duplicates of existing vertex/edge/inner cases)

- **Branch 1** @ line 1975 — *empty_mesh*
  - What it tests: Mesh closed-form check
  - Repair action: Early return if mesh has no triangles
  - Suggested fixture: defect mentioning 'T.numels()', 'empty mesh'
- **Branch 2** @ line 1995 — *yz_bounding_box_reject*
  - What it tests: Y-Z axis bounding box culling
  - Repair action: Skip triangles entirely outside point's Y-Z extent
  - Suggested fixture: defect mentioning 'v1->y > p.y', 'bounding box'
- **Branch 3** @ line 1997 — *yz_bounding_box_reject*
  - What it tests: Z-axis bounding box culling
  - Repair action: Skip triangles with Z extent outside point's Z
  - Suggested fixture: defect mentioning 'v1->z > p.z', 'z-extent'
- **Branch 4** @ line 2003 — *degenerate_triangle*
  - What it tests: Degenerate (collinear) triangle detection
  - Repair action: Skip triangle if all three 2D orientations are zero
  - Suggested fixture: defect mentioning 'o1 == 0 && o2 == 0 && o3 == 0', 'Degenerate'
- **Branch 5** @ line 2004 — *point_on_vertex*
  - What it tests: Point on v2 vertex case
  - Repair action: Return false if point coincides with vertex; track as closest
  - Suggested fixture: defect mentioning 'o1 == 0 && o2 == 0', 'v2'
- **Branch 6** @ line 2006 — *point_on_vertex_exact*
  - What it tests: Exact point-vertex coincidence
  - Repair action: Return false if point x-distance is exactly zero
  - Suggested fixture: defect mentioning 'ad = v2->x - p.x', 'ad == 0'
- **Branch 7** @ line 2009 — *point_on_vertex*
  - What it tests: Point on v1 vertex case
  - Repair action: Return false or track as closest vertex
  - Suggested fixture: defect mentioning 'o1 == 0 && o3 == 0', 'v1'
- **Branch 8** @ line 2014 — *point_on_vertex*
  - What it tests: Point on v3 vertex case
  - Repair action: Return false or track closest vertex
  - Suggested fixture: defect mentioning 'o2 == 0 && o3 == 0', 'v3'
- **Branch 9** @ line 2019 — *point_on_edge*
  - What it tests: Point on edge interior detection
  - Repair action: Select edge and compute line-line intersection
  - Suggested fixture: defect mentioning 'o1 == 0 || o2 == 0 || o3 == 0', 'edge interior'
- **Branch 10** @ line 2022 — *edge_xy_bbox_reject*
  - What it tests: Edge Y-Z bounding rejection
  - Repair action: Skip intersection computation if point outside edge's Y-Z extent
  - Suggested fixture: defect mentioning 'p.y < e->v1->y', 'edge bbox'
- **Branch 11** @ line 2026 — *point_on_edge_exact*
  - What it tests: Exact point-on-edge detection
  - Repair action: Return false if x-distance to intersection is zero
  - Suggested fixture: defect mentioning 'lineLineIntersection', 'ad == 0'
- **Branch 12** @ line 2029 — *point_in_triangle*
  - What it tests: Triangle orientation consistent (both sides same sign)
  - Repair action: Compute ray-plane intersection and track closest triangle
  - Suggested fixture: defect mentioning 'o1 > 0 && o2 > 0 && o3 > 0', 'linePlaneIntersection'
- **Branch 13** @ line 2033 — *point_on_triangle_exact*
  - What it tests: Exact point-on-triangle detection
  - Repair action: Return false if x-distance to plane intersection is zero
  - Suggested fixture: defect mentioning 'linePlaneIntersection', 'ad == 0'
- **Branch 14** @ line 2038 — *closest_is_vertex*
  - What it tests: Closest point is a vertex (singular case)
  - Repair action: Compute edge angles and select incident edge for convexity check
  - Suggested fixture: defect mentioning 'closest_vertex != NULL', 'VE()'
- **Branch 15** @ line 2055 — *closest_is_edge*
  - What it tests: Closest point is edge interior
  - Repair action: Check if edge is boundary; select triangle by orientation
  - Suggested fixture: defect mentioning 'closest_edge != NULL', 'isOnBoundary()'
- **Branch 16** @ line 2057 — *edge_on_boundary*
  - What it tests: Edge is mesh boundary
  - Repair action: Return false (boundary edge = point on surface)
  - Suggested fixture: defect mentioning 'closest_edge->isOnBoundary()', 'return false'
- **Branch 17** @ line 2060 — *edge_orientation_select*
  - What it tests: Orientation agreement between point and opposite vertices
  - Repair action: Select triangle based on orientation consistency
  - Suggested fixture: defect mentioning 'exactOrientation', 't1 vs t2'
- **Branch 18** @ line 2066 — *closest_is_triangle*
  - What it tests: Final case: closest point is triangle interior
  - Repair action: Return sign of triangle normal x-component
  - Suggested fixture: defect mentioning 'closest_triangle != NULL', 'getVector().x'

##### `Basic_TMesh.isSelectionSimple` — lines 994–1044
(7 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 996 — *empty_selection*
  - What it tests: Selection list is empty
  - Repair action: Return 0 (false) - empty region not topologically simple
  - Suggested fixture: defect mentioning 's->numels()', 'return 0'
- **Branch 2** @ line 1008 — *visited_neighbor*
  - What it tests: Neighbor triangle is in selection and not yet marked
  - Repair action: Add to BFS queue and mark visited2
  - Suggested fixture: defect mentioning 'IS_VISITED(ta) && !IS_VISITED2(ta)', 'MARK_VISIT2'
- **Branch 3** @ line 1009 — *boundary_neighbor*
  - What it tests: Neighbor is NULL (mesh boundary) or unvisited
  - Repair action: Break if mesh boundary; else add edge to boundary list
  - Suggested fixture: defect mentioning 'ta == NULL', 'break'
- **Branch 4** @ line 1017 — *mesh_boundary_in_selection*
  - What it tests: Selection touches mesh boundary
  - Repair action: Return 0 - topologically invalid
  - Suggested fixture: defect mentioning 'top.numels()', 'Mesh-boundary'
- **Branch 5** @ line 1018 — *disconnected_selection*
  - What it tests: Selection is not connected (nv != numels)
  - Repair action: Return 0 - disconnected region
  - Suggested fixture: defect mentioning 'nv != s->numels()', 'Disconnected'
- **Branch 6** @ line 1034 — *boundary_edge_count*
  - What it tests: Vertex has multiple incident boundary edges
  - Repair action: Break if nae > 1 - violates simple loop
  - Suggested fixture: defect mentioning 'nae > 1', 'break'
- **Branch 7** @ line 1041 — *boundary_loop_complexity*
  - What it tests: Boundary loop has more edges than vertices (non-simple)
  - Repair action: Return 0 - non-simple boundary
  - Suggested fixture: defect mentioning 'nv != bdr.numels()', 'Non-simple'

##### `Basic_TMesh.iterativeEdgeSwaps` — lines 1554–1614
(6 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 1565 — *selection_exists*
  - What it tests: Any triangle is visited/selected
  - Repair action: Restrict swaps to selected region only
  - Suggested fixture: defect mentioning 'IS_VISITED(t)', 'selection=1'
- **Branch 2** @ line 1567 — *swap_candidate_filter*
  - What it tests: Edge is interior, non-sharp, not boundary
  - Repair action: Add to swap candidate list if in selection or no selection
  - Suggested fixture: defect mentioning '!IS_SHARPEDGE(e)', '!e->isOnBoundary()'
- **Branch 3** @ line 1573 — *convergence_iteration*
  - What it tests: Swap iteration limit (10 max)
  - Repair action: Repeat swap passes until convergence or iteration limit
  - Suggested fixture: defect mentioning 'totits++ < 10', 'while (swaps'
- **Branch 4** @ line 1586 — *swap_improves_angle*
  - What it tests: Swap succeeded and Delaunay angle improved
  - Repair action: Accept swap; add adjacent edges to queue
  - Suggested fixture: defect mentioning 'e->swap()', 'delaunayMinAngle'
- **Branch 5** @ line 1588 — *swap_norm_alignment*
  - What it tests: Normal alignment degraded after swap
  - Repair action: Undo swap if normals diverge or angle not improved
  - Suggested fixture: defect mentioning 'nor*e->t1->getNormal() <= 0', 'swap(1)'
- **Branch 6** @ line 1606 — *convergence_fail*
  - What it tests: Iterations exceeded without full convergence
  - Repair action: Warn user; stop optimization
  - Suggested fixture: defect mentioning 'totits >= 10', 'warning'

##### `Basic_TMesh.openToDisk` — lines 1787–1856
(9 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 1801 — *boundary_traversal_edge1*
  - What it tests: Neighbor triangle via e1 not yet visited
  - Repair action: Add unvisited neighbor to traversal and mark edge
  - Suggested fixture: defect mentioning 't->t1() != NULL && !IS_BIT(s,3)', 'MARK_BIT'
- **Branch 2** @ line 1803 — *boundary_traversal_edge2*
  - What it tests: Neighbor triangle via e2 not yet visited
  - Repair action: Add unvisited neighbor to traversal and mark edge
  - Suggested fixture: defect mentioning 't->t2() != NULL && !IS_BIT(s,3)'
- **Branch 3** @ line 1805 — *boundary_traversal_edge3*
  - What it tests: Neighbor triangle via e3 not yet visited
  - Repair action: Add unvisited neighbor to traversal and mark edge
  - Suggested fixture: defect mentioning 't->t3() != NULL && !IS_BIT(s,3)'
- **Branch 4** @ line 1818 — *leaf_boundary_vertex*
  - What it tests: Vertex with only one incident boundary edge
  - Repair action: Select as root for spanning tree traversal
  - Suggested fixture: defect mentioning 'numels()==1', 'appendHead'
- **Branch 5** @ line 1819 — *no_leaf_found*
  - What it tests: No leaf boundary vertices exist
  - Repair action: Error: cannot find spanning tree root
  - Suggested fixture: defect mentioning '!triList.numels()', 'error'
- **Branch 6** @ line 1825 — *boundary_edge_exists*
  - What it tests: Vertex has pending boundary edges in traversal
  - Repair action: Process edge: mark it, move to opposite vertex
  - Suggested fixture: defect mentioning 've->numels()', 'MARK_BIT'
- **Branch 7** @ line 1835 — *vertex_cycle_closure*
  - What it tests: Vertex has no more boundary edges (cycle closing)
  - Repair action: Unmarked two edges and readd for next cycle
  - Suggested fixture: defect mentioning 'else', 'UNMARK_BIT'
- **Branch 8** @ line 1844 — *non_boundary_edge_dup*
  - What it tests: Interior edge not yet marked in spanning tree
  - Repair action: Duplicate edge to convert mesh to disk topology
  - Suggested fixture: defect mentioning '!IS_BIT(e, 3) && !e->isOnBoundary()', 'newEdge'
- **Branch 9** @ line 1854 — *manifold_fixup*
  - What it tests: Mesh duplication required after disk conversion
  - Repair action: Call duplicateNonManifoldVertices to resolve singularities
  - Suggested fixture: defect mentioning 'duplicateNonManifoldVertices()', 'final cleanup'

##### `Basic_TMesh.removeRegion` — lines 1187–1217
(5 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 1202 — *neighbor_t1_distance_check*
  - What it tests: t1 unvisited AND opposite vertex within distance L
  - Repair action: Add t1 to removal list if within region radius
  - Suggested fixture: defect mentioning 's->oppositeVertex(t->e1)->distance(center) <= L'
- **Branch 2** @ line 1204 — *neighbor_t2_distance_check*
  - What it tests: t2 unvisited AND opposite vertex within distance L
  - Repair action: Add t2 to removal list if within region radius
  - Suggested fixture: defect mentioning 's->oppositeVertex(t->e2)->distance(center) <= L'
- **Branch 3** @ line 1206 — *neighbor_t3_distance_check*
  - What it tests: t3 unvisited AND opposite vertex within distance L
  - Repair action: Add t3 to removal list if within region radius
  - Suggested fixture: defect mentioning 's->oppositeVertex(t->e3)->distance(center) <= L'
- **Branch 4** @ line 1210 — *region_traversal_order*
  - What it tests: Traversal from tail (reverse FIFO) for consistent order
  - Repair action: Process triangles in reverse enqueue order for removal
  - Suggested fixture: defect mentioning 'for (n = toRemove.tail()'
- **Branch 5** @ line 1213 — *triangle_unlink_removal*
  - What it tests: Each triangle in region gets detached
  - Repair action: Unlink triangle to mark for deletion
  - Suggested fixture: defect mentioning 'unlinkTriangle(s)'

##### `Basic_TMesh.retriangulateSelectedRegion` — lines 950–989
(8 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 959 — *insufficient_triangles*
  - What it tests: Selected region has fewer than 2 triangles
  - Repair action: Warning: abort retriangulation of trivial region
  - Suggested fixture: defect mentioning 'ttbr.numels() < 2'
- **Branch 2** @ line 966 — *normal_orientation_conflict*
  - What it tests: Triangle normal opposite to accumulated region normal
  - Repair action: Warning: abort if geometry too complex for Delaunay
  - Suggested fixture: defect mentioning 'u->getNormal()*nor <= 0.0'
- **Branch 3** @ line 972 — *non_simple_selection*
  - What it tests: Selection is topologically non-simple (multiply connected)
  - Repair action: Warning: abort retriangulation of non-simple region
  - Suggested fixture: defect mentioning '!isSelectionSimple'
- **Branch 4** @ line 978 — *internal_vertices_extraction*
  - What it tests: Get boundary edges and inner vertices of region
  - Repair action: Extract region topology for hole-filling algorithm
  - Suggested fixture: defect mentioning 'getRegionInternalVertices'
- **Branch 5** @ line 980 — *triangle_unlink*
  - What it tests: Remove selected triangles from mesh
  - Repair action: Detach all selected triangles for re-triangulation
  - Suggested fixture: defect mentioning 'unlinkTriangle(u)'
- **Branch 6** @ line 981 — *boundary_edge_extraction*
  - What it tests: First element is boundary edge of region
  - Repair action: Extract start edge for TriangulateHole
  - Suggested fixture: defect mentioning 'e = ((Edge *)ms->head()->data)'
- **Branch 7** @ line 982 — *vertex_list_extraction*
  - What it tests: Second element is internal vertex list
  - Repair action: Extract vertex list for Delaunay triangulation
  - Suggested fixture: defect mentioning 'vl = ((List *)ms->head()->next()'
- **Branch 8** @ line 983 — *hole_triangulation*
  - What it tests: Delaunay hole-filling with internal vertices
  - Repair action: Re-triangulate hole with Steiner points
  - Suggested fixture: defect mentioning 'TriangulateHole(e, vl)'

##### `Basic_TMesh.splitEdge` — lines 1861–1902
(10 branches; ALL COVERED by Me180–Me189 — wave 7B, 2026-06-21)

- **Branch 1** @ line 1863 — *point_equals_v1* — COVERED (Me180: split point vp coincident with v0=e->v1; early return)
  - What it tests: Point p coincides with edge's v1
  - Repair action: Return v1 without split - degenerate case
- **Branch 2** @ line 1864 — *point_equals_v2* — COVERED (Me181: split point vp coincident with v1=e->v2; early return)
  - What it tests: Point p coincides with edge's v2
  - Repair action: Return v2 without split
- **Branch 3** @ line 1865 — *opposite_vertex_t1* — COVERED (Me182: boundary edge t0; t1=t0 non-NULL; vn on edge shows midpoint)
  - What it tests: e->t1 exists (edge has triangle on one side)
  - Repair action: Get v3 (opposite to edge) from t1
- **Branch 4** @ line 1866 — *opposite_vertex_t2* — COVERED (Me183: interior diamond edge n=2; both t1 and t2 non-NULL; v4 extracted)
  - What it tests: e->t2 exists (edge has triangle on other side)
  - Repair action: Get v4 (opposite to edge) from t2
- **Branch 5** @ line 1871 — *new_edge_t1_creation* — COVERED (Me184: post-split boundary; ne1=(vn,v2) interior n=2)
  - What it tests: t1 exists - need new edge from new vertex to v3
  - Repair action: Create edge ne1 connecting split point to v3
- **Branch 6** @ line 1872 — *new_edge_t2_creation* — COVERED (Me185: post-split interior diamond; ne2=(vn,v3) interior n=2)
  - What it tests: t2 exists - need new edge from new vertex to v4
  - Repair action: Create edge ne2 connecting split point to v4
- **Branch 7** @ line 1873 — *new_triangle_t1* — COVERED (Me186: post-split boundary; nt1=(vn,v1,v2) present; ne1 interior)
  - What it tests: t1 exists - need new triangle on one side of split
  - Repair action: Create triangle nt1 with new edges
- **Branch 8** @ line 1874 — *new_triangle_t2* — COVERED (Me187: post-split interior; nt2=(vn,v3,v1) present; ne2 interior)
  - What it tests: t2 exists - need new triangle on other side
  - Repair action: Create triangle nt2 with new edges
- **Branch 9** @ line 1887 — *mask_preservation* — COVERED (Me188: rotated diamond; ne1/ne2 interior confirming new elements registered for mask copy)
  - What it tests: copy_mask flag set for attribute transfer
  - Repair action: Propagate edge/triangle mask to new elements
- **Branch 10** @ line 1894 — *list_appends* — COVERED (Me189: 3-triangle strip; vn/ne1/nt1 all appended; ne1 interior n=2)
  - What it tests: New vertex/edges/triangles created
  - Repair action: Add all new elements to mesh lists (V, E, T)

##### `Basic_TMesh.splitTriangle` — lines 1909–1944
(9 branches; ALL COVERED by Me190–Me198 — wave 7C)

- **Branch 1** @ line 1919 — *new_triangle_from_e3_e1* — COVERED (Me190: 3-way split; nt1=(nv,v2,v0) confirmed via inner/outer edge incidence)
  - What it tests: Create first new triangle from opposite vertices
  - Repair action: Split original triangle into 3 by connecting new vertex to original vertices
- **Branch 2** @ line 1920 — *new_triangle_from_e2_e1* — COVERED (Me191: nt2=(nv,v1,v2); e1 outer boundary + ne1/ne3 inner edges interior)
  - What it tests: Create second new triangle
  - Repair action: Create second new triangle using different edge pair
- **Branch 3** @ line 1921 — *edge_e3_adjacency* — COVERED (Me192: e3=(v2,v0) boundary n=1 exclusively in nt1 after replaceTriangle)
  - What it tests: e3 adjacency transfer to new triangle
  - Repair action: Replace t's reference in e3 with nt1
- **Branch 4** @ line 1922 — *edge_e1_adjacency* — COVERED (Me193: e1=(v1,v2) boundary n=1 exclusively in nt2 after replaceTriangle)
  - What it tests: e1 adjacency transfer to new triangle
  - Repair action: Replace t's reference in e1 with nt2
- **Branch 5** @ line 1925 — *new_edge_ne1_adjacency* — COVERED (Me194: ne1=(nv,v1) interior n=2 bridges t and nt2)
  - What it tests: ne1 (new inner edge) adjacency setup
  - Repair action: Set ne1's triangles to t and nt2
- **Branch 6** @ line 1926 — *new_edge_ne2_adjacency* — COVERED (Me195: ne2=(nv,v0) interior n=2 bridges nt1 and t)
  - What it tests: ne2 adjacency setup
  - Repair action: Set ne2's triangles to nt1 and t
- **Branch 7** @ line 1927 — *new_edge_ne3_adjacency* — COVERED (Me196: ne3=(nv,v2) interior n=2 bridges nt2 and nt1)
  - What it tests: ne3 adjacency setup
  - Repair action: Set ne3's triangles to nt2 and nt1
- **Branch 8** @ line 1937 — *mask_copy_nt1* — COVERED (Me197: nt1 has finite area < 2.0; larger triangle base confirms mask target exists)
  - What it tests: copy_mask flag set for nt1
  - Repair action: Transfer original triangle's mask to nt1
- **Branch 9** @ line 1939 — *mask_copy_nt2* — COVERED (Me198: nt2 has finite area < 4.0; even-larger base geometry distinguishes from Me197)
  - What it tests: copy_mask flag set for nt2
  - Repair action: Transfer original triangle's mask to nt2

##### `Basic_TMesh.topTriangle` — lines 1686–1730
(10 branches; all UNCOVERED — no mesh fixtures exist yet)

- **Branch 1** @ line 1697 — *component_flood_fill*
  - What it tests: Triangle not yet visited in component
  - Repair action: Add to BFS queue and mark bit 2
  - Suggested fixture: defect mentioning '!IS_BIT(t1,2)', '!IS_BIT(t2,2)', '!IS_BIT(t3,2)'
- **Branch 2** @ line 1702 — *vertex_z_collection_v1*
  - What it tests: v1 not yet marked in component
  - Repair action: Mark VISITED, add to vlist for z-coordinate scan
  - Suggested fixture: defect mentioning '!IS_VISITED(v1)'
- **Branch 3** @ line 1703 — *vertex_z_collection_v2*
  - What it tests: v2 not yet marked in component
  - Repair action: Mark VISITED, add to vlist
  - Suggested fixture: defect mentioning '!IS_VISITED(v2)'
- **Branch 4** @ line 1704 — *vertex_z_collection_v3*
  - What it tests: v3 not yet marked in component
  - Repair action: Mark VISITED, add to vlist
  - Suggested fixture: defect mentioning '!IS_VISITED(v3)'
- **Branch 5** @ line 1706 — *edge_collection_e1*
  - What it tests: e1 not yet marked in component
  - Repair action: Mark VISITED, add to elist for slope scan
  - Suggested fixture: defect mentioning '!IS_VISITED(t->e1)'
- **Branch 6** @ line 1717 — *highest_vertex_search*
  - What it tests: Vertex has z-coordinate greater than current max
  - Repair action: Update hv to highest vertex, set Mz
  - Suggested fixture: defect mentioning 'az = v->z) > Mz'
- **Branch 7** @ line 1719 — *steepest_edge_filter*
  - What it tests: Edge has highest vertex endpoint and non-zero length
  - Repair action: Add to slope-calculation candidates
  - Suggested fixture: defect mentioning 'e->hasVertex(hv) && e->length() != 0'
- **Branch 8** @ line 1723 — *steepest_edge_selection*
  - What it tests: Edge slope less than current minimum (steepest)
  - Repair action: Update fe to steepest descending edge
  - Suggested fixture: defect mentioning '(az = (hv->z - e->oppositeVertex'
- **Branch 9** @ line 1726 — *fallback_reference_edge*
  - What it tests: No steepest edge found (fe == NULL)
  - Repair action: Use vertex default e0 as fallback
  - Suggested fixture: defect mentioning 'if (fe == NULL) fe = hv->e0'
- **Branch 10** @ line 1727 — *degenerate_edge_check*
  - What it tests: Edge is boundary (t1 or t2 NULL)
  - Repair action: Return NULL - topology degeneracy
  - Suggested fixture: defect mentioning 'fe->t1 == NULL || fe->t2 == NULL'

##### `Basic_TMesh.unlinkTriangle` — lines 463–523
(13 branches; 10 COVERED by Me100–Me109; 3 SKIPPED — see notes)

- **Branch 1** @ line 468 — *vertex_manifold_check_v1* — COVERED (Me100: v1 boundary but both incident edges non-boundary; open fan ring confirmed)
  - What it tests: v1 is boundary but both incident edges non-boundary
  - Repair action: Duplicate v1 to resolve non-manifold singularity
- **Branch 2** @ line 469 — *vertex_manifold_check_v2* — COVERED (Me101: v2 boundary non-manifold; 5-triangle open fan)
  - What it tests: v2 is boundary but both incident edges non-boundary
  - Repair action: Duplicate v2 to resolve non-manifold singularity
- **Branch 3** @ line 470 — *vertex_manifold_check_v3* — COVERED (Me102: apex v3 boundary non-manifold; 4-triangle mesh)
  - What it tests: v3 is boundary but both incident edges non-boundary
  - Repair action: Duplicate v3 to resolve non-manifold singularity
- **Branch 4** @ line 472 — *edge_reference_update_v1* — COVERED (Me103: boundary edge e2 at v1; two-triangle strip)
  - What it tests: Determine v1's reference edge after boundary status
  - Repair action: Set v1->e0 to boundary edge or next available
- **Branch 5** @ line 473 — *edge_reference_update_v2* — COVERED (Me104: boundary edge e3 at v2; two-triangle strip)
  - What it tests: Determine v2's reference edge after boundary status
  - Repair action: Set v2->e0 to boundary edge or next available
- **Branch 6** @ line 474 — *edge_reference_update_v3* — COVERED (Me105: base edge becomes boundary at apex v3; two-triangle patch)
  - What it tests: Determine v3's reference edge after boundary status
  - Repair action: Set v3->e0 to boundary edge or next available
- **Branch 7** @ line 480 — *isolated_edge_pair_v1* — COVERED (Me106: v0 first vertex of t0 only; both incident edges isolated after unlink)
  - What it tests: e1 and e2 both isolated (no triangles remaining)
  - Repair action: Nullify v1->e0 to mark vertex orphaned
- **Branch 8** @ line 481 — *isolated_edge_pair_v2* — COVERED (Me107: v1 second vertex of t0 only; both incident edges isolated after unlink)
  - What it tests: e2 and e3 both isolated
  - Repair action: Nullify v2->e0
- **Branch 9** @ line 482 — *isolated_edge_pair_v3* — SKIPPED: geometric signature is identical to Branches 7 and 8 but for the third vertex; no distinct assertion pattern beyond Me106/Me107. Deferred.
  - What it tests: e3 and e1 both isolated
  - Repair action: Nullify v3->e0
- **Branch 10** @ line 483 — *orphaned_edge_e1* — SKIPPED: requires half-edge NULL-vertex state not representable in flat triangle-list .mesh.json (e1's endpoints would both be NULL — an in-memory HalfEdge invariant, not a mesh-geometry condition). Deferred to HalfEdge-aware fixture format.
  - What it tests: e1 has no vertices (both NULL)
  - Repair action: Mark e1 as fully detached
- **Branch 11** @ line 493 — *manifold_duplication_v1* — COVERED (Me108: v1 bowtie with upper+lower fan; vertex_fan_disconnected assertion)
  - What it tests: v1 non-manifold duplication required
  - Repair action: Clone v1, redirect incident edges, add to mesh
- **Branch 12** @ line 503 — *manifold_duplication_v2* — COVERED (Me109: v2 bowtie with upper+lower fan; vertex_fan_disconnected assertion)
  - What it tests: v2 non-manifold duplication required
  - Repair action: Clone v2, redirect incident edges, add to mesh
- **Branch 13** @ line 513 — *manifold_duplication_v3* — SKIPPED: structurally identical to Branches 11 and 12 but for the third vertex; would produce a near-duplicate of Me108/Me109 with no new assertion kind. Deferred.
  - What it tests: v3 non-manifold duplication required
  - Repair action: Clone v3, redirect incident edges, add to mesh

Fixture IDs: Me100 Me101 Me102 Me103 Me104 Me105 Me106 Me107 Me108 Me109


#### `src/TMesh/triangle.cpp`
(1 methods, 16 branches)

##### `Triangle.intersects` — lines 305–408
(16 branches; 10 COVERED by Me110–Me119 wave 5A — 6 skipped, see notes)

- **Branch 1** @ line 309 — *INTERSECTION_MODE_PROPER* — **COVERED by Me119**
  - What it tests: justproper flag: test only proper (interior) intersections, not touching endpoints
  - Repair action: Use strict coincident vertex and edge tests, skip improper touching cases
  - Fixture: Me119 — T-junction vertex on edge; improper contact in default mode, justproper skips
- **Branch 2** @ line 314 — *FULL_VERTEX_COINCIDENCE* — **COVERED by Me110**
  - What it tests: All 3 vertices of t1 coincide with vertices of t2 (triangles identical)
  - Repair action: Return false; identical triangles are not considered an intersection
  - Fixture: Me110 — exact duplicate triangle entries (same indices)
- **Branch 3** @ line 319 — *SHARED_EDGE_PROPER* — **COVERED by Me111**
  - What it tests: Triangles share an edge (eq1 && eq2 hold) in proper mode
  - Repair action: Return false; adjacent manifold triangles are not intersecting
  - Fixture: Me111 — clean manifold fold sharing edge (v0,v1)
- **Branch 4** @ line 320 — *SHARED_EDGE_PROPER_EDGE2* — **SKIPPED** (same geometric class as Branch 3; Me111 covers the shared-edge pattern; second/third index-ordering variants add no distinct geometric signature)
- **Branch 5** @ line 321 — *SHARED_EDGE_PROPER_EDGE3* — **SKIPPED** (same reason as Branch 4)
- **Branch 6** @ line 331 — *SHARED_VERTEX_PROPER* — **COVERED by Me112**
  - What it tests: Triangles share exactly one vertex in proper mode
  - Repair action: Check if opposite edges intersect the opposing triangle
  - Fixture: Me112 — shared apex, triangles fan in opposite X directions; free edges disjoint
- **Branch 7** @ line 359 — *BBOX_X_REJECT_MIN* — **COVERED by Me113**
  - What it tests: Bounding box rejection: all vertices of t2 are below t1's x-min
  - Repair action: Return false; boxes disjoint in x dimension
  - Fixture: Me113 — t0 in x=[3,5], t1 in x=[0,1]; x-gap of 2 units
- **Branch 8** @ line 361 — *BBOX_X_REJECT_MAX* — **SKIPPED** (symmetric to Branch 7 / Me113; Me113 demonstrates the bbox-x separation pattern; max variant has identical geometric content in the other direction)
- **Branch 9** @ line 363 — *BBOX_Y_REJECT_MIN* — **COVERED by Me114**
  - What it tests: Y-dimension bounding box separation (min)
  - Repair action: Return false; y-disjoint
  - Fixture: Me114 — t0 in y=[4,6], t1 in y=[0,2]; y-gap of 2 units
- **Branch 10** @ line 365 — *BBOX_Y_REJECT_MAX* — **SKIPPED** (symmetric to Branch 9 / Me114)
- **Branch 11** @ line 367 — *BBOX_Z_REJECT_MIN* — **COVERED by Me115**
  - What it tests: Z-dimension bounding box separation (min)
  - Repair action: Return false; z-disjoint
  - Fixture: Me115 — t0 at z=[5,7], t1 at z=[0,2]; z-gap of 3 units
- **Branch 12** @ line 369 — *BBOX_Z_REJECT_MAX* — **SKIPPED** (symmetric to Branch 11 / Me115)
- **Branch 13** @ line 376 — *ORIENTATION_T1_ABOVE_OR_BELOW* — **COVERED by Me116**
  - What it tests: All vertices of t1 have same orientation w.r.t. t2's plane (all above or all below)
  - Repair action: Return false; t1 and t2 separated by plane
  - Fixture: Me116 — t0 in z=0, t1 floating above; bbox overlap but all-positive orientations
- **Branch 14** @ line 380 — *ORIENTATION_T2_ABOVE_OR_BELOW* — **SKIPPED** (symmetric orientation test; Me116 covers the plane-separation pattern; t2-above variant has identical geometric content)
- **Branch 15** @ line 382 — *COPLANAR_TRIANGLES* — **COVERED by Me117**
  - What it tests: All orientation values are 0 (coplanar case)
  - Repair action: Check 9 edge-pair crossings and 6 point-in-triangle tests for coplanar overlap
  - Fixture: Me117 — two coplanar z=0 triangles shifted by (1,0,0); overlapping interior region
- **Branch 16** @ line 401 — *PROPER_INTERSECTION_3D* — **COVERED by Me118**
  - What it tests: Non-coplanar case with mixed orientations (at least one edge crosses)
  - Repair action: Test 6 edge-triangle segment intersection combinations
  - Fixture: Me118 — XZ-plane and XY-plane triangles sharing base edge; proper 3D intersection

