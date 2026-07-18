# Q5 Provenance-Tier Re-classification Proposal — 2026-07-01

**Scope.** Rule-based scan of every entry currently tagged `bytes-sufficient` (or where `provenance_tier` is missing/default) in `STEP_PROBLEM_CATALOG.json`. Uses text signals only (title/description/notes/sources/category/fixture_kind/pair_with). Parallel to the mutation-test job (PID 94338) which will produce oracle-visibility data separately.

**Ground-rules honoured.** No catalog / code / schema edits; audit-only. No new tiers proposed. Priority order when signals conflict: `bytes-only` > `requires-sibling-pair` > `cross-file-state` > `runtime-only` > `writer-side`. Self-declared tier statements in notes/description trump priority ordering.

## Summary

- Total entries scanned in `bytes-sufficient` bucket: **3057**
- Total entries with proposed re-tag: **226** (7.4% of the default bucket)
- Confidence split: **55 HIGH + 117 MEDIUM + 54 LOW**

| Proposed tier | Total | HIGH | MEDIUM | LOW |
|---|---:|---:|---:|---:|
| `requires-sibling-pair` | 35 | 6 | 15 | 14 |
| `cross-file-state` | 7 | 0 | 3 | 4 |
| `runtime-only` | 74 | 27 | 35 | 12 |
| `writer-side` | 110 | 22 | 64 | 24 |

If accepted at HIGH-only, `bytes-sufficient` shrinks by 55 (3057 → 3002). If accepted at HIGH+MEDIUM it shrinks by 172 (3057 → 2885). Accepting LOW-band adds another 54 but each of those wants a hand-review.

## Per-tier proposals

### `requires-sibling-pair` proposals (35)

#### HIGH — 6

- **Wr019** [sec 12.13] `bytes-sufficient → requires-sibling-pair` — self_declared_tier: "notes/desc explicitly say provenance_tier: requires-sibling-pair" _(also matched: writer-side)_
- **Wr021** [sec 12.13] `bytes-sufficient → requires-sibling-pair` — self_declared_tier: "notes/desc explicitly say provenance_tier: requires-sibling-pair" _(also matched: writer-side)_
- **Wr022** [sec 12.13] `bytes-sufficient → requires-sibling-pair` — self_declared_tier: "notes/desc explicitly say provenance_tier: requires-sibling-pair" _(also matched: writer-side)_
- **Wr023** [sec 12.13] `bytes-sufficient → requires-sibling-pair` — self_declared_tier: "notes/desc explicitly say provenance_tier: requires-sibling-pair" _(also matched: writer-side)_
- **Wr026** [sec 12.13] `bytes-sufficient → requires-sibling-pair` — self_declared_tier: "notes/desc explicitly say provenance_tier: requires-sibling-pair" _(also matched: writer-side)_
- **Wr031** [sec 12.13] `bytes-sufficient → requires-sibling-pair` — self_declared_tier: "notes/desc explicitly say provenance_tier: requires-sibling-pair" _(also matched: writer-side)_

#### MEDIUM — 15

- **A017** [sec 12.6] `bytes-sufficient → requires-sibling-pair` — round_trip_loss: "round-trip | a component carries a placement transform attached at the face / ed"
- **A019** [sec 12.6] `bytes-sufficient → requires-sibling-pair` — round_trip_loss: "lost on round-trip"
- **A029** [sec 12.6] `bytes-sufficient → requires-sibling-pair` — round_trip_loss: "round-trip loses the binding because the receiver expects a different target. | "
- **A068** [sec 12.6] `bytes-sufficient → requires-sibling-pair` — round_trip_loss: "lost on round-trip"
- **Gn016** [sec 12.2b] `bytes-sufficient → requires-sibling-pair` — round_trip_loss: "round-trip | writing a `surface_of_revolution` built on an `ellipse` to step and"
- **Gp031** [sec 12.2a] `bytes-sufficient → requires-sibling-pair` — round_trip_loss: "round-trip (or other translator path), a cylindrical face appears with two disti"
- **Gs024** [sec 12.2c] `bytes-sufficient → requires-sibling-pair` — round_trip_loss: "round-trip planar face becomes trimmed b-spline (degree-1 nurbs) | untrimmed `pl"
- **M010** [sec 12.8] `bytes-sufficient → requires-sibling-pair` — round_trip_loss: "lost on round-trip"
- **M025** [sec 12.8] `bytes-sufficient → requires-sibling-pair` — round_trip_loss: "round-trip vs always recomputed | ap242 supports tessellated geometry via `tesse"
- **N044** [sec 12.4] `bytes-sufficient → requires-sibling-pair` — round_trip_loss: "round-trip because the receiver renumbered topology. | **see also**: a011, a028,"
- **Pmi057** [sec 12.7] `bytes-sufficient → requires-sibling-pair` — round_trip_loss: "lost on round-trip"
- **Pmi059** [sec 12.7] `bytes-sufficient → requires-sibling-pair` — round_trip_loss: "lost on round-trip"
- **Tb010** [sec 12.4] `bytes-sufficient → requires-sibling-pair` — round_trip_loss: "round-trip the coordinates collapse to `(0, 0, 0)`, `(1, 0, 0)`, `(2, 0, 0)`, `("
- **Wr054** [sec 12.13] `bytes-sufficient → requires-sibling-pair` — round_trip_loss: "round-trip | a spherical_surface in an open_shell has its enclosing advanced_fac" _(also matched: writer-side)_
- **Wr062** [sec 12.13] `bytes-sufficient → requires-sibling-pair` — round_trip_loss: "round-trip loses colour_rgb and assembly hierarchy | a step file authored with c" _(also matched: writer-side)_

#### LOW — 14

- **A010** [sec 12.6] `bytes-sufficient → requires-sibling-pair` — round_trip_loss: "lost on round-trip" _(also matched: writer-side)_
- **A087** [sec 12.6] `bytes-sufficient → requires-sibling-pair` — round_trip_loss: "round-trip drops bodies", "import then export produces empty file". | §12.6 asse" _(also matched: writer-side)_
- **Gn014** [sec 12.2b] `bytes-sufficient → requires-sibling-pair` — round_trip_loss: "round-trip is the canonical lossy path. | **see also**: gs024, n030. **occ behav" _(also matched: writer-side)_
- **Pmi079** [sec 12.7] `bytes-sufficient → requires-sibling-pair` — round_trip_loss: "round-trip | a dimension pmi is created in the source cad tool, imported correct" _(also matched: writer-side)_
- **Pmi094** [sec 12.7] `bytes-sufficient → requires-sibling-pair` — round_trip_loss: "round-trip to step ap242 pmi | an xcaf document has a flatness tolerance, a posi" _(also matched: writer-side)_
- **Tfa068** [sec 12.3c] `bytes-sufficient → requires-sibling-pair` — round_trip_loss: "lost on round-trip" _(also matched: writer-side)_
- **Wr006** [sec 12.13] `bytes-sufficient → requires-sibling-pair` — round_trip_loss: "round-trip | coordinates that were entered as exact rationals or simple decimals" _(also matched: writer-side)_
- **Wr020** [sec 12.13] `bytes-sufficient → requires-sibling-pair` — round_trip_loss: "round-trip data loss" _(also matched: writer-side)_
- **Wr024** [sec 12.13] `bytes-sufficient → requires-sibling-pair` — round_trip_loss: "round-trip data loss" _(also matched: writer-side)_
- **Wr025** [sec 12.13] `bytes-sufficient → requires-sibling-pair` — round_trip_loss: "round-trip data loss" _(also matched: writer-side)_
- **Wr036** [sec 12.13] `bytes-sufficient → requires-sibling-pair` — round_trip_loss: "round-trip data loss" _(also matched: writer-side)_
- **Wr037** [sec 12.13] `bytes-sufficient → requires-sibling-pair` — round_trip_loss: "lost on re-export" _(also matched: writer-side)_
- **Wr040** [sec 12.13] `bytes-sufficient → requires-sibling-pair` — round_trip_loss: "lost on re-export" _(also matched: writer-side)_
- **Wr059** [sec 12.13] `bytes-sufficient → requires-sibling-pair` — round_trip_loss: "round-trip inflates cylinder analytic surface into b-spline | the brep intermedi" _(also matched: writer-side)_

### `cross-file-state` proposals (7)

#### MEDIUM — 3

- **N052** [sec 12.4] `bytes-sufficient → cross-file-state` — fixture_kind_ktp: "kernel-test-pair"
- **N055** [sec 12.4] `bytes-sufficient → cross-file-state` — fixture_kind_ktp: "kernel-test-pair"
- **P026** [sec 12.6] `bytes-sufficient → cross-file-state` — process_state: "process state"

#### LOW — 4

- **A012** [sec 12.6] `bytes-sufficient → cross-file-state` — external_file_ref: "external file reference" _(also matched: runtime-only)_
- **A104** [sec 12.6] `bytes-sufficient → cross-file-state` — multi_file: "multi-file" _(also matched: writer-side)_
- **Pf010** [sec 12.10] `bytes-sufficient → cross-file-state` — external_file_ref: "external_file" _(also matched: runtime-only)_
- **Pf022** [sec 12.10] `bytes-sufficient → cross-file-state` — process_state: "in-memory state leakage" _(also matched: runtime-only, writer-side)_

### `runtime-only` proposals (74)

#### HIGH — 27

- **Ad052** [sec 12.11] `bytes-sufficient → runtime-only` — infinite_loop: "infinite loop"
- **Ad098** [sec 12.11] `bytes-sufficient → runtime-only` — stack_overflow: "stack overflow"
- **Gb001** [sec 12.2c] `bytes-sufficient → runtime-only` — self_declared_tier: "notes/desc explicitly say provenance_tier: runtime-only" _(also matched: requires-sibling-pair)_
- **Gb002** [sec 12.2c] `bytes-sufficient → runtime-only` — self_declared_tier: "notes/desc explicitly say provenance_tier: runtime-only" _(also matched: requires-sibling-pair)_
- **Gb003** [sec 12.2c] `bytes-sufficient → runtime-only` — self_declared_tier: "notes/desc explicitly say provenance_tier: runtime-only" _(also matched: requires-sibling-pair)_
- **Pf001** [sec 12.10] `bytes-sufficient → runtime-only` — oom_receiver: "until oom"
- **Pf002** [sec 12.10] `bytes-sufficient → runtime-only` — quadratic_algo: "quadratic-cost"
- **Pf005** [sec 12.10] `bytes-sufficient → runtime-only` — slow_import_read: "slow step import"
- **Pf006** [sec 12.10] `bytes-sufficient → runtime-only` — quadratic_algo: "quadratic self"
- **Pf008** [sec 12.10] `bytes-sufficient → runtime-only` — stack_overflow: "stack overflow"
- **Pf009** [sec 12.10] `bytes-sufficient → runtime-only` — stack_overflow: "stack overflow"
- **Pf011** [sec 12.10] `bytes-sufficient → runtime-only` — stack_overflow: "stack overflow"
- **Pf012** [sec 12.10] `bytes-sufficient → runtime-only` — stack_overflow: "stack overflow"
- **Pf016** [sec 12.10] `bytes-sufficient → runtime-only` — infinite_loop: "infinite loop"
- **Pf018** [sec 12.10] `bytes-sufficient → runtime-only` — memory_leak: "memory not released"
- **Pf019** [sec 12.10] `bytes-sufficient → runtime-only` — memory_leak: "memory leaks"
- **Pf021** [sec 12.10] `bytes-sufficient → runtime-only` — runtime_crash_nondet: "floating / non"
- **Pf023** [sec 12.10] `bytes-sufficient → runtime-only` — infinite_loop: "infinite loop"
- **Pf024** [sec 12.10] `bytes-sufficient → runtime-only` — infinite_loop: "infinite loop"
- **Pf025** [sec 12.10] `bytes-sufficient → runtime-only` — infinite_loop: "infinite loop"
- **Pf029** [sec 12.10] `bytes-sufficient → runtime-only` — process_abort: "aborts process"
- **Pf030** [sec 12.10] `bytes-sufficient → runtime-only` — bomb_expansion: "schema-express where-rule evaluation bomb"
- **Pf033** [sec 12.10] `bytes-sufficient → runtime-only` — long_running_op: "long-running mesh"
- **Pf035** [sec 12.10] `bytes-sufficient → runtime-only` — infinite_loop: "infinite loop"
- **Pf036** [sec 12.10] `bytes-sufficient → runtime-only` — infinite_loop: "infinite loop"
- **Pf038** [sec 12.10] `bytes-sufficient → runtime-only` — memory_leak: "memory not released"
- **Pf039** [sec 12.10] `bytes-sufficient → runtime-only` — infinite_loop: "infinite loop"

#### MEDIUM — 35

- **Ad002** [sec 12.11] `bytes-sufficient → runtime-only` — stack_overflow: "stack overflow"
- **Ad004** [sec 12.11] `bytes-sufficient → runtime-only` — infinite_loop: "infinite recursion"
- **Ad026** [sec 12.11] `bytes-sufficient → runtime-only` — infinite_loop: "infinite loop"
- **Ad027** [sec 12.11] `bytes-sufficient → runtime-only` — bomb_expansion: "billion-laughs"
- **Ad031** [sec 12.11] `bytes-sufficient → runtime-only` — bomb_expansion: "billion-laughs"
- **Ad032** [sec 12.11] `bytes-sufficient → runtime-only` — bomb_expansion: "schema-express rule recursion bomb"
- **Ad035** [sec 12.11] `bytes-sufficient → runtime-only` — bomb_expansion: "billion-laughs"
- **Ad042** [sec 12.11] `bytes-sufficient → runtime-only` — bomb_expansion: "billion-laughs"
- **Ad044** [sec 12.11] `bytes-sufficient → runtime-only` — bomb_expansion: "billion-laughs"
- **Ad045** [sec 12.11] `bytes-sufficient → runtime-only` — bomb_expansion: "billion-laughs"
- **Ad053** [sec 12.11] `bytes-sufficient → runtime-only` — infinite_loop: "infinite loop"
- **Ad054** [sec 12.11] `bytes-sufficient → runtime-only` — hang_indefinitely: "loops forever"
- **Ad055** [sec 12.11] `bytes-sufficient → runtime-only` — stack_overflow: "stack overflow"
- **Ad057** [sec 12.11] `bytes-sufficient → runtime-only` — memory_leak: "memory leak"
- **Ad077** [sec 12.11] `bytes-sufficient → runtime-only` — infinite_loop: "infinite loop"
- **Ad081** [sec 12.11] `bytes-sufficient → runtime-only` — process_abort: "abort the process"
- **Ad083** [sec 12.11] `bytes-sufficient → runtime-only` — bomb_expansion: "billion-laughs"
- **Ad099** [sec 12.11] `bytes-sufficient → runtime-only` — infinite_loop: "infinite loop"
- **Ad117** [sec 12.11] `bytes-sufficient → runtime-only` — process_abort: "process aborts"
- **Ad128** [sec 12.11] `bytes-sufficient → runtime-only` — stack_overflow: "stack overflow"
- **Gs054** [sec 12.2c] `bytes-sufficient → runtime-only` — stack_overflow: "stack overflow"
- **Gs097** [sec 12.2c] `bytes-sufficient → runtime-only` — unbounded_memory: "unbounded recursion"
- **M141** [sec 12.8] `bytes-sufficient → runtime-only` — infinite_loop: "infinite recursion"
- **M144** [sec 12.8] `bytes-sufficient → runtime-only` — never_terminates: "never terminates"
- **Me025** [sec 12.14] `bytes-sufficient → runtime-only` — infinite_loop: "infinite loop"
- **Me1173** [sec 12.14] `bytes-sufficient → runtime-only` — infinite_loop: "infinite recursion"
- **Pmi062** [sec 12.7] `bytes-sufficient → runtime-only` — bomb_expansion: "explosion"
- **Pmi111** [sec 12.7] `bytes-sufficient → runtime-only` — unbounded_memory: "unbounded recursion"
- **Tfa063** [sec 12.3c] `bytes-sufficient → runtime-only` — stack_overflow: "stack overflow"
- **Tsh056** [sec 12.3a] `bytes-sufficient → runtime-only` — infinite_loop: "infinite loop"
- **Tsh201** [sec 12.3a] `bytes-sufficient → runtime-only` — unbounded_memory: "unbounded iteration"
- **Twi034** [sec 12.3b] `bytes-sufficient → runtime-only` — never_terminates: "never returns"
- **Twi041** [sec 12.3b] `bytes-sufficient → runtime-only` — infinite_loop: "infinite loop"
- **Xp007** [sec 12.12] `bytes-sufficient → runtime-only` — stack_overflow: "stack overflow"
- **Xp023** [sec 12.12] `bytes-sufficient → runtime-only` — stack_overflow: "stack overflow"

#### LOW — 12

- **Le060** [sec 12.1a] `bytes-sufficient → runtime-only` — infinite_loop: "infinite loop" _(also matched: writer-side)_
- **Pf003** [sec 12.10] `bytes-sufficient → runtime-only` — section_12.10: "Pf performance/runtime section"
- **Pf007** [sec 12.10] `bytes-sufficient → runtime-only` — section_12.10: "Pf performance/runtime section"
- **Pf013** [sec 12.10] `bytes-sufficient → runtime-only` — section_12.10: "Pf performance/runtime section"
- **Pf014** [sec 12.10] `bytes-sufficient → runtime-only` — section_12.10: "Pf performance/runtime section"
- **Pf017** [sec 12.10] `bytes-sufficient → runtime-only` — section_12.10: "Pf performance/runtime section"
- **Pf027** [sec 12.10] `bytes-sufficient → runtime-only` — section_12.10: "Pf performance/runtime section"
- **Pf028** [sec 12.10] `bytes-sufficient → runtime-only` — section_12.10: "Pf performance/runtime section"
- **Pf031** [sec 12.10] `bytes-sufficient → runtime-only` — section_12.10: "Pf performance/runtime section"
- **Pf032** [sec 12.10] `bytes-sufficient → runtime-only` — section_12.10: "Pf performance/runtime section"
- **Pf034** [sec 12.10] `bytes-sufficient → runtime-only` — section_12.10: "Pf performance/runtime section"
- **Pf037** [sec 12.10] `bytes-sufficient → runtime-only` — section_12.10: "Pf performance/runtime section"

### `writer-side` proposals (110)

#### HIGH — 22

- **Ad133** [sec 12.11] `bytes-sufficient → writer-side` — step_writer_noun: "step writer"
- **Wr001** [sec 12.13] `bytes-sufficient → writer-side` — save_export_bug: "exports for change-detection see noise on every line, version-control systems sh"
- **Wr002** [sec 12.13] `bytes-sufficient → writer-side` — emitted_by_writer: "emitted by writer"
- **Wr004** [sec 12.13] `bytes-sufficient → writer-side` — save_export_bug: "exports do. bug"
- **Wr007** [sec 12.13] `bytes-sufficient → writer-side` — locale_writer: "locale-aware formatter"
- **Wr009** [sec 12.13] `bytes-sufficient → writer-side` — writer_strips_omits: "writer omits"
- **Wr017** [sec 12.13] `bytes-sufficient → writer-side` — re_export_generic: "re-exported"
- **Wr032** [sec 12.13] `bytes-sufficient → writer-side` — save_export_bug: "export (ap203 input emitted as ap242 with synthesised stubs) | the input was ap2"
- **Wr038** [sec 12.13] `bytes-sufficient → writer-side` — save_export_bug: "export uses different numbers. this breaks regression tests that compare files f"
- **Wr039** [sec 12.13] `bytes-sufficient → writer-side` — re_export_generic: "re-export"
- **Wr041** [sec 12.13] `bytes-sufficient → writer-side` — writer_emits: "writer emits"
- **Wr044** [sec 12.13] `bytes-sufficient → writer-side` — writer_emits: "writer emits"
- **Wr045** [sec 12.13] `bytes-sufficient → writer-side` — step_writer_noun: "step exporter"
- **Wr046** [sec 12.13] `bytes-sufficient → writer-side` — exports_wrong: "export drops"
- **Wr047** [sec 12.13] `bytes-sufficient → writer-side` — writer_emits: "writer emits"
- **Wr048** [sec 12.13] `bytes-sufficient → writer-side` — step_writer_noun: "step writer"
- **Wr052** [sec 12.13] `bytes-sufficient → writer-side` — writer_emits: "writer emits"
- **Wr055** [sec 12.13] `bytes-sufficient → writer-side` — write_regresses: "writer regression"
- **Wr056** [sec 12.13] `bytes-sufficient → writer-side` — writer_corrupts: "writer aliases"
- **Wr057** [sec 12.13] `bytes-sufficient → writer-side` — writer_emits: "writer emits"
- **Wr058** [sec 12.13] `bytes-sufficient → writer-side` — step_writer_noun: "step writer"
- **Wr060** [sec 12.13] `bytes-sufficient → writer-side` — write_regresses: "writer regression"

#### MEDIUM — 64

- **A001** [sec 12.6] `bytes-sufficient → writer-side` — writer_strips_omits: "writer drops"
- **A002** [sec 12.6] `bytes-sufficient → writer-side` — writer_strips_omits: "writer omits"
- **A024** [sec 12.6] `bytes-sufficient → writer-side` — save_export_bug: "exported with a copy whose orientation is silently corrected, flipping handednes"
- **A037** [sec 12.6] `bytes-sufficient → writer-side` — save_export_bug: "exporters and many open-source / hobbyist tools. | **see also**: a003. **occ beh"
- **A065** [sec 12.6] `bytes-sufficient → writer-side` — step_writer_noun: "step writer"
- **A080** [sec 12.6] `bytes-sufficient → writer-side` — exports_wrong: "export drops"
- **A081** [sec 12.6] `bytes-sufficient → writer-side` — writer_emits: "writer emits"
- **A089** [sec 12.6] `bytes-sufficient → writer-side` — exports_wrong: "export drops"
- **A095** [sec 12.6] `bytes-sufficient → writer-side` — writer_emits: "writer emits"
- **A096** [sec 12.6] `bytes-sufficient → writer-side` — writer_strips_omits: "writer drops"
- **A099** [sec 12.6] `bytes-sufficient → writer-side` — writer_emits: "writer emits"
- **A102** [sec 12.6] `bytes-sufficient → writer-side` — exports_wrong: "exports as"
- **A108** [sec 12.6] `bytes-sufficient → writer-side` — step_writer_noun: "step writer"
- **A110** [sec 12.6] `bytes-sufficient → writer-side` — writer_emits: "writer emits"
- **Ad102** [sec 12.11] `bytes-sufficient → writer-side` — step_writer_noun: "step writer"
- **Ad126** [sec 12.11] `bytes-sufficient → writer-side` — writer_emits: "writer emits"
- **Gn010** [sec 12.2b] `bytes-sufficient → writer-side` — save_export_bug: "exporters botching the rational arithmetic or by integer-overflow on weight norm"
- **Gn017** [sec 12.2b] `bytes-sufficient → writer-side` — save_export_bug: "export | some legacy receivers accept bezier (no internal knots) but not arbitra"
- **Gn020** [sec 12.2b] `bytes-sufficient → writer-side` — save_export_bug: "exported as a `b_spline_surface_with_knots` because the source kernel/exporter d"
- **Gn031** [sec 12.2b] `bytes-sufficient → writer-side` — save_export_bug: "export (swapped start/end vertices on tiny-radius rational b-spline arc) | for s"
- **Gn035** [sec 12.2b] `bytes-sufficient → writer-side` — writer_emits: "writer emits"
- **Gn176** [sec 12.2b] `bytes-sufficient → writer-side` — save_export_bug: "export bug"
- **Gp030** [sec 12.2a] `bytes-sufficient → writer-side` — save_export_bug: "exports (identifiable by `originating_system` 'pro/engineer …' in `file_name`) c"
- **Gp033** [sec 12.2a] `bytes-sufficient → writer-side` — save_export_bug: "exporters that assume at least c1 mis-handle the discontinuity and emit kinks wh"
- **Gp040** [sec 12.2a] `bytes-sufficient → writer-side` — step_writer_noun: "step writer"
- **Gs039** [sec 12.2c] `bytes-sufficient → writer-side` — writer_strips_omits: "writer drops"
- **Gs192** [sec 12.2c] `bytes-sufficient → writer-side` — step_writer_noun: "step writer"
- **Hea016** [sec 12.3c] `bytes-sufficient → writer-side` — writer_strips_omits: "writer drops"
- **Hea017** [sec 12.3c] `bytes-sufficient → writer-side` — exports_wrong: "export as"
- **Lh046** [sec 12.1b] `bytes-sufficient → writer-side` — writer_emits: "writer emits"
- **Ls004** [sec 12.1c] `bytes-sufficient → writer-side` — writer_emits: "writer emits"
- **M045** [sec 12.8] `bytes-sufficient → writer-side` — exports_wrong: "export drops"
- **M056** [sec 12.8] `bytes-sufficient → writer-side` — exports_wrong: "export missing"
- **M061** [sec 12.8] `bytes-sufficient → writer-side` — writer_strips_omits: "writer drops"
- **M068** [sec 12.8] `bytes-sufficient → writer-side` — writer_strips_omits: "writer drops"
- **M145** [sec 12.8] `bytes-sufficient → writer-side` — save_export_bug: "exported with the `top_signal` ply annotated as `fixed_side = 'bottom'`. compone"
- **M166** [sec 12.8] `bytes-sufficient → writer-side` — step_writer_noun: "step writer"
- **M190** [sec 12.8] `bytes-sufficient → writer-side` — step_writer_noun: "step exporter"
- **N017** [sec 12.4] `bytes-sufficient → writer-side` — writer_emits: "writer emits"
- **P001** [sec 12.6] `bytes-sufficient → writer-side` — re_export_generic: "re-exported"
- **P024** [sec 12.6] `bytes-sufficient → writer-side` — re_export_generic: "re-exported"
- **P027** [sec 12.6] `bytes-sufficient → writer-side` — step_writer_noun: "step writer"
- **P028** [sec 12.6] `bytes-sufficient → writer-side` — step_writer_noun: "step writer"
- **Pmi018** [sec 12.7] `bytes-sufficient → writer-side` — save_export_bug: "saved views | two `draughting_model`s for different saved views contain exactly "
- **Pmi060** [sec 12.7] `bytes-sufficient → writer-side` — re_export_generic: "re-export"
- **Pmi088** [sec 12.7] `bytes-sufficient → writer-side` — save_export_bug: "exporter computes area before a final face-merge / sliver-removal pass. a receiv"
- **Pmi089** [sec 12.7] `bytes-sufficient → writer-side` — save_export_bug: "exporter computes the centroid in the body's local frame and the file emits the "
- **Pmi099** [sec 12.7] `bytes-sufficient → writer-side` — save_export_bug: "export and emits three independent slot features — same orientation, same dimens"
- **Pmi123** [sec 12.7] `bytes-sufficient → writer-side` — save_export_bug: "export (writer coverage gap). receivers either degrade to a zero-thickness profi"
- **Pmi138** [sec 12.7] `bytes-sufficient → writer-side` — writer_emits: "writer produces"
- **Tfa023** [sec 12.3c] `bytes-sufficient → writer-side` — exports_wrong: "exports as"
- **Tfa069** [sec 12.3c] `bytes-sufficient → writer-side` — exports_wrong: "exports as"
- **Tfa248** [sec 12.3c] `bytes-sufficient → writer-side` — writer_strips_omits: "writer drops"
- **Tsh003** [sec 12.3a] `bytes-sufficient → writer-side` — re_export_generic: "re-export"
- **Tsh006** [sec 12.3a] `bytes-sufficient → writer-side` — re_export_generic: "re-export"
- **Tsh022** [sec 12.3a] `bytes-sufficient → writer-side` — writer_strips_omits: "writer drops"
- **Twi029** [sec 12.3b] `bytes-sufficient → writer-side` — writer_strips_omits: "writer drops"
- **Twi090** [sec 12.3b] `bytes-sufficient → writer-side` — step_writer_noun: "step exporter"
- **Twi092** [sec 12.3b] `bytes-sufficient → writer-side` — writer_strips_omits: "writer drops"
- **Xp029** [sec 12.12] `bytes-sufficient → writer-side` — exports_wrong: "export drops"
- **Xp030** [sec 12.12] `bytes-sufficient → writer-side` — step_writer_noun: "step writer"
- **Xp034** [sec 12.12] `bytes-sufficient → writer-side` — save_export_bug: "export | iso 10303-46 nominally treats colour_rgb values as linear-space [0.1] f"
- **Xp035** [sec 12.12] `bytes-sufficient → writer-side` — writer_emits: "writer emits"
- **Xp038** [sec 12.12] `bytes-sufficient → writer-side` — exports_wrong: "exports as"

#### LOW — 24

- **Wr003** [sec 12.13] `bytes-sufficient → writer-side` — section_12.13: "Wr writer-defect section"
- **Wr005** [sec 12.13] `bytes-sufficient → writer-side` — section_12.13: "Wr writer-defect section"
- **Wr008** [sec 12.13] `bytes-sufficient → writer-side` — section_12.13: "Wr writer-defect section"
- **Wr010** [sec 12.13] `bytes-sufficient → writer-side` — section_12.13: "Wr writer-defect section"
- **Wr011** [sec 12.13] `bytes-sufficient → writer-side` — section_12.13: "Wr writer-defect section"
- **Wr012** [sec 12.13] `bytes-sufficient → writer-side` — section_12.13: "Wr writer-defect section"
- **Wr013** [sec 12.13] `bytes-sufficient → writer-side` — section_12.13: "Wr writer-defect section"
- **Wr014** [sec 12.13] `bytes-sufficient → writer-side` — section_12.13: "Wr writer-defect section"
- **Wr015** [sec 12.13] `bytes-sufficient → writer-side` — section_12.13: "Wr writer-defect section"
- **Wr016** [sec 12.13] `bytes-sufficient → writer-side` — section_12.13: "Wr writer-defect section"
- **Wr018** [sec 12.13] `bytes-sufficient → writer-side` — section_12.13: "Wr writer-defect section"
- **Wr027** [sec 12.13] `bytes-sufficient → writer-side` — section_12.13: "Wr writer-defect section"
- **Wr028** [sec 12.13] `bytes-sufficient → writer-side` — section_12.13: "Wr writer-defect section"
- **Wr029** [sec 12.13] `bytes-sufficient → writer-side` — section_12.13: "Wr writer-defect section"
- **Wr030** [sec 12.13] `bytes-sufficient → writer-side` — section_12.13: "Wr writer-defect section"
- **Wr033** [sec 12.13] `bytes-sufficient → writer-side` — section_12.13: "Wr writer-defect section"
- **Wr034** [sec 12.13] `bytes-sufficient → writer-side` — section_12.13: "Wr writer-defect section"
- **Wr035** [sec 12.13] `bytes-sufficient → writer-side` — section_12.13: "Wr writer-defect section"
- **Wr042** [sec 12.13] `bytes-sufficient → writer-side` — section_12.13: "Wr writer-defect section"
- **Wr049** [sec 12.13] `bytes-sufficient → writer-side` — section_12.13: "Wr writer-defect section"
- **Wr050** [sec 12.13] `bytes-sufficient → writer-side` — section_12.13: "Wr writer-defect section"
- **Wr051** [sec 12.13] `bytes-sufficient → writer-side` — section_12.13: "Wr writer-defect section"
- **Wr053** [sec 12.13] `bytes-sufficient → writer-side` — section_12.13: "Wr writer-defect section"
- **Wr061** [sec 12.13] `bytes-sufficient → writer-side` — section_12.13: "Wr writer-defect section"

## Confidence-band methodology

- **HIGH** — one of:
  - Self-declared: notes or description explicitly states `provenance_tier: <T>` matching the proposed tier (there are 9 such — 6 Wr → sibling-pair, 3 Gb → runtime-only).
  - Strong-note phrase (`bytes alone insufficient`, `needs sibling input fixture`) plus at least one text signal.
  - Strong-field signal (`pair_with` populated, `fixture_kind` = `producer-receiver-pair` or `kernel-test-pair`) plus at least one text signal.
  - Section-level signal (§12.10 for `runtime-only`, §12.13 for `writer-side`) plus at least one specific text signal.
  - Three or more distinct text signals.
- **MEDIUM** — one strong text signal with no counter-signal in another tier, OR a strong-field signal alone, OR two text signals.
- **LOW** — section-alone (dedicated §12.10 / §12.13 with no reinforcing text), or a single text signal in the presence of a competing counter-signal from another tier. Hand-review required.

## Rule notes

### Signal-family productivity ranking (top 10)

| Rank | Tier / signal | Matches |
|---:|---|---:|
| 1 | `writer-side` / `section_12.13` (dedicated Wr writer-defect section) | 45 |
| 2 | `requires-sibling-pair` / `round_trip_loss` ("round-trip loss" phrasing) | 33 |
| 3 | `runtime-only` / `section_12.10` (dedicated Pf performance section) | 33 |
| 4 | `writer-side` / `save_export_bug` ("export bug" phrasing) | 27 |
| 5 | `writer-side` / `step_writer_noun` ("STEP writer/exporter") | 25 |
| 6 | `runtime-only` / `infinite_loop` | 23 |
| 7 | `writer-side` / `writer_emits` verbs | 16 |
| 8 | `writer-side` / `exports_wrong` | 14 |
| 9 | `runtime-only` / `bomb_expansion` (billion-laughs, schema bomb) | 13 |
| 10 | `runtime-only` / `stack_overflow` | 12 |

### Observations and rule refinements to consider

1. **The section field is the single most productive signal.** §12.10 (Pf) is dedicated to performance/runtime concerns; §12.13 (Wr) is dedicated to writer defects. Together they contribute 78 matches — arguably the correct default provenance_tier for these sections should have been non-`bytes-sufficient` from the start. Consider a schema-level default per section during `_build_catalog_json.py`.

2. **Self-declared tier claims in `notes`.** Nine entries have explicit `provenance_tier: <name>` text in notes that does *not* match the actual field. This is the cleanest signal (0 false positives inspected). Consider making `_build_catalog_json.py` honour explicit note-declared tiers automatically.

3. **Round-trip-loss language is ambiguous between `writer-side` and `requires-sibling-pair`.** Both tiers arguably apply when the file *is* the writer's output but demonstrating the loss needs the pre-writer input. Priority order set to prefer `requires-sibling-pair` for these (16 such conflicts, all Wr-section) — hand-review may want to swap back to `writer-side` if the receiver-side oracle can inspect *just* the output for the missing entities.

4. **"Crash" / "hang" words in Ad/Xp sections are not runtime-only signals.** 83 entries in §12.11-12.12 use the word `crash` but describe a *symptom* triggered by a byte-visible defect (empty aggregate, malformed value, invalid ref) — the bytes carry the defect. These are correctly `bytes-sufficient` and are on the rejection list.

5. **Section 12.13 Wr entries are near-uniformly writer-side.** 55/61 Wr* entries in `bytes-sufficient` got proposed; the 6 remaining (Wr019/021/022/023/026/031) proposed as `requires-sibling-pair` because their notes explicitly claim that. Wr048 ("crashes STEP writer") is edge: the crash aborts writing so no bytes exist — arguably runtime-only. Flagged in the writer-side LOW band.

6. **No new tier needed.** All text-signal families map cleanly onto the six existing tiers.

## Rejection list

Entries where a signal keyword matched but we deliberately did *not* propose re-tag (kept as `bytes-sufficient`):

### "crash" / "hang" / "segfault" wording in non-§12.10 entries — 83 entries

Reason: word describes a *kernel-crash symptom* triggered by a defect that is fully visible in the file bytes. An oracle checking topology or structure can detect the byte-visible defect (empty aggregate, dangling ref, malformed value, etc.); the crash is downstream.

Examples:
- **Ad015** [sec 12.11]: Empty aggregate where schema requires at least one element
- **Ad050** [sec 12.11]: Empty `EDGE_LOOP` / empty wire / empty entity iterator crashes reader
- **Ad051** [sec 12.11]: Reference to non-existent entity number (negative or out-of-range)
- **Ad056** [sec 12.11]: General-transform constructor throws on extreme non-uniform face stretch
- **Ad084** [sec 12.11]: `XCAFDoc_ShapeTool::FindSubShape` crash building XCAF tree
- **Ad087** [sec 12.11]: STEP reader crashes on file with unresolved entity reference
- **Ad088** [sec 12.11]: Crash on reading STEP with malformed parameter values
- **Ad091** [sec 12.11]: Crash on STEP file from non-C locale (decimal separator)
- **Ad092** [sec 12.11]: Crash reading large STEP file: exception during transfer
- **Ad095** [sec 12.11]: STEP file from Pro/Engineer crashes (vendor-attribution)
- **Ad096** [sec 12.11]: Crash on AP242 file: access violation reading entity
- **Ad119** [sec 12.11]: "Unknown ENTITY type" warning is not a hard failure (presentation subgraph silently dropped, BRL-CAD
- ... and 71 more.

### "writer" wording in non-§12.13 entries — 49 entries

Reason: `writer` appears in Notes/Sources as vendor attribution or historical context (e.g. "writer-emitted BSpline", "Onshape STEP export") but the defect is a byte-visible construct in the file (mis-count, malformed name, invalid schema string). The oracle can inspect the bytes; the writer origin is anecdotal.

Examples:
- **Ad059** [sec 12.11]: Mismatched weight / pole counts in BSpline (writer-emitted)
- **Ad122** [sec 12.11]: Damaged STEP export: writer reuses entity-ID slots
- **Ad123** [sec 12.11]: Step Export: crash on PCURVE processing (dangling surface ref)
- **Ad131** [sec 12.11]: OCCT PR #448: malformed `FILE_SCHEMA` with literal `.` between schema name and version triple (every
- **Xp025** [sec 12.12]: Onshape→SolidWorks: assembly children snap to origin (placements lost)
- **Xp026** [sec 12.12]: Fusion 360 AP242 export rejected by NX 12 (no AP242 import)
- **Xp027** [sec 12.12]: Inventor STEP import "stuck at 95%" — long path in FILE_NAME author field
- **Xp032** [sec 12.12]: CATIA V5 degenerate B-spline surface → Inventor "empty PartBody"
- **Xp041** [sec 12.12]: IfcOpenShell rejects valid IFC4X1 file due to lowercase 'x' in schema name
- **Xp042** [sec 12.12]: NX → Onshape "translation error" via super-multiplicity B-spline knot
- ... and 39 more.

## Cross-check with mutation-test job (PID 94338)

Once the mutation-test job at `/tmp/qmut_full.json` completes, expect the two workstreams to converge as follows:

- HIGH-band `runtime-only` proposals here should correspond to entries where mutation-testing shows the *bytes* mutate cleanly but no oracle catches the difference (defect is not in bytes).
- HIGH-band `writer-side` / `requires-sibling-pair` proposals should correspond to entries where an oracle *can* see the bytes but the defect story only makes sense with a paired input.
- LOW-band entries in both workstreams are the ones most likely to disagree — good candidates for human review.

---

_Generated by rule-based scan, no manual defect-domain judgement applied. Rule source lives in /tmp/reclass_proposals_v2.json (raw dump); regenerate with the scanner in the audit conversation transcript._