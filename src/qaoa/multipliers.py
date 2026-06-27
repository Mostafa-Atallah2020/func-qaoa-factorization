"""
Quantum multipliers for the Prog-QAOA multiplication certificate.

Three implementations with different qubit/gate trade-offs let us compare
resource profiles. Each computes ``prod += p * q`` assuming ``prod`` starts in
``|0...0>`` and exposes the same ``(qc, p_reg, q_reg, prod_reg, ancilla)``
signature.

* :func:`mcx_multiplier`: ancilla-free schoolbook accumulation via wide
  multi-controlled-X gates. Zero extra qubits, many CNOTs. A naive baseline that
  the adder/QFT multipliers below improve on.

* :func:`hrs_multiplier`: Qiskit's ``HRSCumulativeMultiplier`` (cumulative
  adder, Haener-Roetteler-Svore). Adder-based, O(n^2) gates, with carry
  ancillas.

* :func:`rgqft_multiplier`: Qiskit's ``RGQFTMultiplier`` (QFT-based,
  Ruiz-Perez & Garcia-Escartin). O(n^2) gates, with QFT ancillas.

Each multiplier ``f`` has a companion ``f_ancilla_count(n_p, n_q, n_prod)``
giving the number of clean ancilla qubits it needs (returned to ``|0>``).
``mcx`` is its own inverse on the product subspace; the Qiskit-backed two are
uncomputed via an explicit ``.inverse()`` in the certificate builder.
"""

from collections import namedtuple

from qiskit.circuit.library import HRSCumulativeMultiplier, RGQFTMultiplier


# --------------------------------------------------------------------------- #
# Ancilla-free, mcx-based schoolbook multiplier                               #
# --------------------------------------------------------------------------- #

def mcx_multiplier(qc, p_reg, q_reg, prod_reg, ancilla=None):
    """``prod += p * q`` with no ancilla, via multi-controlled-X ripples.

    ``ancilla`` is accepted (and ignored) only to share the common multiplier
    signature.
    """
    n_prod = len(prod_reg)
    for i in range(len(p_reg)):
        for j in range(len(q_reg)):
            pos = i + j
            # ripple the partial product p_i & q_j upward through the carries
            for k in range(n_prod - 1, pos, -1):
                controls = [p_reg[i], q_reg[j]] + [prod_reg[t] for t in range(pos, k)]
                qc.mcx(controls, prod_reg[k])
            qc.ccx(p_reg[i], q_reg[j], prod_reg[pos])


def mcx_ancilla_count(n_p, n_q, n_prod):
    """Clean ancilla qubits needed by :func:`mcx_multiplier`: always zero."""
    return 0


# --------------------------------------------------------------------------- #
# Qiskit-library multipliers (padded to equal-width operands)                 #
# --------------------------------------------------------------------------- #
#
# Qiskit's multipliers want equal-width inputs ``a``, ``b`` of size
# ``n = max(n_p, n_q)`` and an output of width ``2n`` (plus an internal helper
# register). Our problem has unequal registers and a ``prod`` register of width
# ``n_prod <= 2n``, so we borrow ancilla qubits to:
#   - pad ``p`` up to width n  (a-padding)
#   - pad ``q`` up to width n  (b-padding)
#   - extend ``prod`` up to width 2n  (out-padding)
#   - supply the multiplier's own internal helper qubits
# All borrowed qubits start and end in ``|0>``.

# Layout of the borrowed ancilla register, computed once and shared by both the
# circuit builder and the ancilla counter.
_QiskitLayout = namedtuple("_QiskitLayout", "n a_pad b_pad out_pad helper total")


def _qiskit_layout(builder_cls, n_p, n_q, n_prod):
    n = max(n_p, n_q)
    a_pad = n - n_p
    b_pad = n - n_q
    out_pad = 2 * n - n_prod
    helper = builder_cls(num_state_qubits=n).num_qubits - 4 * n
    total = a_pad + b_pad + out_pad + helper
    return _QiskitLayout(n, a_pad, b_pad, out_pad, helper, total)


def _qiskit_multiply(builder_cls, qc, p_reg, q_reg, prod_reg, ancilla):
    """Apply a Qiskit library multiplier as ``prod += p * q``."""
    L = _qiskit_layout(builder_cls, len(p_reg), len(q_reg), len(prod_reg))
    anc = list(ancilla)

    # carve the ancilla register into its four roles, in order
    a_pad, anc = anc[:L.a_pad], anc[L.a_pad:]
    b_pad, anc = anc[:L.b_pad], anc[L.b_pad:]
    out_pad, anc = anc[:L.out_pad], anc[L.out_pad:]
    helper = anc[:L.helper]

    a_qubits = list(p_reg) + a_pad          # width n (LSB first)
    b_qubits = list(q_reg) + b_pad          # width n
    out_qubits = list(prod_reg) + out_pad   # width 2n

    gate = builder_cls(num_state_qubits=L.n).to_gate()
    qc.append(gate, a_qubits + b_qubits + out_qubits + helper)


def _qiskit_ancilla_count(builder_cls, n_p, n_q, n_prod):
    return _qiskit_layout(builder_cls, n_p, n_q, n_prod).total


def hrs_multiplier(qc, p_reg, q_reg, prod_reg, ancilla):
    """``prod += p * q`` via Qiskit's ``HRSCumulativeMultiplier``.

    The unequal-width operands are padded to equal width and ``prod`` extended
    using borrowed ``ancilla`` qubits (returned to ``|0>``).

    Args:
        qc: the circuit the multiplier is appended to.
        p_reg: the first operand register.
        q_reg: the second operand register.
        prod_reg: the product register (assumed to start in ``|0...0>``).
        ancilla: clean ancilla qubits sized per :func:`hrs_ancilla_count`.
    """
    _qiskit_multiply(HRSCumulativeMultiplier, qc, p_reg, q_reg, prod_reg, ancilla)


def hrs_ancilla_count(n_p, n_q, n_prod):
    """Clean ancilla qubits needed by :func:`hrs_multiplier`.

    Args:
        n_p: width of the first operand register.
        n_q: width of the second operand register.
        n_prod: width of the product register.

    Returns:
        the number of clean ancilla qubits the multiplier requires.
    """
    return _qiskit_ancilla_count(HRSCumulativeMultiplier, n_p, n_q, n_prod)


def rgqft_multiplier(qc, p_reg, q_reg, prod_reg, ancilla):
    """``prod += p * q`` via Qiskit's ``RGQFTMultiplier``.

    The unequal-width operands are padded to equal width and ``prod`` extended
    using borrowed ``ancilla`` qubits (returned to ``|0>``).

    Args:
        qc: the circuit the multiplier is appended to.
        p_reg: the first operand register.
        q_reg: the second operand register.
        prod_reg: the product register (assumed to start in ``|0...0>``).
        ancilla: clean ancilla qubits sized per :func:`rgqft_ancilla_count`.
    """
    _qiskit_multiply(RGQFTMultiplier, qc, p_reg, q_reg, prod_reg, ancilla)


def rgqft_ancilla_count(n_p, n_q, n_prod):
    """Clean ancilla qubits needed by :func:`rgqft_multiplier`.

    Args:
        n_p: width of the first operand register.
        n_q: width of the second operand register.
        n_prod: width of the product register.

    Returns:
        the number of clean ancilla qubits the multiplier requires.
    """
    return _qiskit_ancilla_count(RGQFTMultiplier, n_p, n_q, n_prod)
