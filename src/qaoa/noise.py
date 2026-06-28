"""Depolarizing + readout noise models for the Prog-QAOA factorization circuits.

Builds a tunable :class:`~qiskit_aer.noise.NoiseModel` controlled by a single
``error_rate`` knob (the two-qubit gate error probability, the dominant source).
The single-qubit gate error and the readout error are derived as fixed fractions
of it, so one parameter sweeps the overall noise strength from ideal
(``error_rate=0``) upward. This lets us trace how success probability degrades as
noise increases, without committing to any particular hardware's rates.

Thermal relaxation (T1/T2) is intentionally omitted to keep the model simple; the
depolarizing-plus-readout model already captures the dominant impact of noise for
this analysis.
"""

from qiskit_aer.noise import NoiseModel, ReadoutError, depolarizing_error

# The single-qubit gate error and readout error are taken as these fractions of
# the (dominant) two-qubit error rate, a typical ordering for gate-based devices.
ONE_QUBIT_FRACTION = 0.1
READOUT_FRACTION = 1.0


def build_noise_model(error_rate, one_qubit_fraction=ONE_QUBIT_FRACTION,
                      readout_fraction=READOUT_FRACTION, basis_gates=("u3", "cx")):
    """Build a depolarizing + readout NoiseModel at the given error rate.

    Args:
        error_rate: the two-qubit (cx) depolarizing probability, and the knob
            that sets the overall noise strength. ``0`` returns a noise-free
            model.
        one_qubit_fraction: single-qubit (u3) error as a fraction of
            ``error_rate``.
        readout_fraction: symmetric readout error as a fraction of
            ``error_rate``.
        basis_gates: the gate set the noise model targets.

    Returns:
        A NoiseModel with depolarizing error on the single- and two-qubit gates
        and a symmetric readout error on measurement.
    """
    nm = NoiseModel(basis_gates=list(basis_gates))
    if error_rate <= 0:
        return nm  # ideal: no errors attached

    e2 = min(max(error_rate, 0.0), 0.999)
    e1 = min(max(error_rate * one_qubit_fraction, 0.0), 0.999)
    er = min(max(error_rate * readout_fraction, 0.0), 0.5)

    nm.add_all_qubit_quantum_error(depolarizing_error(e1, 1), ["u3"])
    nm.add_all_qubit_quantum_error(depolarizing_error(e2, 2), ["cx"])
    nm.add_all_qubit_readout_error(ReadoutError([[1 - er, er], [er, 1 - er]]))
    return nm
