# Phase 4 — Defect-class mining from non-source enumeration

> Per `PLAN_OF_ATTACK.md` Phase 4: enumerate defect classes documented in
> issue trackers / release notes / KB articles that aren't in the OCCT or
> MeshFix headers. This complements the `OCCT_HEAL_COVERAGE_V2.md` and
> `MESH_HEAL_COVERAGE.md` source-code-driven enumerations.
>
> Result: **103 new prose-laundered defect classes** across two sub-mining
> passes. Each is a candidate for a future catalog entry; this doc is the
> punch list, not the entries themselves.

## Source pass 1 — OCCT issue tracker + closed PRs (41 new)

Source: GitHub Issues + closed PRs at `https://github.com/Open-Cascade-SAS/OCCT/issues`. Mantis tracker (`tracker.dev.opencascade.org`) returned 404 during sampling but legacy Mantis bug IDs are embedded in modern GitHub PR titles. ~80 issues/PRs touched; 41 NEW + 6 already-in-catalog enumerated; date range early-2024 through mid-2026.

### Most surprising pattern

**OCCT's recent robustness story is dominated by "add null/guard checks to the healer's own pipeline-state assumptions"**, not by accommodating new wild input shapes. Examples flagged in the mining: null context in #1203, null shape in #1216, null surface in #623/#624, null 2D curve in #876, null 3D curve in #860, array-size assignment race in #1267, reverse range in #863, off-by-one in #863, zero-iterator throw in #70, missing-colour-ref in #76.

**This suggests a new catalog axis: healer-state defects**. Fixtures that don't model bad STEP input but bad *intermediate post-import shape state* that downstream OCCT calls trip over. The existing §12.3a "UnifySameDomain crash family" already lives in this category — it could plausibly become a much larger top-level section.

### Top 5 highest-value NEW defects (from this pass)

1. **`reshape_cycle_in_value_chain_causes_unbounded_recursion`** (PR #1227, #998) — Healer-state pathology class. Fixture witness is "healer emitted 10^6 edges" rather than a single bad entity. Whole new sub-section.
2. **`hyperbola_constructor_falsely_requires_major_ge_minor`** (PR #1100) — Kernel-falsely-rejects-valid-input class. Easy fixture: any STEP `HYPERBOLA` with minor > major.
3. **`brepmesh_delaun_point_in_polygon_rejects_ccw`** (PR #920) — Sign-convention bug affecting roughly half of imported shapes (STEP-conformant CCW ones). High real-world incidence.
4. **`degenerate_torus_bounded_in_two_parameters_misses_seam_insertion`** (PR #699) — Explains long-tail of "imported revolve came in inverted" reports that the current catalog doesn't distinguish from generic torus-sign bugs.
5. **`thickness_circle_to_polygon_loft_falsely_rejected`** (PR #889) — Producer-facing defect (circle-to-rectangle loft) where OCCT silently rejects valid geometry.

Full per-defect details at [`/tmp/occt-defect-mining.md`](/tmp/occt-defect-mining.md) during this session; will be folded into catalog entries in upcoming releases.

## Source pass 2 — Commercial-translator literature (62 new)

Sources sampled:
- **HOOPS Exchange Fixed Bugs List** (SDHE-numbered) — yielded ~50 distinct defects. The single densest publicly-readable defect catalogue on the web.
- **CAD Exchanger CHANGES.txt** — 35 enumerated STEP fixes across versions 3.9–3.24.
- **CAx-IF / MBx-IF Recommended Practices** — GVP, PMI, Composites, Tessellation, Kinematics, Persistent IDs, Supplemental Geometry, Compression, User-Defined Attributes.
- **CADinterop briefs** for STEP-format, CATIA V5, NX, Creo, SolidWorks — kernel-pair specifics.
- **CAx-IF Round 54J / 56J test-suite reports**.
- **ITI CADfix product page** (low yield).

### Most surprising kernel-pair-only pattern

**SolidWorks-without-MBD silent semantic-PMI downgrade**: a defect *literally invisible* from the producer side. SolidWorks-without-MBD writes valid AP242 with visible polyline annotations and zero semantic GD&T — only a metrology-consuming receiver surfaces the loss. License-conditional writers are an entire defect class open-source bug trackers cannot see because the affected feature path is gated behind commercial licensing on the producer.

**56% (35/62) of enumerated defects are kernel-A-to-kernel-B specific** rather than universal. The CAx-IF / HOOPS Exchange / CADfix corpus is highly orthogonal to OCCT's own bug history — confirming the v1.3.0 landscape-audit hypothesis.

### Top 5 highest-value NEW defects (from this pass)

1. **`nx_parasolid_micro_gap_below_step_tolerance`** — Solid arrives as free faces on CATIA/ACIS receivers. The single most-cited interop class.
2. **`solidworks_no_mbd_ap242_silent_semantic_pmi_downgrade`** — File looks correct visually, contains zero semantic GD&T; only detectable by a metrology consumer.
3. **`creo_granite_to_parasolid_tolerance_gap`** — Assembly imports with components as surfaces, not solids.
4. **`draughting_model_item_association_with_placeholder_ignored_by_ap242_ed1`** — PMI present but disassociated from geometry.
5. **`catia_fta_captured_view_show_hide_filters_lost_across_step_ap242_roundtrip`** — All PMI visible at once after receive (no per-view filtering).

Full per-defect details at [`/tmp/cax-translator-mining.md`](/tmp/cax-translator-mining.md); will be folded into catalog entries in upcoming releases.

## Implications for catalog growth

- **Healer-state axis**: section similar to §12.3a's "UnifySameDomain crash family" but broader, covering ~15 OCCT-specific healer-pipeline-state defects.
- **Kernel-pair axis**: the catalog currently labels `producer-receiver-pair` for ~7 fixtures; CAx-IF mining alone could 10× that. Worth its own section or per-kernel-pair sub-class.
- **License-conditional defects**: the SolidWorks-without-MBD class needs a new metadata bit — `requires_consumer_perspective`. We can't synthesise a bad producer; we can synthesise a STEP file that looks correct but is missing semantic data a metrology consumer would expect.
- **Estimated fixture count from Phase 4 alone**: ~80–100 new catalog entries (some Phase 4 defects map to multiple fixtures; some to a single fixture each).

## Up next

Synthesise fixtures for the highest-value 20 defects (a balanced mix from both sources) in v1.4.0, prioritising:
- 5 healer-state defects (OCCT-pass-1 top 5 above)
- 5 kernel-pair defects (CAx-pass-2 top 5 above)
- 10 from the rest of the 103 list, biased toward the new catalog axes (healer-state + kernel-pair)
