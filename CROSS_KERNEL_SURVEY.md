# Cross-kernel validation: kernel landscape survey

**Status:** B3.1 + B3.2 from `BACKLOG.md`.

Goal: pick the next 1-2 kernels to add as oracles alongside OCCT, gmsh,
and ifcopenshell. Each new oracle gives every fixture a differential
truth table — disagreements are the highest-information signal a kernel-
grading corpus can carry.

## Current oracle inventory

| Oracle | Source file | Coverage | Notes |
|---|---|---|---|
| OCCT (heal on/off) | `_occt_oracle.py` (via `validate2.py`) | All STEP fixtures | Primary truth source |
| gmsh | invoked from `validate2.py` | All STEP fixtures | autofix on/off variants |
| ifcopenshell | invoked from `validate2.py` | STEP-as-IFC fixtures | Schema_n/a for most STEP fixtures |
| Tier-3 geometric | `tier3_geometric.py` (OCCT-based) | All loadable STEP | Faces / edges / vertices |
| OCAF / XCAF | `_ocaf_oracle.py` (OCCT) | §12.6-assembly | Label/color/transform/assembly persistence |
| Manifold3d | `_manifold_oracle.py` | Tessellated geometry | empty / not_manifold / segfault |
| Writer pathology | `_writer_oracle.py` | §12.13 only | Byte-level reproduction |
| Schema vocabulary | `_schema_oracle.py` | All STEP | FILE_SCHEMA vs entity vocabulary |
| Mesh (pure-Python) | `_mesh_oracle.py` | §12.14 mesh JSON | NEW (Q4.5 first cut) |

OCCT is the underlying engine for 4 of the above. Diversification means
picking kernels that DON'T share OCCT as a backend.

## Candidate kernels for the next oracle

| Kernel | Lang | STEP-read native? | LGPL/license OK | Install difficulty | Diversity from OCCT |
|---|---|---|---|---|---|
| **CGAL PMP** | C++ + Python bindings | No (needs OFF/PLY intermediate) | GPL/LGPL dual | medium (apt cgal-dev or conda) | High — independent codebase |
| **Geogram** | C++ | No (needs OBJ/PLY) | LGPL | medium (build from source) | High |
| **libIGES** | C++ | IGES native, not STEP | LGPL | low | Low — STEP via OCCT |
| **Open Cascade community fork** (OCE) | C++ | Yes | LGPL | low | **None — same lineage** |
| **PythonOCC** | Python bindings to OCC | Yes | LGPL | low (pip) | **None — wraps OCCT** |
| **pythonocc-core** | Python | Yes | LGPL | low (pip) | **None — same as PythonOCC** |
| **trimesh** | Python | No (mesh-only) | MIT | trivial (pip) | Medium — mesh focus |
| **manifold3d** | C++/Python | No (mesh-only) | MIT | already installed | (already an oracle) |
| **OpenSCAD** | C++ | No (mesh import only via CGAL) | GPLv2 | medium (apt) | Medium — relies on CGAL |
| **libfive** | C++ | No (SDF-based) | MPL2 | medium (build from source) | High |
| **Solvespace** | C++ | Yes (own parser) | GPLv3 | low (apt) | **High — independent STEP parser** |
| **FreeCAD CLI (OCC backend)** | Python | Yes (OCC) | LGPL | medium (apt or conda) | None — wraps OCCT |
| **OpenCASCADE.js** (in-browser) | JS+WASM | Yes | LGPL | low (npm) | Low — wraps OCCT |
| **Step-NX (Brazilian academic)** | C++ | Yes | LGPL | high (academic distribution) | High — independent |
| **STIX** (NIST) | Python/C++ | Yes (validator) | public domain | medium | High — independent EXPRESS-based |

## Top candidates (decision)

After this survey, the two strongest non-OCCT candidates are:

### #1: Solvespace
- **Why**: independent STEP parser (not OCCT-based), GPL3 license OK
  for our use (we're not redistributing — just running as a subprocess
  oracle), apt-installable on Ubuntu 22.04 (CI runner).
- **Coverage**: Solvespace's STEP import handles AP203/AP214 reads. It's
  primarily a constraint solver; geometric load/transfer subset overlaps
  with what we need for cross-kernel disagreement detection.
- **Risk**: smaller community than OCCT; may not handle edge cases the
  catalog targets (which is exactly the signal we want).

### #2: STIX (NIST step-spec compliance checker)
- **Why**: NIST's reference EXPRESS-based STEP validator. Public domain.
  Implements the formal AP214/AP242 EXPRESS schema rules. Catches
  spec-conformance issues OCCT silently heals.
- **Coverage**: EXPRESS-level (entity definitions, WHERE rules, function
  constraints). Doesn't load geometry — purely structural.
- **Risk**: distribution availability uncertain (NIST mirror checks
  required). May overlap with the existing `_part21_validator` more than
  diversify it.

## Recommendation

Start with **Solvespace** for B3.3:
1. Add `_solvespace_oracle.py` that runs `solvespace --convert <file.stp>`
   in subprocess isolation, captures exit code + stderr, emits a JSON
   record `{loaded, n_solids, error, error_class}` matching the
   `_occt_oracle.py` schema.
2. Add solvespace install to `.github/workflows/validate.yml`
   (`sudo apt-get install -y solvespace`).
3. Wire into `validate2.py` as an additional column in the per-fixture
   JSON record.
4. Run the corpus once; cluster fixtures by kernel-agreement signature
   `(occt_status, solvespace_status)`; surface high-disagreement fixtures
   for triage.

Defer Geogram, CGAL PMP, libfive to a second wave once we have a working
single-kernel-add precedent.

## Notes for B3.4 (signature schema)

Per-fixture record should grow to include:
```json
{
  "occt_heal_on": "shape" | "reject" | "empty" | "signal(N)" | ...,
  "occt_heal_off": ...,
  "gmsh_autofix_on": ...,
  "gmsh_autofix_off": ...,
  "ifcopenshell": ...,
  "solvespace": "loaded" | "rejected" | "error" | "timeout",
  ...
}
```

Per-fixture *signature* is `(every kernel's status concatenated)`. Cluster
on signature; rank by cluster size descending. Singleton clusters and
small clusters are where the interesting disagreements live.
