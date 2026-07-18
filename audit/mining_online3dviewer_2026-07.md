# Mining — Online3DViewer + occt-import-js (kovacsv) — 2026-07

**Source repos.** `kovacsv/Online3DViewer` (MIT; app at 3dviewer.net) delegates STEP
import to `kovacsv/occt-import-js` (LGPL-2.1, bundles OCCT ~7.7 compiled to WASM via
Emscripten) and renders through three.js. STEP is therefore **OCCT-correlated** — most
STEP behaviour corroborates the existing OCCT mine — but the WASM sandbox, the
single-precision three.js output buffer, and non-developer reporters who bring their own
"opens in CAD Assistant / empty here" files surface a distinct **cross-oracle** seam:
double-vs-single precision, native-vs-wasm32, desktop-vs-mobile, and OCCT-version
regressions. Those differentials are the yield; they belong in §12.12 `Xp*`.

**License posture.** We copy no bytes. All reporter-attached STEP files are third-party
user uploads (not covered by either repo's license); repo code (occt-import-js = LGPL) is
irrelevant because fixtures are synthesized from the *described pattern*, never derived from
occt-import-js source. Every row below is pattern-only synthesis.

---

## Candidate table

| # | Title / defect-class | Source URL (pattern-only) | Reproducer recipe (concrete) | Expected behavior | Target section | Novelty | License |
|---|---|---|---|---|---|---|---|
| 1 | **Conical face silently dropped by OCCT 7.7.x mesher but present in ≤7.6.1 / desktop CAD** (kernel-*version* differential, not a bad file) | occt-import-js #42 "Surfaces are occasionally missed" → OCCT tracker 33681 | One `MANIFOLD_SOLID_BREP` whose faces include exactly one `ADVANCED_FACE` on a `CONICAL_SURFACE` (semi-angle ~20°, finite frustum bounded by two `CIRCLE` edges); the rest planar/cylindrical. File is fully valid and watertight. On an OCCT-7.7.x mesher the conical `ADVANCED_FACE` yields zero triangles (`BRepMesh` regression) → the solid renders with a hole; OCCT 7.6.1, CAD Assistant, and other CAD show all faces. | Mesh every face of a valid solid; a face that produces zero triangles is a mesher defect, not an input defect — the receiver must not silently emit a solid missing a face. Cross-oracle note: the *same bytes* are complete in one kernel version and defective in the next. | **§12.12 `Xp*`** (kernel-version × conical-face tessellation differential) | **NEW** — no version-divergence differential exists in the catalog; nearest neighbours (Gd*/Gn014 conical-canonical, Pf021 near-apex healing) are input-geometry defects, not a version-differential silent face drop | pattern-only; user file not ingested |
| 2 | **wasm32 address-space silent-empty: valid large STEP reads natively but the Emscripten/WASM build returns all-empty arrays** | occt-import-js #19 "STP > 100MB not supported"; O3DV #527, #453 "Very Large Import" | A structurally valid AP203/AP214 solid assembly whose *tessellated* footprint (many `SURFACE_OF_LINEAR_EXTRUSION` / high-facet faces) drives peak in-memory allocation past the wasm32 ~2–4 GB linear-memory ceiling during triangulation. Native OCCT reads it; the WASM build returns `meshes:[]` / empty position+index arrays with **no error**. (Fixture: synthesize a scaled-down analog that documents the class; the byte-cap itself is runtime-dependent.) | Reader must distinguish "parsed, zero geometry" from "ran out of address space" and raise a diagnostic (`E_OUT_OF_MEMORY` / partial-load warning); silently returning an empty model is the defect. | **§12.12 `Xp*`** (native-vs-wasm32 runtime differential) — cross-ref §12.10 file-size/OOM | **NEW** — §12.10 has native OOM (unbounded alloc, 440 MB O(n²)) and §12.11 has decompression bombs, but none captures the *wasm32 32-bit-address-space* differential where the same valid file is fine natively and silent-empty in WASM | pattern-only |
| 2b | **Mobile-Safari WASM heap crash: same assembly loads on desktop/Android/macOS, hard-crashes iOS Safari** | O3DV #443 "Crash web on mobile web (iOS) when upload this .step" | A valid multi-body STEP assembly whose triangulated buffers + WASM heap exceed iOS WKWebView's lower per-tab memory cap. Loads on Chrome/desktop Safari/Android; iOS Safari tab crashes (no error dialog). | Bound working-set / stream tessellation; detect the platform memory cap and fail gracefully with a diagnostic rather than crashing the tab. | **§12.12 `Xp*`** (platform/runtime memory-cap differential) — cross-ref §12.11 DoS | **SUB-CASE of #2** — same wasm32-heap root cause, platform-differential surface | pattern-only; user file not ingested |
| 3 | **Far-from-origin model → single-precision (float32) three.js buffer collapses all vertex positions to 0** | occt-import-js #37 / O3DV #467 "model doesn't contain any meshes … all positions are 0" (opens in CAD Assistant) | A valid solid placed via an `AXIS2_PLACEMENT_3D` a very large distance from the origin (e.g. location ~1e7–1e8 mm, GIS/absolute-coordinate style) while its own extent is ~10 mm. Double-precision readers (CAD Assistant) render it correctly; a reader that emits a **float32** vertex buffer loses all local relief and the geometry collapses to (near-)zero / degenerate positions. | Recentre far-from-origin geometry to a local frame before down-converting to single precision, or warn that float32 output cannot represent the model at its absolute coordinates; emitting an all-zero mesh without diagnostic is the defect. | **§12.12 `Xp*`** (double-vs-single-precision output differential) | **NEW SUB-CASE** — distinct from Tb013 (far-from-origin *double*-precision ULP-vs-tolerance) and Tb010 (float32 round-trip masks self-intersection); this is the *output-buffer* precision collapse in a WASM/glTF/three.js pipeline. Mechanism partly inferred (could co-occur with #2 size) — flag medium-confidence | pattern-only |
| 4 | **Pure `TESSELLATED_SOLID` representation throws in a BRep-only reader while exact-geometry export / other OCCT builds load** | occt-import-js #39 "Loading issues using tessellated geometries" (CATIA "tessellated" export mode; pythonocc-core 7.8 compared) | A CATIA-style AP242 file whose shape is carried purely as `TESSELLATED_SOLID` + `TESSELLATED_SHAPE_REPRESENTATION` + `COORDINATES_LIST` (no `ADVANCED_FACE` BRep). occt-import-js throws a WASM exception ("failed to import"); the exact-geometry export of the same part, and pythonocc 7.8, load it. | Readers advertising STEP support must handle `tessellated_*` items (or degrade to warn-and-skip), not throw an uncaught exception. Cross-oracle: reader-support gap between two OCCT builds. | **§12.12 `Xp*`** (tessellated-representation reader-support differential) | **SUB-CASE / CORROBORATES** M002 + Os/Tessellated class (line ~8976 `tessellated_solid` no `styled_item`); adds the *reader-differential exception* angle | pattern-only |
| 5 | **`COLOUR_RGB` mis-decoded through wrong colour-space (sRGB↔linear) on READ** | occt-import-js #64 (fix: read with `Quantity_TOC_sRGB`) | `#n=COLOUR_RGB('x',0.576,0.863,0.361);` on a `STYLED_ITEM`; reader applies a linear→sRGB (or the inverse) conversion, so displayed colour is rgb(0.29,0.72,0.11) instead of the authored value — a visible hue shift, not a rounding error. | Treat Part-21 `COLOUR_RGB` components as already in the file's stated colour space; do not silently re-gamma on import. | §12.12 `Xp*` (colour-space × reader) | **CORROBORATES** Xp034 / Xp035 (sRGB↔linear colour) — reader-side variant of the writer-side entries already catalogued | pattern-only |
| 6 | **Assembly-scope colour loss: `STYLED_ITEM` colours present per-part but dropped when the full assembly is loaded** | O3DV #512 "Color is lost after STEP loaded … split part imports with colour"; occt-import-js #23 (colours visible in Creo/OCC sample, `face_colors` undefined here) | A two-level assembly whose leaf-component colours are bound via per-instance `STYLED_ITEM` reached through `MAPPED_ITEM` / `REPRESENTATION_RELATIONSHIP`; XCAF colour propagation drops them under assembly nesting, so the whole-file load is uncoloured while an isolated component (no mapping level) keeps its colour. | Propagate presentation styles across `mapped_item` / representation-relationship boundaries; colour must not depend on whether the component is loaded standalone or nested. | §12.12 `Xp*` (colour × assembly nesting × reader) | **CORROBORATES** A018 ("STYLED_ITEM at wrong scope … nested compound flatten drops inner STYLED_ITEM") + Gs (line ~3175 nested-flatten colour loss) | pattern-only |

---

## Discarded / non-file-level (audited, not catalogued)

- **occt-import-js #63** ("watermark"/moiré patch on a simple box) — reporter's own follow-up: three.js **shadow-acne** rendering artifact, *not* a file or reader defect. Discard.
- **O3DV #367** ("no meshes" when WebWorkers unavailable) — environment/config, no file trigger. Discard.
- **occt-import-js #40** (0.0.22 broken vs 0.0.12) — build-regression, no file detail. Discard.
- **O3DV #536** ("Failed to Import Invalid Vertex", OBJ+MTL) — mesh-format (OBJ), not STEP; likely NaN/blank vertex — belongs to any future OBJ mining, not this pass.
- **occt-import-js #54** (GAS.stp "geometry broken") — real but under-specified; no isolable entity pattern → not actionable as a synthesizable class.

---

## Honest yield

Six catalogue-worthy rows: **3 NEW** classes (#1, #2, #3) — one of which (#2) carries a
platform sub-case (#2b) — plus **1 reader-support sub-case** (#4) and **2 corroborating**
rows (#5 → Xp034/035, #6 → A018). All six are cross-oracle by construction, which is the
point of mining viewers: the novelty is not in the STEP bytes (OCCT-correlated) but in the
*differentials the sandbox exposes* — kernel-version, native-vs-wasm32, double-vs-float32,
desktop-vs-mobile, and reader-support gaps. Five further tickets were audited and discarded
as non-file-level or under-specified. This vein is now largely characterised; remaining open
tickets skew to feature requests, build/TypeScript, and OCCT-corroborating STEP behaviour.
