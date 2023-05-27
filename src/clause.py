from itertools import product

import numpy as np
import pandas as pd
from IPython.display import display
from sympy import simplify


class BitsTable:
    def __init__(self, frame) -> None:
        self.table = frame
        self.bits = set(self.table.columns)
        #display(self.table)

    def remove_carry_bits(self):
        # Remove columns starting with "z_"
        self.table = self.table.filter(regex=r"^(?!z_)")
        # Remove duplicate rows
        self.table = self.table.drop_duplicates()
        return BitsTable(self.table)

    def calc_r(self):
        num_rows = len(self.table)
        num_columns = len(self.table.columns)
        quantity = np.log2(num_rows / (2**num_columns))
        return quantity


class Clause:
    def __init__(self, clause) -> None:
        self.__clause = clause
        self.bits = self.__clause.free_symbols

    def reduce_space(self):
        variables = list(self.bits)
        values = product(range(2), repeat=len(variables))
        reduced_space = []
        for v in values:
            subs_dict = dict(zip(variables, v))
            subs_expr = self.__clause.subs(subs_dict)
            if simplify(subs_expr) == 0:
                reduced_space.append(v)
        df = pd.DataFrame(reduced_space, columns=variables)
        return BitsTable(df)
