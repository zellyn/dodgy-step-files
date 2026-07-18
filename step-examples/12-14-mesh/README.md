# 12-14-mesh

## Fixtures

| ID | Title |
|---|---|
| [Me001](Me001.stp) | non-manifold edge: three triangles share a single edge |
| [Me002](Me002.stp) | degenerate triangle: three collinear vertices, area=0 |
| [Me003](Me003.stp) | near-coincident vertices: 5e-8 separation, distinct entries |
| [Me004](Me004.stp) | boundary hole: 3×3 patch with one triangle missing |
| [Me005](Me005.stp) | self-intersecting face pair: XY and XZ triangles cross at v0 |
| [Me006](Me006.stp) | duplicate triangles: two triangles with identical vertex tuples |
| [Me007](Me007.stp) | inverted normals: tetrahedron with all faces wound inward (CW) |
| [Me008](Me008.stp) | isolated vertex: vertex 3 has no incident triangle |
| [Me009](Me009.stp) | T-junction: vertex 3 lies exactly on edge (v0, v2) of triangle 0 |
| [Me010](Me010.stp) | sliver triangle: aspect ratio > 100, needle aligned along X |
| [Me011](Me011.stp) | non-manifold vertex (bowtie): two triangle fans share only vertex 0 |
| [Me012](Me012.stp) | inconsistent face orientation: triangle 2 wound CW inside CCW mesh |
| [Me013](Me013.stp) | boundary gap (thin): two patches share near-coincident boundary displaced by 2e-7 |
| [Me014](Me014.stp) | disconnected components: large patch plus tiny noise triangle 100 units away |
| [Me015](Me015.stp) | polygon with repeated vertex: triangle 1 lists vertex 1 twice |
| [Me016](Me016.stp) | SI + non-manifold bowtie vertex: genus-preservation decision |
| [Me017](Me017.stp) | SI in CC-A; clean CC-B disconnected: treat_all_CCs decision |
| [Me018](Me018.stp) | SI pocket with displaced apex piercing flat patch: use_smoothing branch |
| [Me019](Me019.stp) | SI region with degenerate zero-area faces: faces_to_treat empties after removal |
| [Me020](Me020.stp) | internal SI in CC-A; CC-B clean: internal-vs-external SI classification |
| [Me021](Me021.stp) | SI near sharp dihedral feature: constrain_sharp_edges branch |
| [Me022](Me022.stp) | SI in annular ring (chi=0 topology): complex-topology handler branch |
| [Me023](Me023.stp) | SI pair surrounded by expansion belt: expand_face_selection branch |
| [Me024](Me024.stp) | SI with singleton compactified region: cc_faces.size()==1 branch |
| [Me025](Me025.stp) | dual persistent SI piercers: something_was_done=false convergence stall |
| [Me026](Me026.stp) | all faces degenerate: entire mesh is zero-area collinear triangles |
| [Me027](Me027.stp) | adjacent degenerate faces: two collinear triangles sharing an edge |
| [Me028](Me028.stp) | border degenerate face: collinear zero-area triangle on open boundary |
| [Me029](Me029.stp) | degenerate edge in face: triangle with a zero-length edge |
| [Me030](Me030.stp) | degree-3 vertex cap: apex with exactly 3 incident triangles |
| [Me031](Me031.stp) | isolated degenerate face among healthy neighbors: flip-candidate branch |
| [Me032](Me032.stp) | connected component of collinear faces: 3-triangle degenerate strip |
| [Me033](Me033.stp) | non-disk degenerate CC: collinear cluster with non-disk topology |
| [Me034](Me034.stp) | flip-impossible degenerate: edge shared 3-way, face removal fallback |
| [Me035](Me035.stp) | border face removal: degenerate triangle on open boundary, direct remove_face |
| [Me036](Me036.stp) | duplicate_polygons KEEP_ONE: three identical triangles, keep one remove two |
| [Me037](Me037.stp) | duplicate_polygons orientation_requirement: reversed-winding pair |
| [Me038](Me038.stp) | duplicate_polygons duplicate_collection: two independent duplicate groups |
| [Me039](Me039.stp) | duplicate_polygons early_exit_empty: all-distinct polygon soup, no duplicates |
| [Me040](Me040.stp) | duplicate_polygons duplicate_group_iteration: three separate duplicate groups |
| [Me041](Me041.stp) | duplicate_polygons keep_decision ERASE_ALL: both copies scheduled for removal |
| [Me042](Me042.stp) | duplicate_polygons removal_iteration: 4-copy group, inner loop runs 3 times |
| [Me043](Me043.stp) | duplicate_polygons treated_skip: shared polygon in two groups, skip on second pass |
| [Me044](Me044.stp) | duplicate_polygons swap_to_end: duplicate swapped to back then erased |
| [Me045](Me045.stp) | duplicate_polygons mark_treated+final_erase: KEEP_ONE_IF_ODD with 3 copies |
| [Me046](Me046.stp) | cyclic orientation flip: odd-parity ring blocks compatible_orientations |
| [Me047](Me047.stp) | non-manifold edge shared by 3 triangles blocks compatible_orientations |
| [Me048](Me048.stp) | orientation constraint conflict: two consistently wound chains are mutually incompatible |
| [Me049](Me049.stp) | boundary halfedge traversal: next_on_border walk around open mesh boundary |
| [Me050](Me050.stp) | degenerate collinear face: SI-impl reports (f,f) self-pair instead of building AABB bbox |
| [Me051](Me051.stp) | two SI pairs: maximum_number count-limit parameter is applicable |
| [Me052](Me052.stp) | zero-limit trivial rejection: maximum_number=0 returns immediately with no output |
| [Me053](Me053.stp) | throw_on_SI mode: single crossing pair fires Throw_at_output_exception on first hit |
| [Me054](Me054.stp) | sequential throw_on_SI: first of two pairs triggers early exit in sequential AABB path |
| [Me055](Me055.stp) | sequential count-limit: 3 SI pairs; Count_and_throw_filter fires after pair 2 |
| [Me056](Me056.stp) | sequential catch-limit: 4 SI pairs; exception caught after Count_and_throw_filter fires |
| [Me057](Me057.stp) | parallel throw_on_SI: two crossing pairs; TBB callback fires Throw_at_output_exception |
| [Me058](Me058.stp) | parallel count-limit: 4 SI pairs; atomic counter fires Throw_functor at limit 3 |
| [Me059](Me059.stp) | parallel catch-limit: 5 SI pairs; exception caught after atomic counter fires at limit 4 |
| [Me060](Me060.stp) | pinch_detection: hexagon (v0,v1,v2,v0,v3,v4) — v0 repeated at position 3 |
| [Me061](Me061.stp) | split_polygon_1: heptagon pinched at v1 (positions 1 and 4) → triangle + quad |
| [Me062](Me062.stp) | polygon_replacement+new_polygon_append: heptagon (v0..v3,v0,v4,v5) → quad+triangle |
| [Me063](Me063.stp) | loop_break: polygon with two potential pinches; first pinch triggers break |
| [Me064](Me064.stp) | small_polygon_skip: triangle (<=3 verts) skipped; adjacent hexagon is pinched |
| [Me065](Me065.stp) | dynamic_polygon_iteration: double-pinched 9-gon grows polygon list via push_back cascade |
| [Me066](Me066.stp) | point_uniqueness_check: 7-gon (v0..v4,v2,v5) — pinch found at map position 5 |
| [Me067](Me067.stp) | pinch_split_boundary: 8-gon with pinch at positions 1 and 6 → pentagon + triangle |
| [Me068](Me068.stp) | pinch_detection: 4-vertex polygon (v0,v1,v2,v0) — minimum pinchable; yields one triangle |
| [Me069](Me069.stp) | new_polygon_append cascade: two independently pinched hexagons each trigger push_back |
| [Me070](Me070.stp) | duplicate_singular_vertices: minimal bowtie — 2-fan vertex in XY plane |
| [Me071](Me071.stp) | duplicate_singular_vertices: 3D bowtie — two fans in orthogonal planes |
| [Me072](Me072.stp) | duplicate_singular_vertices: triple-fan vertex — 3 disjoint link CCs at v0 |
| [Me073](Me073.stp) | duplicate_singular_vertices: bowtie with 3-triangle upper fan and 1-triangle lower fan |
| [Me074](Me074.stp) | duplicate_singular_vertices: two separate bowtie vertices in one mesh |
| [Me075](Me075.stp) | duplicate_singular_vertices: bowtie vertex plus isolated (unreferenced) neighbor vertex |
| [Me076](Me076.stp) | duplicate_singular_vertices: closed-ring upper fan plus open lower fan at bowtie vertex |
| [Me077](Me077.stp) | duplicate_singular_vertices: open-strip fan (CW+CCW traversal) plus isolated lower fan |
| [Me078](Me078.stp) | duplicate_singular_vertices: 3-fan vertex requiring 2 new duplicate points |
| [Me079](Me079.stp) | duplicate_singular_vertices: 4-triangle open-strip fan plus isolated lower fan at bowtie vertex |
| [Me080](Me080.stp) | connectivity null vertex: orphan vertex not referenced by any triangle |
| [Me081](Me081.stp) | connectivity null edge ref: interior orphan vertex at centroid with no incident edges |
| [Me082](Me082.stp) | connectivity null edge endpoint: degenerate triangle with duplicate vertex index (self-loop) |
| [Me083](Me083.stp) | connectivity coincident edge endpoints: edge between two distinct vertices at identical positions |
| [Me084](Me084.stp) | connectivity orphaned edge: open 2×2 quad strip with 7 boundary edges |
| [Me085](Me085.stp) | connectivity triangle-not-owns-edge: non-manifold edge shared by 4 triangles |
| [Me086](Me086.stp) | connectivity edge orientation mismatch: adjacent triangles with opposite normals along shared edge |
| [Me087](Me087.stp) | connectivity null triangle edge: single isolated triangle with all boundary edges |
| [Me088](Me088.stp) | connectivity duplicate triangle edges: two identical triangles with same vertex indices |
| [Me089](Me089.stp) | connectivity disconnected edges: triple-bowtie vertex with 3 disconnected triangle fans |
| [Me090](Me090.stp) | edge_collapse_boundary_validity: both collapse endpoints on mesh boundary |
| [Me091](Me091.stp) | edge_collapse_degenerate_t1_side: collapsing edge creates duplicate triangle on t1 side |
| [Me092](Me092.stp) | edge_collapse_degenerate_t2_side: collapsing edge creates duplicate triangle on t2 side |
| [Me093](Me093.stp) | edge_collapse_single_sided_t1: t1 has no external neighbors (ta1=NULL, ta2=NULL) |
| [Me094](Me094.stp) | edge_collapse_pinch_detect: v0 neighbor already connected to v1, collapse blocked |
| [Me095](Me095.stp) | edge_collapse_vertex_merge: near-coincident v0 and v1, 3-triangle fan on v0 |
| [Me096](Me096.stp) | edge_collapse_adjacency_repair: near-coincident vertices with bilateral neighbors |
| [Me097](Me097.stp) | edge_collapse_orphan_vertex: isolated vertex left behind by collapse cleanup |
| [Me098](Me098.stp) | edge_collapse_orphan_edge_e2: e2 has no neighbors (ta2=NULL), becomes orphan post-collapse |
| [Me099](Me099.stp) | edge_collapse_orphan_edge_e3: e3 has no neighbors (ta3=NULL), becomes orphan post-collapse |
| [Me100](Me100.stp) | unlink_triangle_v1_boundary_non_manifold: v1 on boundary but both incident edges non-boundary |
| [Me101](Me101.stp) | unlink_triangle_v2_boundary_non_manifold: v2 on boundary but both incident edges non-boundary |
| [Me102](Me102.stp) | unlink_triangle_v3_boundary_non_manifold: apex vertex on boundary but both incident edges non-boundary |
| [Me103](Me103.stp) | unlink_triangle_v1_edge_ref_boundary: v1 reference edge updated to boundary after unlink |
| [Me104](Me104.stp) | unlink_triangle_v2_edge_ref_boundary: v2 reference edge updated to boundary after unlink |
| [Me105](Me105.stp) | unlink_triangle_v3_edge_ref_boundary: apex v3 reference edge updated to newly-boundary base edge |
| [Me106](Me106.stp) | unlink_triangle_isolated_edge_pair_v1: v1's both incident edges isolated, v1 becomes orphan |
| [Me107](Me107.stp) | unlink_triangle_isolated_edge_pair_v2: v2's both incident edges isolated, v2 becomes orphan |
| [Me108](Me108.stp) | unlink_triangle_v1_manifold_duplication: v1 is non-manifold bowtie requiring duplication on unlink |
| [Me109](Me109.stp) | unlink_triangle_v2_manifold_duplication: v2 is non-manifold bowtie requiring duplication on unlink |
| [Me110](Me110.stp) | intersects_full_vertex_coincidence: exact duplicate triangles — Branch 2 returns false |
| [Me111](Me111.stp) | intersects_shared_edge_proper: manifold adjacent triangles sharing an edge — Branch 3 returns false |
| [Me112](Me112.stp) | intersects_shared_vertex_proper: shared-apex triangles pointing in opposite directions — Branch 6 returns false |
| [Me113](Me113.stp) | intersects_bbox_x_reject_min: t2 entirely left of t1's x-min — Branch 7 fast-reject |
| [Me114](Me114.stp) | intersects_bbox_y_reject_min: t2 entirely below t1's y-min — Branch 9 fast-reject |
| [Me115](Me115.stp) | intersects_bbox_z_reject_min: t2 entirely below t1's z-min — Branch 11 fast-reject |
| [Me116](Me116.stp) | intersects_orientation_t1_above_plane: t1 entirely above t0's plane — Branch 13 fast-reject |
| [Me117](Me117.stp) | intersects_coplanar_overlap: coplanar triangles with overlapping interiors — Branch 15 fires |
| [Me118](Me118.stp) | intersects_proper_3d: non-coplanar triangles with 3D interior crossing — Branch 16 fires |
| [Me119](Me119.stp) | intersects_proper_mode_endpoint_touch: T-junction vertex on edge — improper contact |
| [Me120](Me120.stp) | inverse_collapse_right_triangle_e2: ta1 exists on right side of split edge e2 |
| [Me121](Me121.stp) | inverse_collapse_left_triangle_e3: ta4 exists on left side of split edge e3 |
| [Me122](Me122.stp) | inverse_collapse_vertex_edge_list_circular: fully interior vertex with circular VE() ring |
| [Me123](Me123.stp) | inverse_collapse_find_e3_position: e3 at position 3 in 6-edge ring, break triggered at k>0 |
| [Me124](Me124.stp) | inverse_collapse_vertex_redirection: 1 intermediate edge redirected from v0 to v_new |
| [Me125](Me125.stp) | inverse_collapse_multi_redirection: 2 intermediate edges redirected to v_new |
| [Me126](Me126.stp) | inverse_collapse_edge_e_update: central edge e between this and v_new |
| [Me127](Me127.stp) | inverse_collapse_edge_e1_update: edge e1 connects v_new to e2 opposite vertex |
| [Me128](Me128.stp) | inverse_collapse_triangle_t1_setup: t1 bounded by edges e, e1, e2 |
| [Me129](Me129.stp) | inverse_collapse_edge_triangle_adjacency: e2/e3 adjacency refs updated to t1/t2 (Branch 9+10) |
| [Me130](Me130.stp) | removeIfRedundant_not_double_flat: apex vertex has non-planar 3D fan, removal blocked |
| [Me131](Me131.stp) | removeIfRedundant_check_neighborhood: vertex with healthy non-degenerate incident triangles |
| [Me132](Me132.stp) | removeIfRedundant_degenerate_neighbor_triangle: collinear incident triangle blocks vertex removal |
| [Me133](Me133.stp) | removeIfRedundant_overlapping_incident_edge: incident edge collinear-overlap blocks vertex removal |
| [Me134](Me134.stp) | removeIfRedundant_double_flat_edge_removal: DoubleFlat vertex has e1 removed from collapse candidates |
| [Me135](Me135.stp) | removeIfRedundant_double_flat_second_edge_removal: DoubleFlat vertex has both e1 and e2 removed from candidate list |
| [Me136](Me136.stp) | removeIfRedundant_opposite_vertex_coincidence: DoubleFlat e1 and e2 share coincident opposite vertex |
| [Me137](Me137.stp) | removeIfRedundant_opposite_vertices_side_check: opposite vertices on opposite sides trigger edge swap before collapse |
| [Me138](Me138.stp) | removeIfRedundant_double_flat_edge_selection: e1 preferred as collapse edge when e2 absent |
| [Me139](Me139.stp) | removeIfRedundant_collapse_failure: edge collapse returns NULL, vertex removal blocked |
| [Me140](Me140.stp) | isInnerPoint_empty_mesh: no triangles, T.numels()==0, early return false |
| [Me141](Me141.stp) | isInnerPoint_yz_bbox_reject: query point outside triangle Y-Z bounding box, skip branch fires |
| [Me142](Me142.stp) | isInnerPoint_degenerate_triangle: collinear vertices give o1=o2=o3=0, skip branch fires |
| [Me143](Me143.stp) | isInnerPoint_point_on_v2_vertex: query point coincides with v2, o1=o2=0, closest_vertex set |
| [Me144](Me144.stp) | isInnerPoint_point_on_v1_vertex: query point coincides with v1, o1=o3=0, closest_vertex=v1 |
| [Me145](Me145.stp) | isInnerPoint_point_on_v3_vertex: query point coincides with v3, o2=o3=0, closest_vertex=v3 |
| [Me146](Me146.stp) | isInnerPoint_point_on_edge: query at edge midpoint gives one orientation=0, edge-intersection branch fires |
| [Me147](Me147.stp) | isInnerPoint_point_in_triangle: all orientations positive, linePlaneIntersection fires |
| [Me148](Me148.stp) | isInnerPoint_closest_is_edge_boundary: closest ray-hit is a boundary edge, isOnBoundary() true, return false |
| [Me149](Me149.stp) | isInnerPoint_closest_is_triangle: ray hits triangle interior, sign(normal.x) determines inside/outside |
| [Me150](Me150.stp) | flipNormals_triangle_invert_guard: seed triangle has bit 6 clear, CW winding inverted |
| [Me151](Me151.stp) | flipNormals_neighbor_enqueue_t1: t1 neighbor CW, enqueued for flip propagation |
| [Me152](Me152.stp) | flipNormals_neighbor_enqueue_t2: t2 neighbor CW, enqueued for flip propagation |
| [Me153](Me153.stp) | flipNormals_neighbor_enqueue_t3: t3 neighbor CW, all four-spoke fan triangles inverted |
| [Me154](Me154.stp) | flipNormals_edge_orientation_e1: e1 reversed when triangle winding is inverted |
| [Me155](Me155.stp) | flipNormals_edge_orientation_e2: e2 reversed when triangle winding is inverted |
| [Me156](Me156.stp) | flipNormals_edge_orientation_e3: e3 reversed when triangle winding is inverted |
| [Me157](Me157.stp) | flipNormals_flip_propagation_guard: second-pass cleanup iterates already-flipped triangles |
| [Me158](Me158.stp) | flipNormals_neighbor_unmark_t1: t1 flip-bit cleared in cleanup pass |
| [Me159](Me159.stp) | flipNormals_edge_unmark_cleanup: edge bit 6 cleared on all edges in second cleanup pass |
| [Me160](Me160.stp) | stitch_boundary_edge_requirement: interior edge rejected for boundary stitching |
| [Me161](Me161.stp) | stitch_start_triangle_t1: boundary edge with t1 occupied selects t1 as walk start |
| [Me162](Me162.stp) | stitch_boundary_walk_v1: boundary chain walk from v1 traverses to find coincident candidate |
| [Me163](Me163.stp) | stitch_boundary_walk_v2: v1 walk fails, boundary walk retries from v2 to find coincident edge |
| [Me164](Me164.stp) | stitch_candidate_found: opposite-vertex match confirms coincident boundary edge pair for stitching |
| [Me165](Me165.stp) | stitch_triangle_merger_t1: candidate stitch edge e1 has incident triangle in t1 slot |
| [Me166](Me166.stp) | stitch_edge_replacement: candidate edge e1 replaced by stitch edge in triangle t via replaceEdge |
| [Me167](Me167.stp) | stitch_anchor_update: v1->e0 and v2->e0 updated to stitch edge after boundary merge |
| [Me168](Me168.stp) | stitch_orphan_edge: candidate e1 nulled (v1=v2=NULL) after boundary stitch to become orphaned edge |
| [Me169](Me169.stp) | stitch_interior_conversion: stitch edge transitions from boundary (n=1) to interior (n=2) via replaceTriangle(NULL,t) |
| [Me170](Me170.stp) | orient polygon_scan: scan loop reaches isolated second component triangle |
| [Me171](Me171.stp) | orient component_init: seed polygon pushed to DFS stack, starts orientation propagation |
| [Me172](Me172.stp) | orient dfs_traversal: DFS stack processes all 4 fan triangles from single seed |
| [Me173](Me173.stp) | orient edge_iteration: per-edge scan of patch finds defect triangle via edge loop |
| [Me174](Me174.stp) | orient marked_edge_skip: non-manifold edge marked; orientation skip continues past it |
| [Me175](Me175.stp) | orient same_orientation_edge: shared edge traversed in same direction by both triangles |
| [Me176](Me176.stp) | orient multi_neighbor_same_orient: same directed edge in >1 incident polygon same-direction map |
| [Me177](Me177.stp) | orient orientation_conflict: oriented neighbor found incompatibly wound, edge marked as conflict |
| [Me178](Me178.stp) | orient orientation_reversal: unoriented CW neighbor reversed by inverse_orientation to match CCW seed |
| [Me179](Me179.stp) | orient opposite_orientation_edge: reverse-direction shared edge correctly pairs two CCW triangles |
| [Me180](Me180.stp) | split_edge_point_equals_v1: split point coincides with v1, early return |
| [Me181](Me181.stp) | split_edge_point_equals_v2: split point coincides with v2, early return |
| [Me182](Me182.stp) | split_edge_opposite_vertex_t1: t1 exists, v3 extracted as oppositeVertex |
| [Me183](Me183.stp) | split_edge_opposite_vertex_t2: t2 exists, v4 extracted as oppositeVertex |
| [Me184](Me184.stp) | split_edge_new_edge_t1_creation: ne1=(vn,v3) created after boundary edge split |
| [Me185](Me185.stp) | split_edge_new_edge_t2_creation: ne2=(vn,v4) created after interior edge split |
| [Me186](Me186.stp) | split_edge_new_triangle_t1: nt1 created on t1 side after boundary edge split |
| [Me187](Me187.stp) | split_edge_new_triangle_t2: nt2 created on t2 side after interior edge split |
| [Me188](Me188.stp) | split_edge_mask_preservation: mask bits copied to ne1/ne2/nt1/nt2 after split |
| [Me189](Me189.stp) | split_edge_list_appends: V/E/T appendHead adds new vertex, edges, triangles |
| [Me190](Me190.stp) | splitTriangle_new_triangle_from_e3_e1: first child triangle nt1 connects nv to v2-v0 side |
| [Me191](Me191.stp) | splitTriangle_new_triangle_from_e2_e1: second child triangle nt2 connects nv to v1-v2 side |
| [Me192](Me192.stp) | splitTriangle_edge_e3_adjacency: outer edge e3 re-assigned from t to nt1 |
| [Me193](Me193.stp) | splitTriangle_edge_e1_adjacency: outer edge e1 re-assigned from t to nt2 |
| [Me194](Me194.stp) | splitTriangle_new_edge_ne1_adjacency: inner edge ne1=(nv,v1) bridges t and nt2 |
| [Me195](Me195.stp) | splitTriangle_new_edge_ne2_adjacency: inner edge ne2=(nv,v0) bridges nt1 and t |
| [Me196](Me196.stp) | splitTriangle_new_edge_ne3_adjacency: inner edge ne3=(nv,v2) bridges nt2 and nt1 |
| [Me197](Me197.stp) | splitTriangle_mask_copy_nt1: mask propagated from original t to first new child nt1 |
| [Me198](Me198.stp) | splitTriangle_mask_copy_nt2: mask propagated from original t to second new child nt2 |
| [Me200](Me200.stp) | zip_vertex_edge_list: vertex v0 has non-empty incident-edge list enabling zip boundary walk |
| [Me201](Me201.stp) | zip_boundary_edge_first: head of VE circular list for v0 is boundary edge → assigned as be1 |
| [Me202](Me202.stp) | zip_boundary_edge_last: tail of VE circular list for v0 is boundary edge → assigned as be2 |
| [Me203](Me203.stp) | zip_edge_not_boundary: closed fan around v0 means no boundary edges at head/tail → zip aborts |
| [Me204](Me204.stp) | zip_geometry_check_enabled: check_geom rejects zip when ov1 and ov2 have distinct coordinates |
| [Me205](Me205.stp) | zip_opposite_vertices_distinct: ov1 and ov2 are distinct objects at coincident positions → zip merge proceeds |
| [Me206](Me206.stp) | zip_vertex_replacement_in_edges: ov2 incident on multiple edges; zip replaceVertex loop touches all of them |
| [Me207](Me207.stp) | zip_edge_triangle_selection: be2 is boundary with exactly 1 incident triangle; ternary selects t1 or t2 slot |
| [Me208](Me208.stp) | zip_triangle_edge_update: t->replaceEdge(be2, be1) swaps be2 out of triangle's edge record during zip |
| [Me209](Me209.stp) | zip_recursive_zip: after zipping v0→ov1 merge, zip recurses on ov1 to close chain seam |
| [Me210](Me210.stp) | cutAndStitch_duplicate_singular_edge: BIT-5 non-manifold edge duplicated before stitching |
| [Me211](Me211.stp) | cutAndStitch_collect_singular_edges: boundary edge appended to singular_edges list |
| [Me212](Me212.stp) | cutAndStitch_orientation_inconsistency: adjacent triangles with antiparallel normals |
| [Me213](Me213.stp) | cutAndStitch_non_manifold_vertices: bowtie vertex requiring duplicateNonManifoldVertices() |
| [Me214](Me214.stp) | cutAndStitch_sort_singular_edges: coincident boundary edges sorted by lexEdgeCompare |
| [Me215](Me215.stp) | cutAndStitch_group_coincident_edges: distinct boundary edges each start a new grouping list |
| [Me216](Me216.stp) | cutAndStitch_bounded_singular_chain: seam edges form bounded chain pinched from common vertex |
| [Me217](Me217.stp) | cutAndStitch_unbounded_singular_chain: closed hole boundary pinched from interior edge |
| [Me218](Me218.stp) | cutAndStitch_cleanup_unlinked: isolated orphan vertex swept by removeUnlinkedElements() |
| [Me220](Me220.stp) | eulerUpdate_component_discovery: BFS discovers second disconnected shell (n_shells++) |
| [Me221](Me221.stp) | eulerUpdate_triangle_adjacency_e1: BFS enqueues unvisited e1 neighbor |
| [Me222](Me222.stp) | eulerUpdate_triangle_adjacency_e2: BFS enqueues unvisited e2 neighbor |
| [Me223](Me223.stp) | eulerUpdate_triangle_adjacency_e3: BFS enqueues unvisited e3 neighbor |
| [Me224](Me224.stp) | eulerUpdate_boundary_edge_detection: boundary edge triggers hasBoundary=true |
| [Me225](Me225.stp) | eulerUpdate_boundary_exists: hasBoundary flag gates boundary-loop processing |
| [Me226](Me226.stp) | eulerUpdate_boundary_loop_traversal: nextOnBoundary() walks two distinct loops |
| [Me227](Me227.stp) | eulerUpdate_euler_characteristic: V-E+F=2 computed via Euler formula (genus 0) |
| [Me228](Me228.stp) | eulerUpdate_topology_reset: d_boundaries=d_handles=d_shells=0 reset at end |
| [Me230](Me230.stp) | topTriangle_component_flood_fill: BFS enqueues adjacent unvisited triangle |
| [Me231](Me231.stp) | topTriangle_vertex_z_collection_v1: v1 appended to z-scan list (unvisited) |
| [Me232](Me232.stp) | topTriangle_vertex_z_collection_v2: v2 appended to z-scan list (unvisited) |
| [Me233](Me233.stp) | topTriangle_vertex_z_collection_v3: v3 appended to z-scan list (unvisited) |
| [Me234](Me234.stp) | topTriangle_edge_collection_e1: e1 appended to slope-candidate list (unvisited) |
| [Me235](Me235.stp) | topTriangle_highest_vertex_search: four staircase z-levels; v3 (z=3) becomes hv |
| [Me236](Me236.stp) | topTriangle_steepest_edge_filter: edges incident on hv=v2 pass hasVertex+nonzero filter |
| [Me237](Me237.stp) | topTriangle_steepest_edge_selection: steeper edge (v1,v2) wins Branch 8 slope comparison |
| [Me238](Me238.stp) | topTriangle_fallback_reference_edge: fully degenerate triangle forces fe=NULL; Branch 9 uses hv->e0 |
| [Me239](Me239.stp) | topTriangle_degenerate_edge_check: steepest edge is boundary; topTriangle returns NULL |
| [Me240](Me240.stp) | negligible_size area_threshold_default: tiny component below bbox-derived area threshold |
| [Me241](Me241.stp) | negligible_size volume_threshold_default: tiny closed component below bbox-derived volume threshold |
| [Me242](Me242.stp) | negligible_size area_check: use_areas=true; small component below explicit area_threshold |
| [Me243](Me243.stp) | negligible_size volume_check: use_volumes=true; tiny closed component below explicit volume_threshold |
| [Me244](Me244.stp) | negligible_size no_criteria: !use_areas && !use_volumes → early return 0 |
| [Me245](Me245.stp) | negligible_size dry_run: collect-only mode; micro-component identified but mesh not mutated |
| [Me246](Me246.stp) | negligible_size open_component: border edges detected; cc_closeness=false skips volume |
| [Me247](Me247.stp) | negligible_size volume_skip_open: non-closed component skips volume via !cc_closeness[i] |
| [Me248](Me248.stp) | negligible_size removal_logic: tiny closed component satisfies area-or-volume removal OR-condition |
| [Me250](Me250.stp) | openToDisk_boundary_traversal_edge1: BFS queues neighbor via e1 shared edge (Branch 1) |
| [Me251](Me251.stp) | openToDisk_boundary_traversal_edge2: BFS queues neighbor via e2 shared edge (Branch 2) |
| [Me252](Me252.stp) | openToDisk_boundary_traversal_edge3: BFS queues neighbor via e3 shared edge (Branch 3) |
| [Me253](Me253.stp) | openToDisk_leaf_boundary_vertex: corner vertex with minimum boundary valence chosen as BFS root (Branch 4) |
| [Me254](Me254.stp) | openToDisk_no_leaf_found: closed tetrahedron has no boundary — error (Branch 5) |
| [Me255](Me255.stp) | openToDisk_boundary_edge_exists: spanning tree processes pending boundary edge (Branch 6) |
| [Me256](Me256.stp) | openToDisk_vertex_cycle_closure: two boundary loops force Branch 7 twice (Branch 7) |
| [Me257](Me257.stp) | openToDisk_non_boundary_edge_dup: torus (chi=0) — interior edges duplicated to cut to disk (Branch 8) |
| [Me258](Me258.stp) | openToDisk_manifold_fixup: bowtie vertex requires duplicateNonManifoldVertices (Branch 9) |
| [Me260](Me260.stp) | range_with_face_set link_condition_ok: zero-length edge satisfies link condition for direct collapse |
| [Me261](Me261.stp) | range_with_face_set link_condition_violated: zero-length edge with shared neighbours fails link condition |
| [Me262](Me262.stp) | range_with_face_set border_triangle_hole: degenerate border edge bounds 3-edge hole → fill_hole |
| [Me263](Me263.stp) | range_with_face_set preserve_genus: degenerate border edge in 3-edge hole; genus preservation blocks fill_hole |
| [Me264](Me264.stp) | range_with_face_set both_on_boundary: near-zero interior edge with both endpoints on mesh border → impossible=true |
| [Me265](Me265.stp) | range_with_face_set marked_faces_topological_disk: non-link-condition edge removed via face-marking + disk validation |
| [Me266](Me266.stp) | range_with_face_set nonmanifold_marked_region: bowtie vertex in neighbourhood triggers nb_cc!=1 expansion |
| [Me267](Me267.stp) | range_with_face_set not_topological_disk_after_expansion: marked region forms cylinder → disk test fails → skip |
| [Me268](Me268.stp) | range_with_face_set whole_component_selected: single-triangle component with degenerate edge → border.empty() → skip |
| [Me269](Me269.stp) | range_with_face_set border_edge_cycle: annular mesh with inner hole; degenerate inner-boundary edge → cycle of border edges → skip |
| [Me270](Me270.stp) | autorefine_triangle_soup no-SI trivial case: si_pairs.empty() → verbatim copy (Branch 1) |
| [Me271](Me271.stp) | autorefine_triangle_soup degenerate-face-tagging: (f,f) self-pair → is_degen flag (Branch 2) |
| [Me272](Me272.stp) | autorefine_triangle_soup intersection-point-count switch: nbi=1 vertex touch (Branch 3) |
| [Me273](Me273.stp) | autorefine_triangle_soup single-point containment: T-vertex on edge → case 1 (Branch 4) |
| [Me274](Me274.stp) | autorefine_triangle_soup segment-intersection two-point branch: case 2 segment SI (Branch 5) |
| [Me275](Me275.stp) | autorefine_triangle_soup polygon-intersection default branch: nbi>=3 coplanar overlap (Branch 6) |
| [Me276](Me276.stp) | autorefine_triangle_soup coplanarity-tracking: coplanar pair → coplanar_triangles (Branch 7) |
| [Me277](Me277.stp) | autorefine_triangle_soup parallel-vs-sequential dedup: multi-triangle SI pool (Branch 8) |
| [Me278](Me278.stp) | autorefine_triangle_soup dedup duplicate-point: coincident insertion points → id_map (Branch 9) |
| [Me279](Me279.stp) | autorefine_triangle_soup segment branch on_same_edge skip: shared edge → no new segment (Branch 5b) |
| [Me280](Me280.stp) | checkGeometry_memory_alloc_fail_vertices: near-coincident vertex pair, alloc guard (Branch 1) |
| [Me281](Me281.stp) | checkGeometry_coincident_vertices_edge_absent: two coincident vertices without connecting edge (Branch 2) |
| [Me282](Me282.stp) | checkGeometry_coincident_vertices_with_edge: coincident vertices connected by zero-length edge (Branch 3) |
| [Me283](Me283.stp) | checkGeometry_memory_alloc_fail_edges: coincident edge pair, edge alloc guard (Branch 4) |
| [Me284](Me284.stp) | checkGeometry_coincident_edges: two spatially identical edges with different vertex indices (Branch 5) |
| [Me285](Me285.stp) | checkGeometry_degenerate_triangle_zero_angle: interior angle = 0° at pivot vertex (Branch 6) |
| [Me286](Me286.stp) | checkGeometry_degenerate_triangle_flat_angle: interior angle = 180° (pi) at pivot vertex (Branch 7) |
| [Me287](Me287.stp) | checkGeometry_overlapping_triangles_dihedral: adjacent coplanar triangles with dihedral = 180° (Branch 8) |
| [Me290](Me290.stp) | connected_components iteration_construct: outer for-loop visits three isolated triangle components |
| [Me291](Me291.stp) | connected_components visited_face_dedup_outer: multi-face CC followed by isolated face exercises handled[] skip |
| [Me292](Me292.stp) | connected_components loop_control: 6-triangle fan forces BFS while-loop to cycle until exhausted |
| [Me293](Me293.stp) | connected_components visited_face_dedup_inner: diamond mesh where face f3 is discoverable from two BFS paths |
| [Me294](Me294.stp) | connected_components inner_halfedge_iteration: center triangle discovers 3 neighbors via 3 halfedges |
| [Me295](Me295.stp) | connected_components logic_guard_ecmap: constrained interior edge creates CC boundary |
| [Me296](Me296.stp) | connected_components null_face_check: open patch — BFS hits boundary halfedges with no opposite face |
| [Me297](Me297.stp) | connected_components visited_face_dedup_cross_halfedge: hub-and-spoke mesh — BFS skips already-handled opposite faces |
| [Me300](Me300.stp) | retriangulateSelectedRegion_insufficient_triangles: region < 2 triangles, abort (Branch 1) |
| [Me301](Me301.stp) | retriangulateSelectedRegion_normal_orientation_conflict: region normals conflict, abort (Branch 2) |
| [Me302](Me302.stp) | retriangulateSelectedRegion_non_simple_selection: two disconnected selected patches, abort (Branch 3) |
| [Me303](Me303.stp) | retriangulateSelectedRegion_internal_vertices_extraction: central vertex is internal to region (Branch 4) |
| [Me304](Me304.stp) | retriangulateSelectedRegion_triangle_unlink: selected triangles unlinked, hole exposed (Branch 5) |
| [Me305](Me305.stp) | retriangulateSelectedRegion_boundary_edge_extraction: boundary edge e = ms->head() (Branch 6) |
| [Me306](Me306.stp) | retriangulateSelectedRegion_vertex_list_extraction: vl = internal vertex list (Branch 7) |
| [Me307](Me307.stp) | retriangulateSelectedRegion_hole_triangulation: TriangulateHole with Steiner point (Branch 8) |
| [Me310](Me310.stp) | watsonInsert_point_in_circumsphere: inserted point inside circumsphere triggers cavity marking (Branch 1) |
| [Me311](Me311.stp) | watsonInsert_cavity_vertex_v1: v1 of removed triangle appended to cavity boundary (Branch 2) |
| [Me312](Me312.stp) | watsonInsert_cavity_vertex_v2: v2 of removed triangle appended to cavity boundary (Branch 3) |
| [Me313](Me313.stp) | watsonInsert_cavity_vertex_v3: v3-slot vertex of removed triangle appended to cavity boundary (Branch 4) |
| [Me314](Me314.stp) | watsonInsert_no_circumsphere_triangles: point outside all circumspheres returns NULL (Branch 5) |
| [Me315](Me315.stp) | watsonInsert_boundary_edge_selection: mixed cavity/non-cavity edges at boundary vertex (Branch 6) |
| [Me316](Me316.stp) | watsonInsert_cavity_triangle_removal: 6 cavity triangles unlinked by unlinkTriangleNoManifold (Branch 7) |
| [Me320](Me320.stp) | with_third_points_empty_input_guard: zero-point hole boundary returns output iterator unchanged (Branch 1) |
| [Me321](Me321.stp) | with_third_points_cdt2_compile_disabled: CGAL_HOLE_FILLING_DO_NOT_USE_CDT2 skips CDT2 path (Branch 2) |
| [Me322](Me322.stp) | with_third_points_dt3_compile_disabled: CGAL_HOLE_FILLING_DO_NOT_USE_DT3 forces use_dt3=false (Branch 3) |
| [Me323](Me323.stp) | with_third_points_visitor_optional: Default_visitor substituted when visitor param absent (Branch 4) |
| [Me324](Me324.stp) | with_third_points_triangle_validity_check: Is_not_degenerate_triangle rejects zero-area candidate (Branch 5) |
| [Me325](Me325.stp) | with_third_points_cost_function_strategy: Weight_min_max_dihedral_and_area scores needle triangle poorly (Branch 6) |
| [Me326](Me326.stp) | with_third_points_cdt2_path_conditional: CDT path fills planar triangular hole with all boundary edges present (Branch 7) |
| [Me327](Me327.stp) | with_third_points_threshold_override: auto bbox threshold too small for wide flat hole; user override needed (Branch 8) |
| [Me328](Me328.stp) | with_third_points_fallback_dt3_or_cubic: CDT fails on non-planar hole; DT3/cubic fallback fires (Branch 9) |
| [Me330](Me330.stp) | pinch_missing_info_field: non-manifold edge info list NULL — pinch returns false (Branch 1) |
| [Me331](Me331.stp) | pinch_non_manifold_vertex_boundary: two coincident boundary edges at shared vertex, merge (Branch 2) |
| [Me332](Me332.stp) | pinch_non_manifold_vertex_not_found: no v1-side boundary match, fallback scan from v2 (Branch 3) |
| [Me333](Me333.stp) | pinch_interior_edge_asymmetry_t1: e1->t1 set, mirror e2->t2 found — merge resolves asymmetry (Branch 4) |
| [Me334](Me334.stp) | pinch_interior_edge_asymmetry_t2: e1->t2 only, mirror e2->t1 found — merge resolves asymmetry (Branch 5) |
| [Me335](Me335.stp) | pinch_merge_failed: non-manifold edge with 3 incident triangles, no valid mirror — pinch returns false (Branch 6) |
| [Me336](Me336.stp) | pinch_cascade_v1: v1 still non-manifold after primary merge — recursive pinch(e_1,true) fires (Branch 7) |
| [Me337](Me337.stp) | pinch_cascade_v2: v2 still non-manifold after primary merge — recursive pinch(e_2,true) fires (Branch 8) |
| [Me340](Me340.stp) | init_info_array_allocation_triangles: duplicate triangle inflates t_info allocation size |
| [Me341](Me341.stp) | init_vertex_copy_iteration: 2 isolated vertices drive FOREACHVVVERTEX over 5 entries |
| [Me342](Me342.stp) | init_edge_copy_iteration: non-manifold edge forces FOREACHVEEDGE to copy over-incident edge entry |
| [Me343](Me343.stp) | init_triangle_copy_iteration: degenerate zero-area triangle forces FOREACHVTTRIANGLE over 2 entries |
| [Me344](Me344.stp) | init_vertex_edge_reference_link: bowtie vertex e0 links into only one disconnected fan group |
| [Me345](Me345.stp) | init_edge_triangle_reference_link: open-boundary mesh forces clone edge t1/t2 pointers during init |
| [Me346](Me346.stp) | init_info_preservation_flag: near-coincident vertex pair forces clone_info to copy degenerate triangle info pointer |
| [Me347](Me347.stp) | init_topology_invalidation: two disconnected open shells require d_boundaries/d_shells/d_handles recompute after init |
| [Me350](Me350.stp) | CreateTriangle_e1_e2_orientation_check: e1->v2 is junction with e2, assign e1->t1 slot |
| [Me351](Me351.stp) | CreateTriangle_e2_e3_orientation_check: e2->v2 is junction with e3, assign e2->t1 slot |
| [Me352](Me352.stp) | CreateTriangle_e3_e1_orientation_check: e3->v2 is junction with e1, assign e3->t1 slot |
| [Me353](Me353.stp) | CreateTriangle_triangle_creation: tt=newTriangle(e1,e2,e3) allocates triangle object |
| [Me354](Me354.stp) | CreateTriangle_triangle_adjacency_assignment: *at1=*at2=*at3=tt links edge slots to triangle |
| [Me355](Me355.stp) | CreateTriangle_mesh_list_append: T.appendHead(tt) inserts triangle into mesh list T |
| [Me356](Me356.stp) | CreateTriangle_visit_flag_mark: MARK_VISIT(tt) tags newly created triangle as visited |
| [Me357](Me357.stp) | CreateTriangle_topology_invalidation: d_boundaries=d_handles=d_shells=1 after shell closure |
| [Me360](Me360.stp) | remove_isolated_points_empty_input: empty vertex list triggers early return with 0 removed |
| [Me361](Me361.stp) | remove_isolated_points_usage_scan: all vertices referenced; visited[] fully populated by polygon scan |
| [Me362](Me362.stp) | remove_isolated_points_unused_detection: isolated v3 found by !visited[i] and swapped toward tail |
| [Me363](Me363.stp) | remove_isolated_points_early_termination: two trailing orphans; i>=first_unused_pos break fires |
| [Me364](Me364.stp) | remove_isolated_points_removal_count_check: closed tetrahedron; removed_points_n==0 triggers early return |
| [Me365](Me365.stp) | remove_isolated_points_physical_erase: two orphan tail vertices erased from points container |
| [Me366](Me366.stp) | remove_isolated_points_index_remapping: isolated vertex at non-tail position forces non-trivial index remap |
| [Me370](Me370.stp) | isSelectionSimple_empty_selection: no triangles marked selected, numels==0, return 0 (Branch 1) |
| [Me371](Me371.stp) | isSelectionSimple_visited_neighbor: 3-triangle fan, BFS discovers each via IS_VISITED+!IS_VISITED2 (Branch 2) |
| [Me372](Me372.stp) | isSelectionSimple_boundary_neighbor: single selected triangle at mesh boundary, NULL neighbor → break (Branch 3) |
| [Me373](Me373.stp) | isSelectionSimple_mesh_boundary_in_selection: 2-triangle strip with open boundary, top.numels()>0 → return 0 (Branch 4) |
| [Me374](Me374.stp) | isSelectionSimple_disconnected_selection: two disjoint selected patches, nv != numels → return 0 (Branch 5) |
| [Me375](Me375.stp) | isSelectionSimple_boundary_edge_count: figure-8 selection with pinch vertex, nae>1 → break (Branch 6) |
| [Me376](Me376.stp) | isSelectionSimple_boundary_loop_complexity: annular selection with two boundary loops, nv != bdr.numels() (Branch 7) |
| [Me380](Me380.stp) | isDoubleFlat_empty_1ring: vertex has no incident edges; VE() NULL triggers Branch 1 return false |
| [Me381](Me381.stp) | isDoubleFlat_edge_convexity_nonzero_first: first non-coplanar edge found; nne incremented to 1 at Branch 2 |
| [Me382](Me382.stp) | isDoubleFlat_edge_convexity_triple: 6-triangle fan with 3 raised outer vertices; nne exceeds 2 → Branch 3 returns false |
| [Me383](Me383.stp) | isDoubleFlat_edge_convexity_second: two ridge edges in 4-triangle fan; second triggers Branch 4 (e2 set, nne=2) |
| [Me384](Me384.stp) | isDoubleFlat_flat_vertex_case: all fan triangles coplanar (z=0); nne==0 → Branch 5 returns true |
| [Me385](Me385.stp) | isDoubleFlat_singular_edge_case: open 4-triangle fan with exactly one ridge; nne==1 at end → Branch 6 returns false |
| [Me386](Me386.stp) | isDoubleFlat_misalignment_check: v0 collinear with opposite vertices of two ridges; exactMisalignment=false → Branch 7 returns true |
| [Me390](Me390.stp) | do_faces_intersect_shared_edge_incident_vertex: coplanar triangles sharing full edge with overlapping interiors (Branch 1) |
| [Me391](Me391.stp) | do_faces_intersect_identical_face_soup_deduplication: two identical triangles in soup mode — deduplication target, not SI (Branch 2) |
| [Me392](Me392.stp) | do_faces_intersect_shared_edge_coplanarity_orientation: coplanar same-orientation faces sharing edge — overlapping SI (Branch 3) |
| [Me393](Me393.stp) | do_faces_intersect_shared_vertex_presence_detection: one shared vertex, no shared edge, no geometric SI (Branch 4) |
| [Me394](Me394.stp) | do_faces_intersect_opposite_segment_triangle_containment: shared-vertex pair where opposite segment pierces other triangle (Branch 5) |
| [Me395](Me395.stp) | do_faces_intersect_full_geometric_triangle_si: no shared vertex or edge, pure geometric crossing (Branch 6) |
| [Me396](Me396.stp) | do_faces_intersect_edge_orientation_search_mode: i==0 shared-vertex permutation path, strip of non-intersecting triangles (Branch 7) |
| [Me400](Me400.stp) | detect_identical_mergeable_vertices sorting_by_point: boundary cycle halfedges sorted by target coordinate; coincident v1==v3 at (1,0,0) (Branch 1) |
| [Me401](Me401.stp) | detect_identical_mergeable_vertices identical_point_detection: sorted boundary halfedge i-1 and i target same point (3,0,0) (Branch 2) |
| [Me402](Me402.stp) | detect_identical_mergeable_vertices candidate_group_creation: single coincident pair a2==a5 at (2,0,0); new group created via resize+push_back (Branch 3) |
| [Me403](Me403.stp) | detect_identical_mergeable_vertices consecutive_identical_collection: q0==q1==q2 at (1,0,0); inner while extends group to size 3 (Branch 4) |
| [Me404](Me404.stp) | detect_identical_mergeable_vertices group_break: coincident b1==b3 at (1,0,0) bounded by distinct neighbors; inner while exits via else branch (Branch 5) |
| [Me405](Me405.stp) | detect_identical_mergeable_vertices interval_sanitation: two coincident groups (c1==c4 at (1,0,0), c2==c5 at (2,0,0)) in same boundary cycle; sanitize_candidates invoked (Branch 6) |
| [Me406](Me406.stp) | detect_identical_mergeable_vertices output_conversion: single coincident group (d1==d3 at (2,0,0)) survives sanitization; mapped to halfedge descriptors (Branch 7) |
| [Me410](Me410.stp) | refineSelectedHolePatches_region_initialization: t0 pre-selected; BFS builds visited region from seed (Branch 1) |
| [Me411](Me411.stp) | refineSelectedHolePatches_edge_first_occurrence: edge not yet visited; marked with BIT5 and added to all_edges (Branch 2) |
| [Me412](Me412.stp) | refineSelectedHolePatches_edge_interior_detection: shared edge seen twice; cleared from BIT5, added to interior_edges (Branch 3) |
| [Me413](Me413.stp) | refineSelectedHolePatches_edge_length_averaging: non-interior boundary edges summed to compute sigma (Branch 4) |
| [Me414](Me414.stp) | refineSelectedHolePatches_vertex_split_density_check: large sparse triangle; all dv>sigma → centroid vertex inserted (Branch 5) |
| [Me415](Me415.stp) | refineSelectedHolePatches_edge_swap_delaunay_improvement: long diagonal satisfies swap condition; swap accepted (Branch 6) |
| [Me416](Me416.stp) | refineSelectedHolePatches_vertex_insertion_convergence: no new vertices in iteration; pnnt==nnt triggers gits++ (Branch 7) |
| [Me420](Me420.stp) | removeOverlappingTriangles_overlapping_edge_swappable: two coplanar triangles sharing edge; swap resolves overlap (Branch 1) |
| [Me421](Me421.stp) | removeOverlappingTriangles_swap_creates_degeneracy: post-swap triangle collinear; undo swap (Branch 2) |
| [Me422](Me422.stp) | removeOverlappingTriangles_swap_creates_neighbor_overlap_next: post-swap nextEdge(t1) overlaps neighbor; undo (Branch 3) |
| [Me423](Me423.stp) | removeOverlappingTriangles_swap_creates_neighbor_overlap_prev: post-swap prevEdge(t1) overlaps neighbor; undo (Branch 4) |
| [Me424](Me424.stp) | removeOverlappingTriangles_swap_creates_t2_overlap_next: post-swap t2->nextEdge overlaps neighbor; undo (Branch 5) |
| [Me425](Me425.stp) | removeOverlappingTriangles_swap_creates_t2_overlap_prev: post-swap t2->prevEdge overlaps neighbor; undo (Branch 6) |
| [Me426](Me426.stp) | removeOverlappingTriangles_unresolvable_overlap: multi-overlap tangle; both triangles unlinked (Branch 7) |
| [Me430](Me430.stp) | forceNormalConsistence t1-inconsistent: adjacent triangle flipped across shared edge e1; antiparallel normal → t1->invert() (Branch 1) |
| [Me431](Me431.stp) | forceNormalConsistence t2-inconsistent: adjacent triangle flipped across shared edge e2; antiparallel normal → t2->invert() (Branch 2) |
| [Me432](Me432.stp) | forceNormalConsistence t3-inconsistent: adjacent triangle flipped across shared edge e3; antiparallel normal → t3->invert() (Branch 3) |
| [Me433](Me433.stp) | forceNormalConsistence boundary-edge-detected: open mesh; isOnBoundary() true → isclosed cleared (Branch 4) |
| [Me434](Me434.stp) | forceNormalConsistence non-orientable-seam: seam edge traversed in same direction by both adjacent triangles; tmp1*tmp2<0 → newEdge cut (Branch 5) |
| [Me435](Me435.stp) | forceNormalConsistence vertex-order-correction: half-edge direction misaligned with triangle winding; tmp==-1 → p_swap (Branch 6) |
| [Me436](Me436.stp) | forceNormalConsistence non-orientable-mesh: wrn=2>0 from two seam cuts → topology dirty, r\|=2 (Branch 7) |
| [Me440](Me440.stp) | removeSmallestComponents_empty_mesh: single-triangle contrast for T.numels()==0 early-return (Branch 1) |
| [Me441](Me441.stp) | removeSmallestComponents_adjacent_t1: BFS expands across t->t1() unvisited neighbor; 2-component mesh 4+1 triangles (Branch 2) |
| [Me442](Me442.stp) | removeSmallestComponents_adjacent_t2: BFS expands across t->t2() unvisited neighbor; fan mesh 3+1 triangles (Branch 3) |
| [Me443](Me443.stp) | removeSmallestComponents_adjacent_t3: BFS expands across t->t3() unvisited neighbor; central triangle with all 3 adjacency slots (Branch 4) |
| [Me444](Me444.stp) | removeSmallestComponents_multiple_components: biggest reference updated twice; 3-component mesh (1+3+5 triangles) (Branch 5) |
| [Me445](Me445.stp) | removeSmallestComponents_non_largest: smaller component marked for removal; 2-component mesh (1 vs 5 triangles) (Branch 6) |
| [Me446](Me446.stp) | removeSmallestComponents_components_removed: topology dirty flags set after removal; 2-component mesh (2 vs 6 triangles) (Branch 7) |
| [Me450](Me450.stp) | removeSmallestComponents area EMPTY_MESH: T.numels()==0 → return 0; no triangles to area-filter |
| [Me451](Me451.stp) | removeSmallestComponents area ADJACENT_TRIANGLE_T1_AREA: BFS expands via t->t1() neighbor; micro-component has area below eps_area |
| [Me452](Me452.stp) | removeSmallestComponents area ADJACENT_TRIANGLE_T2_AREA: BFS expands via t->t2() neighbor; disconnected micro-component below eps_area |
| [Me453](Me453.stp) | removeSmallestComponents area ADJACENT_TRIANGLE_T3_AREA: BFS expands via t->t3() neighbor; disconnected micro-component below eps_area |
| [Me454](Me454.stp) | removeSmallestComponents area AREA_ACCUMULATION: pa += t->area() accumulates component geometric area during BFS; two-component mesh with area disparity |
| [Me455](Me455.stp) | removeSmallestComponents area COMPONENT_AREA_BELOW_THRESHOLD: pa < eps_area → component unlinked; micro-triangle area 5e-5 vs large patch area 1.0 |
| [Me456](Me456.stp) | removeSmallestComponents area SMALL_COMPONENTS_REMOVED: rem_comps > 0 → dirty flags set + removeUnlinkedElements(); nano-triangle component removed |
| [Me460](Me460.stp) | selectConnectedComponent seed_enqueue: todo.appendHead(t0) initializes BFS from seed triangle (Branch 1) |
| [Me461](Me461.stp) | selectConnectedComponent unvisited_triangle_check: BFS skips already-marked triangle on second dequeue (Branch 2) |
| [Me462](Me462.stp) | selectConnectedComponent neighbor_t1_enqueue: BFS enqueues t1 across non-sharp edge e1 (Branch 3) |
| [Me463](Me463.stp) | selectConnectedComponent neighbor_t2_enqueue: BFS enqueues t2 across non-sharp edge e2 (Branch 4) |
| [Me464](Me464.stp) | selectConnectedComponent neighbor_t3_enqueue: BFS enqueues t3 across non-sharp edge e3 (Branch 5) |
| [Me465](Me465.stp) | selectConnectedComponent mark_and_count: MARK_VISIT(t);ns++ fires for each BFS-processed triangle (ns=4) (Branch 6) |
| [Me470](Me470.stp) | remove_a_border_edge link_condition_satisfied: border edge (v0,v1) collapses safely; 2-triangle open strip (Branch 1) |
| [Me471](Me471.stp) | remove_a_border_edge link_condition_violation: border edge (v0,v1) has multiple common neighbors; collapse would break topology (Branch 2) |
| [Me472](Me472.stp) | remove_a_border_edge boundary_reached_during_exploration: all three edges are border; region touches outer boundary immediately (Branch 3) |
| [Me473](Me473.stp) | remove_a_border_edge region_not_topological_disk: 8-triangle annular ring has chi=0; is_selection_a_topological_disk returns false (Branch 4) |
| [Me474](Me474.stp) | remove_a_border_edge isolated_region: 4-triangle free-floating island; all boundary edges are border; hk1 is always border (Branch 5) |
| [Me475](Me475.stp) | remove_a_border_edge hk2_equals_hp: degree-2 apex v0 in 2-triangle fan; hk2 wraps to hp (Branch 6) |
| [Me480](Me480.stp) | removeTriangles list_head_initialization: BFS init from T.head() on 2-triangle open-boundary mesh (Branch 1) |
| [Me481](Me481.stp) | removeTriangles null_edge_e1: triangle [v0,v0,v2] has zero-length e1 edge (v0→v0), e1-NULL precondition (Branch 2) |
| [Me482](Me482.stp) | removeTriangles null_edge_e2: triangle [v0,v1,v1] has zero-length e2 edge (v1→v1), e2-NULL precondition (Branch 3) |
| [Me483](Me483.stp) | removeTriangles null_edge_e3: triangle [v0,v1,v0] has zero-length e3 edge (v0→v0), e3-NULL precondition (Branch 4) |
| [Me484](Me484.stp) | removeTriangles triangle_removal: T.removeCell+delete t; collinear t2=[v0,v1,v2] is orphan to be removed (Branch 5) |
| [Me485](Me485.stp) | removeTriangles topology_invalidation: d_boundaries=d_handles=d_shells=1 after orphan removal; clean 2-triangle survivor mesh (Branch 6) |
| [Me490](Me490.stp) | sanitize_candidates empty_input: coincident v1==v3 share triangle t1; candidate_hedges_with_id empty on entry; return immediately (Branch 1) |
| [Me491](Me491.stp) | sanitize_candidates outer_group_iteration: two disjoint coincident groups (f1==f3, f2==f4); outer for-loop fires for fr_id=0 (Branch 2) |
| [Me492](Me492.stp) | sanitize_candidates inner_group_iteration: three disjoint coincident groups (g1==g4, g2==g5, g3==g6); inner for-loop runs >1 iteration per outer step (Branch 3) |
| [Me493](Me493.stp) | sanitize_candidates interval_overlap_detection: three coincident boundary vertices p0==p1==p2 at (1,0,0) produce overlapping group index ranges; erase triggered (Branch 4) |
| [Me494](Me494.stp) | sanitize_candidates recursive_resanitization: four coincident vertices r0==r1==r2==r3 at (1,0,0); erase triggers recursive sanitize_candidates call (Branch 5) |
| [Me495](Me495.stp) | sanitize_candidates range_size_comparison: three coincident boundary vertices u0==u1==u2 at (1,0,0); equal-range groups compared; second (sr_id) group erased (Branch 6) |
| [Me500](Me500.stp) | remove_almost_degenerate_faces needle_triangle: extreme edge-length ratio 1000:1 triggers is_needle_triangle_face (Branch 1) |
| [Me501](Me501.stp) | remove_almost_degenerate_faces needle_non_collapsible: extra shared neighbor violates link condition; flip path (Branch 2) |
| [Me502](Me502.stp) | remove_almost_degenerate_faces border_edge_needle: short edge on open boundary; Euler::remove_face path (Branch 3) |
| [Me503](Me503.stp) | remove_almost_degenerate_faces needle_flip_impossible: flip target edge already exists; deferred (Branch 4) |
| [Me504](Me504.stp) | remove_almost_degenerate_faces cap_triangle: angle at v2 ≈ 180° triggers is_cap_triangle_face (Branch 5) |
| [Me505](Me505.stp) | remove_almost_degenerate_faces cap_border_edge: cap long base on boundary; remove_face path (Branch 6) |
| [Me506](Me506.stp) | remove_almost_degenerate_faces cap_flip_fails: existing edge v2-v3 blocks flip; collapse fallback (Branch 7) |
| [Me507](Me507.stp) | remove_almost_degenerate_faces no_progress: clean mesh; something_was_done stays false; loop returns false (Branch 8) |
| [Me510](Me510.stp) | Edge.swap EDGE_SWAP_SAFE_VALIDITY: boundary edge (n=1, t2==NULL) blocks safe-mode swap; all three edges are boundary (Branch 1) |
| [Me511](Me511.stp) | Edge.swap EDGE_TOPOLOGY_EXTRACTION: interior diagonal (v0,v2) with two incident triangles; e1=nextEdge(t0) and e3=nextEdge(t1) extracted for cycle replacement (Branch 2) |
| [Me512](Me512.stp) | Edge.swap EDGE_ENDPOINT_SWAP: diagonal endpoints updated from (v0,v2) to opposite vertices (v1,v3); post-swap diagonal spans longer distance across quad (Branch 3) |
| [Me513](Me513.stp) | Edge.swap TRIANGLE_EDGE_REPLACEMENT: right-angle quad; t1->replaceEdge(e1,e3) and t2->replaceEdge(e3,e1) cross-links outer edges into new triangles (Branch 4) |
| [Me514](Me514.stp) | Edge.swap TRIANGLE_ORIENTATION_FLIP: inconsistent winding across shared diagonal (v0,v2); both triangles traverse v2→v0, n0=+z n1=-z; t1.invert()+t2.invert() restore consistency (Branch 5) |
| [Me515](Me515.stp) | Edge.swap INCIDENT_EDGE_UPDATE_E1: outer edges e1=(v1,v2) and e3=(v2,v3) each incident on one triangle; e1->replaceTriangle(t1,t2) and e3->replaceTriangle(t2,t1) complete adjacency update (Branch 6) |
| [Me520](Me520.stp) | iterativeEdgeSwaps selection_exists: partial selection of triangles; swaps restricted to IS_VISITED region (Branch 1) |
| [Me521](Me521.stp) | iterativeEdgeSwaps swap_candidate_filter: interior non-sharp non-boundary edge qualifies for swap queue (Branch 2) |
| [Me522](Me522.stp) | iterativeEdgeSwaps convergence_iteration: multi-pass swap loop (totits++ < 10) across 6-triangle grid (Branch 3) |
| [Me523](Me523.stp) | iterativeEdgeSwaps swap_improves_angle: thin non-Delaunay quad; flip of long diagonal improves min angle (Branch 4) |
| [Me524](Me524.stp) | iterativeEdgeSwaps swap_norm_alignment: non-planar fold; adjacent triangles have anti-parallel normals, swap rejected (Branch 5) |
| [Me525](Me525.stp) | iterativeEdgeSwaps convergence_fail: 4-triangle symmetric fan oscillates swap queue; totits reaches 10 (Branch 6) |
| [Me530](Me530.stp) | holeFilling::joinBoundaryLoops NULL_VERTEX_INPUT: all vertices interior; no boundary; Branch 1 returns NULL |
| [Me531](Me531.stp) | holeFilling::joinBoundaryLoops SAME_BOUNDARY_LOOP_NOJUSTCONNECT: gv and gw on same loop; Branch 2 returns NULL |
| [Me532](Me532.stp) | holeFilling::joinBoundaryLoops ADJACENT_VERTICES_JUSTCONNECT: gw is immediate boundary neighbor; Branch 3 inserts single triangle |
| [Me533](Me533.stp) | holeFilling::joinBoundaryLoops BOUNDARY_LOOP_LENGTH_ACCUMULATION: two-loop triangular annulus; perimeters tl1+tl2 accumulated before bridging (Branch 4) |
| [Me534](Me534.stp) | holeFilling::joinBoundaryLoops BALANCED_TRIANGULATION_CRITERION: two-loop square annulus; c1 vs c2 cost alternates between loops (Branch 5) |
| [Me535](Me535.stp) | holeFilling::joinBoundaryLoops PATCH_REFINEMENT: two-loop pentagon annulus; refine=true triggers refineSelectedHolePatches (Branch 6) |
| [Me540](Me540.stp) | checkAndRepair::removeDegenerateTriangles CAP_GEOMETRY_OV1: opposite vertex ov1 lies on inner segment of cap edge (T-junction triggers splitEdge) |
| [Me541](Me541.stp) | checkAndRepair::removeDegenerateTriangles CAP_GEOMETRY_OV2: second cap vertex ov2 also on inner segment (two adjacent T-junction caps both trigger splitEdge) |
| [Me542](Me542.stp) | checkAndRepair::removeDegenerateTriangles SINGLE_CAP_VERTEX: nov==1 — only one cap triangle adjacent; single cap vertex duplicated (splitvs[1] = splitvs[0]) |
| [Me543](Me543.stp) | checkAndRepair::removeDegenerateTriangles CAP_VERTEX_ORDER_DISTANCE: two caps; ov1 farther from e->v1 than ov2 causing swap of splitvs order |
| [Me544](Me544.stp) | checkAndRepair::removeDegenerateTriangles NEEDLE_EDGE_COINCIDENT_ENDPOINTS: edge (v1,v2) has coincident endpoints at same coordinate; needle triangle collapse |
| [Me545](Me545.stp) | checkAndRepair::removeDegenerateTriangles UNRESOLVABLE_DEGENERACY: collinear triangle resists all cap/needle repair; isExactlyDegenerate true after all passes (degn++) |
| [Me550](Me550.stp) | checkAndRepair::rebuildConnectivity EMPTY_MESH: single isolated vertex with no triangles; V.numels()==0 triggers early return (Branch 1) |
| [Me551](Me551.stp) | checkAndRepair::rebuildConnectivity VERTEX_GEOMETRIC_EQUALITY: v1 and v3 both at (1,0,0); v3->info set to v1 during sorted-walk (Branch 2) |
| [Me552](Me552.stp) | checkAndRepair::rebuildConnectivity VERTEX_POINTER_INDIRECTION_V1: e->v1 for p3 (=p1 at (2,0,0)) has info!=self after unification; v1 dereferenced to canonical (Branch 3) |
| [Me553](Me553.stp) | checkAndRepair::rebuildConnectivity VERTEX_POINTER_INDIRECTION_V2: e->v2 for q3 (=q1 at (3,0,0)) has info!=self after unification; v2 dereferenced to canonical (Branch 4) |
| [Me554](Me554.stp) | checkAndRepair::rebuildConnectivity DEGENERATE_TRIANGLE_DUPLICATE_VERTEX: t2=(r0,r2,r3) with r0==r2 at (0,0,0); v1==v2 after unification; triangle discarded (Branch 5) |
| [Me555](Me555.stp) | checkAndRepair::rebuildConnectivity FIXCONNECTIVITY_REQUESTED: two triangles sharing vertex s2 but no edge (orphan fan); fixconnectivity flag set; fixConnectivity() called (Branch 6) |
| [Me560](Me560.stp) | loopSubdivision midpoint_vs_full_relaxation: central vertex v6 fully interior; eligible for Loop-scheme vertex relaxation (Branch 1) |
| [Me561](Me561.stp) | loopSubdivision selection_constrained_vs_global: selected patch t0+t1+t2 vs unselected t3+t4; bridge edges n=2 (Branch 2) |
| [Me562](Me562.stp) | loopSubdivision sharp_edge_preservation: t0/t1 share crease edge (v1,v2) with steep dihedral; IS_SHARPEDGE branch triggered (Branch 3) |
| [Me563](Me563.stp) | loopSubdivision boundary_vs_interior_edge_split: 4-triangle strip mixing n=1 boundary and n=2 interior edges (Branch 4) |
| [Me564](Me564.stp) | loopSubdivision triangle_topology_after_split: 5-triangle fan; all spoke edges interior (n=2); MARK_VISIT fires on both new sub-triangles per split (Branch 5) |
| [Me565](Me565.stp) | loopSubdivision edge_swap_candidacy: diagonal (v2,v3) connects new midpoint v2 to old vertex v3; poor aspect ratio motivates IS_VISITED2 swap (Branch 6) |
| [Me570](Me570.stp) | Basic_TMesh.invertSelection seed_provided: t0 != NULL; BFS component-local invert from seed triangle (Branch 1) |
| [Me571](Me571.stp) | Basic_TMesh.invertSelection component_invert_direction: IS_VISITED(t0)=true → unmark=true; BFS unmarks pre-marked seed component (Branch 2) |
| [Me572](Me572.stp) | Basic_TMesh.invertSelection neighbor_t1_same_state: t1 of seed is unmarked neighbor; BFS enqueues via t1 edge path (Branch 3) |
| [Me573](Me573.stp) | Basic_TMesh.invertSelection neighbor_t2_same_state: t2 of seed is unmarked neighbor; BFS enqueues via t2 edge path (Branch 4) |
| [Me574](Me574.stp) | Basic_TMesh.invertSelection neighbor_t3_same_state: t3 of seed is unmarked neighbor; BFS enqueues via t3 edge path (Branch 5) |
| [Me575](Me575.stp) | Basic_TMesh.invertSelection global_invert: t0==NULL; FOREACHTRIANGLE flips VISITED bit on all 4 triangles (Branch 6) |
| [Me580](Me580.stp) | Basic_TMesh.createSubMeshFromSelection invalid_triangle_seed: seed t0 not IS_VISITED; extraction aborts, returns NULL (Branch 1) |
| [Me581](Me581.stp) | Basic_TMesh.createSubMeshFromSelection seed_provided: BFS from visited seed collects all visited neighbors (Branch 2) |
| [Me582](Me582.stp) | Basic_TMesh.createSubMeshFromSelection no_seed: NULL seed triggers global FOREACHTRIANGLE scan; two disconnected visited components collected (Branch 3) |
| [Me583](Me583.stp) | Basic_TMesh.createSubMeshFromSelection keep_reference: keep_ref=true preserves info pointers in extracted sub-mesh (Branch 4) |
| [Me584](Me584.stp) | Basic_TMesh.createSubMeshFromSelection edge_adjacency_boundary: selection-boundary interior edge becomes NULL adjacency in sub-mesh (Branch 5) |
| [Me585](Me585.stp) | Basic_TMesh.createSubMeshFromSelection empty_selection: zero triangles IS_VISITED; sT.numels()==0; sub-mesh deleted, returns NULL (Branch 6) |
| [Me590](Me590.stp) | holeFilling_TriangulateHole_edge_not_on_boundary: closed mesh has no boundary edge; TriangulateHole seed fails isOnBoundary check (Branch 1) |
| [Me591](Me591.stp) | holeFilling_TriangulateHole_angle_computation_failure: near-collinear boundary cycle; all candidate angles == DBL_MAX; gang check fires (Branch 2) |
| [Me592](Me592.stp) | holeFilling_TriangulateHole_euler_edge_triangle_failure: best-angle vertex v3 pinched between existing edges; EulerEdgeTriangle returns NULL; vertex marked bad (Branch 3) |
| [Me593](Me593.stp) | holeFilling_TriangulateHole_normal_computation_failure: saddle-shaped hole boundary produces anti-parallel fill normals summing to zero; nor.isNull fires (Branch 4) |
| [Me594](Me594.stp) | holeFilling_TriangulateHole_delaunay_constrained_swap: non-Delaunay fill diagonal triggers edge swap; sw++ fires (Branch 5) |
| [Me595](Me595.stp) | holeFilling_TriangulateHole_watson_insert_failure: L-shaped hole; interior insertion candidate falls in concave notch; watsonInsert returns NULL (Branch 6) |
| [Me600](Me600.stp) | merge_duplicated_vertices_in_boundary_cycle boundary_cycle_traversal: CGAL_precondition guard passes on valid boundary halfedge; 4-edge cycle traversal begins (Branch 1) |
| [Me601](Me601.stp) | merge_duplicated_vertices_in_boundary_cycle vertex_detection: detect_identical_mergeable_vertices finds coincident pair e1==e4 at (2,0,0) on boundary cycle (Branch 2) |
| [Me602](Me602.stp) | merge_duplicated_vertices_in_boundary_cycle merge_iteration: for-each loop over 2 coincident groups (f1==f4 at (1,0,0) and f2==f5 at (3,0,0)) fires twice (Branch 3) |
| [Me603](Me603.stp) | merge_duplicated_vertices_in_boundary_cycle merge_execution: internal::merge_vertices_in_range called for single group g1==g3 at (1,0,0); topological merge fires (Branch 4) |
| [Me604](Me604.stp) | merge_duplicated_vertices_in_boundary_cycle halfedge_advance: do-while traverses 6-edge boundary cycle (h1==h4 at (2,0,0)); start!=h check fires 6 times (Branch 5) |
| [Me610](Me610.stp) | is_cap_triangle_face degenerate_edge: first edge (v0,v1) has zero squared length; coincident endpoints trigger early-exit Branch 1 |
| [Me611](Me611.stp) | is_cap_triangle_face cap_scalar_product: near-180-degree cap vertex v2=(5,0.05,0) above base; scalar-product cap-detection Branch 2 fires |
| [Me612](Me612.stp) | is_cap_triangle_face handle_triplet slot 0: cap vertex v0=(5,0.05,0) at halfedge source p; angle approx 179.7 degrees; Branch 3 fires |
| [Me613](Me613.stp) | is_cap_triangle_face handle_triplet slot 1: cap vertex v1=(5,0.05,0) at halfedge target q; angle approx 179.7 degrees; Branch 4 fires |
| [Me614](Me614.stp) | is_cap_triangle_face handle_triplet slot 2: cap vertex v2=(5,0.05,0) at third vertex r; angle approx 179.7 degrees; Branch 5 fires |
| [Me620](Me620.stp) | removeRegion neighbor_t1_distance_check: seed t0 e1-neighbor t1 within L=2.5 of center (Branch 1) |
| [Me621](Me621.stp) | removeRegion neighbor_t2_distance_check: seed t0 e2-neighbor t2 within L=2.5 of center (Branch 2) |
| [Me622](Me622.stp) | removeRegion neighbor_t3_distance_check: seed t0 e3-neighbor t3 within L=2.5 of center (Branch 3) |
| [Me623](Me623.stp) | removeRegion region_traversal_order: 5-triangle fan; BFS enqueues FIFO, tail-traversal reverses (Branch 4) |
| [Me624](Me624.stp) | removeRegion triangle_unlink_removal: 3-triangle inner fan within L=2.0; unlinkTriangle fires for each (Branch 5) |
| [Me630](Me630.stp) | growSelection selected_triangle_vertex_mark: IS_VISITED(t0) marks v0,v1,v2 in 4-triangle fan (Branch 1) |
| [Me631](Me631.stp) | growSelection vertex_marking: MARK_VISIT(v1); MARK_VISIT(v2); MARK_VISIT(v3) in 5-triangle fan (Branch 2) |
| [Me632](Me632.stp) | growSelection unselected_triangle_neighbor_check: !IS_VISITED(t) enters Branch 3; 3-triangle strip (Branch 3) |
| [Me633](Me633.stp) | growSelection vertex_neighbor_selection: IS_VISITED(v2) selects t1; IS_VISITED(v0\|\|v1) selects t2 (Branch 4) |
| [Me634](Me634.stp) | growSelection vertex_unmark_cleanup: FOREACHVERTEX UNMARK_VISIT fires 7 times; 6-triangle fan (Branch 5) |
| [Me640](Me640.stp) | holeFilling::fillSmallBoundaries SELECTION_PRESENT: pre-selected triangles constrain hole filling (Branch 1) |
| [Me641](Me641.stp) | holeFilling::fillSmallBoundaries VERTEX_ON_BOUNDARY: v->isOnBoundary() true for hole boundary vertex (Branch 2) |
| [Me642](Me642.stp) | holeFilling::fillSmallBoundaries BOUNDARY_CROSSING_CONSTRAINT: IS_BIT(h0,6) forces grd to nbe+1; hole skipped (Branch 3) |
| [Me643](Me643.stp) | holeFilling::fillSmallBoundaries SMALL_BOUNDARY_THRESHOLD: 3-edge hole; grd=3 <= nbe; added to bdrs (Branch 4) |
| [Me644](Me644.stp) | holeFilling::fillSmallBoundaries PATCH_TRIANGULATION_WITH_REFINEMENT: 4-edge hole filled + Steiner point refined (Branch 5) |
| [Me650](Me650.stp) | removeEdges list_head_initialization: non-empty mesh; E.head() initialises traversal pointer at first edge (Branch 1) |
| [Me651](Me651.stp) | removeEdges null_vertex_v1: degenerate edge with v1 coincident to v0 at (0,0,0); proxy for e->v1==NULL (Branch 2) |
| [Me652](Me652.stp) | removeEdges null_vertex_v2: degenerate edge with v2 coincident to v1 at (3,0,0); proxy for e->v2==NULL (Branch 3) |
| [Me653](Me653.stp) | removeEdges edge_removal: zero-length edge (v0==v1 at (1,1,0)) in degenerate triangle; E.removeCell+delete path (Branch 4) |
| [Me654](Me654.stp) | removeEdges topology_invalidation: two disconnected shells; orphaned edge (a0==a1) triggers d_boundaries=d_handles=d_shells=1 (Branch 5) |
| [Me660](Me660.stp) | merge_duplicate_points_in_polygon_soup empty_input: zero-polygon soup; ini_points_n==0 causes immediate return; single isolated vertex as structural contrast (Branch 1) |
| [Me661](Me661.stp) | merge_duplicate_points_in_polygon_soup point_dedup_scan: coincident p1==p3 at (1,0,0); second insert into point_to_id fails (is_insert_successful==false) (Branch 2) |
| [Me662](Me662.stp) | merge_duplicate_points_in_polygon_soup new_unique_point: all four vertices distinct; every insert succeeds and id==unique_points.size() fires for each (Branch 3) |
| [Me663](Me663.stp) | merge_duplicate_points_in_polygon_soup merge_needed_check: 5 input points but 4 unique (u1==u4 at (1,0,0)); unique_points.size()!=ini_points_n triggers remap (Branch 4) |
| [Me664](Me664.stp) | merge_duplicate_points_in_polygon_soup polygon_remap: w1==w4 at (1,0,0); point_index[4] remapped to 1; polygon[i]=point_index[polygon[i]] rewrites t2 and t3 (Branch 5) |
| [Me670](Me670.stp) | mergeCoincidentEdges BOUNDARY_VERTEX_CLASSIFICATION: open mesh; every edge n=1 triggers MARK_BIT(v,5) on both endpoints (Branch 1) |
| [Me671](Me671.stp) | mergeCoincidentEdges VERTEX_DUPLICATION_AT_V1: boundary edge v1 has non-self info pointer (a1 coincident with b0); redirect to canonical representative (Branch 2) |
| [Me672](Me672.stp) | mergeCoincidentEdges VERTEX_DUPLICATION_AT_V2: boundary edge v2 has non-self info pointer (p1 coincident with q1); redirect to canonical representative (Branch 3) |
| [Me673](Me673.stp) | mergeCoincidentEdges EDGE_DUPLICATION_BOUNDARY: two boundary edges (c0,c1) and (d0,d1) at identical coordinates form a stitchable seam; vtxEdgeCompare selects canonical (Branch 4) |
| [Me674](Me674.stp) | mergeCoincidentEdges REDUNDANT_EDGE_REMOVAL: duplicate seam edge (f0,f1) has info redirected to canonical (e0,e1); replaceEdge redirects triangle reference (Branch 5) |
| [Me680](Me680.stp) | TriangulateHole@L98 EDGE_NOT_ON_BOUNDARY: closed tetrahedron; all edges n==2; no boundary edge; return 0 (Branch 1) |
| [Me681](Me681.stp) | TriangulateHole@L98 ANGLE_COMPUTATION_FAILURE: gang==DBL_MAX; boundary loop v0-v1-v2 collinear (180-degree angle); all candidates degenerate; return 0 (Branch 2) |
| [Me682](Me682.stp) | TriangulateHole@L98 EULER_EDGE_TRIANGLE_FAILURE: interior fan pre-uses (v0,v1); sub-hole [v1,v2,v3] fill attempt rejected; MARK_BIT(v2,5) (Branch 3) |
| [Me683](Me683.stp) | TriangulateHole@L98 DELAUNAY_SWAP_IMPROVES_ANGLE: diamond hole v0-v1-v2-v3; short diagonal (v1,v3) yields needle triangles; delaunayMinAngle()<=ang; swap+fast=1 (Branch 4) |
| [Me684](Me684.stp) | TriangulateHole@L98 OPTIMIZATION_TIMEOUT: 12-gon boundary hole; swap-budget i<0; "taking too long"; break optimization (Branch 5) |
| [Me690](Me690.stp) | connected_component loop_control: 5-triangle zigzag strip forces BFS while-loop to cycle 5 times |
| [Me691](Me691.stp) | connected_component visited_vertex_dedup: 4-triangle fan ring where f3 is reachable via two BFS paths |
| [Me692](Me692.stp) | connected_component iteration_construct: center triangle has 3 neighbors discovered via for-loop over halfedges |
| [Me693](Me693.stp) | connected_component logic_guard_ecmap: constrained edge (v0,v2) prevents BFS crossing between t0 and t1 |
| [Me694](Me694.stp) | connected_component null_face_check: open-boundary mesh; BFS encounters null_face at every boundary halfedge |
| [Me700](Me700.stp) | bridgeBoundaries same_edge_or_non_boundary: interior edge (v0,v1) shared by 2 triangles; isOnBoundary() false, bridge returns NULL (Branch 1) |
| [Me701](Me701.stp) | bridgeBoundaries common_vertex_exists: boundary edges (v0,v2) and (v2,v3) share vertex v2; single-triangle EulerEdgeTriangle bridge (Branch 2) |
| [Me702](Me702.stp) | bridgeBoundaries gve_endpoint_selection: gve->t1 non-NULL selects gve->v1 as free endpoint; disjoint boundary edges on separate patches (Branch 3) |
| [Me703](Me703.stp) | bridgeBoundaries gwe_endpoint_selection: gwe->t1 non-NULL selects gwe->v2 as free endpoint; disjoint boundary edges on separate patches (Branch 4) |
| [Me704](Me704.stp) | bridgeBoundaries two_triangle_bridge: disjoint boundary edges (p1,p2) and (q0,q2) bridged by CreateEdge x3 + CreateTriangle x2 (Branch 5) |
| [Me710](Me710.stp) | Basic_TMesh.removeVertices list_head_initialization: V.head() called on 3-vertex mesh; traversal begins (Branch 1) |
| [Me711](Me711.stp) | Basic_TMesh.removeVertices orphan_vertex_check: isolated vertex v4 has e0==NULL; check fires (Branch 2) |
| [Me712](Me712.stp) | Basic_TMesh.removeVertices vertex_removal: V.removeCell+delete fires for each of 2 isolated vertices v3,v4 (Branch 3) |
| [Me713](Me713.stp) | Basic_TMesh.removeVertices topology_invalidation: d_boundaries=d_handles=d_shells=1 after isolated v4 removed (Branch 4) |
| [Me720](Me720.stp) | Basic_TMesh.safeCoordBackApproximation overlapping-edge detection: coplanar triangles with overlapping interiors; nos counter incremented (Branch 1) |
| [Me721](Me721.stp) | Basic_TMesh.safeCoordBackApproximation opposite-vertex selection: small-area triangle apex jittered; ov2 chosen because squaredArea(t1) < squaredArea(t0) (Branch 2) |
| [Me722](Me722.stp) | Basic_TMesh.safeCoordBackApproximation jitter escape condition: overlapping apex trapped inside large triangle; 26-direction jitter scan exercised (Branch 3) |
| [Me723](Me723.stp) | Basic_TMesh.safeCoordBackApproximation convergence check: two independent overlapping pairs; nos decreases across iterations confirming nos<pnos progress (Branch 4) |
| [Me730](Me730.stp) | checkAndRepair::meshclean DEGENERACY_REMOVAL_FAILURE: zero-area collinear triangle resists strongDegeneracyRemoval (branch 1) |
| [Me731](Me731.stp) | checkAndRepair::meshclean INTERSECTION_REMOVAL_FAILURE: overlapping coplanar triangle pair resists strongIntersectionRemoval (branch 2) |
| [Me732](Me732.stp) | checkAndRepair::meshclean BOTH_PASSES_SUCCEEDED: two clean separated triangles; ni=true, nd=true, both passes trivially succeed (branch 3) |
| [Me733](Me733.stp) | checkAndRepair::meshclean REMAINING_DEGENERACY_AFTER_SUCCESS: residual zero-area collinear face after ni && nd succeed; ni set false (branch 4) |
| [Me740](Me740.stp) | TriangulateHole_L439_edge_not_on_boundary: closed tetrahedral mesh; every edge interior (n=2); !e->isOnBoundary() fires; returns 0 (Branch 1) |
| [Me741](Me741.stp) | TriangulateHole_L439_single_vertex_hole: 3-edge boundary loop; nextEdge and prevEdge both boundary; single-vertex hole cannot be triangulated; return 0 (Branch 2) |
| [Me742](Me742.stp) | TriangulateHole_L439_angle_computation_failure: 4-vertex collinear hole boundary; interior angles at h1,h2 are 180 deg; gang stays DBL_MAX; return 0 (Branch 3) |
| [Me743](Me743.stp) | TriangulateHole_L439_euler_edge_triangle_failure: proposed triangle edges already interior (n=2); EulerEdgeTriangle returns NULL; MARK_BIT(v,5); continue (Branch 4) |
| [Me750](Me750.stp) | simplify_polygons_in_polygon_soup polygon_iteration: for-loop body entered for each of 2 polygons in soup (Branch 1) |
| [Me751](Me751.stp) | simplify_polygons_in_polygon_soup degenerate_polygon_skip: all-same-index triangle (v0,v0,v0) represents size-1 polygon; continue fired (Branch 2) |
| [Me752](Me752.stp) | simplify_polygons_in_polygon_soup consecutive_duplicate_removal: triangle (v0,v0,v1) has consecutive duplicate at index 0-1; simplify_polygon erases copy (Branch 3) |
| [Me753](Me753.stp) | simplify_polygons_in_polygon_soup modification_count: two consecutive-duplicate triangles each fire simplify_polygon; simplified_polygons_n incremented twice (Branch 4) |
| [Me760](Me760.stp) | retriangulateVT_triangle_normal_accumulation: 5-triangle fan around hub v0; normals accumulated via nor=nor+t->getNormal() for each incident triangle (Branch 1) |
| [Me761](Me761.stp) | retriangulateVT_hole_triangulation: 3-triangle wall fan around hub v3; inner hole [v0,v1,v2] filled by TriangulateHole(e0, &nor) (Branch 2) |
| [Me762](Me762.stp) | retriangulateVT_retriangulation_quality_check: new triangle t0=(v0,v1,v2) is exactly degenerate (collinear at y=0); quality check fires break (Branch 3) |
| [Me763](Me763.stp) | retriangulateVT_retriangulation_rollback: duplicate triangle t3==t0=(v0,v1,v2) causes quality check failure; i<nt triggers rollback, original VT restored (Branch 4) |
| [Me770](Me770.stp) | is_needle_triangle_face aspect_ratio_below_threshold: near-equilateral triangle; aspect ratio < needle threshold; res==-1 returns null_halfedge (Branch 1) |
| [Me771](Me771.stp) | is_needle_triangle_face shortest_edge_e0: needle triangle v0-v1 base 0.01; e0 shortest; res==0 returns h (Branch 2) |
| [Me772](Me772.stp) | is_needle_triangle_face shortest_edge_e1: needle triangle v1-v2 base 0.01; e1 shortest; res==1 returns next(h,tm) (Branch 3) |
| [Me773](Me773.stp) | is_needle_triangle_face shortest_edge_e2: needle triangle v2-v0 base 0.01; e2 shortest; res==2 returns prev(h,tm) (Branch 4) |
| [Me780](Me780.stp) | polygon_soup_to_polygon_mesh orientation_inconsistency: adjacent t0=(v0,v1,v2) CCW and t1=(v1,v3,v2) opposing winding trigger orient_polygon_soup (Branch 1) |
| [Me781](Me781.stp) | polygon_soup_to_polygon_mesh point_to_vertex_output_iterator: clean consistent-winding 2-triangle soup; point→vertex index map recorded for p0-p3 (Branch 2) |
| [Me782](Me782.stp) | polygon_soup_to_polygon_mesh polygon_to_face_output_iterator: clean consistent-winding 2-triangle soup; polygon→face descriptor map recorded for t0,t1 (Branch 3) |
| [Me790](Me790.stp) | PMP.non_manifold_vertices nonmanifold_vertex_detection: bowtie hub vertex with 2 disconnected umbrella sectors; 4 border halfedges at hub trigger sector enumeration (Branch 1) |
| [Me791](Me791.stp) | PMP.non_manifold_vertices umbrella_sector_boundary: open-mesh pinch vertex; border halfedge at sector boundary triggers is_border; 3-triangle sector A + 1-triangle sector B (Branch 2) |
| [Me792](Me792.stp) | PMP.non_manifold_vertices visited_umbrella_detection: 3-sector bowtie hub; outer loop re-encounters visited halfedges; visited_set skip fires for already-enumerated sectors (Branch 3) |
| [Me800](Me800.stp) | is_polygon_soup_a_polygon_mesh duplicate_vertex_in_polygon: triangle [v0,v1,v0] has repeated vertex index (Branch 1) |
| [Me801](Me801.stp) | is_polygon_soup_a_polygon_mesh non_manifold_edge: edge (v0,v1) shared by 3 triangles marks edge singular (Branch 2) |
| [Me802](Me802.stp) | is_polygon_soup_a_polygon_mesh orientation_consistency: t0 and t1 both traverse halfedge v1→v2; fill_edge_map returns INCOMPATIBLE_ORIENTATION (Branch 3) |
| [Me810](Me810.stp) | StarTriangulateHole_edge_not_on_boundary: closed tetrahedron; every edge n==2; !e->isOnBoundary() returns 0 (Branch 1) |
| [Me811](Me811.stp) | StarTriangulateHole_boundary_loop_closure: 3-vertex hole in fan mesh; nextOnBoundary traversal returns to start; v==e->v1 exits loop (Branch 2) |
| [Me812](Me812.stp) | StarTriangulateHole_barycenter_computation: 5-vertex pentagonal hole; np=np+(*v) accumulates all 5 boundary vertices; barycenter placed at centroid (Branch 3) |
| [Me820](Me820.stp) | does_polygon_soup_self_intersect_duplicate_point_presence: coincident v0==v3 at (0,0,0); merge_duplicate_points fires before SI check (Branch 1) |
| [Me821](Me821.stp) | does_polygon_soup_self_intersect_polygon_type_mixed: needle triangle (aspect >> 1) simulates non-triangle-polygon pre-condition; triangulate_polygons branch fires (Branch 2) |
| [Me822](Me822.stp) | does_polygon_soup_self_intersect_intersection_detection: crossing XY/XZ triangle pair in soup triggers triangle_soup_self_intersections (Branch 3) |
| [Me830](Me830.stp) | is_non_manifold_vertex border-incident-null-face: boundary vertex v0 has exactly one umbrella sector; border halfedge counted but threshold not exceeded (Branch 1) |
| [Me831](Me831.stp) | is_non_manifold_vertex null-face-multiplicity: bowtie hub v0 shared by two disconnected fans; border_counter>1 fires (Branch 2) |
| [Me832](Me832.stp) | is_non_manifold_vertex cycle-break-condition: interior vertex v0 in closed 4-triangle fan; halfedge ring completes full cycle via break (Branch 3) |
| [Me840](Me840.stp) | duplicate_non_manifold_vertices halfedge-visitation-tracking: bowtie hub visited_halfedges.insert skips already-processed halfedge ring (Branch 1) |
| [Me841](Me841.stp) | duplicate_non_manifold_vertices vertex-occurrence-detection: three-sector pinch hub re-encountered in visited_vertices across half-cycles; null_h sentinel fires (Branch 2) |
| [Me842](Me842.stp) | duplicate_non_manifold_vertices non-manifold-class-confirmation: hub found in known_nm_vertices set; duplicate vertex operation proceeds (Branch 3) |
| [Me850](Me850.stp) | does_bound_a_volume connectivity_broken: tetrahedron with base removed; boundary cycle present; is_closed returns false (Branch 1) |
| [Me851](Me851.stp) | does_bound_a_volume orientation_inconsistent: closed tetrahedron; base wound CW; adjacent normals antiparallel; orientation check fails (Branch 2) |
| [Me852](Me852.stp) | does_bound_a_volume self_intersection: XY/XZ crossing fans in closed 8-tri manifold; interior overlap along X-axis; does_self_intersect true (Branch 3) |
| [Me860](Me860.stp) | strongIntersectionRemoval intersection-detection trigger: selectIntersectingTriangles non-empty; enters removal loop (Branch 1) |
| [Me861](Me861.stp) | strongIntersectionRemoval iteration limit: dual persistent SI piercers exhaust max_iters (Branch 2) |
| [Me862](Me862.stp) | strongIntersectionRemoval selection-growth depth: multi-ring growSelection expansion for n=1,2,... (Branch 3) |
| [Me870](Me870.stp) | selectIntersectingTriangles selected-vs-full-mesh: isSelection restricts spatial scan to pre-selected intersecting pair (Branch 1) |
| [Me871](Me871.stp) | selectIntersectingTriangles cell-saturation: 15-triangle dense cluster forces DI_MAX_TRIS_PER_CELL subdivision; embedded SI pair (Branch 2) |
| [Me872](Me872.stp) | selectIntersectingTriangles spatial-recursion vs termination: fork() at outer cells then todo.appendTail at leaf cell containing SI pair (Branch 3) |
| [Me880](Me880.stp) | duplicateNonManifoldVertices NONMANIFOLD_VERTEX_AT_V1: bowtie vertex v0 missing from edge VE list (Branch 1) |
| [Me881](Me881.stp) | duplicateNonManifoldVertices NONMANIFOLD_VERTEX_AT_V2: bowtie vertex v0 missing from edge VE list as v2 (Branch 2) |
| [Me882](Me882.stp) | duplicateNonManifoldVertices NONMANIFOLD_VERTICES_PRESENT: at least one non-manifold vertex found; dv>0 marks topology dirty (Branch 3) |
| [Me890](Me890.stp) | merge_duplicated_vertices_in_boundary_cycles boundary_cycle_discovery: open mesh; extract_boundary_cycles finds 1 boundary cycle; coincident v1==v3 at (2,0,0) (Branch 1) |
| [Me891](Me891.stp) | merge_duplicated_vertices_in_boundary_cycles cycle_iteration: 2-patch mesh; extract_boundary_cycles finds 2 boundary cycles; for-loop iterates both; coincident pairs on each (Branch 2) |
| [Me892](Me892.stp) | merge_duplicated_vertices_in_boundary_cycles merge_delegation/closed_mesh_noop: closed tetrahedron; all edges n=2; extract_boundary_cycles returns empty; for-loop never executes (Branch 3) |
| [Me900](Me900.stp) | orient_triangle_soup_with_reference_triangle_soup reference_degenerate_triangle: collinear reference triangle (area=0) skipped by is_degenerate check; only valid reference face used (Branch 1) |
| [Me901](Me901.stp) | orient_triangle_soup_with_reference_triangle_soup closest_face_search: three-sector fan; AABB closest_point_and_primitive returns valid reference face for each query centroid (Branch 2) |
| [Me902](Me902.stp) | orient_triangle_soup_with_reference_triangle_soup orientation_flip_decision: t1 CW winding gives normal -Z; dot product with reference normal +Z is negative; t1 flipped (Branch 3) |
| [Me910](Me910.stp) | di_cell.selectIntersections redundant-pair-test-detection: crossing pair cached in t->info; containsNode returns true → second-cell test skipped (Branch 1) |
| [Me911](Me911.stp) | di_cell.selectIntersections proper-vs-improper-intersection: justproper flag; touching shared-vertex pair is improper; transverse crossing is proper (Branch 2) |
| [Me912](Me912.stp) | di_cell.selectIntersections info-list-initialization: hub triangle intersects two others; NULL→new List then reuse (Branch 3) |
| [Me920](Me920.stp) | keep_largest component_count_mismatch: desired_num > total_components → return 0 |
| [Me921](Me921.stp) | keep_largest component_size_criterion: face_size >= threshold retains large component |
| [Me922](Me922.stp) | keep_largest dry_run_mode: dry_run=true; component identified but mesh not mutated |
| [Me923](Me923.stp) | keep_largest output_iterator_presence: removed component faces recorded via output_iterator |
| [Me930](Me930.stp) | PMP.orient z-extremum-selection: high-Z tetra updates ref_cc_id over low-Z tetra (Branch 1) |
| [Me931](Me931.stp) | PMP.orient self-intersection-component-skip: cc_to_handle exhausted; loop-break fires (Branch 2) |
| [Me932](Me932.stp) | PMP.orient self-intersecting-pair-detection: Component B shell has t4 pierced by t5; self_intersecting_cc.insert() fires (Branch 3) |
| [Me933](Me933.stp) | PMP.orient orientation-assignment-by-nesting: inner tetra ON_BOUNDED_SIDE; inward orientation assigned (Branch 4) |
| [Me940](Me940.stp) | orient_polygon_soup initial_point_count: initial_nb_pts = points.size() = 4 captured at entry (Branch 1) |
| [Me941](Me941.stp) | orient_polygon_soup edge_map_fill: four-triangle fan; orienter.fill_edge_map() populates 4 interior shared edges (Branch 2) |
| [Me942](Me942.stp) | orient_polygon_soup polygon_orientation_pass: t0 CCW + t1 CW share edge (v1,v2); orienter.orient() flips t1 via DFS (Branch 3) |
| [Me943](Me943.stp) | orient_polygon_soup vertex_duplication: bowtie at v0; orienter.duplicate_singular_vertices() splits v0 into 2 copies (Branch 4) |
| [Me944](Me944.stp) | orient_polygon_soup manifoldness_check: clean 3-triangle manifold strip; initial_nb_pts==points.size()==5 → returns true (Branch 5) |
| [Me950](Me950.stp) | Basic_TMesh.checkGeometry memory_allocation_failure: near-coincident vertex pair v0/v6; varr==NULL alloc guard (Branch 1) |
| [Me951](Me951.stp) | Basic_TMesh.checkGeometry duplicate_vertices: v0==v3 at (0,0,0) in separate triangles, no edge (Branch 2) |
| [Me952](Me952.stp) | Basic_TMesh.checkGeometry duplicate_vertex_with_edge: v0==v1 at (1,0,0), zero-length edge (Branch 3) |
| [Me953](Me953.stp) | Basic_TMesh.checkGeometry edge_alloc_failure: coincident edge pair; evarr==NULL alloc guard (Branch 4) |
| [Me954](Me954.stp) | Basic_TMesh.checkGeometry duplicate_edges: edge (v0,v1) spatially coincident with (v3,v4) (Branch 5) |
| [Me955](Me955.stp) | Basic_TMesh.checkGeometry degenerate_angle_180_degrees: collinear triangle, interior angle PI at middle vertex (Branch 6) |
| [Me956](Me956.stp) | Basic_TMesh.checkGeometry dihedral_angle_180: adjacent coplanar triangles sharing edge (v1,v2), dihedral = PI (Branch 7) |
| [Me960](Me960.stp) | CreateUnorientedTriangle_e1_slot_check: e1's first free t-slot (t1 or t2) assigned without orientation |
| [Me961](Me961.stp) | CreateUnorientedTriangle_e2_slot_check: e2's first free t-slot (t1 or t2) assigned without orientation |
| [Me962](Me962.stp) | CreateUnorientedTriangle_e3_slot_check: e3's first free t-slot (t1 or t2) assigned without orientation |
| [Me963](Me963.stp) | CreateUnorientedTriangle_unoriented_creation: newTriangle(e1,e2,e3) without orientation check |
| [Me964](Me964.stp) | CreateUnorientedTriangle_triangle_adjacency_assignment: *at1=*at2=*at3=tt links edge slots to triangle |
| [Me965](Me965.stp) | CreateUnorientedTriangle_mesh_list_append: T.appendHead(tt) inserts triangle into list T |
| [Me970](Me970.stp) | deselectConnectedComponent_seed_enqueue: todo.appendHead(t0) initializes BFS deselection from seed triangle (Branch 1) |
| [Me971](Me971.stp) | deselectConnectedComponent_visited_triangle_check: IS_VISITED(t) guard skips unselected neighbor; only t0+t1 deselected (Branch 2) |
| [Me972](Me972.stp) | deselectConnectedComponent_neighbor_t1_dequeue: t1 selected + edge (v0,v2) not sharp → todo.appendHead(t1) fires Branch 3 |
| [Me973](Me973.stp) | deselectConnectedComponent_neighbor_t2_dequeue: t2 selected + edge (v0,v3) not sharp → todo.appendHead(t2) fires Branch 4 |
| [Me974](Me974.stp) | deselectConnectedComponent_neighbor_t3_dequeue: t3 selected + edge (v1,v2) not sharp → todo.appendHead(t3) fires Branch 5 |
| [Me975](Me975.stp) | deselectConnectedComponent_unmark_and_count: UNMARK_VISIT(t); ns++ fires 4 times across all-selected 4-triangle patch (Branch 6) |
| [Me980](Me980.stp) | merge_reversible_connected_components component_area_filter: micro-triangle CC-B (area≈5e-9) below threshold; marked as mergeable (Branch 1) |
| [Me981](Me981.stp) | merge_reversible_connected_components orientation_flip_feasibility: Patch-B wound CW vs Patch-A CCW; flip Patch-B enables stitch (Branch 2) |
| [Me982](Me982.stp) | merge_reversible_connected_components stitching_compatibility_check: border edge endpoint coincident at (1,0,0); stitch_borders welds components (Branch 3) |
| [Me990](Me990.stp) | orient_triangle_soup_with_reference_triangle_mesh concurrency_strategy: Sequential_tag / Parallel_tag dispatch before per-triangle orientation loop (Branch 1) |
| [Me991](Me991.stp) | orient_triangle_soup_with_reference_triangle_mesh aabb_tree_construction: AABB tree built from non-empty reference mesh with clear bounding box (Branch 2) |
| [Me992](Me992.stp) | orient_triangle_soup_with_reference_triangle_mesh triangle_degeneracy: collinear degenerate reference triangle skipped by is_degenerate_triangle_face (Branch 3) |
| [Me1000](Me1000.stp) | remove_connected_components.by_face_range Iteration_construct: loop enters for each face in range; 3-triangle component A + isolated triangle B (Branch 1) |
| [Me1001](Me1001.stp) | remove_connected_components.by_face_range Logic_guard: unconstrained vertices (!get(is_cst,v)) in face_range; 4-tri component A + 2-tri unconstrained component B (Branch 2) |
| [Me1002](Me1002.stp) | remove_connected_components.by_face_range Alternative_path: constrained vertex v7 triggers else fallback; 2-tri component A + 3-tri component B with constraint (Branch 3) |
| [Me1010](Me1010.stp) | run_stitch_borders vertex-merge-necessity: h1_tgt representative differs from v_to_keep; redirect to master (Branch 1) |
| [Me1011](Me1011.stp) | run_stitch_borders second-vertex-pair-distinct: h2_src representative differs from h1_tgt master; conditional merge fires (Branch 2) |
| [Me1012](Me1012.stp) | run_stitch_borders second-target-merge-necessity: h2_tgt representative differs from second-endpoint master; union_find merge fires (Branch 3) |
| [Me1013](Me1013.stp) | run_stitch_borders opposite-edge-source-merge: h1_src representative distinct from h2_tgt master; merge completes two-endpoint stitch (Branch 4) |
| [Me1020](Me1020.stp) | compatible_orientations nesting-constraint detector: usage-mode-dispatch on single closed component |
| [Me1021](Me1021.stp) | compatible_orientations nesting-constraint detector: nested_cc_per_cc_shared non-empty (two nested closed tetrahedra) |
| [Me1022](Me1022.stp) | compatible_orientations nesting-constraint detector: nesting_levels[child]==parent+1 direct parent-child relationship |
| [Me1030](Me1030.stp) | split_connected_components component_subdivision: two disconnected triangles each extracted to a new mesh (Branch 1) |
| [Me1031](Me1031.stp) | remove_invalid_polygons_degenerate_filter: duplicate-vertex triangle [v0,v0,v1] triggers remove_if predicate (Branch 1) |
| [Me1032](Me1032.stp) | remove_invalid_polygons_erase_execution: two degenerate triangles erased by polygons.erase(rit, end()); two valid triangles remain (Branch 2) |
| [Me1040](Me1040.stp) | stitch_borders border-component-independence: per_cc routing dispatches per-component vs global; two disconnected open patches (Branch 1) |
| [Me1041](Me1041.stp) | stitch_borders non-border-edge-skip: is_border check skips interior halfedges; open fan mesh with mixed interior/boundary edges (Branch 2) |
| [Me1042](Me1042.stp) | stitch_borders per-component-boundary-segregation: border_edges_per_cc appends boundary halfedge to per-CC slot; three disconnected open triangles (Branch 3) |
| [Me1043](Me1043.stp) | stitch_borders processing-strategy-dispatch: per_cc for-loop iterates over num_cc=2 connected components; two open two-triangle patches (Branch 4) |
| [Me1044](Me1044.stp) | stitch_borders non-manifold-pair-filter: manifold_halfedge_pairs filter rejects candidate that would create edge shared by 3 triangles (Branch 5) |
| [Me1045](Me1045.stp) | stitch_borders halfedge-pair-orientation: hd_kpr canonical swap fires for non-canonical halfedge pair; two patches with reversed coincident boundary edge (Branch 6) |
| [Me1046](Me1046.stp) | stitch_borders single-pass-manifold-filtering: global mode (per_cc=false) single CC; manifold_halfedge_pairs called once for all collected pairs (Branch 7) |
| [Me1050](Me1050.stp) | merge_duplicate_polygons erase_policy_selection KEEP_ONE_IF_ODD: 3-copy group (odd→keep1) + 2-copy group (even→erase all) (Branch 1) |
| [Me1051](Me1051.stp) | merge_duplicate_polygons orientation_requirement: two reversed-winding pairs; same_orientation flag controls merge (Branch 2) |
| [Me1052](Me1052.stp) | merge_duplicate_polygons duplicate_collection: 4-copy group A + 3-copy group B; hash+equality scan collects both (Branch 3) |
| [Me1053](Me1053.stp) | merge_duplicate_polygons early_exit_empty: 4-triangle partial-tetrahedron soup with all-distinct vertex triples; returns 0 immediately (Branch 4) |
| [Me1054](Me1054.stp) | merge_duplicate_polygons duplicate_group_iteration: 4 independent duplicate pairs; outer while loop iterates 4 times (Branch 5) |
| [Me1055](Me1055.stp) | merge_duplicate_polygons keep_decision KEEP_ONE: 5-copy group; i=1 retains copy 0, removes copies 1-4 (Branch 6) |
| [Me1060](Me1060.stp) | duplicate_polygons removal_iteration: 5-copy group, inner loop runs 4 times (Branch 7) |
| [Me1061](Me1061.stp) | duplicate_polygons treated_skip: two independent duplicate groups; second group hits treated[] continue guard (Branch 8) |
| [Me1062](Me1062.stp) | duplicate_polygons swap_to_end: 3 duplicates at non-contiguous positions 0,2,5; swap_position diverges from polygon_to_remove_pos (Branch 9) |
| [Me1063](Me1063.stp) | duplicate_polygons mark_treated: two groups; treated[] bit written for each removed polygon across both groups (Branch 10) |
| [Me1064](Me1064.stp) | duplicate_polygons final_erase: two groups (sizes 2 and 3) both removed by single polygons.erase() call (Branch 11) |
| [Me1070](Me1070.stp) | filter_stitchable_pairs edge-occurrence-limit: two-patch boundary with single coincident-edge pair; count=1 boundary slots confirm manifold safety (Branch 1) |
| [Me1071](Me1071.stp) | filter_stitchable_pairs border-two-edge-exception: two border halfedges on coincident boundary edge; both border → manifold-safe stitch accepted (Branch 2) |
| [Me1072](Me1072.stp) | filter_stitchable_pairs multi-edge-vertex-disqualification: 3 coincident boundary halfedges on same merged edge; default case marks all vertices unstitchable (Branch 3) |
| [Me1073](Me1073.stp) | filter_stitchable_pairs vertex-pair-safety-check: contaminating triple-edge marks e1/e2 unstitchable (Branch 3); victim pair excluded because endpoint in unstitchable_vertices (Branch 4) |
| [Me1080](Me1080.stp) | remove_degenerate_faces no_degenerate_faces: three non-degenerate triangles; degenerate_face_set.empty() early return (Branch 1) |
| [Me1081](Me1081.stp) | remove_degenerate_faces all_faces_degenerate: two collinear zero-area triangles; degenerate_face_set.size()==faces_size clear-all path (Branch 2) |
| [Me1082](Me1082.stp) | remove_degenerate_faces adjacent_degenerate_faces_missed: three collinear triangles in chain; faces_to_visit walk expands partial range (Branch 3) |
| [Me1083](Me1083.stp) | remove_degenerate_faces null_edge_face_detection: zero-length edge in t0 induces collinear degeneracy in adjacent t1; is_degenerate_triangle_face(adj_fd) fires (Branch 4) |
| [Me1084](Me1084.stp) | remove_degenerate_faces border_degenerate_face: collinear t1 shares interior edge with clean t0; is_border(opposite) triggers border_deg_faces queuing (Branch 5) |
| [Me1085](Me1085.stp) | remove_degenerate_faces degenerate_edge_in_face: needle triangle with zero-length edge (n1==n2 at (3,0,0)); is_degenerate_edge fires → remove_degenerate_edges called (Branch 6) |
| [Me1090](Me1090.stp) | degree-3 vertex cap (equilateral variant): apex degree==3, fan edges interior, outer edges boundary |
| [Me1091](Me1091.stp) | isolated degenerate at strip boundary: single flip-candidate attached to open boundary |
| [Me1092](Me1092.stp) | collinear cc strip (5-vertex): 3-triangle connected degenerate component for disk removal |
| [Me1093](Me1093.stp) | complete K4 collinear mesh: all 4 degenerate faces form sphere topology χ=2≠1 (Branch 10) |
| [Me1094](Me1094.stp) | non-monotone CC boundary: degenerate triangle cluster boundary reverses along axis (Branch 11) |
| [Me1095](Me1095.stp) | flip-impossible (3-way diagonal): pre-existing diagonal shared by 3 faces blocks flip (Branch 12) |
| [Me1096](Me1096.stp) | border face removal (open boundary): degenerate collinear triangle at open boundary, direct remove_face (Branch 13) |
| [Me1100](Me1100.stp) | CreateTriangleFromVertices_over_constrained_e1: e1 already has 2 triangles; IS_BIT(e1,5) triggers edge duplication (Branch 1) |
| [Me1101](Me1101.stp) | CreateTriangleFromVertices_over_constrained_e2: e2 already has 2 triangles; IS_BIT(e2,5) triggers edge duplication (Branch 2) |
| [Me1102](Me1102.stp) | CreateTriangleFromVertices_over_constrained_e3: e3 already has 2 triangles; IS_BIT(e3,5) triggers edge duplication (Branch 3) |
| [Me1103](Me1103.stp) | CreateTriangleFromVertices_degenerate_triangle: all edges unlinked; Branch 4 null-guard frees e3 |
| [Me1104](Me1104.stp) | CreateTriangleFromVertices_unlinked_e2: e3 linked; e2=(v1,v2) orphan freed by Branch 5 freeNode |
| [Me1105](Me1105.stp) | CreateTriangleFromVertices_unlinked_e1: e3 and e2 linked; e1=(v0,v1) orphan freed by Branch 6 freeNode |
| [Me1110](Me1110.stp) | pinch-neck non-manifold vertex: genus-preservation decision for SI removal |
| [Me1111](Me1111.stp) | SI in CC-A; clean CC-B disconnected: treat_all_CCs processing-scope decision |
| [Me1112](Me1112.stp) | displaced fan-apex below flat patch causing SI: use_smoothing strategy branch |
| [Me1113](Me1113.stp) | two SI types: interior crossing + corner-touch pair filterable by filter NP |
| [Me1114](Me1114.stp) | zero-area degenerate faces empty SI candidate set: faces_to_treat emptiness detection |
| [Me1120](Me1120.stp) | cross-CC external SI: CC-A and CC-B intersect each other, no intra-CC SI |
| [Me1121](Me1121.stp) | patch vs containment envelope: intruder vertex below z=0 triggers Polyhedral_envelope check |
| [Me1122](Me1122.stp) | local smoothing on SI-bearing CC only: treat_all_CCs=false skips clean CC-B |
| [Me1123](Me1123.stp) | SI adjacent to 90-degree crease edge: constrain_sharp_edges preserves right-angle feature |
| [Me1124](Me1124.stp) | SI under two-crease floor: constrained smoothing stalls, unconstrained fallback fires |
| [Me1130](Me1130.stp) | SI in annular strip (chi=0): euler_characteristic != 1 complex-topology branch |
| [Me1131](Me1131.stp) | SI pair needing 2-ring expansion: expand_face_selection step>0 branch |
| [Me1132](Me1132.stp) | SI in 45-degree-rotated diamond mesh: OBB Aff_transformation branch |
| [Me1133](Me1133.stp) | SI with singleton compactified region (cc_faces.size()==1): skip branch |
| [Me1134](Me1134.stp) | three independent SI piercers: something_was_done=false convergence stall |
| [Me1140](Me1140.stp) | volume_connected_components self_intersection_detection: eight-triangle closed shell where cap faces (z=1 plane vs y=1 plane) cross with no shared vertex; does_self_intersect fires (Branch 1) |
| [Me1141](Me1141.stp) | volume_connected_components boundary_component_detection: two-triangle flat patch with four boundary edges; !is_closed fires before volume analysis (Branch 2) |
| [Me1142](Me1142.stp) | volume_connected_components orientation_consistency: closed tetrahedron with one CW-wound face; is_outward_oriented fails; orientation_error flagged (Branch 3) |
| [Me1143](Me1143.stp) | volume_connected_components nesting_depth_assignment: inner tetrahedron nested inside outer; ray-casting parity assigns volume_id=2 to inner component (Branch 4) |
| [Me1144](Me1144.stp) | volume_connected_components nested_component_orientation: inner tetrahedron has same outward orientation as outer; nesting invariant violated; nested_orientation_error flagged (Branch 5) |
| [Me1150](Me1150.stp) | is_degenerate_edge equal_points: endpoint positions identical (zero-length edge between v0==v1) (Branch 1) |
| [Me1151](Me1151.stp) | remove_a_border_edge simple: wrapper without tracking sets (border edge removal without state tracking) (Branch 1) |
| [Me1152](Me1152.stp) | keep_connected_components by_id: guard on halfedge(v,pmesh) (multi-component mesh selected by id) (Branch 1) |
| [Me1153](Me1153.stp) | is_degenerate_triangle_face collinear: zero-area triangle with all three vertices collinear (Branch 1) |
| [Me1154](Me1154.stp) | keep_connected_components by_face_range: face-range iteration path (multi-component mesh with face-range selection) (Branch 1) |
| [Me1155](Me1155.stp) | PMP.orient component_orientation_selection: outward_orientation flag evaluated for CW-wound closed tetrahedron (Branch 1) |
| [Me1156](Me1156.stp) | PMP.orient nesting_depth_parity: inner CC depth=1 receives inward orientation; outer CC depth=0 outward (Branch 2) |
| [Me1157](Me1157.stp) | PMP.orient component_orientation_consistency: open strip with 4 boundary edges; is_closed=false; component skipped by orient (Branch 3) |
| [Me1158](Me1158.stp) | PMP.orient_to_bound_a_volume single_component_trivial: single CW-wound closed tetrahedron; num_components==1 fast-path (Branch 1) |
| [Me1159](Me1159.stp) | PMP.orient_to_bound_a_volume nesting_depth_calculation: ray casting counts intersection parity for inner CC nested inside outer (Branch 2) |
| [Me1160](Me1160.stp) | PMP.orient_to_bound_a_volume parent_child_orientation_rule: inner CC depth=1 flipped opposite to outer parent shell (Branch 3) |
| [Me1161](Me1161.stp) | triangulate_and_refine_hole.main output_iterator_choice face: Emptyset_iterator substituted when face_output_iterator absent; 3-edge triangular hole (Branch 1) |
| [Me1162](Me1162.stp) | triangulate_and_refine_hole.main output_iterator_choice vertex: Emptyset_iterator substituted when vertex_output_iterator absent; 4-edge quad hole (Branch 2) |
| [Me1163](Me1163.stp) | triangulate_and_refine_hole.main triangulation_failure_handling: 5-edge hole; triangulate_hole fills patch; refine runs on non-empty result (Branch 3) |
| [Me1164](Me1164.stp) | triangulate_and_refine_hole.main visitor_callback_optional: Default_visitor substituted; 6-edge hex hole; start/end_refine_phase no-ops (Branch 4) |
| [Me1165](Me1165.stp) | triangulate_and_refine_hole.main density_control_parameterization: density_control_factor forwarded to refine(); triangular hole; Steiner insertion controlled (Branch 5) |
| [Me1170](Me1170.stp) | fill_edge_map edge_recording: per-edge polygon-id insertion into directed edge map; two-triangle manifold soup (Branch 1) |
| [Me1171](Me1171.stp) | fill_edge_map non_manifold_detection: three polygons share directed edge v0→v1; nb_edges=3 > 2 triggers non-manifold flag (Branch 2) |
| [Me1172](Me1172.stp) | fill_edge_map non_manifold_visitor_callback: four polygons share one undirected edge; visitor.non_manifold_edge callback fired (Branch 3) |
| [Me1173](Me1173.stp) | Basic_TMesh.forceNormalConsistence non_orientable_surface: already-marked triangle causes early return; tetrahedron all-consistent normals (Branch 1) |
| [Me1174](Me1174.stp) | Basic_TMesh.forceNormalConsistence adjacent_triangle_missing: e->t2 not NULL fires propagation to consistent neighbor (Branch 2) |
| [Me1175](Me1175.stp) | Basic_TMesh.forceNormalConsistence orientation_conflict: antiparallel normals on shared edge fire seam cut; inconsistent winding (Branch 3) |
| [Me1176](Me1176.stp) | Basic_TMesh.forceNormalConsistence recursion_base_case: recursive propagation halts at already-marked triangles; 3-fan all consistent (Branch 4) |
| [Me1177](Me1177.stp) | triangulate_hole.main compile_time_feature_disable DT3: CGAL_HOLE_FILLING_DO_NOT_USE_DT3 sets use_dt3=false; triangular hole boundary (Branch 1) |
| [Me1178](Me1178.stp) | triangulate_hole.main compile_time_feature_disable CDT2: CGAL_HOLE_FILLING_DO_NOT_USE_CDT2 sets use_cdt=false; quad hole boundary (Branch 2) |
| [Me1179](Me1179.stp) | triangulate_hole.main planarity_check_needed: bbox+max_squared_distance computation for CDT2 planarity test; planar pentagon hole (Branch 3) |
| [Me1180](Me1180.stp) | triangulate_hole.main threshold_override: explicit threshold_distance named parameter overrides bbox-computed default; hexagonal hole (Branch 4) |
| [Me1181](Me1181.stp) | triangulate_hole.main algorithm_fallback_strategy: non-planar hole triggers DT3 fallback; delegation to internal with use_dt3/use_cdt flags (Branch 5) |
| [Me1182](Me1182.stp) | triangulate_hole.main geometry_traits_deduction: GetGeomTraits deduces traits from point type; triangular hole; default traits path (Branch 6) |
| [Me1183](Me1183.stp) | polygon-soup box corner: three coincident-but-distinct copies of the shared corner vertex leave un-welded seam cracks (multi-vertex seam) |
| [Me1184](Me1184.stp) | out-of-plane spike vertex: one interior vertex of a flat patch displaced far off-surface, fanning extreme-aspect needle triangles with no self-intersection (outlier vertex) |
