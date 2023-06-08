from vqf.preprocessing import create_clauses
from src import Clause, SetsGraph


class SpaceEfficientVQF:
    def __init__(self, biprime: int):
        self.p_bits, self.q_bits, self.z_bits, self.simplified_clauses = create_clauses(
            biprime, apply_preprocessing=True, verbose=False
        )

        self.__eff_clauses = self.__get_space_eff_clauses()
        self.best_superposition_table = self.__get_best_bits_table()
        self.__disjoint_sets = self.__get_disjoint_sets()
        self.superposition_tables = self.__get_superposition_tables()

    def __get_space_eff_clauses(self):
        eff_clauses = {}
        for c in self.simplified_clauses:
            if c != 0:
                c = Clause(c)
                table = c.reduce_space().remove_carry_bits()
                bits = table.bits
                eff_clauses[table] = bits
        return eff_clauses

    def __get_best_bits_table(self):
        min_r = float("inf")  # Initialize min_r to infinity
        best_table = None  # Initialize best_table to None
        tables = self.__eff_clauses.keys()

        for t in tables:
            r = t.calc_r()
            if r < min_r:
                min_r = r
                best_table = t.table

        return best_table

    def __get_key_by_value(self, dictionary, value):
        for key, val in dictionary.items():
            if val == value:
                return key
        return None  # Value not found

    def __get_disjoint_sets(self):
        pq_bits = list(self.__eff_clauses.values())
        self.graph = SetsGraph(pq_bits)
        disjoint_sets = self.graph.disjoint_sets
        return disjoint_sets

    def __get_superposition_tables(self):
        superposition_tables = []
        if len(self.__disjoint_sets) == 0:
            best_clause = self.__get_best_bits_table()
            superposition_tables.append(best_clause)

        else:
            for s in self.__disjoint_sets:
                table = self.__get_key_by_value(self.__eff_clauses, s).table
                superposition_tables.append(table)

        return superposition_tables