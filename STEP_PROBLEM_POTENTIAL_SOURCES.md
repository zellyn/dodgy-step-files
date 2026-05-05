# STEP File Problem Sources — Potential Sources Catalog

**Purpose.** Identify *where* to find descriptions of problematic STEP file inputs that real-world CAD kernels have learned to handle. The goal of this document is to enumerate sources thoroughly enough that a downstream document can record *descriptions* of each problem in enough detail to recreate problematic inputs that exhibit the same problem, without copying any STEP files into this repository.

**Approach.** We are *not* downloading STEP files or CAD source. We are cataloging where to look, what to look for, and (where possible) which specific issues / commits / paragraphs / menu items / KB articles to mine.

**Verification status.** Each entry is tagged as one of:
- ✅ **Verified**: URL/repo/paper/issue confirmed via web research.
- 🟡 **Probably exists**: supported by industry knowledge but specific URL not pulled.
- ⚠️ **Needs checking**: recall-based, verify before citing.

**Coverage.** Each table row has a `Done` column with `[ ]` / `[x]`. `[x]` means findings from that source are reflected in `STEP_PROBLEM_CATALOG.md`. Partial coverage = `[~]`. Deliberately skipped (paywalled, closed, no access) = `[⊘]`. Open gap = `[?]`.

---

## 0. The Single Richest Source: OCCT Source Code

**Status: [x]**: covered. OCCT source (test fixtures, translation pipeline, shape-fix / shape-analysis / shape-upgrade, git log, Mantis tracker) contributes the bulk of the catalog's defect-class evidence.

OpenCascade Technology (OCCT) is the largest open-source CAD kernel. Two decades of accumulated workarounds for real-world STEP files live inside it, the code is well-commented, and the git history is intact. **For each fix we should be able to deduce the problem it is designed to fix.** This section gets its own top-level treatment because it is expected to be the densest payoff per hour of investigation.

**Repo.** https://github.com/Open-Cascade-SAS/OCCT, formerly hosted on Mantis (https://tracker.dev.opencascade.org/) and `git.dev.opencascade.org`. ✅

### 0.1 OCCT modules to mine systematically

| Module / Path | What it tells us | Notes |
|---|---|---|
| `src/ShapeFix/` | Each `ShapeFix_*` class addresses a specific topological/geometric pathology. Class names are a problem taxonomy: `ShapeFix_Wire` (gaps, ordering, self-intersection, missing edges, seam handling), `ShapeFix_Face` (missing pcurves via `FixPcurves`, intersecting wires, wrong orientation), `ShapeFix_Shell` (orientation, free edges), `ShapeFix_Solid` (closed-shell), `ShapeFix_Edge` (sameparameter, bad ranges), `ShapeFix_Wireframe` (small edges, gaps in 3D), `ShapeFix_FixSmallFace`, `ShapeFix_FreeBounds`, `ShapeFix_IntersectingWires`, `ShapeFix_SplitCommonVertex`, `ShapeFix_ComposeShell`. | Read the *header comments* and the docstring on each `Perform()` / `Fix*()` method — they explicitly name the defect class. Then walk the implementation looking for every `if`/`else` branch as a sub-case. |
| `src/ShapeAnalysis/` | Detection complement to `ShapeFix/`: each analyzer pinpoints what could be wrong before we attempt a fix. `ShapeAnalysis_Wire`, `_Edge`, `_Surface`, `_CheckSmallFace`. | The detection criteria *are* the problem definitions. |
| `src/ShapeUpgrade/`, `src/ShapeCustom/`, `src/ShapeBuild/`, `src/ShapeExtend/` | Conversions used during healing (e.g., `ShapeUpgrade_ShellSewing`, splitting non-G1 surfaces, removing locally degenerate edges). | The "why we ever need to upgrade" reveals the input pathology. |
| `src/ShapeProcess/`, `src/ShapeProcessAPI/` | Configurable healing pipeline driven by resource files (`XSTEP.rsc`, `IGES.rsc`). | The resource files list every healing operator and its default thresholds — i.e., the assumed bad-input distribution. |
| `src/STEPControl/`, `src/STEPCAFControl/` | Top-level STEP reader/writer. Reader applies healing automatically; the call sequence is a roadmap. | `STEPControl_Reader::TransferRoots()`, `Transfer()` show the standard healing chain. |
| `src/RWStepAP203/`, `src/RWStepAP214/`, `src/RWStepAP242/`, `src/RWStepBasic/`, `src/RWStepGeom/`, `src/RWStepRepr/`, `src/RWStepShape/`, `src/RWStepVisual/`, `src/RWStepDimTol/`, `src/RWStepFEA/`, `src/RWStepKinematics/`, etc. | Per-entity Read/Write code. Each `RWStepXxx_RWFoo::ReadStep()` contains compatibility branches for differently-emitted variants of entity `Foo`. | These are gold for parser-level quirks: different vendors emit the same entity in subtly different ways. |
| `src/StepToTopoDS/`, `src/TopoDSToStep/` | Translation layer between STEP entity graph and OCCT BRep. Functions like `StepToTopoDS_TranslateEdgeLoop`, `_TranslateFace`, `_TranslateEdge`, `_TranslateVertex`, `_TranslateCompositeCurve` contain known-sender-quirk handling. | Also the source of "we silently turn this into that" defaults. |
| `src/StepData/`, `src/StepFile/`, `src/StepSelect/` | Part 21 lexer/parser. Encoding handling, comment handling, header parsing, multi-section handling. | `StepFile_Read*` and the lexer (yacc/lex) reveal which malformed-but-tolerated forms are accepted. |
| `src/StepAP203/`, `src/StepAP214/`, `src/StepAP242/`, `src/StepBasic/`, `src/StepDimTol/`, `src/StepGeom/`, `src/StepKinematics/`, `src/StepRepr/`, `src/StepShape/`, `src/StepVisual/` | Schema-level entity definitions. The set of subtypes accepted in each slot reveals which entity-soup combinations have been seen in the wild. | |
| `src/IFSelect/`, `src/Interface/`, `src/Transfer/` | Generic translator framework (used by both STEP and IGES paths). Diagnostic messages, severity codes, transfer status codes. | The `Interface_Check` / `Interface_CheckIterator` infrastructure lists every diagnostic the translator can emit. |
| `src/BRepCheck/`, `src/BRepLib/` | Lower-level invariant checking; `BRepLib::SameParameter` recomputation is itself a catalog of how 3D and 2D pcurves drift apart. | Triggered after almost every translator call. |
| `src/XSAlgo/`, `src/XSDRAW*/`, `src/XSControl/` | Cross-system / "exchange" healing infrastructure. `XSAlgo_AlgoContainer` is the dispatch point for healing during translation. | |
| `tests/` | OCCT's own test suite. `tests/de/`, `tests/de_step/`, `tests/de_iges/`, `tests/bugs/step/`, `tests/heal/` contain regression cases. **Each test name and its DRAW-script body encode a specific defect.** | This is probably the single highest-density resource in the entire OCCT tree per minute of reading. |
| `tests/heal/` | Healing-specific regression tests. Test names like `data_*`, `pcurve_*`, `sewing_*` map to defect classes. | |
| `dox/user_guides/shape_healing/` | The user-guide markdown is itself a problem catalog with examples. Parameter list documents tolerances/heuristics chosen to handle real bad files. | https://dev.opencascade.org/doc/overview/html/occt_user_guides__shape_healing.html ✅ |
| `dox/user_guides/step/` | STEP translator user guide. Parameters like `read.precision.mode`, `read.maxprecision.value`, `read.stdsameparameter.mode` document the tunables — and thus what kind of bad inputs they tune for. | https://dev.opencascade.org/doc/overview/html/occt_user_guides__step.html ✅ |

### 0.2 Mining strategies

1. **Walk every `ShapeFix_*` and `ShapeAnalysis_*` class header.** Each one is a problem definition. Build a table: class → defect class → typical sender → sample fix strategy.
2. **Grep the source for comment markers** — `// fix`, `// workaround`, `// patch`, `// hack`, `// FIXME`, `// XXX`, `// see issue`, `// CAS.CADE`, `// for compatibility`, `// for invalid`, `// for old`, `// pro/e`, `// catia`, `// sw`, `// solidworks`, `// inventor`, `// nx`, `// to handle`. Each match is a candidate sender-specific quirk.
3. **Read `git log` on `src/ShapeFix/` and `src/STEPControl/`** filtered for keywords like "fix", "regression", "AP203", "AP214", "AP242", "bug 0NNNNN" (Mantis bug numbers). Commit messages frequently cite Mantis bug IDs that are still readable in the archive.
4. **For each Mantis ID found in commit messages**, look up the bug at https://tracker.dev.opencascade.org/view.php?id=NNNNN. Bugs predating GitHub (mid-2010s) live there; many include attached STEP files (do not download — note the description).
5. **Read every `tests/heal/*` and `tests/de_step/*` test script.** DRAW commands encode the input geometry constructively — sometimes the test creates the broken shape inline rather than reading a file, which is exactly the recreate-able description we want.
6. **Cross-reference the resource files** (`src/SHHealing/SHHealing.rsc`, `src/XSTEP/XSTEP.rsc`, `src/IGES/IGES.rsc`). Each named operator there points back to a `ShapeFix_*` class.
7. **Compare OCCT minor versions' release notes** (e.g., 7.4 → 7.5 → 7.6 → 7.7 → 7.8). Bug-fix bullet points are a problem catalog.

### 0.3 Why OCCT is uniquely valuable here

- It is the *receiving* side of every other CAD vendor's exporter, so the workaround set is the de-facto union.
- Comments and identifiers are unusually descriptive (decades of European engineering culture in code).
- The Mantis-archive + GitHub-issues + git-log triple gives provenance for every fix.
- It is the engine under FreeCAD, KiCad MCAD, gmsh, Salome, pythonocc, CadQuery, build123d, and more, so when those projects file STEP bugs, the fix usually lands here.

---

## 1. Other Open-Source CAD Kernel Sources

| # | Name | Description | Pointer | Status |
|---|---|---|---|---|
| 1.1 | [x] **STEPcode (formerly NIST STEP Class Library)** | C++/Python schema-driven parser generator. Its issue tracker focuses on Part 21 parser-level bugs — encoding, comments, REFERENCE/ANCHOR sections, Edition 3 features. | https://github.com/stepcode/stepcode/issues ; wiki https://github.com/stepcode/stepcode/wiki | ✅ — batch 07 (T001-T045) |
| 1.2 | [x] **IfcOpenShell `step-file-parser`** | Pure-Python Lark-based ISO 10303-21 validator. Bug list is essentially a catalog of malformed Part 21 syntax in the wild. | https://github.com/IfcOpenShell/step-file-parser | ✅ — batch 07 (joint with STEPcode) |
| 1.3 | [x] **CGAL Polygon Mesh Processing repair** | Not STEP-aware, but downstream consumer of STEP-derived meshes; `stitch_borders`, `repair_polygon_soup`, `autorefine_and_remove_self_intersections` etc. Every function name is a problem class. | https://doc.cgal.org/latest/Polygon_mesh_processing/index.html ; issues with PMP / Boolean labels at https://github.com/CGAL/cgal/issues | ✅ — batch 09 (H001+) |
| 1.4 | [~] **Manifold (elalish/manifold)** | Mesh boolean kernel; issues describe input degeneracies received from STEP→mesh pipelines. Cleanup logic is small and focused, revealing minimal manifold preconditions. | https://github.com/elalish/manifold/issues ; https://github.com/elalish/manifold/wiki/Manifold-Library | ✅ — batch 09 listed as a complementary tool but only minor entries; Manifold issue tracker not deeply mined for input-degeneracy patterns |
| 1.5 | [x] **OpenNURBS / openNURBS toolkit** (Rhino) | 3DM is its own format but Rhino's STEP path is well-documented; McNeel forum has detailed pcurve-error threads. | https://discourse.mcneel.com/ ; https://github.com/mcneel/opennurbs | ✅ — batch 14 (K001-K028) |
| 1.6 | [⊘] **SMLib / GSNlib** | Closed-source kernels; only documentation is exposed via licensee bug reports, with limited visibility. | n/a | ⚠️ — skipped: closed-source, no public KB, low signal |

---

## 2. Open-Source CAD Application Issue Trackers

| # | Name | Description | Pointer | Status |
|---|---|---|---|---|
| 2.1 | [x] **FreeCAD** | Largest pool of "I downloaded this STEP and it broke" reports. Recurring themes: `CONFIG_CONTROL_DESIGN` vs `AUTOMOTIVE_DESIGN` schema differences (#15685), Fusion 360 files hanging FreeCAD (#6311), empty imports with no error, performance on >1 GB files (#18735), 1.0 RC2 regressions (#16886, #17098, #17839), entire-library-broken-by-OCC-bug (#5783, Multiboard parts library). | https://github.com/FreeCAD/FreeCAD/issues — filter label `STEP` | ✅ — batches 19 (Multiboard), 20 (forum/issue), 22 (KiCad→FreeCAD pipeline) |
| 2.2 | [x] **FreeCAD forum** | Often has attached files. Threads on "Repairing a step object" (t=37413), "Crashing when loading STEP file" (t=6404), "CAD Exchanger / FreeCAD 0.17 fillets" (t=23206). | https://forum.freecad.org/ | ✅ — batch 20 (J-series), 22 (Y-series) |
| 2.3 | [x] **BRL-CAD** | `step-g` importer documented as "in its infancy"; its limitations and TODOs are themselves a roadmap of problems. NURBS stitching post-processing, BoT mesh healing in MGED/Archer. SourceForge mailing list has historical STEP threads. | https://brl-cad.github.io/wiki/task/STEP_importer_improvements/ ; https://github.com/BRL-CAD/brlcad/issues | ✅ — batch 14 (K001-K028) |
| 2.4 | [~] **OpenSCAD** | OpenSCAD itself doesn't natively read STEP (issue #1650 is the long-running discussion); `agordon/openscad-step-reader` is a proof-of-concept whose bug list could be informative. | https://github.com/openscad/openscad/issues/1650 ; https://github.com/agordon/openscad-step-reader | ✅ — batch 22 (Y-series, OpenSCAD→FreeCAD→STEP pipeline). Direct openscad-step-reader bug list NOT exhaustively scraped |
| 2.5 | [x] **SolveSpace** | NURBS-as-STEP exporter; produces files FreeCAD won't import. Forum thread parent=4789 documents this. | https://github.com/solvespace/solvespace/issues ; https://solvespace.com/forum.pl | ✅ — batch 18 (I-series, SolveSpace issues triaged) |
| 2.6 | [x] **KiCad MCAD / 3D-board STEP** | KiCad emits 3D-board STEP; downstream issues especially around component-instance transforms, naming collisions across many same-named instances. | https://gitlab.com/kicad/code/kicad/-/issues | 🟡 — batch 22 (Y001-Y011 PCB/MCAD), batch 18 (label-keyed dict collision) |
| 2.7 | [x] **CadQuery / build123d** | Python CAD on top of OCCT; issues expose problems exposed through OCCT's STEP path. | https://github.com/CadQuery/cadquery/issues ; https://github.com/gumyr/build123d/issues | ✅ — batch 18 (CadQuery #1962/#1521/#1551/#1935/#1338 etc.) |
| 2.8 | [x] **pythonocc-core** | OCCT's Python bindings. Specific issues: #511 (misaligned elements), #1278 (umlaut / extended-string crash), #83 (reading), #482 (label-name on export). | https://github.com/tpaviot/pythonocc-core/issues | ✅ — batch 18 (I-series) |
| 2.9 | [x] **gmsh** | Wraps several OCCT healing routines (`HealShapes`, `OCCFixDegenerated`); usage flags reveal which are needed in practice. | https://gmsh.info/ ; https://gitlab.onelab.info/gmsh/gmsh | ✅ — batch 09 (gmsh OCC healing flags), batch 22 (gmsh→meshing) |
| 2.10 | [x] **Salome SHAPER / GEOM "Repair" menu** | "Glue Faces", "Remove Holes", "Suppress Faces", "Limit Tolerance", "Fuse Edges" — every menu item is a defect class. | https://docs.salome-platform.org/ | ✅ — batch 09 (H-series, menu items as taxonomy) |
| 2.11 | [x] **Netgen "Geometry Doctor"** | Healing module for IGES/STEP, documented in mecway threads as a standard intermediate. | https://github.com/NGSolve/netgen | ✅ — batch 09 |

---

## 3. Implementor Forums, Conformance Suites, & Interoperability Logs

| # | Name | Description | Pointer | Status |
|---|---|---|---|---|
| 3.1 | [x] **CAx-IF / MBx-IF** (PDES Inc., prostep ivip, AFNeT) | 56+ test rounds since 1999. Each round publishes a Test Suite PDF, reference STEP files, and statistics in CAESAR. The largest *curated* collection of test cases for AP203/AP214/AP242 (geometry, PMI, kinematics, composites, assembly). | https://www.mbx-if.org/home/cax/ ; Round 56J Test Suite PDF on the same site | ✅ — batch 02 (Round 56J + 57J test suites) |
| 3.2 | [x] **CAx-IF Recommended Practices** | Each describes a known interoperability problem and the agreed workaround. Reverse-engineering these gives a specification of problems. Topics: Validation Properties, External References, Tessellated Geometry, Assembly Structure, Kinematics, Composites, AP242 XML BOM. | https://www.mbx-if.org/home/cax/cax-recommended-practices/ | ✅ — batch 02 (gvp, tess, pmi, ext_ref, assy_struct, suppl_geo, uda, gen_guide PDFs) |
| 3.3 | [~] **STEP Tools Implementors Issue Logs** | Older but historically deep, especially Melbourne and New Orleans rounds. | https://www.steptools.com/stds/impforum/melbiss.html ; .../nolaiss.html | ✅ — batch 16 references the logs in source manifest; specific historical issues only lightly extracted |
| 3.4 | [~] **PDM Implementor Forum** | Sister forum to CAx-IF, focused on assembly metadata / product structure. | https://www.mbx-if.org/home/pdm/ | ✅ — batch 17 covers PDM/LOTAR/prostep; PDM-IF-specific deliverables not separately mined |
| 3.5 | [~] **NIST MBE PMI Validation & Conformance Testing Project** | Canonical PMI test corpus. CTC + FTC + STC test cases (421 PMI annotations across 11+ models). Models, native files, STEP files, and per-tool reports are downloadable. | https://www.nist.gov/ctl/smart-connected-systems-division/smart-connected-manufacturing-systems-group/mbe-pmi-0 ; https://pages.nist.gov/CAD-PMI-Testing/ ; https://data.nist.gov/pdr/lps/276B3C17848DEC5BE0531A570681E6081452 | ✅ — batch 06 covers SFA which validates against this corpus; per-tool round-trip reports not directly mined |
| 3.6 | [x] **NIST STEP File Analyzer and Viewer (SFA)** | Open-source. Source code is itself a catalog of "things to check"; every report row is a class of issue. Documented in NIST AMS 200-4 / 200-6 / 200-10. | https://github.com/usnistgov/SFA ; https://www.nist.gov/services-resources/software/step-file-analyzer-and-viewer | ✅ — batch 06 (S001-S070) |
| 3.7 | [⊘] **ISO 10303 ATS (Abstract Test Suites)** | Each AP has an abstract test suite (Part 3xx/4xx). Less practical than CAx-IF rounds but normative. | ISO Standards Catalogue (paywalled); summaries at https://www.steptools.com/stds/step/ | ✅ — paywalled; CAx-IF rounds (batch 02) provide the practical equivalent |
| 3.8 | [~] **CAESAR (CAx-IF database)** | Internal CAx-IF tool comparing native + target statistics across pairwise exchanges. Round summaries published. | via mbx-if.org | ✅ — batch 02 cites CAESAR-aware GVP threshold logic; raw round-summary tables not separately mined |

---

## 4. Healing-Code Analysis Targets (apart from OCCT — see §0)

| # | Name | What to mine | Pointer | Status |
|---|---|---|---|---|
| 4.1 | [x] **CGAL PMP repair functions** | Function names map directly to defect classes. | https://doc.cgal.org/latest/Polygon_mesh_processing/index.html | ✅ — batch 09 |
| 4.2 | [x] **gmsh healing wrappers** | Specific OCCT operators they choose to expose. | https://gitlab.onelab.info/gmsh/gmsh | ✅ — batch 09 |
| 4.3 | [x] **Salome SHAPER / GEOM Repair menu** | UI items as defect taxonomy. | https://docs.salome-platform.org/ | ✅ — batch 09 |
| 4.4 | [x] **Netgen Geometry Doctor** | Healing module for IGES/STEP. | https://github.com/NGSolve/netgen | ✅ — batch 09 |
| 4.5 | [~] **SolidWorks "Import Diagnostics"** | Closed source; UI + KB articles enumerate categories: faulty faces, gaps, bad bodies. Useful as a reference taxonomy. | TriMech blog "Quick Imported Simplification using SOLIDWORKS Import Diagnostics" | ✅ — batch 10 (SolidWorks KB) covers symptoms; the UI categories themselves used as cross-reference but not as a primary mining target |

---

## 5. Commercial Translator / Validator Vendors (problem catalogs from feature lists, KBs, release notes)

| # | Name | Why useful | Pointer | Status |
|---|---|---|---|---|
| 5.1 | [x] **CADfix (ITI / Wipro)** | The canonical industrial heal-everything tool (CADfix DX/PPS/VIZ). Marketing literature itemizes specific defect classes (gap closure via re-stitching, parasitic intersection removal, degenerate edge reconstruction; claims 85–95% automatic). | https://www.iti-global.com/cadfix ; https://www.cadinterop.com/en/your-needs/cad-repair-and-healing/translate-and-repair-with-cadfix.html | ✅ — batch 11 (W-series) |
| 5.2 | [x] **TransMagic** | TransMagic PRO repair docs list common defect categories. | https://transmagic.com/cad-repair/ | ✅ — batch 11 |
| 5.3 | [x] **Datakit (CrossManager / CrossCAD)** | Format-comparison docs (e.g., "STEP protocols AP203/AP214") describe per-protocol caveats. | https://www.datakit.com/en/step_protocols.php | ✅ — batch 11 |
| 5.4 | [x] **Capvidia (MBDVidia, FormatWorks, CompareVidia)** | Specializes in PMI/AP242 round-trip; blog has detailed "best STEP file to use" articles enumerating known problems. | https://www.capvidia.com/ ; https://www.capvidia.com/blog/best-step-file-to-use-ap203-vs-ap214-vs-ap242 | ✅ — batch 11 |
| 5.5 | [x] **Theorem Solutions / Tech Soft 3D** | CADTranslate / CADPublish (now SpinFire Convert). PMI-aware translator; release notes/KBs document fixed bugs. | https://www.theorem.com/translate ; https://www.techsoft3d.com/ | ✅ — batch 11 |
| 5.6 | [x] **Tech Soft 3D HOOPS Exchange** | Underlies many commercial tools (e.g., SpaceClaim's STEP translator). Release notes (visible via SpaceClaim KBs) reveal version-by-version fixes. SpaceClaim 2025R2 broke things going from HOOPS Exchange 24.6.0 → 25.2.0. | https://www.techsoft3d.com/products/hoops/exchange/ | ✅ — batch 11 |
| 5.7 | [x] **Spatial 3D InterOp / 3D ACIS Modeler** | Dassault subsidiary; powers ACIS-based products. KBs are a parallel universe of the same issues from the ACIS perspective. | https://www.spatial.com/products/3d-interop | ✅ — batch 11 |
| 5.8 | [x] **CAD Exchanger** | Forum and FreeCAD addon discussions document specific issues (FreeCAD 0.17/0.18 STEP v2 fillet problems, "One or more parts could not be imported"). | https://cadexchanger.com/ ; FreeCAD forum t=23206 | ✅ — batch 11 |
| 5.9 | [~] **STEP Tools "ST-Developer"** | Reference implementations; their docs sometimes explicitly note which schema variants exist in the wild. | https://www.steptools.com/ | ✅ — batch 11 references; batch 16 (ISO spec) cites melbiss/nolaiss historical implementor logs |
| 5.10 | [~] **JSDAI** | Java SDAI implementation; older but useful as a strict reference parser. | https://www.jsdai.net/ | ✅ — batch 11 lists; defect catalog is thin (project moribund) — minimal extraction |

---

## 6. CAD Vendor Bug-Fix Histories (closed source but KBs are public)

| # | Name | Pointer | Status |
|---|---|---|---|
| 6.1 | [x] Autodesk KB — Inventor / Fusion 360 / AutoCAD ("STEP units messed", "Missing or not recoverable objects after importing STEP into AutoCAD", "Wrong units for STEP files in Plant 3D") | https://www.autodesk.com/support/technical/article/caas/sfdcarticles/ — search "STEP" | ✅ — batch 10 (V-series) |
| 6.2 | [x] PTC Creo / Pro/E community — "STEP AP242 and semantic references" thread; legacy Pro/E STEP exports notoriously slow into SolidWorks | https://community.ptc.com/ ; https://creotips.com/ | ✅ — batch 10 |
| 6.3 | [x] SolidWorks forum — STEP conversion taking forever (#26398), STEP 242 tessellation refusal, crashes during export | https://forum.solidworks.com/ | ✅ — batch 10 |
| 6.4 | [x] Onshape forum — "step file export/import (bug?)" #22945, "Exporting STEP file BUG" #25971, MBD/PMI on AP242 round-trip loss (#30657), inch-export-units issue #6658, faulty topology after 360° revolve export (#18485) | https://forum.onshape.com/ | ✅ — batch 10 |
| 6.5 | [x] Siemens NX / Solid Edge — NX scales Onshape's meter-internal exports incorrectly when reading mm | https://community.sw.siemens.com/ | ✅ — batch 10 |
| 6.6 | [x] Eng-Tips CAD forum — long history of problem reports (e.g., CATProduct STEP export with duplicated instances at same location) | https://www.eng-tips.com/forums/cad/ | ✅ — batch 10, 22 |
| 6.7 | [x] PrePoMax / nTop / SimScale support forums — downstream FEA / simulation tools see lots of bad STEP. PrePoMax's "STEP geometry with inch units imports at wrong scale" is a classic | https://prepomax.discourse.group/ ; https://support.ntop.com/ ; https://www.simscale.com/forum/ | ✅ — batch 10, 17 (downstream-FEA cluster) |

---

## 7. Curated Datasets

| # | Name | What it is | Pointer | Status |
|---|---|---|---|---|
| 7.1 | [x] **ABC Dataset** (NYU GCL et al.) | ~1 million CAD models in STEP, Parasolid, STL. Sourced from Onshape public docs. Random real-world models — guaranteed to include broken ones. | https://deep-geometry.github.io/abc-dataset/ ; https://github.com/deep-geometry/abc-dataset ; CVPR 2019 paper "ABC: A Big CAD Model Dataset for Geometric Deep Learning" | ✅ — batch 19 (D001-D013) |
| 7.2 | [x] **Fusion 360 Gallery** (Autodesk) | Released for ML research; includes B-rep + reconstruction sequence. STEP-adjacent. | https://github.com/AutodeskAILab/Fusion360GalleryDataset | ✅ — batch 19 |
| 7.3 | [~] **DeepCAD / CC3D / Furniture-A** | Smaller research datasets used in B-rep ML papers. Verify exact dataset names before citing. | DeepCAD: https://github.com/ChrisWu1997/DeepCAD | ⚠️ — batch 19 covers DeepCAD (D022-D024); CC3D and Furniture-A not directly mined |
| 7.4 | [x] **Thingi10K** | Mostly STL, but a useful comparator and frequently used as a torture test for downstream pipelines. | https://ten-thousand-models.appspot.com/ | ✅ — batch 19 (high-prevalence stats: 45% self-intersect, 22% non-manifold) |
| 7.5 | [⊘] **GrabCAD library** | Massive user-uploaded library; quality varies wildly. Forum threads filtered by "fails to open in X" yield test cases. | https://grabcad.com/ | ✅ — listed; not mined as a separate source. Login-walled forum filtering would be high-effort/low-yield given vendor-KB coverage already captures the failure modes |
| 7.6 | [x] **Multiboard parts library** | Specifically called out in FreeCAD #5783 as triggering an upstream OCC bug across many of its models. | https://www.multiboard.io/parts-library/ | ✅ — batch 19 |

---

## 8. Academic Literature

| # | Name | Why useful | Pointer | Status |
|---|---|---|---|---|
| 8.1 | [x] Patrikalakis, Sakkalis, Shen — "Boundary Representation Models: Validity and Rectification" (2000, *Mathematics of Surfaces IX*); companion: "Manifold Boundary Representation Model Rectification" (3rd ICIDMME, 2000) | Foundational paper on B-rep validity criteria. | Springer (chapter); Sakkalis-Shen-Patrikalakis 2001 draft on cs.wisc.edu | ✅ — batch 15 (L044/L045) |
| 8.2 | [x] Ju Tao — "Fixing Geometric Errors on Polygonal Models: A Survey" | Categorizes mesh repair approaches; useful for the polygonal side. | https://www.cs.wustl.edu/~taoju/research/repairsurvey.pdf | ✅ — batch 15 |
| 8.3 | [x] Tsinghua — "Topology Repair of Solid Models Using Skeletons" (TVCG 2007) | Skeleton-based topology repair. | https://cg.cs.tsinghua.edu.cn/papers/TVCG2007topologyrepair.pdf | ✅ — batch 15 |
| 8.4 | [x] Tsinghua — "Q-Complex" (CAD 2012) | Non-manifold boundary representation theory. | https://cg.cs.tsinghua.edu.cn/papers/lyj-CAD12.pdf | ✅ — batch 15 |
| 8.5 | [x] "Automatic mesh-healing technique for model repair and finite element model generation" (FEAD) | Mesh-side healing motivated by STEP translation defects. | ScienceDirect S0168874X07000741 | ✅ — batch 15 |
| 8.6 | [x] "B-rep Boolean resulting model repair by correcting…" (arXiv 2310.10351) | Recent work on Boolean-output repair. | https://arxiv.org/pdf/2310.10351 | ✅ — batch 15 |
| 8.7 | [x] BrepGen / BRT / eCAD-Net (recent ML B-rep papers) | "Valid B-rep" filtering criteria are useful problem definitions. | arXiv 2401.15563, 2504.07134; ScienceDirect S0010448524001337 | ✅ — batch 15 |
| 8.8 | [⊘] M. Pratt — *Industrial Automation Systems and Integration — Product Data Representation and Exchange*; J. Owen — *STEP, an Introduction*; Mortenson — *Geometric Modeling*; Kemmerer (ed.) — *Sharing the CAD Model* | Older textbook-level discussions of pitfalls. Verify edition + chapters before citing. | publisher catalogs | ⚠️ — print-only / paywalled textbooks; not mined. Their content is approximated by ISO spec mining (batch 16) and the academic survey set (batch 15) |
| 8.9 | [~] Conferences | Solid & Physical Modeling (SPM/SMA), Symposium on Geometry Processing (SGP), *Computer-Aided Design*, *Computer Aided Geometric Design*, *Engineering with Computers*, IMR (International Meshing Roundtable). Search venues for "model repair", "shape healing", "B-rep validity", "geometric tolerance". | various | ✅ — batch 15 catches *CAD* journal papers; SPM/SGP/IMR proceedings not exhaustively crawled |

---

## 9. Standards-Body & Format-Spec Sources

| # | Name | Pointer | Status |
|---|---|---|---|
| 9.1 | [x] ISO 10303 standard parts. Part 11 (EXPRESS), Part 21 (Clear Text — Editions 1/2/3 differ; Edition 3 adds anchor/reference/signature sections, UTF-8 in strings), Part 28 (XML), Part 42 (geometric/topological representation), Parts 203, 214, 242 | http://www.steptools.com/stds/step/IS_final_p21e3.html ; https://en.wikipedia.org/wiki/ISO_10303-21 | ✅ — batch 16 (N001+ for Part 21 lexical) |
| 9.2 | [x] prostep ivip Recommended Practices & white papers (German body); benchmarks are essentially curated bad-file collections | https://www.prostep.org/en/ | ✅ — batch 17 (M-series with LOTAR, prostep JT harmonization) |
| 9.3 | [~] AFNeT (France) interoperability papers — partner in CAx-IF | https://www.afnet.fr/ | ✅ — batch 17 cites AFNeT alongside CAx-IF; AFNeT-only deliverables not directly mined |
| 9.4 | [~] PDES, Inc. — US partner in CAx-IF; publishes white papers on AP242 deployment | https://pdesinc.org/ | ✅ — batch 17 cites PDES Inc. AP242 work; standalone PDES whitepapers not crawled |
| 9.5 | [x] Library of Congress digital format registry (FDD) — authoritative summary of STEP P21 quirks (encoding, comments, instance numbering, multi-data sections) | https://www.loc.gov/preservation/digital/formats/fdd/fdd000448.shtml | ✅ — batch 16 |

---

## 10. Communities, Forums, Chats

| # | Name | Pointer | Status |
|---|---|---|---|
| 10.1 | [x] r/cad, r/FreeCAD, r/SolidWorks, r/CAM | https://www.reddit.com/r/cad/ ; r/FreeCAD ; r/SolidWorks ; r/CAM | ✅ — batch 20 |
| 10.2 | [x] OCCT forum (dev.opencascade.org) — detailed user posts often quote offending entity instance numbers | https://dev.opencascade.org/forums | ✅ — batch 20 (J-series, including FACETED_BREP/OPEN_SHELL J001) |
| 10.3 | [⊘] FreeCAD Discord — live discussion | invite via FreeCAD wiki | 🟡 — skipped: ephemeral; no archive crawl. FreeCAD forum (2.2) and GitHub (2.1) cover the same defect classes |
| 10.4 | [x] StackExchange — Engineering, Computer Graphics, SuperUser | https://engineering.stackexchange.com/ ; https://computergraphics.stackexchange.com/ | ✅ — batch 20 |
| 10.5 | [x] CFD-Online / CFDSupport forums — CFD users see lots of bad CAD | https://www.cfd-online.com/Forums/ | ✅ — batch 22 (CFD short-edge / sliver clusters) |
| 10.6 | [x] quaoar.su blog (Sergey Slyadnev, OCCT contributor) — focused on healing edge cases ("Concatenate pcurves" etc.) | https://quaoar.su/blog/ | ✅ — batch 13 (B-series) |
| 10.7 | [x] Analysis Situs — open-source OCCT-based inspector; surfaces issues visually | https://analysissitus.org/ | ✅ — batch 13 |
| 10.8 | [x] GitHub global search — `is:issue STEP import`, `is:issue ShapeFix`, `is:issue CONFIG_CONTROL_DESIGN` | https://github.com/search?type=issues | ✅ — batches 18, 20 |

---

## 11. Other Angles Worth Mining

| # | Angle | Why useful |
|---|---|---|
| 11.1 | [x] **Fuzzers and CI corpora** — OSS-Fuzz has had STEP-related fuzz targets; oss-fuzz issue tracker may contain crashes for STEP parsers. | https://google.github.io/oss-fuzz/ ; bug tracker. Crashes are often minimal Part-21 files showing parser invariants. ✅ — batch 12 (A-series) |
| 11.2 | [x] **CVE database** — CVEs filed against STEP parsers (in CAD viewers, eDrawings, etc.) often include description and PoC characteristics. | https://www.cvedetails.com/ ; https://nvd.nist.gov/ — search "STEP" + CAD vendor names. ✅ — batch 12 |
| 11.3 | [x] **Patent literature** — patents on STEP/IGES translation describe failure modes their invention "solves" (especially Spatial, Theorem, ITI patents). | Google Patents for `(STEP OR IGES) AND (heal OR repair OR translation)` and assignees. ✅ — batch 21 (X-series) |
| 11.4 | [~] **PR / commit messages mentioning STEP fixes across CAD-adjacent repos** — beyond OCCT itself, repos like FreeCAD, gmsh, SALOME, BRL-CAD, Open Cascade-CE forks. Search `git log --grep="STEP"` and PR titles. | gh CLI, git log on each. ✅ — batch 08 covers OCCT git log; FreeCAD/gmsh/SALOME/BRL-CAD git logs only spot-mined via batches 14 and 22 |
| 11.5 | [x] **Test-suite test names as taxonomy** — every conformance suite (CAx-IF, NIST, OCCT `tests/`) names its tests after the defect or feature; test names alone form a taxonomy. | scrape names with `find tests -type f` etc. ✅ — batch 03 (OCCT tests/heal, tests/de_step, tests/bugs/step) |
| 11.6 | [~] **Round-trip diffs across translators** — public benchmarks where File A is exported by N tools and re-imported by M tools, with the cells flagged red. CAESAR matrices and prostep benchmarks publish these. | https://www.mbx-if.org/ ; https://www.prostep.org/ . ✅ — batches 02, 17 cite the framework; raw round-trip matrices not extracted entry-by-entry (locked behind member portals) |
| 11.7 | [~] **Bug bounty / responsible disclosure write-ups** — companies that publish PoC details for parser bugs (e.g., Talos / Cisco for SolidWorks/eDrawings). | https://talosintelligence.com/vulnerability_reports . 🟡 — batch 12 cites Talos/ZDI advisories generically; specific Cisco Talos write-ups for SolidWorks/eDrawings only sampled |
| 11.8 | [x] **Vendor "preferred export options" guides** — vendors publish guides like "When exporting STEP from SolidWorks, choose options X/Y to avoid Z" — these *imply* the failure modes of the non-recommended options. | vendor knowledge bases. ✅ — batches 10, 11, 14 |
| 11.9 | [~] **Re-implementations of OCCT in other languages** — there are partial Rust/Go/Zig STEP parsers; their TODO lists explicitly enumerate which Part 21 / AP cases they don't yet handle (and why). | search GitHub for `topic:step-file` and `topic:iso-10303`. ✅ — batch 14 covers BRL-CAD step-g; batch 07 STEPcode/IfcOpenShell. Partial Rust/Go/Zig STEP parsers were NOT separately enumerated |
| 11.10 | [~] **Slicer / 3D-printing toolchains** — PrusaSlicer, Cura, etc., have logs on weird mesh inputs derived from STEP→STL pipelines. Often surface unit-of-measure misinterpretations. | their issue trackers. ✅ — batch 22 covers OpenSCAD→FreeCAD pipelines; PrusaSlicer/Cura issue trackers not directly searched |
| 11.11 | [~] **Open-source viewers** — KiCad's 3D viewer, OCCT's CAD Assistant, FreeCAD's STEP examples folder (`examples/`), thingiverse-CAD-Assistant tickets. | various. ✅ — batches 18, 22 cover KiCad+FreeCAD; CAD Assistant Apple/Android store reviews / thingiverse tickets not mined |
| 11.12 | [⊘] **AP242 BOM XML companion files** — bugs at the XML/STEP boundary (e.g., references in XML dangling into the .stp). | prostep ivip references. 🟡 — partly via batch 02 (AP242 Domain Model XML Product & Assembly Structure v4.0); deeper XML/STEP boundary bugs not separately mined |
| 11.13 | [x] **AP203 vs AP214 vs AP242 migration whitepapers** — typically structured as "if you do X under AP203 you must change to Y under AP242" — the cross-walk implies the pitfalls. | Capvidia, prostep, NIST whitepapers. ✅ — batches 11 (Capvidia), 17 (prostep) |

---

## 12. Problem Categories To Look For (taxonomy)

The taxonomy serves two purposes: (a) when scanning a source above, it tells us which buckets to drop findings into; (b) when reviewing the catalog later, it ensures we have coverage breadth.

### 12.1 File-format / lexical / syntax (Part 21)

- **Encoding chaos.** ISO-8859-1 vs ASCII vs UTF-8 (Edition 3); `\X\`, `\X2\`, `\X4\` control directives; raw high-bit bytes; BOM; mixed line endings (CR / LF / CRLF). pythonocc-core #1278 (umlaut crash) is a concrete instance.
- **Comments and whitespace.** Nested-looking `/* */`, comments inside parameter lists, comments between header and `DATA;`, very long comments, comments containing `'` or `;`.
- **Instance numbering.** Out-of-order, sparse, very large (close to 2^63), zero or negative (illegal but seen), reused after `DELETE`, gaps that crash naive parsers.
- **String literals.** Embedded apostrophes (`''` escape), embedded backslashes, very long strings, multi-line continuation.
- **Numeric literal edge cases.** Excess precision, non-IEEE exotic forms, missing decimal point, `D`-exponent (Fortran-style) seen in old exporters, `-0.0`, denormals, infinities/NaNs sneaking in via tools that don't sanitize.
- **Header section.** Multiple `FILE_DESCRIPTION` lines, empty `FILE_NAME` fields, malformed timestamps, schema names that don't match the actual schema used (e.g., file claims AP203 but uses AP214 entities).
- **Multi-section files (Edition 3).** Anchor/Reference/Signature sections; multiple `DATA` sections with population scoping; few parsers handle these.
- **Unknown / typed / untyped attributes.** `*` (omitted), `$` (null), derived attributes, complex entity instances with multiple subtypes (`( A() B() C() )`).
- **EXPRESS schema mismatches.** File declares `CONFIG_CONTROL_DESIGN` but uses `AUTOMOTIVE_DESIGN` entities (FreeCAD #15685); mixing AP214 GD&T entities into AP203; private extensions (AP242 ED2 vs ED3 vs ED4).
- **Truncated, concatenated, or over-trimmed files.** Truncated downloads; two STEP files glued together; extra trailing data after `END-ISO-10303-21;`; missing END marker.

### 12.2 Geometric representation

- **Degenerate primitives.** Zero-length edges, zero-area faces, slivers, edges shorter than tolerance, points-coincident-but-not-identical.
- **Self-intersecting wires/surfaces.** Wires crossing themselves; trimmed surfaces with self-intersecting trim curves; non-simple parametric loops.
- **Pcurve issues.** Missing pcurves (often by export choice; some tools omit pcurves to shrink files); pcurve disagreement with 3D curve beyond SameParameter tolerance; long pcurves on cylinders/cones/revolutions; seam edges not flagged as such; pcurve direction reversed.
- **Knot vector pathologies.** Zero-length knot spans, repeated knots beyond multiplicity = degree+1, near-equal but not equal knots, normalized vs unnormalized.
- **NURBS rationality issues.** Zero or negative weights; weights drifting from 1.0 in supposedly-non-rational surfaces.
- **Surface degeneracies.** Cone with apex inside face range, sphere/torus seam ambiguities, degenerate toroidal surfaces (OCCT 0033620).
- **Curve discontinuities.** C0-only joins where C1 expected; analytic curves (line, circle) approximated as splines and back, losing exactness.

### 12.3 Topology

- **Open shells masquerading as solids** (and vice versa).
- **Inconsistent face orientation.** Some faces flipped within a shell.
- **Non-manifold edges/vertices.** Three or more faces sharing an edge.
- **Missing or incorrect edge-face sharing.** Edges that should be shared aren't (gap), or are shared with wrong orientation.
- **Vertex tolerance balls overlapping or not closing gaps.** OCCT increases vertex tolerance up to MaxTolerance() to bridge; files relying on this are fragile.
- **Loops that don't close.** Trailing-vertex != leading-vertex within tolerance.
- **Inner loops outside outer loops** (parameter space).
- **Wrongly-oriented inner wires** (CW where CCW expected).
- **Empty shells, empty solids, empty assemblies** (FreeCAD #16292).

### 12.4 Tolerance & numerical precision

- **Tolerance hierarchy violations.** vertex < edge < face is the OCCT invariant; violators trigger SameParameter recomputation.
- **Mixed working precisions.** File made by software in inches stored as mm yields tiny relative tolerances on small features.
- **Floating-point accumulation.** Boolean cascade producing self-intersections after re-export.
- **Coordinate-system origin offsets.** Models placed millions of units from origin lose precision.

### 12.5 Units & coordinate systems

- **Wrong unit declarations.** mm reported, in actual; meters internal but mm declared (Onshape→NX). PrePoMax, ViaCAD bugs documented.
- **Unit-and-scale mismatch on assemblies.** Sub-assembly in different unit than parent.
- **Multiple `LENGTH_UNIT`s / inconsistent `CONVERSION_BASED_UNIT`.**
- **Plane-angle units in radians vs degrees confusion.**

### 12.6 Assembly hierarchy

- **Duplicated component instances at same transform** (CATIA bug; multiple instances flattened to same location).
- **External references.** AP242 external references to other STEP files: missing files, circular references, version mismatches.
- **Lost assembly structure on round-trip** (BREP-only intermediate flattens it).
- **Nested PRODUCT_DEFINITION cycles.**
- **Naming collisions / non-unique part names; characters in names that break downstream tools.**
- **Color/layer attribution.** Colors at face vs body level; `styled_item` vs `presentation_layer_assignment` conflicts.

### 12.7 PMI / GD&T (AP214 / AP242)

- **Semantic vs graphic PMI mismatch.** Annotation rendered visually but no semantic meaning, or vice versa.
- **Lost references on round trip.** Datum references attached to features that don't exist after export (Creo <9.0 issue).
- **Tolerance zone shape misinterpretation.** Cylindrical vs spherical zones.
- **Modifier flags lost.** Free-state, projected tolerance zone, between-symbol.
- **Composite tolerance frames flattened.**
- **Annotation-plane orientation flipped on import.**

### 12.8 Mixed / auxiliary data

- **Tessellation mixed with B-rep (AP242).** SolidWorks doesn't read tessellated 242; mixing both confuses many readers.
- **Mesh-vs-BREP confusion.** STL-to-STEP converters that wrap a mesh as a degenerate B-rep with thousands of tiny planar facets.
- **Validation properties present but wrong** (computed surface area / volume / centroid disagreeing with geometry).
- **Embedded raster textures, materials, attributes.** Often dropped silently.
- **Kinematics (AP242 ED2).** Joints, constraints — round-tripped poorly.
- **Composite materials / piping / electrical harness extensions.** AP242 sub-domains with very thin implementor support.

### 12.9 Sender-specific idioms ("known bad exporters")

Tag every catalog entry with the senders/receivers involved. Useful sender categories:

- **Legacy Pro/E 2000i, Wildfire 2/3, Creo 1.0**: pre-AP242, often produces enormous files with many tiny faces; sometimes exports curves in `B_SPLINE_CURVE_WITH_KNOTS` instead of analytics where analytics exist.
- **CATIA V4 vs V5 vs V6**: V4 vintage often emits IGES-flavored conventions even in STEP; V5 has the duplicate-instance issue; CATIA names via `APPLICATION_PROTOCOL` set V6-isms.
- **SolidWorks**: STEP 242 tessellation refusal; large-assembly export crashes; Surfaces vs Solids ambiguity.
- **Inventor**: millimeter-as-microns bug to SolidWorks.
- **NX / Solid Edge**: generally good; idiosyncratic in PMI placement.
- **AutoCAD 3D / Plant 3D**: wrong unit declaration.
- **Fusion 360**: known to hang FreeCAD (#6311); produces files SolidWorks corrupts on import.
- **Onshape**: meters-internal unit oddity; revolve-360° topology bugs.
- **SpaceClaim**: HOOPS-Exchange version dependent; regressions visible across 25R2.
- **Rhino**: exports inch-as-mm in AP203 path.
- **TinkerCAD / cloud STL→STEP converters**: pseudo-B-rep wrapping.
- **KiCad**: board STEP with many same-named instances at different transforms.
- **FreeCAD / OCCT-based tools generally**: "by-product" of OCCT idioms (specific ways `SameParameter` is enforced, etc.).
- **OpenSCAD-to-STEP via FreeCAD pipeline**: fragile B-reps from CSG approximations.
- **GIS / BIM tools (Revit, ArchiCAD via IFC→STEP)**: different scale, non-standard schemas.

### 12.10 Scale & performance edge cases

- **Very large files** (>1 GB; FreeCAD #18735 — minutes to hours to import).
- **Many entities with deep dependency graphs** (combinatorial reference resolution).
- **Pathological B-rep** (millions of tiny faces from converted mesh).
- **Cyclic reference graphs.**
- **Files needing many passes of healing** (where one fix exposes another defect).

### 12.11 Adversarial / fuzz inputs

- **Malformed-on-purpose** (security): unbalanced parens, infinite recursion via reference cycles, gigantic numbers.
- **Truncated files** (download errors).
- **Concatenated files** (two STEP files glued together via copy-paste).
- **Files with extra trailing data after `END-ISO-10303-21;`.**
- **Files with the END marker missing.**

---

## 13. Suggested Workflow

Given the user's focus on test-first / verify-first development, a productive order is:

1. **Section 0 first.** OCCT's `src/ShapeFix/`, `src/ShapeAnalysis/`, `src/STEPControl/`, `src/RWStep*`, and `tests/` is the single densest source. Build a problem table directly from class names and `tests/heal/*` test names.
2. **Cross-reference with CAx-IF Recommended Practices (§3.2).** These are *intended* problems — what implementors agreed to handle uniformly.
3. **Mine FreeCAD + OCCT issue trackers (§1, §2)** filtered by `STEP` label for *real-world* problems with attached files (or detailed descriptions you can synthesize).
4. **Use NIST SFA's report categories (§3.6) as a checklist** of validation properties.
5. **Walk vendor-KB tables (§5, §6)** for sender-specific idioms.
6. **Hold ABC dataset (§7.1) in reserve** as a corpus to actually exercise each problem class on once the kernel is partially functional.

Ideally each catalog entry records: (a) description, (b) sender, (c) failing receiver(s), (d) minimal reproducer recipe, (e) expected behavior (accept / reject-with-error-X / heal-to-Y).

---

## 14. Verification Status Summary

- **✅ Verified** entries: bulk of the table; URLs / repos / issue numbers / paper titles confirmed in research.
- **🟡 Probably exists**: e.g., FreeCAD Discord (exists, get current invite), KiCad MCAD STEP issue patterns (happens but not centrally tracked), Talos write-ups for STEP parsers (varies by year).
- **⚠️ Needs checking**: closed-source kernels' KBs (5.x family generally), CC3D / Furniture-A dataset names, older textbook citations (Mortenson, Pratt). Verify edition + chapters before citing.
