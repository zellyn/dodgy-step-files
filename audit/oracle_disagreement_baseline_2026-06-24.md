# Cross-kernel oracle-disagreement baseline — 2026-06-24

Baseline for BACKLOG.md B3.6 (cross-kernel diff-detection). Computed
by `/tmp/oracle_disagreement_baseline.py` against `/tmp/cad-v2-out/`
populated by the most recent `_run_corpus.py` / `_final_verdict.py` pass.

## Headline

- **2,231 fixtures analyzed** (STEP corpus, excluding §12-2/§12-3 wave-B placeholder reruns)
- **19 distinct oracle-signature buckets** across (occt, gmsh, ifc, manifold, ocaf)
- **Only 2 fixtures** carry a truly unique signature (Gn090, Tfa153)

## Top signature buckets

| count | occt | gmsh | ifc | manifold | ocaf | example |
|---:|---|---|---|---|---|---|
| 837 | shape(N) | shape(N) | schema_n/a | not_manifold | ocaf_loaded | Pf001 |
| 483 | empty | empty | schema_n/a | no_shapes_loaded | ocaf_loaded | Ad078 |
| 279 | shape(N) | shape(N) | schema_n/a | empty_mesh | ocaf_loaded | Pf002 |
| 234 | empty | empty | schema_n/a | no_shapes_loaded | failed | Ad002 |
| 169 | signal | signal | schema_n/a | process_signal | signal | Ad015 |
| 104 | shape(N) | empty | schema_n/a | empty_mesh | ocaf_loaded | Gp161 |
| 42 | shape(N) | reject | schema_n/a | not_manifold | ocaf_loaded | Ad120 |
| 33 | shape(N) | reject | schema_n/a | empty_mesh | ocaf_loaded | Wr054 |
| 16 | reject | reject | schema_n/a | step_read_failed | failed | Ad001 |
| 10 | reject | reject | reject | step_read_failed | failed | Ad097 |
| 7 | empty | empty | reject | no_shapes_loaded | failed | Le018 |
| 4 | signal | signal | accept | process_signal | signal | Gp056 |
| 3 | empty | signal | schema_n/a | no_shapes_loaded | signal | M041 |
| 2 | empty | empty | accept | no_shapes_loaded | failed | Xp041 |
| 2 | signal | signal | reject | process_signal | signal | Gn055 |

## Singleton-signature audit candidates

These two fixtures have unique oracle-signatures in the corpus — each
is its own divergence pattern:

| fixture | occt | gmsh | ifc | manifold | ocaf |
|---|---|---|---|---|---|
| Gn090 | shape(N) | reject | schema_n/a | nonfinitevertex | ocaf_loaded |
| Tfa153 | empty | reject | schema_n/a | no_shapes_loaded | ocaf_loaded |

Tfa153 was already audited (see `audit/A6_audit_groups_punch_list_2026-06-24.md`
and catalog Notes); the divergence is intentional (1e15 coord overflow
that both parsers reject but categorize differently).

Gn090 audited 2026-06-24: catalog claim is "B-spline with Z=NaN control
point that OCC silently heals". Live oracle matches the Expected line
(`occt=shape(1)/shape(1) gmsh=reject`), and manifold's `nonfinitevertex`
signal IS the kernel-mishandling demonstration. Fixture is correct;
the unique signature is informative-not-broken.

## Kernel-pair disagreement rates

The "interesting" signal — fixtures where kernel A and kernel B
disagree on whether the file is loadable / what shapes it produces.

| pair | compared | disagree | rate |
|---|---:|---:|---:|
| **occt – gmsh** | 2231 | 188 | **8.4%** |
| occt – manifold | 2231 | 2205 | 98.8% (mesh-vs-brep is structural, not informative) |
| occt – ocaf | 2231 | 734 | 32.9% |
| gmsh – manifold | 2231 | 2201 | 98.7% (same caveat) |
| gmsh – ocaf | 2231 | 907 | 40.7% |
| manifold – ocaf | 2231 | 1959 | 87.8% |
| occt – ifc | 25 | 13 | 52.0% |
| gmsh – ifc | 25 | 13 | 52.0% |
| ifc – manifold | 25 | 8 | 32.0% |
| ifc – ocaf | 25 | 6 | 24.0% |

**The occt-gmsh 8.4% disagreement is the headline cross-kernel signal**
the corpus currently provides — both are B-rep readers, both produce
shape counts, and the 188 disagreeing fixtures expose real
load-time-strictness differences.

**Manifold and OCAF "disagreement" is mostly structural**: manifold
checks a tessellated mesh, OCAF reports root-label count in the doc
tree. They diverge from OCC face-count by construction, not because
they're disagreeing about validity. Their rows are kept for
completeness but should not be over-weighted.

The IFC oracle only fires on the 25 §12-1b header fixtures with
explicit IFC schemas; not relevant to most of the corpus.

## What BRL-CAD adds

Once `step-g` is installed and the corpus is re-run, this baseline
should be re-computed with brlcad included. Expectations from the B3
survey:

- BRL-CAD ↔ OCC disagreement: probably **15-25%** (much higher than
  gmsh-OCC because gmsh internally uses an OCC fork, while BRL-CAD
  uses STEPcode — completely independent code path)
- BRL-CAD will likely reject many §12.2 nurbs/pcurves fixtures that
  OCC silently heals (different NURBS tolerance model + stricter
  schema enforcement)
- The 188 occt-gmsh disagreements should mostly land in distinct
  brlcad buckets, giving 3-way clustering for the highest-value
  audit candidates

## Reproduction

```bash
python3 /tmp/oracle_disagreement_baseline.py
```

The analysis is read-only against `/tmp/cad-v2-out/`. If the cache is
stale, re-run `_run_corpus.py` first.
