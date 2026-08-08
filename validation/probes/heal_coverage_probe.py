"""Which of OCCT's named repairs does each fixture actually trigger?

The corpus currently grades fixtures on what OCCT's READER does (reject / empty /
shape(n)). That misses the thing the corpus is actually for: OCCT's accumulated
HEALING knowledge lives in ShapeFix_*, and the reader token cannot express any
of it.

ShapeFix_Wire enumerates 13 distinct repairs by name. That list is a far better
coverage denominator than anything derived from shape counts, because it is
OCCT's own taxonomy of "things that go wrong in real STEP wires and how to fix
them" -- exactly the 20-30 years of bug-report-driven knowledge a new kernel
author needs to reimplement.

This probe answers, per fixture:
    which named repairs fire, on which wire, and did the topology change

and corpus-wide:
    which repairs NO fixture exercises  (-> real coverage gaps)
    which fixtures trigger NO repair    (-> possibly weak fixtures)

!! VALIDATED AND FOUND INADEQUATE (2026-08-07). READ THIS BEFORE REUSING. !!
Seven fixtures whose titles claim a specific wire defect were checked for the
matching repair firing: 0 of 7 fired anything. Running ShapeFix at THIS point --
on the post-transfer shape -- measures the wrong thing, because the catalog's
defect lives in the FILE, not in the resulting TopoDS wire. The transfer either
drops the defect (token `empty`, zero wires to measure) or builds a clean wire
from it. Gs175 (Degenerated + SelfIntersection) is the exception, not the rule.
A correct version must apply the repair where the defect still exists -- built
from the file's own entities -- not to OCCT's already-normalised output.
Do NOT build a coverage scoreboard on this as written. See BACKLOG (G).

Read-only measurement. Emits JSON on stdout. Does not touch the catalog and is
not wired into CI -- see probes/README.md.

    cd validation && uv run python probes/heal_coverage_probe.py <file.stp>
"""
from __future__ import annotations

import json
import sys

# The 13 named wire repairs, in OCCT's own declaration order.
WIRE_FIXES = [
    "Reorder", "Small", "Connected", "EdgeCurves", "Degenerated", "Closed",
    "SelfIntersection", "Lacking", "Gaps3d", "Gaps2d", "Notches",
    "FixTails", "RemovedSegment",
]


def probe(path: str) -> dict:
    from OCP.STEPControl import STEPControl_Controller, STEPControl_Reader
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.ShapeFix import ShapeFix_Wire
    from OCP.ShapeExtend import ShapeExtend_Status
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopAbs import TopAbs_FACE, TopAbs_WIRE
    from OCP.TopoDS import TopoDS

    STEPControl_Controller.Init_s()
    reader = STEPControl_Reader()
    if reader.ReadFile(path) != IFSelect_RetDone:
        return {"token": "reject", "fires": {}, "wires": 0}
    n_roots = reader.TransferRoots()
    shape = reader.OneShape()
    if shape.IsNull() or n_roots == 0:
        return {"token": "empty", "fires": {}, "wires": 0}

    # DONE* means "this repair actually fired". FAIL* means it tried and could
    # not. Both are interesting; conflating them would overstate coverage.
    DONE = ShapeExtend_Status.ShapeExtend_DONE
    FAIL = ShapeExtend_Status.ShapeExtend_FAIL

    fires: dict[str, int] = {}
    fails: dict[str, int] = {}
    n_wires = 0
    exp_f = TopExp_Explorer(shape, TopAbs_FACE)
    while exp_f.More():
        face = TopoDS.Face_s(exp_f.Current())
        exp_w = TopExp_Explorer(face, TopAbs_WIRE)
        while exp_w.More():
            wire = TopoDS.Wire_s(exp_w.Current())
            n_wires += 1
            try:
                sfw = ShapeFix_Wire(wire, face, 1.0e-7)
                sfw.Perform()
                for name in WIRE_FIXES:
                    acc = getattr(sfw, "Status" + name, None)
                    if acc is None:
                        continue
                    try:
                        # RemovedSegment is a plain bool with no status arg,
                        # unlike the other twelve. Querying it the same way
                        # would silently mis-score it as never firing.
                        if name == "RemovedSegment":
                            if acc():
                                fires[name] = fires.get(name, 0) + 1
                        elif acc(DONE):
                            fires[name] = fires.get(name, 0) + 1
                        elif acc(FAIL):
                            fails[name] = fails.get(name, 0) + 1
                    except Exception:
                        # An accessor that cannot be queried is NOT evidence of
                        # "did not fire" -- record it rather than scoring it 0.
                        fails.setdefault("_unqueryable:" + name, 0)
                        fails["_unqueryable:" + name] += 1
            except Exception as e:
                fails.setdefault("_wire_exception", 0)
                fails["_wire_exception"] += 1
                fires.setdefault("_note", 0)
            exp_w.Next()
        exp_f.Next()

    return {"token": f"shape({n_roots})", "wires": n_wires,
            "fires": fires, "fails": fails}


def main() -> int:
    try:
        print(json.dumps(probe(sys.argv[1])))
    except Exception as e:                      # never report a crash as "no repairs"
        print(json.dumps({"token": "probe_error", "error": repr(e)[:200]}))
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
