import networkx as nx

import operations_simulator.plumbing.plumbing_utils as utils


class PlumbingEngine:
    '''Engine that represents a plumbing system'''

    def __init__(self, components={}, mapping={}, initial_nodes={}, initial_states={}):
        self.time_resolution = utils.DEFAULT_TIME_RESOLUTION_MICROS
        self.plumbing_graph = nx.MultiDiGraph()
        self.load_graph(components, mapping, initial_nodes, initial_states)

    def load_graph(self, components, mapping, initial_nodes, initial_states):
        '''Load in a graph to the PlumbingEngine'''
        self.component_dict = components
        self.mapping = mapping
        self.plumbing_graph.clear()

        # Populating the graph by mapping from components
        for name, component in self.component_dict.items():
            component_graph = component.component_graph
            nodes_map = self.mapping.get(name)
            if nodes_map is None:
                raise KeyError(f"Component with name '{name}' not found in provided mapping dict.")
            for start_node, end_node, edge_key in component_graph.edges(keys=True):
                if nodes_map.get(start_node) is None:
                    raise KeyError(
                        f"Component '{name}', node {start_node} not found in mapping dict.")
                if nodes_map.get(end_node) is None:
                    raise KeyError(
                        f"Component '{name}', node {end_node} not found in mapping dict.")
                self.plumbing_graph.add_edge(
                    nodes_map[start_node], nodes_map[end_node], edge_key)

        # Set a time resolution based on lowest teq (highest FC) if graph isn't empty
        if not nx.classes.function.is_empty(self.plumbing_graph):
            for component_name in self.component_dict.keys():
                self._set_time_resolution(component_name)

        # Assign default pressure value of 0 to every node
        nx.classes.function.set_node_attributes(
            self.plumbing_graph, 0, 'pressure')

        # Assign initial pressures to given nodes
        for node_name, node_pressure in initial_nodes.items():
            if self.plumbing_graph.nodes.get(node_name) is None:
                raise KeyError(f"Node {node_name} not found in initial node pressures dict.")
            self.plumbing_graph.nodes[node_name]['pressure'] = node_pressure

        # Assign initial states to edges
        for component_name in self.component_dict.keys():
            if initial_states.get(component_name) is None:
                raise KeyError(
                    f"Component `{component_name}` state not found in initial states dict.")
            state_id = initial_states[component_name]
            self.set_component_state(component_name, state_id)

    def set_component_state(self, component_name, state_id):
        '''Change a component's state on the main graph'''
        if self.mapping.get(component_name) is None:
            raise KeyError(f"Component '{component_name}' not found in mapping dict.")

        # Map from component to graph node for this component
        component_map = self.mapping[component_name]
        component = self.component_dict[component_name]

        if component.states.get(state_id) is None:
            raise KeyError(f"State '{state_id}' not found.")

        # Dict of {edges:FC} with component node names
        state_edges_component = component.states[state_id]

        component.current_state = state_id

        # Create new dict keyed by graph edges rather than component ones
        state_edges_graph = {}
        for cedge in state_edges_component.keys():
            cstart_node, cend_node, key = cedge
            new_edge = (component_map[cstart_node], component_map[cend_node], key)
            state_edges_graph[new_edge] = state_edges_component[cedge]

        # Set FC on main graph according to new dict
        nx.classes.function.set_edge_attributes(self.plumbing_graph, state_edges_graph, 'FC')

    def _set_time_resolution(self, component_name):
        '''Set a time resolution based on lowest teq (highest FC)'''
        max_fc = utils.teq_to_FC(self.time_resolution * utils.DEFAULT_RESOLUTION_SCALE)
        component_states = (self.component_dict[component_name]).states
        for state in component_states.values():
            for fc in state.values():
                # Prevent open valves from always giving the minimum teq as time resolution
                if fc != utils.FC_MAX and fc > max_fc:
                    max_fc = fc
        if max_fc:
            self.time_resolution = int(utils.FC_to_teq(max_fc) / utils.DEFAULT_RESOLUTION_SCALE)


class PlumbingComponent:
    '''Represents a discrete plumbing component, such as a tank or valve'''

    def __init__(self, name, states, edge_list):
        self.name = name
        self.component_graph = nx.MultiDiGraph(edge_list)
        self.states = states
        self.current_state = None

        # Convert provided teq values into FC values
        for state in self.states.values():
            for edge in state:
                if isinstance(state[edge], (float, int)):
                    state[edge] = utils.s_to_micros(state[edge])

                # TODO(jacob/wendi): Look into eventually implementing
                # this with datetime.timedelta object.
                state[edge] = utils.teq_to_FC(state[edge])

                # NOTE: This error may have to be changed, depending on
                # how the application handles bypassable warnings.
                if state[edge] > utils.FC_MAX:
                    raise ValueError(
                        f"Provided teq value too low, minimum value is: {utils.micros_to_s(utils.TEQ_MIN)}s")
