# Mining OrcaSlicer for NEW file-level STEP defect classes (2026-07)

**Source.** `SoftFever/OrcaSlicer` (org since renamed; `OrcaSlicer/OrcaSlicer`
URLs redirect to the same repo) — the highest-volume 3D-printing slicer with native
STEP import. Its importer is a thin wrapper over **OCCT** (`STEPControl_Reader` →
`BRepMesh` tessellation → per-solid mesh), so — exactly as the source survey
predicted — its STEP failure stream **correlates heavily with the already-mined OCCT
classes** and diversifies the *kernel* not at all. Value here is cross-oracle
corroboration ("valid in Onshape/Fusion/FreeCAD, wrong in OCCT-based Orca"), not new
mechanisms.

**Method.** `gh issue list`/`gh issue view` over `SoftFever/OrcaSlicer` (the repo's
GitHub search index is currently returning empty for `--search`, so issues were
fetched by number from web-search hits), plus WebSearch across issues + discussions +
wiki. Read the strongest STEP tickets (crash, empty/partial import, dropped features,
wrong orientation, tessellation artifacts, assembly flattening) and grepped
`STEP_PROBLEM_CATALOG.md` for novelty. **License:** OrcaSlicer is **AGPL-3.0**;
issue-attached `.step`/`.zip` files are user-uploaded and proprietary (Onshape /
Fusion 360 / SolidWorks / FreeCAD exports). **Pattern-only — DESCRIBE, never ingest
bytes.** Any fixture would be synthesized from the described pattern.

---

## Candidate table

| # | Title / defect class | Source URL (pattern only) | Reproducer recipe (concrete) | Expected behavior | Target section / prefix | Novelty | License |
|---|---|---|---|---|---|---|---|
| 1 | Internal cut-sphere **void renders as solid** — concave spherical cavity's inner shell orientation makes OCCT tessellate it filled | issues/7578 (FreeCAD 1.0 export; opens fine in FreeCAD + 3dviewer.net, cavity solid in Orca/Bambu) | Solid block with a fully-interior spherical cavity: `MANIFOLD_SOLID_BREP` whose inner `CLOSED_SHELL` is a `SPHERICAL_SURFACE` face with `same_sense`/wire orientation flipped so the cavity normal points *outward* (into the void) | Heal: derive shell in/out from volume sign, not per-face `same_sense`; or warn. Must not silently fill an interior void. | §12.5 shell / face-orientation (near Tsh035, line ~2921) | **SUB-CASE** of face-orientation-flip (CORROBORATES OCCT shell-orientation family) — distinct only in that carrier is a *concave interior sphere* whose fill is visually dramatic | AGPL-3.0; pattern only |
| 2 | Whole **analytic spherical feature silently dropped** on tessellation; STL of same part is complete | issues/6441, issues/6560 (Onshape STEP; sphere present in Onshape/Fusion/FreeCAD, absent in Orca) | Solid = box + tangent full `SPHERICAL_SURFACE` ball; OCCT `BRepMesh` drops the sphere face, rest of solid meshes | Tessellate every face or fail loudly; never silently omit a face from the mesh while importing the rest | §12.5 / §12.4 silent-drop | **CORROBORATES** Gs039 (cap-only sphere) + OCCT silent-face-drop family; strong cross-oracle signal but same mechanism | AGPL-3.0; pattern only |
| 3 | STEP → **no geometry at all** (silent-empty import; drag-drop and File→Import both yield empty) | issues/12366 (Orca 2.3.2-beta) | Any STEP whose only body is a non-solid (`OPEN_SHELL` / `SHELL_BASED_SURFACE_MODEL` / surface-only), which the mesh path silently discards → "no geometry" | Import surface/open-shell bodies as meshes or warn with reason; never silent-empty | §12.4 / §12.5 silent-empty | **CORROBORATES** existing silent-empty + Tsh002 (`FACETED_BREP`→`OPEN_SHELL` aborts empty) | AGPL-3.0; pattern only |
| 4 | **Extraneous jagged micro-facet artifacts** injected on import of Fusion 360 STEP (stray slivers disrupt bed placement) | issues/2970 (F360 export) | Curved `ADVANCED_FACE` (torus/NURBS) trimmed such that `BRepMesh` emits sliver/degenerate boundary triangles at trim seams | Chordal-error-refine trim curves consistently with surface interior; drop zero-area facets | §12.7 tessellation (near Gs033) | **CORROBORATES** Gs033 (jagged trim tessellation) | AGPL-3.0; pattern only |
| 5 | **Coarse default deflection** degrades STEP mesh quality (visible faceting / VFA on curved walls; no user control) | issues/9794 (feature req, with printed-artifact evidence) | Any smooth cylindrical/spherical wall imported at OCCT default linear/angular deflection → faceted print surface | Expose deflection control; document that STEP mesh quality is deflection-bound | §12.7 tessellation | **CORROBORATES** Gn007 (under-sampled tessellation) — this is a *default-parameter* variant, not a file defect | AGPL-3.0; pattern only |
| 6 | **Assembly component grouping lost — every leaf solid exposed flat** (5 logical components → ~200 ungrouped solids; regression at 2.3.0) | issues/9255 (Fusion 360 hierarchical assembly) | STEP assembly with `NEXT_ASSEMBLY_USAGE_OCCURRENCE` grouping many `MANIFOLD_SOLID_BREP` leaves under few `PRODUCT_DEFINITION` components; reader ignores grouping and exposes each leaf solid | Preserve `NAUO`/`PRODUCT_DEFINITION` grouping on import; expose components, not raw leaf solids | §12.6 assembly (near A005) | **SUB-CASE** of A005 (lost-hierarchy-flatten) — *inverse direction*: over-split vs collapse-to-one. Both are grouping-loss → CORROBORATES A005 | AGPL-3.0; pattern only |

## Runtime / non-file (SKIP)

- **issues/12104** (discussion) — 1.8 GB SolidWorks STEP → `0xC0000005` access-violation crash after ~10 h. Resource-exhaustion/size DoS; no minimal static reproducer distinct from existing §12.11 Ad DoS classes. SKIP.
- **issues/11509** — crash when *cancelling* the "Step file import parameters" dialog. UI/lifecycle bug, no file. SKIP.
- **issues/8592** — "no geometry" on `.stl` (not STEP) from a third-party repo. Off-format (mesh) + off-source. SKIP.
- **issues/7836** — modifier-mesh unit scaling; 3MF/UI, not STEP. SKIP.

---

## Honest yield assessment

Zero clean **NEW** classes. Two **SUB-CASE** candidates (#1 concave-sphere-cavity
renders solid; #6 assembly-grouping over-split) that are worth a fixture only if the
maintainer wants finer granularity — both fundamentally CORROBORATE existing OCCT
orientation / assembly-flatten families. The remaining STEP tickets (#2, #3, #4, #5)
are textbook OCCT behaviors the corpus already covers (silent face-drop, silent-empty
on non-solid bodies, jagged trim tessellation, deflection-bound mesh quality).

This matches the survey's structural takeaway #2 exactly: **OCCT-based slicers are
high-volume but OCCT-correlated** — they corroborate the OCCT mine rather than
diversify the kernel. The genuine kernel-diversity novelty lives in the independent
parsers (ruststep / assimp-STEP / steputils / Foxtrot), not here.

**Recommendation:** do NOT open a fixture wave from OrcaSlicer. At most, cite #7578
(concave-sphere-cavity-renders-solid) and #6441/#6560 (analytic-sphere-silently-
dropped, strong cross-oracle) as corroborating cross-oracle evidence in the Notes of
the existing OCCT shell-orientation and silent-face-drop entries. OrcaSlicer's best
standalone use is as a **cross-oracle validator** ("valid in Onshape/FreeCAD, wrong in
OCCT-Orca"), not as a defect-class source.
