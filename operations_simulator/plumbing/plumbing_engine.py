import networkx as nx
import matplotlib.pyplot as plt
import config


def teq_to_FC(teq):
    if teq == 0:
        fc = config.FC_MAX
    elif teq == config.CLOSED_KEYWORD:
        fc = 0
    else:
        fc = 4.5 / teq
    return fc


def FC_to_teq(FC):
    return 4.5 / FC


class PlumbingEngine:
    '''Engine that represents a plumbing system'''

    def __init__(self, components=[], mapping={}, initial_nodes={}, initial_states={}):
        self.time_resolution = config.DEFAULT_TIME_RESOLUTION
        self.plumbing_graph = nx.MultiDiGraph()
        self.load_graph(components, mapping, initial_nodes, initial_states)

    def load_graph(self, components, mapping, initial_nodes, initial_states):
        '''Load in a graph to the PlumbingEngine'''
        self.components_list = components
        self.mapping = mapping
        self.plumbing_graph.clear()

        # Populating the graph by mapping from components
        for component in self.components_list:
            component_graph = component.component_graph
            nodes_map = self.mapping[component.name]
            for start_node, end_node, edge_key in component_graph.edges(keys=True):
                self.plumbing_graph.add_edge(
                    nodes_map[start_node], nodes_map[end_node], edge_key)

        # Set a time resolution based on lowest teq (highest FC) if graph isn't empty
        if not nx.classes.function.is_empty(self.plumbing_graph):
            for component in self.components_list:
                self._set_time_resolution(component)

        # Assign default pressure value of 0 to every node
        nx.classes.function.set_node_attributes(
            self.plumbing_graph, 0, 'pressure')

        # Assign initial pressures to given nodes
        for node_name, node_pressure in initial_nodes.items():
            self.plumbing_graph.nodes[node_name]['pressure'] = node_pressure

        # Assign initial states to edges
        for component in self.components_list:
            state_id = initial_states[component.name]
            self.toggle_component(component, state_id)

    def toggle_component(self, component, state_id):
        '''change a component's state on the main graph'''
        # Map from component to graph node for this component
        component_map = self.mapping[component.name]

        component.current_state = state_id

        # Dict of {edges:FC} with component node names
        state_edges_component = component.states[state_id]

        # Create new dict keyed by graph edges rather than component ones
        state_edges_graph = {}
        for cedge in state_edges_component.keys():
            cstart_node, cend_node, key = cedge
            new_edge = (component_map[cstart_node],
                        component_map[cend_node], key)
            state_edges_graph[new_edge] = state_edges_component[cedge]

        # set FC on main graph according to new dict
        nx.classes.function.set_edge_attributes(
            self.plumbing_graph, state_edges_graph, 'FC')

    def _set_time_resolution(self, component):
        '''set a time resolution based on lowest teq (highest FC)'''
        max_fc = teq_to_FC(self.time_resolution *
                           config.DEFAULT_RESOLUTION_SCALE)
        component_states = component.states
        for state in component_states.values():
            for fc in state.values():
                if fc > max_fc:
                    max_fc = fc
        if max_fc:
            self.time_resolution = FC_to_teq(
                max_fc) / config.DEFAULT_RESOLUTION_SCALE


class PlumbingComponent:
    def __init__(self, name, states, edge_list):
        self.name = name
        self.component_graph = nx.MultiDiGraph(edge_list)
        self.states = states
        self.current_state = ''

        # Convert provided teq values into FC values
        for state in self.states.values():
            for edge in state:
                if state[edge] == 0:
                    state[edge] = config.FC_MAX
                elif state[edge] == config.CLOSED_KEYWORD:
                    state[edge] = 0
                else:
                    state[edge] = teq_to_FC(state[edge])
