# Mesh-corpus mutation-test baseline — 2026-06-24

First mutation-test pass against the 760-fixture mesh sub-corpus
(§12.14, Me001–Me1182). Method analogous to `_mutation_test.py` for
STEP fixtures, adapted to `.mesh.json` + the pymeshfix oracle.

## Method

For each fixture:
1. Run pymeshfix on the untouched bytes → baseline signature
2. For each of 3 mutations:
   a. Pick a random digit byte inside the `vertices` / `triangles` JSON arrays
   b. Flip the digit to a different digit (0–9)
   c. Re-run pymeshfix on the mutated bytes (subprocess-isolated to
      contain MeshFix C++ SIGSEGVs on adversarial input)
   d. Compare new signature vs baseline
3. Fixture is "mutation-detected" if any mutation produced a different
   signature; otherwise "structurally inert"

Signature = `(status, n_vertices_in, n_triangles_in, n_vertices_out,
n_triangles_out, n_boundaries)`.

Tooling: `validation/src/step_corpus/_mesh_mutation_test.py`.

## Headline

| Bucket | Count | % |
|---|---:|---:|
| Baseline `loaded` | 754 | 99.2 |
| Baseline `rejected` | 6 | 0.8 |
| **Loaded + detected by ≥1 mutation** | **380** | **50.4** of loaded |
| **Loaded + structurally inert** | **374** | **49.6** of loaded |

For comparison, the STEP corpus's silent-empty subset showed ~88%
structural inertness in prior Q5 mutation passes. The mesh corpus is
substantially less inert overall (50% vs 12% detection rate
respectively), but with a significant strengthening target.

## Inertness clusters in small-mesh fixtures

The 374 structurally-inert fixtures cluster heavily in low-vertex-count
designs:

| Baseline (n_v_in, n_t_in) | Inert count |
|---|---:|
| (6, 2) | 56 |
| (5, 3) | 31 |
| (4, 2) | 26 |
| (7, 3) | 18 |
| (8, 4) | 16 |
| (5, 4) | 16 |
| (6, 4) | 16 |
| (3, 1) | 15 |
| (5, 2) | 14 |
| (4, 4) | 14 |
| ... (smaller buckets) | 152 |

**Top-10 buckets account for 222 of 374 inert fixtures (59%).** These
are all "minimal input to trigger one code branch" fixtures — the same
class the pymeshfix-unchanged audit (`audit/pymeshfix_unchanged_audit_2026-06-24.md`)
classified as "code-path probes" that are legitimately invisible to
pymeshfix's repair surface.

For these fixtures, single-byte digit mutations either:
- Produce invalid JSON → `rejected` (different status but uninformative)
- Produce a near-equivalent topology with the same boundary count
- Get caught by pymeshfix's tolerance and ignored

## Implication: not a quality red-flag

The 49.6% inertness is NOT analogous to the STEP silent-empty
strengthening case. There, structurally-inert fixtures had no
*independent* evidence beyond their bytes-level claim. Here, the inert
mesh fixtures are independently verified by:
- The catalog claim (every Me* entry has explicit `defect_class` +
  catalog text)
- Often a `_mesh_oracle` assertion (the per-fixture geometric
  invariants checked by `_mesh_oracle.py`)
- The mesh-builder source (each Me* has a deterministic `mesh_sources/`
  builder that documents the construction intent)

A small mesh fixture being mutation-inert doesn't mean the catalog
claim is wrong — it means the bytes are too minimal for random
single-digit flips to perturb pymeshfix's specific defect detector.

## Real-signal subsets to investigate further

The interesting candidates aren't the small-mesh inerts. They're:

1. **Large-mesh inert fixtures**: any inert fixture with V > 20 or T > 10.
   Those have plenty of mutation surface, so inertness is suspicious.
2. **`grew` inert fixtures**: pymeshfix actively healed the input, but
   mutating digits didn't change the heal outcome. The healing must be
   robust to the perturbations, which is interesting.
3. **`zero-out` inert fixtures**: pymeshfix invalidated the input
   entirely, and mutations didn't change that. Unsurprising (a broken
   mesh stays broken) but worth confirming there aren't redundant
   fixtures in this set.

The JSONL output at `/tmp/mesh_mutation_results.jsonl` (regeneratable)
contains per-fixture details for follow-up analysis.

## Reproduction

```bash
cd validation && uv run python -m step_corpus._mesh_mutation_test \
    --mutations 3 --json-out /tmp/mesh_mutation_results.jsonl
```

Run time: ~5–8 minutes on macOS arm64 (subprocess overhead per
pymeshfix call, ~50–100ms × 760 × 3 mutations).

## Comparison to STEP-corpus mutation testing

The STEP `_mutation_test.py` uses a similar harness but operates on
the DATA section of `.stp` files, with validate2 (multi-oracle) as
the signal. Per the Q5 sweeps documented in user memory, STEP showed
~10% detection on silent-empty fixtures and 91.8% on oracle-active
fixtures. The mesh corpus's 50% sits closer to the oracle-active end
— pymeshfix produces a strong differential signal because every
fixture is "oracle-active" (pymeshfix has an opinion on every mesh).

## Optional follow-up

- Filter the JSONL to find large-mesh inert outliers; spot-audit those
- Add a `_mesh_oracle` per-fixture verdict mode so the mutation test
  can compare against two oracles simultaneously (pymeshfix +
  `_mesh_oracle`)
- Wire mutation testing into CI as a long-tier check (currently no
  CI coverage)
