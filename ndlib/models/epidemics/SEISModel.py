from ..DiffusionModel import DiffusionModel
import numpy as np
import future.utils

__author__ = "Elisa Salatti"
__license__ = "BSD-2-Clause"


class SEISModel(DiffusionModel):
    """
       Model Parameters to be specified via ModelConfig

       :param beta: The infection rate (float value in [0,1])
       :param lambda: The recovery rate (float value in [0,1])
    """

    def __init__(self, graph):
        """
             Model Constructor

             :param graph: A networkx graph object
         """
        super(self.__class__, self).__init__(graph)
        self.available_statuses = {
            "Susceptible": 0,
            "Exposed": 2,
            "Infected": 1
        }

        self.parameters = {
            "model": {
                "alpha": {
                    "descr": "Incubation period",
                    "range": [0, 1],
                    "optional": False},
                "beta": {
                    "descr": "Infection rate",
                    "range": [0, 1],
                    "optional": False},
                "lambda": {
                    "descr": "Recovery rate",
                    "range": [0, 1],
                    "optional": False
                }
            },
            "nodes": {},
            "edges": {},
        }

        self.name = "SEIS"
        self.progress = {}

    def iteration(self, node_status=True):
        """
        Execute a single model iteration

        :return: Iteration_id, Incremental node status (dictionary node->status)
        """
        self.clean_initial_status(self.available_statuses.values())

        actual_status = {node: nstatus for node, nstatus in future.utils.iteritems(self.status)}

        if self.actual_iteration == 0:
            self.actual_iteration += 1
            delta, node_count, status_delta = self.status_delta(actual_status)
            if node_status:
                return {"iteration": 0, "status": actual_status.copy(),
                        "node_count": node_count.copy(), "status_delta": status_delta.copy()}
            else:
                return {"iteration": 0, "status": {},
                        "node_count": node_count.copy(), "status_delta": status_delta.copy()}

        for u in self.graph.nodes:

            u_status = self.status[u]
            eventp = np.random.random_sample()
            neighbors = self.graph.neighbors(u)
            if self.graph.directed:
                neighbors = self.graph.predecessors(u)

            if u_status == 0:  # Susceptible
                infected_neighbors = len([v for v in neighbors if self.status[v] == 2 or self.status[v] == 1])
                if eventp < self.params['model']['beta'] * infected_neighbors:
                    actual_status[u] = 2  # Exposed
                    self.progress[u] = 0

            elif u_status == 2:
                if self.progress[u] < 1:
                    self.progress[u] += self.params['model']['alpha']
                else:
                    actual_status[u] = 1  # Infected
                    del self.progress[u]

            elif u_status == 1:
                if eventp < self.params['model']['lambda']:
                    actual_status[u] = 0  # Susceptible

        delta, node_count, status_delta = self.status_delta(actual_status)
        self.status = actual_status
        self.actual_iteration += 1

        if node_status:
            return {"iteration": self.actual_iteration - 1, "status": delta.copy(),
                    "node_count": node_count.copy(), "status_delta": status_delta.copy()}
        else:
            return {"iteration": self.actual_iteration - 1, "status": {},
                    "node_count": node_count.copy(), "status_delta": status_delta.copy()}
