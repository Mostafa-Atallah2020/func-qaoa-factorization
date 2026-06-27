"""Shared building blocks for the multiplication-certificate phase separator.

The multiplication-certificate construction. A single QAOA cost layer applies,
on registers ``H_p``, ``H_q`` and an ancilla product register ``H_product``
(initialised to ``|0>``):

    1. MUL: compute ``p * q`` into ``H_product``
    2. XOR m: bitwise-xor the product register with the binary of ``m``
    3. Z-rot: qubit-wise Z-rotation on ``H_product``
    4. uncompute steps 1-2

The qubit-wise rotation realises a phase proportional to the number of bits at
which ``p*q`` and ``m`` differ, i.e. the cost is ``Hamming(p*q, m)``. Its ground
space is the set of ``(p, q)`` with ``p*q == m`` (within ``n_prod`` bits), which
always includes the trivial ``(m, 1)`` solution. The trivial pair is a genuine
ground state in the simulation (it has non-zero amplitude), but it is excluded
from the reported success probability: only non-trivial factor pairs count as a
success (see ``FactorizationProblem.solution_pairs`` and
:mod:`src.qaoa.metrics`).

These blocks (register allocation and the phase separator) are shared by both
QAOA variants: the uniform ansatz in :mod:`src.qaoa.uniform_ansatz` and the
reduced ansatz in :mod:`src.qaoa.reduced_ansatz`, which differ only in their
initial state and mixer.
"""

from qiskit import QuantumCircuit, QuantumRegister

from src.qaoa.problem import FactorizationProblem
from src.qaoa.multipliers import (
    mcx_multiplier, mcx_ancilla_count,
    hrs_multiplier, hrs_ancilla_count,
    rgqft_multiplier, rgqft_ancilla_count,
)

# Registry of available multipliers: name -> (apply_fn, ancilla_count_fn).
MULTIPLIERS = {
    "mcx": (mcx_multiplier, mcx_ancilla_count),
    "hrs": (hrs_multiplier, hrs_ancilla_count),
    "rgqft": (rgqft_multiplier, rgqft_ancilla_count),
}


def _xor_m(qc, prod_reg, m: int):
    """Bitwise XOR of the product register with the binary of ``m``."""
    for k in range(len(prod_reg)):
        if (m >> k) & 1:
            qc.x(prod_reg[k])


def _multiply_subcircuit(problem, multiplier, p_reg, q_reg, prod_reg, anc_reg):
    """Build the MUL block as a standalone circuit (so we can invert it)."""
    regs = [p_reg, q_reg, prod_reg] + ([anc_reg] if anc_reg is not None else [])
    sub = QuantumCircuit(*regs, name="MUL")
    multiplier(sub, p_reg, q_reg, prod_reg, anc_reg)
    return sub


def allocate_registers(problem: FactorizationProblem, multiplier: str):
    """Return ``(p_reg, q_reg, prod_reg, anc_reg_or_None)`` for ``multiplier``."""
    if multiplier not in MULTIPLIERS:
        raise ValueError(f"unknown multiplier {multiplier!r}; choices: {list(MULTIPLIERS)}")
    _, anc_fn = MULTIPLIERS[multiplier]
    p_reg = QuantumRegister(problem.n_p, "p")
    q_reg = QuantumRegister(problem.n_q, "q")
    prod_reg = QuantumRegister(problem.n_prod, "prod")
    n_anc = anc_fn(problem.n_p, problem.n_q, problem.n_prod)
    anc_reg = QuantumRegister(n_anc, "anc") if n_anc else None
    return p_reg, q_reg, prod_reg, anc_reg


def make_phase_separator(problem, multiplier, p_reg, q_reg, prod_reg, anc_reg):
    """Return ``(mul, mul_inv)`` sub-circuits for the certificate's MUL block."""
    mult_fn, _ = MULTIPLIERS[multiplier]
    mul = _multiply_subcircuit(problem, mult_fn, p_reg, q_reg, prod_reg, anc_reg)
    return mul, mul.inverse()


def apply_phase_separator(qc, problem, mul, mul_inv, prod_reg, gamma):
    """MUL, XOR m, qubit-wise Z-rotation, uncompute."""
    qc.compose(mul, inplace=True)
    _xor_m(qc, prod_reg, problem.m)
    for qb in prod_reg:
        qc.rz(2 * gamma, qb)           # phase ~ number of differing bits
    _xor_m(qc, prod_reg, problem.m)
    qc.compose(mul_inv, inplace=True)
