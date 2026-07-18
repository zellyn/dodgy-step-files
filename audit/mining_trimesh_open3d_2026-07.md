# Mining trimesh + Open3D for file-level mesh/format defect classes (2026-07)

**Sources.** Two **independent, non-OCCT** mesh loaders:
- **trimesh** (Python), https://github.com/mikedh/trimesh — MIT. Ships an
  in-repo edge-case/broken-model corpus under `models/` that its test suite
  (`tests/test_obj.py`, `test_ply.py`, `test_stl.py`, `test_off.py`) drives
  through the loaders. Filenames are self-documenting: `negative_indices.obj`,
  `notenoughindices.obj`, `nancolor.obj`, `jacked.obj`, `wallhole.obj`,
  `face_in_group_name.obj`, `obj_with_no_face_in_chunk.obj`, `singlevn.obj`,
  `not_convex.obj`, `polygonfaces.obj`, `multibody.stl`, `soup.stl`,
  `busted.STL`, `two_objects_mixed_case_names.stl`, `comments.off`,
  `whitespace.off`, `points_emptyface.ply`, `points_ascii_with_lists.ply`,
  `no_indices_3storybuilding.glb`, `mode5.gltf`.
- **Open3D** (C++/Python), https://github.com/isl-org/Open3D — MIT. Uses
  **RPly** (independent PLY parser), tinyobjloader-style OBJ, and its own STL
  path. Issue tracker surfaces real parse-layer failures (RPly EOF, Rhino
  binary-PLY line endings, OBJ index disorder).

**License.** Both repos are MIT. We **describe patterns only** — no file bytes,
no repro attachments. trimesh's `models/` fixtures carry mixed provenance
(several CC / third-party). Every catalog fixture below would be **synthesized
from scratch** to embody the described construct; nothing is copied.

---

## Novelty context (checked against the live corpus + the assimp mining doc)

- §12.14 (`Me*`, 762 entries) is emitted by `mesh_builder.py` and is
  **geometry/topology defects on a structurally-valid file** (non-manifold,
  degenerate, self-intersection, holes, duplicates, orientation, non-finite
  *position*). It cannot express a header lie, a token-scan confusion, a
  channel-length underrun, a detection trap, or a container-structure defect.
- `audit/mining_assimp_2026-07.md` already established the **§12.15 `Ip*`**
  bucket (parse-layer / file-structure) and catalogued 26 classes. To avoid
  double-counting, every candidate below is graded against **both** the live
  `Me*`/`Ad*` sections **and** that assimp doc.
- Local grep confirms: no `concave n-gon fan-triangulation`, no `line
  continuation / backslash-EOL`, no `ascii-vs-binary STL detection`, no
  `multi-solid STL container`, no `non-finite color channel`, no `OBJ face-like
  substring` class anywhere in the catalog. (The catalog's many `backslash`
  hits are all STEP Part-21 *string-escape* directives — unrelated.)

---

## Candidate defect classes

Citations are `trimesh models/<file>` (+ the test that drives it) or
`open3d#NNNN` — **pattern reference only, no bytes**.

| # | Title / defect class | Source (pattern-only) | Format | Reproducer recipe (concrete) | Expected behavior | TARGET | Novelty | License |
|---|---|---|---|---|---|---|---|---|
| 1 | **OBJ face record with <3 vertex refs** | `notenoughindices.obj` (test_obj) | OBJ | A face statement supplies only two indices, e.g. `f 1 2` (or `f 1//1 2//2`), so the record cannot form a triangle. trimesh silently drops it (`assert len(m.faces)==1` after the bad face is discarded). | Reject or skip-with-diagnostic the under-specified face; never emit a 2-vertex "triangle" or index past the end. | §12.15 `Ip*` | **NEW** — assimp #5 was glTF LINE_LOOP<2 (a *line* primitive); an OBJ `f` line with <3 refs is a distinct format/record class. | MIT; synthesize |
| 2 | **OBJ backslash line-continuation across records** | `wallhole.obj` (test_obj; `assert m.faces.shape==(66,3)`) | OBJ | A `v`/`f` statement is split across physical lines with a trailing `\` continuation (`f 1 2 \`⏎`   3 4`). A line-oriented parser that ignores `\`-EOL mis-tokenizes both halves. | Join `\`-terminated physical lines before tokenizing; a naive splitter must not drop/mangle the record. | §12.15 `Ip*` | **NEW** — no line-continuation/lexical-join class in corpus or assimp doc. | MIT; synthesize |
| 3 | **OBJ face-like substring inside a name confuses a naive `f `-scanner** | `face_in_group_name.obj`, `obj_with_no_face_in_chunk.obj` (test_obj) | OBJ | A group/object/material/comment token contains text resembling face syntax, e.g. `g f 1 2 3` or `# f 1 2 3` or `usemtl f 1 2`. A parser that greps for the substring `"f "` (rather than tokenizing the leading keyword) invents phantom faces or miscounts. trimesh asserts the *correct* count (`len(m.vertices)==1`; `verts==3, faces==1`). | Dispatch on the first whitespace-delimited **token** only; substring matches inside names/comments must not be read as face data. | §12.15 `Ip*` | **NEW** — token-vs-substring lexical-context confusion; not in corpus or assimp doc. | MIT; synthesize |
| 4 | **OBJ attribute channel shorter than vertex count (vn/vt underrun)** | `singlevn.obj` (test_obj) | OBJ | File declares many `v` but only a single `vn` (or fewer `vt` than referenced), then `f a//1 b//1 c//1` reuses the one normal. A loader that indexes a per-vertex normal array by vertex id over-reads. | Bounds-check every `vn`/`vt` reference against the declared count of that channel; tolerate sparse normals without OOB. | §12.15 `Ip*` | **NEW** — assimp #9 was a glTF *UV accessor* short of vertices; the OBJ `vn`/`vt`-count-underrun is a distinct format/record class. | MIT; synthesize |
| 5 | **Non-finite (NaN/Inf) in a vertex COLOR / non-position channel** | `nancolor.obj` (test_obj) | OBJ (extended `v x y z r g b`) / PLY | A vertex line carries a finite position but a `NaN`/`Inf` in the trailing color triple (or a PLY `red/green/blue` scalar = NaN). The mesh geometry is fine; the *attribute* is poison and propagates into shading/averaging. | Detect and reject/clamp non-finite **attribute** values, not just coordinates. | §12.15 `Ip*` | **NEW** — `Me*` `non_finite_coordinate` covers only the *position*; a poisoned color/attribute channel on otherwise-valid geometry is unrepresented. | MIT; synthesize |
| 6 | **ASCII STL with multiple `solid…endsolid` bodies in one file** | `multibody.stl` (test_stl; `len(s.geometry)==2`, keys `{bodyA,bodyB}`) | STL (ASCII) | One file concatenates two `solid NAME … endsolid NAME` blocks. Spec-strict single-solid readers keep only the first body and silently drop the rest (or mis-nest on the second `solid`). | Treat the file as a scene of N named solids; never silently truncate to the first body. | §12.15 `Ip*` | **NEW** — first multi-body *container* class for a flat mesh format; not in corpus or assimp doc. | MIT; synthesize |
| 7 | **Binary STL whose 80-byte header begins with ASCII "solid" → mis-detected as ASCII** | `two_objects_mixed_case_names.stl`; STL detection folklore | STL (binary) | A binary STL's 80-byte header text starts with the word `solid` (some exporters write `solid <name>` into the header). Content-sniffers that key off a leading `solid` token mis-route the binary body to the ASCII parser → garbage / parse abort. Twin: mixed-case `SOLID`/`Solid` keyword defeats case-sensitive detection. | Detect binary-vs-ASCII by *structure* (file length vs `84 + 50·count`), not by a leading `solid` token; keyword match must be case-insensitive. | §12.15 `Ip*` | **NEW** — assimp #26 was binary *count-vs-filesize*; this is the distinct **"solid"-header detection trap**. | MIT; synthesize |
| 8 | **OFF header tokenization ambiguity (magic glued to counts / leading comments)** | `whitespace.off`, `comments.off` (test_off) | OFF | The magic and counts collapse onto one line (`OFF 8 12 0`), or the `OFF` token is glued to the first count (`OFF8 …`), or `#` comment lines precede the magic / sit on the count line. A parser expecting magic and counts on separate clean lines misreads V/F/E. | Tokenize the magic independently of the count triple; strip `#` comments anywhere; accept combined/whitespace-irregular headers. | §12.15 `Ip*` | **SUB-CASE** of assimp #18 (OFF header trust) but a distinct *lexical/tokenization* facet (glued magic, comment lines) worth its own fixture. | MIT; synthesize |
| 9 | **PLY element declared with count 0 alongside populated elements** | `points_emptyface.ply` (test_ply; PointCloud shape `(1024,3)`) | PLY | Header declares `element vertex 1024` **and** `element face 0`; the empty `face` block has zero body rows. Parsers that assume ≥1 row per declared element, or that require faces to build a mesh, mis-handle the legitimately-empty element. | Honor a declared count of 0 (skip the element cleanly); a point cloud with an empty face element is valid. | §12.15 `Ip*` | **NEW** (minor) — zero-count element edge; distinct from assimp #10 (count > rows). | MIT; synthesize |
| 10 | **OBJ vertex-reference disorder / forward reference** | open3d#5582 ("Vertex Index disorder when reading from obj file") | OBJ | A `f` statement references a vertex index that appears *later* in the file, or relies on 1-based/global ordering the loader resolves inconsistently → faces bound to the wrong vertices. Independent second loader (Open3D) reproduces disorder trimesh does not. | Resolve OBJ indices against the final 1-based global vertex table after a full pass; forward references are legal and must resolve. | §12.15 `Ip*` | **NEW** (ordering/resolution facet) — cross-loader differential; not the plain out-of-range case (assimp #13). | MIT; synthesize |
| 11 | **glTF primitive with no `indices` accessor / non-TRIANGLES mode** | `no_indices_3storybuilding.glb`, `mode5.gltf`, `Mesh_PrimitiveMode_04` (trimesh models) | glTF/GLB | A primitive omits `indices` (implicit sequential draw-array topology), and/or sets `mode` to TRIANGLE_STRIP(5)/FAN(6)/POINTS(0)/LINES(1). Loaders hard-wired to indexed TRIANGLES either read a null index accessor or mis-assemble strip/fan connectivity. | Reconstruct implicit topology per `mode`; a missing `indices` accessor means sequential vertices, not an error. | §12.15 `Ip*` | **SUB-CASE** of assimp #5 (which only covered LINE_LOOP<2); the *no-indices* + strip/fan-mode facet is new. | MIT; synthesize |
| 12 | **Concave n-gon face → naive fan triangulation emits out-of-polygon / overlapping triangles** | `not_convex.obj`, `polygonfaces.obj` (test_obj) | OBJ/PLY (n-gon faces) | A single `f a b c d e …` polygon face is **non-convex**. A loader that triangulates by a naive fan from the first vertex produces triangles that fall outside the polygon and overlap each other → self-intersecting/overlapping tessellation on an input the file author intended as one flat face. | Ear-clip / monotone-triangulate concave polygons; never assume convex fan validity. | §12.14 `Me*` | **NEW** — the resulting *geometry* (overlapping/self-intersecting triangles from concave-polygon tessellation) is a mesh defect distinct from `Me595` (hole-fill watsonInsert) and from soup-level self-intersection; would need `mesh_builder` polygon-face support (note as infra dependency). | MIT; synthesize |

---

## Corroboration / already-COVERED (independent-loader confirmation, NOT counted as novel)

These reproduce, in a **second independent kernel**, classes the assimp doc or
`Me*` already holds — valuable as cross-oracle corroboration, but not new:

- **PLY truncated body / header count > streamed rows** — open3d#7241 ("RPly:
  Unexpected end of file … number 16295"). COVERED by assimp #10; adds the
  **truncation** sub-facet (file ends mid-stream) and an independent RPly
  witness.
- **Binary PLY CR/LF line-ending after `end_header` shifts the binary body** —
  open3d#5091 (Rhino 6 exporter). COVERED by assimp #11; independent Open3D
  witness of the exact byte-alignment defect.
- **OBJ face index out of range / negative below `-(count)`** — trimesh
  `negative_indices.obj` is the *valid* relative-index baseline; the
  out-of-range variants are COVERED by assimp #13/#15.
- **STL polygon soup (no shared vertices)** — trimesh `soup.stl`. COVERED by
  `Me*` `polygon_soup_unindexed`.
- **Read-from-bytes "unknown format" (extension vs content sniffing)** —
  open3d#6913. Adjacent to trap #7; not a distinct geometry/structure defect.
- `busted.STL` / `jacked.obj` (trimesh) are known-broken fixtures whose exact
  defect the tests don't pin down structurally — flagged for later byte-level
  inspection, **not** claimed as a class here (accuracy over count).

---

## Target-bucket notes

- **11 of 12 novel candidates are §12.15 `Ip*`** (parse-layer / file-structure)
  and need the pending raw-file writer — same infra dependency the assimp doc
  already flagged as a BACKLOG item. They extend `Ip*` into OBJ lexical
  edge-cases (continuation, token-vs-substring, channel underrun), STL
  container/detection traps, and OFF/PLY/glTF header facets the assimp sweep
  did not reach.
- **1 candidate (#12) is §12.14 `Me*`** but needs `mesh_builder` to gain
  **polygon-face (n-gon) input** so it can emit the concave-fan tessellation;
  today the builder only takes triangles. Note as an infra sub-task before
  ingest.
