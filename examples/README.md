# Using the STEP defect corpus in a downstream test suite

This directory shows how a CAD-kernel author would integrate the corpus into
their own test runner.

## Recommended workflow

1. **Pin a corpus version.** Vendor the repo as a git submodule, or pin to a
   specific commit. The catalog JSON
   (`STEP_PROBLEM_CATALOG.json`) is byte-stable across regenerations of the
   same markdown source, so you can hash it as a version stamp.
2. **Iterate fixtures via the catalog API.** Each canonical entry includes
   the fixture's relative path, expected kernel behavior, and the codified
   `expected_validation` spec.
3. **Assert your kernel against the catalog claim**, not against any single
   reference kernel. The catalog tells you *what the file is supposed to
   provoke*; your kernel can take any defensible position (heal / reject /
   warn) as long as it's documented.

## Sample integration: pytest

See [`pytest_integration.py`](pytest_integration.py) for a worked example of
parameterizing pytest test cases over the catalog.

## Cataloging your kernel's coverage

For each catalog entry you handle, record one of these decisions in your
own kernel's test results:

- `pass` — your kernel handled the file the way the catalog said it
  should
- `xfail (known)` — your kernel currently doesn't handle it; document why
- `disagree (intentional)` — your kernel takes a different position than
  the catalog (e.g. you reject something the catalog says to heal); make
  sure your reasoning is in the test annotation
- `unexpected` — the file did something neither you nor the catalog
  predicted; investigate

Compute coverage as `(pass + xfail + disagree) / total_catalog_entries`. A
kernel approaches OCCT-parity when this ratio approaches 1 with very few
`disagree` cases.

## Catalog version stability

`STEP_PROBLEM_CATALOG.json` is regenerated deterministically from
`STEP_PROBLEM_CATALOG.md`; the same markdown produces byte-identical JSON.
This means:

- Hash the JSON file's bytes as your "corpus version stamp".
- A change in the hash means at least one entry's prose, ID, or section
  was modified — your kernel test results may need re-baselining.
- New entries (catalog grows) won't break old kernel tests; they just
  add new tests to run.

## When the catalog adds new defect classes

Catalog releases follow semver-like discipline:

- **Patch** (e.g. v0.3.1): clarification edits, prose audit, no new entries.
- **Minor** (e.g. v0.4.0): new entries; fixture IDs preserved.
- **Major** (e.g. v1.0.0): re-numbering or section restructuring.

Pin to the minor version that matches your kernel's documented coverage
matrix; bump deliberately when you're ready to extend coverage.
