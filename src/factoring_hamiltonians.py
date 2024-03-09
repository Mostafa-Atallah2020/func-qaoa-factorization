"""
refs

[1] https://arxiv.org/abs/1808.08927
"""

from vqf.preprocessing import create_clauses
from src import Clause
from qiskit.quantum_info import Pauli, Operator

I = Pauli("I")
Z = Pauli("Z")

I = Operator(I)
Z = Operator(Z)

from sympy import (
    Float,
    Integer,
    Mul,
    Pow,
    Symbol,
    factor,
    Symbol,
)

from sympy.core.numbers import NegativeOne


class IsingHamiltonian:
    def __init__(self, biprime: int) -> None:
        self.__classical_hamiltonian = FactoringHamiltonian(biprime)
        self.hamiltonian = self.__get_ising()

    def __get_ising(self):
        ising_terms = []
        for i in range(len(self.__classical_hamiltonian.terms)):
            t = self.__classical_hamiltonian.terms[i]

            # ignoring constant terms in the ising hamiltonians
            if not isinstance(t, int):
                pauli_str = self.__get_pauli_str(t, self.__classical_hamiltonian.bits)
                # print(str(pauli_str) + "\n")
                if not isinstance(pauli_str, type(None)):
                    ising_terms.append(pauli_str)

        hamiltonian = sum(ising_terms)
        hamiltonian = hamiltonian.reduce()

    def __get_symbols(self, term: Mul):
        """
        It retuns symbols and coefficient for a sympy symbol of the form c * x_1 * x_2 * ... * x_n.
        """
        args = term.args
        try:
            if isinstance(args[0], (Integer, Float, NegativeOne)):
                coeff = float(args[0])
                args_no_coeff = args[1:]

            else:
                coeff = 1
                args_no_coeff = args[:]

        except:
            if len(args) == 0 and isinstance(term, Symbol):
                coeff = 1
                args_no_coeff = (term,)

            else:
                coeff = term
                args_no_coeff = ()

        return coeff, args_no_coeff

    def __get_pauli_str(self, energy_term: Mul, bits):
        """
        It returns qiskit pauli string for a classical energy term.
        """
        bits = list(bits)
        coeff, symbols = self.__get_symbols(energy_term)
        symbols = list(symbols)
        vars = {}

        if len(symbols) > 0:
            for i in range(len(bits)):
                s = bits[i]
                vars[s] = False

            for i in range(len(symbols)):
                if symbols[i] in vars.keys():
                    vars[symbols[i]] = True

            if vars[bits[0]]:
                ising = (I - Z) / 2
            else:
                ising = I

            for i in range(1, len(bits)):
                if vars[bits[i]]:
                    ising ^= (I - Z) / 2
                else:
                    ising ^= I
            # else:
            #    print("Constant terms in an ising hamiltonians are unimportatnt.")
            # return coeff

            # print(coeff * ising)
            return coeff * ising


class FactoringHamiltonian:
    """
    Calculates the factoring Hamiltonian for a biprime `m`.

    Returns:
    -------

    `hamiltonian` : sympy expression
        The Hamiltonian representing the factoring of the biprime `m`, as defined in eq(7) in [1].


    """

    def __init__(self, biprime: int) -> None:
        self.hamiltonian = self.__get_classical_energy(biprime, apply_rules=True)

    def __get_classical_energy(self, m: int, apply_rules=False, verbose=False):
        """
        Calculates the classical energy for the set of classically simplified clauses for a prime m.

        Args:
        -----

        - `m (int)`: Prime number to calculate the classical energy for.
        - `apply_rules (bool)`: If `True`, applies rules for simplifying the energy expression. Defaults to `False`s.

        Returns:
        --------

        - SymPy expression representing the classical energy.

        Refer to equation (6) in the VQF paper (https://arxiv.org/abs/1808.08927) for more information.
        """
        # create_clauses() creates a list of clauses from the given expression
        # and applies preprocessing operations (if apply_preprocessing is True)
        _, _, _, clauses = create_clauses(
            m, apply_preprocessing=apply_rules, verbose=verbose
        )
        # Calculate the energy of the expression
        # by building an equation using each clause in the given expression
        energy = sum([clauses[i] ** 2 for i in range(len(clauses))])
        # Expand the expression to simplify the calculation
        energy = energy.expand()

        # Apply the preprocessing rules to the expression, if it is necessary
        if apply_rules:
            # Simplify the expression with known expressions, if necessary
            energy = self.__simplify_clause(energy, known_expressions={})

        return Clause(energy)

    def __simplify_clause(self, clause, known_expressions):
        """
        Performs simplification of clauses in an efficient manner.

        Args:
        -----

            `clause` (`sympy.Expr`): A single clause in the form of a sympy expression.
            `known_expressions` (`dict`): A dictionary of expressions that have been deduced from the clauses.
                                    Keys are sympy expressions, either simple ones (e.g.: `q_0`),
                                    which represent single unknowns, or more complex (e.g.: `p_1*q_1`).
                                    Values are either sympy expressions or integers (0 or 1).
        Returns:
        --------

            simplified_clause (sympy.Expr): The simplified form of the input `clause`.
        """
        simplified_clause = clause.subs(known_expressions).expand()

        for term in simplified_clause.args:
            if isinstance(term, Pow) and term.exp == 2:
                simplified_clause = simplified_clause.subs({term: term.base})
            elif isinstance(term, Mul):
                for subterm in term.args:
                    if isinstance(subterm, Pow) and subterm.exp == 2:
                        simplified_clause = simplified_clause.subs(
                            {subterm: subterm.base}
                        )

        simplified_clause = factor(simplified_clause)

        return simplified_clause
