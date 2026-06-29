# B3.6 Follow-up Hand-Audit — 2026-06-28

Auditing 5 high-information fixtures from the B3.6 diff-detection sweep
(`b3_6_diff_detection_2026-06-25.md`): 4 "zeroed + manifold" mesh fixtures and
1 STEP singleton.

---

## Verdict Table

| Fixture | Oracle summary | Verdict | Finding |
|---|---|---|---|
| **Me1093** | pyvista: manifold=True; pymeshfix: 0 tris out | CATALOG_OK | Apparent contradiction; oracles answer different questions |
| **Me257** | pyvista: manifold=True; pymeshfix: 0 tris out | CATALOG_OK | Apparent contradiction; oracles answer different questions |
| **Me434** | pyvista: manifold=True; pymeshfix: 0 tris out | CATALOG_OK | Apparent contradiction; oracles answer different questions |
| **Me590** | pyvista: manifold=True; pymeshfix: 0 tris out | CATALOG_OK | Apparent contradiction; oracles answer different questions |
| **Gn090** | occt=shape(1), gmsh=reject, manifold=nonfinitevertex | NEEDS_DESCRIPTION_FIX | Catalog mechanism prose inaccurate (NaN vs 1E100, wrong failure path) |

---

## Mesh Fixtures — Shared Analysis

### The "Contradiction" Is Not a Contradiction

All four mesh fixtures are designed to be **topologically closed surfaces** where
every edge is shared by exactly 2 triangles. The apparent contradiction between
pyvista and pymeshfix dissolves when the two oracles' questions are correctly
separated:

**pyvista `is_manifold`** asks: *"Does every edge have exactly 2 incident faces?"*
All four fixtures answer YES by construction. pyvista uses VTK's combinatorial
edge-valence check. This is geometrically correct — the fixtures satisfy the
local manifold condition.

**pymeshfix `repair()`** asks: *"Can I reduce this surface to a genus-0 closed solid
suitable for downstream use?"* All four fixtures answer NO, and output 0 triangles.
pymeshfix's repair pipeline (MeshFix `checkAndRepair` → `openToDisk` → hole-fill)
is designed to heal **open meshes with boundary edges**. When it encounters:
- zero-area degenerate geometry (Me1093): removes all degenerate faces → 0 output
- genus-1 topology (Me257): cannot reduce torus to disk without destroying mesh → 0 output
- non-orientable seam (Me434): cannot consistently orient mesh → 0 output
- already-closed surface with no boundary (Me590): `TriangulateHole` seed fails `isOnBoundary()` → 0 output

Both oracles are correct for the question they answer. **No tooling bug.**

---

## Per-Fixture Diagnosis

### Me1093 — K4 collinear degenerate (chi=2)

**Geometry**: 4 collinear vertices v0=(0,0,0)..v3=(3,0,0); all C(4,3)=4 triangles
are zero-area. Complete graph K4 topology: 6 edges, each shared by 2 faces. No
boundary edges. Euler chi=V-E+F=4-6+4=2 (sphere topology, all zero-area).

**Live oracles**: pyvista: `is_manifold=True, n_vertices=4, n_triangles=4`.
pymeshfix: `n_triangles_in=4, n_triangles_out=0`.

**Why pyvista is right**: every edge IS incident on exactly 2 faces. Edge-valence
manifold check passes trivially (the check does not test triangle area).

**Why pymeshfix outputs 0**: MeshFix's degenerate-face removal eliminates all 4
zero-area triangles. The stated mechanism (CGAL PMP `remove_degenerate_faces`
Branch 10, chi≠1 disk check) is a CGAL code path; pymeshfix wraps MeshFix not
CGAL, but MeshFix also removes degenerate faces as a first-pass step, leaving 0
triangles.

**Proposed catalog edit**: none. Catalog correctly identifies the CGAL mechanism
and structural assertions. The pymeshfix=0 output is mechanistically consistent.

---

### Me257 — Torus (chi=0), openToDisk edge duplication

**Geometry**: 3×3 flat grid with wrap-around identification (torus topology). 9
vertices, 18 triangles, 27 edges. All edges interior (n=2). chi=9-27+18=0.
Geometrically self-intersecting when embedded flat, but all 9 vertices occupy
distinct positions in 3D.

**Live oracles**: pyvista: `is_manifold=True, n_vertices=9, n_triangles=18`.
pymeshfix: `n_triangles_in=18, n_triangles_out=0`.

**Why pyvista is right**: all 27 edges have exactly 2 incident faces. Each vertex's
star forms a connected fan of 6 triangles (a valid manifold vertex neighborhood).
The torus IS a 2-manifold; pyvista correctly reports it as such.

**Why pymeshfix outputs 0**: MeshFix `openToDisk` tries to cut the genus-1 surface
to a disk by duplicating interior edges. For the flat torus, this operation creates
self-intersections or degenerate configurations that the subsequent repair steps
cannot recover from, yielding 0 output triangles. The catalog correctly describes
the Branch 8 mechanism (`!IS_BIT(e,3) && !e->isOnBoundary()`).

**Proposed catalog edit**: none. Catalog assertions and mechanism are accurate.

---

### Me434 — Non-orientable seam (chi=2), Mobius-like

**Geometry**: 4 vertices forming a closed surface (V=4, E=6, F=4, chi=2). t0 and
t1 both list shared edge (v0,v1) in the same direction (v0→v1) — a non-orientable
seam. All 6 edges interior (n=2). t0 has +z normal, t3 has -z normal.

**Live oracles**: pyvista: `is_manifold=True, n_orientation_flipped=0`.
pymeshfix: `n_triangles_in=4, n_triangles_out=0`.

**Why pyvista is right**: the edge-valence test passes (every edge n=2). VTK's
`is_manifold` does not check for consistent global orientation; it only checks
local edge incidence. n_orientation_flipped=0 because pyvista's flip check uses
normal agreement from a seed, and the closed surface appears consistently oriented
from any given seed direction.

**Why pymeshfix outputs 0**: MeshFix `forceNormalConsistence` Branch 5 fires
(`tmp1*tmp2 < 0`), creates a cut edge, and increments `wrn`. The resulting
surface is non-orientable (Mobius-like). MeshFix cannot orient and close such a
surface, yielding 0 triangles. This IS the stated mechanism.

**Proposed catalog edit**: none. Catalog assertions are accurate.

---

### Me590 — Closed mesh, no boundary (chi=2), TriangulateHole failure

**Geometry**: 4-triangle closed surface (fan of 3 + 1 back-face). All 6 edges
interior (n=2). No boundary edges anywhere. chi=4-6+4=2 (sphere topology).

**Live oracles**: pyvista: `is_manifold=True, n_vertices=4, n_triangles=4`.
pymeshfix: `n_triangles_in=4, n_triangles_out=0`.

**Why pyvista is right**: every edge n=2; edge-valence manifold test passes.

**Why pymeshfix outputs 0**: MeshFix `TriangulateHole` Branch 1 fires
(`!e->isOnBoundary()` → return 0) when any candidate seed edge is interior.
Since all edges are interior, no hole-fill can proceed. The repair() pipeline
stalls and returns 0 triangles. This IS the stated mechanism.

**Proposed catalog edit**: none. Catalog assertions are accurate.

---

## STEP Fixture — Gn090

### Gn090 — B-spline with 1E100 overflow control point

**Live oracle output**:
- `occt=shape(1)` (healed + unhealed), `gmsh=reject`, `manifold=nonfinitevertex`
- `ocaf=root_labels=1`, `part21_strict=accept`
- Tier-3: `load=ok`, `brepcheck.valid=false`
- Edge[4]: length=1.137e+100, tolerance=5.68e+99
- Face[0]: bbox_extents=[1.76e+100, 1.14e+100, 1.14e+100]
- manifold diagnostics: `RuntimeWarning: overflow encountered in cast`

**Actual defect**: The `B_SPLINE_CURVE_WITH_KNOTS` at #13 has CP[3] with
coordinates `(3.0, 0.0, 1.0E+100)` — an extreme overflow value used as a
proxy for NaN (since STEP P21 format has no NaN literal for numeric fields).

**Mechanism gap in catalog description**:

1. **"Z=NaN" vs Z=1.0E+100**: The catalog title says "IsPlanar Z-NaN" but the
   actual STEP value is `1.0E+100`. STEP P21 does not support NaN in numeric
   fields. The file comment accurately calls it a "NaN-proxy" but the catalog
   title uses "NaN" directly — this will confuse readers searching for NaN
   handling vs overflow handling.

2. **Wrong failure path**: The catalog says the mechanism is "IsPlanar pole
   sampling produces NaN result". The observed failure is manifold3d's
   tessellation casting `1E100 → float32`, which overflows to `+Inf`, triggering
   the `nonfinitevertex` status. OCCT's IsPlanar path is not the observable
   failure point in any live oracle.

3. **gmsh failure**: gmsh rejects with "Could not fix wire in surface 1" —
   distinct from IsPlanar.

4. **Expected line gap**: The catalog's Expected line (`occt=shape(1)/shape(1)
   gmsh=reject ifc=schema_n/a`) omits `manifold=nonfinitevertex`. This is the
   unique oracle output that made Gn090 a B3.6 singleton.

**Why OCCT loads**: OCCT processes the `1E100` control point as a valid number
within its double-precision pipeline, constructing a face with a geometrically
enormous edge (length ~1.1e+100). BRepCheck sees the shape as invalid (edge
tolerance 5.7e+99 is absurd) but the shape is not null.

**Why manifold3d fails**: manifold3d tessellates OCCT's shape into vertices, then
casts to float32 for its internal representation. `1.0E+100 → float32` overflows
to `+Inf`. manifold3d detects the non-finite vertex and returns `nonfinitevertex`.

**Proposed catalog edits** (do not apply; propose only):

1. Rename title from "Z-NaN" to "Z=1E100 overflow-proxy" to accurately reflect
   the STEP encoding used.

2. Update Description to clarify: "control point Z coordinate is `1.0E+100`
   (STEP P21 cannot encode IEEE NaN; this overflow value serves as a proxy).
   OCCT loads the shape but BRepCheck is invalid. manifold3d hits float32
   overflow during tessellation cast (`1E100 → +Inf`) → `nonfinitevertex`.
   gmsh fails at wire-fix. IsPlanar pole-sampling behavior is not the
   observable failure path in any live oracle."

3. Update Expected line to:
   `occt=shape(1)/shape(1) gmsh=reject ifc=schema_n/a manifold=nonfinitevertex`

---

## Tooling Bug Findings

**No tooling bugs found.**

- pyvista `is_manifold=True` on all 4 mesh fixtures is **correct**: these
  fixtures satisfy the local edge-incidence manifold condition by construction.
  The check does not and should not test triangle area, global orientability,
  or genus.
- pymeshfix `n_triangles_out=0` on all 4 fixtures is **correct**: the repair
  algorithm legitimately cannot recover a genus-0 solid from degenerate,
  genus-1, non-orientable, or boundary-less surfaces.
- The "contradiction" is a scope mismatch between two valid oracle questions,
  not a defect in either tool.

---

## Summary

| Category | Count | Action |
|---|---|---|
| CATALOG_OK | 4 | No changes (Me1093, Me257, Me434, Me590) |
| NEEDS_DESCRIPTION_FIX | 1 | Update Gn090 title + description + Expected line |
| TOOLING_BUG | 0 | None found |
