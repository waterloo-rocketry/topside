import copy

import networkx as nx

import topside.plumbing.exceptions as exceptions
import topside.plumbing.invalid_reasons as invalid
import topside.plumbing.plumbing_utils as utils


class PlumbingEngine:
    '''Engine that represents a plumbing system'''

    def __init__(self, components=None, mapping=None, initial_nodes=None, initial_states=None):
        if not components:
            components = {}
        if not mapping:
            mapping = {}
        if not initial_nodes:
            initial_nodes = {}
        if not initial_states:
            initial_states = {}

        self.time_resolution = utils.DEFAULT_TIME_RESOLUTION_MICROS
        self.plumbing_graph = nx.MultiDiGraph()
        self.error_set = set()
        self.valid = True
        self.load_graph(components, mapping, initial_nodes, initial_states)

    def load_graph(self, components, mapping, initial_nodes, initial_states):
        '''Load in a graph to the PlumbingEngine'''
        self.component_dict = copy.deepcopy(components)
        self.mapping = copy.deepcopy(mapping)
        self.plumbing_graph.clear()
        self.error_set.clear()
        initial_nodes = copy.deepcopy(initial_nodes)
        initial_states = copy.deepcopy(initial_states)

        # Populating the graph by mapping from components
        for name, component in self.component_dict.items():
            nodes_map = self.mapping.get(name)

            if nodes_map is None:
                error = invalid.InvalidComponentName(
                    f"Component with name '{name}' not found in provided mapping dict.", name)
                invalid.add_error(error, self.error_set)
                continue

            self._add_component(component, nodes_map)

        # Set a time resolution based on lowest teq (highest FC) if graph isn't empty
        if not nx.classes.function.is_empty(self.plumbing_graph):
            for component_name in self.component_dict.keys():
                self._set_time_resolution(component_name)

        # Assign initial pressure of 0
        for node in self.plumbing_graph.nodes():
            self.set_pressure(node, 0)

        # Assign initial pressures to given nodes
        for node_name, node_pressure in initial_nodes.items():
            try:
                self.set_pressure(node_name, node_pressure)
            except exceptions.BadInputError as err:
                error = invalid.InvalidNodePressure(
                    err.args[0], node_name)
                self.error_set.add(error)

        # Assign initial states to edges
        for component_name in self.component_dict.keys():
            if initial_states.get(component_name) is None:
                error = invalid.InvalidComponentName(
                    f"Component '{component_name}' state not found in initial states dict.",
                    component_name)
                self.error_set.add(error)
                continue
            state_id = initial_states[component_name]
            self.set_component_state(component_name, state_id)

        self.valid = len(self.error_set) == 0

    def set_component_state(self, component_name, state_id):
        '''Change a component's state on the main graph'''
        if self.mapping.get(component_name) is None:
            raise exceptions.BadInputError(
                f"Component '{component_name}' not found in mapping dict.")

        # Map from component to graph node for this component
        component_map = self.mapping[component_name]
        component = self.component_dict[component_name]

        if component.states.get(state_id) is None:
            raise exceptions.BadInputError(
                f"State '{state_id}' not found in {component_name} states dict.")

        # Dict of {edges:FC} with component node names
        state_edges_component = component.states[state_id]

        component.current_state = state_id

        # Create new dict keyed by graph edges rather than component ones
        state_edges_graph = {}
        for cedge in state_edges_component.keys():
            cstart_node, cend_node, key = cedge

            both_nodes_valid = True
            if component_map.get(cstart_node) is None:
                error = invalid.InvalidComponentNode(
                    f"Component '{component.name}', node {cstart_node} not found in mapping dict.",
                    component.name, cstart_node)
                invalid.add_error(error, self.error_set)
                both_nodes_valid = False
            if component_map.get(cend_node) is None:
                error = invalid.InvalidComponentNode(
                    f"Component '{component.name}', node {cend_node} not found in mapping dict.",
                    component.name, cend_node)
                invalid.add_error(error, self.error_set)
                both_nodes_valid = False

            if both_nodes_valid:
                new_edge = (component_map[cstart_node], component_map[cend_node],
                            component_name + '.' + key)
                state_edges_graph[new_edge] = state_edges_component[cedge]

        # Set FC on main graph according to new dict
        nx.classes.function.set_edge_attributes(self.plumbing_graph, state_edges_graph, 'FC')

    def _set_time_resolution(self, component_name):
        '''Given a component, set a time resolution based on its lowest teq (highest FC)'''
        max_fc = utils.teq_to_FC(self.time_resolution * utils.DEFAULT_RESOLUTION_SCALE)
        component_states = (self.component_dict[component_name]).states
        for state in component_states.values():
            for fc in state.values():
                # Prevent open valves from always giving the minimum teq as time resolution
                if fc != utils.FC_MAX and fc > max_fc:
                    max_fc = fc
        if max_fc:
            self.time_resolution = int(utils.FC_to_teq(max_fc) / utils.DEFAULT_RESOLUTION_SCALE)

    def _add_component(self, component, mapping):
        name = component.name
        component_graph = component.component_graph

        # Updating the plumbing engine's records about itself with new component
        self.component_dict[name] = component
        self.mapping[name] = copy.deepcopy(mapping)
        self._set_time_resolution(name)

        # Adding and connecting new nodes to main graph as necessary
        for start_node, end_node, edge_key in component_graph.edges(keys=True):
            both_nodes_valid = True

            if mapping.get(start_node) is None:
                error = invalid.InvalidComponentNode(
                    f"Component '{name}', node {start_node} not found in mapping dict.",
                    name, start_node)
                invalid.add_error(error, self.error_set)
                both_nodes_valid = False
            if mapping.get(end_node) is None:
                error = invalid.InvalidComponentNode(
                    f"Component '{name}', node {end_node} not found in mapping dict.",
                    name, end_node)
                invalid.add_error(error, self.error_set)
                both_nodes_valid = False

            if both_nodes_valid:
                self.plumbing_graph.add_edge(
                    mapping[start_node], mapping[end_node], component.name + '.' + edge_key)
        self.valid = len(self.error_set) == 0

    def add_component(self, component, mapping, state_id, pressures=None):
        '''Adds a component to the main plumbing graph according to provided specifications'''
        if not pressures:
            pressures = {}

        pressures = copy.deepcopy(pressures)
        for node in mapping.values():
            if not pressures.get(node) and node not in self.plumbing_graph:
                pressures[node] = 0

        self._add_component(component, mapping)
        self.set_component_state(component.name, state_id)

        for node_name, node_pressure in pressures.items():
            self.set_pressure(node_name, node_pressure)

    def is_valid(self):
        '''Returns whether the plumbing engine is valid'''
        return self.valid

    def remove_component(self, component_name):
        '''Removes component and associated errors'''
        # Check validity of provided component name
        if self.component_dict.get(component_name) is None:
            raise exceptions.BadInputError(
                f"Component with name {component_name} not found in component dict.")

        component = self.component_dict[component_name]
        og_name = component_name  # In case of errors
        component_name = component.name
        mapping = self.mapping[component_name]

        # Remove all edges associated with component
        to_remove = []
        for edge in self.plumbing_graph.edges(keys=True):
            if component_name in edge[2]:
                to_remove.append(edge)
        self.plumbing_graph.remove_edges_from(to_remove)

        # Remove unconnected (redundant) nodes
        to_remove = []
        for node in self.plumbing_graph.nodes():
            if not list(self.plumbing_graph.neighbors(node)):
                to_remove.append(node)

        self.plumbing_graph.remove_nodes_from(to_remove)

        # Self info housekeeping
        self._resolve_errors(og_name)
        if self.mapping.get(component_name):
            del self.mapping[component_name]
        del self.component_dict[og_name]
        self.time_resolution = utils.DEFAULT_TIME_RESOLUTION_MICROS
        for name in self.component_dict.keys():
            self._set_time_resolution(name)
        self.valid = len(self.error_set) == 0

    def _resolve_errors(self, component_name):
        '''Resolve all errors associated with a certain component'''
        component = self.component_dict[component_name]

        # Find all errors associated with a component
        to_remove = []
        for error in self.error_set:
            if hasattr(error, 'component_name') and error.component_name == component_name:
                to_remove.append(error)
            elif hasattr(error, 'node_name'):
                mapped_nodes = [self.mapping[component][node] for node in component.component_graph]
                if error.node_name in mapped_nodes:
                    to_remove.append(error)

        for error in self.error_set:
            if isinstance(error, invalid.DuplicateError) and error.original_error in to_remove:
                to_remove.append(error)

        for error in to_remove:
            self.error_set.remove(error)

    def reverse_orientation(self, component_name):
        '''Reverse direction of suitable components, such as check valves'''
        if self.component_dict.get(component_name) is None:
            raise exceptions.BadInputError(
                f"Component '{component_name}' not found in component dict.")

        component = self.component_dict[component_name]

        if len(component.component_graph.edges()) != 2:
            raise exceptions.InvalidComponentError(
                "Component must only have two edges to be automatically reversed.\n"
                "Consider adjusting direction manually.")

        # Reverse orientation by switching direction of FCs
        to_switch = [e for e in self.plumbing_graph.edges(keys=True) if component_name in e[2]]
        edge1 = list(to_switch[0])
        edge2 = list(to_switch[1])

        temp = self.plumbing_graph.edges[edge1]['FC']
        self.plumbing_graph.edges[edge1]['FC'] = self.plumbing_graph.edges[edge2]['FC']
        self.plumbing_graph.edges[edge2]['FC'] = temp

    def set_pressure(self, node_name, pressure):
        '''Sets pressure at given node'''
        if not isinstance(pressure, (int, float)):
            raise exceptions.BadInputError(f"Pressure {pressure} must be a number.")
        if pressure < 0:
            raise exceptions.BadInputError(f"Negative pressure {pressure} not allowed.")
        if not node_name in self.plumbing_graph:
            raise exceptions.BadInputError(f"Node {node_name} not found in graph.")

        self.plumbing_graph.nodes[node_name]['pressure'] = pressure

    def set_teq(self, component_name, which_edge):
        '''Sets teq at given dict of edges for one component'''
        if self.component_dict.get(component_name) is None:
            raise exceptions.BadInputError(
                f"Component name '{component_name}' not found in component dict.")

        component = self.component_dict[component_name]
        which_edge = copy.deepcopy(which_edge)

        for state_id, edge_dict in which_edge.items():
            if component.states.get(state_id) is None:
                raise exceptions.BadInputError(
                    f"State '{state_id}' not found in component {component_name}'s states dict.")

            for edge, teq in edge_dict.items():
                teq = utils.s_to_micros(teq)
                if teq < utils.TEQ_MIN:
                    raise exceptions.BadInputError(
                        f"Provided teq {utils.micros_to_s(teq)} (component '{component_name}',"
                        f" state '{state_id}', edge {edge}) too low. "
                        f"Minimum teq is {utils.micros_to_s(utils.TEQ_MIN)}s.")
                if component.states[state_id].get(edge) is None:
                    raise exceptions.BadInputError(
                        f"State '{state_id}', edge {edge} not found in component"
                        f" {component_name}'s states dict.")

                component.states[state_id][edge] = utils.teq_to_FC(teq)

        # Update teq changes on main plumbing graph
        if component.current_state in which_edge.keys():
            self.set_component_state(component_name, component.current_state)

        self._set_time_resolution(component_name)
