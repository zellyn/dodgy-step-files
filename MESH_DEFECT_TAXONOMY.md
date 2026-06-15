# Mesh-Defect Taxonomy & Repair-Surface Survey

Survey-and-design report for adding mesh-geometry-defect fixtures to (or
alongside) the STEP-defect catalog at `/Users/zellyn/gh/dodgy-step-files/`.

The existing corpus is overwhelmingly B-rep + encoding fixtures. Mesh repair
is a distinct domain owned by **MeshFix** (Attene 2010), **CGAL Polygon Mesh
Processing**, **MeshLab**, and **libigl/OpenMesh**. OCCT is the wrong source
for these classes.

---

## Part A: Defect Taxonomy

Naming convention: `lower_snake_case`, geometric-defect-first. Each row says
whether the kernel should reject the file at parse (`encoding-defect`) or
attempt to repair (`geometry-defect` — sometimes both, when the same shape
can arrive as malformed encoding *or* valid encoding of broken geometry).

| # | Name | Description | Reject-or-repair | Fixture form | Reference |
|---|------|-------------|------------------|--------------|-----------|
| 1 | `duplicate_triangles` | Two or more triangles with identical (or rotated/reversed) vertex tuples; redundant faces inflate counts and break Euler checks. | geometry-defect | STL + STEP `TRIANGULATED_FACE` | MeshFix `removeDuplicatedTriangles`; CGAL `merge_duplicate_polygons_in_polygon_soup` |
| 2 | `duplicate_vertices` | Distinct vertex records sharing identical coordinates; faces reference both, leaving the mesh "polygon-soup" rather than topologically welded. | geometry-defect | STL (canonical) + STEP `COORDINATES_LIST` | CGAL `merge_duplicate_points_in_polygon_soup` |
| 3 | `near_coincident_vertices` | Vertices within epsilon but not bit-identical; numerically a single point but stored separately, causing T-junctions and tiny cracks. | geometry-defect | STL with eps-scattered points | MeshFix `meshclean`; CGAL `Snapping/snap_vertices` |
| 4 | `zero_area_triangle` | Face with three collinear or coincident vertices; area 0, normal undefined, breaks every triangle-based traversal. | geometry-defect | STL | MeshFix `removeDegenerateTriangles`; CGAL `is_degenerate_triangle_face`, `remove_degenerate_faces` |
| 5 | `needle_triangle` | Triangle where one edge is much shorter than the other two (sliver); aspect ratio explodes, normals unstable. | geometry-defect | STL | CGAL `is_needle_triangle_face`, `remove_almost_degenerate_faces` |
| 6 | `cap_triangle` | Triangle with one obtuse angle near 180 degrees; area nontrivial but normal ill-conditioned. | geometry-defect | STL | CGAL `is_cap_triangle_face`, `remove_almost_degenerate_faces` |
| 7 | `degenerate_edge` | Edge whose endpoints are identical (or eps-coincident) points; bookkeeping edge with zero length. | geometry-defect | STL | CGAL `is_degenerate_edge`, `remove_degenerate_edges` |
| 8 | `isolated_vertex` | Vertex referenced in coordinate list but in no face; harmless but pollutes counts. | geometry-defect | STL/PLY | CGAL `remove_isolated_vertices`, `remove_isolated_points_in_polygon_soup` |
| 9 | `non_manifold_edge` | Edge shared by three or more triangles; topology is no longer a 2-manifold, half-edge data structures cannot represent it cleanly. | geometry-defect | STL | MeshFix `cutAndStitch`; CGAL `non_manifold_vertices` (edge variant via incident-face count) |
| 10 | `non_manifold_vertex` | "Bowtie" or "pinch" vertex incident on two surface patches that share only that one vertex; locally a figure-8. | geometry-defect | STL | MeshFix `duplicateNonManifoldVertices`; CGAL `duplicate_non_manifold_vertices` |
| 11 | `boundary_hole` | A boundary cycle (chain of edges incident to only one face) where the mesh should be closed; e.g. missing patch. | geometry-defect | STL | MeshFix `fillSmallBoundaries`, `FillHole`; CGAL `triangulate_hole`, `triangulate_and_refine_hole`, `triangulate_refine_and_fair_hole` |
| 12 | `boundary_gap_thin` | Two patches that *should* share a boundary but their boundary cycles are eps-displaced; stitching-class defect. | geometry-defect | STL (two patches) | CGAL `stitch_borders`, `stitch_boundary_cycle`, `merge_duplicated_vertices_in_boundary_cycles`; MeshFix `mergeCoincidentEdges` |
| 13 | `inconsistent_face_orientation` | Adjacent faces oriented oppositely (one CW, one CCW) so the manifold is not orientable as written; normals flip across edge. | geometry-defect | STL (per-face) | MeshFix `forceNormalConsistence`; CGAL `orient`, `reverse_face_orientations` |
| 14 | `inverted_normals` | All faces consistently oriented, but inward instead of outward; volume becomes negative. | geometry-defect | STL | CGAL `is_outward_oriented`, `orient_to_bound_a_volume` |
| 15 | `self_intersection_face_pair` | Two triangles whose interiors intersect in a segment; common in CSG output and digitized scans. | geometry-defect | STL | MeshFix `strongIntersectionRemoval`, `selectIntersectingTriangles`; CGAL `self_intersections`, `experimental::remove_self_intersections` |
| 16 | `overlapping_triangles` | Coplanar triangles whose projections overlap; degenerate sub-case of self-intersection. | geometry-defect | STL | MeshFix `removeOverlappingTriangles`; CGAL `triangle_soup_self_intersections` |
| 17 | `disconnected_components` | Mesh has more than one connected shell; sometimes intentional (assembly), sometimes a scan artefact (floating noise islands). | geometry-defect | STL (multi-shell) | MeshFix `removeSmallestComponents`, `shells`; CGAL `keep_largest_connected_components` (in `connected_components.h`) |
| 18 | `negligible_component` | Connected component with area or volume below a threshold; almost always noise. | geometry-defect | STL | CGAL `remove_connected_components_of_negligible_size` |
| 19 | `non_orientable_surface` | Mesh is a topological Mobius strip or Klein bottle locally; no consistent orientation exists. | geometry-defect | STL | MeshFix `forceNormalConsistence` (cuts to make orientable) |
| 20 | `polygon_soup_unindexed` | Triangle list with no vertex sharing — every triangle has its own three vertices (canonical STL). Repair = reindex. | geometry-defect | STL (binary) | CGAL `repair_polygon_soup`, `orient_polygon_soup`, `polygon_soup_to_polygon_mesh` |
| 21 | `polygon_with_repeated_vertex` | A single polygon face whose vertex list contains the same vertex twice; degenerate polygon. | geometry-defect | OBJ/STEP higher-order face | CGAL `repair_polygon_soup` (sub-pass) |
| 22 | `t_junction` | Vertex lying on the interior of another triangle's edge but not topologically incident; causes cracks in shading and CSG. | geometry-defect | STL | CGAL `Snapping/snap`; MeshFix `meshclean` (partial) |
| 23 | `intersecting_distinct_components` | Two otherwise valid closed shells that interpenetrate; for a single solid this is invalid. | geometry-defect | STL (two shells) | MeshFix `joinClosestComponents`; CGAL `does_self_intersect` over union |
| 24 | `non_finite_coordinate` | Vertex coordinate is NaN, +Inf, or -Inf; mesh is structurally fine but unusable. | encoding-defect | STL (binary, raw bits) | both (reject at parse) |
| 25 | `near_zero_normal_face` | Vertex coordinates finite but triangle normal computes to ~0 in floating point due to magnitude/cancellation; degenerate-in-precision. | geometry-defect | STL | CGAL `remove_almost_degenerate_faces` |
| 26 | `flipped_face_in_otherwise_consistent_mesh` | A single face oriented opposite to its neighbors; subclass of #13 useful as a minimal fixture. | geometry-defect | STL | CGAL `compatible_orientations`, `reverse_face_orientations` |
| 27 | `unreferenced_face_data` | STL/PLY records faces referencing vertex indices outside the coord list; structural corruption. | encoding-defect | STL/PLY | both (reject at parse) |
| 28 | `mismatched_normal_attribute` | STL per-face normal disagrees with the geometric normal computed from vertices; not strictly a defect but a consistency violation kernels disagree on. | encoding-defect (loose) or geometry-defect | STL ASCII | MeshFix recomputes; libigl ignores stored normals |
| 29 | `pinched_triangle_strip` | A run of needle triangles forming a zero-volume tube; multiple-defect compound (needle + non-manifold-edge variations). | geometry-defect | STL | MeshFix `strongDegeneracyRemoval` |
| 30 | `near_self_intersection` | Two triangles whose minimum distance is below epsilon but they don't actually intersect; future-failure under any tolerance widening. | geometry-defect | STL | CGAL `snap`-family (preventive) |

Total: **30 defect classes**, two encoding-defect (24, 27), one mixed (28),
the rest geometry-defect.

---

## Part B: MeshFix Repair-Operation Enumeration

Source: `https://github.com/MarcoAttene/MeshFix-V2.1`, `include/TMesh/tin.h`
(public API of `Basic_TMesh`) and `src/MeshFix/meshfix.cpp` (CLI driver).
The CLI driver invokes only a small subset; the class exposes more.

### Topological-repair methods

- `Basic_TMesh::removeSmallestComponents()` — remove all but the largest connected shell.
- `Basic_TMesh::removeSmallestComponents(double epsilon)` — remove shells with area below threshold.
- `Basic_TMesh::forceNormalConsistence()` — propagate consistent triangle orientation across the surface; cuts the mesh where non-orientable.
- `Basic_TMesh::forceNormalConsistence(Triangle*)` — same restricted to one component with a seed face.
- `Basic_TMesh::duplicateNonManifoldVertices()` — split bowtie/pinch vertices into one copy per surface patch.
- `Basic_TMesh::removeDuplicatedTriangles()` — eliminate redundant faces with identical vertex tuples.
- `Basic_TMesh::mergeCoincidentEdges()` — unify edges that are topologically distinct but geometrically the same.
- `Basic_TMesh::cutAndStitch()` — convert a non-manifold mesh into a manifold by cutting along non-manifold edges and re-stitching where consistent.
- `Basic_TMesh::removeUnlinkedElements()` — purge orphan vertices/edges/triangles.
- `Basic_TMesh::removeRedundantVertices()` — drop vertices whose removal does not change the geometric realization (interior of a flat patch).
- `Basic_TMesh::fixConnectivity()` — repair half-edge connectivity between geometric elements.
- `Basic_TMesh::rebuildConnectivity()` — recompute topology from raw geometry (polygon-soup → connected mesh).

### Geometric-repair methods

- `Basic_TMesh::removeDegenerateTriangles()` — collapse/split zero-area triangles.
- `Basic_TMesh::strongDegeneracyRemoval(int max_iters)` — iterative degeneracy removal with neighborhood growth when local fix fails.
- `Basic_TMesh::removeOverlappingTriangles()` — remove coplanar overlapping faces.
- `Basic_TMesh::selectIntersectingTriangles(...)` — mark self-intersecting triangles for removal.
- `Basic_TMesh::strongIntersectionRemoval(int max_iters)` — iteratively remove self-intersections and re-fill the resulting holes.
- `Basic_TMesh::checkGeometry()` — find first degeneracy/coincident vertex/overlap (diagnostic).
- `Basic_TMesh::safeCoordBackApproximation()` — round coordinates to ASCII-safe precision without introducing intersections.
- `Basic_TMesh::meshclean(int max_iters=10, int inner_loops=3)` — top-level "clean degeneracies + intersections to a fixed point".

### Hole filling

- `Basic_TMesh::StarTriangulateHole(Edge*)` — star-fill a boundary loop from its barycenter.
- `Basic_TMesh::TriangulateHole(Edge*)` — heuristic boundary-loop triangulation.
- `Basic_TMesh::TriangulateHole(Edge*, Point* normal)` — planar Delaunay fill with given plane normal.
- `Basic_TMesh::TriangulateHole(Edge*, List* additional_points)` — fill incorporating extra interior points.
- `Basic_TMesh::FillHole(Edge*, bool refine=true)` — fill plus refinement to match surrounding density.
- `Basic_TMesh::fillSmallBoundaries(int max_edge_count, bool refine)` — fill every boundary loop with at most N edges.
- `Basic_TMesh::refineSelectedHolePatches(...)` — densify a freshly-filled patch.
- `Basic_TMesh::joinBoundaryLoops(Vertex*, Vertex*, ...)` — bridge two boundary loops into one (or close handles).

### Driver-level (file-scope in `meshfix.cpp`)

- `closestPair()` — find shortest vertex pair between two boundary loops.
- `joinClosestComponents()` — connect floating components via shortest-bridge edges (driven by `-a` flag).

### Diagnostic / queries

- `Basic_TMesh::boundaries()` — number of boundary loops.
- `Basic_TMesh::handles()` — genus / number of handles.
- `Basic_TMesh::shells()` — number of connected components.
- `Basic_TMesh::checkConnectivity()` — verify half-edge invariants.
- `Basic_TMesh::eulerUpdate()` — recompute boundary/handle/shell counts.

Total: **~28 repair-relevant public operations** (plus many element-factory
and IO methods omitted).

---

## Part C: CGAL Polygon Mesh Processing Repair Surface

Source: `https://github.com/CGAL/cgal/tree/main/PMP_Mesh_repair/include/CGAL/Polygon_mesh_processing/`. Function names are verbatim
from the headers.

### Polygon-soup repair (`repair_polygon_soup.h`)

- `CGAL::Polygon_mesh_processing::remove_isolated_points_in_polygon_soup` — drop points not referenced by any polygon.
- `CGAL::Polygon_mesh_processing::merge_duplicate_points_in_polygon_soup` — collapse geometrically identical points.
- `CGAL::Polygon_mesh_processing::merge_duplicate_polygons_in_polygon_soup` — remove polygons with identical vertex tuples.
- `CGAL::Polygon_mesh_processing::repair_polygon_soup` — composite pipeline running the three above plus orientation.

### Polygon-soup → mesh and orientation (`orient_polygon_soup.h`, `polygon_soup_to_polygon_mesh.h`)

- `CGAL::Polygon_mesh_processing::orient_polygon_soup` — make a soup orientable; duplicate points where required.
- `CGAL::Polygon_mesh_processing::polygon_soup_to_polygon_mesh` — convert oriented soup into a half-edge mesh.

### Degeneracy removal (`repair_degeneracies.h`, `shape_predicates.h`)

- `CGAL::Polygon_mesh_processing::is_degenerate_edge` — predicate.
- `CGAL::Polygon_mesh_processing::degenerate_edges` — collect.
- `CGAL::Polygon_mesh_processing::is_degenerate_triangle_face` — predicate.
- `CGAL::Polygon_mesh_processing::degenerate_faces` — collect.
- `CGAL::Polygon_mesh_processing::is_needle_triangle_face` — sliver predicate.
- `CGAL::Polygon_mesh_processing::is_cap_triangle_face` — obtuse-cap predicate.
- `CGAL::Polygon_mesh_processing::remove_degenerate_edges` — collapse zero-length edges.
- `CGAL::Polygon_mesh_processing::remove_degenerate_faces` — drop zero-area faces.
- `CGAL::Polygon_mesh_processing::remove_almost_degenerate_faces` — drop needles and caps.

### Self-intersection (`self_intersections.h`, `repair_self_intersections.h`)

- `CGAL::Polygon_mesh_processing::self_intersections` — collect intersecting face pairs.
- `CGAL::Polygon_mesh_processing::does_self_intersect` — boolean predicate.
- `CGAL::Polygon_mesh_processing::triangle_soup_self_intersections` — same on raw soup.
- `CGAL::Polygon_mesh_processing::does_triangle_soup_self_intersect` — boolean on soup.
- `CGAL::Polygon_mesh_processing::experimental::remove_self_intersections` — repair via smoothing and hole-fill.

### Stitching, manifoldness, borders (`stitch_borders.h`, `manifoldness.h`, `merge_border_vertices.h`)

- `CGAL::Polygon_mesh_processing::stitch_borders` — auto-match and stitch compatible border halfedges.
- `CGAL::Polygon_mesh_processing::stitch_boundary_cycle` / `stitch_boundary_cycles` — stitch within one or all cycles.
- `CGAL::Polygon_mesh_processing::is_non_manifold_vertex` / `non_manifold_vertices` — detect.
- `CGAL::Polygon_mesh_processing::duplicate_non_manifold_vertices` — repair bowties.
- `CGAL::Polygon_mesh_processing::merge_duplicated_vertices_in_boundary_cycle(s)` — weld eps-coincident boundary verts.

### Orientation (`orientation.h`)

- `CGAL::Polygon_mesh_processing::is_outward_oriented`
- `CGAL::Polygon_mesh_processing::reverse_face_orientations`
- `CGAL::Polygon_mesh_processing::reverse_face_orientations_of_mesh_with_polylines`
- `CGAL::Polygon_mesh_processing::orient`
- `CGAL::Polygon_mesh_processing::volume_connected_components`
- `CGAL::Polygon_mesh_processing::does_bound_a_volume`
- `CGAL::Polygon_mesh_processing::orient_to_bound_a_volume`
- `CGAL::Polygon_mesh_processing::merge_reversible_connected_components`
- `CGAL::Polygon_mesh_processing::compatible_orientations`

### Hole filling (`triangulate_hole.h`)

- `CGAL::Polygon_mesh_processing::triangulate_hole` — basic.
- `CGAL::Polygon_mesh_processing::triangulate_and_refine_hole` — fill + density match.
- `CGAL::Polygon_mesh_processing::triangulate_refine_and_fair_hole` — fill + refine + smooth (fairing).
- `CGAL::Polygon_mesh_processing::triangulate_hole_polyline` — fill arbitrary polyline.

### Top-level cleanup (`repair.h`)

- `CGAL::Polygon_mesh_processing::remove_isolated_vertices`
- `CGAL::Polygon_mesh_processing::remove_connected_components_of_negligible_size`

### Snapping (internal but documented)

- `CGAL::Polygon_mesh_processing::internal::snap_borders` — eps-snap border vertices (T-junction repair).
- `CGAL::Polygon_mesh_processing::internal::snap_vertices` — eps-weld interior vertices.

Total: **~35 public repair-related functions** in PMP (plus ~5 internal but
documented snapping helpers).

---

## Part D: Suggested First Fixture Batch

Cross-referencing Parts A/B/C. Each fixture exercises a single defect class
in its minimal form (4-12 triangles); STL is the primary format because
every mesh library reads it and per-face data isolates topology defects
cleanly. STEP `TRIANGULATED_FACE` companions are noted where the bug can
also arrive embedded in AP242 mesh entities.

| ID | Defect class | Suggested form | MeshFix op | CGAL PMP op |
|----|--------------|----------------|------------|-------------|
| `Mx001` | `duplicate_triangles` | STL with 2 unit triangles + one repeated | `removeDuplicatedTriangles` | `merge_duplicate_polygons_in_polygon_soup` |
| `Mx002` | `duplicate_vertices` | STL: tetrahedron whose binary records list every vertex 3x (canonical STL polygon-soup form) | `rebuildConnectivity` | `merge_duplicate_points_in_polygon_soup` |
| `Mx003` | `zero_area_triangle` | STL: cube with one face replaced by a collinear-3-vertex triangle | `removeDegenerateTriangles` | `remove_degenerate_faces` |
| `Mx004` | `needle_triangle` | STL: cube with one face replaced by a 1:1000 aspect-ratio sliver | (`strongDegeneracyRemoval`) | `is_needle_triangle_face`, `remove_almost_degenerate_faces` |
| `Mx005` | `non_manifold_edge` | STL: 3 triangles sharing one edge ("Y-fan") | `cutAndStitch` | `duplicate_non_manifold_vertices` (related) |
| `Mx006` | `non_manifold_vertex` | STL: two tetrahedra joined at a single vertex ("bowtie") | `duplicateNonManifoldVertices` | `duplicate_non_manifold_vertices` |
| `Mx007` | `boundary_hole` | STL: cube minus one face | `fillSmallBoundaries` | `triangulate_hole`, `triangulate_refine_and_fair_hole` |
| `Mx008` | `inconsistent_face_orientation` | STL: cube with one face's vertex order reversed | `forceNormalConsistence` | `orient`, `reverse_face_orientations` |
| `Mx009` | `inverted_normals` | STL: closed cube with every face wound inward | (manual flip) | `is_outward_oriented`, `orient_to_bound_a_volume` |
| `Mx010` | `self_intersection_face_pair` | STL: two unit triangles whose interiors cross | `strongIntersectionRemoval` | `self_intersections`, `experimental::remove_self_intersections` |
| `Mx011` | `disconnected_components` | STL: large cube + tiny noise tetra | `removeSmallestComponents` | `remove_connected_components_of_negligible_size` |
| `Mx012` | `near_coincident_vertices` | STL: cube whose 8 corners each appear 3-6 times within eps=1e-7 | `meshclean` | `Snapping::snap_vertices`, `merge_duplicate_points_in_polygon_soup` |
| `Mx013` | `boundary_gap_thin` | STL: two open patches whose shared boundary is eps-displaced | `mergeCoincidentEdges` | `stitch_borders`, `merge_duplicated_vertices_in_boundary_cycles` |
| `Mx014` | `t_junction` | STL: quad split into two triangles on one side, single triangle on the other; middle vertex lies on but is not in the opposite edge | `meshclean` (partial) | `Snapping::snap` |
| `Mx015` | `non_finite_coordinate` | STL binary: cube with one vertex coord = NaN bit-pattern | rejected at parse | rejected at parse |

Notes:

- `Mx015` is the only fixture that exercises an **encoding-defect** boundary;
  the rest are pure geometry-defects and serve as the kernel's repair-grader.
- `Mx002` and `Mx012` are deliberately the same shape (welded cube) at
  different *scales* of vertex coincidence — bit-identical vs eps-close —
  because the repair operations differ (string-key dedup vs spatial snap).
- A second batch (`Mx016`-`Mx030`) would cover the rest of Part A in order;
  most natural additions are `cap_triangle`, `overlapping_triangles`,
  `polygon_with_repeated_vertex`, `degenerate_edge`, `isolated_vertex`,
  `flipped_face_in_otherwise_consistent_mesh`, and `non_orientable_surface`.

---

## Part E: Design Recommendation

**Recommendation: separate sub-catalog at `github.com/zellyn/dodgy-mesh-files`.**

Rationale (catalog-property arguments, per the constraint):

1. **Different source library.** The STEP-defect corpus is graded against
   OCCT — a B-rep kernel that has no opinion about triangle slivers,
   non-manifold edges, or hole-fill quality. Mesh defects are graded
   against MeshFix / CGAL PMP / MeshLab / libigl. The two catalogs share
   zero reference implementations, so the "ground truth" oracle is
   different per file. Mixing them forces every fixture to declare which
   oracle applies; splitting eliminates that flag.

2. **Different fixture file format.** STEP-defect fixtures are
   primarily `.step`/`.stp` ASCII files; an entity-list problem statement is
   meaningful and a STEP-aware diff tool is the natural inspection
   workflow. Mesh-defect fixtures are primarily `.stl`/`.ply`/`.off`
   binary or ASCII; the natural inspection workflow is a 3D viewer
   (MeshLab/F3D) and `tri_check`-style scripts. A single corpus with two
   file-format dialects splits tooling (different validators, different
   visualizers, different LFS settings) without sharing infrastructure.

3. **Different domain audience.** STEP-defect users are CAD-kernel and
   PDM-import authors; mesh-defect users are 3D-print, finite-element, and
   game-asset pipeline authors. A single catalog conflates two
   bug-reporting communities and dilutes search relevance for each.

The mesh catalog should mirror the STEP catalog's layout (numbered
section directories, fixture-id naming convention, problem-pattern
phrasing per the LGPL-fix you adopted) so that lessons learned port
across, but the two corpora belong in distinct repositories with their
own CI, validators, and grading harnesses.
