"""Driver for the classical factorization search-space reduction.

Implements the VQF clause-preprocessing pipeline end to end for a biprime: it
generates and simplifies the multiplication clauses, finds the bits whose value
is forced (known bits), builds the per-clause feasible-assignment tables and
their compression ratios, selects a non-overlapping (disjoint) set of the
most-reducing tables via :class:`~src.preprocessing.bits_network.BitSetGraph`, and
exposes the resulting superposition tables.

Those tables define the reduced, clause-feasible search space that the reduced
QAOA initial state is prepared over (see
:mod:`src.qaoa.reduced_ansatz`). This module runs no quantum circuit; it produces
the classical tables the circuits consume. It orchestrates the data primitives
in :mod:`src.preprocessing.clauses`.
"""

from vqf.preprocessing import create_clauses

from src.preprocessing.clauses import Clause
from src.preprocessing.bits_network import BitSetGraph
from src.preprocessing.utils import (convert_elements_to_str, convert_to_dataframe,
                              create_merged_dict, find_non_matching_values,
                              get_key_by_value, merge_dictionaries)


class SearchSpaceReducer:
    """Classical preprocessing that reduces the factorization search space.

    Applies the VQF clause-preprocessing rules to a biprime: it simplifies the
    multiplication clauses, finds known/constrained bits, and builds the
    superposition tables that define the reduced (clause-feasible) search space
    the reduced QAOA initial state is prepared over. It does not run any quantum
    circuit; it produces the classical tables those circuits consume.
    """

    def __init__(self, biprime: int):
        """Initialize the instance variables of the class.

        Args:
            biprime: the biprime value used to generate the clauses.
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

        self.known_bits = self.__get_known_bits()
        self.selected_clauses = []
        self.__reduced_clause_tables = dict(self.__get_reduced_clause_tables())
        self.__compression_ratios = dict(self.__get_compression_ratios())
        # Calculate the best superposition table based on the selected clauses
        self.best_superposition_table = self.__get_best_superposition_table()

        # Calculate the disjoint sets of pq-bits based on the selected clauses
        self.__disjoint_sets = self.__get_disjoint_sets()

        # Calculate the superposition tables based on the disjoint sets
        self.superposition_tables = self.__get_superposition_tables()
        self.table_clause_dict = dict(self.__get_table_clause_dict())

    def __get_known_bits(self):
        p_bits = create_merged_dict(self.p_bits, self.p_bits_simple)
        q_bits = create_merged_dict(self.q_bits, self.q_bits_simple)

        known_p_bits = find_non_matching_values(p_bits)
        known_q_bits = find_non_matching_values(q_bits)

        known_bits = merge_dictionaries(known_p_bits, known_q_bits)
        known_bits = convert_to_dataframe(known_bits, columns=["Known Bit", "Value"])
        return known_bits

    def __get_table_clause_dict(self):
        for table in self.superposition_tables:
            for c in self.selected_clauses:
                set1 = convert_elements_to_str(c.pq_part.free_symbols)
                set2 = convert_elements_to_str(set(table.table.columns))
                if set1 == set2:
                    yield c, table

    def __get_compression_ratios(self):
        for table, bits in self.__reduced_clause_tables.items():
            r = table.compression_ratio()
            yield r, bits

    def __get_reduced_clause_tables(self):
        """Select a subset of the simplified clauses and reduce their space.

        Yields:
            a ``(reduced_table, bits)`` tuple for each selected clause, where
            ``bits`` is the table's bit representation.
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
        """Calculate the best superposition table based on the selected clauses.

        Returns:
            the best superposition table.
        """
        min_r = float("inf")  # Initialize min_r to infinity
        best_table = None  # Initialize best_table to None

        for table in self.__reduced_clause_tables:
            r = table.compression_ratio()
            if r < min_r:
                min_r = r
                best_table = table
        return best_table

    def __get_disjoint_sets(self):
        """Calculate the disjoint sets of pq-bits based on the selected clauses.

        Returns:
            the disjoint sets of pq-bits.
        """
        self.graph = BitSetGraph(self.__compression_ratios)
        disjoint_sets = self.graph.disjoint_sets
        return disjoint_sets

    def __get_superposition_tables(self):
        """Calculate the superposition tables based on the disjoint sets.

        Returns:
            the superposition tables.
        """
        superposition_tables = []
        if len(self.__disjoint_sets) == 0:
            superposition_tables.append(self.best_superposition_table)
        else:
            for s in self.__disjoint_sets:
                table = get_key_by_value(self.__reduced_clause_tables, s)
                superposition_tables.append(table)
        return superposition_tables
