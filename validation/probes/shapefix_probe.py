"""Does a REAL ShapeFix pass produce a signal the current oracle cannot see?

The published token (reject/empty/shape(n)) comes from the READ outcome, so no
choice of healing knob can move it. This probes the two places a real healing
signal could live instead:
    (1) topology counts before vs after ShapeFix_Shape
    (2) ShapeFix's own status flags -- what it says it repaired
"""
import sys, json
from OCP.STEPControl import STEPControl_Controller, STEPControl_Reader
from OCP.IFSelect import IFSelect_RetDone
from OCP.ShapeFix import ShapeFix_Shape
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import (TopAbs_VERTEX, TopAbs_EDGE, TopAbs_WIRE, TopAbs_FACE,
                        TopAbs_SHELL, TopAbs_SOLID)
from OCP.ShapeExtend import ShapeExtend_Status

KINDS = [("vertex", TopAbs_VERTEX), ("edge", TopAbs_EDGE), ("wire", TopAbs_WIRE),
         ("face", TopAbs_FACE), ("shell", TopAbs_SHELL), ("solid", TopAbs_SOLID)]

def counts(sh):
    if sh is None or sh.IsNull():
        return {k: 0 for k, _ in KINDS}
    out = {}
    for k, t in KINDS:
        e, c = TopExp_Explorer(sh, t), 0
        while e.More():
            c += 1; e.Next()
        out[k] = c
    return out

def probe(path):
    STEPControl_Controller.Init_s()
    r = STEPControl_Reader()
    if r.ReadFile(path) != IFSelect_RetDone:
        return {"token": "reject"}
    n = r.TransferRoots()
    sh = r.OneShape()
    if sh.IsNull() or n == 0:
        return {"token": "empty"}
    before = counts(sh)
    try:
        sf = ShapeFix_Shape(sh)
        sf.Perform()
        fixed = sf.Shape()
        after = counts(fixed)
        flags = [nm for nm, st in [
            ("DONE1", ShapeExtend_Status.ShapeExtend_DONE1),
            ("DONE2", ShapeExtend_Status.ShapeExtend_DONE2),
            ("DONE3", ShapeExtend_Status.ShapeExtend_DONE3),
            ("DONE4", ShapeExtend_Status.ShapeExtend_DONE4),
            ("DONE5", ShapeExtend_Status.ShapeExtend_DONE5),
            ("DONE6", ShapeExtend_Status.ShapeExtend_DONE6),
            ("DONE7", ShapeExtend_Status.ShapeExtend_DONE7),
            ("DONE8", ShapeExtend_Status.ShapeExtend_DONE8),
            ("FAIL1", ShapeExtend_Status.ShapeExtend_FAIL1),
            ("FAIL2", ShapeExtend_Status.ShapeExtend_FAIL2),
        ] if sf.Status(st)]
        return {"token": f"shape({n})", "before": before, "after": after,
                "changed": before != after, "flags": flags}
    except Exception as e:
        return {"token": f"shape({n})", "shapefix_exception": repr(e)[:120]}

print(json.dumps(probe(sys.argv[1])))
