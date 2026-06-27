"""Data model for the multiplication clauses and their feasible assignments.

Factoring ``m = p*q`` via binary multiplication produces one clause per output
bit, each a symbolic constraint over the ``p``/``q`` bits and carry bits ``z``.
This module provides the two primitives the search-space-reduction pipeline
operates on:

* :class:`Clause` wraps one such clause and can enumerate the bit-assignments
  that satisfy it (make it evaluate to zero).
* :class:`FeasibleAssignments` wraps the resulting table of allowed assignments
  (columns are bit-variables, rows are allowed value-combinations) and exposes
  its compression ratio, carry-bit removal, and the statevector of the equal
  superposition over only those feasible assignments, which the reduced QAOA
  initial state is prepared from.

These are pure data structures; the orchestration that uses them lives in
:mod:`src.preprocessing.search_space_reduction`.
"""

import itertools

import numpy as np
import pandas as pd
from qiskit.quantum_info import Statevector
from symengine import Integer, sympify
from sympy import Add

from src.preprocessing.utils import get_table_bin_combinations


class FeasibleAssignments:
    """Allowed value-assignments for a clause, stored as a table.

    Wraps a pandas DataFrame whose columns are bit-variables (``p_i``,
    ``q_j``, ``z_k``) and whose rows are the value-assignments consistent
    with a clause.
    """

    def __init__(self, frame) -> None:
        """Store the assignment table and record its bit-variable columns.

        Args:
            frame: a pandas DataFrame whose columns are bit-variables and
                whose rows are the allowed assignments.
        """
        self.table = frame
        self.bits = set(self.table.columns)

    def get_superposition_statevector(self):
        """Return the statevector of the uniform superposition over the rows.

        Returns:
            the statevector of the uniform superposition over the table's
            allowed assignments.
        """
        table_combs = get_table_bin_combinations(self.table)
        n_amps = len(table_combs)
        amp = 1 / (n_amps**0.5)
        desired_state = sum(
            [
                amp * Statevector.from_label(table_combs[i]).data
                for i in range(len(table_combs))
            ]
        )
        return desired_state

    def remove_carry_bits(self):
        """Drop the carry-bit (``z_*``) columns and any resulting duplicate rows.

        Returns:
            A new FeasibleAssignments holding only the ``p``/``q`` columns.
        """
        # Remove columns starting with "z_"
        self.table = self.table.filter(regex=r"^(?!z_)")
        # Remove duplicate rows
        self.table = self.table.drop_duplicates()
        return FeasibleAssignments(self.table)

    def compression_ratio(self):
        """Return the table's compression ratio.

        Returns:
            ``log2(num_rows) - num_columns``: how much the allowed-assignment
            table compresses the full bit space.
        """
        num_rows = len(self.table)
        num_columns = len(self.bits)
        quantity = np.log2(num_rows) - num_columns
        return quantity


class Clause:
    """A single multiplication clause from the factoring constraints.

    Wraps a symbolic clause expression and splits it into its product part
    (the ``p*q`` terms) and its carry part (the ``z`` terms).
    """

    def __init__(self, clause) -> None:
        """Store the clause and split it into product and carry parts.

        Args:
            clause: the symbolic clause expression.
        """
        self.clause = clause
        self.bits = self.clause.free_symbols
        self.pq_part, self.z_part = self.__split()

    def __table_from_expr(self, expr):
        """Tabulate an expression over all 0/1 assignments of its variables.

        Args:
            expr: the symbolic expression to evaluate.

        Returns:
            A DataFrame with one column per variable plus a ``value`` column
            holding the expression's value for each 0/1 combination.
        """
        expr = sympify(expr)
        # Create a list of variables
        variables = expr.free_symbols
        # Generate all possible combinations of 0 and 1 for the variables
        combinations = itertools.product(
            [Integer(0), Integer(1)], repeat=len(variables)
        )

        table = []
        for comb in combinations:
            # Create a dictionary of variables and their corresponding values
            subs_dict = dict(zip(variables, comb))
            # Substitute variables in expr and evaluate the expression
            expr_val = expr.subs(subs_dict).evalf()

            # Append the combination and corresponding value to the table
            table.append(comb + (expr_val,))

        # Create pandas DataFrames for each table
        df = pd.DataFrame(table, columns=list(variables) + ["value"])
        return df

    def __split(self):
        """Split the clause into its carry (``z``) part and the rest.

        Returns:
            A ``(pq_part, z_part)`` tuple of symbolic expressions, where
            ``z_part`` collects the ``z_*`` carry terms and ``pq_part`` is the
            remainder.
        """
        coeff_dict = self.clause.as_coefficients_dict()
        z_expr = Add(
            *[term * z for z, term in coeff_dict.items() if str(z).startswith("z_")]
        )
        other_expr = self.clause - z_expr
        return other_expr, z_expr

    def reduce_space(self):
        """Return the bit-assignments that satisfy the clause (evaluate to 0).

        Combines the product-part and carry-part value tables, keeping only the
        rows whose sums cancel, i.e. the assignments consistent with the clause.

        Returns:
            A FeasibleAssignments holding the clause-satisfying assignments.
        """
        combined_table = []
        z_table = self.__table_from_expr(self.z_part)
        pq_table = self.__table_from_expr(self.pq_part)

        z_values = z_table.values[:, :-1]  # Extract values excluding the last column
        z_sums = z_table["value"].values

        pq_values = pq_table.values[:, :-1]
        pq_sums = pq_table["value"].values

        zero_sum_indices = np.where(
            z_sums[:, np.newaxis] + pq_sums == 0
        )  # Find indices where sum is zero

        for z_index, pq_index in zip(*zero_sum_indices):
            combined_row = np.concatenate([z_values[z_index], pq_values[pq_index]])
            combined_table.append(combined_row)

        combined_columns = list(z_table.columns)[:-1] + list(pq_table.columns)[:-1]
        combined_array = np.array(combined_table)
        combined_df = pd.DataFrame(combined_array, columns=combined_columns).astype(
            np.uint8
        )
        return FeasibleAssignments(combined_df)
