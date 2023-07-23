import itertools

import numpy as np
import pandas as pd
from qiskit.quantum_info import Statevector
from symengine import Integer, sympify
from sympy import Add

from src.clause_utils import get_table_bin_combinations


class BitsTable:
    def __init__(self, frame) -> None:
        self.table = frame
        self.bits = set(self.table.columns)

    def get_init_state(self):
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
        # Remove columns starting with "z_"
        self.table = self.table.filter(regex=r"^(?!z_)")
        # Remove duplicate rows
        self.table = self.table.drop_duplicates()
        return BitsTable(self.table)

    def calc_r(self):
        num_rows = len(self.table)
        num_columns = len(self.bits)
        quantity = np.log2(num_rows) - num_columns
        return quantity


class Clause:
    def __init__(self, clause) -> None:
        self.clause = clause
        self.bits = self.clause.free_symbols
        self.pq_part, self.z_part = self.__split()

    def __table_from_expr(self, expr):
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
        coeff_dict = self.clause.as_coefficients_dict()
        z_expr = Add(
            *[term * z for z, term in coeff_dict.items() if str(z).startswith("z_")]
        )
        other_expr = self.clause - z_expr
        return other_expr, z_expr

    def reduce_space(self):
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
        return BitsTable(combined_df)
