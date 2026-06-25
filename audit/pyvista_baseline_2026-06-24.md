# Mesh-layer oracle baseline — pyvista across the 760-fixture corpus

Companion to `audit/mesh_oracle_disagreement_baseline_2026-06-24.md`
(pymeshfix baseline). pyvista was wired as the second non-OCC mesh
oracle (commit `73797e32`) specifically to close the
audit #479 (`pymeshfix-unchanged`) blind spot: pymeshfix has no
window into orientation-only defects or non-manifoldness, so the 60
fixtures it called "unchanged" needed a second opinion before we
could trust them as truly clean.

## Headline

| Status | Count | % |
|---|---:|---:|
| loaded | 754 | 99.2 |
| rejected | 6 | 0.8 |

Identical to pymeshfix — the 6 rejected fixtures have empty
vertices or triangles arrays and parse-reject in both oracles
before any geometric check fires.

## What pyvista exposes that pymeshfix doesn't

For the 754 loaded fixtures:

| is_manifold | count | % |
|---|---:|---:|
| False (VTK's edge-incidence check fails) | 707 | 93.8 |
| True | 47 | 6.2 |

| n_orientation_flipped | count | % |
|---|---:|---:|
| 0 (winding already consistent) | 713 | 94.6 |
| ≥1 (VTK's vtkPolyDataNormals would flip ≥1 triangle) | 41 | 5.4 |

Flip-count distribution: 1 → 13, 2 → 11, 8 → 6, 4 → 4, 6 → 4,
3 → 2, 11 → 1.

## Cross-tab — the differential signal

|             | flips=0 | flips>0 |
|---|---:|---:|
| **NON-MANIFOLD** | 682 | 25 |
| **MANIFOLD**     | 31  | 16  |

The 16 **MANIFOLD + flips>0** fixtures are the most diagnostic
class — closed surfaces with locally inverted normals. pymeshfix's
`repair()` returns these "unchanged" because the topology is
already a watertight 2-manifold, but the orientation IS broken.
Samples: Me1140, Me1142, Me1156, Me1159, Me1160, Me149, Me357, Me530.

## Differential vs pymeshfix on the audit #479 set

Of the 60 fixtures pymeshfix marked "unchanged":

| pyvista verdict | count | % |
|---|---:|---:|
| **catches a defect** (non-manifold OR flips>0) | **45** | **75** |
| also clean | 15 | 25 |

**75% of pymeshfix's blind spot is recovered.** The 15 fixtures
genuinely clean to both oracles are: Me007, Me147, Me157, Me227,
Me254, Me364, Me680, Me740, Me810, Me851, Me1020, Me1053, Me1155,
Me1158, Me1173. (Five of these — Me740, Me810, Me851, Me1020, Me1053
— are the long-tail "well-formed reference mesh" controls that *should*
be clean.)

Of the 45 caught: 37 are non-manifold-only (pymeshfix's edge-count
proxy missed), 7 are orientation-only (manifold but flips>0), 1 is
both. The orientation-only catches are the most interesting because
no edge-count-based oracle would ever surface them.

## Cost

| metric | value |
|---|---:|
| min duration  | 0.7 ms |
| median        | 0.7 ms |
| max           | 15.5 ms |
| total (754 fixtures) | 568 ms |

Negligible. Pure-Python wrapper over VTK; no subprocess fork per
fixture. Adding pyvista to a full-corpus sweep adds <1 sec.

## Sample fixtures per class (8 each)

- **NON-MANIFOLD + flips>0** (25 total): Me001, Me016, Me021,
  Me1101, Me1102, Me1114, Me1123, Me1124
- **NON-MANIFOLD + flips=0** (682 total): Me002, Me003, Me004,
  Me005, Me006, Me008, Me009, Me010
- **MANIFOLD + flips>0** (16 total): Me1140, Me1142, Me1156,
  Me1159, Me1160, Me149, Me357, Me530
- **MANIFOLD + flips=0** (31 total): Me007, Me040, Me088, Me1020,
  Me1021, Me1022, Me1053, Me1054

## Reproduction

```bash
cd validation && uv run python -c "
from pathlib import Path
from step_corpus._pyvista_oracle import run_pyvista
for f in sorted(Path('../mesh-examples/12-14-mesh').glob('Me*.mesh.json')):
    r = run_pyvista(f)
    print(f.stem, r['status'], r.get('is_manifold'),
          r.get('n_orientation_flipped'))
"
```

Full corpus run takes <1 second on macOS arm64.

## Next steps (deferred)

- Promote the 15-fixture clean-to-both set as a candidate
  "well-formed reference" pool for negative-control work.
- Hand-audit a sample of the 16 MANIFOLD+flips>0 fixtures —
  these are the strongest candidates for "we thought it was a
  topology defect but it's really an orientation defect" catalog
  re-classification. If catalog's claimed mechanism is topological
  and the fixture's only real defect is orientation, the mechanism
  string is misleading.
- Consider extending `_mesh_oracle.py` (per-assertion) with an
  `is_manifold` assertion so fixtures that *claim* manifoldness
  can be auto-flagged against pyvista's verdict.
