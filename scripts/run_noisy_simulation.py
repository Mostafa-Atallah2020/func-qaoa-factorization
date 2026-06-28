"""Sweep the impact of noise on the Prog-QAOA factorization success probability.

For one biprime (default m = 15, the cheapest of the reported sizes), this
recovers the ideal-optimal QAOA angles with the exact statevector optimizer,
then re-evaluates those fixed angles under a depolarizing + readout noise model
across a sweep of error rates, using shot-based sampling. The result shows how
success degrades as the error rate rises.

Examples:
    # quick run
    python scripts/run_noisy_simulation.py -m 15 --variants uniform -p 1 \
        --error-rates 1e-3 1e-1 --seeds 2 --shots 512 --run-name noisy_quick

    # full noise sweep (both variants, p = 1..5)
    python scripts/run_noisy_simulation.py -m 15 --multiplier hrs \
        --variants uniform reduced -p 1 2 3 4 5 \
        --error-rates 1e-4 1e-2 1e-1 --seeds 5 --shots 256 \
        --run-name noisy_m15

    # resume an interrupted run
    python scripts/run_noisy_simulation.py --resume results/qaoa_noisy_<stamp>
"""

import argparse
import csv
import json
import os
import sys
import time

import numpy as np

# allow running from the repo root or the scripts/ directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import SearchSpaceReducer
from src.qaoa.problem import make_problem
from src.qaoa.certificate import MULTIPLIERS
from src.qaoa.uniform_ansatz import build_ansatz
from src.qaoa.metrics import SuccessEvaluator, success_probability_noisy
from src.qaoa.reduced_ansatz import build_reduced_ansatz
from src.qaoa.noise import build_noise_model


FIELDNAMES = [
    "m", "n_m", "variant", "reps", "n_qubits",
    "multiplier", "shots", "error_rate",
    "seed", "success_noisy", "success_ideal", "seconds", "angles",
]


def build_for_variant(problem, vqf, reps, multiplier, variant):
    """Return the ansatz for the given variant ('uniform' or 'reduced')."""
    if variant == "uniform":
        return build_ansatz(problem, reps, multiplier=multiplier)
    if variant == "reduced":
        return build_reduced_ansatz(problem, vqf, reps, multiplier=multiplier)
    raise ValueError(f"unknown variant {variant!r}")


def optimize_one_seed(evaluator, reps, seed, maxiter):
    """Optimize the QAOA angles from one random seed (statevector objective).

    Args:
        evaluator: a SuccessEvaluator for the ansatz.
        reps: number of QAOA layers (sets the angle count).
        seed: random seed for the COBYLA initial angles.
        maxiter: max COBYLA iterations.

    Returns:
        A ``(angles, ideal_success)`` tuple: the optimized angle vector and its
        exact (noise-free) success probability.
    """
    from scipy.optimize import minimize

    rng = np.random.default_rng(seed)
    x0 = rng.uniform(0, np.pi, size=2 * reps)
    res = minimize(lambda x: -evaluator.evaluate(x), x0,
                   method="COBYLA", options={"maxiter": maxiter})
    return res.x, float(evaluator.evaluate(res.x))


def load_done_rows(path):
    """Return the set of (variant, reps, error_rate, seed) already in the CSV."""
    done = set()
    if not os.path.exists(path):
        return done
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            done.add((row["variant"], int(row["reps"]),
                      float(row["error_rate"]), int(row["seed"])))
    return done


def main():
    ap = argparse.ArgumentParser(
        description="Prog-QAOA noisy-simulation noise-level sweep.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    ap.add_argument("-m", "--biprime", type=int, default=15,
                    help="biprime m to factor (single value)")
    ap.add_argument("--multiplier", default="hrs", choices=list(MULTIPLIERS),
                    help="multiplier implementation for the MUL block")
    ap.add_argument("--variants", nargs="+", default=["uniform", "reduced"],
                    choices=["uniform", "reduced"], help="search-space variants")
    ap.add_argument("-p", "--reps", type=int, nargs="+", default=[1, 2, 3, 4, 5],
                    help="QAOA layer counts")
    ap.add_argument("--error-rates", type=float, nargs="+",
                    default=[1e-4, 1e-2, 1e-1],
                    help="two-qubit error probabilities to sweep (the noise-free "
                         "value is recorded separately as success_ideal)")
    ap.add_argument("--seeds", type=int, default=5,
                    help="optimizer-seed restarts; each seed optimizes its own "
                         "angles and is evaluated noise-free and at every error "
                         "rate (gives the error bars)")
    ap.add_argument("--shots", type=int, default=8192, help="measurement shots")
    ap.add_argument("--maxiter", type=int, default=150,
                    help="max COBYLA iterations per restart")
    ap.add_argument("--outdir", default="results",
                    help="base directory; each run writes to a subfolder")
    ap.add_argument("--run-name", default=None,
                    help="fixed folder name under --outdir; appends and skips "
                         "finished rows. Mutually exclusive with --resume.")
    ap.add_argument("--resume", metavar="RUN_DIR", default=None,
                    help="resume into an existing run folder, skipping finished rows")
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
        appending = os.path.isdir(run_dir)
        os.makedirs(run_dir, exist_ok=True)
    else:
        from datetime import datetime
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        run_dir = os.path.join(args.outdir, f"qaoa_noisy_{stamp}")
        os.makedirs(run_dir, exist_ok=True)

    csv_path = os.path.join(run_dir, "qaoa_noisy.csv")
    done = load_done_rows(csv_path) if appending else set()

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

    new_file = not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0
    f = open(csv_path, "a", newline="")
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
    if new_file:
        writer.writeheader()
        f.flush()
    print(f"Writing results to {run_dir}/", flush=True)

    m = args.biprime
    problem = make_problem(m)
    vqf = None

    # Loop p in the OUTER position so each layer count finishes across all
    # configurations before the next p starts (p=1 for every variant, then p=2,
    # ...), giving complete low-p data and a usable plot early.
    for reps in args.reps:
        for variant in args.variants:
            if variant == "reduced" and vqf is None:
                vqf = SearchSpaceReducer(m)

            tag = f"[m={m} {variant} p={reps}]"
            ansatz = build_for_variant(problem, vqf, reps, args.multiplier, variant)
            evaluator = SuccessEvaluator(problem, ansatz)
            param_order = sorted(ansatz.parameters, key=lambda pp: pp.name)
            n_qubits = ansatz.num_qubits

            # Each seed is an independent optimizer restart: it optimizes its OWN
            # angles, then those angles are evaluated noise-free (exact) and at
            # every error rate. Variance across seeds gives error bars on every
            # curve, including the noise-free baseline.
            for seed in range(args.seeds):
                # error_rate < 0 marks the noise-free baseline row for this seed.
                pending = [er for er in args.error_rates
                           if (variant, reps, float(er), seed) not in done]
                need_baseline = (variant, reps, -1.0, seed) not in done
                if not pending and not need_baseline:
                    continue

                print(f"{tag} seed={seed}: optimizing angles...", flush=True)
                _t_opt = time.time()
                angles, ideal = optimize_one_seed(
                    evaluator, reps, seed, args.maxiter)
                opt_secs = time.time() - _t_opt
                bound = ansatz.assign_parameters(dict(zip(param_order, angles)))
                angles_json = json.dumps([round(float(a), 8) for a in angles])
                print(f"{tag} seed={seed}: ideal success={ideal:.4f}", flush=True)

                def write_row(er, sn, secs):
                    writer.writerow({
                        "m": m, "n_m": m.bit_length(),
                        "variant": variant, "reps": reps,
                        "n_qubits": n_qubits, "multiplier": args.multiplier,
                        "shots": args.shots, "error_rate": er, "seed": seed,
                        "success_noisy": round(sn, 6) if sn is not None else "",
                        "success_ideal": round(ideal, 6),
                        "seconds": round(secs, 1),
                        "angles": angles_json,
                    })
                    f.flush()

                # noise-free baseline row (error_rate = -1, no shots needed; its
                # 'seconds' is the angle-optimization time for this seed)
                if need_baseline:
                    write_row(-1.0, None, opt_secs)

                for er in pending:
                    try:
                        t0 = time.time()
                        print(f"{tag} seed={seed} error={er:g}: sampling "
                              f"{args.shots} shots...", flush=True)
                        sn = success_probability_noisy(
                            problem, bound, build_noise_model(er),
                            shots=args.shots, seed=1000 * seed + int(er * 1e6))
                        write_row(er, sn, time.time() - t0)
                        print(f"{tag} seed={seed} error={er:g}: "
                              f"noisy={sn:.4f} (ideal={ideal:.4f}) "
                              f"({time.time() - t0:.0f}s)", flush=True)
                    except Exception as e:
                        print(f"{tag} seed={seed} ERROR error={er:g}: "
                              f"{type(e).__name__}: {e}", flush=True)

    f.close()
    print(f"\nDone. Results in {run_dir}/", flush=True)


if __name__ == "__main__":
    main()
