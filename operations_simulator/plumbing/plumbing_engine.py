import networkx as nx
import matplotlib.pyplot as plt
import config

class PlumbingEngine:
    '''engine that represents a plumbing system'''
    def __init__(self, components=[], mapping={}, initial_nodes={}, initial_states={}):
        self.time_resolution = config.DEFAULT_TIME_RESOLUTION
        self.plumbing_graph = nx.MultiDiGraph()
        self.load_graph(components, mapping, initial_nodes, initial_states)

    def load_graph(self, components, mapping, initial_nodes, initial_states):
        '''load in a graph to the PlumbingEngine'''
        self.components_list = components
        self.mapping = mapping
        self.plumbing_graph.clear()

        # populating the graph by mapping from components
        for component in self.components_list:
            component_graph = component.component_graph
            nodes_map = self.mapping[component.name]
            for start_node, end_node, edge_key in component_graph.edges(keys=True):
                self.plumbing_graph.add_edge(nodes_map[start_node], nodes_map[end_node], edge_key)
    
        # set a time resolution based on lowest teq (highest FC) if graph isn't empty
        if not nx.classes.function.is_empty(self.plumbing_graph):
            max_fc = 4.5 / (config.DEFAULT_TIME_RESOLUTION * config.DEFAULT_RESOLUTION_SCALE)
            for component in self.components_list:
                component_states = component.states
                for state in component_states.values():
                    for fc in state.values():
                        if fc > max_fc:
                            max_fc = fc
            self.time_resolution = 4.5 / (max_fc * config.DEFAULT_RESOLUTION_SCALE)

        # assign default pressure value of 0 to every node
        nx.classes.function.set_node_attributes(self.plumbing_graph, 0, 'pressure')

        # assign initial pressures to given nodes
        for node_name, node_pressure in initial_nodes.items():
            self.plumbing_graph.nodes[node_name]['pressure'] = node_pressure

        # assign initial states to edges
        # NOTE: this will probably get moved into its own toggle_component() function
        for component in self.components_list:
            component_map = self.mapping[component.name] # map from component to graph node for this component
            state_id = initial_states[component.name]
            component.current_state = state_id
            state_edges_component = component.states[state_id] # dict of {edges:FC} with component node names

            # create new dict keyed by graph edges rather than component ones
            state_edges_graph = {}
            for cedge in state_edges_component.keys():
                cstart_node, cend_node, key = cedge
                new_edge = (component_map[cstart_node], component_map[cend_node], key)
                state_edges_graph[new_edge] = state_edges_component[cedge]

            nx.classes.function.set_edge_attributes(self.plumbing_graph, state_edges_graph, 'FC')

class PlumbingComponent:
    def __init__(self, name, states, edge_list):
        self.name = name
        self.component_graph = nx.MultiDiGraph(edge_list)
        self.states = states
        self.current_state = ''

        # convert provided teq values into FC values
        for state in self.states.values():
            for edge in state:
                if state[edge] == 0:
                    state[edge] = config.FC_MAX
                elif state[edge] == config.CLOSED_KEYWORD:
                    state[edge] = 0
                else:
                    state[edge] = 4.5/state[edge]


pc1_states = {
    'open' : {
        (1, 2, 'A1') : 0.001,
        (2, 1, 'A2') : 0.001
        },
    'closed' : {
        (1, 2, 'A1') : 1000,
        (2, 1, 'A2') : 1000
        }
    }
pc1_edges = [(1, 2, 'A1'), (2, 1, 'A2')]
pc1 = PlumbingComponent('valve1', pc1_states, pc1_edges)

pc2_states = {
    'open' : {
        (1, 2, 'B1') : 0.001,
        (2, 1, 'B2') : 0.001
        },
    'closed' : {
        (1, 2, 'B1') : 1000,
        (2, 1, 'B2') : 1000
        }
    }
pc2_edges = [(1, 2, 'B1'), (2, 1, 'B2')]
pc2 = PlumbingComponent('valve2', pc2_states, pc2_edges)

component_mapping = {
    'valve1' : {
        1 : 1,
        2 : 2
    },
    'valve2' : {
        1 : 2,
        2 : 3
    }
}

pressures = {3 : 100}
default_states = {'valve1' : 'closed', 'valve2' : 'open'}
plumb = PlumbingEngine([pc1, pc2], component_mapping, pressures, default_states)
print(plumb.plumbing_graph.edges(data=True, keys=True))
print(plumb.plumbing_graph.nodes(data=True))
