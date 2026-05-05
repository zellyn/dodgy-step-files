# §12.3 Tsh validation

Auto-generated heuristic verdicts. CONFIRMED = parser/oracle behavior matches catalog claim. CONCERN = needs manual check. ERROR = tooling problem.

## Per-file

Tsh001 CONCERN — silent corruption signal but catalog doesn't explicitly claim it — ManifoldSolidBrep.outer references OPEN_SHELL
Tsh002 CONCERN — silent corruption signal but catalog doesn't explicitly claim it — FACETED_BREP.outer references OPEN_SHELL
Tsh003 CONCERN — silent corruption signal but catalog doesn't explicitly claim it — Closed solid round-trips as SHELL_BASED_SURFACE_MO
Tsh004 CONCERN — silent corruption signal but catalog doesn't explicitly claim it — Sheet bodies imported in place of solids (FEA pipe
Tsh005 CONFIRMED — silent corruption — 109 entities parsed but no shape — Solid demoted by stricter receiver tolerance ("cle
Tsh006 CONFIRMED — silent corruption — 99 entities parsed but no shape — Bundled component STEP packages emit OPEN_SHELL co
Tsh007 CONCERN — silent corruption signal but catalog doesn't explicitly claim it — `IsClosed` flag inconsistent with actual shell top
Tsh008 CONFIRMED — silent corruption — 108 entities parsed but no shape — Mis-oriented faces in shell (Möbius-detect)
Tsh009 CONFIRMED — silent corruption — 108 entities parsed but no shape — Solid built from open shell with inward-pointing o
Tsh010 CONCERN — silent corruption signal but catalog doesn't explicitly claim it — Reversed face normal in closed shell ("inside-out"
Tsh011 CONCERN — silent corruption signal but catalog doesn't explicitly claim it — `FACE_OUTER_BOUND` orientation flag inconsistent w
Tsh012 CONCERN — silent corruption signal but catalog doesn't explicitly claim it — Mixed `.T.`/`.F.` flags on `ORIENTED_EDGE` mismatc
Tsh013 MERGED — merged stub — `ShapeFix_Face::FixSplitFace` — face needing split (multiple
Tsh015 CONCERN — silent corruption signal but catalog doesn't explicitly claim it — Brep_with_voids: void shell oriented `.T.` instead
Tsh018 CONFIRMED — silent corruption — 42 entities parsed but no shape — Volume orientation mismatch between `LastShape()` 
Tsh019 CONFIRMED — silent corruption — 79 entities parsed but no shape — Non-manifold edge (≥3 incident faces) in shell or 
Tsh020 CONFIRMED — silent corruption — 83 entities parsed but no shape — Edge appearing only once or more than twice on fac
Tsh021 CONFIRMED — silent corruption — 58 entities parsed but no shape — Non-manifold vertex (bowtie / hourglass / fan-of-f
Tsh022 CONFIRMED — silent corruption — 66 entities parsed but no shape — Non-manifold STEP loses XCAF attributes (color/PMI
Tsh023 ERROR — missing or empty pre-computed JSON: Tsh023.json
Tsh024 MERGED — merged stub — `CONNECTED_FACE_SET` containing non-face entities
Tsh026 CONFIRMED — silent corruption — 115 entities parsed but no shape — Coincident / duplicate faces in shell
Tsh027 CONFIRMED — silent corruption — 204 entities parsed but no shape — Coincident-but-not-shared faces between adjacent s
Tsh028 CONFIRMED — silent corruption — 69 entities parsed but no shape — `STYLED_ITEM` lost / mis-bound after sliver-face r
Tsh029 CONFIRMED — silent corruption — 99 entities parsed but no shape — Naked / dangling edge in shell (free edges, LOTAR 
Tsh030 MERGED — merged stub — Non-finite (infinite) solid built from open shell
Tsh032 CONFIRMED — silent corruption — 108 entities parsed but no shape — Inconsistent face orientation in mesh-derived BREP
Tsh033 CONFIRMED — silent corruption — 48 entities parsed but no shape — Mirrored block instances flip surface direction wi
Tsh035 CONFIRMED — silent corruption — 24 entities parsed but no shape — DEGENERATE_TOROIDAL_SURFACE orientation depends on
Tsh036 CONCERN — silent corruption signal but catalog doesn't explicitly claim it — Revolved shape imported with complementary (revers
Tsh037 MERGED — merged stub — Free wires/edges in compound (Q029, F080 — no faces, INTERNA
Tsh039 CONFIRMED — silent corruption — 65 entities parsed but no shape — Self-touching boundary cycle (figure-eight wire af
Tsh040 CONFIRMED — silent corruption — 80 entities parsed but no shape — `OPEN_SHELL`s with shared interior edge mis-classi
Tsh041 CONCERN — silent corruption signal but catalog doesn't explicitly claim it — Shell extrusion with shared edges yields CompSolid
Tsh042 CONCERN — silent corruption signal but catalog doesn't explicitly claim it — `bad vertex`: vertex misplaced relative to inciden

## Summary
Total files: 35
CONFIRMED: 18
CONCERN: 12
ERROR: 1
MERGED: 4
