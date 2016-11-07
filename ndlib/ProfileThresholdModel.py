from DiffusionModel import DiffusionModel
import numpy as np
import networkx as nx

__author__ = "Giulio Rossetti"
__email__ = "giulio.rossetti@gmail.com"


class ProfileThresholdModel(DiffusionModel):
    """

    """

    def iteration(self):
        """

        """

        actual_status = {node: nstatus for node, nstatus in self.status.iteritems()}

        for u in self.graph.nodes():
            if actual_status[u] == 1:
                continue

            neighbors = self.graph.neighbors(u)
            if isinstance(self.graph, nx.DiGraph):
                neighbors = self.graph.predecessors(u)

            infected = 0
            for v in neighbors:
                infected += self.status[v]

            if infected > 0:
                eventp = np.random.random_sample()
                if eventp >= self.params['nodes']['profile'][u]:
                    infected_ratio = float(infected)/len(neighbors)
                    if infected_ratio >= self.params['nodes']['threshold'][u]:
                        actual_status[u] = 1

        self.status = actual_status
        self.actual_iteration += 1

        return self.actual_iteration, actual_status