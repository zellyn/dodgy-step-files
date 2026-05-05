"""Parallel runner for validate2 across the full corpus."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import subprocess
import sys
import time
from pathlib import Path


def run_one(args):
    stp_path, out_path, tier3_path = args
    if out_path.exists() and out_path.stat().st_size > 0:
        if tier3_path.exists() and tier3_path.stat().st_size > 0:
            return (stp_path.name, "skip", 0)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tier3_path.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    try:
        # Tier 1+2: subprocess-isolated validate2.
        proc = subprocess.run(
            [
                sys.executable, "-m", "step_corpus.validate2",
                str(stp_path), "--json",
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        out_path.write_text(proc.stdout)
        # Tier 3: geometric introspection (face areas, edge lengths, knot arithmetic).
        # Run separately because tier3 doesn't use subprocess isolation; if a
        # fixture would crash OCCT, validate2's signal(11) tells us, and tier3
        # may also crash but won't kill us via subprocess wrapping.
        try:
            tier3_proc = subprocess.run(
                [
                    sys.executable, "-m", "step_corpus.tier3_geometric",
                    str(stp_path), "--json",
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if tier3_proc.returncode == 0 and tier3_proc.stdout:
                tier3_path.write_text(tier3_proc.stdout)
            else:
                # Record the crash/failure status; useful as a defect signal too.
                tier3_path.write_text(f'{{"status": "tier3_failed", "rc": {tier3_proc.returncode}}}')
        except subprocess.TimeoutExpired:
            tier3_path.write_text('{"status": "tier3_timeout"}')
        except Exception as e:
            tier3_path.write_text(f'{{"status": "tier3_error", "error": {json.dumps(str(e)[:200])}}}')
        dt = time.time() - t0
        return (stp_path.name, "ok" if proc.returncode == 0 else f"rc={proc.returncode}", round(dt, 2))
    except Exception as e:
        return (stp_path.name, f"error: {e}", round(time.time() - t0, 2))


def main():
    # This file lives at: <repo-root>/validation/src/step_corpus/_run_corpus.py
    # So the repo root is parents[3].
    repo_root = Path(__file__).resolve().parents[3]
    default_examples = str(repo_root / "step-examples")

    ap = argparse.ArgumentParser()
    ap.add_argument("--examples", default=default_examples)
    ap.add_argument("--out", default="/tmp/cad-v2-out")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--filter", default="")
    args = ap.parse_args()

    examples = Path(args.examples)
    out_base = Path(args.out)
    out_base.mkdir(parents=True, exist_ok=True)

    tier3_base = out_base.parent / (out_base.name + "-tier3")
    tier3_base.mkdir(parents=True, exist_ok=True)

    pairs = []
    for stp in sorted(examples.rglob("*.stp")):
        rel = stp.relative_to(examples)
        if args.filter and args.filter not in str(rel):
            continue
        out_path = out_base / rel.parent / f"{stp.stem}.json"
        tier3_path = tier3_base / rel.parent / f"{stp.stem}.json"
        pairs.append((stp, out_path, tier3_path))

    print(f"Discovered {len(pairs)} fixtures, running with {args.workers} workers")
    t0 = time.time()
    done = 0
    skipped = 0
    failed = 0
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as ex:
        for fname, status, dt in ex.map(run_one, pairs):
            if status == "skip":
                skipped += 1
            elif status == "ok":
                done += 1
            else:
                failed += 1
                print(f"  ! {fname}: {status} ({dt}s)")
            if (done + skipped + failed) % 50 == 0:
                rate = (done + failed) / max(time.time() - t0, 1)
                print(f"  progress: {done+skipped+failed}/{len(pairs)} ({rate:.1f}/s)")
    print(f"done: {done} ok, {skipped} skipped, {failed} failed, {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
