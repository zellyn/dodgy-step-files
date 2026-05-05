# §12.10 — Scale & performance defects (Pf-prefix)

Scale and performance defects: large-file growth, excessive entity counts, deep aggregation chains, fragmented STRING literals, and other inputs that stress parsers' time/memory budgets.

See [`../../STEP_PROBLEM_CATALOG.md`](../../STEP_PROBLEM_CATALOG.md) (§12.10) for canonical entries.

## Fixtures

| ID | Title |
|---|---|
| [Pf001](Pf001.stp) | Multi-GB Creo AP242 assemblies trigger unbounded receiver memory |
| [Pf002](Pf002.stp) | Quadratic-cost STEP write on dense forward-reference `VERTEX_POINT` / `EDGE_CURVE` / `ADVANCED_FACE` web (200k-entity scale) |
| [Pf003](Pf003.stp) | 50-second read on a 20 MB STEP: forward-reference DATA section forces multi-pass resolution (single-threaded) |
| [Pf005](Pf005.stp) | Slow STEP import on geometric-set-heavy file |
| [Pf006](Pf006.stp) | Quadratic self-intersection check dominates STEP read on perforated sheets |
| [Pf007](Pf007.stp) | `ADVANCED_FACE` with many circular inner `FACE_BOUND` holes triggers eager UV-bounds wire-walk on every type-only surface query |
| [Pf008](Pf008.stp) | Stack overflow on huge faces-per-shell counts |
| [Pf009](Pf009.stp) | Stack overflow when meshing with TBB pool from STEP import |
| [Pf010](Pf010.stp) | Cyclic / self-referential reference graph causes infinite recursion |
| [Pf011](Pf011.stp) | `EntityCluster` infinite recursion / leak on pathological deep chain |
| [Pf012](Pf012.stp) | Stack overflow via deeply nested aggregate parens |
| [Pf013](Pf013.stp) | Entity-count amplification: tiny file, many GB resident |
| [Pf014](Pf014.stp) | Long helix exported as huge B-spline (millions of poles) |
| [Pf015](Pf015.stp) | Pathological B-rep from mesh conversion: `OPEN_SHELL` from OpenSCAD/STL→STEP |
| [Pf016](Pf016.stp) | STEP assembly reader hangs in Transfer on cyclic `SHAPE_REPRESENTATION_RELATIONSHIP` web (Catia/NX-emitted file, OCCT 7.9) |
| [Pf017](Pf017.stp) | Healing pipeline hangs on huge single-shell input (multi-pass divergence) |
| [Pf018](Pf018.stp) | Memory not released after STEP assembly read (Linux / Docker) |
| [Pf019](Pf019.stp) | Memory leaks in STEP/IGES controller initialisation enum tables |
| [Pf020](Pf020.stp) | OCAF modification-delta leak on long-running healing test suites |
| [Pf021](Pf021.stp) | Floating / non-deterministic crash in shape healing on near-apex `CONICAL_SURFACE` edge |
| [Pf022](Pf022.stp) | Non-deterministic empty-export from in-memory state leakage |
| [Pf023](Pf023.stp) | Iterative ShapeFix exposes new defect every pass (unbounded) |
| [Pf024](Pf024.stp) | Self-intersection-healing tool enters infinite loop on `EDGE_LOOP` with crossed diagonals (out-of-range split index) |
| [Pf025](Pf025.stp) | `ADVANCED_FACE` with internal-vertex `VERTEX_LOOP` `FACE_BOUND` (`.U.`) causes outer-wire-detection infinite loop (IFC-derived) |
| [Pf027](Pf027.stp) | Mixed-scale features produce millions of tiny faces post-tessellation |
| [Pf028](Pf028.stp) | Rhino joins > 10k face polysurfaces in O(n²) |
| [Pf029](Pf029.stp) | `TDocStd_Document` creation aborts process under VSCode server runtime |
| [Pf030](Pf030.stp) | Schema-EXPRESS WHERE-rule evaluation bomb (billion-laughs analogue) |
| [Pf031](Pf031.stp) | STEP read parsing slow due to single-pass tokenisation |
| [Pf032](Pf032.stp) | Reader hangs during XCAF tree build on deep assembly |
| [Pf033](Pf033.stp) | Long-running mesh on STEP file load |
| [Pf034](Pf034.stp) | Shape-divide pass raises end-of-iteration on large shape |
