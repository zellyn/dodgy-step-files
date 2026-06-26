# B3.6 — Kernel-agreement diff-detection (pyvista folded in)

For each fixture, compute a tuple of normalized oracle verdicts; cluster
by tuple; surface low-frequency clusters (N≤3) as audit candidates.

This sweep folds in the new pyvista oracle (mesh side) on top of the
2026-06-24 baselines. brlcad and solvespace remain `not_installed`
locally so are excluded from the signature; their entries pre-exist
in the cache as the static `not_installed` token.

## STEP corpus — 2,224 fixtures

Signature: `(occt_heal_on, gmsh_autofix_on, ifcopenshell, manifold, ocaf)`,
each value coarsened to one of: `shape(N)`, `empty`, `reject`, `signal`,
`accept`, `ocaf_loaded`, `failed`, `step_read_failed`, `no_shapes_loaded`,
`process_signal`, `not_manifold`, `empty_mesh`, `nonfinitevertex`,
`schema_n/a`.

**19 distinct signatures.**

### Top 9 clusters (cover 99.0% of corpus)

| count | occt | gmsh | ifc | manifold | ocaf | example |
|---:|---|---|---|---|---|---|
| 837 | shape(N) | shape(N) | schema_n/a | not_manifold | ocaf_loaded | Pf001 |
| 483 | empty | empty | schema_n/a | no_shapes_loaded | ocaf_loaded | Ad078 |
| 279 | shape(N) | shape(N) | schema_n/a | empty_mesh | ocaf_loaded | Pf002 |
| 227 | empty | empty | schema_n/a | no_shapes_loaded | failed | Ad002 |
| 169 | signal | signal | schema_n/a | process_signal | signal | Ad015 |
| 104 | shape(N) | empty | schema_n/a | empty_mesh | ocaf_loaded | Gp161 |
| 42 | shape(N) | reject | schema_n/a | not_manifold | ocaf_loaded | Ad120 |
| 33 | shape(N) | reject | schema_n/a | empty_mesh | ocaf_loaded | Wr054 |
| 16 | reject | reject | schema_n/a | step_read_failed | failed | Ad001 |

### Small clusters (N=2–3): 5 clusters, 11 fixtures

| N | signature | fixtures |
|---:|---|---|
| 3 | occt=empty / gmsh=signal / manifold=no_shapes_loaded / ocaf=signal | M041, M042, M048 |
| 2 | occt=empty / gmsh=empty / ifc=accept / manifold=no_shapes_loaded / ocaf=failed | Xp041, Lh019 |
| 2 | occt=signal / gmsh=signal / ifc=reject / manifold=process_signal / ocaf=signal | Gn055, Gn058 |
| 2 | occt=shape(N) / gmsh=signal / manifold=not_manifold / ocaf=signal | A079, Pmi111 |
| 2 | occt=shape(N) / gmsh=signal / manifold=empty_mesh / ocaf=signal | Pmi006, Pmi019 |

### N=1 singletons (highest-info audit candidates)

| ID | signature | status |
|---|---|---|
| **Gn090** | occt=shape(N) / gmsh=reject / ifc=schema_n/a / manifold=`nonfinitevertex` / ocaf=ocaf_loaded | NEW — `nonfinitevertex` is a unique manifold3d return code not seen elsewhere in the corpus |
| Tfa153 | occt=empty / gmsh=reject / ifc=schema_n/a / manifold=no_shapes_loaded / ocaf=ocaf_loaded | Already audited in task #474 (CONCERN; live-oracle accept) |

**Net new STEP audit lead from this sweep: Gn090.** A nurbs B-spline
fixture where manifold3d's tessellation pass hits a non-finite vertex
(NaN/Inf in the surface evaluation), and gmsh outright rejects, but
OCCT happily loads + OCAF carries it to root_labels=1. That divergence
pattern is unique in the corpus.

---

## Mesh corpus — 760 fixtures

Signature: `(pymeshfix_outcome, pyvista_outcome)` where:
- `pymeshfix_outcome` ∈ {loaded-result class: `unchanged`, `shrunk`,
  `grew`, `zeroed`, `rejected`}
- `pyvista_outcome` ∈ {`manifold`, `manifold+flips`, `nonmanifold`,
  `nonmanifold+flips`, `rejected`}

**13 distinct signatures.**

| count | pymeshfix | pyvista | example |
|---:|---|---|---|
| **465** | zeroed | nonmanifold | Me003 |
| 165 | shrunk | nonmanifold | Me002 |
| 38 | unchanged | nonmanifold | Me008 |
| **15** | unchanged | **manifold** | Me007 |
| 14 | grew | nonmanifold | Me014 |
| 13 | shrunk | nonmanifold+flips | Me016 |
| 12 | shrunk | manifold | Me040 |
| 9 | shrunk | manifold+flips | Me1140 |
| 7 | grew | nonmanifold+flips | Me021 |
| **7** | unchanged | manifold+flips | Me1142 |
| 6 | rejected | rejected | Me140 |
| 5 | zeroed | nonmanifold+flips | Me001 |
| **4** | **zeroed** | **manifold** | Me1093 |

### High-information mesh clusters

#### Cluster A — "zeroed + manifold" (4 fixtures): pymeshfix–pyvista deep contradiction

Me1093, Me257, Me434, Me590.

pyvista calls the input mesh fully manifold; pymeshfix's repair
algorithm decides the entire mesh should be deleted (output = 0 triangles).
Either pymeshfix is being wildly conservative on legitimately clean
inputs, or pyvista's `is_manifold` check returns True vacuously on a
class of degenerate-but-edge-incidence-consistent meshes (e.g.
two-component manifolds where pymeshfix's algorithm trips on the
component-handling logic).

**Action**: hand-audit these 4. Highest-priority differential cases in
the mesh corpus.

#### Cluster B — "unchanged + manifold" (15 fixtures): genuine clean-to-both pool

Me007, Me147, Me157, Me227, Me254, Me364, Me680, Me740, Me810, Me851,
Me1020, Me1053, Me1155, Me1158, Me1173.

Both oracles call these clean. These are the strongest candidates for
**negative-control** promotion (mesh-side "well-formed reference"
fixtures). 5 of these (Me740, Me810, Me851, Me1020, Me1053) are
intentional well-formed control meshes per their catalog descriptions —
already serving as reference geometry. The other 10 are candidates for
similar promotion or for cross-reference notes.

**Action**: verify the 10 non-control entries are intentionally clean
(catalog mechanism is a code-path trigger that doesn't depend on mesh
defects); promote the rest into the negative-control set.

#### Cluster C — "unchanged + manifold+flips" (7 fixtures): audit #479 gap

Me149, Me357, Me530, Me575, Me713, Me892, Me1142.

These are the exact fixtures pymeshfix called "unchanged" but pyvista
flags as having orientation defects. **Already hand-audited 2026-06-25
in `manifold_orient_audit_2026-06-25.md` — all 7 are CORRECT_CATALOG
(catalog correctly names orientation/normals/code-path as the
mechanism).** No action needed; this is the documented gap closure.

#### Cluster D — "shrunk + manifold+flips" (9 fixtures): PMP.orient family

Me852, Me930, Me931, Me932, Me933, Me1140, Me1156, Me1159, Me1160.

The CGAL PMP `orient_to_bound_a_volume` family — all 9 documented as
nested-component / self-intersection / orientation defects in the
catalog. pymeshfix shrinks them (removing one component) and pyvista
sees the surviving manifold has flipped triangles. **Catalog already
correctly names the mechanism**; no action needed.

#### Other clusters (mass clusters, no singleton signal)

- "zeroed + nonmanifold" (465) — main body of the corpus; pymeshfix
  rejects, pyvista confirms non-manifold. Boring cluster.
- "shrunk + nonmanifold" (165) — partial-repair class; pymeshfix
  reduces triangle count, pyvista still flags non-manifold residuals.
- 38 + 14 + 13 + 7 + 12 + 5 = 89 other fixtures across non-singleton
  shrunk/grew/unchanged + non-manifold combinations. Routine defect
  patterns; no per-fixture audit warranted.

---

## Summary

- **STEP**: 2,224 fixtures, 19 signatures, 2 singletons. **1 new audit
  candidate**: Gn090 (`nonfinitevertex` unique to it).
- **Mesh**: 760 fixtures, 13 signatures. **4 new audit candidates**
  (Me1093, Me257, Me434, Me590 — "zeroed + manifold" contradiction)
  + **10 promotion candidates** for the negative-control pool.
- **0 false positives** from the audit #479 gap-closure check —
  all 7 "unchanged + manifold+flips" + 9 "shrunk + manifold+flips"
  fixtures already correctly classified in the catalog.

Total new audit leads from this B3.6 pass: **5 fixtures** (1 STEP +
4 mesh), down from B3.6 v1's 188 STEP candidates because the
v1 audits cleared the prior noise. The diff-detection apparatus
is now in steady state: ~5 leads per refresh, surfacing only what
new oracle wiring reveals.

## Reproduction

```bash
cd validation && uv run python -m step_corpus._oracle_disagreement_baseline
# Mesh side: regenerate /tmp/b3_6_mesh_sigs.json via the snippet
# embedded in this audit's commit message.
```
