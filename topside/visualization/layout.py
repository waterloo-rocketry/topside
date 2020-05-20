import networkx as nx


def terminal_graph(plumbing_engine):
    """
    Create an augmented graph suitable for visualization.

    The terminal graph T is created by the following process, for a
    plumbing engine P with graph G:
        1. All non-atm nodes from G are placed in T.
        2. For each component C in P:
            a) For each node n in C:
                i. Create a node C_n in T, where the node name of C_n is
                   <name of C>.<name of n>.
                ii. Create an edge in T from C_n to C.mapping[n].

    Parameters
    ----------

    plumbing_engine: topside.PlumbingEngine

    Returns
    -------

    t: networkx.Graph
    """
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
