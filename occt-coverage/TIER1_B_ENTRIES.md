# Tier-1B staging: §12.15 MeshLab-mined parser differentials (2026-07)

Staging file for new catalog entries pending merge into `STEP_PROBLEM_CATALOG.md`.
Source: `audit/mining_meshlab_draco_ftetwild_2026-07.md`, MeshLab/vcglib candidates
9–11 only (candidates 1–8 are Draco `.drc` — owned by a sibling agent, not
duplicated here; candidates 12–16 are fTetWild — deferred to §12.14, see note
at end of this file, not synthesized here).

---

### Ip031 — OFF well-formed n-gon face crashes fan-triangulation on an independent reader
- **Category**: §12.15 import-format parser robustness (sub-class: n-gon-fan-triangulation)
- **Sources**: Pattern-mined from cnr-isti-vclab/meshlab#1163 (`confirmed`) (GPL-3.0 — pattern only, no bytes copied).
- **Description**: An OFF file whose header `8 1 0` and body counts are exactly correct (8 vertex rows, 1 face row) — no declared-count-vs-body mismatch, unlike Ip003/Ip010 — defines a single well-formed 7-gon face `7 4 6 0 2 3 1 5`. The face is syntactically valid: all 7 referenced indices are in range and none repeat. vcglib's polygon→triangle fan-triangulation path (used by MeshLab's OFF importer) mishandles n>4 polygons on this input (ml#1163, `confirmed`). This is a pure differential: the file has no malformation an OFF-spec validator would flag.
- **Reproducer recipe**: OFF header `8 1 0` matching 8 coordinate rows and 1 face row exactly, with the face line `7 4 6 0 2 3 1 5` — a 7-sided polygon (k=7 followed by 7 valid, non-repeating vertex indices, one vertex of the 8 left unreferenced).
- **Expected kernel behavior**: fan-triangulate (or ear-clip) an arbitrary well-formed n-gon face robustly for any n, or reject with a diagnostic naming the face; never crash on a syntactically valid polygon record.
- **Byte assertion**: contains(b'7 4 6 0 2 3 1 5')
- **Fixture path**: import-examples/12-15-import-formats/Ip031.off
- **Fixture kind**: raw import-format file (parser-robustness; graded against assimp/trimesh, not Part-21)
- **Notes**: Live-verified 2026-07-17 with trimesh 4.12.2: loads cleanly, fan-triangulates the 7-gon from its first listed index (vertex 4) into 5 triangles `[[4,6,0],[4,0,2],[4,2,3],[4,3,1],[4,1,5]]`, drops the one unreferenced vertex (7 verts / 5 faces reported) — no exception. ml#1163 documents MeshLab's vcglib-based OFF importer crashing (`confirmed` label) on this same well-formed-n-gon pattern — a clean cross-oracle divergence on identical, spec-valid bytes. Synonyms: "OFF n-gon fan triangulation crash", "polygon face k>4 crash", "well-formed OFF polygon crashes importer", "vcglib populateTriangles n-gon". Provenance tier: bytes-only.
- **Severity**: P2
- **Model impact**: A syntactically valid polygon face with no count or index defect crashes one independent reader outright while another silently re-triangulates it via an implementation-chosen fan (order-dependent for non-convex polygons); the kernel cannot assume n-gon handling is either safe or triangulation-order-stable across importers.

---

### Ip032 — PLY unknown per-vertex LIST property crashes an independent reader (formerly ignored)
- **Category**: §12.15 import-format parser robustness (sub-class: unrecognized-list-typed-property)
- **Sources**: Pattern-mined from cnr-isti-vclab/meshlab#1624 (GPL-3.0 — pattern only, no bytes copied).
- **Description**: An ASCII PLY vertex element declares a custom, non-standard property that is *list-typed* rather than scalar: `property list uchar int neighbor_indices`, i.e. each vertex row carries its own count-prefixed integer list (here, 2 neighbor indices) in addition to `x y z`. The header is fully self-describing (count-type `uchar`, value-type `int`, declared per PLY spec) and every vertex row supplies exactly the count it declares. ml#1624 reports this construct — previously silently skipped by MeshLab — now over-reads or crashes, a regression from tolerant to fragile on a file the spec permits. Distinct from Ip009 (extra *scalar* fields) and Ip015 (zero-count element): this is a *list-typed* custom property on the vertex element, which a naive property-skipper (that assumes every unknown property is a fixed-width scalar) mishandles by advancing the read cursor by a wrong, fixed byte count.
- **Reproducer recipe**: an ASCII PLY with `element vertex 3`, `property float x/y/z`, then `property list uchar int neighbor_indices` before `end_header`; each of the 3 vertex rows carries `x y z <count> <count ints>` (here count=2), followed by a normal triangular face element.
- **Expected kernel behavior**: skip unrecognized properties by consuming exactly their declared per-row structure (read the list's own count prefix and skip that many list elements), never assume unknown properties are fixed-width scalars.
- **Byte assertion**: contains(b'property list uchar int neighbor_indices')
- **Fixture path**: import-examples/12-15-import-formats/Ip032.ply
- **Fixture kind**: raw import-format file (parser-robustness; graded against assimp/trimesh, not Part-21)
- **Notes**: Live-verified 2026-07-17 with trimesh 4.12.2: loads cleanly, correctly skips the unrecognized `neighbor_indices` list property per vertex row and returns the intended 3 vertices / 1 face with correct coordinates — no exception, no corruption. ml#1624 documents MeshLab's PLY importer regressing from silent-ignore to over-read/crash on this same list-typed unknown-property pattern. Synonyms: "PLY unknown list property crash", "custom per-vertex list field", "PLY property skip assumes scalar width", "non-standard vertex list property". Provenance tier: bytes-only.
- **Severity**: P2
- **Model impact**: A reader that assumes unrecognized properties are fixed-width scalars will misalign every subsequent field read once it encounters a list-typed custom property, corrupting all downstream vertex/face parsing for the rest of the file — or crash outright, as MeshLab does per ml#1624.

---

### Ip033 — glTF POINTS-mode primitive (no indices) routed through a triangle assembler
- **Category**: §12.15 import-format parser robustness (sub-class: primitive-mode-mismatch)
- **Sources**: Pattern-mined from cnr-isti-vclab/meshlab#1387 (`confirmed`), ml#1484 (GPL-3.0 — pattern only, no bytes copied).
- **Description**: A minimal, spec-valid glTF 2.0 document defines one mesh primitive with `"mode": 0` (POINTS) and only a `POSITION` accessor — no `indices`, as the glTF spec permits for point-cloud primitives (draw mode 0 renders each vertex as an independent point, no connectivity needed). ml#1387/#1484 report MeshLab's glTF importer feeding every primitive, regardless of declared `mode`, into a templated `populateTriangles<T>()` assembler that assumes triangle connectivity — producing a SEGV on a POINTS primitive with no index buffer to read triangles from. Distinct from the assimp-mined glTF candidates (Ip004/Ip007/Ip008/Ip011/Ip012, all attribute/accessor layout defects): this file has no accessor or buffer defect at all — every accessor is well-formed and in-bounds — the defect is purely that the primitive's declared draw `mode` is never branched on before triangle assembly.
- **Reproducer recipe**: a glTF JSON with one mesh, one primitive whose `attributes` is `{"POSITION": 0}` (no `"indices"` key) and `"mode": 0`, backed by a correctly-sized base64 data-URI buffer holding 3 well-formed VEC3/float32 positions.
- **Expected kernel behavior**: branch on the primitive's declared `mode` before assembling triangle connectivity; render/import POINTS (and LINES/LINE_STRIP/etc.) primitives through a mode-appropriate path, or reject with a diagnostic if only triangle primitives are supported — never assume every primitive has triangle indices.
- **Byte assertion**: contains(b'"mode": 0')
- **Fixture path**: import-examples/12-15-import-formats/Ip033.gltf
- **Fixture kind**: raw import-format file (parser-robustness; graded against assimp/trimesh, not Part-21)
- **Notes**: Live-verified 2026-07-17 with trimesh 4.12.2: loads cleanly as a `Scene` containing one `trimesh.points.PointCloud` with `vertices.shape=(3,3)` — trimesh correctly branches on `mode: 0` and never attempts triangle assembly. ml#1387 (`confirmed`) and ml#1484 document MeshLab's glTF importer crashing (SEGV) on this same well-formed POINTS-mode pattern by unconditionally routing every primitive through its triangle assembler. Synonyms: "glTF POINTS mode primitive crash", "point cloud primitive routed to triangle assembler", "glTF mode 0 no indices SEGV", "primitive mode not branched before triangulation". Provenance tier: bytes-only.
- **Severity**: P2
- **Model impact**: A spec-valid point-cloud primitive (a legitimate glTF construct, e.g. LIDAR/scan-derived assets) crashes an importer that assumes universal triangle connectivity; any pipeline ingesting third-party glTF assets must not assume `mode` is always 4 (TRIANGLES).

---

## fTetWild candidates (12–16): deferred to §12.14 `Me*`, NOT synthesized here

Per task scope: these are volumetric/mesh-*repair* oracle defects, not
import-format *parse*-layer defects — forcing them into a raw `Ip*` file would
misrepresent what they demonstrate (the input files are all **structurally
valid** per `mesh_builder`'s model; the defect is only visible to a
tetrahedralizer/CSG oracle the mesh test harness does not currently invoke).
This matches the mining doc's own target-bucket conclusion (§"Target-bucket
summary": "fit `mesh_builder`'s structurally-valid model, but require grading
against a volumetric oracle... the oracle wiring is the BACKLOG item").

Deferred, in mining-doc order:

- **#12** Inconsistent triangle winding → winding-number volume extractor drops
  the interior (near-empty tet output). Needs a volumetric/winding-number
  oracle; current `Me*` orientation fixtures grade against surface healers only.
- **#13** Non-watertight CSG operand → boolean returns zero cells, silent-empty
  at the volumetric-boolean stage (ftw#37). Needs a CSG/tetrahedralizer oracle.
- **#14** Multi-material stack sharing an interior face → non-manifold
  *interior/volume* face (ftw#69), distinct from existing Me001's non-manifold
  *surface edge*. Needs per-region volumetric tagging support in the harness.
- **#15** Tangent/touching solids (measure-zero contact patch) → degenerate
  conformal interface (ftw#64). Needs volumetric-interface oracle.
- **#16** Many-component (~hundreds) input → segfault in fTetWild's
  edge-swap preprocessing (ftw#75). Weakest of the five (mining doc notes "no
  minimal upstream repro"); also needs the volumetric-oracle wiring, so
  deferred alongside the rest rather than partially synthesized.

None of these were written as `Ip*` fixtures or consumed reserved IDs. They
remain candidates for a future §12.14 mesh-pipeline wave once a volumetric
oracle (fTetWild or equivalent) is wired into the mesh test harness — see
`BACKLOG.md`.
