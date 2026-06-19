# Issue-tracker mining log

**Status:** B4 from `BACKLOG.md`, wave-1 in progress.

Pattern-mine GitHub issue trackers (FreeCAD, OCCT, IfcOpenShell) for
real-world STEP defect patterns not yet captured in our catalog. Same
methodology as B1 (OCCT tests/ mining):

1. **Sample**: 30 STEP-relevant issues per tracker via `gh issue list
   --search "STEP in:title"`.
2. **Extract**: title + first 600 chars of body.
3. **Match**: BM25 against our 2310-entry catalog.
4. **Classify**: Haiku NOVEL / DUPLICATE / NOISE pass on misses.
5. **Synthesize**: build NOVEL fixtures via Python builder.
6. **Verify**: adversarial-verify loop.

## Wave 1

Status: classification dispatched.

- [x] Build issue corpus across 3 trackers (FreeCAD/OCCT/IfcOpenShell):
      69 issues total.
- [x] BM25 search each against the catalog at threshold 60: **15 hits,
      54 misses** (78% nominal-novelty rate at the chosen threshold).
- [x] Haiku classification of the 54 misses: **17 NOVEL · 24 DUPLICATE
      · 13 NOISE**. Result at `/tmp/issue_classification.md`.
- [ ] Synthesize the 17 NOVEL subset (open queue). Most cluster into
      4 broad classes:
  - `ExportImportCrash` (6): generic robustness defects in export/
    import path. Hard to synthesize without the specific reproducer
    files; many are already covered structurally by §12.11 Ad*
    crash-witnesses.
  - `GeometryLoss` (4): missing faces/edges/content on round-trip.
    Pattern-matches existing §12.13 Wr* writer-pathology entries;
    individual subclasses worth synthesizing if the bug body cites a
    specific entity type.
  - `SurfaceDefect` (2): from OCCT issue tracker; surface/face
    geometry corruption on export/import. Specific to NURBS/B-spline
    or trimmed-surface entities.
  - `AssemblyOpDefect` (1): mirror/array/join feature-export defect.
    Specific to §12.6 Assembly mirror semantics.
  - `ScaleDefect` (1): scaling / coordinate transformation.
  - Other (3): miscellaneous specific patterns.

Next step: open each high-value bug body to identify the specific
entity-level pattern, then synthesize.

### Wave 1 nominal-novelty conclusion

After classification, true novelty rate is **17 / 69 = 24.6%** —
significantly higher than B1's OCCT-tests novelty (0.67%). The issue
trackers expose user-facing patterns that the regression-test corpus
doesn't. B4 should continue with future waves to keep mining this
richer signal source.

Inventory cached at `/tmp/issue_corpus.json` (69 records). Misses
classification at `/tmp/issue_misses.json` (54 records). Top match
column lets us compare each issue against the closest catalog entry
and judge real novelty.

## Threshold calibration

| BM25 threshold | Hits | Misses | Nominal novelty |
|---:|---:|---:|---:|
| 40 | 43 | 26 | 37.7% |
| 60 | 15 | 54 | 78.3% |
| 80 | 10 | 59 | 85.5% |
| 100 | 4 | 65 | 94.2% |

Threshold 60 chosen as the working novelty cutoff: low enough to catch
real lexical matches but high enough to surface candidates worth manual
review. Mind the threshold-vs-noise tradeoff: at 60, ~26 NOISE entries
(UI bugs, performance regressions, viewer issues) are mixed into the
54 misses; Haiku classification filters those out.

## Provenance

Source repos (all open):
- `FreeCAD/FreeCAD` (30 issues sampled)
- `Open-Cascade-SAS/OCCT` (23 issues — OCCT is the same repo we mined
  tests/ from in B1, but issues are user-facing and may surface
  different defect patterns than the regression test corpus)
- `IfcOpenShell/IfcOpenShell` (16 issues — IFC overlap)

Issue bodies may contain attachments / reproduction files; we never
fetch or copy those. We synthesize from the *pattern* described in
title + body, never copy bytes.

## Findings

(populated as wave-1 classification completes)
