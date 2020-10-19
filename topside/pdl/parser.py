import topside as top
import topside.pdl.exceptions as exceptions


class Parser:
    """Produces plumbing engine input that's representative of its given files."""

    def __init__(self, files, input_type='f'):
        """
        Initialize a parser from one or more PDL files.

        A Parser contains a Package; most of its functionality lies in restructuring the data
        contained in its Package into output suitable for loading a plumbing engine.

        Parameters
        ----------

        files: iterable
            files is the iterable (usually a list) of one or more paths of the PDL files we
            want parsed. Alternatively, it can also be a list of strings that are each a valid
            PDL file. Alternatively, a single string or file path is also acceptable.

        input_type: char
            input_type indicates whether the argument provided to "files" is
            a list of file paths (f) or a list of strings (s).

        """
        file_list = []

        # if a single element, put into list for processing
        if isinstance(files, str):
            files = [files]

        for file in files:
            file_list.append(top.File(file, input_type))
        self.package = top.Package(file_list)

        self.components = {}
        self.mapping = {}
        self.initial_pressures = {}
        self.initial_states = {}

        self.parse_components()
        self.parse_graphs()

    def parse_components(self):
        """Create and store components for plumbing engine."""
        for entry in self.package.components():
            name = entry['name']

            # extract edge list, plus dict of {edge name: edge tuple}
            edge_dict = extract_edges(entry)
            edge_list = []
            for edge in edge_dict.values():
                edge_list.extend(edge)

            # extract states dict {state_name: {edge: teq}} for each edge
            # in both directions
            states = {}
            for state_name, edges in entry['states'].items():
                edge_teqs = {}
                for edge_name, teqs in edges.items():
                    fwd_edge, back_edge = edge_dict[edge_name]

                    edge_teqs[fwd_edge] = teqs['fwd']
                    edge_teqs[back_edge] = teqs['back']
                states[state_name] = edge_teqs

            component = top.PlumbingComponent(name, states, edge_list)
            self.components[name] = component

    def parse_graphs(self):
        """Extract and store graph information for plumbing engine."""
        graphs = self.package.graphs()
        main_present = False

        # move main graph to end so that its settings take precedence
        for idx, entry in enumerate(graphs):
            if entry['name'] == 'main':
                main_present = True
                graphs.append(graphs.pop(idx))
                break
        if not main_present:
            raise exceptions.BadInputError("must have graph main")

        for entry in graphs:
            for graph_node, node_data in entry['nodes'].items():
                if 'initial_pressure' in node_data:
                    self.initial_pressures[graph_node] = (node_data['initial_pressure'], False)
                if 'fixed_pressure' in node_data:
                    self.initial_pressures[graph_node] = (node_data['fixed_pressure'], True)
                for component_name, component_node in node_data['components']:
                    if component_name not in self.mapping:
                        self.mapping[component_name] = {}

                    self.mapping[component_name][component_node] = graph_node

            self.initial_states.update(entry['states'])

    def make_engine(self):
        """Create the plumbing engine from the provided input."""
        plumb = top.PlumbingEngine(self.components, self.mapping,
                                   self.initial_pressures, self.initial_states)
        return plumb


def extract_edges(entry):
    """
    Extract dict of {edge_name: (fwd_edge, back_edge)} from a component entry.

    fwd_edge and back_edge take the form (node1, node2, key), where key is unique among
    edges going between the same nodes.
    """
    name = entry['name']
    edge_dict = {}

    # edges_seen keeps track of edges between the same nodes. Takes form
    # {(node1, node2): key}, where key is the lowest integer that has been used
    # as a key for this set of nodes.
    edges_seen = {}
    for edge_name, edges in entry['edges'].items():
        if len(edges['nodes']) != 2:
            raise exceptions.BadInputError(
                f"malformed nodes entry ({edges['nodes']}) for edge {edge_name} in" +
                f" component {name}")

        # key will just be fwd or back, unless there are multiple edges between the same
        # two nodes, in which case the key will have a unique int appended.
        key = ''
        nodes = tuple(edges['nodes'])
        swapped_nodes = (nodes[1], nodes[0])
        if nodes in edges_seen:
            edges_seen[nodes] += 1
            key = edges_seen[nodes]
        elif swapped_nodes in edges_seen:
            edges_seen[swapped_nodes] += 1
            key = edges_seen[swapped_nodes]
        else:
            edges_seen[nodes] = 1

        node_1, node_2 = edges['nodes']

        fwd_edge = (node_1, node_2, 'fwd' + str(key))
        back_edge = (node_2, node_1, 'back' + str(key))

        edge_dict[edge_name] = (fwd_edge, back_edge)

    return edge_dict
