# Mining the NIST / MBx-IF / CAx-IF license-clean seam — 2026-07-11

## Purpose & method

Mine the **NIST MBE-PMI / CAx-IF / MBx-IF** public STEP test-file seam for **NEW file-level
defect / edge-case classes** absent from `STEP_PROBLEM_CATALOG.md`. Per the task brief this seam
is the biggest *license-clean, ingestible* new source: exotic-but-**legal** AP242 / PMI /
tessellation constructs that kernels are known to mishandle. Method: (1) learn corpus conventions
and existing §12.7 (Pmi) / §12.8 (M) / §12.12 (Xp) coverage; (2) three parallel research agents to
pin down source URLs + license status + the actual entity vocabulary present in the files; (3)
structural novelty check — grep every candidate construct against the catalog and keep only
0-hit / stray-hit classes.

**Key result:** the NIST CTC/FTC/STC AP242 files contain a whole family of **semantic GD&T
tolerance types and modifiers**, plus **AP242 tessellation packed-array constructs** and
**saved-view presentation entities**, that our 2300-entry corpus has **zero dedicated entries**
for — despite the corpus's very deep unit / annotation-plane / persistent-id PMI coverage. These
are all *VALID-BUT-HARD* (legal constructs kernels drop or mis-index), with several natural
malformed *DEFECT* variants.

Deprioritized (already saturated in corpus, verified by grep): unit/context handling (U*/N* series,
40+ entries), annotation-plane orientation (Pmi004/014/015/047/068), validation properties
(M026–M030, Pmi089 — and NIST files verified to *lack* `geometric_validation_property` anyway),
persistent-id/UUID (Pmi012/022–024), AP242 Ed.3 new-entity-dropped family (Pmi142–155),
external-file references (A012–A014, A033, M060), **kinematics** (actively mined in B4 wave-9 —
left to that effort).

---

## Source file-sets — license verdicts (verified by the research agents)

**Governing license quote (INGESTIBLE-CLEAN), verbatim from the NIST MBE-PMI project page:**
> "The test cases, CAD models, and STEP files can be used without any restrictions. Their use in
> other software or hardware products does not imply a recommendation or endorsement of those
> products by NIST."

Reinforced by NIST site-wide policy (https://www.nist.gov/copyrights-disclaimers): NIST-employee
work is *"not subject to copyright protection within the United States"* and site material is
*"public information and may be distributed or copied."* → US public domain, safe to ingest,
redistribute, and mutate. Attribution requested, not required.

| Source | URL | License verdict | Ingest? |
|---|---|---|---|
| **NIST MBE-PMI CTC/FTC/STC STEP files (zip, 49 files ~57 MB)** | `https://www.nist.gov/system/files/documents/noindex/2024/06/19/NIST-PMI-STEP-Files.zip` (landing: https://www.nist.gov/document/nist-pmi-step-files) | **INGESTIBLE-CLEAN** (public domain, quote above) | ✅ **BEST single URL** |
| NIST-PMI zip — byte-identical GitHub mirror | `https://github.com/usnistgov/SFA/raw/master/Release/NIST-PMI-STEP-Files.zip` | INGESTIBLE-CLEAN | ✅ |
| NIST MBE-PMI project page | https://www.nist.gov/ctl/smart-connected-systems-division/smart-connected-manufacturing-systems-group/mbe-pmi-0 | INGESTIBLE-CLEAN | ✅ (portal) |
| usnistgov/SFA (STEP File Analyzer) — bundles the same zip | https://github.com/usnistgov/SFA | INGESTIBLE-CLEAN (NIST gov work) | ✅ (same files) |
| usnistgov/CAD-PMI-Testing (dashboards; points back to the zip) | https://pages.nist.gov/CAD-PMI-Testing/ | INGESTIBLE-CLEAN (models); PDFs describe-only | ✅ (models) |
| steptools/bom2stp, stp2webgl (AP242 BOM⇄STEP tooling + tiny external-ref/assembly samples) | https://github.com/steptools/bom2stp | **Apache-2.0** | ✅ (small samples only) |
| stepcode/stepcode (AP203/214/242 schemas + `test/` data) | https://github.com/stepcode/stepcode | BSD-style, `NOASSERTION` | ⚠️ verify per-file |
| **MBx-IF / CAx-IF "production" test cases** (richest: kinematics, composites, full PMI, DM-XML) | https://www.mbx-if.org/home/cax/resources/ | **DESCRIBE-ONLY** — *"none of the production test cases … may be publicly released for any purpose"* (members-only) | ❌ design-reference only |
| CAx-IF "Recommended Practices" PDFs (encoding spec for the constructs) | https://www.mbx-if.org/home/cax/resources/ | Describe-only (no verified public-domain grant on the PDFs) | ❌ reference |
| OCCT / FreeCAD test STEP assets | github.com/Open-Cascade-SAS/OCCT · github.com/FreeCAD/FreeCAD | LGPL-2.1 (copyleft) | ❌ |
| Incidental GitHub CAD dumps w/ real `COMPLEX_TRIANGULATED_SURFACE_SET` / `CONSTRUCTIVE_GEOMETRY_REPRESENTATION` bytes (e.g. `jewbetcha/openflight`) | — | AGPL-3.0 / none | ❌ byte-study only |

**License scoping (important — the survey's blanket "no restrictions" is only HALF true).** The
CAx-IF test corpus has **four rights-holders** (Round 54J Test Suite §1.4): (1) **NIST-authored**
synthetic cases = *public domain, ingestible-clean* (the CTC/FTC/STC zip); (2) **member production
cases** (AFNeT / PDES Inc. / prostep ivip) = *"must not be… publicly released for any purpose"*
→ RESTRICTED; (3) **JAMA/JAPIA** models (JPMI test) = redistribution needs JAMA permission →
RESTRICTED; (4) **LOTAR** cases = RESTRICTED. Only bucket (1) is ingestible. General Guidelines
§2.5.1: models "shall not be used for any other purpose than MBx-IF testing," public exception =
"recommended practices, and synthetic STEP files the group agrees on publishing."

**Public but describe-only — the MBx-IF Recommended-Practices PDFs** (freely downloadable, but the
prose has no verified public-domain grant; use as construct/encoding reference, synthesize
fixtures). Base path `https://www.mbx-if.org/home/wp-content/uploads/`:
- Tessellated 3D Geometry v1.1 — `2024/05/rec_prac_3dtess_geo_v11.pdf`
- Supplemental Geometry v1.3 — `2025/09/rec_prac_suppl_geo_v13.pdf`
- PMI Representation & Presentation (AP242) v4.1 — `2024/06/rec_pracs_pmi_v41.pdf`
- Model Styling & Organization v1.10 — `2025/09/rec_prac_styling_org_v1.10.pdf`
- External (Element) References v3.1 — `2024/05/rec_prac_ext_ref_v31.pdf`
- Composite Materials v4.4 — `2026/01/Rec_Pracs_Composites_V4.4.pdf`
- Geometric & Assembly Validation Properties v4.6 — `2024/05/rec_prac_gvp_v46.pdf`
- Index: https://www.mbx-if.org/home/cax/recpractices/ · Test rounds (spec PDFs only, models member-gated): https://www.mbx-if.org/home/cax/testrounds/

**Net:** the NIST CTC/FTC/STC AP242 files are the one directly-ingestible, exotic-rich,
public-domain seam. Everything richer (kinematics, composites, full production PMI) sits behind the
MBx-IF members-only, no-redistribution wall — reference the public RP PDFs for construct *design*,
but synthesize our own fixtures. The corpus rule (synthesize the *pattern*, never copy bytes)
applies regardless.

**Files verified present in the ingestible zip** (test-case IDs are literal filenames):
`nist_ctc_01..05_asme1_ap242-e{1,2}.stp`, `nist_ftc_06..11_asme1_ap242-e{1,2}.stp`, and the unique
tessellated-geometry variant **`nist_ftc_08_asme1_ap242-e1-tg.stp`** (faceted, no semantic PMI),
`nist_stc_06..10_asme1_ap242-e3.stp`, plus AP203 graphical-PMI twins and PDFs.
Caveat from the zip README: *"These are NOT reference STEP files without any errors … will report
some Syntax Errors."* — i.e. realistic/dirty, not golden; good for a grading corpus.

---

## Candidate NEW entries (18) — all novelty-verified (0-hit / stray-hit vs catalog)

Legend: **[V]** = VALID-BUT-HARD (legal construct kernels mishandle) · **[D]** = DEFECT (malformed).
"Present in" = the ingestible NIST file family that actually carries the construct (verified by the
agents grepping the unzipped files). All target §12.7 (Pmi) unless noted.

### Semantic GD&T tolerance types & modifiers (NIST FTC/CTC seam — deepest gap)

| # | Title / class | Kind | Reproducer recipe (minimal AP242 construct) | Expected kernel behavior | Novelty (nearest existing) | Present in |
|---|---|---|---|---|---|---|
| 1 | **`CIRCULAR_RUNOUT_TOLERANCE` / `TOTAL_RUNOUT_TOLERANCE` with datum-axis reference** | [V] | Cylinder feature; `circular_runout_tolerance` (and a second `total_runout_tolerance`) each with `toleranced_shape_aspect` = the cylinder face and `geometric_tolerance_with_datum_reference` → a datum axis `A`. Value 0.05mm. | Import both runout FCFs; preserve the datum-axis link; runout must not be silently downgraded to circularity or dropped. | **NEW** — 0 catalog hits for `runout_tolerance`; nearest = generic `position_tolerance` (Pmi010). Runout family absent. | FTC/CTC |
| 2 | **`SURFACE_PROFILE_TOLERANCE` / `LINE_PROFILE_TOLERANCE` with `ALL_AROUND_SHAPE_ASPECT` scope** | [V] | Profiled edge; `line_profile_tolerance` (unique to CTC 2) or `surface_profile_tolerance`, target = an `all_around_shape_aspect` (or `composite_group_shape_aspect`) so the zone wraps the whole profile "all-around". | Resolve the all-around/between scope so the profile zone covers every bounded segment, not just the first face. | **NEW** — 0 hits `surface_profile_tolerance`/`line_profile_tolerance`/`all_around_shape_aspect`. | CTC 2, FTC |
| 3 | **`GEOMETRIC_TOLERANCE_WITH_MODIFIERS` carrying material-condition modifier (MMC / LMC / free-state / tangent-plane)** | [V] | Position tolerance on a hole; `geometric_tolerance_with_modifiers` whose `modifiers` set includes `maximum_material_requirement` (and variants: `least_material_requirement`, `free_state`, `tangent_plane`). | Preserve the ⓂⓁ modifier on round-trip; do not silently coerce to RFS. Modifier changes the tolerance semantics (bonus tolerance) — dropping it is a correctness bug. | **NEW** — `geometric_tolerance_with_modifiers` = 1 stray, `maximum_material_requirement`/`least_material_requirement`/`tangent_plane` = 0. | FTC, CTC |
| 4 | **`DATUM_REFERENCE_COMPARTMENT` / `DATUM_REFERENCE_ELEMENT` with per-datum material modifier (MMC on the datum)** | [V] | AP242 Ed.2 FCF datum system `A|B(Ⓜ)|C`: ordered `datum_reference_compartment`s, one bearing a `simple_datum_reference_modifier` / `datum_reference_modifier_with_value` (movable/translation). | Preserve compartment ordering AND the per-datum modifier. Readers that flatten to a legacy `datum_reference` list lose both. | **NEW** — nearest = Pmi025/027/028 (identical datums, legacy datum_reference, common_datum) but none carry compartment+modifier. `datum_reference_modifier_with_value` = 0. | FTC, CTC |
| 5 | **`UNEQUALLY_DISPOSED_GEOMETRIC_TOLERANCE` (unilateral / "UZ" profile)** | [V] | Surface-profile tolerance 0.4 with `unequally_disposed_geometric_tolerance.displacement` = 0.1 (zone biased +0.1/−0.3 rather than symmetric). | Apply the asymmetric zone offset; a reader assuming a symmetric zone mis-places the tolerance band by the displacement. | **NEW** — `unequally_disposed_geometric_tolerance` = 1 stray, no entry. | FTC |
| 6 | **Full GD&T symbol-set entities beyond position/perpendicularity/flatness** (`CYLINDRICITY_`, `CIRCULARITY/ROUNDNESS_`, `STRAIGHTNESS_`, `ANGULARITY_`, `CONCENTRICITY_`, `SYMMETRY_TOLERANCE`) | [V] | One file with each of the six remaining form/orientation/location tolerance entities on appropriate features (cylindricity on a cylinder, symmetry across a slot, etc.). | Recognize each subtype distinctly; a reader that maps unknown subtypes onto a generic tolerance loses the symbol semantics. | **NEW** — 0 hits for each entity name; catalog only has position/perpendicularity/flatness. | FTC, CTC |
| 7 | **`ANGULAR_SIZE` / `ANGULAR_LOCATION` semantic dimension** (vs linear `DIMENSIONAL_SIZE`) | [V] | Wedge feature; `angular_size` = 30° with `plus_minus_tolerance`, plus an `angular_location` between two faces, tied via `dimensional_characteristic_representation`. | Carry the angular dimension with its plane-angle unit; don't coerce to a linear size or drop the angular unit. | **NEW** — `angular_size`/`angular_location` = 0; nearest = Pmi072 (dimension_pair unit mismatch). | FTC, CTC |

### DEFECT variants mined from the same constructs

| # | Title / class | Kind | Reproducer recipe | Expected kernel behavior | Novelty | — |
|---|---|---|---|---|---|---|
| 8 | **Runout tolerance with NO datum reference** (schema/GD&T-illegal — runout requires a datum axis) | [D] | Same as #1 but omit `geometric_tolerance_with_datum_reference`; leave `circular_runout_tolerance` datum-less. | Reject or warn: a runout FCF without a datum axis is meaningless; a compliant reader must flag it, not silently accept. | **NEW** (defect of #1) | — |
| 9 | **`maximum_material_requirement` modifier applied to a FORM tolerance** (illegal: MMC only on size features) | [D] | `geometric_tolerance_with_modifiers` = MMC attached to a `flatness_tolerance` (a form tolerance, which has no size feature). | Warn/reject: Ⓜ on a feature without size is a rule violation (ASME Y14.5); accepting it silently propagates a bad bonus-tolerance calc. | **NEW** (defect of #3) | — |

### AP242 tessellation packed-array constructs (FTC-08-tg seam)

| # | Title / class | Kind | Reproducer recipe | Expected kernel behavior | Novelty (nearest existing) | Present in |
|---|---|---|---|---|---|---|
| 10 | **Single shared `COORDINATES_LIST` for a whole `TESSELLATED_SHELL`, 1-based integer index lists** | [V] | `tessellated_shell` whose faces all index a *single* packed real-array `coordinates_list` (AP242's point holder — **note: `cartesian_point_list_3d` is the AP203/214 name; AP242 uses `coordinates_list`**), triangles referencing 1-based integer indices into it — not individual `CARTESIAN_POINT` entities. | Index the shared packed array with correct 1-based semantics; kernels built around per-point entities, or that assume a per-face list, mis-index or drop faces. | **NEW angle** — `coordinates_list` has 16 catalog hits but only as **M004**'s *anti*-pattern (each face its OWN list, watertightness lost). The **shared single-list + 1-based indexing** form is uncovered. | ftc_08-e1-tg |
| 11 | **`COMPLEX_TRIANGULATED_SURFACE_SET` with `triangle_strips` + `triangle_fans` (implicit vertex reuse)** | [V] | Triangulated set encoded partly as strips/fans (each sublist reusing the two prior indices) rather than an explicit triangle list. | Expand strips/fans by the implicit reuse rule; a reader handling only plain triangle lists silently loses those faces. | **NEW** — `triangle_strips`/`triangle_fans` = 0; `complex_triangulated_surface_set` only appears as passing mentions, no strip/fan entry. | ftc_08-e1-tg |
| 12 | **Tessellated surface set with per-vertex `NORMALS` + separate normal-index array** | [V] | `triangulated_surface_set` (or complex form) with a `normals` list and a `normal_index`/`pnindex` array whose length/index base must pair 1:1 with vertices. | Pair normals to vertices correctly; readers commonly ignore normals or assume `count(normals)==count(vertices)` and mis-shade or crash. A count-mismatch is the natural **[D]** variant. | **NEW** — `normal_index`/`pnmax` = 0; `pnindex` = 1 stray. | ftc_08-e1-tg |
| 13 | **`TESSELLATED_SOLID` as the sole shape — no exact `MANIFOLD_SOLID_BREP` counterpart** | [V] | Part whose only `SHAPE_REPRESENTATION` item is a `tessellated_solid`/`tessellated_shell` (faceted), with no exact B-rep and no dual-representation link. | Accept faceted-only geometry as the part shape; kernels expecting exact geometry return an empty solid. Distinct from **M022** (STL-derived triangulated_face *ignored*) and **M056** (tessellation *conflicting* with B-rep) — here the B-rep is simply *absent by design*. | **NEW angle** — `tessellated_solid_representation` = 0. | ftc_08-e1-tg |

### Saved-view / annotation presentation entities

| # | Title / class | Kind | Reproducer recipe | Expected kernel behavior | Novelty | Present in |
|---|---|---|---|---|---|---|
| 14 | **`CONTEXT_DEPENDENT_INVISIBILITY` — per-saved-view invisibility of PMI/geometry** | [V] | Two `model_geometric_view`s; a `context_dependent_invisibility` hides an annotation in view 1 but shows it in view 2 (invisibility scoped to a `presentation_view`, not global). | Honor per-view visibility state; readers that apply global `invisibility` (or ignore it) show/hide the wrong items per saved view. | **NEW** — `context_dependent_invisibility` = 0; catalog has global `invisibility` (10 hits, e.g. P019) only. | CTC |
| 15 | **`FILL_AREA_STYLE_HATCHING` / `ANNOTATION_FILL_AREA_OCCURRENCE` — section-view crosshatch presentation** | [V] | Section/cutaway saved view with a hatched fill: `annotation_fill_area_occurrence` styled by `fill_area_style_hatching` (angle, spacing, `curve_style`). | Preserve the hatch style + geometry of the section fill; a reader dropping fill-area styling loses the section presentation entirely. | **NEW** — `fill_area_style_hatching`/`annotation_fill_area_occurrence`/`hatching` = 0. | CTC |
| 16 | **`VIEW_VOLUME` + `MODEL_GEOMETRIC_VIEW` saved-view frustum / clipping bounds** | [V] | `default_model_geometric_view` + a `model_geometric_view` with a `view_volume` (front/back clipping planes, projection) referencing a `camera_model_d3`. | Reconstruct the saved-view camera + clipping frustum; kernels ignoring the presentation layer lose all MBD "view state" (orientation, clip, zoom). | **NEW angle** — `view_volume` = 1 stray, `context_dependent_invisibility`/`default_model_geometric_view` absent; nearest = Pmi006/019 (camera_model_d3 name placement) but not the frustum/clip. | CTC 05 |

### Describe-only-sourced (synthesize from the *public* MBx-IF Recommended-Practices PDFs — no ingestible file, but pattern is documented)

| # | Title / class | Kind | Reproducer recipe | Expected kernel behavior | Novelty | Source (describe-only) |
|---|---|---|---|---|---|---|
| 17 | **`TESSELLATION_ACCURACY_PARAMETERS` on a tessellated shape (`..._with_accuracy_parameters`)** | [V] | `tessellated_shape_representation_with_accuracy_parameters` carrying `tessellation_accuracy_parameters` (chordal deviation, `tessellated_facet_long_short_edge_ratio`) declaring the facet quality the mesh was built to. | Read/preserve the declared accuracy so downstream re-tessellation or validation can trust the mesh quality; kernels ignore it and silently re-facet at their own tolerance. | **NEW** — `tessellation_accuracy_parameters`/`with_accuracy_parameters`/`tessellated_facet_long_short_edge_ratio` = 0. | Tessellated 3D Geometry RP v1.1 (public PDF) |
| 18 | **AP242-native composite laminate: `PLY_LAMINATE_TABLE` / `PLY_ORIENTATION_ANGLE` / `REINFORCEMENT_ORIENTATION_BASIS`** | [V] | Composite panel: `ply_laminate_table` → `ply_laminate_definition`s each with a `ply_orientation_angle` relative to a `reinforcement_orientation_basis`, `composite_assembly_table` stacking sequence; no manifold B-rep solid. | Carry the ply stack + per-ply fibre orientation; kernels expecting a solid produce nothing, and orientation-basis drift silently rotates every ply. | **NEW** — `ply_laminate`/`ply_orientation_angle`/`reinforcement_orientation_basis`/`composite_assembly_table` = 0; nearest = **M084/M085** (AP209/AP210 *empty*/mismatched ply — different schema, not AP242-native stack). | Composite Materials RP v4.4 (public PDF; CO2 production models are member-restricted) |

---

## Directly-ingestible file-set URLs (license-clean, for direct download)

1. **`https://www.nist.gov/system/files/documents/noindex/2024/06/19/NIST-PMI-STEP-Files.zip`** — NIST CTC/FTC/STC AP242 e1/e2/e3 semantic+graphical PMI + `ftc_08-e1-tg` tessellated variant. Public domain. **← top pick.**
2. `https://github.com/usnistgov/SFA/raw/master/Release/NIST-PMI-STEP-Files.zip` — byte-identical mirror.
3. `https://www.nist.gov/document/nist-pmi-step-files` — official landing page (redirects to #1).
4. `https://github.com/steptools/bom2stp` + `https://github.com/steptools/stp2webgl` — Apache-2.0; small AP242 external-reference / assembly-structure samples only.
5. `https://github.com/stepcode/stepcode` — BSD-style (`NOASSERTION`); `test/` STEP data, verify per-file.

Describe-only (design reference, do NOT ingest): `https://www.mbx-if.org/home/cax/resources/`
(MBx-IF/CAx-IF production models + Recommended-Practices PDFs — members-only, redistribution
forbidden).

---

## Notes / caveats

- All 18 candidates are **file-level** (a single static `.stp` reproduces each) and **novelty-checked**
  by grep against the full catalog (counts cited inline). The GD&T tolerance-type / modifier cluster
  (#1–#9) is the single largest coherent gap: the corpus's 140 Pmi entries cover annotation-plane,
  persistent-id, units, saved-view *names*, and machining features exhaustively, but **not the
  semantic tolerance-symbol vocabulary itself** (runout, profile, cylindricity, MMC/LMC modifiers,
  datum-reference compartments) — exactly what NIST FTC/CTC are built to exercise.
- Fixtures must be **synthesized** from the pattern (corpus rule); the NIST files are the
  construct/vocabulary reference and an oracle-divergence target, not a byte source — though their
  license *would* also permit direct ingest if ever desired.
- The NIST files carry deliberate syntax errors (per their README) — helpful for realistic grading,
  but each synthesized fixture should isolate ONE construct so its claim is unambiguous (per the
  quality-over-completeness convention).
- Suggested build order by value: #1–#7 (semantic GD&T, highest novelty + direct NIST provenance) →
  #10–#13 (tessellation packed arrays) → #14–#16 (saved-view presentation) → #8/#9 (defect variants)
  → #17/#18 (describe-only-sourced; lowest priority as they lack an ingestible oracle file).
