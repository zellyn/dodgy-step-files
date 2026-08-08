"""Which BRepCheck statuses does each fixture actually raise?

Companion to heal_coverage_probe.py, but measuring at a point where the
measurement is VALID. That probe failed validation because ShapeFix on a
post-transfer shape is fixing something OCCT already normalised. BRepCheck is
different: it is OCCT's VALIDITY DETECTOR, and running it on the transferred
shape is precisely its intended use. So a status raised here is real evidence,
and a status absent here is evidence of absence *for the transferred shape*
(which may still differ from the bytes -- see the caveat below).

Motivation: `Bo005` was the sole cited witness for `bc-unorientable-shape` but
its bytes contain ZERO edges shared between two loops, so no orientation
contradiction exists to detect -- it measures IsValid=True. A fixture cited as
a witness for a defect it does not encode is a fidelity bug. This sweep finds
that class corpus-wide.

CAVEAT that must stay attached to any use of this output: BRepCheck runs AFTER
the STEP reader has already repaired much of what it finds. A fixture can
legitimately encode a defect in its bytes, have OCCT synthesise the fix during
transfer, and therefore show NoError here. That is the documented
"oracle-invisible" class -- confirmed for Gp175/Gp091, where the bytes omit the
PCURVE and the reader synthesises one. So:

    fires a status   => the defect survives transfer and is detectable. Strong.
    NoError          => AMBIGUOUS. Either pre-healed (fine) or not encoded
                        (a bug). Distinguish by reading the BYTES, never by
                        this output alone.

    cd validation && uv run python probes/brepcheck_survey.py <file.stp>
"""
from __future__ import annotations

import json
import sys


def survey(path: str) -> dict:
    from OCP.STEPControl import STEPControl_Controller, STEPControl_Reader
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.BRepCheck import BRepCheck_Analyzer, BRepCheck_Status
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopAbs import (TopAbs_VERTEX, TopAbs_EDGE, TopAbs_WIRE,
                            TopAbs_FACE, TopAbs_SHELL, TopAbs_SOLID)

    STEPControl_Controller.Init_s()
    reader = STEPControl_Reader()
    if reader.ReadFile(path) != IFSelect_RetDone:
        return {"token": "reject", "valid": None, "statuses": {}}
    n_roots = reader.TransferRoots()
    shape = reader.OneShape()
    if shape.IsNull() or n_roots == 0:
        return {"token": "empty", "valid": None, "statuses": {}}

    an = BRepCheck_Analyzer(shape)
    statuses: dict[str, int] = {}
    counts = {}
    for label, t in [("vertex", TopAbs_VERTEX), ("edge", TopAbs_EDGE),
                     ("wire", TopAbs_WIRE), ("face", TopAbs_FACE),
                     ("shell", TopAbs_SHELL), ("solid", TopAbs_SOLID)]:
        exp, n = TopExp_Explorer(shape, t), 0
        while exp.More():
            sub = exp.Current()
            n += 1
            try:
                res = an.Result(sub)
            except Exception:
                res = None
            if res is not None:
                try:
                    for st in res.Status():
                        if st != BRepCheck_Status.BRepCheck_NoError:
                            name = str(st).split(".")[-1]
                            statuses[name] = statuses.get(name, 0) + 1
                except Exception:
                    statuses["_status_unreadable"] = \
                        statuses.get("_status_unreadable", 0) + 1
            exp.Next()
        counts[label] = n

    return {"token": f"shape({n_roots})", "valid": bool(an.IsValid()),
            "counts": counts, "statuses": statuses}


def main() -> int:
    try:
        print(json.dumps(survey(sys.argv[1])))
    except Exception as e:      # never let a crash read as "clean"
        print(json.dumps({"token": "probe_error", "error": repr(e)[:200]}))
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
