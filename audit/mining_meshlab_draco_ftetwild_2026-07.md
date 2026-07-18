# Mining MeshLab / Draco / fTetWild for file-level mesh + codec defect classes (2026-07)

**Sources (all independent of OCCT — kernel/codec diversity).**
- MeshLab + vcglib — https://github.com/cnr-isti-vclab/meshlab — GPL-3.0. An
  independent importer stack (its own PLY/OFF/OBJ readers via vcglib, plus a
  bundled glTF path). Several `confirmed`-labeled parser crashers.
- Draco — https://github.com/google/draco — **Apache-2.0**. Google's compressed
  mesh/point-cloud codec (`.drc`), OSS-Fuzz-integrated. A **container + entropy
  codec** attack surface the corpus has never exercised.
- fTetWild — https://github.com/wildmeshing/fTetWild — **MPL-2.0**. Volumetric
  tetrahedral mesher; a genuinely different *oracle* — it fails/silent-empties on
  specific structurally-valid-but-defective input STLs (many from Thingi10K).

**License / provenance discipline.** GPL-3.0 (MeshLab), Apache-2.0 (Draco),
MPL-2.0 (fTetWild). We **describe patterns only** — every fixture is synthesized
from scratch to embody the described construct. The base64 PoC in Draco #1169 and
the hexdump in #1162 are **reference-only; do NOT copy those bytes** — the `.drc`
fixtures must be re-generated with `draco_encoder` + a documented single-field
mutation, never harvested. No OSS-Fuzz corpus files are ingested.

---

## Novelty context (checked vs `STEP_PROBLEM_CATALOG.md`, 762 `Me*` entries)

- `grep` of the whole catalog: **`draco` / `.drc` / `Edgebreaker` / `rANS` /
  kd-tree-attribute-codec = 0 occurrences.** There is **no compressed-mesh /
  entropy-codec / bitstream** defect anywhere. §12.11 `Ad*` has exactly one
  container item (`Ad111` 3MF/IFCZIP **zip-bomb** — generic DEFLATE OOM), but
  nothing that drives allocation or over-reads from a *codec-internal* count.
- §12.14 `Me*` is emitted by `mesh_builder.py`, which only produces
  **structurally-valid** JSON meshes carrying geometry/topology defects. It
  cannot express a codec bitstream, a container header lie, or a parser OOB.
- The assimp mining pass (`mining_assimp_2026-07.md`) already staked out the
  §12.15 `Ip*` glTF/PLY/OBJ/OFF/COLLADA/3MF/FBX/STL **parser** surface. This pass
  is scoped to **(a) MeshLab differentials that are genuinely distinct from the
  assimp classes**, and **(b) an entirely new CODEC bucket (Draco) plus a new
  volumetric-oracle bucket (fTetWild)** that assimp does not touch.

**Conclusion.** Draco `.drc` is a brand-new **CONTAINER/CODEC** category (flagged
`new-codec` below). fTetWild contributes a new *oracle class* (volumetric
winding-number / CSG extraction) for §12.14. MeshLab contributes three §12.15
parser differentials distinct from the assimp set.

---

## Candidate defect classes (16 novel across 3 sources)

Citations: `draco#NNNN` = github.com/google/draco/issues, `ml#NNNN` =
cnr-isti-vclab/meshlab, `ftw#NN` = wildmeshing/fTetWild. **Pattern reference
only, no bytes.**

### Draco `.drc` — compressed mesh/point-cloud CODEC  → **new-codec sub-category**

| # | Defect class | Citation | Format | Reproducer recipe (synthesize, don't harvest) | Expected behavior | TARGET | Novelty |
|---|---|---|---|---|---|---|---|
| 1 | **Count-driven decompression bomb**: `num_faces` read from stream → `vector::reserve()` with no upper bound | draco#1169 (`MeshEdgebreakerDecoderImpl::DecodeConnectivity`, mesh_edgebreaker_decoder_impl.cc:380) | `.drc` | Encode a trivial mesh; mutate the connectivity-header `num_faces` varint to a huge value (a ~60-byte file implying multi-GB alloc). Body supplies almost no symbols. | Bound `num_faces` against remaining buffer size before reserve; graceful error. | new-codec (§12.15) | NEW — codec-internal count→alloc bomb; distinct from `Ad111` DEFLATE zip-bomb |
| 2 | **Entropy-decoder stack overflow**: rANS bit-decoder reads a size/prob prefix and writes a fixed LUT | draco#1102 (`RAnsBitDecoder::RAnsBitDecoder`, rans_bit_decoder.cc:23) | `.drc` | Mutate the rANS sub-stream length/probability byte so the decoder's stack LUT write runs past its fixed buffer. | Validate rANS prefix vs symbol table bound before writing. | new-codec (§12.15) | NEW — first entropy-coder / arithmetic-decoder class in corpus |
| 3 | **Truncated bitstream over-read**: `DecoderBuffer::Peek<u32>` past declared end | draco#1103 (decoder_buffer.h:89) | `.drc` | Header/section length claims N bytes of payload; file is truncated so a `Peek`/`Decode` reads past the buffer tail. | Every Peek/Decode must bounds-check against `remaining_size()`. | new-codec (§12.15) | NEW — codec-bitstream truncation (distinct from ASCII/text EOF over-reads in assimp set) |
| 4 | **Edgebreaker split-symbol OOB**: `ProcessSplitData()` indexes `split_data_` without validating size | draco#1162 / #1161 (edgebreaker_decoder_impl.cc:312) | `.drc` | Craft a connectivity symbol stream whose `S` (split) opcode references a split record that was never emitted → OOB index. | Validate split-record index against `split_data_.size()`. | new-codec (§12.15) | NEW — connectivity-symbol-stream semantics (Edgebreaker `CLERS`) |
| 5 | **Point-cloud kd-tree attribute decode SEGV**: level/point-count mismatch in portable-transform stage | draco#1105 (`KdTreeAttributesDecoder::DecodeDataNeededByPortableTransforms`, :453) | `.drc` (point cloud) | Point-cloud `.drc` whose kd-tree attribute header (num_points / dimensionality / level count) disagrees with the encoded attribute payload. | Cross-check attribute geometry vs point count before decode. | new-codec (§12.15) | NEW — point-cloud codec path; corpus has zero PC-compression coverage |
| 6 | **Attribute count = INT_MAX → buffer overflow** on mesh-attribute decompress | draco#1172 (root-cause w/ PR#1166) | `.drc` | Mutate an attribute's `num_components`/count field to `INT_MAX`; decode multiplies count×component-size → overflow → undersized alloc, overrun write. | Reject implausible attribute counts; use checked multiply. | new-codec (§12.15) | NEW — integer-overflow in codec size math |
| 7 | **Sequential-integer attribute decoder OOB** on crafted connectivity bit pattern | draco#1202 (`SequentialIntegerAttributeDecoder::DecodeIntegerValues`) | `.drc` | Byte pattern in the integer-attribute section (upstream cite: `0xFF 0x00 0xFF` region) drives an out-of-range read in the integer decoder. | Bounds-check decoded run/length before consuming. | new-codec (§12.15) | NEW — integer-attribute codec layer |
| 8 | **Empty-mesh decoder segfault**: syntactically-valid header, zero faces/points | draco#1171 | `.drc` | Encode header for a mesh with 0 faces (or 0 points) and no attribute payload; decoder dereferences an unpopulated attribute/connectivity object. | Handle the empty-geometry case → empty scene, not null-deref. | new-codec (§12.15) | NEW — codec zero-geometry edge case |

### MeshLab / vcglib — independent parser differentials (distinct from the assimp set)

| # | Defect class | Citation | Format | Reproducer recipe | Expected behavior | TARGET | Novelty |
|---|---|---|---|---|---|---|---|
| 9 | **OFF single n-gon face** (k=7 polygon, *well-formed*, counts correct) crashes fan-triangulation | ml#1163 (`confirmed`) | `.off` | Valid OFF `8 1 0`, 8 verts, one face `7 4 6 0 2 3 1 5` (a 7-gon). vcglib's polygon→triangle fan mishandles n>4. Cross-oracle: assimp/others load it. | Fan-triangulate arbitrary convex/concave n-gons or reject with diagnostic; never crash. | §12.15 (`Ip*`) | NEW vs assimp OFF #2228 (that was header-count *mismatch*; this is a **correct** n-gon) |
| 10 | **PLY custom per-vertex LIST property** (unknown list field) crashes loader — regression from silent-ignore | ml#1624 | `.ply` | A PLY point cloud with a `property list uchar int <name>` per vertex holding an index list MeshLab doesn't recognize. Formerly ignored; now over-reads/crashes. | Skip unknown list properties by consuming their declared count; never assume scalar width. | §12.15 (`Ip*`) | NEW vs assimp PLY #5729 (that was declared-count > body rows / extra *scalar*; this is a **list-typed** custom property) |
| 11 | **glTF/GLB POINTS-mode primitive** routed through triangle assembler → templated index-decode SEGV | ml#1387 (`confirmed`), ml#1484 | `.glb`/`.gltf` | A glTF whose primitive `mode` = 0 (POINTS) — a point cloud, no indices — fed to `populateTriangles<T>()` which assumes triangle connectivity. | Branch on primitive mode; handle POINTS/LINES before triangle assembly. | §12.15 (`Ip*`) | NEW vs assimp glTF #6634 (that was LINE_LOOP < 2 indices; this is **POINTS** point-cloud mode) |

### fTetWild — volumetric mesher as a NEW oracle for structurally-valid-but-defective STL

These files are **structurally valid** (fit the §12.14 model), but the defect is
only *revealed by a volumetric winding-number / CSG extractor* — an oracle
class no existing `Me*` fixture is graded against (current orientation/hole
fixtures grade against *surface* healers CGAL-PMP / MeshFix).

| # | Defect class | Citation | Format | Reproducer recipe | Expected behavior | TARGET | Novelty |
|---|---|---|---|---|---|---|---|
| 12 | **Inconsistent triangle orientation → winding-number filter drops the volume** (near-empty tet output) | fTetWild paper §heuristic-winding + repo (flood-fill fallback) | STL/mesh | Closed surface whose triangles have mixed CW/CCW winding; the heuristic winding-number volume-extraction classifies interior as exterior → outputs ~0 tets. Flood-fill would recover it. | Robust interior extraction independent of per-triangle winding, or diagnose the orientation inconsistency. | §12.14 | NEW oracle behavior — orientation defect graded on a **volumetric** extractor, not a surface healer |
| 13 | **Non-watertight / open input → CSG/boolean returns zero cells** (silent-empty volume) | ftw#37 (`--csg` returns no elements) | STL + CSG | An `.stl` operand of a CSG `join`/`intersection` that is open (boundary holes) → winding number ill-defined → 0 output cells, no error. | Detect non-watertight CSG operands; error rather than emit an empty volume. | §12.14 | NEW — silent-empty at the **volumetric-boolean** stage (corpus silent-empty is all surface/BRep) |
| 14 | **Multi-material stack sharing an interior face → non-manifold *interior* face** mishandled | ftw#69 | multi-STL / tagged | Stacked solids ("hamburger" of N materials) sharing internal separating surfaces; the shared interior faces form non-manifold *volume* interfaces the extractor mis-labels. | Support conformal interior interfaces; tag tets per region correctly. | §12.14 | NEW — non-manifold **interior/volume** face; existing Me001 is a non-manifold *surface edge* |
| 15 | **Tangent / touching solids** (cube ∪ cylinder meeting at a single contact) → degenerate conformal interface | ftw#64 | multi-STL | Two solids that *touch* (coincident contact patch / tangent line) rather than overlap; the union has a measure-zero contact → degenerate non-manifold interface. | Produce a conformal mesh distinguishing the two volumes, or diagnose the zero-measure contact. | §12.14 | NEW — coincident-solid contact degeneracy at a volume interface |
| 16 | **Many-component preprocessing swap segfault** (robustness / component-count blowup) | ftw#75 (segfault in preprocessing "swapping") | STL | Input aggregating a large number (~hundreds) of separate closed surfaces triggers a crash in the edge-swap preprocessing stage. | Bound/guard preprocessing against pathological component counts. | §12.14 | NEW — volumetric-preprocessing robustness (weaker: no minimal upstream repro) |

---

## Cross-oracle corroboration (NOT counted as new — strengthens an existing candidate)

- **Draco OBJ front-end accepts `vt`/`vn`/`v` face indices beyond declared count**
  — draco#1194 (`PointAttribute::DeduplicateFormattedValues`, OOB read). This is
  the **same class** as assimp OBJ #1047 / #755 (attribute-index-out-of-range),
  now reproduced on a *third independent* OBJ reader (Draco's). Use as a
  differential-oracle note on that assimp candidate — Draco reads it, over-reads;
  a good multi-reader disagreement signal — not a new fixture.

---

## Recurring themes (highest-value to synthesize first)

1. **Codec-internal count/size field drives allocation or copy without a buffer
   bound** — Draco #1169 (num_faces), #1172 (attr count), #6-analogues. *The
   single strongest new class; the corpus has none.*
2. **Truncated / crafted bitstream over-reads the decode buffer** — Draco #1103,
   #1162, #1202. Distinct from ASCII EOF over-reads because it's a *binary
   entropy-coded* stream (no line/token structure to anchor on).
3. **Structurally-valid geometry that only a volumetric oracle rejects** —
   fTetWild #12/#13 (winding-number / CSG silent-empty). New *oracle*, not a new
   file malformation.
4. **Independent parser disagreement on a well-formed edge case** — MeshLab
   n-gon OFF #9, glTF POINTS #11: the file is valid; one reader crashes, another
   loads. Differential-tolerance signal.

Expected behavior across all: reject with a diagnostic (or clamp/skip) rather
than crash, hang, over-allocate, or silently emit an empty result.

---

## Target-bucket summary

- **8 new-codec (Draco `.drc`)** → **flag: warrants its own sub-category** under
  §12.15, e.g. `Ip*` with a `codec/draco` sub-class, OR a dedicated container/codec
  band. These need a **`.drc` writer** (invoke `draco_encoder` on a trivial mesh,
  then apply one documented byte/field mutation) — genuinely new tooling, heavier
  than the raw-text `Ip*` writer the assimp pass proposed. **BACKLOG.**
- **3 §12.15 `Ip*`** (MeshLab OFF n-gon, PLY list-property, glTF POINTS) — raw
  hand-authored files; same tooling as the assimp `Ip*` proposal.
- **5 §12.14** (fTetWild winding/CSG/interior-nonmanifold/touching/robustness) —
  fit `mesh_builder`'s structurally-valid model, but require **grading against a
  volumetric oracle** (tetrahedralizer) the mesh harness does not yet call. The
  *fixtures* are cheap; the *oracle wiring* is the BACKLOG item.

No git commit performed (mining artifact stays local per push policy).
