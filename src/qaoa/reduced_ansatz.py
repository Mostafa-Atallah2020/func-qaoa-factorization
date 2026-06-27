"""
Search-space reduction for the Prog-QAOA factorization certificate.

Using the classical VQF preprocessing
(:class:`~src.preprocessing.search_space_reduction.SearchSpaceReducer`) yields, for some bits of
``p`` and ``q``, the set of value-assignments consistent with the
multiplication clauses ("superposition reduction"). Instead of starting QAOA
in a uniform Hadamard superposition over all of ``H_p``/``H_q``, we:

* set the least-significant bit of ``p`` and ``q`` to ``|1>`` (factors of an
  odd biprime are odd; the bit-substitution case), and
* prepare, on each constrained group of bits, the uniform superposition over
  exactly the allowed assignments from the corresponding table (the
  superposition-reduction case), via a general state-preparation routine, and
* apply Hadamards to the remaining unconstrained ``p``/``q`` qubits.

The full state-preparation circuit ``U`` is then reused to build a Grover
mixer ``U (2|0><0| - I) U^\\dagger``, which mixes amplitude only within the
reduced search space.

Bit naming: a column ``q_k`` / ``p_k`` denotes bit ``k`` (1-indexed, LSB = bit
0) of register ``q`` / ``p``. These map to qubit index ``k`` of the
corresponding register in the certificate.
"""

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit import Parameter
from qiskit.circuit.library import StatePreparation

from src.preprocessing.search_space_reduction import SearchSpaceReducer


def _parse_bit(symbol):
    """'q_2' -> ('q', 2)."""
    reg, idx = str(symbol).split("_")
    return reg, int(idx)


def _table_state_vector(table):
    """Uniform superposition over the table's allowed assignments.

    Returns ``(qubit_specs, statevector)`` where ``qubit_specs`` is the list of
    ``(register, bit_index)`` in the column order used by the statevector
    (little-endian: first column is the least-significant amplitude index bit).
    """
    cols = list(table.table.columns)
    specs = [_parse_bit(c) for c in cols]
    sv = np.asarray(table.get_superposition_statevector(), dtype=complex)
    sv = sv / np.linalg.norm(sv)
    return specs, sv


def constrained_bits(vqf: SearchSpaceReducer):
    """All ``(register, bit_index)`` covered by some superposition table."""
    out = set()
    for t in vqf.superposition_tables:
        if t is None:
            continue
        for c in t.table.columns:
            out.add(_parse_bit(c))
    return out


def build_reduced_initial_state(problem, vqf: SearchSpaceReducer) -> QuantumCircuit:
    """State-preparation circuit ``U`` for the reduced search space.

    Acts on registers named ``p`` (size ``n_p``) and ``q`` (size ``n_q``).
    """
    p_reg = QuantumRegister(problem.n_p, "p")
    q_reg = QuantumRegister(problem.n_q, "q")
    qc = QuantumCircuit(p_reg, q_reg, name="U_init")
    reg_of = {"p": p_reg, "q": q_reg}

    # bit-substitution: LSB of p and q fixed to 1 (odd factors)
    qc.x(p_reg[0])
    qc.x(q_reg[0])

    covered = set()
    covered.add(("p", 0))
    covered.add(("q", 0))

    # superposition-reduction: prepare each table on its specific qubits
    for t in vqf.superposition_tables:
        if t is None:
            continue
        specs, sv = _table_state_vector(t)
        target_qubits = [reg_of[r][b] for (r, b) in specs]
        qc.append(StatePreparation(sv), target_qubits)
        covered.update(specs)

    # remaining unconstrained p/q qubits -> uniform superposition
    for reg_name, reg in (("p", p_reg), ("q", q_reg)):
        for b in range(len(reg)):
            if (reg_name, b) not in covered:
                qc.h(reg[b])

    return qc


def grover_mixer(init_state: QuantumCircuit, beta: Parameter) -> QuantumCircuit:
    """Parameterised QAOA Grover mixer ``U . Phase_0(2 beta) . U^\\dagger``.

    ``U`` is the reduced state-preparation circuit. ``Phase_0`` applies a phase
    ``exp(-i * 2 beta)`` to the all-zeros state only, so that conjugating by
    ``U`` mixes amplitude solely within the reduced search space (the states
    reachable by ``U`` from ``|0...0>``). Acts on ``init_state``'s qubits.
    """
    n = init_state.num_qubits
    qc = QuantumCircuit(*init_state.qregs, name="grover_mixer")

    qc.compose(init_state.inverse(), inplace=True)

    # phase on |0...0>: X-sandwich a multi-controlled phase
    qc.x(range(n))
    if n == 1:
        qc.p(2 * beta, 0)
    else:
        qc.mcp(2 * beta, list(range(n - 1)), n - 1)
    qc.x(range(n))

    qc.compose(init_state, inplace=True)
    return qc


def build_reduced_ansatz(problem, vqf: SearchSpaceReducer, reps: int,
                         multiplier: str = "mcx"):
    """Certificate ansatz with the reduced initial state and a Grover mixer.

    Same phase separator as :func:`~src.qaoa.uniform_ansatz.build_ansatz`, but
    the uniform Hadamard init is replaced by the reduced state-preparation
    ``U`` (see :func:`build_reduced_initial_state`) and the X-mixer by the
    Grover mixer built from ``U``. Parameters per layer: ``gamma_<l>`` and
    ``beta_<l>``.
    """
    from qiskit import QuantumCircuit as _QC
    from src.qaoa.certificate import (
        allocate_registers, make_phase_separator, apply_phase_separator,
    )

    p_reg, q_reg, prod_reg, anc_reg = allocate_registers(problem, multiplier)
    regs = [p_reg, q_reg, prod_reg] + ([anc_reg] if anc_reg is not None else [])
    qc = _QC(*regs)

    # reduced initial state on the p/q registers
    U = build_reduced_initial_state(problem, vqf)
    pq_qubits = list(p_reg) + list(q_reg)
    qc.compose(U, qubits=pq_qubits, inplace=True)

    mul, mul_inv = make_phase_separator(problem, multiplier, p_reg, q_reg, prod_reg, anc_reg)

    for layer in range(reps):
        gamma = Parameter(f"gamma_{layer}")
        beta = Parameter(f"beta_{layer}")
        apply_phase_separator(qc, problem, mul, mul_inv, prod_reg, gamma)
        # Grover mixer on the p/q registers, built from U
        mixer = grover_mixer(U, beta)
        qc.compose(mixer, qubits=pq_qubits, inplace=True)

    return qc
