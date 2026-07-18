# Mining assimp for file-level malformed-input defect classes (2026-07)

**Source.** assimp (Open Asset Import Library), https://github.com/assimp/assimp —
an **independent** importer for many mesh/geometry container formats, heavily
OSS-Fuzz'd (`assimp_fuzzer`). Flagged HIGH in `audit/source_survey_2026-07.md`
because (a) it is a non-OCCT import path (kernel diversity) and (b) fuzzer
crashers ship minimal self-contained reproducers.

**License.** assimp is BSD-3-Clause. We **describe patterns only** — no file
bytes, no repro attachments, and no OSS-Fuzz corpus files are ingested. Every
fixture below would be **synthesized from scratch** to embody the described
construct. OSS-Fuzz repro files carry mixed/unknown licenses → describe-only,
harvest individually, never bulk-ingest (survey §"Public test-file collections").

---

## Novelty context (checked against the live corpus)

- The mesh corpus (**§12.14 `Me*`, 762 entries**) is built by
  `validation/src/step_corpus/mesh_builder.py`, which emits a JSON mesh (plus
  optional OBJ/PLY *interop* renders) carrying **geometry/topology defects**
  (non-manifold edges, degenerate/sliver triangles, self-intersections, holes,
  CGAL-PMP / MeshFix branch-coverage cases). **Every file it produces is
  structurally valid** — the builder cannot express a lie in the header, a
  count/row mismatch, an out-of-range index, an unresolved reference, or a
  truncated/encoding fault.
- `grep` of §12.14: **glTF / COLLADA / 3MF / FBX = 0 occurrences.** OBJ/PLY/OFF
  appear only as *geometry-defect* render targets, never as parser-defect
  carriers. There is **no** file-level "header count > body rows", "index ≥
  vertex count", "accessor over-runs bufferView", or "truncated multibyte"
  fixture anywhere in the mesh section.
- §12.11 Adversarial (`Ad*`) holds STEP/Part-21 parser crashers and one
  STEP-adjacent container item (`Ad111` 3MF/IFCZIP **zip-bomb**, decompression
  OOM only). It contains **no** native mesh-container parser fixtures and no
  payload-index / count-mismatch class.

**Conclusion:** every candidate below is a **NEW file-level parser/container
class** for a format the corpus does not exercise at the parse layer. They need
**raw synthesized files**, so they do **NOT** fit `mesh_builder`. See "Target
category" at the end.

---

## Candidate defect classes (26 across 9 formats)

Citations are `assimp#NNNN` (github.com/assimp/assimp/issues/NNNN) plus upstream
OSS-Fuzz testcase ids where known — **pattern reference only, no bytes**.

### glTF / GLB — JSON + binary buffer; independent glTF2 importer

| # | Defect class | Citation | Reproducer recipe | Expected behavior |
|---|---|---|---|---|
| 1 | Node `matrix` with insufficient backing data → 64 B read from ~1 B alloc | #6612 (`CopyValue`, glTFCommon.h) | Node declares a `MAT4` transform but the accessor/value supplies < 16 floats. `CopyValue(float[16])` unconditionally reads 64 B. | Verify 16 floats present before copy; else diagnostic-reject. |
| 2 | Accessor over-runs its bufferView (`count×stride > byteLength`) | #6488 / #1002 (`ExtractData`; assert `i*stride < byteLength`); OSS-Fuzz 483102963 | `accessor.count × element-size` (or `byteOffset`) exceeds `bufferView.byteLength`. ExtractData copies without clamping. | Enforce `byteOffset + count*stride ≤ bufferView.byteLength ≤ buffer.byteLength`. |
| 3 | Accessor `type`/`componentType` mismatch vs buffer element size | #5683 | `type:"VEC3"` + `componentType:5121` (UNSIGNED_BYTE) but data laid out as float; raw `memcpy` ignores component size/normalization. | Honor declared component type & normalization; size-check first. |
| 4 | `bufferView`/`buffer`/node `children` reference index out of range | #6485 (`ImportNode`), OSS-Fuzz 483501004 | An object index (`accessor.bufferView`, `bufferView.buffer`, node `children[]`, scene node list) is ≥ the referenced array length. | Validate every object index against its array length at load. |
| 5 | LINE_LOOP / LINE_STRIP primitive with < 2 indices | #6634 (`ImportMeshes`) | Primitive `mode` = LINE_LOOP/LINE_STRIP but the index accessor yields 1 index; code reads `indexBuffer[1]`. | Require ≥ 2 indices for line primitives; skip/reject otherwise. |
| 6 | `componentType` is an invalid enum value | #6527 (`Accessor::Read`), OSS-Fuzz 483099602 (UBSAN) | `componentType` outside {5120…5126}; cast to enum and used for element-size math. | Reject unknown componentType before size computation. |
| 7 | Unchecked `ExtractData()` NULL return dereferenced | #6609 (glTF 1.0 `ImportMeshes`) | Texcoord accessor references a missing/invalid bufferView → ExtractData returns NULL, which is then dereferenced. | Null-check ExtractData result before use. |
| 8 | Animation channel targets a NULL / unpopulated node slot | #6611 (`LazyDict::operator[]`) | Animation channel target node index points at a dictionary slot never populated (NULL). | Bounds/NULL-check node indices in animation targets. |
| 9 | Degenerate/short UV channel → tangent-space post-process OOB | #6350 (`CalcTangentsProcess`) | Texcoord accessor yields fewer UVs than vertices; with `aiProcess_CalcTangentSpace`, `meshTex[p]` indexes past the UV array. | Guard tangent calc against missing/short UV channels. |

### PLY — ASCII + binary; `PLYImporter`

| # | Defect class | Citation | Reproducer recipe | Expected behavior |
|---|---|---|---|---|
| 10 | `element vertex N` header > body rows / extra property field → OOB write | #5729, OSS-Fuzz 6544205135544320 (`LoadVertex`, heap-overflow WRITE); fix PR#5956 | Header declares more vertices than the body streams, OR a row supplies more scalar fields than declared properties. LoadVertex writes past the vertex buffer. | Bound each write to declared N and declared property count. |
| 11 | Blank line after `end_header` shifts binary body → wild face indices | #5341 (`PlyParser` / `SkipSpacesAndLineEnd`) | A `\n` right after `end_header` is swallowed, mis-consuming the first face record byte; all element parsing shifts → face indices like 33554432. | Do not skip blank lines in binary bodies; treat post-header bytes literally. |
| 12 | Face list index ≥ declared vertex count | #5341 downstream (validation-caught, but post-parse) | A `vertex_indices` list entry names an index ≥ declared vertex count. | Reject/clamp out-of-range face indices at parse time. |

### OBJ — ASCII; `ObjFileParser`

| # | Defect class | Citation | Reproducer recipe | Expected behavior |
|---|---|---|---|---|
| 13 | Face vertex index exceeds vertex count (positive OOB) | #1047 ("vertex index out of range"; MeshLab tolerates) | `f a b c` where a/b/c > number of `v` lines. Cross-oracle: assimp errors, MeshLab loads. | Clamp/skip or error gracefully; differential-tolerance signal. |
| 14 | Vertex-normal / texcoord index out of range | #755 ("vertex normal index out of range") | `f v//vn` where `vn` index > number of `vn` lines (or `vt` > `vt` count). | Bounds-check per-attribute index; tolerate or error, don't hard-stop. |
| 15 | Negative relative index below `-(current count)` | #281, #2349 (broken-index class); assimp 6.0.4 face-scan fix | OBJ allows negative back-refs; `f -9 -1 -1` when < 9 vertices seen → resolves < 1. | Resolve negatives against running count; reject if < 1. |
| 16 | Crafted counts drive unbounded allocation / super-linear parse (OOM/timeout) | #6571 (OOM, OSS-Fuzz 487634479), #6502 (timeout, OSS-Fuzz 483113942) | Constructs implying huge vertex/index ranges or quadratic tokenizer behavior (many groups/materials, long malformed lines). | Cap allocation vs input size; linear-time parse with a work bound. |

### OFF — ASCII; via `ParsingUtils`

| # | Defect class | Citation | Reproducer recipe | Expected behavior |
|---|---|---|---|---|
| 17 | Missing line terminator → `SkipLine`/`NextToken` infinite loop (DoS) | #6604 (OFFLoader.cpp), also #6016/#5860 (`GetNextLine`/`SkipSpacesAndLineEnd`) | Token line lacks the expected terminator at EOF; SkipLine never advances → 25 s+ hang. | SkipLine must advance on EOF; bound the loop to buffer end. |
| 18 | Header `V F E` counts > actual rows; polygon prefix / index mismatch | #2228 (OFF header-trust class) | Header claims more verts/faces than present, or a face `k i0 i1 …` whose `k` disagrees with the row, or `ij ≥ V`. | Stop at EOF; validate prefix vs row and each index vs V. |

### COLLADA / DAE — XML; `ColladaParser` / `ColladaLoader`

| # | Defect class | Citation | Reproducer recipe | Expected behavior |
|---|---|---|---|---|
| 19 | `<p>` primitive index references vertex beyond `<source>` → OOB read | #6522 (`CopyVertex`/`ReadPrimitives`), OSS-Fuzz 483173710 | A `<p>` index inside `<triangles>`/`<polylist>` ≥ the count of the referenced `<source>`/`<float_array>`; CopyVertex reads past the array. | Validate every `<p>` index against source accessor count. |
| 20 | `<accessor>` count/stride/offset describe more than `<float_array>` holds | #4285 (`CreateMesh`, SIGSEGV) | Accessor geometry claims more elements than the underlying array; mesh assembly reads past it. | Cross-check accessor geometry vs actual array length. |
| 21 | Empty / self-referential document → crash or hang | #110 (empty Collada crash/hang) | Syntactically-valid but empty doc (no `library_geometries`), or a `<node>`/`instance_node` self-reference cycle. | Empty scene or clean error; never hang / null-deref. |

### 3MF — ZIP + XML/OPC container; `D3MFImporter`

| # | Defect class | Citation | Reproducer recipe | Expected behavior |
|---|---|---|---|---|
| 22 | `<triangle>` references vertex index ≥ `<vertices>` count | #1128 (3MF import path); distinct from corpus `Ad111` | Inside `3D/3dmodel.model`, a `<triangle v1 v2 v3>` names an index ≥ number of `<vertex>` in the `<mesh>`. | Bounds-check triangle vertex refs; reject/repair. |
| 23 | Dangling / cross-part resource reference (build item, production ext) | #5811 (model-to-model refs), #5307 (`ValidateDS(aiTexture)` UAF after 3MF) | `<build><item objectid="K">` (or a `<component>` in another `.model`) references an id no `<object>` declares; or a resource freed on validation failure is re-accessed. | Resolve references before use; error on dangling; no access-after-free. |

### FBX — ASCII/binary; `FBXImporter`

| # | Defect class | Citation | Reproducer recipe | Expected behavior |
|---|---|---|---|---|
| 24 | Deeply nested `{ }` scopes → recursion stack overflow | #6501 (`Element`), #6588 (`Scope`), OSS-Fuzz 483106345 / 442253768 | Text FBX with unbounded nested scope blocks → unbounded recursion in Element/Scope construction. | Enforce a max nesting depth; reject beyond it. |
| 25 | `PolygonVertexIndex` / material index beyond its array | #6635 (`ConvertMeshMultiMaterial`); binary tokenizer crash #1638 | `PolygonVertexIndex` entry (after `~i = XOR(-1-i)` end-of-poly decode) ≥ control-point count, or a per-face material index ≥ material count. | Decode end-markers, then bounds-check against control points / material count. |

### STL — binary/ascii detection; `STLImporter` (distinct from geometry-defect `Me*`)

| # | Defect class | Citation | Reproducer recipe | Expected behavior |
|---|---|---|---|---|
| 26 | Binary triangle-count header vs file size mismatch / ambiguous ascii-vs-binary detect → preprocess OOB | #4304 (`ScenePreprocessor::ProcessMesh` via STL); encoding twin #6579 (`ConvertToUTF8`, OSS-Fuzz 493453713) | 4-byte binary triangle count disagrees with body length, or a file is ambiguously ascii/binary → mis-detected → OOB mesh reads. Encoding twin: ascii-STL whose tail is a truncated multibyte/BOM overruns `ConvertToUTF8`. | Reconcile triangle count against file size before alloc; bound transcoding to buffer length. |

**Cross-format lexer/encoding note** (applies to any text importer — OBJ/PLY/OFF/DAE/STL):
`BaseImporter::ConvertToUTF8` (#6027, #6579) and `GetNextLine`/`SkipSpacesAndLineEnd`
(#5860, #6016) over-read on truncated multibyte / BOM-at-EOF / missing-terminator
tails. Best expressed as **one shared class instantiated per format**, not 5 separate fixtures.

**Adjacent (STEP, for completeness — belongs in §12.11 `Ad*`, not the new bucket):**
STEP EXPRESS numeric-literal integer overflow — assimp#4622, OSS-Fuzz 44247
(`STEP::EXPRESS::DataType::Parse`). assimp's STEP path is independent of OCCT, so
this is a genuine cross-kernel corroboration of the corpus's existing STEP
literal-parsing classes (cf. Ad014/Ad049).

---

## Recurring cross-format themes (highest-value patterns to synthesize)

1. **Declared count > actual body data** — PLY #5729/#5341, OFF #6604/#2228, STL
   binary count #4304, OBJ #6571. *The single most common file-level defect.*
2. **Index references entity beyond its array** — COLLADA `<p>` #6522, glTF
   node/child #6485, glTF accessor-over-bufferView #6488, OBJ face #1047/#281,
   PLY face #5341, 3MF triangle #1128, FBX material #6635.
3. **Fixed-width read with insufficient backing bytes** — glTF 4×4 matrix #6612,
   glTF ExtractData #6488.
4. **Missing terminator / unbounded nesting → DoS** — OFF infinite loop #6604,
   FBX scope recursion #6501/#6588, OBJ timeout/OOM #6502/#6571.
5. **Unchecked NULL / uninitialized propagation** — glTF ExtractData NULL #6609,
   glTF LazyDict NULL #6611, COLLADA uninit #6531.
6. **Encoding / BOM edge cases** — ConvertToUTF8 #6579/#6027, PLY binary
   line-ending #5341.
7. **Invalid enum / type tag** — glTF componentType #6527, STEP EXPRESS #4622.

Expected behavior across all: reject with a diagnostic (or clamp/skip the bad
element) rather than crash, hang, over-allocate, or emit a null scene.

---

## Target category — a NEW bucket is needed

These are **file-level parser/container** defects for **non-STEP, non-mesh_builder**
formats. They fit nowhere clean today:

- **Not §12.14 `Me*`** — that section is geometry/topology defects emitted by
  `mesh_builder`, which only produces *structurally valid* files. A header-lie,
  count/row mismatch, out-of-range index, dangling reference, or truncated
  multibyte cannot be expressed by the builder; each needs a **raw hand-authored
  malformed file**.
- **Not §12.11 `Ad*`** — that is STEP/Part-21 parser robustness. Folding native
  glTF/PLY/OBJ/OFF/COLLADA/3MF/FBX/STL crashers into it would conflate two
  kernels and multiple file dialects. (The one STEP item here, #4622, *does*
  belong in `Ad*`.)

**Recommendation (maintainer decision):** open a new section, e.g.
**§12.15 "Import-format parser robustness"** with per-format tagging (or an
`Ip*` prefix), holding raw `.gltf/.glb/.ply/.obj/.off/.dae/.3mf/.fbx/.stl`
fixtures graded against assimp (secondarily tinygltf / RPly / lib3mf differentials).
This gives the corpus its first **glTF, COLLADA, 3MF, FBX** coverage and its first
genuine **container-format payload-index** class beyond the single `Ad111`
zip-bomb. Requires new fixture tooling (raw-file writers), not `mesh_builder` —
note as a BACKLOG item before ingest.
