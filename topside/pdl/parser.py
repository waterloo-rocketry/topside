import topside as top
import topside.pdl.exceptions as exceptions


class Parser:
    def __init__(self, files):
        self.package = top.Package(files)

        self.components = []
        self.mapping = {}
        self.initial_pressure = {}
        self.initial_states = {}

        self.parse_components()

    def parse_components(self):
        for entry in self.package.components():
            name = entry['name']

            edge_dict = extract_edges(entry)

            edge_list = [edge[0] for edge in edge_dict.values()]
            back_edge_list = [edge[1] for edge in edge_dict.values()]
            edge_list.extend(back_edge_list)

            states = {}
            for state_name, edges in entry['states'].items():
                edge_teqs = {}
                for edge_name, teqs in edges.items():
                    fwd_edge = edge_dict[edge_name][0]
                    edge_teqs[fwd_edge] = teqs['fwd']

                    back_edge = edge_dict[edge_name][1]
                    edge_teqs[back_edge] = teqs['back']
                states[state_name] = edge_teqs

            component = top.PlumbingComponent(name, states, edge_list)
            if not component.is_valid():
                raise exceptions.BadInputError(f"errors in component {name} instantiation: {component.errors()}")
            self.components.append(component)


def extract_edges(entry):
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
        key = ""
        nodes = tuple(edges['nodes'])
        swapped_nodes = tuple(swap(edges['nodes']))
        if nodes in edges_seen:
            key = edges_seen[nodes]
            edges_seen[nodes] += 1
        elif swapped_nodes in edges_seen:
            key = edges_seen[swapped_nodes]
            edges_seen[swapped_nodes] += 1
        else:
            edges_seen[nodes] = 0

        node_1 = edges['nodes'][0]
        node_2 = edges['nodes'][1]

        fwd_edge = (node_1, node_2, "fwd" + key)
        back_edge = (node_2, node_1, "back" + key)

        edge_dict[edge_name] = (fwd_edge, back_edge)

    return edge_dict



def swap(indexable):
    """Take an indexable object and return a list of only its first two elements swapped."""
    ret = []
    ret.append(indexable[1])
    ret.append(indexable[0])
    return ret
