from vqf.preprocessing import create_clauses
from src import Clause, SetsGraph
from src.clause_utils import get_key_by_value


class SpaceEfficientVQF:
    def __init__(self, biprime: int):
        self.p_bits, self.q_bits, self.z_bits, self.simplified_clauses = create_clauses(
            biprime, apply_preprocessing=True, verbose=False
        )

        self.__eff_clauses = dict(self.__get_space_eff_clauses())
        self.best_superposition_table = next(self.__get_best_bits_table())
        self.__disjoint_sets = self.__get_disjoint_sets()
        self.superposition_tables = self.__get_superposition_tables()

    def __get_space_eff_clauses(self):
        for c in self.simplified_clauses:
            if c != 0:
                c = Clause(c)
                pq_limit = len(c.pq_part.free_symbols)
                if pq_limit <= 16:
                    table = c.reduce_space().remove_carry_bits()
                    bits = table.bits
                    yield table, bits
                else:
                    del c
                    continue
        

    def __get_best_bits_table(self):
        min_r = float("inf")  # Initialize min_r to infinity
        best_table = None  # Initialize best_table to None

        for table in self.__eff_clauses:
            r = table.calc_r()
            if r < min_r:
                min_r = r
                best_table = table.table
                yield best_table  # Use generator to yield the best table instead of storing in memory
        return best_table

    def __get_disjoint_sets(self):
        pq_bits = list(self.__eff_clauses.values())
        self.graph = SetsGraph(pq_bits)
        disjoint_sets = self.graph.disjoint_sets
        return disjoint_sets

    def __get_superposition_tables(self):
        superposition_tables = []
        if len(self.__disjoint_sets) == 0:
            superposition_tables.append(self.best_superposition_table)
        else:
            for s in self.__disjoint_sets:
                table = get_key_by_value(self.__eff_clauses, s).table
                superposition_tables.append(table)
        return superposition_tables
