"""
Run the Prog-QAOA factorization simulation sweep.

For every combination of biprime ``m``, number of QAOA layers ``p``,
multiplier, and search-space variant (uniform vs reduced), the QAOA angles are
optimised to maximise the success probability (total probability on the
non-trivial true-factor states), and the resulting success probability plus
resource metrics (qubits, depth, CNOT count) are recorded.

Examples:
    # quick run: two small biprimes, mcx multiplier, layers 1-3, both variants
    python scripts/run_qaoa_simulation.py -m 15 21 --multipliers mcx -p 1 2 3

    # full sweep
    python scripts/run_qaoa_simulation.py -m 15 21 35 77 \
        --multipliers mcx hrs rgqft -p 1 2 3 4 5 --variants uniform reduced

    # resume an interrupted run (skips rows already in the CSV)
    python scripts/run_qaoa_simulation.py -m 15 21 35 77 --resume
"""

import argparse
import csv
import os
import statistics
import sys
import time

import numpy as np
from scipy.optimize import minimize

# allow running from the repo root or the scripts/ directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import SearchSpaceReducer
from src.qaoa.problem import make_problem
from src.qaoa.certificate import MULTIPLIERS
from src.qaoa.uniform_ansatz import build_ansatz
from src.qaoa.metrics import SuccessEvaluator, resource_metrics, search_space_size
from src.qaoa.reduced_ansatz import build_reduced_ansatz, build_reduced_initial_state


FIELDNAMES = [
    "m", "n_m", "multiplier", "variant", "reps",
    "seed", "success_prob",
    "n_qubits", "n_search_qubits",
    "search_space_size", "reduction_ratio",
    "depth", "cnot_count", "u3_count",
    "n_seeds", "opt_seconds",
]


def build_for_variant(problem, vqf, reps, multiplier, variant):
    """Return the ansatz for the given variant ('uniform' or 'reduced')."""
    if variant == "uniform":
        return build_ansatz(problem, reps, multiplier=multiplier)
    if variant == "reduced":
        return build_reduced_ansatz(problem, vqf, reps, multiplier=multiplier)
    raise ValueError(f"unknown variant {variant!r}")


def optimize_success(problem, ansatz, reps, seeds, maxiter, progress_prefix=""):
    """Optimise the QAOA angles to maximise success probability.

    Runs ``seeds`` independent COBYLA restarts (each from a different random
    initial angle) and returns the **per-seed** best success probabilities, so
    downstream plots can show the seed-to-seed spread (mean +/- std).

    Uses a :class:`SuccessEvaluator`, which decomposes the ansatz to gate level
    once and then only rebinds angles per evaluation, avoiding the
    per-evaluation re-decomposition that otherwise dominates the cost.

    Returns ``(per_seed_success_list, seconds)``.
    """
    evaluator = SuccessEvaluator(problem, ansatz)
    t0 = time.time()
    per_seed = []

    for s in range(seeds):
        seed_state = {"best": None, "evals": 0}

        def neg(x):
            val = -evaluator.evaluate(x)
            seed_state["evals"] += 1
            if seed_state["best"] is None or val < seed_state["best"] - 1e-4:
                seed_state["best"] = val
                print(f"{progress_prefix}    seed {s + 1}: success={-val:.4f} "
                      f"(eval {seed_state['evals']}, {time.time() - t0:.0f}s)", flush=True)
            elif val < seed_state["best"]:
                seed_state["best"] = val
            return val

        rng = np.random.default_rng(s)
        x0 = rng.uniform(0, np.pi, size=2 * reps)
        minimize(neg, x0, method="COBYLA", options={"maxiter": maxiter})
        seed_best = -seed_state["best"]
        per_seed.append(seed_best)
        print(f"{progress_prefix}  seed {s + 1}/{seeds} done: "
              f"success={seed_best:.4f} ({time.time() - t0:.0f}s)", flush=True)

    return per_seed, time.time() - t0


def load_done_rows(path):
    """Return the set of (m, multiplier, variant, reps) already in the CSV."""
    done = set()
    if not os.path.exists(path):
        return done
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            done.add((int(row["m"]), row["multiplier"], row["variant"], int(row["reps"])))
    return done


def main():
    ap = argparse.ArgumentParser(
        description="Prog-QAOA factorization simulation sweep.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    ap.add_argument("-m", "--biprimes", type=int, nargs="+", default=[15, 21, 35, 77],
                    help="biprimes m to factor")
    ap.add_argument("--multipliers", nargs="+", default=["mcx"],
                    choices=list(MULTIPLIERS),
                    help="multiplier implementations for the MUL block")
    ap.add_argument("-p", "--reps", type=int, nargs="+", default=[1, 2, 3],
                    help="QAOA layer counts to sweep")
    ap.add_argument("--variants", nargs="+", default=["uniform", "reduced"],
                    choices=["uniform", "reduced"],
                    help="search-space variants")
    ap.add_argument("--seeds", type=int, default=4,
                    help="random restarts for the angle optimisation")
    ap.add_argument("--maxiter", type=int, default=120,
                    help="max COBYLA iterations per restart")
    ap.add_argument("--outdir", default="results",
                    help="base directory; each run writes to a timestamped subfolder")
    ap.add_argument("--run-name", default=None,
                    help="fixed folder name under --outdir (e.g. 'qaoa_sweep_full') "
                         "so several runs share one folder; appends and skips finished "
                         "rows automatically. Mutually exclusive with --resume.")
    ap.add_argument("--resume", metavar="RUN_DIR", default=None,
                    help="resume into an existing run folder, skipping finished rows "
                         "(instead of creating a new timestamped folder)")
    args = ap.parse_args()

    # Determine the run folder. Priority: --resume > --run-name > new timestamp.
    appending = False
    if args.resume:
        run_dir = args.resume
        if not os.path.isdir(run_dir):
            ap.error(f"--resume folder does not exist: {run_dir}")
        appending = True
    elif args.run_name:
        run_dir = os.path.join(args.outdir, args.run_name)
        appending = os.path.isdir(run_dir)  # append if it already exists
        os.makedirs(run_dir, exist_ok=True)
    else:
        from datetime import datetime
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        run_dir = os.path.join(args.outdir, f"qaoa_sweep_{stamp}")
        os.makedirs(run_dir, exist_ok=True)

    csv_path = os.path.join(run_dir, "qaoa_sweep.csv")
    done = load_done_rows(csv_path) if appending else set()

    # record the run configuration for traceability; append successive invocations
    # (e.g. one per multiplier sharing a --run-name folder) rather than clobbering.
    import json
    meta_path = os.path.join(run_dir, "run_metadata.json")
    history = []
    if os.path.exists(meta_path):
        try:
            prev = json.load(open(meta_path))
            history = prev if isinstance(prev, list) else [prev]
        except Exception:
            history = []
    history.append(vars(args))
    with open(meta_path, "w") as mf:
        json.dump(history, mf, indent=2)

    # open in append mode; write header only if the file is new/empty
    new_file = not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0
    f = open(csv_path, "a", newline="")
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
    if new_file:
        writer.writeheader()
        f.flush()
    print(f"Writing results to {run_dir}/", flush=True)

    # cache one SearchSpaceReducer per m (only needed for the reduced variant)
    vqf_cache = {}

    total = len(args.biprimes) * len(args.multipliers) * len(args.reps) * len(args.variants)
    count = 0
    for m in args.biprimes:
        problem = make_problem(m)
        uniform_size = problem.n_search_qubits  # log2(2**n_search)
        for variant in args.variants:
            vqf = None
            if variant == "reduced":
                vqf = vqf_cache.get(m)
                if vqf is None:
                    vqf = vqf_cache[m] = SearchSpaceReducer(m)

            # paper-defined search-space size (log2 of the support) and the
            # reduction ratio (reduced size / uniform size); depends only on
            # (m, variant), so compute it once here.
            if variant == "reduced":
                ss_size = search_space_size(build_reduced_initial_state(problem, vqf))
            else:
                ss_size = float(uniform_size)
            reduction_ratio = round(ss_size / uniform_size, 4) if uniform_size else 1.0

            for multiplier in args.multipliers:
                for reps in args.reps:
                    count += 1
                    key = (m, multiplier, variant, reps)
                    if key in done:
                        print(f"[{count}/{total}] skip (done) m={m} {multiplier} "
                              f"{variant} p={reps}", flush=True)
                        continue
                    try:
                        tag = f"[{count}/{total}] m={m} {multiplier} {variant} p={reps}"
                        print(f"{tag}  optimizing ({args.seeds} seeds)...", flush=True)
                        ansatz = build_for_variant(problem, vqf, reps, multiplier, variant)
                        per_seed, secs = optimize_success(
                            problem, ansatz, reps, args.seeds, args.maxiter,
                            progress_prefix=tag)
                        rm = resource_metrics(problem, ansatz)
                        # one row per seed; resource metrics are identical across
                        # seeds (same circuit), so they are repeated on each row.
                        for seed_idx, seed_succ in enumerate(per_seed):
                            writer.writerow({
                                "m": m, "n_m": m.bit_length(),
                                "multiplier": multiplier, "variant": variant, "reps": reps,
                                "seed": seed_idx, "success_prob": round(seed_succ, 6),
                                "n_qubits": rm["n_qubits"],
                                "n_search_qubits": rm["n_search_qubits"],
                                "search_space_size": round(ss_size, 4),
                                "reduction_ratio": reduction_ratio,
                                "depth": rm["depth"], "cnot_count": rm["cnot_count"],
                                "u3_count": rm["u3_count"],
                                "n_seeds": args.seeds, "opt_seconds": round(secs, 1),
                            })
                        f.flush()
                        mean = statistics.mean(per_seed)
                        std = statistics.pstdev(per_seed) if len(per_seed) > 1 else 0.0
                        print(f"[{count}/{total}] m={m} {multiplier} {variant} p={reps}"
                              f"  success={mean:.4f}+/-{std:.4f} (best={max(per_seed):.4f})"
                              f"  qubits={rm['n_qubits']} depth={rm['depth']}"
                              f"  cx={rm['cnot_count']} u3={rm['u3_count']}"
                              f"  ({secs:.0f}s)", flush=True)
                    except Exception as e:
                        print(f"[{count}/{total}] ERROR m={m} {multiplier} {variant} "
                              f"p={reps}: {type(e).__name__}: {e}", flush=True)

    f.close()
    print(f"\nDone. Results in {run_dir}/", flush=True)


if __name__ == "__main__":
    main()
