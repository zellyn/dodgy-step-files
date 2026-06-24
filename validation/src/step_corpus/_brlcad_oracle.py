"""BRL-CAD oracle: cross-kernel STEP validation via the `step-g` converter.

BRL-CAD reads STEP through STEPcode (NIST PDES Inc. parser), which is
entirely independent of OpenCASCADE. This is the most independent free
STEP reader available and the highest-value cross-kernel diversifier
for the validation matrix (per the 2026-06-24 B3 survey).

Usage:
    uv run python -m step_corpus._brlcad_oracle <fixture.stp> [--json]
    uv run python -m step_corpus._brlcad_oracle --check-install

If the `step-g` binary isn't in PATH, the oracle reports
`{status: "not_installed", ...}` rather than failing — fixtures get an
honest "we don't know" rather than a fake verdict.

Install (macOS):
    Download BRL-CAD from https://brlcad.org/d/download (.dmg) and
    symlink: `ln -sf /Applications/BRL-CAD.app/Contents/MacOS/step-g /usr/local/bin/step-g`

Install (Ubuntu 22.04 CI):
    curl -L https://github.com/BRL-CAD/brlcad/releases/download/rel-7-38-0/BRL-CAD_7.38.0_Linux_x86_64.tar.bz2 | tar -xj
    sudo cp BRL-CAD*/bin/step-g /usr/local/bin/

Output JSON record (matches the cross-kernel schema):
    {
      "kernel": "brlcad",
      "status": "loaded" | "rejected" | "error" | "timeout" | "not_installed",
      "n_regions": int | null,
      "stderr_tail": str,
      "duration_ms": float
    }
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


BRLCAD_BIN = shutil.which("step-g")
DEFAULT_TIMEOUT_S = 60

# step-g prints summary lines like:
#   "Regions:           42"
#   "Created N regions"
# at end of conversion. The regex below tolerates either pattern.
_REGION_COUNT_RE = re.compile(
    r"(?:regions?\s*[:=]\s*|created\s+)(\d+)\s+regions?",
    re.IGNORECASE,
)


def check_install() -> dict:
    """Probe whether step-g is installed and discoverable."""
    if BRLCAD_BIN is None:
        return {
            "installed": False,
            "binary": None,
            "version": None,
            "reason": (
                "step-g not in PATH; install BRL-CAD from brlcad.org and "
                "symlink step-g into /usr/local/bin"
            ),
        }
    try:
        result = subprocess.run(
            [BRLCAD_BIN, "-h"],
            capture_output=True, text=True, timeout=5,
        )
        # step-g -h prints usage; the BRL-CAD version is usually in the
        # banner of step-g --version, but the converter may not support
        # --version. Probe both and take whatever succeeds.
        version = ((result.stdout or "") + (result.stderr or "")).strip().splitlines()
        version_line = next(
            (line for line in version if "BRL-CAD" in line or "version" in line.lower()),
            version[0] if version else "unknown",
        )
    except subprocess.TimeoutExpired:
        version_line = "unknown (-h timed out)"
    except Exception as e:
        version_line = f"unknown ({e})"
    return {
        "installed": True,
        "binary": BRLCAD_BIN,
        "version": version_line,
    }


def _classify_outcome(returncode: int, stderr: str, out_path: Path) -> str:
    """Map step-g exit + stderr + output-file presence to a status string."""
    stderr_lower = stderr.lower()
    if returncode == 0 and out_path.exists() and out_path.stat().st_size > 0:
        return "loaded"
    if "syntax" in stderr_lower or "parse error" in stderr_lower or "unable to read" in stderr_lower:
        return "rejected"
    if "schema" in stderr_lower and "fail" in stderr_lower:
        return "rejected"
    # Default to rejected for non-zero exit; "error" reserved for
    # subprocess-level failures (which are caught at the call site).
    return "rejected"


def _count_regions(stderr: str) -> int | None:
    """Extract the BRL-CAD region count from step-g's summary output."""
    match = _REGION_COUNT_RE.search(stderr)
    if not match:
        return None
    try:
        return int(match.group(1))
    except (ValueError, IndexError):
        return None


def run_brlcad(fixture: Path, timeout_s: float = DEFAULT_TIMEOUT_S) -> dict:
    """Run step-g on a fixture and classify the outcome."""
    if BRLCAD_BIN is None:
        return {
            "kernel": "brlcad",
            "status": "not_installed",
            "n_regions": None,
            "stderr_tail": "",
            "duration_ms": 0.0,
        }

    # step-g writes a .g geometry database file. Use a tempfile per call
    # so concurrent runs don't clobber each other.
    with tempfile.NamedTemporaryFile(suffix=".g", delete=False) as tmp:
        out_path = Path(tmp.name)
    try:
        try:
            t0 = time.perf_counter()
            result = subprocess.run(
                [BRLCAD_BIN, str(fixture), str(out_path)],
                capture_output=True, text=True, timeout=timeout_s,
            )
            duration_ms = (time.perf_counter() - t0) * 1000.0
        except subprocess.TimeoutExpired:
            return {
                "kernel": "brlcad",
                "status": "timeout",
                "n_regions": None,
                "stderr_tail": "timed out",
                "duration_ms": timeout_s * 1000.0,
            }
        except Exception as e:
            return {
                "kernel": "brlcad",
                "status": "error",
                "n_regions": None,
                "stderr_tail": f"subprocess failed: {e}"[-200:],
                "duration_ms": 0.0,
            }

        stderr = (result.stderr or "").strip()
        # step-g prints summary on stdout sometimes, stderr others — concat.
        combined = ((result.stdout or "") + "\n" + stderr).strip()
        status = _classify_outcome(result.returncode, combined, out_path)
        n_regions = _count_regions(combined) if status == "loaded" else None
        return {
            "kernel": "brlcad",
            "status": status,
            "n_regions": n_regions,
            "stderr_tail": combined[-200:],
            "duration_ms": duration_ms,
        }
    finally:
        try: out_path.unlink()
        except Exception: pass


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("fixture", nargs="?")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--check-install", action="store_true")
    ap.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_S)
    args = ap.parse_args()

    if args.check_install:
        info = check_install()
        print(json.dumps(info, indent=2) if args.json else info)
        return 0 if info["installed"] else 1

    if not args.fixture:
        ap.error("fixture path required (or use --check-install)")

    fixture = Path(args.fixture)
    if not fixture.is_file():
        print(f"fixture not found: {fixture}", file=sys.stderr)
        return 2

    result = run_brlcad(fixture, timeout_s=args.timeout)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"{result['kernel']}: {result['status']} "
              f"(n_regions={result['n_regions']}, {result['duration_ms']:.1f} ms)")
        if result["stderr_tail"]:
            print(f"  stderr: {result['stderr_tail']}")
    return 0 if result["status"] in ("loaded", "rejected", "not_installed") else 1


if __name__ == "__main__":
    sys.exit(main())
