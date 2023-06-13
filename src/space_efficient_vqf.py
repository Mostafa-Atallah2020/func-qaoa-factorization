from vqf.preprocessing import create_clauses
from src import Clause, SetsGraph
from src.clause_utils import get_key_by_value


class SpaceEfficientVQF:
    """
    A class that implements a space-efficient version of the VQF algorithm.
    """

    def __init__(self, biprime: int):
        """
        Initializes the instance variables of the class.

        Parameters:
        -----------

        `biprime` (`int`): The biprime value used to generate the clauses.
        """
        # Generate the simplified clauses and reduce their space requirements
        self.p_bits, self.q_bits, self.z_bits, self.clauses = create_clauses(
            biprime, apply_preprocessing=False, verbose=False
        )
        (
            self.p_bits_simple,
            self.q_bits_simple,
            self.z_bits_simple,
            self.simplified_clauses,
        ) = create_clauses(biprime, apply_preprocessing=True, verbose=False)
        self.selected_clauses = []
        self.__eff_clauses = dict(self.__get_space_eff_clauses())

        # Calculate the best superposition table based on the selected clauses
        self.best_superposition_table = self.__get_best_superposition_table()

        # Calculate the disjoint sets of pq-bits based on the selected clauses
        self.__disjoint_sets = self.__get_disjoint_sets()

        # Calculate the superposition tables based on the disjoint sets
        self.superposition_tables = self.__get_superposition_tables()

    def __get_space_eff_clauses(self):
        """
        Selects a subset of the simplified clauses and reduces their space requirements.

        Yields:
        -------

        `tuple`: A tuple containing the reduced table and its bit representation.
        """
        for c in self.simplified_clauses:
            if c != 0:
                c = Clause(c)
                n_pq_vars = len(c.pq_part.free_symbols)
                if n_pq_vars <= 16:
                    table = c.reduce_space().remove_carry_bits()
                    bits = table.bits
                    self.selected_clauses.append(c)
                    yield table, bits
                else:
                    del c
                    continue

    def __get_best_superposition_table(self):
        """
        Calculates the best superposition table based on the selected clauses.

        Returns:
        ---------

        `list`: The best superposition table.
        """
        min_r = float("inf")  # Initialize min_r to infinity
        best_table = None  # Initialize best_table to None

        for table in self.__eff_clauses:
            r = table.calc_r()
            if r < min_r:
                min_r = r
                best_table = table.table
        return best_table

    def __get_disjoint_sets(self):
        """
        Calculates the disjoint sets of pq-bits based on the selected clauses.

        Returns:
        --------

        `list`: The disjoint sets of pq-bits.
        """
        pq_bits = list(self.__eff_clauses.values())
        self.graph = SetsGraph(pq_bits)
        disjoint_sets = self.graph.disjoint_sets
        return disjoint_sets

    def __get_superposition_tables(self):
        """
        Calculates the superposition tables based on the disjoint sets.

        Returns:
        --------

        `list`: The superposition tables.
        """
        superposition_tables = []
        if len(self.__disjoint_sets) == 0:
            superposition_tables.append(self.best_superposition_table)
        else:
            for s in self.__disjoint_sets:
                table = get_key_by_value(self.__eff_clauses, s).table
                superposition_tables.append(table)
        return superposition_tables
