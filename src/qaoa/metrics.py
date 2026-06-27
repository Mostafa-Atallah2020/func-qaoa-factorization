"""Simulation and metrics for the Prog-QAOA factorization ansatz.

Statevector evaluation of the success probability (exact and shot-based noisy),
a fast repeated-evaluation helper for the optimizer, the search-space size, and
transpiled resource counts (qubits, depth, CNOT/u3). These work on any ansatz
built by :mod:`src.qaoa.uniform_ansatz` or :mod:`src.qaoa.reduced_ansatz`.
"""

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

from src.qaoa.problem import FactorizationProblem


_SIM = AerSimulator(method="statevector")


def _simulate_probabilities(circ):
    """Run a (already gate-level) circuit and return the statevector |amp|^2."""
    circ = circ.copy()
    circ.save_statevector()
    sv = np.asarray(_SIM.run(circ).result().get_statevector())
    return np.abs(sv) ** 2


def search_space_probabilities(problem: FactorizationProblem, bound_circuit):
    """Return a dict ``{(p, q): probability}`` over the search registers.

    The product ancilla is disentangled (it returns to ``|0>`` after the
    uncompute), so marginalising over it just sums the |amplitude|^2 of the
    matching basis states.
    """
    probs = _simulate_probabilities(bound_circuit.decompose(reps=5))

    n_p, n_q = problem.n_p, problem.n_q
    out = {}
    for idx, pr in enumerate(probs):
        if pr < 1e-12:
            continue
        p = idx & ((1 << n_p) - 1)
        q = (idx >> n_p) & ((1 << n_q) - 1)
        out[(p, q)] = out.get((p, q), 0.0) + float(pr)
    return out


def search_space_size(initial_state) -> float:
    """log2(# basis states spanning the state).

    ``initial_state`` is the state-preparation circuit (acting on the p/q
    search qubits). Returns ``log2`` of the number of computational basis
    vectors with non-zero amplitude.
    """
    probs = _simulate_probabilities(initial_state.decompose(reps=5))
    support = int(np.count_nonzero(probs > 1e-12))
    return float(np.log2(support)) if support else 0.0


def success_probability(problem: FactorizationProblem, bound_circuit) -> float:
    """Total probability on non-trivial true-factor states (excludes (m,1))."""
    probs = search_space_probabilities(problem, bound_circuit)
    targets = set(problem.solution_pairs(include_trivial=False))
    return sum(pr for pair, pr in probs.items() if pair in targets)


def success_probability_noisy(problem: FactorizationProblem, bound_circuit,
                              noise_model, shots=8192, seed=None,
                              basis_gates=("u3", "cx")) -> float:
    """Shot-based success probability under a noise model.

    Transpiles the bound circuit to ``basis_gates``, measures only the ``p`` and
    ``q`` search qubits (the product ancilla is uncomputed to ``|0>``), runs the
    noisy sampler, and returns the fraction of shots whose measured ``(p, q)`` is
    a non-trivial true factor pair. This is the noisy analogue of
    :func:`success_probability`, suitable when an exact statevector is no longer
    available because of noise.

    Args:
        problem: the FactorizationProblem (defines the search registers).
        bound_circuit: the angle-bound ansatz (no measurements).
        noise_model: a qiskit-aer NoiseModel to apply.
        shots: number of measurement shots.
        seed: optional simulator seed for reproducible sampling.
        basis_gates: gate set to transpile to before adding noise.

    Returns:
        The estimated success probability (shots on a true factor / total shots).
    """
    n_p, n_q = problem.n_p, problem.n_q
    qc = bound_circuit.decompose(reps=5)
    tqc = transpile(qc, basis_gates=list(basis_gates), optimization_level=1)
    # measure the search qubits (indices 0..n_p+n_q-1) into a dedicated register
    tqc = tqc.copy()
    search = list(range(n_p + n_q))
    tqc.measure_all(inplace=True)  # measures all qubits; we slice p,q from the key

    sim = AerSimulator(noise_model=noise_model)
    run_kwargs = {"shots": shots}
    if seed is not None:
        run_kwargs["seed_simulator"] = int(seed)
    counts = sim.run(tqc, **run_kwargs).result().get_counts()

    targets = set(problem.solution_pairs(include_trivial=False))
    # measure_all bitstrings are big-endian over all qubits: bit 0 is qubit 0 at
    # the right end. Strip spaces, then index from the right for p/q qubits.
    hits = 0
    total = 0
    for bitstr, c in counts.items():
        bits = bitstr.replace(" ", "")
        total += c
        # qubit k is bits[-1-k]
        p = sum((bits[-1 - k] == "1") << k for k in range(n_p))
        q = sum((bits[-1 - (n_p + k)] == "1") << k for k in range(n_q))
        if (p, q) in targets:
            hits += c
    return hits / total if total else 0.0


class SuccessEvaluator:
    """Fast repeated success-probability evaluation for a fixed ansatz.

    Decomposes the parametric ansatz to gate level **once** (the expensive
    step), then each :meth:`evaluate` only rebinds the angles and simulates,
    avoiding the per-call re-decomposition that dominates optimisation cost.

    A boolean mask over statevector indices selects the basis states whose
    ``(p, q)`` is a non-trivial true factor pair; success probability is the
    summed probability of those indices.
    """

    def __init__(self, problem: FactorizationProblem, ansatz):
        # decompose the PARAMETRIC circuit once (Parameters are preserved)
        self._template = ansatz.decompose(reps=5)
        self._params = sorted(self._template.parameters, key=lambda p: p.name)

        # precompute which statevector indices count as success
        n_p, n_q = problem.n_p, problem.n_q
        targets = set(problem.solution_pairs(include_trivial=False))
        dim = 1 << self._template.num_qubits
        mask = np.zeros(dim, dtype=bool)
        for idx in range(dim):
            p = idx & ((1 << n_p) - 1)
            q = (idx >> n_p) & ((1 << n_q) - 1)
            if (p, q) in targets:
                mask[idx] = True
        self._mask = mask

    @property
    def parameters(self):
        """Ansatz parameters sorted by name (the angle order for ``evaluate``)."""
        return list(self._params)

    def evaluate(self, angles) -> float:
        """Success probability for the given angle vector (order = ``parameters``)."""
        bound = self._template.assign_parameters(dict(zip(self._params, angles)))
        probs = _simulate_probabilities(bound)
        return float(probs[self._mask].sum())


def resource_metrics(problem: FactorizationProblem, ansatz: QuantumCircuit,
                     basis_gates=("cx", "u3"), optimization_level: int = 3) -> dict:
    """Transpile the ansatz and report qubit count, depth and CNOT count.

    ``n_qubits`` is the true circuit width (search + product + any multiplier
    ancillas), so it reflects the cost of the chosen multiplier.
    """
    bound = ansatz.assign_parameters(
        {pr: 0.0 for pr in ansatz.parameters}
    ) if ansatz.parameters else ansatz
    tqc = transpile(bound, basis_gates=list(basis_gates),
                    optimization_level=optimization_level)
    ops = tqc.count_ops()
    return {
        "n_qubits": ansatz.num_qubits,
        "n_search_qubits": problem.n_search_qubits,
        "depth": tqc.depth(),
        "cnot_count": int(ops.get("cx", 0)),
        "u3_count": int(ops.get("u3", 0)),
    }
