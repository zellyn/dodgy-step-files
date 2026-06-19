"""Solvespace oracle: cross-kernel STEP validation via subprocess.

Solvespace has its own STEP import/export (not OCCT-backed), making it a
useful diversifier for cross-kernel disagreement detection. Per
`CROSS_KERNEL_SURVEY.md`, this is the first non-OCCT kernel we add to
the matrix.

Usage:
    uv run python -m step_corpus._solvespace_oracle <fixture.stp> [--json]
    uv run python -m step_corpus._solvespace_oracle --check-install

If the `solvespace` binary isn't in PATH, the oracle reports
`{status: "not_installed", ...}` rather than failing — fixtures get a
honest "we don't know" rather than a fake verdict.

CI setup (Ubuntu 22.04):
    sudo apt-get install -y solvespace

Output JSON record (matches the cross-kernel schema in
`CROSS_KERNEL_SURVEY.md`):
    {
      "kernel": "solvespace",
      "status": "loaded" | "rejected" | "error" | "timeout" | "not_installed",
      "n_solids": int | null,
      "stderr_tail": str,
      "duration_ms": float
    }
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path


SOLVESPACE_BIN = shutil.which("solvespace") or shutil.which("solvespace-cli")
DEFAULT_TIMEOUT_S = 60


def check_install() -> dict:
    """Probe whether solvespace is installed and discoverable."""
    if SOLVESPACE_BIN is None:
        return {
            "installed": False,
            "binary": None,
            "version": None,
            "reason": "solvespace not in PATH; try `apt-get install solvespace` or `brew install solvespace`",
        }
    try:
        result = subprocess.run(
            [SOLVESPACE_BIN, "--version"],
            capture_output=True, text=True, timeout=5,
        )
        version = (result.stdout or result.stderr).strip().splitlines()[0]
    except subprocess.TimeoutExpired:
        version = "unknown (--version timed out)"
    except Exception as e:
        version = f"unknown ({e})"
    return {
        "installed": True,
        "binary": SOLVESPACE_BIN,
        "version": version,
    }


def run_solvespace(fixture: Path, timeout_s: float = DEFAULT_TIMEOUT_S) -> dict:
    """Run solvespace on a fixture and classify the outcome.

    The exact subprocess invocation depends on the solvespace CLI form
    available on the runner. We try the most common variants in order
    and report the first that responds. Capture exit code + stderr; map
    to a small set of status values for the cross-kernel matrix.
    """
    if SOLVESPACE_BIN is None:
        return {
            "kernel": "solvespace",
            "status": "not_installed",
            "n_solids": None,
            "stderr_tail": "",
            "duration_ms": 0.0,
        }

    # Try `solvespace --convert <input> <output>` first; if that flag
    # doesn't exist, try a load-and-export pattern. The probe pattern is
    # forward-compatible: each new solvespace release tends to expand the
    # CLI surface, not break old flags.
    out_path = fixture.with_suffix(".solvespace-probe.stl")
    candidates = [
        [SOLVESPACE_BIN, "--convert", str(fixture), str(out_path)],
        [SOLVESPACE_BIN, "convert", str(fixture), str(out_path)],
    ]
    last_err = ""
    for cmd in candidates:
        try:
            t0 = time.perf_counter()
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout_s,
            )
            duration_ms = (time.perf_counter() - t0) * 1000.0
        except subprocess.TimeoutExpired:
            return {
                "kernel": "solvespace",
                "status": "timeout",
                "n_solids": None,
                "stderr_tail": "timed out",
                "duration_ms": timeout_s * 1000.0,
            }
        except Exception as e:
            last_err = f"subprocess failed: {e}"
            continue

        # Treat "unknown flag"-style errors as "try next variant".
        stderr = (result.stderr or "").strip()
        if result.returncode != 0 and any(
            s in stderr.lower()
            for s in ("unknown option", "unrecognized option", "usage:", "invalid argument")
        ):
            last_err = stderr
            continue

        if result.returncode == 0 and out_path.exists():
            # Solvespace accepted and converted. Try to count solids via
            # the STL output (rough approximation: each "solid" block in
            # ASCII STL, or assume 1 for binary STL).
            try:
                stl_text = out_path.read_text(errors="replace")
                n_solids = stl_text.lower().count("solid ")
                if n_solids == 0:
                    n_solids = 1  # binary STL
            except Exception:
                n_solids = None
            finally:
                try: out_path.unlink()
                except Exception: pass
            return {
                "kernel": "solvespace",
                "status": "loaded",
                "n_solids": n_solids,
                "stderr_tail": stderr[-200:],
                "duration_ms": duration_ms,
            }

        # Non-zero exit but not a CLI-shape error → solvespace rejected.
        return {
            "kernel": "solvespace",
            "status": "rejected",
            "n_solids": None,
            "stderr_tail": stderr[-200:],
            "duration_ms": duration_ms,
        }

    return {
        "kernel": "solvespace",
        "status": "error",
        "n_solids": None,
        "stderr_tail": last_err[-200:],
        "duration_ms": 0.0,
    }


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

    result = run_solvespace(fixture, timeout_s=args.timeout)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"{result['kernel']}: {result['status']} "
              f"(n_solids={result['n_solids']}, {result['duration_ms']:.1f} ms)")
        if result["stderr_tail"]:
            print(f"  stderr: {result['stderr_tail']}")
    return 0 if result["status"] in ("loaded", "rejected", "not_installed") else 1


if __name__ == "__main__":
    sys.exit(main())
