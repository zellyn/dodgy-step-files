# §12.3 Tfa validation

Auto-generated heuristic verdicts. CONFIRMED = parser/oracle behavior matches catalog claim. CONCERN = needs manual check. ERROR = tooling problem.

## Per-file

Tfa001 CONFIRMED — silent corruption — 37 entities parsed but no shape — FACE_SURFACE.face_geometry is null
Tfa002 CONFIRMED — silent corruption — 22 entities parsed but no shape — Unbound ADVANCED_FACE (no FACE_OUTER_BOUND, no FAC
Tfa003 CONFIRMED — silent corruption — 30 entities parsed but no shape — FaceOuterBound translation failed (face incomplete
Tfa004 CONFIRMED — silent corruption — 26 entities parsed but no shape — Missing natural bound on sphere / torus face
Tfa005 CONFIRMED — silent corruption — 31 entities parsed but no shape — Periodic face given by single belt wire (degenerat
Tfa006 CONFIRMED — silent corruption — 38 entities parsed but no shape — Spot face: face collapsed to a point
Tfa007 CONCERN — silent corruption signal but catalog doesn't explicitly claim it — Strip face: face one-dimensional within tolerance
Tfa008 CONFIRMED — silent corruption — 38 entities parsed but no shape — Pin / sliver face
Tfa010 CONCERN — silent corruption signal but catalog doesn't explicitly claim it — Splitting vertex within face (vertex of one wire o
Tfa011 CONFIRMED — silent corruption — 60 entities parsed but no shape — Multiple outer wires (face needs split)
Tfa012 CONFIRMED — silent corruption — 38 entities parsed but no shape — Face area zero / negative after fixshape
Tfa013 CONFIRMED — silent corruption — 38 entities parsed but no shape — Face area exceeds limit (needs split)
Tfa014 CONFIRMED — silent corruption — 38 entities parsed but no shape — FixFaceSize: small face below threshold
Tfa015 CONFIRMED — OCCT loaded shape; defect likely consumer-side — DropSmallSolids / debris solids from booleans
Tfa016 CONCERN — silent corruption signal but catalog doesn't explicitly claim it — Faces share same supporting surface — UnifySameDom
Tfa017 CONFIRMED — silent corruption — 56 entities parsed but no shape — UnifySameDomain inflates vertex tolerance
Tfa018 CONFIRMED — silent corruption — 44 entities parsed but no shape — UnifySameDomain SIGSEGV / invalid result on Recons
Tfa019 CONCERN — silent corruption signal but catalog doesn't explicitly claim it — FaceConnect: vertices not shared between faces
Tfa020 MERGED — merged stub — Sewing — free bounds on closed shell
Tfa022 CONCERN — silent corruption signal but catalog doesn't explicitly claim it — ConnectEdgesToWires produces wires with wrong Clos
Tfa023 CONCERN — silent corruption signal but catalog doesn't explicitly claim it — ShellSewing — disconnected adjacent faces (sewing 
Tfa024 CONFIRMED — silent corruption — 50 entities parsed but no shape — Glue Faces (coincident faces)
Tfa025 CONCERN — silent corruption signal but catalog doesn't explicitly claim it — Glue Edges (coincident edges)
Tfa026 MERGED — merged stub — OFFSET_SURFACE used (out of AP214 scope)
Tfa028 MERGED — merged stub — Surface revolution span exceeds angle cap (split_angle)
Tfa030 CONFIRMED — silent corruption — 41 entities parsed but no shape — Reshape recording / location handling lost
Tfa031 CONFIRMED — silent corruption — 40 entities parsed but no shape — Locations attached to sub-shapes — instance flatte
Tfa032 MERGED — merged stub — bopcheck unclean after UnifySameDomain on boolean result
Tfa034 MERGED — merged stub — Face orientation flag inconsistent with shell normal (FixFac

## Summary
Total files: 29
CONFIRMED: 17
CONCERN: 7
MERGED: 5
