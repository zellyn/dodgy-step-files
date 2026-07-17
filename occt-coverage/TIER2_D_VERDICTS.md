# Tier-2 D — verification verdicts (staging)

Per-fixture verification evidence so the integrator can flip the scoreboard verdict in
`occt-coverage/exchange/problems.json` / `occt-coverage/tkshhealing/problems.json`.

All verification run in this worktree's `validation/.venv` (OCP / OCCT 7.8.1).

---

## Target 2 — `sew-cutting-hanging-vertex-split` (exchange) — GAP → **CLOSE (fixture shipped)**

- **Fixture**: `step-examples/12-3a-shells/Tsh260.stp`  (new id, next free after Tsh259)
- **problem_id covered**: `sew-cutting-hanging-vertex-split`  (domain `exchange/sewing`)
- **Subvariant covered**: snap/new-cut node insertion via `Cutting` / `CreateCuttingNodes` /
  `CreateSections` (the base T-junction hanging-vertex edge split). The two secondary
  subvariants (non-manifold-vertex preservation across the cut; seam dual-pcurve propagation)
  are NOT exercised by this fixture and remain open.
- **Verdict recommendation**: flip `coverage_verdict` GAP → PARTIAL (or COVERED for the base
  mechanism) and add `Tsh260` to `fixture_ids`. The base Cutting/hanging-vertex edge-split
  mechanism is now genuinely and reproducibly demonstrated; the two auxiliary subvariants are
  still uncovered, so PARTIAL is the precise call.

### Runtime-scaffold evidence (reproducible)

Read the fixture with `STEPControl_Reader`, then run `BRepBuilderAPI_Sewing`:

```
READ-BACK: shape_null=False  faces=2  unique_edges=6  unique_verts=6
reference long edge present intact: True      # [(1.0,0.0,0.0),(1.0,2.0,0.0)]

--- BRepBuilderAPI_Sewing(1e-2, sew=True, analysis=True, cutting=True, nonmanifold=False).Perform() ---
unique edges: before=6  after=7   NbContig=1
reference long edge still intact after sew: False        # <-- the long edge was consumed
collinear x=1 sub-edges after sew:
    [(1.0, 0.0, 0.0), (1.0, 0.5, 0.0)]
    [(1.0, 0.5, 0.0), (1.0, 1.5, 0.0)]     # merged section (NbContig=1)
    [(1.0, 1.5, 0.0), (1.0, 2.0, 0.0)]
VERDICT Cutting fired (long edge replaced by interior-node sub-edges): True
```

The single long reference edge `(1,0)-(1,2)` is replaced by three collinear sub-edges cut
exactly at the two hanging vertices `(1,0.5)` and `(1,1.5)` — vertices that exist ONLY on the
unrelated Face-SHORT candidate edge. There is no source for interior nodes at y=0.5 and y=1.5
on the x=1 line other than a genuine `Cutting` split. Unique-shape counting
(`TopTools_IndexedMapOfShape`), not naive `TopExp_Explorer` traversal, so this is not the
double-counting artifact that impeached M045.

### Why prior sessions missed it (reconciliation with BACKLOG §(e))

1. They keyed on `Sewing::IsModified(long_edge)` — which returns **False** across a Cutting
   split (OCCT registers the merge under `Modified`, not the Cutting sections). Confirmed:
   `IsModified` is False here too, yet the result topology unambiguously shows the 3-way split.
2. Their geometries used a single hanging vertex or a shared corner (e.g. M045's tab, and
   in-memory faces sharing an endpoint), where the split either did not net-increase the unique
   edge count or the "hanging" vertex was actually a shared/glued node. The trigger the class
   needs is a candidate edge whose **entire span** lies strictly interior to the longer edge
   (both endpoints strictly interior, no shared vertex) — forcing a genuine 2-node cut. That is
   the geometry Tsh260 encodes.

### Other checks (fixture hygiene)

- `_structural_oracle.lint_file` → `ok` (identical to template Tsh246).
- Byte assertions all pass: PLANE==2, ADVANCED_FACE==2, EDGE_CURVE==6, OPEN_SHELL==1.
- Tier-3 (live `tier3_geometric.geometric_report`): shape_null=False, n_faces_total=2,
  n_edges_total=6, face surface_types = ['plane','plane'].
- Expected validation (live `validate2`): `occt=shape(1)/shape(1) gmsh=shape(14) ifc=schema_n/a`.
  (The `occt_diag` "Incorrect Syntax : Fails Count : 2" line is a benign corpus-wide artifact —
  template Tsh246 and Tsh259 emit the identical diagnostic while still accepting n_roots=1.)

---

## Target 1 — `tkshh-indirect-elementary-surface-axes` (tkshhealing) — GAP → **NO fixture (unreachable, re-confirmed)**

- **problem_id**: `tkshh-indirect-elementary-surface-axes` (domain `TKShHealing`,
  `ShapeCustom_DirectModification` / `ShapeCustom::DirectFaces`).
- **Verdict recommendation**: leave `coverage_verdict: GAP` with the existing
  `VERIFICATION: STRUCTURALLY-UNREACHABLE` note. No fixture shipped. Do NOT invent a fixture —
  it would be a Tfa-style "named repair never fires" trap.

### Evidence (independently reproduced this session; matches the prior verifier's conclusion)

The repair `ShapeCustom::DirectFaces` DOES fire on an in-memory indirect surface, but no STEP
file can ever hand it one, because `STEPControl_Reader` sanitizes both defect encodings on read:

1. **Indirect (left-handed) placement.** In-memory: a `Geom_Plane` on a `gp_Ax3` after
   `YReverse()` has `Position().Direct()==False`, and `DirectFaces` modifies it (Direct→True) —
   the operator genuinely fires. But writing that face with `STEPControl_Writer` serializes it by
   NEGATING the ref_direction (`AXIS2_PLACEMENT_3D` ref_direction `(-1,0,0)`), i.e. the writer
   cannot even express an indirect frame; reading it back gives `Position().Direct()==True` and
   `DirectFaces` does nothing. Any raw `AXIS2_PLACEMENT_3D` builds an inherently right-handed
   `gp_Ax2`/`gp_Ax3` (`StepToGeom` MakeAxis2Placement / MakeTransformation3d), so no Part-21
   encoding yields an indirect surface after read.

2. **Negative semi-angle cone.** In-memory: `Geom_ConicalSurface(ax3, semi=-0.5236, r=5)` has
   `SemiAngle()==-0.5236`, and `DirectFaces` modifies it (SemiAngle→+0.5236) — the operator fires.
   But hand-forcing a negative semi-angle into the STEP bytes
   (`CONICAL_SURFACE('',#p,5.,-0.523598775598)`) and reading it back yields
   `SemiAngle()==1e-12` — `StepToGeom.cxx:1139` clamps any negative semi-angle to
   `Precision::Angular()` before `Geom_ConicalSurface` construction. So `DirectFaces` sees a
   positive (degenerate-tiny) cone and does nothing.

Both routes independently reproduce the two facts in the existing `problems.json` note. The
runtime-scaffold approach that worked for Target 2 cannot rescue Target 1: the scaffold can only
invoke the repair on the shape the reader produced, and the reader has already forced that shape
to a direct frame / positive semi-angle. Conclusion: genuinely STEP-unreachable; correctly left
a GAP carve-out.
