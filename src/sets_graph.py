import rustworkx as rx
from rustworkx.visualization import mpl_draw


class SetsGraph:
    def __init__(self, sets) -> None:
        self.__sets = sets
        self.__graph = rx.PyGraph()
        [self.__graph.add_node(s) for s in self.__sets]
        self.disjoint_sets = []
        self.__get_disjoint_sets()
        self.__remove_repeated_data(self.disjoint_sets)

    def draw(self):
        mpl_draw(self.__graph, with_labels=True, labels=str)

    def __get_disjoint_sets(self):
        nodes = self.__graph.nodes()
        for i in range(len(nodes)):
            for j in range(len(nodes)):
                if i != j:
                    if len(nodes[i].intersection(nodes[j])) > 0:
                        self.__graph.add_edge(i, j, nodes[i].intersection(nodes[j]))
                    else:
                        self.disjoint_sets.append([nodes[i], nodes[j]])

    def __remove_repeated_data(self, data):
        for i in data:
            for j in data:
                if j[::-1] == i:
                    data.remove(j)
