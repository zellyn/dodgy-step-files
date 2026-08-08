# probes/

One-off measurement scripts kept because a BACKLOG entry cites their numbers.
Not imported by the package, not run by CI, not covered by tests — they exist
so a reported measurement can be re-run and checked rather than taken on faith.

- `shapefix_probe.py` — does a real `ShapeFix_Shape` pass produce a signal the
  current two-mode OCCT oracle cannot see? Cited by BACKLOG §(G). Usage:

      cd validation && uv run python probes/shapefix_probe.py <file.stp>

  Emits JSON: read token, topology counts before/after healing, and which
  `ShapeExtend_Status` flags the healer raised.

- `heal_coverage_probe.py` — per-repair `ShapeFix_Wire` status per wire.
  **Kept as a negative result, not as a working metric:** validated against 7
  fixtures with specific claimed wire defects and 0 of 7 fired the matching
  repair, because it measures OCCT's already-normalised transfer output rather
  than the file's actual defect. Read the module docstring and BACKLOG §(G)
  before reusing. Usage:

      cd validation && uv run python probes/heal_coverage_probe.py <file.stp>
