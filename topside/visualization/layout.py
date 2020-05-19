import networkx as nx


def terminal_graph(plumbing_engine):
    t = nx.Graph()

    for name, c in plumbing_engine.component_dict.items():
        for edge in c.component_graph.edges:
            (n1, n2, edge_id) = edge
            t.add_edge(name + '.' + str(n1), name + '.' + str(n2))
        for node in c.component_graph.nodes:
            if not plumbing_engine.mapping[name][node] == 'atm':
                t.add_edge(name + '.' + str(node), plumbing_engine.mapping[name][node])

    return t


def component_nodes(plumbing_engine):
    return [[name + '.' + str(node) for node in c.component_graph]
            for name, c in plumbing_engine.component_dict.items()]
