"""Pick a non-overlapping set of bit-groups to reduce the search space.

The clause preprocessing yields several candidate bit-groups (each a set of
``p``/``q`` bits a clause constrains, with an associated compression ratio).
To prepare their reduced superpositions independently, the chosen groups must
be pairwise **disjoint**: two groups that share a bit cannot both fix that
qubit. Selecting the most-reducing disjoint groups is a maximum-(weighted-)
independent-set problem on the "conflict graph" whose nodes are the bit-groups
and whose edges join any two groups that intersect.

This module models that conflict graph (:class:`BitSetGraph`) and extracts the
disjoint groups that minimize the summed compression ratio. The graph also
supports a :meth:`BitSetGraph.draw` visualization; the selection itself is a
direct brute-force over group intersections.
"""

import itertools

import matplotlib.pyplot as plt
import networkx as nx


class BitSetGraph:
    """Graph over bit-sets used to pick disjoint superposition tables.

    Each compression ratio maps to a set of bits; those sets become the graph's
    nodes, with edges between any two sets that intersect.
    """

    def __init__(self, sets_by_ratio) -> None:
        """Initialize a BitSetGraph object.

        Args:
            sets_by_ratio: maps each compression ratio to its set of bits; the
                sets become nodes in the graph.
        """
        self.__sets = list(sets_by_ratio.values())
        self.__ratios = list(sets_by_ratio.keys())
        self.__graph = nx.Graph()
        self.__add_nodes()
        self.__add_edges()

        self.disjoint_sets = []
        self.__get_disjoint_sets()

    def __get_disjoint_sets(self):
        """Find the maximum independent set of nodes while minimizing the r_vals.

        Returns:
            a list of sets representing the maximum independent set of nodes.
        """
        # Generate all possible combinations of nodes
        all_nodes = set(range(len(self.__sets)))
        independent_sets = []
        max_independent_set = []
        min_r_vals = float("inf")

        # Brute-force algorithm to find the maximum independent set with minimized r_vals
        for r in range(len(self.__sets) + 1):
            for nodes in itertools.combinations(all_nodes, r):
                is_independent = True

                r_vals = []
                for el in nodes:
                    r_vals.append(self.__ratios[el])

                for pair in itertools.combinations(nodes, 2):
                    set1 = self.__sets[pair[0]]
                    set2 = self.__sets[pair[1]]
                    if set1.intersection(set2):
                        is_independent = False
                        break

                if is_independent:
                    independent_sets.append(nodes)
                    if sum(r_vals) < min_r_vals:
                        max_independent_set = nodes
                        min_r_vals = sum(r_vals)

        [self.disjoint_sets.append(self.__sets[node]) for node in max_independent_set]

    def draw(self):
        """Draw the graph with labeled nodes."""
        # Draw the graph with labeled nodes
        pos = nx.spring_layout(self.__graph)
        nx.draw(
            self.__graph,
            pos,
            with_labels=False,
            node_size=500,
            node_color="lightblue",
            font_weight="bold",
        )

        # Add labels for each node representing its corresponding set
        labels = nx.get_node_attributes(self.__graph, "set")
        nx.draw_networkx_labels(self.__graph, pos, labels=labels)

        # Show the graph
        plt.show()

    def __add_nodes(self):
        """Add nodes to the graph and label them with their corresponding set."""
        # Add nodes to the graph and label them with their corresponding set
        for i, s in enumerate(self.__sets):
            self.__graph.add_node(i, set=s)

    def __add_edges(self):
        """Add edges to the graph between nodes that have intersecting sets."""
        for i in range(len(self.__sets)):
            for j in range(i + 1, len(self.__sets)):
                if self.__sets[i].intersection(self.__sets[j]):
                    self.__graph.add_edge(i, j)
