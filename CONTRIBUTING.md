# Contributing

Thanks for adding to the STEP corpus. This guide covers how to add a defect entry, how to construct its fixture, the conventions the project uses end-to-end, and what reviewers will check.

## What this project is

`STEP_PROBLEM_CATALOG.md` is the canonical reference. Every `.stp` file under `step-examples/` exists to demonstrate exactly one canonical catalog entry. The validator under `validation/` adversarially confirms that each fixture exhibits the claimed defect.

A pull request typically does one of three things:

1. **Adds a new canonical defect entry** (catalog + fixture + validator confirmation).
2. **Replaces a fixture with a corrected one** when the validator surfaces a mismatch between fixture and catalog.
3. **Tightens or generalizes a validator check**: adds a per-defect-id YAML spec under `validation/checks/`, fixes a heuristic that produces CONCERN where it should produce CONFIRMED, etc.

We do not accept third-party STEP exchange data. Even single-entity excerpts copied from another tool's output are out of scope. Every byte of every fixture must be original work derived from the catalog text.

## §12.x category taxonomy

Defects are filed by category. The category determines the entry-ID prefix, the directory the fixture lives in, and the report it appears in.

| Section | Prefix | Subject |
|---|---|---|
| §12.1a | `Le` | encoding & string-literal defects (BOMs, `\X\` / `\X2\` / `\X4\` / `\S\` / `\P\` directives, raw multibyte, locale issues) |
| §12.1b | `Lh` | header structure, instance numbering, FILE_SCHEMA / FILE_DESCRIPTION conformance |
| §12.1c | `Ls` | Part-21 grammar (literals, list syntax, comments, anchors) |
| §12.2a | `Gp` | pcurve defects (orphans, near-period shifts, missing seams) |
| §12.2b | `Gn` | NURBS / B-spline (knot multiplicities, weights, degree, control points) |
| §12.2c | `Gs` | surface & curve degeneracies (zero-area, self-intersection, near-tangent) |
| §12.3a | `Tsh` | shell & orientation (open shells, flipped normals, non-manifold seams) |
| §12.3b | `Twi` | wire / loop / edge (gaps, self-intersection, period shifts) |
| §12.3c | `Tfa` | face / sewing / free bounds (slivers, zero-thickness, free edges) |
| §12.4 | `N` | tolerance & numerical precision (epsilon scales, near-zero comparisons) |
| §12.5 | `U` | units & coordinate systems (mm/inch confusion, conversion-based units) |
| §12.6 | `A`, `P` | assembly hierarchy (`P001`–`P028` reserved for FreeCAD-origin findings; new entries use `A`) |
| §12.7 | `Pmi` | PMI / GD&T (datum references, tolerance frames, leader presentation) |
| §12.8 | `M` | mixed / auxiliary (tessellation, validation properties, supplemental geometry, FEA, appearance) |
| §12.10 | `Pf` | scale & performance (deep graphs, very large strings, entity count amplification) |
| §12.11 | `Ad` | adversarial / parser-robustness |

If a defect plausibly fits two sections, file it under the section that owns the *primary* invariant being violated, and add a `**See also**:` cross-reference to the other section in the entry's Notes line.


## Adding a new canonical entry

1. **Find the next free ID** in the relevant prefix. Run a grep across `STEP_PROBLEM_CATALOG.md` to confirm the ID is not already used (canonical or merged).
2. **Write the catalog entry** in `STEP_PROBLEM_CATALOG.md`, in the appropriate §12.x section, in numerical-ID order. Use the standard entry shape:

   ```
   ### {ID} — {short title}
   - **Category**: §12.x.y ({sub-class})
   - **Sources**: {issue-tracker citation / public-doc reference}
   - **Sender** (if known): {producing CAD tool}
   - **Receiver** (if relevant): {consuming CAD tool that fails}
   - **Description**: {detailed enough to recreate, in your own words}
   - **Reproducer recipe**: {minimal Part-21 form}
   - **Expected kernel behavior**: {accept / reject-with-error / heal-to-Y, with diagnostic codes where applicable}
   - **Notes**: {cross-references}
   - **Expected validation**: `occt={heal_on}/{heal_off} gmsh={autofix_on} ifc={oracle}`
   ```

3. **Write the fixture** under `step-examples/<section>/<ID>.stp` per the style guide below.
4. **Run the validator** locally (see "Running validation" below). The fixture must produce CONFIRMED, or, if the defect is a "silent acceptance" / "over-tolerance" class, the validator output must match what the catalog says about silent acceptance.
5. **Update validator checks** if your defect needs a new per-id YAML check under `validation/checks/`. The existing patterns in that directory show the schema.
6. **Re-generate the affected per-section report** at `validation/reports/<section>-validation.md`.

## Cross-referencing

When two entries describe overlapping or related defects, add `**See also**: <ID list>` to both entries' Notes lines. The `**See also**:` lint enforces that every referenced ID resolves to a canonical entry.

## Sender attribution

The catalog records the producing CAD tool ("Sender") because some defects are signature behaviors of specific kernels. Use these canonical names:

- `CATIA` (V5, V6 — annotate the version when known)
- `Pro/E` (use this for Pro/Engineer; switch to `Creo` for Creo Parametric)
- `Creo`
- `SolidWorks`
- `Inventor`
- `NX` (formerly Unigraphics; use `NX` even for older `UG NX` files)
- `SolidEdge`
- `FreeCAD`
- `OCCT` (when the file is round-tripped through Open CASCADE Technology)
- `STEP-Tools` / `JT2STEP` / `IFC` and other converters when known

If the producing tool is unknown but the file's `FILE_NAME` originating-system slot names a tool, quote that slot verbatim in Notes (`Originating-system tag: 'FOO 2019'`).

If multiple tools are known to emit the defect, list them comma-separated. Receivers (consuming tools that fail) follow the same convention.

## Fixture style guide

Every fixture under `step-examples/` follows this shape. Look at `12-1a-encoding/Le001.stp` and `12-2b-nurbs/Gn003.stp` for canonical examples.

### File naming

The filename is the entry ID plus `.stp`. No prefixes, no suffixes, no version numbers. `Le001.stp`, `Gn003.stp`, `Pmi049.stp`, `Ad027.stp`.

### Top-of-file comment

The first non-magic content is a Part-21 `/* */` comment naming the entry ID, the entry title, and the defect class in plain prose. Keep it under 8 lines. For fixtures whose defect *is* a malformed Part-21 framing (UTF-8 BOM, missing END marker, etc.), the comment may sit before the magic line — see `Le001.stp` for the BOM-before-comment pattern.

```
/* Le001 — UTF-8 BOM at start of ISO-10303-21;
   Defect: leading EF BB BF bytes appear before the magic line, violating
   the Part-21 framing grammar that requires ISO-10303-21; as the first token.
   Note: the BOM is the FIRST three bytes of this file; this comment sits
   AFTER the BOM. Strict parsers fail at the first non-ASCII byte. */
```

### HEADER section

```
ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('<entry-id> - <one-line title>'),'2;1');
FILE_NAME('<entry-id>.stp','2026-04-26T00:00:00',('auto-generated'),(''),
  'auto-generated','','');
FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }'));
ENDSEC;
```

`FILE_NAME` arg 1 must equal `<entry-id>.stp`. Use schema `AUTOMOTIVE_DESIGN { 1 0 10303 214 3 1 1 }` unless the defect is specifically about an alternate schema (`AP242`, `AP203`, schema-mixing, etc.), in which case declare what the catalog entry says.

### DATA section

Include only the entities required to express the defect. Do not pad. If the defect is geometric and the validator's tier-3 step needs to compute a measurement (face area, edge length, knot multiplicity sum), wrap the geometry in the minimal `PRODUCT` → `PRODUCT_DEFINITION_FORMATION` → `PRODUCT_DEFINITION` → `PRODUCT_DEFINITION_SHAPE` → `SHAPE_DEFINITION_REPRESENTATION` chain so OCCT's `TransferRoots` can reach the geometry.

For purely lexical, header, or syntax defects, no PRODUCT chain is needed; a handful of `CARTESIAN_POINT` / `DIRECTION` / `AXIS2_PLACEMENT_3D` entities is enough.

Use inline `/* */` comments above the defect-bearing entities to call out exactly which line is the defect. The catalog entry's "Reproducer recipe" should appear, byte-for-byte where possible, in the fixture.

### Closing

```
ENDSEC;
END-ISO-10303-21;
```

Files always end with a trailing newline.

### License-cleanliness

- No copy-paste from third-party STEP exchange data, even single-entity excerpts.
- No copy-paste from CAD-tool test suites.
- It is OK to refer to public-domain spec text (ISO 10303-21 Ed.3 is paraphrasable; do not quote at length).
- It is OK to cite issue trackers by URL/ID in the catalog entry.

If a fixture would only "look right" by replicating a real file, file a bug instead — the fixture is too specific.

## Running validation locally

```bash
cd validation
uv sync
uv run python -m step_corpus.validate2 ../step-examples/12-1a-encoding/Le001.stp
```

Run on the full corpus to regenerate per-section reports:

```bash
cd validation
uv run python -m step_corpus.validate2 --corpus ../step-examples
```

The validator emits one JSON line per file (suitable for CI) plus a markdown report under `reports/`. CONFIRMED and CONCERN are both acceptable in CI; FAIL is a bug.

If your fixture lands as CONCERN, the validator's heuristic couldn't decide. Either improve the fixture so the defect is unambiguous, or add a per-id YAML check under `validation/checks/` that gives the validator the information it needs.

## Pull request review checklist

Reviewers will look for:

- [ ] Catalog entry uses the next free ID in its prefix and is filed in numerical order.
- [ ] Catalog entry has all required fields (Category, Sources, Description, Reproducer recipe, Expected kernel behavior, Expected validation).
- [ ] Fixture filename equals `<entry-id>.stp`.
- [ ] Fixture starts with a `/* */` comment naming the entry ID, title, and defect class.
- [ ] `FILE_NAME` first arg equals `<entry-id>.stp`; date is the build date; author / org / preprocessor are `('auto-generated')`.
- [ ] DATA section is minimal: only entities the defect requires (plus a wrapping PRODUCT chain if tier-3 measurement is needed).
- [ ] No copied third-party STEP content; reproducer recipe in the catalog entry matches what is actually in the fixture.
- [ ] Sender / Receiver attributions use the canonical names from the list above.
- [ ] Cross-references (`See also`) point at IDs that resolve.
- [ ] Validator run locally produces CONFIRMED (or behavior matching the catalog's silent-acceptance claim).
- [ ] If the defect needed a new check, a YAML entry exists under `validation/checks/`.
- [ ] Per-section report under `validation/reports/` is regenerated and the totals at the bottom match.
- [ ] CI passes; no fixture FAILs.

## Aspirational: what we would love to see

- New §12.x categories when a real-world defect class falls outside the existing taxonomy.
- Tier-3 geometric checks for sections that currently only produce heuristic verdicts (§12.3a/b/c).
- Better OCCT diagnostic capture (custom `Message_Printer` via `OCP.Message`) so the validator can read structured kernel diagnostics rather than parsing colored stderr.
- Cross-validation against additional kernels (Parasolid via OEM tooling, ACIS, CGM) when they're accessible.
- A NIST SFA tier (`tier4_sfa.py`) that wraps NIST's STEP File Analyzer and cross-references its diagnostics with the catalog's expected defect class.
