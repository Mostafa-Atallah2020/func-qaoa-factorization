import networkx as nx
import matplotlib.pyplot as plt
import itertools


class SetsGraph:
    def __init__(self, sets_r_values) -> None:
        """
        Initializes a SetsGraph object.

        Args:
            sets (list): A list of sets to be represented as nodes in the graph.
        """
        self.__sets = list(sets_r_values.values())
        self.__r_vals = list(sets_r_values.keys())
        self.__graph = nx.Graph()
        self.__add_nodes()
        self.__add_edges()

        self.disjoint_sets = []
        self.__get_disjoint_sets()

    def __get_disjoint_sets(self):
        """
        Finds the maximum independent set of nodes in the graph while minimizing the r_vals.

        Returns:
            list: A list of sets representing the maximum independent set of nodes.
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
                    r_vals.append(self.__r_vals[el])

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
        """
        Draws the graph with labeled nodes.
        """
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
        """
        Adds nodes to the graph and labels them with their corresponding set.
        """
        # Add nodes to the graph and label them with their corresponding set
        for i, s in enumerate(self.__sets):
            self.__graph.add_node(i, set=s)

    def __add_edges(self):
        """
        Adds edges to the graph between nodes that have intersecting sets.
        """
        for i in range(len(self.__sets)):
            for j in range(i + 1, len(self.__sets)):
                if self.__sets[i].intersection(self.__sets[j]):
                    self.__graph.add_edge(i, j)
