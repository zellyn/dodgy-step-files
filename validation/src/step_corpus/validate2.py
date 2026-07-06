"""Subprocess-isolated multi-oracle validator (v2).

For each oracle, spawn a subprocess (`python -m step_corpus._oracle_workers <oracle> <file>`).
Capture its stdout (one JSON line) and stderr (free-form diagnostics) separately.
Aggregate into a single result.

Benefits over v1:
- OCCT segfaults / aborts in a subprocess don't kill the parent runner.
- Complete stdout/stderr capture (no fd-juggling).
- Each oracle starts with a fresh OCCT/gmsh state; no cross-fixture pollution.
- Easy to add timeout per oracle.

Usage:
    uv run python -m step_corpus.validate2 <file.stp> [--json]
"""

from __future__ import annotations

import io
import json
import os
import re
import subprocess
import sys
import traceback
from pathlib import Path

ORACLES = ["ifcopenshell", "occt_heal_on", "occt_heal_off", "gmsh_autofix_on", "gmsh_autofix_off", "part21_strict", "manifold", "ocaf", "solvespace", "brlcad", "structural"]


def byte_signature(path: Path) -> dict:
    data = path.read_bytes()
    sig = {
        "size": len(data),
        "bom_utf8": data[:3] == b"\xef\xbb\xbf",
        "bom_utf16le": data[:2] == b"\xff\xfe",
        "bom_utf16be": data[:2] == b"\xfe\xff",
        "starts_with_iso_token": data.lstrip().startswith(b"ISO-10303-21"),
        "ends_with_close_token": data.rstrip().endswith(b"END-ISO-10303-21;"),
        "has_crlf": b"\r\n" in data,
        "has_lone_cr": (b"\r" in data) and (b"\r\n" not in data.replace(b"\r\n", b"")),
        "has_nul": b"\x00" in data,
        "has_form_feed": b"\f" in data,
        "high_bit_byte_count": sum(1 for b in data if b >= 0x80),
    }
    try:
        head = data[:8192].decode("latin-1", errors="replace")
        m = re.search(r"FILE_SCHEMA\s*\(\s*\(\s*'([^']+)'", head)
        sig["file_schema"] = m.group(1) if m else None
    except Exception:
        sig["file_schema"] = None
    return sig


def entity_summary(path: Path) -> dict:
    text = path.read_text(encoding="latin-1", errors="replace")
    types: dict[str, int] = {}
    for m in re.finditer(r"#\d+\s*=\s*([A-Z][A-Z0-9_]*)\s*\(", text):
        types[m.group(1)] = types.get(m.group(1), 0) + 1
    return {
        "total_entity_definitions": sum(v for k, v in types.items()),
        "distinct_types": len(types),
        "top_types": dict(sorted(types.items(), key=lambda kv: -kv[1])[:15]),
    }


def run_oracle(oracle: str, path: str, timeout: float = 30.0) -> dict:
    """Spawn an oracle subprocess. Capture stdout/stderr separately. Return aggregated result."""
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "step_corpus._oracle_workers", oracle, path],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as e:
        return {
            "status": "timeout",
            "timeout_seconds": timeout,
            "stdout_partial": (e.stdout or "")[-500:],
            "stderr_partial": (e.stderr or "")[-500:],
        }
    except Exception as e:
        return {"status": "spawn_failed", "error": str(e)[:300]}

    # Parse oracle JSON from stdout
    stdout = proc.stdout or ""
    stderr = proc.stderr or ""
    rc = proc.returncode

    # Strip ANSI color codes from stderr / stdout for cleanliness
    ansi = re.compile(r"\x1b\[[0-9;]*m")
    stderr_clean = ansi.sub("", stderr)
    stdout_clean = ansi.sub("", stdout)

    # Locate the last JSON line on stdout
    payload = None
    for line in stdout_clean.splitlines()[::-1]:
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            try:
                payload = json.loads(line)
                break
            except Exception:
                continue

    # Extract diagnostic lines from stderr (and any non-JSON stdout)
    diag_sources = stderr_clean + "\n" + stdout_clean
    diag_lines = [
        l.strip() for l in diag_sources.splitlines()
        if l.strip()
        and ("ERR" in l or "WARN" in l or "Error" in l or "Warning" in l
             or "Fail" in l or "Exception" in l)
        and not (l.strip().startswith("{") and l.strip().endswith("}"))
    ]

    if rc < 0:
        # Process killed by signal: almost certainly OCCT segfault
        sig = -rc
        return {
            "status": "process_signal",
            "signal": sig,
            "rc": rc,
            "stderr_snippet": stderr_clean[-500:],
            "diagnostics": diag_lines[:20],
            "payload_if_any": payload,
            "note": "subprocess killed by signal; kernel aborted on input",
        }
    if rc != 0 and payload is None:
        return {
            "status": "subprocess_error",
            "rc": rc,
            "stderr_snippet": stderr_clean[-500:],
            "diagnostics": diag_lines[:20],
        }
    if payload is None:
        return {
            "status": "no_json",
            "rc": rc,
            "stdout_snippet": stdout_clean[-500:],
            "stderr_snippet": stderr_clean[-500:],
        }

    # Attach diagnostics to the payload
    payload["diagnostics"] = diag_lines[:20]
    payload["rc"] = rc
    return payload


def _diag_signature(d: dict) -> str:
    """Compress an oracle's diagnostic stream into a short stable signature.

    Two fixtures with the same diagnostic-line count and the same first
    diagnostic produce the same signature. Used to distinguish
    silent-empty fixtures by *why* they came out empty: a fixture where
    OCC emits "Line 47: pcurve undefined" before yielding empty differs
    from one where OCC emits nothing at all.

    Format: ``"none"`` if no diagnostics, else ``"<N>:<first40chars>"``.
    """
    diags = d.get("diagnostics") or []
    if not diags:
        return "none"
    first = diags[0]
    # Take a stable digest of the first line
    cleaned = re.sub(r"\s+", " ", first).strip()
    if len(cleaned) > 60:
        cleaned = cleaned[:57] + "..."
    return f"{len(diags)}:{cleaned}"


def derive_summary(per_oracle: dict) -> dict:
    s = {}
    for oracle in ["occt_heal_on", "occt_heal_off"]:
        d = per_oracle.get(oracle, {})
        st = d.get("status", "unknown")
        if st == "reject_at_read":
            s[oracle] = "reject"
        elif st == "accept_silent":
            s[oracle] = "empty"
        elif st == "accept":
            s[oracle] = f"shape({d.get('n_roots', 0)})"
        elif st in ("exception",):
            s[oracle] = "except"
        elif st == "process_signal":
            s[oracle] = f"signal({d.get('signal')})"
        elif st == "timeout":
            s[oracle] = "timeout"
        else:
            s[oracle] = st

    for oracle in ["gmsh_autofix_on", "gmsh_autofix_off"]:
        d = per_oracle.get(oracle, {})
        st = d.get("status", "unknown")
        if st == "accept":
            n = d.get("total_entities", 0)
            s[oracle] = f"shape({n})"
        elif st == "accept_silent":
            s[oracle] = "empty"
        elif st == "reject":
            s[oracle] = "reject"
        elif st == "process_signal":
            s[oracle] = f"signal({d.get('signal')})"
        elif st == "timeout":
            s[oracle] = "timeout"
        else:
            s[oracle] = st

    d = per_oracle.get("ifcopenshell", {})
    st = d.get("status", "unknown")
    if st == "reject":
        s["ifcopenshell"] = "reject"
    elif st == "schema_class_reject":
        s["ifcopenshell"] = "schema_n/a"
    elif st == "accept":
        s["ifcopenshell"] = f"accept({d.get('n_entities', 0)})"
    else:
        s["ifcopenshell"] = st

    # part21_strict: pure-Python ISO 10303-21 validator independent of OCCT.
    # Spec string: "accept" / "warn" / "reject(<first_error_code>)"
    d = per_oracle.get("part21_strict", {})
    st = d.get("status", "unknown")
    if st == "accept":
        s["part21_strict"] = "accept"
    elif st == "accept_with_warnings":
        s["part21_strict"] = f"warn({d.get('first_warning') or '?'})"
    elif st == "reject":
        s["part21_strict"] = f"reject({d.get('first_error') or '?'})"
    else:
        s["part21_strict"] = st

    # Auxiliary: per-oracle diagnostic signatures. Keep the legacy
    # `occt=*` and `gmsh=*` strings stable (DRIFT detector relies on
    # them) but expose the diagnostic profile separately. Two
    # silent-empty fixtures with different `occt_diag_off` signatures
    # are now distinguishable.
    s["occt_diag_on"]  = _diag_signature(per_oracle.get("occt_heal_on",  {}))
    s["occt_diag_off"] = _diag_signature(per_oracle.get("occt_heal_off", {}))
    s["gmsh_diag"]     = _diag_signature(per_oracle.get("gmsh_autofix_off", {}))

    # Manifold auxiliary oracle. Format: short status string. Volume /
    # genus are exposed in the per-oracle raw record but not flattened
    # into the summary spec to keep the legacy DRIFT line stable.
    d = per_oracle.get("manifold", {})
    s["manifold"] = d.get("status", "unknown")

    # OCAF / XCAF document-layer oracle. The most-load-bearing single
    # value here is the root-label count: zero means the OCAF reader
    # produced no top-level shape (a §12.6-style assembly defect),
    # nonzero means the product graph survived. ``failed`` means the
    # CAF reader could not parse the file at all.
    d = per_oracle.get("ocaf", {})
    st = d.get("status", "unknown")
    if st == "accept":
        s["ocaf"] = f"root_labels={d.get('root_labels', 0)}"
    elif st == "reject":
        s["ocaf"] = "failed"
    elif st == "process_signal":
        s["ocaf"] = f"signal({d.get('signal')})"
    elif st == "timeout":
        s["ocaf"] = "timeout"
    else:
        s["ocaf"] = st

    # Solvespace cross-kernel oracle. Compact summary form:
    # "loaded(n_solids=N)" / "rejected" / "not_installed" / "timeout".
    d = per_oracle.get("solvespace", {})
    st = d.get("status", "unknown")
    if st == "loaded":
        s["solvespace"] = f"loaded(n_solids={d.get('n_solids', 0)})"
    elif st == "not_installed":
        s["solvespace"] = "not_installed"
    else:
        s["solvespace"] = st

    # BRL-CAD cross-kernel oracle. Compact summary form:
    # "loaded(n_regions=N)" / "rejected" / "not_installed" / "timeout".
    d = per_oracle.get("brlcad", {})
    st = d.get("status", "unknown")
    if st == "loaded":
        s["brlcad"] = f"loaded(n_regions={d.get('n_regions', 0)})"
    elif st == "not_installed":
        s["brlcad"] = "not_installed"
    else:
        s["brlcad"] = st

    # Structural linter (non-kernel): the most-salient STEP structural defect
    # code, or "ok". Kept OUT of the legacy occt/gmsh/ifc spec triple so the
    # DRIFT line stays byte-stable for every existing fixture; consumed via the
    # separate `structural` summary key + per-entry Structural assertions.
    d = per_oracle.get("structural", {})
    st = d.get("status", "unknown")
    if st == "ok_scan":
        s["structural"] = d.get("code", "ok")
    else:
        s["structural"] = st

    return s


def validate(path: Path) -> dict:
    per = {}
    for oracle in ORACLES:
        per[oracle] = run_oracle(oracle, str(path))
    return {
        "file": str(path),
        "summary": derive_summary(per),
        "byte_signature": byte_signature(path),
        "entity_summary": entity_summary(path),
        **per,
    }


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if not argv or argv[0] in ("-h", "--help"):
        print("usage: validate2.py <file.stp> [--json]", file=sys.stderr)
        return 2
    path = Path(argv[0])
    as_json = "--json" in argv[1:]
    result = validate(path)
    if as_json:
        json.dump(result, sys.stdout, indent=2, default=str)
        sys.stdout.write("\n")
    else:
        from rich.console import Console
        from rich.pretty import Pretty
        Console().print(Pretty(result, expand_all=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
