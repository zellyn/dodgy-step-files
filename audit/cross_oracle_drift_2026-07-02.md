# Cross-Oracle DRIFT Audit — 2026-07-02

## Summary

- Catalog entries: 3153
- Scanned (baseline present, Expected populated, not §12.14): 2388
- Skipped §12.14 mesh: 760
- Skipped (no baseline JSON): 0
- Skipped (no Expected line): 5

- **Total DRIFT flags raised: 1945**
  - HIGH confidence: 94
  - MEDIUM confidence: 1505
  - LOW confidence: 346

### Flags by DRIFT type

| Type | Count | Band |
|------|-------|------|
| `occt_mismatch` | 16 | HIGH |
| `gmsh_mismatch` | 78 | HIGH |
| `occt_heal_split` | 0 | HIGH |
| `gmsh_heal_split` | 0 | HIGH |
| `stale_ifc_mentioned_missing` | 0 | HIGH |
| `unmentioned_manifold_diverges` | 1032 | MEDIUM |
| `unmentioned_ocaf_diverges` | 463 | MEDIUM |
| `ifc_mismatch` | 10 | MEDIUM |
| `unmentioned_part21_diverges` | 346 | LOW |
| `unmentioned_ifcopenshell_active` | 0 | LOW |

## Per-DRIFT-type detail

### `occt_mismatch` — 16 hits

_Expected `occt=` value does not match live `occt_heal_on/off`. Catalog Expected line is stale vs. runtime oracle._

- **Ad095** (§12.11): expected=shape(1) live=empty
- **Tsh074** (§12.3a): expected=unknown live=shape(1)
- **Tsh075** (§12.3a): expected=unknown live=shape(1)
- **Tsh076** (§12.3a): expected=unknown live=shape(1)
- **Tsh077** (§12.3a): expected=unknown live=shape(1)
- **Tsh078** (§12.3a): expected=unknown live=shape(1)
- **Tsh088** (§12.3a): expected=shape(1) live=shape(2)
- **Tsh092** (§12.3a): expected=shape(1) live=shape(2)
- **Tsh097** (§12.3a): expected=empty live=shape(1)
- **Tsh107** (§12.3a): expected=empty live=shape(1)
- **Tsh175** (§12.3a): expected=empty live=shape(1)
- **Tsh176** (§12.3a): expected=empty live=shape(1)
- **Tsh179** (§12.3a): expected=empty live=shape(1)
- **Tsh187** (§12.3a): expected=empty live=shape(1)
- **Tsh189** (§12.3a): expected=empty live=shape(1)
- **Tsh190** (§12.3a): expected=empty live=shape(1)

### `gmsh_mismatch` — 78 hits

_Expected `gmsh=` value does not match live `gmsh_autofix_on`. Catalog Expected line is stale vs. runtime oracle._

- **Ad095** (§12.11): expected=shape(1) live_on=empty
- **Gs191** (§12.2c): expected=shape(2) live_on=shape(18)
- **Tsh069** (§12.3a): expected=shape(14) live_on=shape(19)
- **Tsh070** (§12.3a): expected=shape(15) live_on=shape(14)
- **Tsh071** (§12.3a): expected=shape(13) live_on=shape(16)
- **Tsh072** (§12.3a): expected=shape(15) live_on=shape(13)
- **Tsh074** (§12.3a): expected=unknown live_on=shape(10)
- **Tsh075** (§12.3a): expected=unknown live_on=reject
- **Tsh076** (§12.3a): expected=unknown live_on=shape(27)
- **Tsh077** (§12.3a): expected=unknown live_on=empty
- **Tsh078** (§12.3a): expected=unknown live_on=shape(9)
- **Tsh084** (§12.3a): expected=empty live_on=shape(9)
- **Tsh085** (§12.3a): expected=empty live_on=shape(15)
- **Tsh086** (§12.3a): expected=empty live_on=shape(18)
- **Tsh087** (§12.3a): expected=empty live_on=shape(19)
- **Tsh088** (§12.3a): expected=empty live_on=shape(18)
- **Tsh089** (§12.3a): expected=empty live_on=shape(25)
- **Tsh090** (§12.3a): expected=empty live_on=shape(9)
- **Tsh091** (§12.3a): expected=empty live_on=shape(10)
- **Tsh092** (§12.3a): expected=empty live_on=shape(18)
- **Tsh093** (§12.3a): expected=empty live_on=shape(2)
- **Tsh097** (§12.3a): expected=empty live_on=shape(18)
- **Tsh100** (§12.3a): expected=reject live_on=shape(15)
- **Tsh101** (§12.3a): expected=shape(16) live_on=shape(18)
- **Tsh104** (§12.3a): expected=shape(9) live_on=shape(15)
- **Tsh107** (§12.3a): expected=empty live_on=shape(17)
- **Tsh130** (§12.3a): expected=reject live_on=shape(25)
- **Tsh131** (§12.3a): expected=reject live_on=shape(26)
- **Tsh132** (§12.3a): expected=shape(36) live_on=shape(25)
- **Tsh141** (§12.3a): expected=empty live_on=shape(15)
- _...and 48 more_

### `occt_heal_split` — 0 hits

_Live `occt_heal_on` != `occt_heal_off` but Expected uses collapsed `X/X` form — heal step changes outcome, and Expected obscures it._

_no hits_

### `gmsh_heal_split` — 0 hits

_Live `gmsh_autofix_on` != `gmsh_autofix_off` but Expected omits the split — autofix step changes outcome, and Expected obscures it._

_no hits_

### `stale_ifc_mentioned_missing` — 0 hits

_Expected mentions `ifc=` but baseline lacks any `ifcopenshell` field._

_no hits_

### `unmentioned_manifold_diverges` — 1032 hits

_Expected line does not mention manifold, but live manifold oracle reports a non-trivial state (process_signal, not_manifold with shape(1), or nonfinitevertex)._

- **Pf001** (§12.10): manifold=not_manifold but occt=shape(1) accepted
- **Pf008** (§12.10): manifold=not_manifold but occt=shape(1) accepted
- **Pf015** (§12.10): manifold=not_manifold but occt=shape(1) accepted
- **Pf017** (§12.10): manifold=not_manifold but occt=shape(1) accepted
- **Pf020** (§12.10): manifold=not_manifold but occt=shape(1) accepted
- **Pf022** (§12.10): manifold=not_manifold but occt=shape(1) accepted
- **Pf027** (§12.10): manifold=not_manifold but occt=shape(1) accepted
- **Pf028** (§12.10): manifold=not_manifold but occt=shape(1) accepted
- **Pf033** (§12.10): manifold=not_manifold but occt=shape(1) accepted
- **Pf034** (§12.10): manifold=not_manifold but occt=shape(1) accepted
- **Pf035** (§12.10): manifold=not_manifold but occt=shape(1) accepted
- **Pf038** (§12.10): manifold=not_manifold but occt=shape(1) accepted
- **Pf039** (§12.10): manifold=not_manifold but occt=shape(1) accepted
- **Ad055** (§12.11): manifold=not_manifold but occt=shape(1) accepted
- **Ad064** (§12.11): manifold=not_manifold but occt=shape(1) accepted
- **Ad077** (§12.11): manifold=not_manifold but occt=shape(1) accepted
- **Ad084** (§12.11): manifold=not_manifold but occt=shape(1) accepted
- **Ad116** (§12.11): manifold=not_manifold but occt=shape(1) accepted
- **Ad117** (§12.11): manifold=not_manifold but occt=shape(1) accepted
- **Ad120** (§12.11): manifold=not_manifold but occt=shape(1) accepted
- **Ad121** (§12.11): manifold=not_manifold but occt=shape(1) accepted
- **Ad122** (§12.11): manifold=not_manifold but occt=shape(1) accepted
- **Ad123** (§12.11): manifold=not_manifold but occt=shape(1) accepted
- **Ad124** (§12.11): manifold=not_manifold but occt=shape(1) accepted
- **Ad125** (§12.11): manifold=not_manifold but occt=shape(1) accepted
- **Ad126** (§12.11): manifold=not_manifold but occt=shape(1) accepted
- **Ad127** (§12.11): manifold=not_manifold but occt=shape(1) accepted
- **Ad128** (§12.11): manifold=not_manifold but occt=shape(1) accepted
- **Ad129** (§12.11): manifold=not_manifold but occt=shape(1) accepted
- **Ad130** (§12.11): manifold=not_manifold but occt=shape(1) accepted
- _...and 1002 more_

### `unmentioned_ocaf_diverges` — 463 hits

_Expected line does not mention ocaf, but live ocaf reports failed / signal / root_labels=2 (assembly-layer signal is silently unclaimed)._

- **Pf018** (§12.10): ocaf=root_labels=2 (expected line does not mention ocaf)
- **Pf029** (§12.10): ocaf=root_labels=2 (expected line does not mention ocaf)
- **Ad001** (§12.11): ocaf=failed (expected line does not mention ocaf)
- **Ad002** (§12.11): ocaf=failed (expected line does not mention ocaf)
- **Ad004** (§12.11): ocaf=failed (expected line does not mention ocaf)
- **Ad005** (§12.11): ocaf=failed (expected line does not mention ocaf)
- **Ad014** (§12.11): ocaf=failed (expected line does not mention ocaf)
- **Ad015** (§12.11): ocaf=signal(11) (expected line does not mention ocaf)
- **Ad026** (§12.11): ocaf=failed (expected line does not mention ocaf)
- **Ad027** (§12.11): ocaf=failed (expected line does not mention ocaf)
- **Ad030** (§12.11): ocaf=failed (expected line does not mention ocaf)
- **Ad031** (§12.11): ocaf=failed (expected line does not mention ocaf)
- **Ad032** (§12.11): ocaf=failed (expected line does not mention ocaf)
- **Ad033** (§12.11): ocaf=failed (expected line does not mention ocaf)
- **Ad035** (§12.11): ocaf=failed (expected line does not mention ocaf)
- **Ad038** (§12.11): ocaf=failed (expected line does not mention ocaf)
- **Ad042** (§12.11): ocaf=failed (expected line does not mention ocaf)
- **Ad043** (§12.11): ocaf=failed (expected line does not mention ocaf)
- **Ad044** (§12.11): ocaf=failed (expected line does not mention ocaf)
- **Ad045** (§12.11): ocaf=failed (expected line does not mention ocaf)
- **Ad046** (§12.11): ocaf=failed (expected line does not mention ocaf)
- **Ad047** (§12.11): ocaf=failed (expected line does not mention ocaf)
- **Ad049** (§12.11): ocaf=failed (expected line does not mention ocaf)
- **Ad050** (§12.11): ocaf=signal(11) (expected line does not mention ocaf)
- **Ad051** (§12.11): ocaf=failed (expected line does not mention ocaf)
- **Ad052** (§12.11): ocaf=failed (expected line does not mention ocaf)
- **Ad056** (§12.11): ocaf=failed (expected line does not mention ocaf)
- **Ad057** (§12.11): ocaf=failed (expected line does not mention ocaf)
- **Ad059** (§12.11): ocaf=failed (expected line does not mention ocaf)
- **Ad080** (§12.11): ocaf=failed (expected line does not mention ocaf)
- _...and 433 more_

### `ifc_mismatch` — 10 hits

_Expected `ifc=` value does not match live `ifcopenshell` value (e.g. schema_n/a vs reject)._

- **Tsh084** (§12.3a): expected=accept(0) live=schema_n/a
- **Tsh085** (§12.3a): expected=accept(0) live=schema_n/a
- **Tsh086** (§12.3a): expected=accept(0) live=schema_n/a
- **Tsh087** (§12.3a): expected=accept(0) live=schema_n/a
- **Tsh088** (§12.3a): expected=accept(0) live=schema_n/a
- **Tsh089** (§12.3a): expected=accept(0) live=schema_n/a
- **Tsh090** (§12.3a): expected=accept(0) live=schema_n/a
- **Tsh091** (§12.3a): expected=accept(0) live=schema_n/a
- **Tsh092** (§12.3a): expected=accept(0) live=schema_n/a
- **Tsh093** (§12.3a): expected=accept(0) live=schema_n/a

### `unmentioned_part21_diverges` — 346 hits

_Expected line does not mention part21_strict, but live part21_strict reports reject/warn (parser-layer signal not claimed)._

- **Pf001** (§12.10): part21=reject(E_UNRESOLVED_REFS) (expected line does not mention part21)
- **Pf003** (§12.10): part21=warn(W_FORWARD_REF) (expected line does not mention part21)
- **Pf010** (§12.10): part21=warn(W_FORWARD_REF) (expected line does not mention part21)
- **Pf032** (§12.10): part21=reject(E_UNRESOLVED_REFS) (expected line does not mention part21)
- **Pf035** (§12.10): part21=reject(E_UNRESOLVED_REFS) (expected line does not mention part21)
- **Pf036** (§12.10): part21=warn(W_COMPLEX_ORDER) (expected line does not mention part21)
- **Pf037** (§12.10): part21=reject(E_UNRESOLVED_REFS) (expected line does not mention part21)
- **Pf038** (§12.10): part21=reject(E_UNRESOLVED_REFS) (expected line does not mention part21)
- **Pf039** (§12.10): part21=reject(E_UNRESOLVED_REFS) (expected line does not mention part21)
- **Ad004** (§12.11): part21=warn(W_COMPLEX_ORDER) (expected line does not mention part21)
- **Ad005** (§12.11): part21=reject(E_UNRESOLVED_REFS) (expected line does not mention part21)
- **Ad015** (§12.11): part21=warn(W_FORWARD_REF) (expected line does not mention part21)
- **Ad026** (§12.11): part21=warn(W_COMPLEX_ORDER) (expected line does not mention part21)
- **Ad031** (§12.11): part21=reject(E_FILE_DESC_ARITY) (expected line does not mention part21)
- **Ad042** (§12.11): part21=reject(E_UNRESOLVED_REFS) (expected line does not mention part21)
- **Ad043** (§12.11): part21=reject(E_UNRESOLVED_REFS) (expected line does not mention part21)
- **Ad051** (§12.11): part21=reject(E_UNRESOLVED_REFS) (expected line does not mention part21)
- **Ad053** (§12.11): part21=warn(W_FORWARD_REF) (expected line does not mention part21)
- **Ad054** (§12.11): part21=warn(W_FORWARD_REF) (expected line does not mention part21)
- **Ad064** (§12.11): part21=reject(E_UNRESOLVED_REFS) (expected line does not mention part21)
- **Ad078** (§12.11): part21=reject(E_UNRESOLVED_REFS) (expected line does not mention part21)
- **Ad080** (§12.11): part21=warn(W_DUP_REF) (expected line does not mention part21)
- **Ad081** (§12.11): part21=reject(E_UNRESOLVED_REFS) (expected line does not mention part21)
- **Ad082** (§12.11): part21=warn(W_FORWARD_REF) (expected line does not mention part21)
- **Ad083** (§12.11): part21=reject(E_UNRESOLVED_REFS) (expected line does not mention part21)
- **Ad085** (§12.11): part21=warn(W_FORWARD_REF) (expected line does not mention part21)
- **Ad086** (§12.11): part21=reject(E_UNRESOLVED_REFS) (expected line does not mention part21)
- **Ad087** (§12.11): part21=reject(E_UNRESOLVED_REFS) (expected line does not mention part21)
- **Ad090** (§12.11): part21=reject(E_CLOSE_CASE) (expected line does not mention part21)
- **Ad096** (§12.11): part21=reject(E_UNRESOLVED_REFS) (expected line does not mention part21)
- _...and 316 more_

### `unmentioned_ifcopenshell_active` — 0 hits

_(unused) placeholder_

_no hits_

## Section breakdown (entries with at least one DRIFT flag)

| Section | Entries flagged |
|---------|-----------------|
| §12.3a | 238 |
| §12.3c | 216 |
| §12.3b | 129 |
| §12.6 | 109 |
| §12.2c | 107 |
| §12.8 | 91 |
| §12.2a | 84 |
| §12.11 | 76 |
| §12.4 | 76 |
| §12.7 | 76 |
| §12.2b | 66 |
| §12.13 | 59 |
| §12.1a | 55 |
| §12.1b | 46 |
| §12.1c | 46 |
| §12.12 | 44 |
| §12.5 | 37 |
| §12.10 | 20 |

## Confidence bands

- **HIGH (94)** — Value-level divergence between Expected and live baseline for oracles the Expected line explicitly claims (occt/gmsh/ifc), plus heal_on vs heal_off splits that the collapsed form hides. These are clear bugs in Expected; fix path is straightforward (regenerate Expected from live oracle per Accept-live-oracle policy).
- **MEDIUM (1505)** — Cross-oracle disagreement where an oracle NOT mentioned in Expected (manifold, ocaf) reports a non-trivial state that the fixture description likely implies but Expected silently drops. Requires judgment: is the oracle`s verdict part of the fixture`s claim, or an incidental side-effect?
- **LOW (346)** — part21_strict warnings/rejects that Expected omits. Often intentional (part21 is a parser-layer check tangential to the geometric defect). Edge cases likely explainable, but worth revisiting because ~200 W_FORWARD_REF/E_UNRESOLVED_REFS signals may be uncatalogued.

## Method

- Catalog: `/Users/zellyn/gh/dodgy-step-files/STEP_PROBLEM_CATALOG.json` (3153 entries)
- Baseline cache: `/tmp/cad-v2-out/<section_dir>/<id>.json`
- Expected parser: `occt=A/B gmsh=C ifc=D` -> {occt: (A,B), gmsh: C, ifc: D}
- Oracles compared: occt_heal_on/off, gmsh_autofix_on/off, ifcopenshell, manifold, ocaf, part21_strict
- Skipped: §12.14 mesh (760 entries), solvespace and brlcad (both universally `not_installed`)
