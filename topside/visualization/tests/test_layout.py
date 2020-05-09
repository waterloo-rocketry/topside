import networkx as nx

import topside as top


def one_component_engine():
    states = {
        'static': {
            (1, 2, 'A1'): 1,
            (2, 1, 'A2'): 1
        },
    }
    edges = [(1, 2, 'A1'), (2, 1, 'A2')]

    c1 = top.PlumbingComponent('c1', states, edges)

    mapping = {'c1': {1: 1, 2: 2}}
    pressures = {1: 0, 2: 0}
    initial_states = {'c1': 'static'}

    return top.PlumbingEngine({'c1': c1}, mapping, pressures, initial_states)


def series_component_engine():
    states = {
        'static': {
            (1, 2, 'A1'): 1,
            (2, 1, 'A2'): 1
        },
    }
    edges = [(1, 2, 'A1'), (2, 1, 'A2')]

    c1 = top.PlumbingComponent('c1', states, edges)
    c2 = top.PlumbingComponent('c2', states, edges)

    mapping = {'c1': {1: 1, 2: 2}, 'c2': {1: 2, 2: 3}}
    pressures = {1: 0, 2: 0, 3: 0}
    initial_states = {'c1': 'static', 'c2': 'static'}

    return top.PlumbingEngine({'c1': c1, 'c2': c2}, mapping, pressures, initial_states)


def parallel_component_engine():
    states = {
        'static': {
            (1, 2, 'A1'): 1,
            (2, 1, 'A2'): 1
        },
    }
    edges = [(1, 2, 'A1'), (2, 1, 'A2')]

    c1 = top.PlumbingComponent('c1', states, edges)
    c2 = top.PlumbingComponent('c2', states, edges)

    mapping = {'c1': {1: 1, 2: 2}, 'c2': {1: 1, 2: 2}}
    pressures = {1: 0, 2: 0}
    initial_states = {'c1': 'static', 'c2': 'static'}

    return top.PlumbingEngine({'c1': c1, 'c2': c2}, mapping, pressures, initial_states)


def test_terminal_graph_one_component():
    p = one_component_engine()
    t = top.terminal_graph(p)

    expected_t = nx.Graph([(1, 'c1.1'), ('c1.1', 'c1.2'), ('c1.2', 2)])
    assert nx.is_isomorphic(t, expected_t)


def test_terminal_graph_series_components():
    p = series_component_engine()
    t = top.terminal_graph(p)

    expected_t = nx.Graph([(1, 'c1.1'), ('c1.1', 'c1.2'), ('c1.2', 2),
                           (2, 'c2.1'), ('c2.1', 'c2.2'), ('c2.2', 3)])
    assert nx.is_isomorphic(t, expected_t)


def test_terminal_graph_parallel_components():
    p = parallel_component_engine()
    t = top.terminal_graph(p)

    expected_t = nx.Graph([(1, 'c1.1'), ('c1.1', 'c1.2'), ('c1.2', 2),
                           (1, 'c2.1'), ('c2.1', 'c2.2'), ('c2.2', 2)])
    assert nx.is_isomorphic(t, expected_t)


def test_component_nodes_one_component():
    p = one_component_engine()
    nodes = top.component_nodes(p)

    expected_component_nodes = [['c1.1', 'c1.2']]
    assert nodes == expected_component_nodes


def test_component_nodes_series_components():
    p = series_component_engine()
    nodes = top.component_nodes(p)

    expected_component_nodes = [['c1.1', 'c1.2'], ['c2.1', 'c2.2']]
    assert nodes == expected_component_nodes


def test_component_nodes_parallel_components():
    p = parallel_component_engine()
    nodes = top.component_nodes(p)

    expected_component_nodes = [['c1.1', 'c1.2'], ['c2.1', 'c2.2']]
    assert nodes == expected_component_nodes
