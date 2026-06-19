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
- [ ] Haiku classification of the 54 misses (in progress).
- [ ] Synthesize the NOVEL subset.

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
