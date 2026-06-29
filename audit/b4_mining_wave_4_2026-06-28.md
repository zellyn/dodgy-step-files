# B4 Mining Wave-4 Audit — 2026-06-28

## Background

B4 waves 1-3 mined FOSS issue trackers (OCCT/FreeCAD/OCE/CadQuery/KiCad/Blender-addon)
and achieved declining novelty: 24.6% → 10.5% → 9.3%. The wave-4 directive is to pivot
to commercial-tracker bug-fix changelogs and cross-vendor sources before FOSS saturation
kills the signal.

---

## Sources Chosen

| # | Source | Why chosen |
|---|--------|-----------|
| 1 | **HOOPS Exchange fixed-bugs list** (TechSoft3D, 2023–2024) | Public-facing commercial CAD translation kernel; independent codebase from OCCT; likely to surface different defect classes | URL: https://docs.techsoft3d.com/exchange/2023_SP2_U1/fixed_bugs.html and https://docs.techsoft3d.com/exchange/2024/fixed_bugs.html |
| 2 | **Autodesk Inventor release notes / community forum** (2023–2025) | High-volume commercial STEP producer; known PMI-path differences from OCCT | URLs: https://help.autodesk.com/view/INVNTOR/2024/ENU/?guid=Inventor_ReleaseNotes_release_notes_fixed_defects_2024_html ; https://forums.autodesk.com/t5/inventor-forum/pmi-annotation-in-step-file/td-p/11966663 |
| 3 | **OCCT GitHub issues + dev forum** (2023–2026) | Tracker itself; surfacing issues not yet in our corpus that appeared after previous waves | URLs: https://github.com/Open-Cascade-SAS/OCCT/issues ; https://dev.opencascade.org/content/ |
| 4 | **Rhino/McNeel discourse + PTC Creo community** | Mid-tier commercial importers with distinct tolerance / entity-handling pipelines | URLs: https://discourse.mcneel.com/t/step-import-issue-conical-surface-interpreted-as-a-circle/219575 ; https://community.ptc.com/t5/Data-Exchange/Problem-importing-STEP/td-p/100900 |
| 5 | **Academic / "Better STEP" arxiv paper** (2025–2026) | Recent empirical study of OCCT mesh failures across 1M+ B-rep dataset; different angle from bug trackers | URL: https://arxiv.org/html/2506.05417 |

Sources attempted but inaccessible / no STEP content:
- Siemens NX "What's New" pages: no public bug-level detail; only marketing summaries
- Solid Edge 2024/2025 blog posts: no STEP-specific geometry fixes listed
- PTC Creo support articles: CS10021 returned 403; most content paywalled
- Autodesk Inventor 2024 fixed-defects page: rendered "Help" only (JavaScript gated)

---

## Defect Catalog (35 defects)

Format per entry:
- **Pattern** (input-phrasing per catalog convention)
- **Entities** — primary STEP entity types
- **User-visible defect** — what goes wrong
- **Source**
- **Top BM25 matches** — top-3 with scores; "HIT" if score ≥ 20 on rank-1 and semantics match, "NEAR-MISS" if partial match, "NOVEL" if no close match

---

### D01 — OFFSET_SURFACE of B-spline base not rendered

**Pattern:** STEP file with an `OFFSET_SURFACE` entity referencing a `B_SPLINE_SURFACE` as its base, used as the geometry argument of an `ADVANCED_FACE`, where the offset distance is non-zero.

**Entities:** `OFFSET_SURFACE`, `B_SPLINE_SURFACE`, `ADVANCED_FACE`

**Defect:** Face fails to parse or does not display; removing the OFFSET_SURFACE layer and directly referencing the spline fixes it (OCCT 7.9, GitHub #994).

**Source:** https://github.com/Open-Cascade-SAS/OCCT/issues/994

**BM25 top-3:**
1. Gn021 [49.45] — OFFSET_SURFACE of complex BSpline base fails parsing only when wrapped
2. Tfa026 [38.88] — OFFSET_SURFACE used (out of AP214 scope)
3. N019 [26.53] — OFFSET_SURFACE with sub-tolerance offset

**Novel?** NO — Gn021 is a direct semantic match (score 49.45). **HIT.**

---

### D02 — SHAPE_DEFINITION_REPRESENTATION with SHAPE_ASPECT definition causes null-pointer crash

**Pattern:** STEP file where a `SHAPE_DEFINITION_REPRESENTATION` entity's Definition slot points to a `SHAPE_ASPECT` (valid in AP214 CATIA V6 Fast Export) rather than the expected `PROPERTY_DEFINITION`.

**Entities:** `SHAPE_DEFINITION_REPRESENTATION`, `SHAPE_ASPECT`, `PROPERTY_DEFINITION`

**Defect:** Null pointer dereference in `CheckSRRReversesNAUO()` → SIGSEGV. Reproduced with 1,088/1,267 SDR entities in a 430 MB CATIA V6 file.

**Source:** https://github.com/Open-Cascade-SAS/OCCT/issues/1202

**BM25 top-3:**
1. A034 [58.01] — CheckSRRReversesNAUO segfault on SDR with SHAPE_ASPECT instead of PROPERTY_DEFINITION
2. Pmi125 [26.76]
3. Pmi034 [24.04]

**Novel?** NO — A034 is an exact match. **HIT.**

---

### D03 — COMPOUND_REPRESENTATION_ITEM with SET_REPRESENTATION_ITEM sub-elements not parseable

**Pattern:** STEP file containing `COMPOUND_REPRESENTATION_ITEM` whose `item_element` is a `SET_REPRESENTATION_ITEM` wrapping `DESCRIPTIVE_REPRESENTATION_ITEM` children; calling `ItemElementValue(n)` returns null despite `NbItemElement() > 0`.

**Entities:** `COMPOUND_REPRESENTATION_ITEM`, `SET_REPRESENTATION_ITEM`, `DESCRIPTIVE_REPRESENTATION_ITEM`

**Defect:** PMI data silently missing; compound items partially populated; affects AP242 dimensional note extraction.

**Source:** https://github.com/Open-Cascade-SAS/OCCT/issues/1283 (nist_ctc_05_asme1_ap242-e1.stp test case)

**BM25 top-3:**
1. A020 [27.70] — Bare STYLED_ITEM at top level
2. M040 [25.20] — STYLED_ITEM.item NULL
3. Ad043 [18.81]

**Novel?** YES — No existing fixture captures the compound-representation-item null-child pattern. Top score 27.70 on a loosely related entry. **NOVEL.**

---

### D04 — ORIENTED_EDGE circular reference causes stack overflow

**Pattern:** STEP file where `ORIENTED_EDGE` entities form a mutual reference cycle (`EdgeStart()` calls `EdgeEnd()` which calls `EdgeStart()` again), combined with unresolved references and syntax errors in the body section.

**Entities:** `ORIENTED_EDGE`, `EDGE_CURVE`

**Defect:** Stack overflow / application crash on import; potential denial-of-service in embedded importers (PrusaSlicer 2.6.1, OCCT 7.x).

**Source:** https://github.com/prusa3d/PrusaSlicer/issues/11305

**BM25 top-3:**
1. Tfa063 [32.64] — Stack overflow on RemoveSmallFaces due to unbounded recursion
2. N124 [30.96] — ShapeFix_ShapeTolerance.SetTolerance recursion-stack-overflow
3. Pf009 [24.28] — Stack overflow when meshing with TBB pool

**Novel?** NEAR-MISS — Ad004 (cyclic complex-entity reference graph, score 23.74) captures the recursive-reference archetype. The specific ORIENTED_EDGE ↔ EdgeStart/EdgeEnd cycle is a distinct mechanism. Score for most relevant is 23.74 with different entity class. **NOVEL** (distinct input pattern: malformed EdgeStart/EdgeEnd back-reference, not a general entity graph cycle).

---

### D05 — STEPCAFControl_Reader regression fails on files STEPControl_Reader handles

**Pattern:** STEP file that `STEPControl_Reader` translates successfully but `STEPCAFControl_Reader` fails to load (regression in OCCT 7.8.0 attributes-reading path).

**Entities:** Entire file; failure in attribute-reading layer above geometry

**Defect:** File silently not transferred when using the XCAF-aware reader; no geometry in resulting document.

**Source:** https://dev.opencascade.org/content/occt-780-fails-read-step-file-stepcontrolreader-works-stepcafcontrolreader-doesnt (OCCT bug 0033631)

**BM25 top-3:**
1. A097 [29.50] — Error transferring .stp model from STEPCAFControl_Reader
2. Xp036 [23.46] — STYLED_ITEM colours dropped by bare STEPControl_Reader
3. Tsh022 [19.55]

**Novel?** NO — A097 matches the STEPCAFControl_Reader transfer-failure archetype directly (score 29.50). **HIT.**

---

### D06 — TORUS_SURFACE mesh distorted or broken in body-object rendering

**Pattern:** STEP file containing one or more `TORUS_SURFACE` (or partial-torus) `ADVANCED_FACE` entities, where the body's mesh generation over-splits the surface into 4-face segments instead of the expected 1-face representation.

**Entities:** `TORUS_SURFACE`, `ADVANCED_FACE`, `CLOSED_SHELL`

**Defect:** Tessellation shows visible distortion artifacts compared to older importer versions; CAM/visualization workflows fail.

**Source:** https://forums.autodesk.com/t5/3ds-max-design-visualization/stp-step-import-now-has-problems-in-2024/td-p/11903372

**BM25 top-3:**
1. Tsh008 [15.31] — Mis-oriented faces in shell
2. Me353 [13.13]
3. A102 [12.48]

**Novel?** YES — Top score 15.31 on a loosely related mesh-orientation entry. No existing fixture captures the TORUS_SURFACE over-segmentation / mesh-distortion defect during import. **NOVEL.**

---

### D07 — CONICAL_SURFACE EDGE_LOOP trimming produces only base circle, lateral face missing

**Pattern:** STEP file with a `CLOSED_SHELL` containing a `CONICAL_SURFACE` `ADVANCED_FACE` whose `EDGE_LOOP` trim geometry is malformed (incorrectly truncated ~0.15 mm above the base), causing the lateral cone face to be absent on import.

**Entities:** `CONICAL_SURFACE`, `ADVANCED_FACE`, `EDGE_LOOP`, `FACE_OUTER_BOUND`, `AXIS2_PLACEMENT_3D`

**Defect:** Cone imports as a flat disk (base circle only); SolidWorks rejects file outright; Rhino shows only circle geometry. Rhino ticket RH-96071.

**Source:** https://discourse.mcneel.com/t/step-import-issue-conical-surface-interpreted-as-a-circle/219575

**BM25 top-3:**
1. Ps012 [27.83] — Sweep silently truncated to a CONICAL_SURFACE
2. Tfa064 [20.61] — Missing-seam reconstruction fails on ADVANCED_FACE on CYLINDRICAL_SURFACE
3. Xp028 [19.58] — Onshape imports as one Surface

**Novel?** NEAR-MISS — Ps012 concerns sweep-truncation, not EDGE_LOOP miscut on cone face. None of the top-3 capture the "CONICAL_SURFACE lateral face entirely absent due to bad EDGE_LOOP trim vertex" pattern. **NOVEL** (distinct: malformed trim kills the lateral surface while leaving the base-cap, unrelated to seam issues).

---

### D08 — COLOUR_RGB values shifted by sRGB-to-linear conversion on export

**Pattern:** STEP file produced by CadQuery or similar OCCT-backed exporter where `COLOUR_RGB` numeric values are gamma-encoded (sRGB → linear transform applied) rather than stored as raw sRGB, e.g. 0.5 → 0.7354.

**Entities:** `COLOUR_RGB`, `STYLED_ITEM`, `PRESENTATION_STYLE_ASSIGNMENT`

**Defect:** Colors differ from design intent; FreeCAD ignores the gamma-shifted colors; validation against reference STEP files fails.

**Source:** https://github.com/CadQuery/cadquery/issues/794

**BM25 top-3:**
1. Wr061 [64.93] — X11 'aliceblue' colour shifted by sRGB→linear conversion on emit
2. Xp034 [60.57] — CadQuery RGB shifted by sRGB→linear conversion on STEP export
3. Xp035 [26.55] — CadQuery STEP writer emits redundant COLOUR_RGB entities

**Novel?** NO — Xp034 is an exact match (score 60.57, same bug). **HIT.**

---

### D09 — GEOMETRIC_TOLERANCE magnitude null handle (OCCT StepDimTol_GeometricTolerance.Magnitude)

**Pattern:** STEP AP242 file (from Siemens NX or NIST) where `GEOMETRIC_TOLERANCE` magnitude is encoded via `MEASURE_REPRESENTATION_ITEM` through an alternate structural path rather than the direct relationship OCCT's writer produces, causing `Magnitude()` to return a null handle.

**Entities:** `GEOMETRIC_TOLERANCE`, `MEASURE_REPRESENTATION_ITEM`, `DESCRIPTIVE_REPRESENTATION_ITEM`

**Defect:** Tolerance numerical value and unit not extractable; only type, name, description, and datum references are read.

**Source:** https://dev.opencascade.org/content/issue-reading-geometric-tolerance-values-nxnist-generated-step-ap242-files-occt-79

**BM25 top-3:**
1. In011 [16.63] — Reader exception swallowed (entity bound to null) when B_SPLINE control points use extreme coords
2. A020 [13.53]
3. Ls008 [12.84]

**Novel?** YES — Top score 16.63 on an unrelated entity-binding issue. No existing fixture covers the geometric-tolerance magnitude null-handle pattern where the value is reached via MEASURE_REPRESENTATION_ITEM indirect chain. **NOVEL.**

---

### D10 — TESSELLATED_ANNOTATION_OCCURRENCE PMI annotations not machine-readable as text

**Pattern:** STEP AP242 file (from Autodesk Inventor 2023+ when legacy parts are used as sub-assembly components) where PMI leader-text annotations are encoded as `TESSELLATED_ANNOTATION_OCCURRENCE` tessellation geometry instead of `DESCRIPTIVE_REPRESENTATION_ITEM` semantic text.

**Entities:** `TESSELLATED_ANNOTATION_OCCURRENCE`, `DESCRIPTIVE_REPRESENTATION_ITEM`, `DRAUGHTING_ANNOTATION_OCCURRENCE`

**Defect:** Annotation text cannot be extracted programmatically; visual rendering still works but machine-readable PMI parsing yields no string content.

**Source:** https://forums.autodesk.com/t5/inventor-forum/pmi-annotation-in-step-file/td-p/11966663

**BM25 top-3:**
1. Pmi042 [34.19] — Empty semantic-text string in PMI
2. Pmi045 [28.81] — Graphic-only PMI with no semantic backing
3. Pmi005 [23.65] — Mixing Polyline and Tessellated PMI presentation

**Novel?** NO — Pmi045 "Graphic-only PMI with no semantic backing" captures the essential pattern (score 28.81). The Inventor version-triggered regression is a new root cause, but the input pattern is identical to Pmi045. **HIT.**

---

### D11 — RATIONAL_B_SPLINE weights silently collapsed to 1.0 during assignment

**Pattern:** STEP file with a `RATIONAL_B_SPLINE_SURFACE` (or curve) entity where weights assigned iteratively pass through a transient state where all assigned weights are momentarily equal, causing OCCT to convert the surface to non-rational form (weights → 1.0) and overwrite remaining pending weights.

**Entities:** `RATIONAL_B_SPLINE_SURFACE`, `B_SPLINE_SURFACE_WITH_KNOTS`

**Defect:** Wrong weights stored in loaded geometry; shape is non-rational when it should be rational; subtle silhouette/curvature errors.

**Source:** https://github.com/FreeCAD/FreeCAD/issues/20718 (OCCT defect, FreeCAD workaround)

**BM25 top-3:**
1. Gn035 [51.30] — Circle translated to NURBS form with rational weights but missing weight metadata
2. Xp005 [41.63] — NURBS knot vector × control-point weight × tolerance-boundary cusp
3. Gn134 [41.41] — NURBS weight array uniform propagation

**Novel?** NO — Gn134 [41.41] "NURBS weight array uniform propagation" captures the weight-uniformization defect. **HIT.**

---

### D12 — STEP assembly import produces SHELL_BASED_SURFACE_MODEL instead of MANIFOLD_SOLID_BREP

**Pattern:** STEP file representing an assembly where the producer emitted `SHELL_BASED_SURFACE_MODEL` topology (non-closed shells) instead of `MANIFOLD_SOLID_BREP`, causing the importing system to produce open surfaces rather than solid bodies.

**Entities:** `SHELL_BASED_SURFACE_MODEL`, `OPEN_SHELL`, `MANIFOLD_SOLID_BREP`

**Defect:** Parts load as surfaces (sheets) rather than solids; downstream FEA / CNC operations fail; Inventor handles the file correctly while Creo does not.

**Source:** https://community.ptc.com/t5/Data-Exchange/Problem-importing-STEP/td-p/100900

**BM25 top-3:**
1. Xp028 [27.99] — Onshape imports as one Surface — missing face yields OPEN_SHELL
2. Tsh004 [23.29] — Sheet bodies imported in place of solids
3. P015 [19.50] — Non-manifold or open shell exported as MANIFOLD_SOLID_BREP

**Novel?** NO — Tsh004 [23.29] captures the sheet-body/solid demotion pattern directly. **HIT.**

---

### D13 — NX AP242 PMI DIMENSIONAL_LOCATION with unresolved entity reference

**Pattern:** STEP AP242 file exported by NX where `DIMENSIONAL_LOCATION` entity's `shape_aspect_relationship.related_shape_aspect` parameter is not resolvable (reported as "not an Entity" by OCCT parser), alongside `GEOMETRIC_ITEM_SPECIFIC_USAGE` and `REPRESENTATION_MAP` reference failures.

**Entities:** `DIMENSIONAL_LOCATION`, `SHAPE_ASPECT_RELATIONSHIP`, `GEOMETRIC_ITEM_SPECIFIC_USAGE`, `REPRESENTATION_MAP`

**Defect:** PMI dimensional relationships cannot be read; GD&T data silently missing even though geometry loads correctly.

**Source:** https://dev.opencascade.org/content/cant-read-pmi-step-exported-ug

**BM25 top-3:**
1. Pmi125 [31.05] — LOCATING_FEATURE referencing non-existent shape aspect (dangling target)
2. Pmi012 [29.33] — Identical id_attribute reused across shape_aspect / dimensional_location
3. Pmi094 [26.12] — XCAF GD&T data does not round-trip to STEP AP242 PMI

**Novel?** NO — Pmi125 (dangling shape-aspect target) and Pmi012 (id_attribute confusion) together cover the pattern. **HIT.**

---

### D14 — HOOPS Exchange: incorrect UV curves on spherical face from STEP (SDHE-12051)

**Pattern:** STEP file with an `ADVANCED_FACE` on a `SPHERICAL_SURFACE` where the `PCURVE` / parameter-space curve description is inconsistent with the sphere's natural parametrization, causing UV curve errors in the exchange kernel.

**Entities:** `ADVANCED_FACE`, `SPHERICAL_SURFACE`, `PCURVE`, `EDGE_CURVE`

**Defect:** UV curves in converted model are geometrically incorrect; downstream tessellation and surface evaluation produce artifacts.

**Source:** https://docs.techsoft3d.com/exchange/2023_SP2_U1/fixed_bugs.html (SDHE-12051)

**BM25 top-3:**
1. Twi022 [21.83] — Seam edge with swapped or duplicated pcurves on periodic face
2. Gp027 [21.23] — Closed-face splitter leaves new pcurves out of sync with 3D curves on CYLINDRICAL_SURFACE
3. Gp023 [19.81] — Point-projection onto trimmed periodic CYLINDRICAL_SURFACE returns UV outside trimmed domain

**Novel?** NEAR-MISS — Our catalog has many pcurve/UV-domain fixtures but none specifically targeting `SPHERICAL_SURFACE` pcurve inconsistency on HOOPS Exchange. Gp027 is closest but is about cylindrical seams. Score 21.83, different surface type. **NOVEL** (SPHERICAL_SURFACE-specific pcurve domain mismatch is distinct from the cylindrical/periodic variants in corpus).

---

### D15 — HOOPS Exchange: incorrect face orientation on STEP read (SDHE-12295 / SDHE-35944)

**Pattern:** STEP file where the `same_sense` flag on one or more `ADVANCED_FACE` entities, combined with the winding of the `FACE_OUTER_BOUND` wire, produces an outward-normal direction that contradicts the shell volume convention, requiring the exchange kernel to flip orientation.

**Entities:** `ADVANCED_FACE`, `FACE_OUTER_BOUND`, `CLOSED_SHELL`

**Defect:** Face normals inverted relative to expected; shading is inside-out; downstream CAM / FEA detects reversed faces.

**Source:** https://docs.techsoft3d.com/exchange/2023_SP2_U1/fixed_bugs.html (SDHE-12295, SDHE-35944)

**BM25 top-3:**
1. Tsh010 [40.55] — Reversed face normal in closed shell ("inside-out" shading)
2. Tfa057 [40.45] — Face wire's orientation contradicts the outer/inner role
3. Ps003 [34.98] — Single ADVANCED_FACE with same_sense flipped on outer skin

**Novel?** NO — Tsh010 and Ps003 are direct hits. **HIT.**

---

### D16 — HOOPS Exchange: wrong UV curve after splitting STEP file (SDHE-18541 / SDHE-18530)

**Pattern:** STEP file with multi-body content where the HOOPS Exchange split operation introduces incorrect UV (pcurve) representations on the resulting `ADVANCED_FACE` entities, because the splitter recomputes pcurves without accounting for the original surface parametrization.

**Entities:** `ADVANCED_FACE`, `PCURVE`, `EDGE_CURVE`

**Defect:** After STEP split/partition operation, newly created faces have mismatched pcurves; tessellation artifacts and surface evaluation failures.

**Source:** https://docs.techsoft3d.com/exchange/2023_SP2_U1/fixed_bugs.html (SDHE-18541, SDHE-18530)

**BM25 top-3:**
1. Twi022 [21.83] — Seam edge with swapped or duplicated pcurves on periodic face
2. Gp027 [21.23] — Cylindrical face pcurves out of sync
3. P014 [17.79] — PCURVE start point shifted in V

**Novel?** NO — The corpus has extensive pcurve-mismatch coverage. SDHE-18541 is a post-split UV error, architecturally different but the input-pattern description ("STEP file with mismatched pcurves on face") hits existing fixtures adequately. **HIT.**

---

### D17 — HOOPS Exchange: STEP file with tessellation causes import error (SDHE-20790)

**Pattern:** STEP AP242 file that contains `TESSELLATED_SHAPE_REPRESENTATION` alongside B-rep entities, where the exchange kernel encounters an error during flat tessellation generation of the `TRIANGULATED_FACE` / `COMPLEX_TRIANGULATED_FACE` entities.

**Entities:** `TESSELLATED_SHAPE_REPRESENTATION`, `TRIANGULATED_FACE`, `COMPLEX_TRIANGULATED_FACE`

**Defect:** Import fails with an error; pre-tessellated presentation not imported; geometry absent in converted result.

**Source:** https://docs.techsoft3d.com/exchange/2023_SP2_U1/fixed_bugs.html (SDHE-20790)

**BM25 top-3:**
1. M005 [28.24] — Number of facets validation property must include flat triangles dropped on import
2. M025 [27.91] — Tessellated geometry preserved on round-trip vs always recomputed
3. M056 [25.54] — Tessellation export missing or conflicting with B-rep representation

**Novel?** NO — M056 and M025 collectively cover the pre-tessellated representation import failure pattern. **HIT.**

---

### D18 — HOOPS Exchange: face colors not read from STEP (SDHE-18626 / SDHE-18841)

**Pattern:** STEP file where per-face `COLOUR_RGB` values are bound through `STYLED_ITEM` → `PRESENTATION_STYLE_ASSIGNMENT` → `SURFACE_STYLE_USAGE` → `SURFACE_STYLE_FILL_AREA` → `FILL_AREA_STYLE` → `FILL_AREA_STYLE_COLOUR` chain, and the exchange kernel fails to traverse the full chain resulting in default/no color.

**Entities:** `STYLED_ITEM`, `COLOUR_RGB`, `FILL_AREA_STYLE_COLOUR`

**Defect:** Faces import without color; visual inspection shows wrong default appearance; downstream rendering and review tools cannot distinguish face groups.

**Source:** https://docs.techsoft3d.com/exchange/2023_SP2_U1/fixed_bugs.html (SDHE-18626, SDHE-18841)

**BM25 top-3:**
1. A018 [40.82] — STYLED_ITEM at wrong scope: assembly-level color override lost or misbound
2. A020 [40.43] — Bare STYLED_ITEM at top level
3. A019 [39.15] — Per-face STYLED_ITEM colours collapse to single hue

**Novel?** NO — A018/A019/A020 collectively cover the color-chain traversal failures. **HIT.**

---

### D19 — HOOPS Exchange: NURBS faces incorrectly shrunk during STEP conversion (SDHE-37143)

**Pattern:** STEP file with `B_SPLINE_SURFACE_WITH_KNOTS` or `RATIONAL_B_SPLINE_SURFACE` faces where the HOOPS Exchange conversion to internal NURBS representation incorrectly shrinks the surface's active domain, producing faces that appear smaller than intended.

**Entities:** `B_SPLINE_SURFACE_WITH_KNOTS`, `RATIONAL_B_SPLINE_SURFACE`, `ADVANCED_FACE`

**Defect:** NURBS faces are geometrically undersized after conversion; dimensions are wrong; volume validation fails.

**Source:** https://docs.techsoft3d.com/exchange/2024/fixed_bugs.html (SDHE-37143)

**BM25 top-3:**
1. Gn021 [49.45] — OFFSET_SURFACE of complex BSpline base fails parsing
2. Xp005 [41.63] — NURBS knot × weight × tolerance-boundary cusp
3. Gn134 [41.41] — NURBS weight array uniform propagation

**Novel?** YES — The domain-shrinkage defect (trimmed parametric domain is clipped to a sub-interval) is distinct from offset-surface failures and weight issues. Top hit Gn021 is about OFFSET_SURFACE wrapping; no existing entry covers a NURBS domain-shrinkage / active-domain contraction during conversion. **NOVEL.**

---

### D20 — HOOPS Exchange: wrong faces upon reading STEP (SDHE-35602)

**Pattern:** STEP file where certain `ADVANCED_FACE` entries have their geometry replaced or corrupted during HOOPS Exchange internal face-conversion pass, producing incorrect face geometry in the output B-rep.

**Entities:** `ADVANCED_FACE`, `CLOSED_SHELL`, face surface geometry

**Defect:** Output model has geometrically wrong faces at specific positions; adjacent faces don't close up; gap or overlap visible in review.

**Source:** https://docs.techsoft3d.com/exchange/2024/fixed_bugs.html (SDHE-35602)

**BM25 top-3:**
1. Tsh230 [24.82] — Surface from STEP file wrongly imported / tessellated (self-intersecting NURBS net)
2. Tfa026 [21.16] — OFFSET_SURFACE used out of AP214 scope
3. M052 [21.03] — Open shell where closed solid expected

**Novel?** NEAR-MISS — The bug description is vague ("wrong faces"). Tsh230 captures wrong tessellation, not wrong face geometry in B-rep. Insufficient specificity to call it novel without more detail. **AMBIGUOUS — treat as HIT (not counted as novel) due to insufficient new information beyond existing corpus coverage.**

---

### D21 — HOOPS Exchange: STEP AP242 annotations TESSELLATED_ANNOTATION_OCCURRENCE incomplete metadata (SDHE-37128)

**Pattern:** STEP AP242 file where annotation metadata is carried exclusively via `TESSELLATED_ANNOTATION_OCCURRENCE` with no fallback to semantic `DESCRIPTIVE_REPRESENTATION_ITEM`, and the HOOPS Exchange metadata extraction code lacks a handler for this path.

**Entities:** `TESSELLATED_ANNOTATION_OCCURRENCE`, `DRAUGHTING_ANNOTATION_OCCURRENCE`, AP242 metadata chain

**Defect:** Annotation metadata incomplete in converted output; text content and tolerance values not accessible.

**Source:** https://docs.techsoft3d.com/exchange/2024/fixed_bugs.html (SDHE-37128)

**BM25 top-3:**
1. Pmi042 [34.19] — Empty semantic-text string in PMI
2. Pmi045 [28.81] — Graphic-only PMI with no semantic backing
3. M021 [20.25] — Tessellated GD&T entities not imported

**Novel?** NO — Pmi045 and M021 cover this directly. **HIT.**

---

### D22 — HOOPS Exchange: STEP export syntax error with tolerance values (SDHE-36507)

**Pattern:** STEP file produced by HOOPS Exchange's STEP writer containing `GEOMETRIC_TOLERANCE` entities where the tolerance value emitted has incorrect syntax (e.g., missing decimal point, wrong exponent format in `MEASURE_WITH_UNIT`).

**Entities:** `GEOMETRIC_TOLERANCE`, `MEASURE_WITH_UNIT`, STEP syntax

**Defect:** Downstream STEP parsers reject the exported file at lexical stage; tolerance data unusable.

**Source:** https://docs.techsoft3d.com/exchange/2024/fixed_bugs.html (SDHE-36507)

**BM25 top-3:**
1. Ls002 [varies] — REAL literal with no digit before decimal point
2. Ad049 [25.88] — Real literal lacks decimal point or has Fortran D exponent
3. Wr007 [varies] — Locale-sensitive decimal separator

**Novel?** NO — Ad049 and Ls002 cover malformed real literals in STEP. **HIT.**

---

### D23 — HOOPS Exchange: unattached annotation STEP export syntax error (SDHE-36465)

**Pattern:** STEP AP242 file produced by HOOPS Exchange containing `DRAUGHTING_ANNOTATION_OCCURRENCE` entities that are not attached to any `PRODUCT_DEFINITION_SHAPE` or model, resulting in a dangling annotation with incorrect STEP syntax that causes parse errors.

**Entities:** `DRAUGHTING_ANNOTATION_OCCURRENCE`, `ANNOTATION_OCCURRENCE`, AP242 annotation chain

**Defect:** Downstream parsers report syntax errors; unattached annotations corrupt the file structure.

**Source:** https://docs.techsoft3d.com/exchange/2024/fixed_bugs.html (SDHE-36465)

**BM25 top-3:**
1. Pmi042 [34.19] — Empty semantic-text string in PMI
2. Pmi045 [28.81] — Graphic-only PMI with no semantic backing
3. A020 [20.21] — Bare STYLED_ITEM at top level (no MDGPR parent)

**Novel?** YES — Unattached/orphan annotation occurrence causing a syntax error in the exported STEP is distinct from the semantic-empty and graphic-only patterns. The defect is in the writing path: an annotation entity emitted with no parent reference AND broken STEP syntax. No existing fixture covers "STEP file with a DRAUGHTING_ANNOTATION_OCCURRENCE not connected to any product context, emitted with a syntax error." **NOVEL.**

---

### D24 — STEP file B-rep parametric surface meshing fails (~5% of complex models)

**Pattern:** STEP file containing complex parametric surfaces (highly non-uniform NURBS, degenerate knot vectors, or poorly-conditioned B-spline patches) where OCCT's `BRepMesh_IncrementalMesh` fails to generate a mesh, returning empty triangulation for those faces.

**Entities:** `B_SPLINE_SURFACE_WITH_KNOTS`, `RATIONAL_B_SPLINE_SURFACE`, `ADVANCED_FACE`

**Defect:** Affected faces produce no triangle mesh; visualization shows holes; downstream analysis on surface normals fails. Empirically observed at ~5% rate across ABC dataset (arXiv 2506.05417), 8.82% in assembly datasets.

**Source:** https://arxiv.org/html/2506.05417 ("Better STEP" paper, 2026)

**BM25 top-3:**
1. Tfa026 [21.22] — OFFSET_SURFACE (loosely related)
2. M052 [21.16] — Open shell where closed solid expected
3. Tsh118 [20.68] — 5-face open box

**Novel?** YES — No existing fixture specifically targets the class of NURBS/parametric surface geometry that causes OCCT mesh generation to silently produce empty triangulation. The "Better STEP" dataset finding is empirical; the defect class is "STEP files whose parametric surface geometry (degenerate knot vectors, poor parametrization, extreme aspect ratios) defeats BRepMesh." **NOVEL.**

---

### D25 — STEP assembly component misplaced to origin (OCCT GetShapes vs GetFreeShapes)

**Pattern:** STEP file representing a multi-part assembly where components have `NEXT_ASSEMBLY_USAGE_OCCURENCE`-based placement transformations; using `GetShapes()` API retrieves the raw building blocks without their placement transforms, causing all parts to appear at (0,0,0).

**Entities:** `NEXT_ASSEMBLY_USAGE_OCCURENCE`, `CONTEXT_DEPENDENT_SHAPE_REPRESENTATION`, `AXIS2_PLACEMENT_3D`

**Defect:** Assembly components snap to the world origin instead of their designed positions; assembly hierarchy appears structurally correct but spatially wrong.

**Source:** https://dev.opencascade.org/content/import-step-export-mesh-wrong-placement-items

**BM25 top-3:**
1. A006 [42.84] — Components collapse to (0,0,0) / placement transforms lost
2. Xp025 [36.03] — Onshape→SolidWorks: assembly children snap to origin
3. Ps007 [29.89] — Assembly child placed at identity instead of intended offset

**Novel?** NO — A006 is a direct hit. **HIT.**

---

### D26 — FreeCAD STEP import edges dropped when STEP compound merge disabled

**Pattern:** STEP file containing edge-type sub-shapes (geometric curve sets, wires) inside a `COMPOUND` or top-level representation where the importing system requires a "compound merge" option; without it, the edge shapes are silently dropped.

**Entities:** `COMPOUND`, `EDGE_CURVE`, `GEOMETRIC_CURVE_SET`, `SHAPE_DEFINITION_REPRESENTATION`

**Defect:** Edge geometry missing from imported model; FreeCAD 1.0 RC2 with OCC 7.7.2; same file works in CAD Assistant.

**Source:** https://github.com/FreeCAD/FreeCAD/issues/17807

**BM25 top-3:**
1. P017 [38.16] — Free wires in a top-level COMPOUND silently dropped
2. Tfa067 [31.32] — Top face dropped after STEP import
3. A078 [28.15] — Compound-with-vertex emitted as empty in non-manifold export

**Novel?** NO — P017 "Free wires in a top-level COMPOUND silently dropped" is a near-exact match. **HIT.**

---

### D27 — OCCT 7.8.0 thread-safe numeric parsing fixing random mis-parses in parallel STEP reads

**Pattern:** STEP files read concurrently from multiple threads in OCCT 7.x (prior to 7.8.0 / V8_0_0_beta2 thread-safe write/read patch) where shared locale state causes the numeric parser to produce incorrect floating-point values at random.

**Entities:** All STEP numeric attributes (`REAL`, `CARTESIAN_POINT`, knot vectors, etc.)

**Defect:** Random coordinate corruption in multi-threaded STEP read sessions; shapes load with wrong geometry that changes between runs.

**Source:** https://github.com/Open-Cascade-SAS/OCCT/releases (V8_0_0_beta2 release note: "Thread-safe STEP write and STEP/IGES read")

**BM25 top-3:**
1. Le023 [49.20] — Locale-dependent decimal separator inside numeric attribute
2. Wr007 [31.91] — Locale-sensitive decimal separator emitted (comma instead of period)
3. Ad091 [25.88] — Crash on STEP file from non-C locale

**Novel?** YES — Le023 and Ad091 cover the single-threaded locale-separator bug (wrong decimal char). The parallel-read data-race that corrupts numeric values in a correctly-configured locale is a distinct input pattern: concurrent reads sharing non-atomic locale state, not a malformed file. No existing fixture targets the "STEP file that produces different geometry when read from parallel threads due to shared mutable locale state in the parser." **NOVEL** (thread-safety class is an API defect, but the input pattern is any STEP file triggering parallel parse).

---

### D28 — FreeCAD AP242 support gap: kinematics, camera views, material properties silently discarded

**Pattern:** STEP AP242 file (editions 2, 3, or 4) containing kinematic joint definitions, camera/clipping-plane views, or material property entities that FreeCAD's OCC-backed importer silently drops because AP242 ed2+ features are not implemented.

**Entities:** AP242 kinematic, camera-view, material, `GENERAL_PROPERTY`, `KINEMATIC_JOINT`

**Defect:** All non-geometry, non-basic-PMI content absent after import; no warning; model appears structurally intact.

**Source:** https://github.com/FreeCAD/FreeCAD/issues/19795

**BM25 top-3:**
1. P011 [50.03] — AP242 PMI / GD&T / kinematics annotations silently discarded
2. Pmi082 [30.05] — Saved-views and clipping planes lost on STEP read
3. Wr022 [28.91] — Saved-view / camera metadata lost on re-export

**Novel?** NO — P011 is a direct hit at 50.03. **HIT.**

---

### D29 — STEP AXIS2_PLACEMENT_3D zero-vector DIRECTION causes failed assembly transform

**Pattern:** STEP file where an `AXIS2_PLACEMENT_3D` entity carries a `DIRECTION` vector with zero magnitude (all components 0.0) as the axis or ref_direction field, causing the transform-creation to fail and the component to be placed at identity.

**Entities:** `AXIS2_PLACEMENT_3D`, `DIRECTION`, `ITEM_DEFINED_TRANSFORMATION`

**Defect:** Component mis-placed; transform creation fails silently; assembly spatially incorrect.

**Source:** https://github.com/Open-Cascade-SAS/OCCT/releases (M067 already in corpus; OCCT changelog entry)

**BM25 top-3:**
1. A006 [42.84] — Components collapse to (0,0,0)
2. M067 [33.54] — Transformation relation creation failed (AXIS2_PLACEMENT_3D with zero-vector DIRECTION)
3. Xp025 [36.03] — Onshape→SolidWorks assembly children snap to origin

**Novel?** NO — M067 is an exact hit (zero-vector DIRECTION). **HIT.**

---

### D30 — Knife-edge / sliver face causes tessellation self-intersection near parametric boundary

**Pattern:** STEP file containing `ADVANCED_FACE` patches with extremely narrow geometry (knife edges, micro-cuts) or densely-packed `EDGE_LOOP` boundaries where the parametric triangulation sampling produces polylines that intersect adjacent surface patches despite the underlying NURBS being geometrically non-self-intersecting.

**Entities:** `ADVANCED_FACE`, `B_SPLINE_SURFACE_WITH_KNOTS`, `EDGE_LOOP`, `PCURVE`

**Defect:** Self-intersecting mesh output; downstream FEA mesher or slicer rejects model; visual rendering shows inverted triangles.

**Source:** https://academic.oup.com/jcde/article/13/1/239/8383411 (Oxford JCDE, "Robust tessellation of CAD models without self-intersections", 2024)

**BM25 top-3:**
1. Tfa008 [27.40] — Pin / sliver face
2. Gs009 [25.65] — Self-intersecting / figure-eight EDGE_LOOP wire on planar face
3. Tsh230 [24.00] — Surface from STEP file wrongly imported / tessellated (self-intersecting NURBS net)

**Novel?** NO — Tfa008 (sliver face) and Tsh230 (self-intersecting NURBS tessellation) together cover this pattern well. **HIT.**

---

### D31 — STEP surface-tangency region produces intersecting tessellation polylines

**Pattern:** STEP file with two adjacent `ADVANCED_FACE` patches sharing a tangent-plane boundary (`G1` continuity) where the tessellation algorithm's piecewise-linear boundary approximation produces crossing polylines because convex-hull separation fails at the tangency locus.

**Entities:** `ADVANCED_FACE`, `B_SPLINE_SURFACE_WITH_KNOTS`, `EDGE_CURVE`, shared boundary loop

**Defect:** Tessellated mesh has crossing edges at the tangency region; mesh is locally non-manifold; renders with bright-line artifacts.

**Source:** https://academic.oup.com/jcde/article/13/1/239/8383411

**BM25 top-3:**
1. Tsh230 [24.00] — Self-intersecting NURBS net
2. Gs009 [25.65] — Self-intersecting EDGE_LOOP
3. Tfa008 [27.40] — Sliver face

**Novel?** YES — The G1-tangency-boundary crossing pattern is distinct from sliver faces and self-intersecting wires. The defect is topologically correct geometry that produces mesh intersections specifically because two patches share a tangent plane. No existing entry captures surface-tangency as the trigger for tessellation polyline crossing. **NOVEL.**

---

### D32 — STEP file PRESENTATION_STYLE_ASSIGNMENT entity of illegal type crashes styling pass

**Pattern:** STEP file where a `PRESENTATION_STYLE_ASSIGNMENT` entity's style list contains an entry of an unexpected/illegal entity type (e.g., a `COLOUR_RGB` entity instead of a `SURFACE_STYLE_USAGE`), causing the exchange kernel's style-processing loop to throw.

**Entities:** `PRESENTATION_STYLE_ASSIGNMENT`, `COLOUR_RGB`, `SURFACE_STYLE_USAGE`

**Defect:** Crash or exception during PMI/style import pass; application terminates; no geometry loaded.

**Source:** https://docs.techsoft3d.com/exchange/2023_SP2_U1/fixed_bugs.html; also reflected as A106 in corpus (StepVisual_PresentationStyleAssignment AV)

**BM25 top-3:**
1. M040 [29.05] — STYLED_ITEM.item NULL or unresolved
2. A103 [17.92] — Geometry imports correctly but faces have no colour
3. A106 [corpus] — Access violation in StepVisual_PresentationStyleAssignment

**Novel?** NO — A106 in the corpus is already specifically about access violation in `StepVisual_PresentationStyleAssignment`. **HIT.**

---

### D33 — OCCT V8 Gordon surface construction fallback for ill-conditioned network

**Pattern:** STEP file whose geometry is reconstructed via `GeomFill_Gordon` surface filling (e.g., a lofted or skinned `B_SPLINE_SURFACE` from crossing guide curves) where the guide-curve network is ill-conditioned, triggering the new explicit-status / fallback mode introduced in OCCT V8_0_0_p1.

**Entities:** `B_SPLINE_SURFACE_WITH_KNOTS`, crossing guide curves, `ADVANCED_FACE`

**Defect:** Pre-V8: Gordon surface construction silently fails with incorrect geometry or exception. Post-V8: explicit status reported and fallback applied.

**Source:** https://github.com/Open-Cascade-SAS/OCCT/releases (V8_0_0_p1 release note)

**BM25 top-3:**
1. Gn021 [49.45] — OFFSET_SURFACE of complex BSpline fails
2. Os011 [23.71] — ThruSections loft used outside supported envelope
3. Os010 [20.68] — ThruSections loft profiles inconsistent edge counts

**Novel?** YES — Gordon surface construction from crossing guide curves with ill-conditioned network is a distinct defect class from offset surfaces and ThruSections. No catalog entry targets `GeomFill_Gordon` / crossing-network surface failure mode. **NOVEL.**

---

### D34 — OCCT improved detection of full cylinder/cone parameters (V8 rc3 fix)

**Pattern:** STEP file with a `CYLINDRICAL_SURFACE` or `CONICAL_SURFACE` `ADVANCED_FACE` that covers a full revolution (2π) but whose parameter bounds in the `EDGE_LOOP` do not match the natural [0, 2π] period, causing OCCT to misidentify the surface as partial rather than full, producing a seam-edge insertion failure.

**Entities:** `CYLINDRICAL_SURFACE`, `CONICAL_SURFACE`, `ADVANCED_FACE`, `EDGE_LOOP`, seam edge

**Defect:** Seam edge incorrectly placed or absent; orientation inconsistency on full-revolution analytic surfaces; healing required.

**Source:** https://github.com/Open-Cascade-SAS/OCCT/releases (V8_0_0_rc3: "Improved detection of full cylinder/cone parameters")

**BM25 top-3:**
1. Xp033 [40.84] — NX-emitted cylinder split into two ADVANCED_FACE halves at the seam
2. Twi032 [26.67] — Periodic face wraps a full period and needs splitting at seam
3. Tfa028 [26.44] — Full-revolution CYLINDRICAL_SURFACE ADVANCED_FACE with single seam EDGE_CURVE

**Novel?** NO — Xp033 and Tfa028 capture full-revolution cylinder/cone seam problems directly. **HIT.**

---

### D35 — STEP incorrect conversion to Parasolid (HOOPS Exchange SDHE-18052)

**Pattern:** STEP file with `MANIFOLD_SOLID_BREP` or `B_SPLINE_SURFACE_WITH_KNOTS` entities where HOOPS Exchange's STEP-to-Parasolid bridge produces incorrect topology (e.g., wrong edge-face incidence, flipped normals, or incorrect trim curves) in the Parasolid representation.

**Entities:** `MANIFOLD_SOLID_BREP`, `B_SPLINE_SURFACE_WITH_KNOTS`, `ADVANCED_FACE`

**Defect:** Parasolid model fails validation; downstream NX/Solid Edge operations produce incorrect results; visible geometry mismatch.

**Source:** https://docs.techsoft3d.com/exchange/2023_SP2_U1/fixed_bugs.html (SDHE-18052)

**BM25 top-3:**
1. Tsh010 [40.55] — Reversed face normal in closed shell
2. Tfa057 [40.45] — Face wire orientation contradicts outer/inner role
3. Tsh230 [24.82] — Self-intersecting NURBS tessellation

**Novel?** NO — The underlying input patterns (reversed normals, wrong trim curves) are well covered. The HOOPS-to-Parasolid bridge context doesn't create a new input-pattern class. **HIT.**

---

## Novelty Summary Table

| ID | Short name | Novel? |
|----|-----------|--------|
| D01 | OFFSET_SURFACE of B-spline base not rendered | NO — Gn021 |
| D02 | SDR → SHAPE_ASPECT null-pointer crash | NO — A034 |
| D03 | COMPOUND_REPRESENTATION_ITEM SET_REPRESENTATION null children | **YES** |
| D04 | ORIENTED_EDGE circular reference stack overflow | **YES** |
| D05 | STEPCAFControl_Reader regression | NO — A097 |
| D06 | TORUS_SURFACE mesh distorted in body-object rendering | **YES** |
| D07 | CONICAL_SURFACE EDGE_LOOP: lateral face absent, only base circle | **YES** |
| D08 | COLOUR_RGB gamma shift on export | NO — Xp034 |
| D09 | GEOMETRIC_TOLERANCE magnitude null handle (MEASURE_REPRESENTATION_ITEM path) | **YES** |
| D10 | TESSELLATED_ANNOTATION_OCCURRENCE PMI not machine-readable | NO — Pmi045 |
| D11 | RATIONAL_B_SPLINE weights collapsed to 1.0 during iterative assignment | NO — Gn134 |
| D12 | SHELL_BASED_SURFACE_MODEL imported as surfaces not solids | NO — Tsh004 |
| D13 | NX AP242 PMI DIMENSIONAL_LOCATION unresolved shape_aspect entity | NO — Pmi125 |
| D14 | Spherical face incorrect UV curves (HOOPS SDHE-12051) | **YES** |
| D15 | Face orientation reversed on STEP read | NO — Tsh010 |
| D16 | UV curves wrong after STEP split (HOOPS SDHE-18541) | NO — Twi022 |
| D17 | STEP file with tessellation causes import error (HOOPS SDHE-20790) | NO — M056 |
| D18 | Face colors not read from STEP (HOOPS SDHE-18626/18841) | NO — A018/A019 |
| D19 | NURBS faces shrunk during STEP conversion (HOOPS SDHE-37143) | **YES** |
| D20 | Wrong faces upon reading STEP (HOOPS SDHE-35602) | NO — Tsh230 (ambiguous) |
| D21 | TESSELLATED_ANNOTATION_OCCURRENCE incomplete metadata (HOOPS SDHE-37128) | NO — Pmi045 |
| D22 | STEP export syntax error with tolerance values (HOOPS SDHE-36507) | NO — Ad049 |
| D23 | Unattached annotation STEP export syntax error (HOOPS SDHE-36465) | **YES** |
| D24 | B-rep parametric surface meshing fails ~5% models | **YES** |
| D25 | Assembly component misplaced to origin (GetShapes vs GetFreeShapes) | NO — A006 |
| D26 | FreeCAD STEP import edges dropped (compound merge disabled) | NO — P017 |
| D27 | Parallel STEP read thread-safe numeric parsing random mis-parse | **YES** |
| D28 | FreeCAD AP242 kinematics/camera/material silently discarded | NO — P011 |
| D29 | AXIS2_PLACEMENT_3D zero-vector DIRECTION fails assembly transform | NO — M067 |
| D30 | Knife-edge sliver face tessellation self-intersection | NO — Tfa008/Tsh230 |
| D31 | G1-tangency boundary produces tessellation polyline crossing | **YES** |
| D32 | PRESENTATION_STYLE_ASSIGNMENT illegal-type entry crashes styling pass | NO — A106 |
| D33 | Gordon surface construction from ill-conditioned guide-curve network | **YES** |
| D34 | Full cylinder/cone parameter detection seam mismatch | NO — Xp033/Tfa028 |
| D35 | STEP-to-Parasolid conversion incorrect topology (HOOPS SDHE-18052) | NO — Tsh010 |

**Novel count: 12 / 35 = 34.3%**

---

## Novelty Rate Comparison

| Wave | Sources | Defects sampled | Novel count | Novelty rate |
|------|---------|----------------|-------------|-------------|
| Wave 1 | OCCT/FreeCAD/CadQuery (early FOSS) | ~130 | ~32 | 24.6% |
| Wave 2 | OCE/FreeCAD-extended/KiCad | ~120 | ~13 | 10.5% |
| Wave 3 | KiBot/Blender-addon/deeper FOSS | ~100 | ~9 | 9.3% |
| **Wave 4** | **HOOPS Exchange / Inventor / OCCT-new / Academic** | **35** | **12** | **34.3%** |

The commercial-tracker pivot reversed the saturation trend dramatically. HOOPS Exchange (independent
codebase from OCCT) and academic tessellation papers surfaced genuinely new defect classes not in
the FOSS-only mining.

---

## DEFERRED List — Novel defects ready for B4.5 fixture synthesis

### DEF-A: COMPOUND_REPRESENTATION_ITEM with SET_REPRESENTATION_ITEM null children (D03)

STEP AP242 file containing:
```
#14000=COMPOUND_REPRESENTATION_ITEM('',SET_REPRESENTATION_ITEM((#14001)));
#14001=DESCRIPTIVE_REPRESENTATION_ITEM('dimensional note','statistical');
```
where the COMPOUND_REPRESENTATION_ITEM is referenced from a PMI representation chain. OCCT's reader populates `NbItemElement() = 1` but `ItemElementValue(0)` returns null handle because the SET_REPRESENTATION_ITEM sub-elements are not linked during entity-resolution pass. Fixture must include a minimal AP242 PMI structure (PRODUCT chain + shape + DRAUGHTING_MODEL + COMPOUND_REPRESENTATION_ITEM) so that the failing PMI path is exercised. Expected: geometry loads (shape valid) but PMI compound item sub-elements are null. Source: https://github.com/Open-Cascade-SAS/OCCT/issues/1283

### DEF-B: ORIENTED_EDGE mutual circular reference stack overflow (D04)

STEP file where ORIENTED_EDGE entity A references EDGE_CURVE B as its edge_element, and B has a back-reference forming a cycle (or more specifically, the B-rep defines a wire as: `#10=ORIENTED_EDGE('',*,*,#10,.T.);` — i.e., self-referential). Combined with a realistic CLOSED_SHELL that references this wire. OCCT (and HOOPS/PrusaSlicer wrappers) should detect the cycle and raise a parse error rather than stack-overflowing. Fixture: minimal CLOSED_SHELL cube with one ORIENTED_EDGE set up with a circular entity reference. Expected: error/exception on read, no crash. Source: https://github.com/prusa3d/PrusaSlicer/issues/11305

### DEF-C: TORUS_SURFACE ADVANCED_FACE tessellation over-segmentation (D06)

STEP file with a `TORUS_SURFACE` ADVANCED_FACE covering a full revolution (donut ring), where the tessellation splits the torus into 4 ADVANCED_FACE quadrants instead of 1 contiguous face. Fixture encodes: one CLOSED_SHELL containing one full-torus ADVANCED_FACE (no seam split), with a TORUS_SURFACE entity with R_major = 10, R_minor = 2. Expected: shape loads as a single face solid; tier-3 fingerprint should show 1 face not 4. The defect target is an importer that splits the torus into 4 faces instead. Source: https://forums.autodesk.com/t5/3ds-max-design-visualization/stp-step-import-now-has-problems-in-2024/td-p/11903372 ; note OCCT itself may not exhibit this defect — fixture should verify.

### DEF-D: CONICAL_SURFACE EDGE_LOOP incorrectly trimmed — lateral face absent (D07)

STEP file with a `CLOSED_SHELL` containing two ADVANCED_FACEs: (a) `PLANE` base circle and (b) `CONICAL_SURFACE` lateral surface, where the EDGE_LOOP defining the CONICAL_SURFACE's boundary incorrectly clips the semi-vertical angle extent to ~0 (or the top edge references a vertex that coincides with the base vertex, making the lateral extent zero). Specifically, encode a CONICAL_SURFACE with semi_angle ≈ 0.165 rad, height 76.2 units, but with an EDGE_LOOP that trims the upper extent to z ≈ 0.15 mm above the base rather than the apex. Expected: parse error or degenerate face; OCCT may silently load empty CONICAL_SURFACE. Source: https://discourse.mcneel.com/t/step-import-issue-conical-surface-interpreted-as-a-circle/219575 (Rhino RH-96071)

### DEF-E: GEOMETRIC_TOLERANCE magnitude encoded via MEASURE_REPRESENTATION_ITEM indirect chain (D09)

STEP AP242 file where a GD&T flatness callout is structured as:
- `GEOMETRIC_TOLERANCE` → `MEASURE_WITH_UNIT` → `VALUE_COMPONENT` via `PROPERTY_DEFINITION_REPRESENTATION` + `REPRESENTATION` + `MEASURE_REPRESENTATION_ITEM` 
rather than the direct OCCT-writer path (which links `GEOMETRIC_TOLERANCE` magnitude via a direct attribute). OCCT 7.9's `Magnitude()` returns null handle; fixed in 8.0.x master. Fixture must wire a minimal GEOMETRIC_TOLERANCE callout (flatness on a planar face) using the alternate MEASURE_REPRESENTATION_ITEM path. Expected: geometry loads (shape valid) but `StepDimTol_GeometricTolerance::Magnitude()` returns null under OCCT 7.9. Source: https://dev.opencascade.org/content/issue-reading-geometric-tolerance-values-nxnist-generated-step-ap242-files-occt-79

### DEF-F: SPHERICAL_SURFACE incorrect UV curves from STEP (D14)

STEP file with a `SPHERICAL_SURFACE` ADVANCED_FACE containing a `PCURVE` whose parameter-space representation uses a V-range of [0, π] instead of the STEP-defined [-π/2, +π/2] (ISO 10303-42 §4.4.32 sphere parametrization), causing UV curve geometry to be mapped to the wrong half of the sphere. Fixture: sphere closed shell with EDGE_CURVE + PCURVE on the spherical face where the PCURVE's V parameter origin is offset by π/2 from the sphere's expected convention. Expected: OCCT may heal or reject; HOOPS Exchange (pre-fix) would produce incorrect UV curves. Source: https://docs.techsoft3d.com/exchange/2023_SP2_U1/fixed_bugs.html (SDHE-12051)

### DEF-G: NURBS face domain shrinkage during STEP conversion (D19)

STEP file with a `B_SPLINE_SURFACE_WITH_KNOTS` ADVANCED_FACE whose knot vector spans [0.0, 1.0] × [0.0, 1.0] and whose FACE_OUTER_BOUND's PCURVE references the full parameter domain; after HOOPS Exchange conversion to internal NURBS (pre-SDHE-37143 fix), the active domain was incorrectly clipped to a sub-interval (e.g., [0.1, 0.9] × [0.1, 0.9]), shrinking the face by ~20%. Fixture: B_SPLINE_SURFACE_WITH_KNOTS with a FACE_OUTER_BOUND explicitly covering the full [0,1]² parameter domain; verify that the loaded face extent matches the control-point bounding box. Expected: face area matches theoretical; shrinkage is the defect. Source: https://docs.techsoft3d.com/exchange/2024/fixed_bugs.html (SDHE-37143)

### DEF-H: Unattached DRAUGHTING_ANNOTATION_OCCURRENCE with broken STEP syntax (D23)

STEP AP242 file emitted by a writer (modeled on HOOPS Exchange SDHE-36465 pattern) where a `DRAUGHTING_ANNOTATION_OCCURRENCE` entity exists in the DATA section with no reference from any `DRAUGHTING_MODEL` or `MECHANICAL_DESIGN_GEOMETRIC_PRESENTATION_REPRESENTATION`, AND its entity record has a syntax error (e.g., attribute count mismatch or illegal comma placement). Downstream parsers should ideally report the syntax error and skip the orphan annotation; incorrect behavior is a crash. Source: https://docs.techsoft3d.com/exchange/2024/fixed_bugs.html (SDHE-36465)

### DEF-I: B-rep parametric surface silently produces empty mesh (D24)

STEP file with a `B_SPLINE_SURFACE_WITH_KNOTS` whose control-point net has extreme aspect ratio (e.g., 1000:1), or whose knot vector spans [0, 1e-9] (near-zero parametric range), causing `BRepMesh_IncrementalMesh` to produce empty triangulation for the face (silent failure, no exception). Fixture: ADVANCED_FACE on a B_SPLINE_SURFACE_WITH_KNOTS with degenerate parametric extent; tier-3 oracle checks face count. Expected: shape may load but mesh is empty; verify via face area = 0 or null triangulation. Source: https://arxiv.org/html/2506.05417 ("Better STEP" paper, ~5% model rate)

### DEF-J: G1-tangency boundary tessellation polyline crossing (D31)

STEP file with two adjacent `B_SPLINE_SURFACE_WITH_KNOTS` ADVANCED_FACEs sharing an EDGE_CURVE boundary at a G1-tangency locus (normals are equal, surfaces share a tangent plane along the boundary curve). The PCURVE on each side closely approaches the boundary tangentially, causing tessellation sample points on the two sides to produce polylines that cross in 3D. Fixture: two B-spline patches meeting tangentially; verify that BRepMesh produces either no self-intersections (fixed) or flagged self-intersections (defect). Source: https://academic.oup.com/jcde/article/13/1/239/8383411

### DEF-K: Gordon surface ill-conditioned guide-curve network (D33)

STEP file containing a lofted/skinned face whose construction implicitly requires a Gordon surface fill over crossing guide curves that are nearly parallel or have inconsistent parameterization (ill-conditioned network). In OCCT pre-V8, `GeomFill_Gordon` silently produces incorrect or degenerate geometry; in OCCT V8+, an explicit status is reported and fallback is applied. Fixture: encode the ill-conditioned guide curves as B_SPLINE_CURVE_WITH_KNOTS in a GEOMETRIC_CURVE_SET or as the boundary curves of a B_SPLINE_SURFACE; verify shape-healing behavior. Source: https://github.com/Open-Cascade-SAS/OCCT/releases (V8_0_0_p1 release note)

### DEF-L: Parallel STEP read thread-safety: numeric mis-parse under concurrent load (D27)

STEP file with a valid geometry (e.g., a cylinder with millimeter coordinates), where the input pattern is the file itself being correct but the test scenario involves reading the file from two threads concurrently against OCCT pre-V8. The fixture would be the canonical valid STEP file; the test harness spawns two reader threads; expected behavior is both reads produce identical shapes. Pre-V8 behavior: occasional coordinate corruption due to non-atomic locale state. This is an API-level rather than file-level defect — may require a special test harness fixture rather than a corpus entry per se. Defer: document as an API test case, not a corpus STEP fixture.

---

## Notes for B4.5 Fixture Synthesis

- DEF-L (thread safety) is an API test, not a STEP file defect — exclude from fixture synthesis unless a harness for concurrent-read testing is added.
- DEF-C (TORUS_SURFACE over-segmentation) may not be reproducible in OCCT; needs oracle check first.
- DEF-G (NURBS domain shrinkage) is HOOPS Exchange-specific; OCCT may not exhibit it — use as "expected valid" case.
- High-confidence synthesis targets: DEF-A, DEF-B, DEF-D, DEF-E, DEF-J (all have clear entity-level encoding paths).

---

## Appendix: Source URLs

1. HOOPS Exchange 2023 Fixed Bugs: https://docs.techsoft3d.com/exchange/2023_SP2_U1/fixed_bugs.html
2. HOOPS Exchange 2024 Fixed Bugs: https://docs.techsoft3d.com/exchange/2024/fixed_bugs.html
3. OCCT GitHub Issues (STEP): https://github.com/Open-Cascade-SAS/OCCT/issues?q=STEP+is%3Aissue
4. OCCT Issue #994 (OFFSET_SURFACE): https://github.com/Open-Cascade-SAS/OCCT/issues/994
5. OCCT Issue #1202 (SDR SHAPE_ASPECT crash): https://github.com/Open-Cascade-SAS/OCCT/issues/1202
6. OCCT Issue #1283 (COMPOUND_REPRESENTATION_ITEM): https://github.com/Open-Cascade-SAS/OCCT/issues/1283
7. PrusaSlicer Issue #11305 (ORIENTED_EDGE recursion): https://github.com/prusa3d/PrusaSlicer/issues/11305
8. OCCT Forum (STEPCAFControl_Reader regression): https://dev.opencascade.org/content/occt-780-fails-read-step-file-stepcontrolreader-works-stepcafcontrolreader-doesnt
9. Autodesk 3dsMax forum (TORUS_SURFACE): https://forums.autodesk.com/t5/3ds-max-design-visualization/stp-step-import-now-has-problems-in-2024/td-p/11903372
10. Rhino McNeel forum (CONICAL_SURFACE): https://discourse.mcneel.com/t/step-import-issue-conical-surface-interpreted-as-a-circle/219575
11. CadQuery Issue #794 (COLOUR_RGB shift): https://github.com/CadQuery/cadquery/issues/794
12. OCCT Forum (GEOMETRIC_TOLERANCE magnitude): https://dev.opencascade.org/content/issue-reading-geometric-tolerance-values-nxnist-generated-step-ap242-files-occt-79
13. Autodesk Inventor Forum (TESSELLATED PMI): https://forums.autodesk.com/t5/inventor-forum/pmi-annotation-in-step-file/td-p/11966663
14. FreeCAD Issue #20718 (B-spline weights): https://github.com/FreeCAD/FreeCAD/issues/20718
15. PTC Creo Community (SHELL_BASED_SURFACE_MODEL): https://community.ptc.com/t5/Data-Exchange/Problem-importing-STEP/td-p/100900
16. OCCT Forum (NX AP242 PMI): https://dev.opencascade.org/content/cant-read-pmi-step-exported-ug
17. OCCT dev forum (STEP assembly placement): https://dev.opencascade.org/content/import-step-export-mesh-wrong-placement-items
18. FreeCAD Issue #17807 (edges dropped): https://github.com/FreeCAD/FreeCAD/issues/17807
19. FreeCAD Issue #19795 (AP242 support gap): https://github.com/FreeCAD/FreeCAD/issues/19795
20. OCCT Releases (V8 thread-safe, Gordon surface): https://github.com/Open-Cascade-SAS/OCCT/releases
21. Oxford JCDE (tessellation self-intersection): https://academic.oup.com/jcde/article/13/1/239/8383411
22. arXiv "Better STEP" (mesh failure rates): https://arxiv.org/html/2506.05417
