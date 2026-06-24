# Codebase Landscape: Open-Source Repair / Heal / Fix Surfaces Worth Auditing

**Purpose.** Map open-source codebases whose REPAIR/HEAL/FIX operations a comprehensive
defect catalog should audit, *beyond* the original OCCT + MeshFix + CGAL PMP baseline.
This is enumeration only; we synthesise prose-laundered defect descriptions from documentation,
function names, issue trackers, and class headers — we never copy code or fixtures.

**Method.** Web-fetched READMEs, online docs, doxygen pages, issue-tracker summaries
for each project. Rankings are based on (a) breadth of the project's repair-surface,
(b) how distinct its defect domain is from OCCT/MeshFix/CGAL PMP, and
(c) availability of self-describing prose (header docs, manual pages, named operators).

**Date.** 2026-06-14 (refreshed 2026-06-24 with coverage status).

---

## Coverage status snapshot — 2026-06-24

Progress since the landscape was first drafted:

- **OCCT (TKShHealing + BRepLib + BRepBuilderAPI_Sewing + ShapeCustom/Extend/Process):**
  per-method deep-pass enumerated 317 methods + 3399 repair branches.
  867 branches covered (25.5%). See `OCCT_HEAL_COVERAGE_V2.md`.
- **CGAL PMP + MeshFix (item #3 from the priorities list):** mesh
  waves 1–41 shipped 760 fixtures covering 115+/151 methods (~44%).
  Sub-corpus lives in `mesh-examples/12-14-mesh/`. See
  `MESH_HEAL_COVERAGE.md`. **This addresses priority #3 below;
  consider it substantively covered, with deferrable depth gaps logged
  per-method.**
- **Issue-tracker mining (B4):** waves 1–3 against FreeCAD, solvespace,
  pythonocc-core, cascadio, KiCad, CadQuery, Blender STEP-addon, etc.
  Yielded 35 NOVEL synthesized fixtures total; saturation signal at
  9.3% yield in wave 3. See BACKLOG.md B4.
- **Total corpus:** 3,086 catalog entries (2,350 STEP + 760 mesh +
  small sibling-input). See VALIDATION_SUMMARY.md for verdict matrix.
- **Quality state:** post-rebaseline `_final_verdict` reports
  2230 CONFIRMED · 1 CONCERN (documented) · 0 DRIFT · 119 ERROR (mesh
  routing). DRIFT-rebaseline workflow now documented in user memory.

**Still untouched from the priorities list:** vcglib/MeshLab,
VTK, assimp, lib3mf, admesh, Blender bmesh, fTetWild, Manifold issue
tracker, ifcopenshell `ifcpatch`. These remain the highest-EV
next targets if/when the corpus is ready for breadth expansion beyond
the OCCT/MeshFix/CGAL baseline.

---

## TOP PRIORITIES — Next 5–10 Codebases to Audit

Ranked by expected novel-defect yield per audit-hour:

1. **vcglib + MeshLab `filter_clean` plugin.** MeshLab's "Cleaning and Repairing" filter
   menu is an unusually clean *named taxonomy* of defects. The filter implementations live
   in `src/meshlabplugins/filter_clean/` and use `vcg::tri::Clean` primitives. Every menu
   item maps to a defect class. **Domain: surface mesh.**
2. **VTK Filters/Core + Filters/Modeling.** `vtkCleanPolyData`, `vtkFillHolesFilter`,
   `vtkPolyDataNormals`, `vtkStaticCleanPolyData`, `vtkTriangleFilter`, plus the
   `vtkBooleanOperationPolyDataFilter` and `vtkLoopBooleanPolyDataFilter` failure modes.
   Strong header-doc prose. **Domain: surface mesh + filter-graph defects.**
3. **CGAL Polygon Mesh Processing — Repair package (deeper pass).** Partial coverage exists,
   but the *Polygon Mesh Repair* group reference manual (`PkgPolygonMeshProcessingRef`) and
   the new (2025) `autorefine_and_snap` / triangle-soup-repair routines should be re-audited.
   High signal, well-documented prose. **Domain: surface mesh.**
4. **assimp `postprocess.h` 30+ flag taxonomy.** Multi-format breadth (OBJ, FBX, COLLADA,
   glTF, 3DS, BLEND, X3D, PLY, STL, etc.) that no other library matches. Each
   `aiProcess_*` flag is a defect class the readers know how to fix.
   **Domain: file-format / generic mesh.**
5. **lib3mf (3MF Consortium) + 3MF validator.** Currently zero coverage. The 3MF spec
   has explicit *namespace*, *MUST-IGNORE*, *production-extension* failure modes that have
   no STL/STEP analog. Closest thing to a STEP-equivalent for the additive-manufacturing
   world. **Domain: file-format parsing.**
6. **admesh + Slic3r/PrusaSlicer model-repair path.** ADMesh's `fix*` operations
   (`fix-normal-directions`, `remove-unconnected-facets`, `fill-holes`, `fix-backward-edges`)
   are a canonical STL-level defect taxonomy at the binary-record level — distinct from
   B-rep healing. AGPL/GPL on the host slicer is fine for prose-only audit.
   **Domain: STL parse-level defects.**
7. **Blender bmesh operators.** `bmo_dissolve.c`, `bmo_fill_holes.c`,
   `bmo_recalc_face_normals.c`, `bmo_remove_doubles.c`, `bmo_triangulate.c`,
   `bmo_connect_nonplanar.c`, plus the `bmesh_opdefines.c` master list. Blender's editor
   has accumulated decades of artist-driven repair primitives. Distinct vocabulary
   (dissolve vs delete vs collapse vs decimate). **Domain: surface mesh editor operators.**
8. **fTetWild / TetWild preprocessing pipeline.** The whole *point* of TetWild is "accept
   arbitrary garbage surface mesh input" — its preprocessing pipeline is an enumeration of
   what input garbage looks like. **Domain: volumetric / surface→tet.**
9. **Manifold (elalish/manifold) issue tracker.** Coverage exists at the API-surface level,
   but the Manifold *issue tracker* is essentially a curated list of "things that broke
   the boolean kernel" — minimal-precondition catalogue. Apache-2.0.
   **Domain: minimal manifold preconditions / boolean robustness.**
10. **ifcopenshell `ifcpatch` recipes + IFC++ parser quirks.** `ifcpatch` ships pre-packaged
    repair scripts; their script names map to recurring real-world IFC defects. IFC++ is a
    second-implementation viewpoint useful for parser-divergence quirks.
    **Domain: BIM-level defects, distinct from STEP geometry defects.**

---

## BODY — Per-codebase catalogue

Each entry: **Name** | URL | License | Domain | Languages | Scale | Entry points | **Relevance**.

### B-rep / CAD-kernel domain

#### 1. OCCT (Open CASCADE Technology)
- URL: https://github.com/Open-Cascade-SAS/OCCT
- License: LGPL-2.1-with-exception
- Domain: B-rep CAD kernel + STEP/IGES/BREP parsers
- Languages: C++
- Scale: ~3M LoC; `src/ShapeFix/`, `src/ShapeAnalysis/`, `src/ShapeUpgrade/`, `src/ShapeProcess/`
- Entry points: `ShapeFix_Shape::Perform()`, `ShapeFix_Wire::Perform()`, `STEPControl_Reader::TransferRoots()`, `BRepBuilderAPI_Sewing`
- **Relevance: HIGH (baseline — already audited).**

#### 2. FreeCAD Part workbench
- URL: https://github.com/FreeCAD/FreeCAD ; `src/Mod/Part/`
- License: LGPL-2.1
- Domain: B-rep app on top of OCCT
- Languages: C++ / Python
- Entry points: `Part::Refine`, `Part Check Geometry` (with BOP check), `Part SewShape`, `Part RefineShape`, `Part_ShapeFromMesh` ("sew tolerance")
- **Relevance: MEDIUM.** Almost all defects re-route to OCCT, but FreeCAD's user-visible *workflow* names ("Refine Shape", "Check Geometry", "Make Compound") provide a usability-layer taxonomy missing from OCCT.

#### 3. Salome SHAPER / GEOM repair menu
- URL: https://github.com/SalomePlatform/geom ; https://docs.salome-platform.org/
- License: LGPL-2.1
- Domain: B-rep CAD on top of OCCT
- Languages: C++ / Python
- Entry points: `Repair > Shape Processing`, `Glue Faces`, `Glue Edges`, `Limit Tolerance`, `Suppress Faces`, `Suppress Holes`, `Fuse Collinear Edges`, `Remove Webs`, `Remove Extra Edges`, `Sewing`, `Close Contour`, `FixShape`
- **Relevance: HIGH.** Every menu item is a defect class; the user-guide pages name them all with parameter descriptions. Already partially audited (batch 09).

#### 4. BRL-CAD
- URL: https://github.com/BRL-CAD/brlcad
- License: BSD-3-Clause / LGPL combo
- Domain: CSG + BoT (Bag of Triangles) + NURBS
- Languages: C, C++
- Entry points: `bot repair` (MGED/Archer command), `rt_heal` (planned NURBS healing routine), `step-g` importer
- **Relevance: MEDIUM-HIGH.** BoT-specific (non-manifold-bot) repair vocabulary is distinct from B-rep and from triangle-soup repair. `step-g` importer TODO list = an explicit roadmap of known STEP-parser limitations.

#### 5. pythonOCC / pythonocc-core
- URL: https://github.com/tpaviot/pythonocc-core
- License: LGPL-3.0
- Domain: Python bindings over OCCT
- Languages: Python / C++ (SWIG)
- Entry points: Wraps OCCT shape-healing classes; issue tracker is most valuable (umlauts, label naming, alignment).
- **Relevance: LOW-MEDIUM (already audited).**

#### 6. CadQuery / build123d
- URL: https://github.com/CadQuery/cadquery ; https://github.com/gumyr/build123d
- License: Apache-2.0
- Domain: Python CAD on OCCT
- Languages: Python
- Entry points: `Workplane.combine`, `clean`, `fix`; issue trackers
- **Relevance: LOW (already audited).**

#### 7. KiCad MCAD / 3D-board STEP path
- URL: https://gitlab.com/kicad/code/kicad
- License: GPL-3.0
- Domain: PCB+MCAD STEP emitter
- Languages: C++
- Entry points: `pcbnew/exporters/step/` ; assembly-instance flattening
- **Relevance: MEDIUM (partially audited).** Reveals exporter-side defects (naming collisions, repeated instances, transform composition).

#### 8. OpenNURBS toolkit (Rhino / 3DM)
- URL: https://github.com/mcneel/opennurbs
- License: MIT
- Domain: NURBS modelling kernel, 3DM format
- Languages: C++
- Entry points: `ON_Brep::RepairForExport`, `ON_Brep::IsValid`, McNeel pcurve-error threads
- **Relevance: MEDIUM (already audited).**

#### 9. Netgen / NGSolve
- URL: https://github.com/NGSolve/netgen
- License: LGPL-2.1
- Domain: 3D tet mesher with STL/STEP/IGES front-end
- Languages: C++ / Python
- Entry points: "Geometry doctor" UI; `STLGeometry::DoArchive`, `OCC_Heal*` flags
- **Relevance: MEDIUM.** Smaller surface than OCCT/gmsh; mostly wraps OCCT healing flags.

#### 10. gmsh
- URL: https://gitlab.onelab.info/gmsh/gmsh ; https://gmsh.info/
- License: GPL-2.0+
- Domain: Mesh generator with OCC frontend
- Languages: C++ / Python
- Entry points: `HealShapes`, `OCCFixDegenerated`, `OCCFixSmallEdges`, `OCCFixSmallFaces`, `OCCSewFaces`, `OCCMakeSolids`; `OCC.heal()` Python API
- **Relevance: MEDIUM (already audited).** The *parameter flags* gmsh exposes for OCC healing reveal which OCCT operators are actually needed in practice.

---

### Polygon mesh repair domain

#### 11. MeshFix (Attene)
- URL: https://github.com/MarcoAttene/MeshFix-V2.1
- License: GPL-3.0
- Domain: Triangle-mesh healing (digitised input)
- Languages: C++
- Entry points: `JMeshExt::clean`, `JMeshExt::removeSmallestComponents`, `JMeshExt::checkAndRepair`; greedy local-repair loop
- **Relevance: HIGH (baseline — already audited).**

#### 12. CGAL Polygon Mesh Processing — Repair package
- URL: https://doc.cgal.org/latest/Polygon_mesh_processing/group__PkgPolygonMeshProcessingRef.html
- License: GPL/LGPL with commercial dual-license
- Domain: Triangle-mesh repair + boolean
- Languages: C++ templates
- Entry points: `stitch_borders`, `merge_duplicate_polygons_in_polygon_soup`, `repair_polygon_soup`, `remove_isolated_vertices`, `remove_degenerate_faces`, `remove_degenerate_edges`, `remove_self_intersections`, `experimental::autorefine_and_remove_self_intersections`, `autorefine_triangle_soup`, `triangulate_hole`, `triangulate_hole_polyline`, `does_self_intersect`, `does_bound_a_volume`, `orient_polygon_soup`, `polygon_mesh_to_polygon_soup`, `experimental::snap_borders`
- **Relevance: HIGH (partially audited — deserves another deep pass).** The June 2025 `autorefine-and-snap` addition is post-original-audit.

#### 13. libigl
- URL: https://github.com/libigl/libigl
- License: MPL-2.0 (core) / GPL-3.0 (copyleft modules)
- Domain: Geometry processing in C++
- Languages: C++ templates / Python
- Scale: ~200 single-header algorithms in `include/igl/`
- Entry points: `igl::remove_duplicate_vertices`, `igl::remove_duplicates`, `igl::collapse_small_triangles`, `igl::decimate`, `igl::resolve_duplicated_faces`, `igl::is_edge_manifold`, `igl::is_vertex_manifold`, `igl::unique_edge_map`, `igl::triangulate`, `igl::copyleft::cgal::remesh_self_intersections`, `igl::copyleft::cgal::mesh_boolean`
- **Relevance: HIGH.** `copyleft/cgal/` submodule combines igl + CGAL approaches; novel test-data routines.

#### 14. MeshLab
- URL: https://github.com/cnr-isti-vclab/meshlab
- License: GPL-3.0
- Domain: Mesh GUI + filter graph
- Languages: C++ / Qt
- Entry points: `src/meshlabplugins/filter_clean/cleanfilter.cpp` — *the* canonical menu-driven taxonomy: Remove Duplicate Faces, Remove Duplicate Vertices, Remove Zero Area Faces, Remove Unreferenced Vertices, Remove Faces from Non Manifold Edges, Remove T-Vertices by Edge Flip / Edge Collapse, Repair non-Manifold Edges (split / collapse), Repair non-Manifold Vertices by splitting, Snap Mismatched Borders, Close Holes, Merge Close Vertices, Remove Isolated Pieces (by diameter / face count), Coplanar Faces Merge
- **Relevance: HIGH.** Distinct *naming conventions* will add defect-class entries not findable in OCCT or CGAL.

#### 15. vcglib (VCG / Visual Computing Lab)
- URL: https://github.com/cnr-isti-vclab/vcglib
- License: GPL-3.0
- Domain: Header-only mesh primitives, used inside MeshLab
- Languages: C++
- Entry points: `vcg::tri::Clean<>` namespace: `RemoveDuplicateVertex`, `RemoveDuplicateFace`, `RemoveZeroAreaFace`, `RemoveNonManifoldFace`, `RemoveNonManifoldVertex`, `RemoveSmallConnectedComponentsSize`, `CountNonManifoldEdgeFF`, `CountNonManifoldVertexFF`, `IsBitFFFlippable`, `CountHoles`; `vcg::tri::Hole` for hole filling
- **Relevance: HIGH.** Lower-level than MeshLab — function names are precise defect tags.

#### 16. OpenMesh
- URL: https://www.graphics.rwth-aachen.de/openmesh/ (gitlab @ RWTH Aachen)
- License: BSD-3-Clause (since v8)
- Domain: Halfedge data structure for polygon meshes
- Languages: C++
- Entry points: `PolyConnectivity::delete_face`, `delete_vertex`, `delete_edge` (mark only); `garbage_collection()`; `Decimater`; status-attribute infrastructure
- **Relevance: MEDIUM.** Smaller repair surface than vcglib/CGAL but illustrates a unique two-phase "mark then GC" approach. Defect detection is implicit (status flags).

#### 17. PMP Library (pmp-library)
- URL: https://github.com/PMP-library/pmp-library ; https://www.pmp-library.org/
- License: MIT
- Domain: Mesh processing (academic teaching codebase)
- Languages: C++
- Entry points: `SurfaceRemeshing`, `SurfaceHoleFilling`, `SurfaceTriangulation`, `SurfaceFairing`, `SurfaceFeatures`, `SurfaceCurvature`, `SurfaceSimplification`, `SurfaceSubdivision`
- **Relevance: MEDIUM.** Smaller and "academic clean" — hole filling and remeshing are repair-relevant.

#### 18. Open3D
- URL: https://github.com/isl-org/Open3D
- License: MIT
- Domain: 3D point-cloud + mesh
- Languages: C++ / Python
- Entry points: `is_edge_manifold`, `is_vertex_manifold`, `is_self_intersecting`, `is_watertight`, `is_orientable`, `get_non_manifold_edges`, `get_non_manifold_vertices`, `get_self_intersecting_triangles`, `remove_duplicated_vertices`, `remove_duplicated_triangles`, `remove_degenerate_triangles`, `remove_unreferenced_vertices`, `remove_non_manifold_edges`, `cluster_connected_triangles`, `simplify_vertex_clustering`, `simplify_quadric_decimation`
- **Relevance: HIGH.** Naming conventions are highly explicit; documentation is publicly readable; covers a slightly different defect set (point-cloud derived meshes).

#### 19. trimesh (Python)
- URL: https://github.com/mikedh/trimesh
- License: MIT
- Domain: Mesh I/O + repair + analysis
- Languages: Python
- Entry points: `trimesh.repair.fix_winding`, `fix_normals`, `fix_inversion`, `fill_holes`, `broken_faces`, `stitch`, `merge_vertices`; `trimesh.bool`; `trimesh.boolean`
- **Relevance: HIGH.** Single-file `repair.py` is dense and well-commented; idiomatic surface.

#### 20. PyMesh
- URL: https://github.com/PyMesh/PyMesh
- License: MPL-2.0
- Domain: Python mesh-processing wrapper around CGAL/libigl/etc.
- Languages: C++ / Python
- Entry points: `remove_degenerated_triangles`, `remove_duplicated_vertices`, `remove_duplicated_faces`, `remove_isolated_vertices`, `split_long_edges`, `collapse_short_edges`, `remove_obtuse_triangles`, `resolve_self_intersection`, `tetrahedralize`; the `fix_mesh.py` script is a canonical recipe
- **Relevance: HIGH.** Documentation page `Local Mesh Cleanup` is a direct defect list.

#### 21. Geogram (Bruno Lévy)
- URL: https://github.com/BrunoLevy/geogram
- License: BSD-3-Clause
- Domain: Geometry processing + Voronoi + remeshing + booleans
- Languages: C++
- Entry points: `mesh_repair` module; `tetrahedralize`; surface reconstruction; boolean operations via `co3ne`/`vorpaline`
- **Relevance: MEDIUM-HIGH.** Different theoretical basis (Voronoi/Lp-centroidal) than CGAL — produces a distinct defect taxonomy when used as a cleanup tool.

#### 22. Cinolib
- URL: https://github.com/mlivesu/cinolib
- License: MIT
- Domain: Polygonal + polyhedral meshes
- Languages: C++ (header-only)
- Entry points: Mesh validation primitives; common base class across surface/volumetric meshes
- **Relevance: MEDIUM.** Stronger in volumetric mesh side than pure repair.

#### 23. pymeshfix
- URL: https://github.com/pyvista/pymeshfix
- License: GPL-3.0 (inherits from MeshFix)
- **Relevance: LOW (duplicate of MeshFix).**

#### 24. Blender bmesh operators
- URL: https://github.com/blender/blender — `source/blender/bmesh/operators/`
- License: GPL-2.0+
- Domain: Mesh editor primitives
- Languages: C
- Entry points: `bmo_dissolve.c` (vertex/edge/face/limit dissolve), `bmo_fill_holes.c`, `bmo_recalc_face_normals.c`, `bmo_remove_doubles.c`, `bmo_triangulate.c`, `bmo_connect_nonplanar.c`, `bmo_symmetrize.c`, `bmo_unsubdivide.c`, `bmo_bevel.c` (degenerate handling), `bmo_smooth_laplacian.c`; master list in `intern/bmesh_opdefines.c`
- **Relevance: HIGH.** Artist-driven repair ops with vocabulary (dissolve / decimate / unsubdivide) not present in academic libraries.

#### 25. VTK (Visualization Toolkit)
- URL: https://gitlab.kitware.com/vtk/vtk
- License: BSD-3-Clause
- Domain: Visualization + filter graph; significant mesh repair
- Languages: C++ / Python
- Entry points: `vtkCleanPolyData`, `vtkStaticCleanPolyData`, `vtkFillHolesFilter`, `vtkPolyDataNormals`, `vtkTriangleFilter`, `vtkFeatureEdges`, `vtkExtractEdges`, `vtkStripper`, `vtkDelaunay2D`/`3D`, `vtkBooleanOperationPolyDataFilter`, `vtkLoopBooleanPolyDataFilter`, `vtkCleanUnstructuredGrid`
- **Relevance: HIGH.** Header docstrings are uniformly thorough; `vtkClean*` parameter docs are an in-line defect-handling taxonomy.

---

### File-format / parser-level domain

#### 26. STEPcode (formerly NIST STEP Class Library)
- URL: https://github.com/stepcode/stepcode
- License: BSD-3-Clause
- Domain: ISO 10303 Part 21 parser generator
- Languages: C++ / Lex / Yacc / Python
- Entry points: `stepcode/src/exp2cxx`, the lex/yacc grammar files; issue tracker
- **Relevance: HIGH (partially audited).**

#### 27. IfcOpenShell — `step-file-parser` and `ifcpatch`
- URL: https://github.com/IfcOpenShell/IfcOpenShell ; https://github.com/IfcOpenShell/step-file-parser
- License: LGPL-3.0
- Domain: IFC + Part 21
- Languages: Python / C++ / Lark
- Entry points: `step-file-parser` (Lark grammar); `ifcpatch` (canonical repair recipes); `ifcedit`
- **Relevance: HIGH (partially audited — `ifcpatch` recipe names underexplored).**

#### 28. IFC++ (ifcplusplus)
- URL: https://github.com/ifcquery/ifcplusplus
- License: MIT
- Domain: IFC reader/writer (Part 21)
- Languages: C++
- Entry points: Parallel parser; geometry processing via Carve or OCCT
- **Relevance: MEDIUM.** Different parser implementation than IfcOpenShell — bug list will reveal parser-divergence quirks.

#### 29. lib3mf (3MF Consortium)
- URL: https://github.com/3MFConsortium/lib3mf
- License: BSD-2-Clause
- Domain: 3MF file format
- Languages: C++ / multi-language bindings
- Entry points: Validator (warnings/errors against the 3MF spec); test corpus in repo
- **Relevance: HIGH (not yet audited).** 3MF is a ZIP-of-XML format with extension namespaces, MUST-IGNORE rules, production-extension defects — completely distinct from STEP, STL, mesh.

#### 30. admesh (libadmesh)
- URL: https://github.com/admesh/admesh
- License: GPL-2.0
- Domain: STL repair CLI + library
- Languages: C
- Entry points: `--fix-normal-directions`, `--fix-normal-values`, `--remove-unconnected-facets`, `--fill-holes`, `--check-degenerate`, `--check-nearby`, `--reverse-all`; library API mirrors flags
- **Relevance: HIGH.** Defects are at the *binary STL record* level — distinct from B-rep, distinct from generic mesh. Used inside Slic3r/PrusaSlicer.

#### 31. Slic3r / PrusaSlicer model_repair path
- URL: https://github.com/prusa3d/PrusaSlicer ; https://github.com/slic3r/Slic3r
- License: AGPL-3.0
- Domain: Slicer with model repair (Windows uses Netfabb API; Linux uses admesh fallback)
- Languages: C++
- Entry points: `xs/src/admesh/`, `src/libslic3r/TriangleMesh.cpp::repair()`; Win API integration in `src/slic3r/GUI/`
- **Relevance: MEDIUM-HIGH.** Glue between admesh, CGAL, and Microsoft repair API documents which defect classes need a fallback path on which OS.

#### 32. Bambu Studio
- URL: https://github.com/bambulab/BambuStudio
- License: AGPL-3.0
- Domain: Slicer (Prusa fork) with extended repair
- Languages: C++
- Entry points: PrusaSlicer's repair surface + Bambu's added pre-slicing fixes (over-extrusion-prone regions)
- **Relevance: MEDIUM.** Mostly inherits Prusa; novel pieces in Bambu-specific extensions.

#### 33. Cura / CuraEngine
- URL: https://github.com/Ultimaker/CuraEngine
- License: AGPL-3.0
- Domain: Slicer; less explicit mesh-repair than Prusa
- Languages: C++
- Entry points: Tolerance for broken/non-watertight models in slicing layer (rather than pre-slice repair)
- **Relevance: LOW-MEDIUM.** Implicit defect-tolerance, not explicit repair.

#### 34. assimp (Open Asset Import Library)
- URL: https://github.com/assimp/assimp
- License: BSD-3-Clause
- Domain: Multi-format 3D asset reader
- Languages: C++
- Entry points: `aiProcess_JoinIdenticalVertices`, `aiProcess_Triangulate`, `aiProcess_FixInfacingNormals`, `aiProcess_FindDegenerates`, `aiProcess_FindInvalidData`, `aiProcess_GenSmoothNormals`, `aiProcess_ImproveCacheLocality`, `aiProcess_RemoveRedundantMaterials`, `aiProcess_OptimizeMeshes`, `aiProcess_OptimizeGraph`, `aiProcess_SplitLargeMeshes`, `aiProcess_PreTransformVertices`, `aiProcess_LimitBoneWeights`, `aiProcess_ValidateDataStructure`, `aiProcess_SortByPType`
- **Relevance: HIGH.** `postprocess.h` is a 30+ flag *taxonomy* of "what could be wrong with a file that the reader can fix" — covers OBJ, FBX, COLLADA, glTF, 3DS, BLEND, X3D, PLY, STL, etc. Multi-format breadth not available anywhere else.

#### 35. tinyobjloader / tinygltf / tinyply / happly
- URL: https://github.com/tinyobjloader/tinyobjloader ; https://github.com/syoyo/tinygltf ; https://github.com/nmwsharp/happly
- License: MIT
- Domain: Header-only single-format readers
- Languages: C++
- Entry points: Robust OBJ parser w/ mapbox earcut triangulation; tinygltf has codegen-from-JSON-schema for safety
- **Relevance: MEDIUM.** Individual-format quirks (OBJ NaN coords, glTF JSON edge cases, PLY endianness) documented in issue trackers.

#### 36. meshio (nschloe/meshio)
- URL: https://github.com/nschloe/meshio
- License: MIT
- Domain: I/O between many FEM mesh formats
- Languages: Python
- Entry points: Format-detection logic, per-format readers (Gmsh `.msh` v2/v4, XDMF, Exodus, CGNS, DOLFIN XML, Abaqus `.inp`, ANSYS msh, MED, OFF, OBJ, PLY, STL, VTK, VTU, AVS-UCD, etc.); `ReadError` taxonomy
- **Relevance: HIGH.** Issue tracker is dense with format-level defects per-format. Multi-format breadth.

---

### CSG / boolean / SDF / volumetric domain

#### 37. Manifold (elalish)
- URL: https://github.com/elalish/manifold
- License: Apache-2.0
- Domain: Guaranteed-manifold triangle-mesh boolean kernel
- Languages: C++ / WASM
- Entry points: `Manifold::AsOriginal`, `Manifold::Status`, `Manifold::IsManifold`, `Merge` (slightly-non-manifold fixup); issue tracker for input-degeneracy patterns
- **Relevance: HIGH (only partially audited).**

#### 38. Carve
- URL: https://github.com/folded/carve (multiple forks; Blender vendor copy)
- License: GPL-2.0 (with some MIT components)
- Domain: CSG / mesh boolean
- Languages: C++
- Entry points: `csg::CSG::compute`, `csg_triangulator`, intersection-detection helpers
- **Relevance: MEDIUM.** Known unstable on degenerate input — bug history reveals failure-mode taxonomy. Used by Blender pre-Manifold and IFC++.

#### 39. VTKbool (zippy84/vtkbool)
- URL: https://github.com/zippy84/vtkbool
- License: Apache-2.0
- Domain: Alternative VTK boolean filter
- Languages: C++
- Entry points: `vtkPolyDataBooleanFilter`; issues document failure modes (CutCells failure, ambiguous intersection lines, non-manifold-edge contact)
- **Relevance: MEDIUM-HIGH.** Failure-mode prose is unusually well-explained in issues.

#### 40. libfive
- URL: https://github.com/libfive/libfive
- License: MPL-2.0 / GPL-2.0 (Studio)
- Domain: F-rep / implicit modelling
- Languages: C++ / Scheme / Python
- Entry points: Watertight-manifold mesher (DC variant); meshing-output validation
- **Relevance: MEDIUM.** Mostly avoids defects by construction — but the mesher's invariants are themselves a description of what *could* go wrong.

#### 41. OpenSCAD
- URL: https://github.com/openscad/openscad
- License: GPL-2.0
- Domain: CSG via CGAL Nef polyhedra or Manifold backend
- Languages: C++
- Entry points: `polyset` repair logic; "CGAL Nef-to-mesh" conversion edge cases; #1650 STEP-import discussion
- **Relevance: MEDIUM.** Issue tracker has decade-spanning CSG-edge-case discussion.

#### 42. OpenVDB
- URL: https://github.com/AcademySoftwareFoundation/openvdb
- License: MPL-2.0
- Domain: Sparse volumetric grids; mesh<->volume conversion
- Languages: C++
- Entry points: `meshToVolume`, `volumeToMesh`; `isNonManifold` in dual-contouring meshing; voxelisation tolerates self-intersection, degenerate faces, non-manifold input
- **Relevance: HIGH (no current coverage).** Mesh-via-volume *introduces* a distinct defect class (staircase artefacts, dual-contour non-manifold output, aliasing) and *tolerates* a distinct input set — the inverse domain from boolean kernels.

---

### Volumetric / tet-mesh domain

#### 43. TetGen
- URL: https://www.wias-berlin.de/software/tetgen/
- License: AGPL-3.0 (v1.5+) / MIT-with-noncommercial (v1.4.3)
- Domain: Constrained-Delaunay tet mesher
- Languages: C++
- Entry points: PLC preprocessing; CDT pre-conditions
- **Relevance: MEDIUM.** PLC validation is a tetra-specific defect taxonomy.

#### 44. fTetWild / TetWild / WildMeshing
- URL: https://github.com/wildmeshing/fTetWild
- License: MPL-2.0
- Domain: Robust tetrahedral meshing from messy surface input
- Languages: C++
- Entry points: `--skip-simplify`, `--manifold-surface`, `--smooth-open-boundary`, `--filter-with-input`; envelope-based snapping; preprocessing pipeline
- **Relevance: HIGH.** Whole *point* of TetWild is "accept arbitrary garbage input" — the preprocessing pipeline is an enumeration of what input garbage looks like.

#### 45. MMG / MMG3D
- URL: https://github.com/MmgTools/mmg
- License: LGPL-3.0+
- Domain: Surface + 3D mesh adaptation/remeshing
- Languages: C
- Entry points: `MMG3D_mmg3dlib`; isotropic/anisotropic remeshing; boundary recovery
- **Relevance: MEDIUM.** Boundary-recovery problems are a tet-mesh-specific defect class.

---

### Triangulation / Delaunay / Voronoi-cell domain

#### 46. Triangle (Shewchuk)
- URL: https://www.cs.cmu.edu/~quake/triangle.html
- License: Non-commercial (proprietary-ish)
- Domain: 2D Delaunay / CDT
- Languages: C
- **Relevance: LOW.** Closed-license problematic; but its input-validation taxonomy (collinear input, duplicate input, segment-intersection handling) is a small but distinct defect class.

#### 47. CGAL 2D Triangulations + 2D Conforming Triangulations
- URL: https://doc.cgal.org/latest/Triangulation_2/
- License: GPL/LGPL
- **Relevance: MEDIUM.** Distinct domain from PMP repair.

#### 48. mapbox/earcut
- URL: https://github.com/mapbox/earcut
- License: ISC
- Domain: Polygon-with-holes ear-clip triangulation
- Languages: C++ / JS / Python
- Entry points: Robust handling of self-touching polygons, near-degenerate input
- **Relevance: MEDIUM.** Used inside tinyobjloader; documents polygon-input edge cases.

---

### Subdivision / NURBS domain

#### 49. OpenSubdiv (Pixar)
- URL: https://github.com/PixarAnimationStudios/OpenSubdiv
- License: Apache-2.0
- Domain: Subdivision surface evaluator
- Entry points: Watertight crease handling; non-manifold control-mesh handling
- **Relevance: LOW-MEDIUM.** Subdivision-control-mesh defects are a separate domain.

---

### Closed-source benchmarks (worth knowing about, prose only)

#### 50. Polygonica (TechSoft 3D)
- URL: https://www.machineworks.com/polygonica/
- License: Commercial only
- Domain: Industrial mesh-healing SDK (embedded in 30+ products incl. Stratasys, 3D Systems, ANSYS)
- **Relevance: AUDIT-ABLE BY DOC ONLY.** Marketing pages enumerate defect classes: gaps, self-intersections, non-manifold geometry, foldovers, overlaps; published taxonomy aligns with MeshFix but adds *foldover* and *wall-thickness-driven* repair primitives.

#### 51. Netfabb / Microsoft Model Repair (Azure)
- URL: https://tools3d.azurewebsites.net/
- License: Commercial (Autodesk) / free Microsoft cloud service
- Domain: STL/3MF cloud repair
- **Relevance: AUDIT-ABLE BY DOC ONLY.** Documented defect classes: duplicate vertices, bad face normals, non-manifold edges, internal-geometry removal, unintended cavities.

#### 52. Spatial 3D InterOp (ACIS-adjacent)
- URL: https://www.spatial.com/
- License: Commercial
- **Relevance: LOW (closed; only blog posts).**

---

## STILL-MISSING DOMAINS — Even after a fuller audit

Even with the above 52 codebases catalogued and audited, the following areas remain under- or
un-represented in our current catalogue and would close gaps:

1. **CAD-history / feature-tree repair.** All audited codebases operate on *resolved* geometry.
   Defects in the *feature-history graph* — broken sketch constraints, dangling parametric
   references, regenerate-failed features, lost design intent on STEP-roundtrip — have no
   open-source kernel equivalent. The closest is FreeCAD's parametric-graph error reporting,
   but it is shallow. **Audit candidate:** FreeCAD Sketcher constraint-solver issues +
   SolveSpace constraint-solver issues. We have *zero* feature-graph-defect coverage.

2. **CAM-toolpath repair.** Self-intersecting toolpaths, gouge-detection failures, non-monotonic
   feeds — distinct from mesh repair but adjacent. Open-source: `pycam`, `LibreCAM`,
   `FreeCAD Path workbench`, `LinuxCNC` G-code. **Not yet audited.**

3. **GD&T / PMI semantic defects.** PMI tessellation in STEP AP242 can be syntactically valid
   but semantically wrong (datum on a degenerated face, tolerance referencing missing geometry).
   Audited at the CAx-IF level but not at the open-source-implementation level — `STEPcode-pmi`,
   `IfcOpenShell` semantics layer not deeply mined.

4. **Drawing / 2D-DXF repair.** DXF self-intersecting hatches, broken polylines, gradient-fill
   degeneracies. Open-source: `LibreCAS`, `QCAD`, `ezdxf`, `dxflib`. **Not yet audited — entirely
   separate defect domain.** STEP-AP242 view-and-drawing path also lives here.

5. **Point-cloud → mesh defects (scan-to-CAD).** Defects introduced by surface reconstruction
   from noisy point clouds (Poisson reconstruction bridges, MLS-overshoot artefacts).
   `Open3D`, `MeshLab Poisson plugin`, `CGAL Surface_reconstruction_points_3`,
   `Geogram co3ne`. **Not yet audited.**

6. **Voxel-back-to-surface healing.** OpenVDB partially covered above, but dedicated work in
   *dual contouring*, *manifold dual contouring*, *Cubical Marching Squares* (e.g.
   `libfive`, `Dreams Doc / Dreamcatcher`, MS DirectXMesh) deserves attention as a distinct
   defect-producing pipeline.

7. **3MF + glTF semantic extensions.** glTF has many vendor-extensions (KHR_materials_*,
   EXT_mesh_gpu_instancing). Defects at the *extension* level are a parser-tolerance domain
   with no current coverage — particularly DRACO mesh-compression decode errors and
   `KHR_mesh_quantization` numeric edge cases.

8. **STL / PLY *binary* corruption.** Bit-level defects: misaligned strides, truncated files,
   wrong endianness on PLY, NaN in coords, header lies about facet count. Admesh covers some
   but not all. **`tinyply`, `happly`, `libplyio`** worth auditing.

9. **IFC semantic repair (not geometric).** Building-element classification errors (a `IfcSlab`
   that is actually a beam), property-set drift, broken `IfcRelAggregates`. `ifcpatch` recipes
   target some of this; `IDS` (Information Delivery Specification) validation tooling is a
   newer concept worth tracking. **Out of scope for a *geometry* defect catalogue, but
   relevant if scope is "STEP / IFC interop quality".**

10. **Sweep / loft / fillet algorithmic failure modes.** OCCT `BRepFill`, `BRepOffsetAPI_MakePipe`,
    `BRepOffsetAPI_MakePipeShell`, `BRepFilletAPI_*` have known input-degeneracy classes
    (rail-curves not C1, spine self-intersection, fillet radius > local radius of curvature).
    These are *in* OCCT and arguably already partly audited, but the *sweep-specific* failure
    taxonomy is not separated out. Worth a focused re-pass.

11. **Procedural-geometry / OpenSCAD / signed-distance pipeline defects.** Self-overlapping
    procedural geometry, infinite-recursion sketches, parameter-driven degeneracies. Open-source:
    `OpenSCAD` issue tracker (#1650 et al.), `libfive`, `SDFKit`. **Not yet audited at scale.**

12. **Microsoft / Windows 3D-API repair surfaces.** `Direct3D11Mesh` validation, `DirectXMesh`
    optimisation. Closed but documented. **No coverage.**

13. **Reverse-engineering / scan-to-CAD round-trip defects.** Geomagic / 3D-Systems pipelines.
    Closed source. Patent literature is the only open prose.

14. **Hex-mesh and mixed-element-mesh repair.** Different from tet-mesh repair: scaled jacobian,
    inverted hexes, hanging nodes from non-conforming refinement. `coreform/cubit-trelis`
    (closed), `OpenFOAM checkMesh`, `Mmgs`. **No coverage.**

15. **GPU / compute-mesh defects** — mesh shaders, meshlet boundaries, draw-call-level
    primitives. `MeshOptimizer` (zeux/meshoptimizer) has its own taxonomy of "this mesh is
    bad for the GPU" defects (vertex-cache thrash, overdraw, meshlet-boundary cuts). **Not yet
    catalogued.**

---

## Audit-priority shortlist (collapsed)

If only 5 more audits happen, take them in this order:

1. **MeshLab `filter_clean` + vcglib `vcg::tri::Clean` namespace** — most distinct vocabulary;
   single-source taxonomy.
2. **VTK `Filters/Core` + `Filters/Modeling` clean/fill/repair headers** — well-documented;
   covers a defect axis (filter-graph defects) currently underrepresented.
3. **CGAL Polygon Mesh Processing — Repair package deep re-audit + the 2025 autorefine-and-snap
   update** — closes a known gap (we have only partial PMP coverage).
4. **Assimp `postprocess.h` 30+ flag taxonomy** — multi-format breadth no other library matches.
5. **lib3mf + admesh** — only file-format-level repair surfaces in the corpus distinct from STEP.

---

*End of landscape document. Read-only enumeration; no code or fixtures copied.*
