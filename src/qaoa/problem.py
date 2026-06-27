"""Problem and register model for the Prog-QAOA factorization certificate.

Defines the register layout for factoring a biprime ``m`` and enumerates the
target factor pairs that count as a solution.
"""

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class FactorizationProblem:
    """Register layout and target solutions for factoring ``m``."""

    m: int
    n_p: int
    n_q: int
    n_prod: int

    @property
    def n_search_qubits(self) -> int:
        """Qubits whose superposition forms the search space (p and q)."""
        return self.n_p + self.n_q

    @property
    def n_qubits(self) -> int:
        """Total qubits in the certificate circuit (p + q + product ancilla)."""
        return self.n_p + self.n_q + self.n_prod

    def solution_pairs(self, include_trivial: bool = False):
        """All ``(p, q)`` in the search space with ``p*q == m`` (mod 2**n_prod).

        With ``include_trivial=False`` the ``(m, 1)`` and ``(1, m)`` pairs are
        excluded, matching the success definition used for reporting.
        """
        mask = (1 << self.n_prod) - 1
        pairs = []
        for p in range(2 ** self.n_p):
            for q in range(2 ** self.n_q):
                if ((p * q) ^ self.m) & mask == 0:
                    if not include_trivial and (p == self.m or q == self.m or p == 1 or q == 1):
                        continue
                    pairs.append((p, q))
        return pairs


def make_problem(m: int) -> FactorizationProblem:
    """Build register sizes from ``m``: ``n_p = n_m``, ``n_q = ceil(n_m/2)``."""
    n_m = m.bit_length()
    n_p = n_m
    n_q = math.ceil(n_m / 2)
    n_prod = n_p + n_q
    return FactorizationProblem(m=m, n_p=n_p, n_q=n_q, n_prod=n_prod)
