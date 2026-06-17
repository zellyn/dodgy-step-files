# fixture_sources/

Python source files that build STEP fixtures via the minimal builder at
`validation/src/step_corpus/step_builder.py`.

## Why a builder

LLM-driven fixture synthesis kept producing syntactically-broken Part-21
files: misplaced parens, FILE_DESCRIPTION arity bugs, Unicode minus
signs, LINE self-references, etc. The Part-21 validator now catches
those at validation time, but each new wave still requires regen +
fix-pass.

A builder addresses the root cause: **the LLM writes intent
(`f.manifold_solid_brep(outer=open_shell)`), the builder writes syntax**.

## Convention

- One Python file per fixture: `fixture_sources/<section>/<ID>.py`.
- Each file constructs a `StepFile` and assigns it to a top-level
  variable named `f`.
- Running the builder regenerates `step-examples/<section>/<ID>.stp`.

```python
# fixture_sources/12-3a-shells/Tsh020.py
from step_corpus.step_builder import StepFile

f = StepFile(catalog_id="Tsh020",
             defect="Edge appearing 3 times across faces (T-junction non-manifold)")

# ... build geometry using f.cartesian_point, f.line, f.advanced_face,
#     f.manifold_solid_brep, f.add_product_chain, etc.
```

## Regenerate

```bash
cd validation
uv run python -m step_corpus.step_builder ../fixture_sources/12-3a-shells/Tsh020.py
```

## What the builder provides

- Entity-ID allocation (no manual `#1`, `#2`, …).
- Part-21 serialization (correct paren balance, REAL decimal
  formatting, apostrophe doubling).
- Canonical HEADER block (FILE_DESCRIPTION 2-arg, FILE_NAME, FILE_SCHEMA).
- Standard PRODUCT chain via `f.add_product_chain(model_entity)`.
- Geometry primitives: `cartesian_point`, `direction`, `vector`, `line`,
  `circle`, `axis2_placement_3d`.
- Topology: `vertex_point`, `edge_curve`, `oriented_edge`, `edge_loop`,
  `face_outer_bound`, `face_bound`, `advanced_face`, surfaces (`plane`,
  `cylindrical_surface`, etc.), shells (`open_shell`, `closed_shell`),
  `manifold_solid_brep`.
- Convenience: `closed_polyline_loop([points])` builds a closed wire
  from a list of CARTESIAN_POINTs.

## Intentional malformation hooks

Some fixtures need defects that the validator would otherwise flag.
The builder accommodates:

- `DanglingRef(eid)` — produces an unresolved `#N` reference. Used by
  Tfa098 to demonstrate "edge geometry references undefined entity".
- `manifold_solid_brep(outer=open_shell, ...)` — accepted (the builder
  attaches an `_note` for trace) so fixtures can demonstrate
  "outer-shell-is-OPEN" defects like Tsh020-class fixtures.

## What this POC covers

5 fixtures (Tsh020, Tsh021, Tsh027, Tfa098, Tfa145) — chosen from the
`_quarantine/phase_F_boilerplate/` set to prove the builder produces
defect-specific geometry that explicitly demonstrates the catalog
claim, replacing the generic boilerplate that haiku regens produced.

## What this POC does **not** do

- The other ~2,200 active fixtures don't have `.py` sources. They
  remain canonical-as-`.stp` and can be migrated lazily (e.g. when
  a fixture is touched / regenerated for any reason).
- No CI invariant requiring `.py` and `.stp` to round-trip yet.
  Recommended: add a check that re-running the builder on each
  `.py` produces a byte-identical `.stp`, then promote to CI.
- Only ~25 entity types are supported. Fixtures that need rarer
  entities can either extend the builder or use the existing `.stp`
  authoring flow.

## Consumer note

Consumers of the corpus still read `.stp` files directly (Rust crate,
browse pages, test harnesses). The `.py` files are build-time tools,
not part of the consumer API. Adding the builder doesn't change how
the fixtures are used downstream.
