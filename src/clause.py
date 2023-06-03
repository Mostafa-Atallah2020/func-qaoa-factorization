from itertools import product

import numpy as np
import pandas as pd
from IPython.display import display
from sympy import simplify, Add


class BitsTable:
    def __init__(self, frame) -> None:
        self.table = frame
        self.bits = set(self.table.columns)
        # display(self.table)

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

    def __split(self):
        coeff_dict = self.__clause.as_coefficients_dict()
        z_expr = Add(
            *[term * z for z, term in coeff_dict.items() if str(z).startswith("z_")]
        )
        other_expr = self.__clause - z_expr
        return other_expr, z_expr

    def reduce_space(self):
        variables = list(self.bits)
        values = product(range(2), repeat=len(variables))
        reduced_space = []
        for v in values:
            subs_dict = dict(zip(variables, v))
            subs_expr = self.__clause.subs(subs_dict)
            if simplify(subs_expr) == 0:
                reduced_space.append(v)
        df = pd.DataFrame(reduced_space, columns=variables).astype(np.uint8)
        return BitsTable(df)
