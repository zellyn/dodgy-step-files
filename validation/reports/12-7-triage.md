# §12.7 PMI / GD&T — CONCERN Triage

Source: `12-7-validation.md` (57 files, 56 CONFIRMED, 1 CONCERN, 0 FAIL).

Triage rule applied: kernel-mishandling IS the defect. signal(N) → CONFIRMED. Empty + reject claim → CONFIRMED. Empty + crash → CONFIRMED-WEAK. shape(N) + PMI-not-attached claim → CONFIRMED if PMI entities present but missing GISU links.

## Triaged entries

| ID | Catalog claim | Validate2 evidence | Verdict | Rationale |
|---|---|---|---|---|
| Pmi049 | tessellated_solid with no styled_item; warn + default neutral material | OCCT heal-on/off: `signal(11)`; gmsh autofix-on/off: `signal(11)`; ifcopenshell: schema_class_reject (AP242). Entity summary contains `TESSELLATED_SOLID=1`, `TESSELLATED_SHELL=1`, `TRIANGULATED_FACE=1`, `COORDINATES_LIST=1`; no STYLED_ITEM in distinct_types. Inspecting `Pmi049.stp` confirms `#40 = TESSELLATED_SOLID('unstyled_solid',(#35),$)` with no styled_item referencing it (matches recipe verbatim). | **CONFIRMED** | Two independent kernels (OCCT, gmsh) SIGSEGV on a 26-entity AP242 file whose only structural defect is an unstyled tessellated_solid. signal = CONFIRMED per triage rule. Catalog claim "warn; default neutral material" is the correct expected behavior; SIGSEGV is gross mishandling. The 12-7-validation.md "thin reproducer" note was an artifact of the validator's `top_types` truncation hiding the tessellated entities — the file does contain the claimed defect. |

## Outcome

- Pmi049 reclassified: CONCERN → **CONFIRMED**.
- Updated §12.7 totals: **CONFIRMED 57, CONCERN 0, FAIL 0** (out of 57).

## Notes

- All 57 §12.7 files are minimal AP242_MANAGED_MODEL_BASED_3D_ENGINEERING_MIM_LF reproducers (2.1–4.2 KB).
- ifcopenshell schema_class_reject is uniform and not a §12.7-specific signal (AP242 unsupported by IFC).
- The OCCT/gmsh signal(11) on Pmi049 is consistent with several other §12.7 entries that crash on tessellated-PMI structural defects — the kernel-mishandling pattern is well represented in this section.
