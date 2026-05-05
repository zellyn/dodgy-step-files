"""Subprocess-isolated runner for validate + tier3_geometric.

Reason: OCCT load can segfault on some adversarial fixtures, killing the
in-process script. Running each oracle in its own subprocess isolates that.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

VALIDATION_DIR = Path("/Users/zellyn/gh/cad/research/validation")


def _run_pyfunc(snippet: str, timeout: int = 60) -> dict:
    """Run a Python snippet in a subprocess; return parsed JSON or error info."""
    cmd = ["uv", "run", "python", "-c", snippet]
    try:
        proc = subprocess.run(
            cmd, cwd=str(VALIDATION_DIR),
            capture_output=True, timeout=timeout, text=True,
        )
    except subprocess.TimeoutExpired:
        return {"_status": "timeout"}
    if proc.returncode == 139:
        return {"_status": "segfault", "_stderr_tail": proc.stderr[-300:]}
    if proc.returncode != 0:
        # could still have written valid JSON before segfault on cleanup
        if proc.stdout.strip():
            try:
                return {"_status": "ok_with_exit_err", "_returncode": proc.returncode,
                        "data": json.loads(proc.stdout)}
            except Exception:
                pass
        return {"_status": "error", "_returncode": proc.returncode,
                "_stderr_tail": proc.stderr[-300:], "_stdout_tail": proc.stdout[-300:]}
    try:
        return {"_status": "ok", "data": json.loads(proc.stdout)}
    except Exception as e:
        return {"_status": "bad_json", "_error": str(e), "_stdout_tail": proc.stdout[-300:]}


def byte_and_entity(path: Path) -> dict:
    s = f"""
import sys, json, os
from pathlib import Path
sys.path.insert(0, 'src')
from step_corpus.validate import byte_signature, entity_summary
p = Path({str(path)!r})
out = dict(byte_signature=byte_signature(p), entity_summary=entity_summary(p))
sys.stdout.write(json.dumps(out, default=str))
sys.stdout.flush()
os._exit(0)
"""
    return _run_pyfunc(s, timeout=20)


def ifcopenshell_check(path: Path) -> dict:
    s = f"""
import sys, json, os
from pathlib import Path
sys.path.insert(0, 'src')
from step_corpus.validate import parse_ifcopenshell
p = Path({str(path)!r})
sys.stdout.write(json.dumps(parse_ifcopenshell(p), default=str))
sys.stdout.flush()
os._exit(0)
"""
    return _run_pyfunc(s, timeout=20)


def occt_check(path: Path, healing: bool) -> dict:
    s = f"""
import sys, json, os
from pathlib import Path
sys.path.insert(0, 'src')
from step_corpus.validate import parse_occt
p = Path({str(path)!r})
sys.stdout.write(json.dumps(parse_occt(p, healing={healing}), default=str))
sys.stdout.flush()
os._exit(0)
"""
    return _run_pyfunc(s, timeout=60)


def tier3_check(path: Path) -> dict:
    s = f"""
import sys, json, os
from pathlib import Path
sys.path.insert(0, 'src')
from step_corpus.tier3_geometric import geometric_report
p = Path({str(path)!r})
sys.stdout.write(json.dumps(geometric_report(p), default=str))
sys.stdout.flush()
os._exit(0)
"""
    return _run_pyfunc(s, timeout=90)


def gather(path: Path) -> dict:
    return {
        "path": str(path),
        "byte_entity": byte_and_entity(path),
        "ifcopenshell": ifcopenshell_check(path),
        "occt_heal_on": occt_check(path, True),
        "occt_heal_off": occt_check(path, False),
        "tier3": tier3_check(path),
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: _runner.py <stp> [<stp> ...]", file=sys.stderr)
        sys.exit(2)
    out = {p: gather(Path(p)) for p in sys.argv[1:]}
    json.dump(out, sys.stdout, indent=2, default=str)
