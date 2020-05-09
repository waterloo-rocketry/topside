from dataclasses import dataclass

import numpy as np
import networkx as nx


def terminal_graph(plumbing_engine):
    t = nx.Graph()

    non_atm_nodes = [n for n in plumbing_engine.plumbing_graph if not n == 'atm']
    t.add_nodes_from(non_atm_nodes)

    component_nodes = {}

    for name, c in plumbing_engine.component_dict.items():
        component_nodes[name] = []
        for edge in c.component_graph.edges:
            (n1, n2, edge_id) = edge
            t.add_edge(name + '.' + str(n1), name + '.' + str(n2))
        for node in c.component_graph.nodes:
            component_nodes[name].append(name + '.' + str(node))
            if not plumbing_engine.mapping[name][node] == 'atm':
                t.add_edge(name + '.' + str(node), plumbing_engine.mapping[name][node])

    return t, non_atm_nodes, component_nodes
