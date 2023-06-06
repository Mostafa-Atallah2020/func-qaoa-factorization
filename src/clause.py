import numpy as np
import pandas as pd
from sympy import Add
from symengine import sympify, Integer
import itertools


class BitsTable:
    def __init__(self, frame) -> None:
        self.table = frame
        self.bits = set(self.table.columns)

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
        self.__clause = clause
        self.bits = self.__clause.free_symbols
        self.pq_part, self.z_part = self.__split()

    def __table_from_expr(self, expr):
        expr = sympify(expr)
        # Create a list of variables
        variables = expr.free_symbols
        # Generate all possible combinations of 0 and 1 for the variables
        combinations = itertools.product([Integer(0), Integer(1)], repeat=len(variables))

        table = []
        for comb in combinations:
            # Create a dictionary of variables and their corresponding values
            subs_dict = dict(zip(variables, comb))
            # Substitute variables in expr and evaluate the expression
            expr_val = expr.subs(subs_dict).evalf()

            # Append the combination and corresponding value to the table
            table.append(comb + (expr_val,))


        # Create pandas DataFrames for each table
        df = pd.DataFrame(
            table, columns=[str(variable) for variable in variables] + ["value"]
        )
        return df

    def __split(self):
        coeff_dict = self.__clause.as_coefficients_dict()
        z_expr = Add(
            *[term * z for z, term in coeff_dict.items() if str(z).startswith("z_")]
        )
        other_expr = self.__clause - z_expr
        return other_expr, z_expr

    def reduce_space(self):
        combined_table = []
        z_part, pq_part = self.__split()
        z_table = self.__table_from_expr(z_part)
        pq_table = self.__table_from_expr(pq_part)

        for z_row in z_table.iterrows():
            z_row_values = z_row[1].values[:-1]  # Exclude the last column ('value')
            z_row_sum = z_row[1]["value"]

            for pq_row in pq_table.iterrows():
                pq_row_values = pq_row[1].values[:-1]
                pq_row_sum = pq_row[1]["value"]

                if z_row_sum + pq_row_sum == 0:
                    combined_row = list(z_row_values) + list(pq_row_values)
                    combined_table.append(combined_row)

        # Create pandas DataFrame for the combined table
        variables_z = list(z_table.columns)[:-1]
        variables_pq = list(pq_table.columns)[:-1]
        combined_columns = variables_z + variables_pq
        combined_df = pd.DataFrame(combined_table, columns=combined_columns)
        return BitsTable(combined_df)
