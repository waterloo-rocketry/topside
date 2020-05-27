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
        self.load_graph(components, mapping, initial_nodes, initial_states)

    def load_graph(self, components, mapping, initial_nodes, initial_states):
        '''Load in a graph to the PlumbingEngine'''
        self.component_dict = copy.deepcopy(components)
        self.mapping = copy.deepcopy(mapping)
        self.plumbing_graph.clear()
        self.error_set.clear()
        initial_nodes = copy.deepcopy(initial_nodes)
        initial_states = copy.deepcopy(initial_states)

        for name, component in self.component_dict.items():
            if not component.is_valid():
                error = invalid.InvalidComponentName(
                    f"Component with name '{name}' is not valid;"
                    " component cannot be loaded in until errors are resolved.", name)
                invalid.add_error(error, self.error_set)
                continue
            name_valid = True
            if name not in self.mapping:
                error = invalid.InvalidComponentName(
                    f"Component with name '{name}' not found in mapping dict.", name)
                invalid.add_error(error, self.error_set)
                name_valid = False
            if name not in initial_states:
                error = invalid.InvalidComponentName(
                    f"Component '{name}' state not found in initial states dict.",
                    name)
                invalid.add_error(error, self.error_set)
                name_valid = False
            if not name_valid:
                continue

            # Only pass in those pressures that are relevant to the current component
            node_pressures = {}
            for node, pressure in initial_nodes.items():
                if node in self.mapping[name].values():
                    node_pressures[node] = pressure

            self.add_component(
                component, mapping[name], initial_states[name], node_pressures, fail_silently=True)

        # Raise this error (instead of writing to the error set) because there's no intuitive
        # point to remove afterwards. Won't interfere with any engine setup, since it's at the very
        # end of the function call
        for node in initial_nodes.keys():
            if node not in self.plumbing_graph.nodes():
                raise exceptions.BadInputError(f"Node {node} not found in graph.")

    def set_component_state(self, component_name, state_id):
        '''Change a component's state on the main graph'''
        if component_name not in self.mapping:
            raise exceptions.BadInputError(
                f"Component '{component_name}' not found in mapping dict.")

        # Map from component to graph node for this component
        component_map = self.mapping[component_name]
        component = self.component_dict[component_name]

        if state_id not in component.states:
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
            if cstart_node not in component_map:
                error = invalid.InvalidComponentNode(
                    f"Component '{component.name}', node {cstart_node} not found in mapping dict.",
                    component.name, cstart_node)
                invalid.add_error(error, self.error_set)
                both_nodes_valid = False
            if cend_node not in component_map:
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

    def add_component(self, component, mapping, state_id, pressures=None, fail_silently=False):
        '''Adds a component to the main plumbing graph according to provided specifications'''
        if not fail_silently and not component.is_valid():
            raise exceptions.BadInputError(
                "Component not valid; all errors must be resolved before loading in.")

        if not pressures:
            pressures = {}

        name = component.name
        component_graph = component.component_graph

        # Updating the plumbing engine's records about itself with new component
        self.component_dict[name] = component
        self.mapping[name] = copy.deepcopy(mapping)
        self._set_time_resolution(name)

        # Adding and connecting new nodes to main graph as necessary
        for start_node, end_node, edge_key in component_graph.edges(keys=True):
            both_nodes_valid = True

            if start_node not in mapping:
                error_msg = f"Component '{name}', node {start_node} not found in mapping dict."
                if fail_silently:
                    error = invalid.InvalidComponentNode(error_msg, name, start_node)
                    invalid.add_error(error, self.error_set)
                    both_nodes_valid = False
                else:
                    raise exceptions.BadInputError(error_msg)
            if end_node not in mapping:
                error_msg = f"Component '{name}', node {end_node} not found in mapping dict."
                if fail_silently:
                    error = invalid.InvalidComponentNode(error_msg, name, end_node)
                    invalid.add_error(error, self.error_set)
                    both_nodes_valid = False
                else:
                    raise exceptions.BadInputError(error_msg)

            if both_nodes_valid:
                self.plumbing_graph.add_edge(
                    mapping[start_node], mapping[end_node], component.name + '.' + edge_key)

        self.set_component_state(component.name, state_id)

        # Set a default pressure of 0
        for node in mapping.values():
            if node in self.plumbing_graph and 'pressure' not in self.plumbing_graph.nodes[node]:
                self.set_pressure(node, 0)

        # Assign specified node pressures
        pressures = copy.deepcopy(pressures)
        for node_name, node_pressure in pressures.items():
            try:
                self.set_pressure(node_name, node_pressure)
            except exceptions.BadInputError as err:
                if fail_silently:
                    if err.args[0] == f"Node {node_name} not found in graph.":
                        raise
                    error = invalid.InvalidNodePressure(err.args[0], node_name)
                    invalid.add_error(error, self.error_set)
                else:
                    raise

    def is_valid(self):
        '''Returns whether the plumbing engine is valid'''
        return len(self.error_set) == 0

    def remove_component(self, input_component_name):
        '''Removes component and associated errors'''
        # Check validity of provided component name
        if input_component_name not in self.component_dict:
            raise exceptions.BadInputError(
                f"Component with name {input_component_name} not found in component dict.")

        component = self.component_dict[input_component_name]
        component_name = component.name

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
        self._resolve_errors(input_component_name)
        if component_name in self.mapping:
            del self.mapping[component_name]
        del self.component_dict[input_component_name]
        self.time_resolution = utils.DEFAULT_TIME_RESOLUTION_MICROS
        for name in self.component_dict.keys():
            self._set_time_resolution(name)

    def _resolve_errors(self, component_name):
        '''Resolve all errors associated with a certain component'''
        # Find all errors associated with a component
        to_remove = []
        for error in self.error_set:
            if hasattr(error, 'component_name') and error.component_name == component_name:
                to_remove.append(error)
            # Remove any errors associated with nodes that have now been removed
            elif hasattr(error, 'node_name'):
                if error.node_name not in self.plumbing_graph:
                    to_remove.append(error)

        for error in self.error_set:
            if isinstance(error, invalid.DuplicateError) and error.original_error in to_remove:
                to_remove.append(error)

        for error in to_remove:
            self.error_set.remove(error)

    def reverse_orientation(self, component_name):
        '''Reverse direction of suitable components, such as check valves'''
        if component_name not in self.component_dict:
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
        if node_name not in self.plumbing_graph:
            raise exceptions.BadInputError(f"Node {node_name} not found in graph.")

        self.plumbing_graph.nodes[node_name]['pressure'] = pressure

    def set_teq(self, component_name, which_edge):
        '''Sets teq at given dict of edges for one component'''
        if component_name not in self.component_dict:
            raise exceptions.BadInputError(
                f"Component name '{component_name}' not found in component dict.")

        component = self.component_dict[component_name]
        which_edge = copy.deepcopy(which_edge)

        for state_id, edge_dict in which_edge.items():
            if state_id not in component.states:
                raise exceptions.BadInputError(
                    f"State '{state_id}' not found in component {component_name}'s states dict.")

            for edge, teq in edge_dict.items():
                teq = utils.s_to_micros(teq)
                if teq < utils.TEQ_MIN:
                    raise exceptions.BadInputError(
                        f"Provided teq {utils.micros_to_s(teq)} (component '{component_name}',"
                        f" state '{state_id}', edge {edge}) too low. "
                        f"Minimum teq is {utils.micros_to_s(utils.TEQ_MIN)}s.")
                if edge not in component.states[state_id]:
                    raise exceptions.BadInputError(
                        f"State '{state_id}', edge {edge} not found in component"
                        f" {component_name}'s states dict.")

                component.states[state_id][edge] = utils.teq_to_FC(teq)

        # Update teq changes on main plumbing graph
        if component.current_state in which_edge.keys():
            self.set_component_state(component_name, component.current_state)

        self._set_time_resolution(component_name)

    def list_toggles(self):
        '''Returns a list of toggleable components (by name)'''
        return [c.name for c in self.component_dict.values() if len(c.states) > 1]

    def current_state(self, *args):
        '''Given one or more component_names, returns the state_id of their current states'''
        if len(args) == 0:
            return {component.name: component.current_state
                    for component in self.component_dict.values()}

        # If passed a list, unpack those list elements into args
        args = utils.flatten(args)

        try:
            if len(args) == 1:
                component_name = args[0]
                return self.component_dict[component_name].current_state
            else:
                return {name: self.component_dict[name].current_state for name in args}
        except KeyError as err:
            raise exceptions.BadInputError(
                f"Component '{err.args[0]}' not found in component dict.")

    def current_pressures(self, *args):
        '''Given one or more nodes, returns their current pressure'''
        if len(args) == 0:
            return {n: self.plumbing_graph.nodes[n]['pressure']
                    for n in self.plumbing_graph.nodes()}

        # If passed a list, unpack those list elements into args
        args = utils.flatten(args)

        try:
            if len(args) == 1:
                return self.plumbing_graph.nodes[args[0]]['pressure']
            else:
                return {n: self.plumbing_graph.nodes[n]['pressure'] for n in args}
        except KeyError as err:
            raise exceptions.BadInputError(f"Node {err.args[0]} not found in graph.")

    def current_FC(self, *args):
        '''Given a component name or edge id, return a dict of corresponding FCs'''
        if len(args) == 0:
            return {edge: self.plumbing_graph.edges[edge]['FC']
                    for edge in self.plumbing_graph.edges(keys=True)}

        # If passed a list, unpack those list elements into args
        args = utils.flatten(args, unpack_tuples=False)

        if len(args) == 1 and args[0] in list(self.plumbing_graph.edges(keys=True)):
            return self.plumbing_graph.edges[args[0]]['FC']

        ret = {}
        for arg in args:
            if arg in self.component_dict:
                for edge in self.plumbing_graph.edges(keys=True):
                    if edge[2].startswith(arg + '.'):
                        ret[edge] = self.plumbing_graph.edges[edge]['FC']
            elif arg in list(self.plumbing_graph.edges(keys=True)):
                ret[arg] = self.plumbing_graph.edges[arg]['FC']
            else:
                raise exceptions.BadInputError(
                    f"'{arg}' not found as component name or edge identifier.")

        return ret

    def errors(self):
        return self.error_set

    def nodes(self, data=True):
        return list(self.plumbing_graph.nodes(data=data))

    def edges(self, data=True):
        return list(self.plumbing_graph.edges(keys=True, data=data))

    def step(self, timestep=None):
        if not self.plumbing_graph:
            raise exceptions.InvalidEngineError(
                "Step() cannot be called on an empty engine.")
        if not self.is_valid():
            raise exceptions.InvalidEngineError(
                "Step() cannot be called on an invalid engine. Check for errors.")

        if timestep is None:
            timestep = self.time_resolution
        if timestep < utils.MIN_TIME_RES_MICROS:
            timestep = utils.MIN_TIME_RES_MICROS

        new_pressures = {}
        for node in self.nodes():
            dp = 0
            pressure = self.current_pressures(node)
            for edge in self.plumbing_graph.out_edges(node, keys=True):
                _, neighbor, _ = edge
                npressure = self.current_pressures(neighbor)
                if pressure > npressure:
                    fc = self.current_FC(edge)
                    dp -= fc * (pressure - npressure)
            for edge in self.plumbing_graph.in_edges(node, keys=True):
                _, neighbor, _ = edge
                npressure = self.current_pressures(neighbor)
                if pressure < npressure:
                    fc = self.current_FC(edge)
                    dp += fc * (npressure - pressure)
            new_pressures[node] = pressure + dp*timestep

        for node, pressure in new_pressures.items():
            self.set_pressure(node, pressure)

        return new_pressures

    def solve(self, min_delta=0.5, max_time=utils.s_to_micros(60), return_resolution=None):
        timestep = self.time_resolution
        if return_resolution is not None and return_resolution < self.time_resolution:
            timestep = return_resolution

        all_states = []
        time = 0
        while not utils.all_converged(all_states, timestep, min_delta) and time < max_time:
            all_states.append(self.step(timestep))
            time += timestep

        if return_resolution is None:
            return all_states[-1]

        return all_states
