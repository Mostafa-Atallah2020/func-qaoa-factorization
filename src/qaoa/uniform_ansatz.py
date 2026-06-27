"""The uniform Prog-QAOA ansatz: full search space with an X-mixer.

Builds the multiplication-certificate QAOA ansatz over the *full* search space:
a uniform Hadamard initial state on ``H_p``/``H_q`` (the product ancilla stays
``|0>``) and the transverse-field X-mixer. It reuses the shared phase separator
from :mod:`src.qaoa.certificate`. The reduced counterpart, which swaps the
initial state for a clause-feasible superposition and the X-mixer for a Grover
mixer, is in :mod:`src.qaoa.reduced_ansatz`.
"""

from qiskit import QuantumCircuit
from qiskit.circuit import Parameter

from src.qaoa.problem import FactorizationProblem
from src.qaoa.certificate import allocate_registers, make_phase_separator, apply_phase_separator


def build_ansatz(problem: FactorizationProblem, reps: int,
                 multiplier: str = "mcx") -> QuantumCircuit:
    """Construct the ``reps``-layer multiplication-certificate QAOA ansatz.

    Uses a uniform Hadamard initial state and an X-mixer. Returns a
    parameterised circuit with ``2 * reps`` parameters ordered per layer as
    ``gamma_<l>`` (objective) and ``beta_<l>`` (mixer).

    Args:
        problem: the :class:`~src.qaoa.problem.FactorizationProblem`.
        reps: number of QAOA layers.
        multiplier: which multiplier to use for the MUL block; one of
            :data:`~src.qaoa.certificate.MULTIPLIERS`
            (``"mcx"``, ``"hrs"``, ``"rgqft"``).

    Returns:
        the parameterised QAOA ansatz circuit.
    """
    p_reg, q_reg, prod_reg, anc_reg = allocate_registers(problem, multiplier)
    regs = [p_reg, q_reg, prod_reg] + ([anc_reg] if anc_reg is not None else [])
    qc = QuantumCircuit(*regs)

    # initial state: uniform superposition over the search space
    qc.h(p_reg)
    qc.h(q_reg)

    mul, mul_inv = make_phase_separator(problem, multiplier, p_reg, q_reg, prod_reg, anc_reg)

    search_qubits = list(p_reg) + list(q_reg)
    for layer in range(reps):
        gamma = Parameter(f"gamma_{layer}")
        beta = Parameter(f"beta_{layer}")
        apply_phase_separator(qc, problem, mul, mul_inv, prod_reg, gamma)
        # X-mixer on the search qubits
        for qb in search_qubits:
            qc.rx(2 * beta, qb)

    return qc
