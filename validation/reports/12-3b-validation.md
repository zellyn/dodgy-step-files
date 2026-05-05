# §12.3 Twi validation

Auto-generated heuristic verdicts. CONFIRMED = parser/oracle behavior matches catalog claim. CONCERN = needs manual check. ERROR = tooling problem.

## Per-file

Twi001 CONFIRMED — silent corruption — 11 entities parsed but no shape — Empty edge_list in EDGE_LOOP
Twi002 CONCERN — silent corruption signal but catalog doesn't explicitly claim it — Single-edge EDGE_LOOP with non-coincident start/en
Twi003 CONCERN — silent corruption signal but catalog doesn't explicitly claim it — EDGE_LOOP edges not head-to-tail (disconnected adj
Twi004 CONCERN — silent corruption signal but catalog doesn't explicitly claim it — ORIENTED_EDGE wrapping another ORIENTED_EDGE
Twi005 CONCERN — silent corruption signal but catalog doesn't explicitly claim it — ORIENTED_EDGE.edge_element references non-EDGE_CUR
Twi006 CONCERN — silent corruption signal but catalog doesn't explicitly claim it — ORIENTED_EDGE underlying EDGE_CURVE is null/missin
Twi007 CONCERN — silent corruption signal but catalog doesn't explicitly claim it — Disordered edges in wire (head-to-tail breakage so
Twi008 CONFIRMED — silent corruption — 28 entities parsed but no shape — Wire ordering ambiguous between 2D and 3D ("miscib
Twi009 CONFIRMED — silent corruption — 59 entities parsed but no shape — Common vertex shared between two distinct wires (S
Twi010 CONCERN — silent corruption signal but catalog doesn't explicitly claim it — Figure-eight / pinched wire (wire revisits a verte
Twi011 MERGED — merged stub — Wire tail / hair (thin spike beyond max-angle/width threshol
Twi013 MERGED — merged stub — Small / sliver / zero-length edges (FixSmall)
Twi017 CONCERN — silent corruption signal but catalog doesn't explicitly claim it — Closed 3D curve with two distinct VERTEX_POINTs (s
Twi018 CONFIRMED — silent corruption — 17 entities parsed but no shape — Edge with start==end vertex but open curve (zero a
Twi019 CONFIRMED — silent corruption — 25 entities parsed but no shape — Closed edges need splitting at parametric break
Twi020 CONFIRMED — silent corruption — 23 entities parsed but no shape — Missing seam edge on closed (periodic) surface
Twi021 CONFIRMED — silent corruption — 24 entities parsed but no shape — Missing degenerate edge at surface singularity (co
Twi022 MERGED — merged stub — Seam edge with swapped pcurves (FixSeam)
Twi024 MERGED — merged stub — Wires forming inner loops outside outer loop (mis-classified
Twi027 CONFIRMED — silent corruption — 19 entities parsed but no shape — ConnectEdgesToWires fails on INTERNAL-only edges /
Twi028 CONFIRMED — silent corruption — 28 entities parsed but no shape — Disordered edges on torus — wire-reorder triggers 
Twi029 CONFIRMED — silent corruption — 24 entities parsed but no shape — STEP writer drops entire wire if it contains a deg
Twi030 CONFIRMED — silent corruption — 38 entities parsed but no shape — Degenerate edge re-encountered for multiple faces
Twi031 CONFIRMED — silent corruption — 31 entities parsed but no shape — Degenerate edges duplicated at apex (Pro/E)
Twi032 CONCERN — silent corruption signal but catalog doesn't explicitly claim it — Closed face needs splitting at seam (ShapeUpgrade_
Twi033 CONCERN — silent corruption signal but catalog doesn't explicitly claim it — Wire with two coincident edges (FixWiresTwoCoincEd
Twi034 CONCERN — silent corruption signal but catalog doesn't explicitly claim it — Open vs closed wire mismatched assumption (ClosedW
Twi035 CONFIRMED — silent corruption — 22 entities parsed but no shape — Sphere given by two meridians (special wire shape)
Twi036 CONFIRMED — silent corruption — 25 entities parsed but no shape — Lacking edge: UV gap not closable by vertex tolera
Twi037 CONFIRMED — silent corruption — 58 entities parsed but no shape — Free bounds need joining (sewing) — open wire trea
Twi038 CONCERN — silent corruption signal but catalog doesn't explicitly claim it — Wire-reorder doesn't trigger replacement (FixReord
Twi039 CONFIRMED — silent corruption — 23 entities parsed but no shape — `Wire self-interference check failed` on mirrored 
Twi040 CONCERN — silent corruption signal but catalog doesn't explicitly claim it — `Could not fix wire in surface` regression after O
Twi041 CONCERN — silent corruption signal but catalog doesn't explicitly claim it — Wire visits internal vertex causing infinite loop 
Twi043 CONCERN — silent corruption signal but catalog doesn't explicitly claim it — Disjoined / Same/Close wire vertices needing resol
Twi044 CONFIRMED — silent corruption — 59 entities parsed but no shape — Internal wires below area threshold (RemoveInterna
Twi045 CONFIRMED — silent corruption — 59 entities parsed but no shape — FixSmallAreaWire on reversed face wrongly orients 

## Summary
Total files: 37
CONFIRMED: 18
CONCERN: 15
MERGED: 4
