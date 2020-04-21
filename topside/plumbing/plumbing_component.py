import copy

import networkx as nx

import topside.plumbing.invalid_reasons as invalid
import topside.plumbing.plumbing_utils as utils


class PlumbingComponent:
    '''Represents a discrete plumbing component, such as a tank or valve'''

    def __init__(self, name, states, edge_list):
        self.name = name
        self.component_graph = nx.MultiDiGraph(edge_list)
        self.states = copy.deepcopy(states)
        self.current_state = None
        self.error_set = set()

        # Convert provided teq values into FC values
        for state_id, state in self.states.items():
            for edge in state:
                if edge not in edge_list:
                    error = invalid.InvalidComponentEdge(
                        f"Edge '{edge}' not found in provided edge list.", edge)
                    invalid.add_error(error, self.error_set)
                    continue
                og_teq = state[edge]
                if isinstance(state[edge], (float, int)):
                    state[edge] = int(utils.s_to_micros(state[edge]))
                elif isinstance(state[edge], str):
                    if state[edge] != utils.CLOSED_KEYWORD:
                        error = invalid.InvalidTeq(
                            f"Invalid provided teq value ('{state[edge]}'), accepted keyword is: "
                            f"'{utils.CLOSED_KEYWORD}'", self.name, state_id, edge, og_teq)
                        invalid.add_error(error, self.error_set)
                        state[edge] = utils.CLOSED_KEYWORD

                # TODO(jacob/wendi): Look into eventually implementing this with datetime.timedelta.
                state[edge] = utils.teq_to_FC(state[edge])

                if state[edge] > utils.FC_MAX:
                    error = invalid.InvalidTeq(
                        "Provided teq value too low, minimum value is: "
                        f"{utils.micros_to_s(utils.TEQ_MIN)}s", self.name, state_id, edge, og_teq)
                    invalid.add_error(error, self.error_set)
                    state[edge] = utils.FC_MAX

    def is_valid(self):
        return len(self.error_set) == 0
