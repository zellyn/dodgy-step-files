# NEW Source Survey — Malformed CAD/Mesh Input Reports (2026-07)

**Purpose.** Discover *fresh, mineable* sources of "problematic CAD input" defect
reports to expand the corpus, **beyond** what `STEP_PROBLEM_POTENTIAL_SOURCES.md`
already tracks. Method: web research (WebSearch/WebFetch) plus three parallel
research agents, verifying (a) 2025-2026 maintenance status, (b) issue-tracker URL,
(c) forum/community URL, (d) 1-2 concrete malformed-input bug examples, (e) mining
promise. We never copy files/bytes — we synthesize reproducers from the *pattern*.

**Already-mined (DONE — not re-surveyed here):** OCCT issues + Mantis + git log +
`tests/`, CAx-IF / MBx-IF recommended practices, FreeCAD (issues+forum), IfcOpenShell
`step-file-parser`, STEPcode, pythonocc-core, CadQuery/build123d, SolveSpace, KiCad,
gmsh (OCC healing flags), Salome/Netgen, CGAL PMP, MeshFix, commercial-translator KBs
(HOOPS Exchange, CADfix, CAD Exchanger, Capvidia, Datakit, Spatial), vendor community
forums (Autodesk/SolidWorks/Onshape/PTC/Siemens — *general*), NIST SFA + PMI suite,
ABC / Fusion360 Gallery / Thingi10K / DeepCAD datasets, OSS-Fuzz (STEP angle), CVE/Talos.

**Headline finding.** The STEP/OCCT/commercial/standards side is close to saturated.
The genuinely un-tapped frontier is four-fold:
1. **Mesh-library issue trackers as *input-bug* sources** (not just heal-function taxonomies) — especially the OSS-Fuzz-integrated ones (assimp, Draco).
2. **OCCT-wrapping JS/WASM importers + slicer STEP importers** — huge volume of *user-uploaded breaking files* with attachments and cross-oracle ("opens in X, empty in Y") signal.
3. **Independent (non-OCCT) STEP parsers** in Rust/Python/C# — the highest *kernel-diversity* novelty; their trackers + TODO lists enumerate unhandled Part-21/AP cases.
4. **The IFC/buildingSMART Gherkin validation-rule corpus + MBx-IF license-clean test files** — a maintained, executable taxonomy of malformed-input classes and a license-clean fixture seam.

---

## Landscape table

Promise = expected yield of *file-level* malformed-input reports (a static fixture can
reproduce it). Low often means the tracker skews to API/build/threading bugs.

| Software / library | Maintained (2025-26)? | Kernel / how it reads input | Issue tracker | Forum / community | Promise | Notes |
|---|---|---|---|---|---|---|
| **assimp** | Yes, very active (6.0.x) | Own C++ importers (STEP path independent of OCCT; shares IFC reader) | https://github.com/assimp/assimp/issues | https://github.com/orgs/assimp/discussions | **HIGH** | **Top overall.** Heavily OSS-Fuzz'd (`assimp_fuzzer`); most crashers ship a minimal static reproducer. Also STEP mis-dispatch + `automotive_design` schema rejection (#3800) + silent NULL scene (#6343). |
| **ruststep** | Partial (0.3.0 Jun 2024, tracker live to 2026) | Independent Rust `nom` Part-21 parser + `espr` EXPRESS codegen | https://github.com/ricosjp/ruststep/issues | GitHub only | **HIGH** | Best *kernel-diversity* Part-21 source. #252 `DATA;` tokenizer fail on Plasticity/HOOPS AP203 (file attached); #256 empty param list `()`; #243/#181 literal/string tokenization. Files tagged with source CAD tool = ideal provenance. |
| **trimesh** | Yes, very active (5.0.0rc) | Own loaders (mesh) | https://github.com/mikedh/trimesh/issues | GitHub issues | **HIGH** | Built to load messy real-world files. #95 empty ASCII STL < 84 B crashes binary loader; #239 `vt` < `v` OBJ. Ships in-repo `models/` corpus of broken/edge-case files. |
| **Open3D** | Yes, very active (v0.19, Intel ISL) | Own loaders (RPly/OBJ) | https://github.com/isl-org/Open3D/issues | https://github.com/isl-org/Open3D/discussions | **HIGH** | RPly parser: many "this exact PLY fails to read" reports. #4517 "polygon could not be decomposed into triangles"; #1302 truncated face data. (Do NOT conflate with "o3de" game engine.) |
| **MeshLab + vcglib** | Yes, active (2025.07) | vcg importers | https://github.com/cnr-isti-vclab/meshlab/issues · /vcglib/issues | SO tag `meshlab`, /discussions | **HIGH** | Parser-level crashers: #1112 `stack smashing detected` on malformed PLY; #391 OBJ open-fail + STL crash. Filter label `confirmed` + attached file. Fixes land in vcglib. |
| **Online3DViewer** | Yes, very active | Delegates STEP → occt-import-js, renders three.js | https://github.com/kovacsv/Online3DViewer/issues | app: 3dviewer.net | **HIGH** | Non-devs upload real breaking STEP. #467 imports to empty result; #512 color/XCAF lost. Cross-tool signal, good attachments. (OCCT-reader behavior → partly corroborates OCCT mine.) |
| **occt-import-js** | Yes, low cadence (bundles OCCT 7.7) | Emscripten/WASM OCCT wrapper | https://github.com/kovacsv/occt-import-js/issues | GitHub only | **HIGH** | #54 broken geometry on attached `GAS.stp`; #37 STEP opens in CAD Assistant but 0 meshes (silent-empty). Reporters attach the offending STEP. |
| **PrusaSlicer** | Yes, very active (2.9.x) | Native STEP via OCCT → mesh → open-edge/manifold check | https://github.com/prusa3d/PrusaSlicer/issues | https://forum.prusa3d.com | **HIGH** | #11305 stack overflow on **malformed STEP** (fuzz-grade repro); #8998 STEP → 127 open edges absent from STL of same part; #14395 wrong only on OCCT 7.8.x (kernel-version divergence); #13892 curved surfaces faceted/degenerate. |
| **OrcaSlicer** | Yes, very active (2.3.x) | Native STEP via OCCT | https://github.com/OrcaSlicer/OrcaSlicer/issues | /discussions | **HIGH** | High-volume STEP tickets w/ attachments. #6441 spheres dropped from Onshape STEP; #7578 bad face orientation renders cut-sphere solid; #12366 STEP → no geometry (2026). |
| **lib3mf** | Yes, very active (v2.5.0 Feb 2026) | Own 3MF (ZIP+XML/OPC) reader | https://github.com/3MFConsortium/lib3mf/issues | 3mf.io; downstream slicer forums | **HIGH** | 3MF = ZIP+XML container → broad malformed surface. TALOS-2020-1226 use-after-free from crafted .3mf; #7 valid samples rejected as bad ZIP; #307 UTF16 exception. Crash + interop classes. |
| **buildingSMART Validation Service + ifc-gherkin-rules** | Yes, very active | Gherkin rules over IfcOpenShell | https://github.com/buildingSMART/ifc-gherkin-rules · /validate/issues | https://validate.buildingsmart.org | **HIGH** (taxonomy) | Executable, maintained taxonomy of malformed-IFC classes (geometry subcontexts GEM*, units, placement, alignment). Analogous to mining ShapeFix class-names but for IFC/AP242-adjacent. IfcOpenShell #5098 shows rule-vs-practice tension. |
| **Assimp STEP path** (as above) | — | — | — | — | HIGH | Called out separately: behavioral mishandling (wrong-importer dispatch #3791, schema rejection #3800) is a distinct class from parser crashes. |
| **fTetWild** | Yes, moderate | Tetra-meshing; eats triangle-soup / non-watertight | https://github.com/wildmeshing/fTetWild/issues | GitHub | **MED-HIGH** | Designed to ingest self-intersecting / non-manifold input. #75 segfault in preprocessing; #82 Thingi10K `96773_sf.stl` blows up — named STLs map to a public dataset. |
| **Draco** | Yes, slowing (v1.5.7) | Own `.drc` codec | https://github.com/google/draco/issues | Khronos/glTF forums | **MED-HIGH** | **On OSS-Fuzz** → minimal `.drc` crashers (#1096, Feb 2025). #356 encoder segfault on degenerate/dup-vertex; #1013 undecodable sequential `.drc`. Self-contained bad files. |
| **CAD Assistant** (OCCT viewer) | Yes (closed) | Native OCCT XCAF | (no GH) → https://dev.opencascade.org | OCCT forum | **MED-HIGH** | File-centric, cross-oracle (imports half-sphere; invalid glTF from STEP). Overlaps already-mined OCCT forum — treat as OCCT-forum sub-mine. |
| **Manifold** | Yes, very active | Own mesh boolean kernel | https://github.com/elalish/manifold/issues | /discussions | **MED** | Rejects non-manifold by design → few "broken import" repros, but a solid **degenerate-yet-manifold** vein: #1491 UAF in QuickHull on degenerate Revolve; #1283 union → 968 zero-area tris + NaN. In-repo FuzzTest (`MANIFOLD_FUZZ`). |
| **VTK** | Yes, very active (Kitware, 9.x) | Own polydata filters | https://gitlab.kitware.com/vtk/vtk/-/issues | https://discourse.vtk.org (very active) | **MED** | Degenerate/dup-point/non-manifold polydata mishandled by `vtkCleanPolyData`/`vtkFillHolesFilter` (#17320, MR!4874). Often wrong-output w/ code repro, not attached file. Mine Discourse too. |
| **opencascade.js** | Semi-dormant (2.0 beta) | Full OCCT → WASM, raw API | https://github.com/donalffons/opencascade.js/issues | /discussions | **MED** | Skews API/build. Failures surface as OCCT return codes. Targeted skim only. |
| **Foxtrot** (Formlabs) | Marginal / PoC (to Feb 2026) | Independent Rust `nom` EXPRESS parser + own triangulation | https://github.com/Formlabs/foxtrot/issues | GitHub | **MED** | #21 wrong STEP→STL tessellation; #10 "unreachable executed" on unhandled case. Implements ~26 entity types vs ~915 in AP214 — TODO list = defect list. |
| **steputils** (mozman) | Dormant (~2021) | Independent Python lexer → STEP DOM | https://github.com/mozman/steputils/issues | GitHub | **MED** | #1 `invalid character in string` on Rhino/Creo files (ISO-8859-1 in string literals; fixed PR#3). One high-quality named-source encoding defect. |
| **TetGen** | Semi-active (v1.6.0 May 2025) | Tetra-meshing | https://codeberg.org/TetGen/TetGen/issues | — | **MED** (via wrappers) | Own tracker bare; real bad-input reports live downstream (libigl #684 non-closed surface, GIBBON #52). |
| **TetWild** (orig) | Deprecated → fTetWild | Tetra-meshing | https://github.com/Yixin-Hu/TetWild/issues | — | **MED** | #67 segfault on `--input test.stl`; #41 non-manifold output. Files rarely attached. |
| **admesh** | Maintenance-mode (v0.98.4 2022) | Purpose-built STL repair | https://github.com/admesh/admesh/issues | — | **MED** | #25 heap overflow from malformed STL; #29 infinite hang on specific STL. `stlinit.c`/`stl_io.c` a natural target. Low volume. |
| **pyiges** (pyvista) | Yes | Own IGES parser | https://github.com/pyvista/pyiges/issues | GitHub | **MED** | #15 Creo cylindrical features fail; #42 500 MB hang. Rare IGES-native (non-OCCT) source. |
| **libigl** | Yes, active (2.6.x) | Thin OBJ/OFF/MESH loaders | https://github.com/libigl/libigl/issues | https://libigl.github.io/faq/ | **MED** | Degeneracy reports often mid-pipeline output, not static bad file. #1078 dup-vertex → zero-area faces → NaN; #1033 OBJ load crash. |
| **cascadio** (trimesh) | Yes | nanobind OCCT wrapper (STEP→GLB) | https://github.com/trimesh/cascadio/issues | via trimesh | **LOW-MED** | Very low volume; useful as a *second* OCCT-binding cross-check. STEP bugs often land in trimesh/trimesh. |
| **Bambu Studio** | Yes, noisy triage | Native STEP via OCCT | https://github.com/bambulab/BambuStudio/issues | https://forum.bambulab.com | **MED-HIGH** | #5208 crash on STEP (unhandled OCCT exception); #6079 hang/crash. Good crash stream diluted by hardware/UI noise. |
| **OpenVSP** (NASA) | Yes, active | OCCT-based STEP/IGES export | https://github.com/OpenVSP/OpenVSP/issues | https://groups.google.com/g/openvsp | **MED** | *Producer* of pathological STEP: thin blunt trailing edges → degenerate patches → crash; #155 segfault exporting default-wing STEP. Source of realistic degenerate-geometry recipes. |
| **chili3d** | Yes, new/active | OCCT 7.9.1 via WASM | https://github.com/xiangechen/chili3d/issues | GitHub | **MED** | New web CAD with its own STEP/IGES import bug stream; young tracker. |
| **PyMesh** | Semi-dormant (~2024) | Own loaders | https://github.com/PyMesh/PyMesh/issues | — | **LOW-MED** | #74 >3-vertex OBJ faces; #351 STL AttributeError. Ships `fix_mesh.py` (domain signal); issues skew build/API. |
| **Instant Meshes** | Dormant (last 2019) | Own | https://github.com/wjakob/instant-meshes/issues | — | **MED-LOW** | #48 point-cloud silent-empty; #140 non-manifold PLY hangs at "Coloring.." (file). Repro files on bit-rot Google Drive links. |
| **Cura** | Yes (5.x) | STL/3MF/OBJ only — NO STEP | https://github.com/Ultimaker/Cura/issues | https://community.ultimaker.com | **MED** (mesh) | #15351 manifold false-positive on watertight CAD mesh; #16779 inch→mm scale. STEP feature repeatedly declined (#19007). |
| **OpenMesh** | Yes, slow/academic | Own OBJ/OFF | GitLab (login-gated) | mailing list | **LOW** | Tracker not web-crawlable; few file-level reports. Better as a strict *reader to run against* corpus than a report source. |
| **truck** (Rust kernel) | Very active (to Jul 2026) | STEP via `truck-stepio` → ruststep | https://github.com/ricosjp/truck/issues | GitHub | **LOW-MED** | Parser defects surface upstream in ruststep; kernel/geometry issues dominate here. |
| **IxMilia.Step** (C#) | Low/experimental | Independent .NET Part-21 | https://github.com/ixmilia/step/issues | — | **LOW** | #3 parameterized file schemas unhandled. |
| **StepParser** (MinimalWindowsDev, C#) | New/minimal | Independent, claims ~600 entity types + AP242:2025 | https://github.com/MinimalWindowsDev/StepParser/issues | — | **LOW** (watch) | README documents WARNING-and-continue on non-conformant complex entities — a stated leniency policy worth watching. |
| **LibreDWG** | Yes, very active | Own DWG/DXF reader | https://github.com/LibreDWG/libredwg/issues | GNU mailing list | **HIGH (DWG/DXF, off-format)** | **On OSS-Fuzz**, hundreds of `[FUZZ]`-labeled crashers + CVEs (CVE-2025-61154 heap overflow; OSV-2026-995 double-free). DWG/DXF ≠ STEP, but a gold vein *if* the corpus ever covers DWG/DXF adversarial parsing. |
| **Blender 3D-Print-Toolbox / bmesh** | Yes | Internal bmesh | https://projects.blender.org/extensions/print3d_toolbox/issues (403 to bots) | blender.stackexchange | **LOW-MED** | Real defect taxonomy (degenerate/non-manifold/intersecting/zero-thickness) but input is internal bmesh — rarely a portable attached file. Use as taxonomy, not file source. |
| **Fornjot** (Rust b-rep) | **Discontinued (2025)** | Own Rust b-rep | https://github.com/hannobraun/fornjot/issues | — | **LOW** | Project ended; STEP was future-only. Historical only. |

---

## Ranked shortlist — top ~10 NEW sources to mine next

1. **assimp issue tracker + OSS-Fuzz** — *why:* single richest vein of malformed-file→crash across many formats, and OSS-Fuzz means most crashers arrive as minimal self-contained reproducer files; its STEP importer is **independent of OCCT** (kernel diversity). *First look:* `is:issue label:"crash"` + the fuzzer meta-issues #2734/#2878, and cross-ref `google/oss-fuzz-vulns` YAMLs (e.g. OSV-2025-280). STEP-specific: #3800 (`automotive_design` schema rejection), #6343 (silent NULL scene).
2. **ruststep** — *why:* the best *independent Part-21 parser* source; clean, minimal syntax defects with files tagged by originating CAD tool. *First look:* https://github.com/ricosjp/ruststep/issues/252 (Plasticity/HOOPS AP203 `DATA;` tokenizer failure, file attached) → then #256 empty `()`, #243/#181 literal tokenization.
3. **PrusaSlicer STEP importer** — *why:* mature OCCT STEP path with a well-labeled open-edge / faceting / malformed-crash stream and reproducer files; surfaces kernel-version divergence. *First look:* #11305 (stack overflow on malformed STEP) and #8998 (STEP→127 open-edges vs STL of same part).
4. **OrcaSlicer STEP importer** — *why:* highest-volume, attachment-rich slicer STEP stream; many face-orientation / dropped-feature / empty-import tickets. *First look:* #7578 (bad face orientation renders cut-sphere solid), #6441 (spheres dropped from Onshape STEP), #12366 (STEP→no geometry).
5. **Online3DViewer + occt-import-js** — *why:* non-developers upload real breaking STEP with strong cross-oracle signal ("opens in CAD Assistant, 0 meshes here"). *First look:* Online3DViewer `is:issue step` for empty/broken-render attachments (#467, #512); occt-import-js #54, #37.
6. **lib3mf** — *why:* 3MF is a ZIP+XML/OPC container → an entirely under-covered malformed surface (bad ZIP, duplicate ResourceIDs, OPC/encoding errors) plus fuzzing/CVE history; the corpus has almost no container-format defects. *First look:* TALOS-2020-1226 (crafted-.3mf UAF), #7 (valid rejected as bad ZIP), #307 (UTF16).
7. **buildingSMART `ifc-gherkin-rules` + Validation Service** — *why:* a maintained, *executable* taxonomy of malformed-input classes (geometry subcontexts, units, placement, alignment) — mine rule names/`.feature` files the way we mined ShapeFix class names, giving IFC/AP242-adjacent coverage. *First look:* browse `features/` rule groups (GEM*, geometry/units) + IfcOpenShell #5098 (rule-vs-practice tension).
8. **trimesh + Open3D** — *why:* both are "load any messy file" libraries; trimesh ships an in-repo broken-model corpus, Open3D's RPly path yields many concrete "this exact PLY fails" reports. *First look:* Open3D "Read PLY failed"/"RPly" search; trimesh #95 (empty ASCII STL <84 B), #239 (`vt`<`v` OBJ), and the `models/` folder.
9. **MeshLab `meshlab/issues`** — *why:* parser-level crashers (stack-smash on malformed PLY/OBJ) with attached files. *First look:* filter label `confirmed` + attachment; #1112 (stack smashing on PLY), #391.
10. **Draco + fTetWild** — *why:* Draco is OSS-Fuzz'd → minimal self-contained `.drc` crashers; fTetWild eats triangle-soup and names failing STLs that map to public Thingi10K models. *First look:* Draco #1096 (OSS-Fuzz `.drc` crash), #356; fTetWild #82 (`96773_sf.stl`), #75.

*Bonus (off-format, hold):* **LibreDWG** — enormous OSS-Fuzz/CVE crasher stream, but DWG/DXF, not STEP; mine only if the corpus expands to DWG/DXF adversarial parsing.

---

## Public test-file collections / datasets of known-bad inputs

License notes are load-bearing: we can **INGEST** license-clean files, but only **DESCRIBE**
anything restricted. Verify per-file headers before ingest in all cases.

| Dataset | What | URL | License | Pathological? | Promise |
|---|---|---|---|---|---|
| **MBx-IF / NIST test cases** (STC 6-10, FTC 6-11, CTC 1-5, HTC 2024, MTC, D2MI) | NIST-authored parts, native CAD + STEP AP242 & AP203, distinct from the already-mined PMI suite | https://www.mbx-if.org/home/cax/resources/ | Stated **"no restrictions"** → **INGEST** (verify) | Valid-but-edge-case (exotic-but-legal PMI/tolerancing/AP242 constructs kernels mishandle) | **HIGH** — biggest clean new seam; strong oracle-divergence material |
| **CAx-IF test-round STEP files** (per round) | Real exporter output submitted twice-yearly; vendor-specific quirks | https://www.mbx-if.org/home/cax/testrounds/ | MBx-IF "no restrictions" (some production models member-gated) → INGEST clean subset | Real-world exporter quirks | **HIGH** — complements nearly-exhausted AP242 Ed.3 seam |
| **Better STEP (`better-step/abs`)** | Converter Fusion360+ABC B-reps → HDF5; **~5% fail to mesh in OCCT** | https://github.com/better-step/abs · arXiv:2506.05417 | Code open; data = ABC/Fusion360 (already cleared, permissive) | Pathology is *labeled* (the failing 5%), not injected | **MED-HIGH** — run it as a *filter* to isolate OCCT-mesh-failing models |
| **MeshRepairTestModels** | Purpose-built broken meshes (holes, non-manifold, degenerate) | https://github.com/caretdashcaret/MeshRepairTestModels | Verify repo LICENSE before ingest | **Yes — defective by construction** | **MED-HIGH** (mesh side; small) |
| **fTetWild-referenced Thingi10K subset** | Named failing STLs (e.g. `96773_sf.stl`) map to public Thingi10K | https://ten-thousand-models.appspot.com | Thingi10K per-model licenses (mixed; mostly CC) — check per file | Yes (self-intersecting/non-watertight) | **MED-HIGH** — Thingi10K already mined; use the *failing-subset labels* as a target list |
| **CC3D-PSE / CC3D-Ops** (Uni. Luxembourg) | ~50k scan→CAD pairs; PSE meshes are noisy real scans | https://cvi2.uni.lu/cc3d-dataset/ | **Signed license agreement required** → **DESCRIBE-ONLY** unless signed | Yes (scan pathology) for PSE | **MED** — great pathology, licensing friction |
| **MFCAD / MFCAD++ / MFCAD-VLM** | Synthetic pythonOCC STEP with per-face machining-feature labels | https://github.com/hducg/MFCAD · zenodo 14038050 | Per-repo (likely permissive) → verify, likely INGEST | No — clean synthetic B-reps | **LOW-MED** — value = license-clean *valid* STEP for negative controls |
| **MechCAD / FllumaOne (2026)** | Labeled real-part STEP; FllumaOne = kernel-validated feature histories | FllumaOne arXiv:2606.17696 | Unconfirmed → DESCRIBE until checked | Mostly clean | **LOW-MED** — watch FllumaOne (kernel-validation angle) |
| **assimp / Draco / LibreDWG OSS-Fuzz corpora** | Minimal crashing files from continuous fuzzing | oss-fuzz-vulns; per-project `test/models-nonbsd` | Reproducers embedded in issues; corpus licenses vary → DESCRIBE, synthesize equivalent | Yes (adversarial/malformed) | **HIGH as reproducers** (harvest individually, don't bulk-ingest) |

**Negative finding:** OCCT is **not** a dedicated OSS-Fuzz project; there is no public STEP/IGES
fuzz crash *corpus*. STEP fuzz-grade reproducers must be scavenged individually from trackers
(e.g. PrusaSlicer #11305). Only **assimp, Draco, LibreDWG, lib3mf** have OSS-Fuzz/fuzzing veins,
and those are mesh/container/DWG formats, not STEP.

---

## Gaps note — defect categories our corpus likely under-covers

These sources map to buckets the STEP-centric corpus is thin on:

- **Container-format defects (3MF = ZIP+XML/OPC).** Bad ZIP central directory, duplicate
  `ResourceID`s, OPC relationship errors, UTF-16/encoding faults. → **lib3mf**. The corpus has
  essentially no ZIP-container or OPC-layer fixtures.
- **Adversarial/fuzz minimal crashers with real reproducers.** Heap overflow / UAF / double-free /
  stack-smash on truncated or crafted files — currently only lightly represented (§12.11 Ad*).
  → **assimp, Draco, MeshLab, admesh, lib3mf** (and LibreDWG if DWG/DXF is ever in scope).
- **Independent-parser Part-21 lexical divergences.** Empty parameter lists `()`, `DATA;`
  delimiter handling, string/literal tokenization, non-ASCII string literals — cases OCCT silently
  tolerates but stricter parsers reject (differential signal). → **ruststep, steputils, Foxtrot, assimp**.
- **STEP-vs-mesh round-trip divergence.** "Same part: STEP import shows N open edges the STL does
  not," faceting of curved surfaces, kernel-version-sensitive results. → **PrusaSlicer/OrcaSlicer/Bambu**.
- **Producer-side degenerate-geometry recipes.** Thin trailing edges → degenerate patches (aircraft
  CAD). → **OpenVSP** — realistic recipes for *generating* pathological STEP.
- **IFC/AP242-adjacent geometry-context & placement rules.** Wrong geometric subcontexts, unit
  inconsistencies, placement/alignment faults, as an *executable* rule taxonomy. → **buildingSMART
  ifc-gherkin-rules**.
- **PLY/OFF-specific parser pathologies.** Non-triangulable polygon faces, truncated face data,
  RPly decomposition failures — the corpus is STL/STEP-heavy and PLY-light. → **Open3D, MeshLab, trimesh**.
- **License-clean *valid* STEP for negative controls.** MFCAD/MFCAD++ and MBx-IF give clean,
  ingestible STEP to strengthen the Ctl<NNN> negative-control set and oracle-divergence baselines.

---

## Structural takeaways

1. **OSS-Fuzz presence is the shortcut to minimal crashing files** — only **assimp, Draco,
   LibreDWG** (and **lib3mf** via Talos history; **Manifold** via in-repo FuzzTest) have it.
   Everywhere else, file-level reproducers are scavenged from issue/forum attachments.
2. **OCCT-JS viewers + OCCT-based slicers are high-volume but OCCT-correlated** — they partly
   *corroborate* the existing OCCT mine rather than diversify the kernel. The genuine
   kernel-diversity novelty is **ruststep / assimp-STEP / steputils / Foxtrot** (independent parsers).
3. **Recurring catalog-worthy classes across all mesh trackers are consistent:** truncated/short
   binary headers + facet-count mismatch (STL), non-triangulable/degenerate polygon faces,
   non-manifold edges (>2 faces/edge), zero-area/sliver/duplicate triangles, inverted/inconsistent
   normals, open/non-watertight surfaces, and container-level bad-ZIP/XML/encoding (3MF).
4. **Deprioritize:** OpenMesh (login-gated tracker), PyMesh (stale), Instant Meshes (dormant),
   Fornjot (discontinued), Blender toolbox (non-portable bmesh input), cascadio (very low volume).
