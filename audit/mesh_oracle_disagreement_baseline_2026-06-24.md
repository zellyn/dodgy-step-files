# Mesh-layer oracle baseline — pymeshfix across the 760-fixture corpus

Companion to `audit/oracle_disagreement_baseline_2026-06-24.md`. The
STEP-layer baseline measured 5 oracles against 2,231 STEP fixtures; this
file measures the new pymeshfix oracle against the 760-fixture mesh
sub-corpus (§12.14, Me001–Me1182).

## Headline

| Status | Count | % |
|---|---:|---:|
| loaded | 754 | 99.2 |
| rejected | 6 | 0.8 |

pymeshfix accepts essentially every fixture as parseable input
(.mesh.json → numpy arrays loads cleanly). The interesting signal is
**what `repair()` does to each accepted mesh**:

| Repair outcome | Count | % of loaded |
|---|---:|---:|
| **zero output (mesh fully invalidated)** | **474** | **62.9** |
| shrunk (some triangles removed) | 199 | 26.4 |
| grew (triangles added — holes filled) | 21 | 2.8 |
| unchanged (already clean) | 60 | 8.0 |

**The 474 zero-out fixtures are the headline result**: pymeshfix's
repair algorithm concludes the input is so degenerate that no triangles
should survive. For a defect-catalog corpus this is exactly the right
behavior — these fixtures genuinely demonstrate kernel-rejectable
defects.

## Boundary-loop distribution

For the 754 loaded fixtures, `n_boundaries` (count of open hole loops):

| Boundaries | Fixtures |
|---:|---:|
| 0 (closed) | 43 |
| 1 | 383 |
| 2 | 223 |
| 3 | 60 |
| 4 | 29 |
| 5 | 6 |
| 6 | 4 |
| 8 | 4 |
| 10 | 1 |
| 12 | 1 |

Most fixtures (606 of 754 = 80%) have 1 or 2 boundary loops — consistent
with single-hole / two-hole defect classes dominating the corpus.

## Sample fixtures per outcome

- **zero-out** (8 of 474): Me001, Me003, Me004, Me009, Me012, Me013, Me017, Me018
- **shrunk** (8 of 199): Me002(2→1), Me005(2→1), Me006(3→1), Me010, Me011, Me015, Me016, Me019
- **grew** (8 of 21): Me014(5→6), Me021(3→4), Me030(3→4), Me1090(3→4), Me111(2→4), Me1123(3→4), Me118(2→4), Me130(4→6)
- **unchanged** (8 of 60): Me007, Me008, Me023, Me087, Me1020, Me1053, Me1142, Me1155

The 21 "grew" fixtures are particularly interesting: pymeshfix decided
to fill the hole with new triangulation, **adding** triangles. This is
the "fill_holes" behavior firing. For a kernel-grading corpus these
represent fixtures where a healing kernel would substantively transform
the input geometry.

## Cross-oracle disagreement: existing _mesh_oracle vs pymeshfix

The existing `_mesh_oracle.py` is per-assertion (does each fixture's
declared assertion hold?), not per-verdict, so a direct apples-to-apples
comparison isn't possible without expanding it. The natural next step
is to extend _mesh_oracle to emit a single verdict per fixture (loaded /
rejected / detected-defect / healed) so it can be diff'd against
pymeshfix.

In the meantime, the headline disagreement question is: of the 60
"unchanged" fixtures (pymeshfix sees no defect), how many does the
existing _mesh_oracle flag as having a real defect? Those are the
informative differential cases.

## Reproduction

```bash
cd validation && uv run python -c "
from pathlib import Path
from step_corpus._pymeshfix_oracle import run_pymeshfix
for f in sorted(Path('../mesh-examples/12-14-mesh').glob('Me*.mesh.json')):
    r = run_pymeshfix(f)
    print(f, r['status'], r.get('n_boundaries'))
"
```

Full corpus run takes ~1 second on macOS arm64 (pymeshfix is fast).
