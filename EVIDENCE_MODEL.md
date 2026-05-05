# Evidence model

What evidence backs each catalog entry? Different fixtures need different
proofs, and the corpus is honest about which proof applies where.

## TL;DR

| Class of defect | Test that proves it | Coverage |
|---|---|---|
| Encoding / framing / syntax (§12.1, §12.11) | byte-level review + parser oracle | 144 fixtures |
| Header / schema / structural (§12.1b, §12.8) | byte-level review + Part-21 parser | 76 fixtures |
| Geometry / topology with PRODUCT chain (§12.3) | tier-3 metrics + adversarial review | ~95 fixtures |
| Geometry / topology, minimal scaffold (§12.2, §12.4) | byte-level review (oracle silent) | ~250 fixtures |
| Assembly / PMI / mixed (§12.6, §12.7, §12.8) | byte-level review (mostly silent oracle) | ~260 fixtures |
| Performance (§12.10) | scaled-down structural patterns + catalog notes | 32 fixtures |
| Cross-product (§12.12) | composes evidence of cited single defects | 22 fixtures |

The headline `1281 CONFIRMED + 9 CONFIRMED-WEAK + 0 DRIFT + 0 FAIL` describes
*catalog-spec consistency* (Expected validation matches live oracle output),
not *oracle-independent verification*. Read on for what each entry actually
proves.

## What "CONFIRMED" means

For each catalog entry, validate2 produces an **oracle spec string** like
`occt=empty/empty gmsh=empty ifc=schema_n/a` or
`occt=signal(11)/signal(11) gmsh=signal(11) ifc=schema_n/a`. The catalog
codifies the *expected* spec. CONFIRMED means observed = expected.

For most fixtures, observed = expected = `occt=empty/empty
gmsh=empty ifc=schema_n/a`. That's **silent-empty**: the oracle didn't
attempt geometric construction (the fixture has no PRODUCT chain rooting
a SHAPE_REPRESENTATION). For those entries, CONFIRMED is meaningful only
in the sense that the fixture loads as valid Part-21 *and* the catalog
agrees the oracle should be silent. The defect's *proof* is not in the
oracle's silence; it's in the fixture's bytes.

For the oracle-active subset (~266 fixtures with reject / segfault /
shape-loading baselines), CONFIRMED carries strong oracle signal: the
kernel actually *did* something distinct, and the catalog correctly
predicts what.

## Independent confidence signals per fixture

Three signals, applied per-fixture and aggregated:

### 1. Forward adversarial review (bytes support the claim)

An agent reads the catalog claim and the fixture, then tries to *disprove*
that the fixture's bytes / entity graph exhibit the claimed defect.
Result across the corpus: **918 / 960 fixtures demonstrate their claim**
in entity-graph evidence; 42 are runtime-only (perf / process-state)
entries whose defect lives outside the bytes.

### 2. Reverse self-evidence (cold reader finds the canonical entry)

An agent reads the .stp file *cold*, without consulting the catalog,
and writes a bug-reporter description of the defect. We then BM25-search
the catalog using the agent's description and check whether the canonical
entry surfaces in the top-3 hits. Result across the reviewed fixtures:
**87.4 % top-3 self-evidence**; 16 weak entries (1.7 %) where the bytes
support some defect but BM25 doesn't surface the catalog's particular
phrasing.

### 3. Mutation sensitivity (bytes drive oracle output)

For each oracle-active fixture, we mutate a byte in the DATA section
three times (different positions) and re-run validate2 + tier-3. We
compare both summaries plus the OCCT diagnostic-message signature.
**91.8 % detection rate** on a 100-fixture stratified sample. The
undetected 8 are binary-output baselines (segfault / parser-reject /
process-signal) where flips can't change the binary state.

### 4. Structural mutation (silent-empty subset)

For the silent-empty fixtures, random byte mutation can't help; the
oracle is uniformly silent regardless. Instead we run a *structural*
mutation: swap one `#N` reference to a different defined instance of a
different entity type, then compare oracle output.

**Result: 9.9 % detection rate.** That's honest about the silent-empty
subset's confidence floor. For the ~88 % that don't react to structural
mutation, OCC is not walking the entity graph deeply enough on minimal
scaffolds for the catalog-documented wiring to be load-bearing. **The
defect is in the bytes (forward + reverse review confirms) but OCC's
silent-empty response is inert under that wiring**. Their evidence
pipeline is byte-level review only.

The mitigation is PRODUCT-chain wrapping: making OCC actually attempt
shape transfer turns silent-empty fixtures into oracle-active ones,
where mutation testing then has high detection.

## How to use a corpus entry

If you're a kernel author wiring this corpus into your test suite:

- **CONFIRMED + non-silent oracle baseline** (~266 fixtures): your
  kernel should produce the same spec string. Strong oracle agreement.

- **CONFIRMED + silent-empty baseline** (the rest): your kernel may
  legitimately do something different (load and produce shapes, or
  reject). Use the catalog claim's `**Expected kernel behavior**:` line
  as the assertion target, not the oracle spec. The fixture's value is
  as a *test input* whose defect is documented in the catalog.

- **CONFIRMED-WEAK** (9 fixtures): the catalog's full claim isn't
  reproducible at fixture scale (perf entries, process-state entries).
  Read the entry's `**Notes**:` for what's testable.

- **Tier-3 assertion** present: a machine-checkable invariant the
  fixture demonstrates. Run `step_corpus._tier3_assertions` to verify.

## Stronger oracle signal

The biggest open question for corpus quality is: how do we get oracle
differential signal on the silent-empty subset? Three avenues:

1. **PRODUCT-chain wrap** so OCCT's `TransferRoots` runs and tier-3
   measures shape geometry, expanding the oracle-active subset.

2. **Stronger oracle.** Capture OCCT's diagnostic message stream so
   silent-empty fixtures can be distinguished by *why* they came out
   empty.

3. **External-kernel cross-validation.** Running a non-OCCT kernel on
   each fixture (the pure-Python ISO 10303-21 strict parser is currently
   integrated; CGAL / other kernels are future work) gives oracle
   independence: agreement across kernels means "uninteresting / clean",
   divergence means "real defect".

For the silent-empty subset today, the corpus's primary evidence remains
entity-graph adversarial review.
