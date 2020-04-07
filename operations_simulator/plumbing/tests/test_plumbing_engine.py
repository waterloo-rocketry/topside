import operations_simulator as ops


def test_plumbing_engine_exists():
    plumb = ops.PlumbingEngine()
    assert plumb is not None


def test_plumbing_component_exists():
    plumb_comp = ops.PlumbingComponent('', {}, [])
    assert plumb_comp is not None


def test_plumbing_component_setup():
    pc1_states = {
        'open': {
            (1, 2, 'A1'): 0.001,
            (2, 1, 'A2'): 0.001
        },
        'closed': {
            (1, 2, 'A1'): 'closed',
            (2, 1, 'A2'): 'closed'
        }
    }
    pc1_edges = [(1, 2, 'A1'), (2, 1, 'A2')]
    pc1 = ops.PlumbingComponent('valve1', pc1_states, pc1_edges)

    assert pc1.component_graph.edges(keys=True) == [(1, 2, 'A1'), (2, 1, 'A2')]
    assert pc1.component_graph.nodes() == [1, 2]
    assert pc1.states == {'open': {(1, 2, 'A1'): 4500.0, (2, 1, 'A2'): 4500.0}, 'closed': {
        (1, 2, 'A1'): 0.0045, (2, 1, 'A2'): 0.0045}}


def test_plumbing_engine_setup():
    pc1_states = {
        'open': {
            (1, 2, 'A1'): 0,
            (2, 1, 'A2'): 0
        },
        'closed': {
            (1, 2, 'A1'): 'closed',
            (2, 1, 'A2'): 'closed'
        }
    }
    pc1_edges = [(1, 2, 'A1'), (2, 1, 'A2')]
    pc1 = ops.PlumbingComponent('valve1', pc1_states, pc1_edges)

    pc2_states = {
        'open': {
            (1, 2, 'B1'): 0,
            (2, 1, 'B2'): 0
        },
        'closed': {
            (1, 2, 'B1'): 'closed',
            (2, 1, 'B2'): 'closed'
        }
    }
    pc2_edges = [(1, 2, 'B1'), (2, 1, 'B2')]
    pc2 = ops.PlumbingComponent('valve2', pc2_states, pc2_edges)

    component_mapping = {
        'valve1': {
            1: 1,
            2: 2
        },
        'valve2': {
            1: 2,
            2: 3
        }
    }

    pressures = {3: 100}
    default_states = {'valve1': 'closed', 'valve2': 'open'}
    plumb = ops.PlumbingEngine(
        [pc1, pc2], component_mapping, pressures, default_states)

    assert plumb.plumbing_graph.edges(data=True, keys=True) == [(1, 2, 'A1', {
        'FC': 0}), (2, 1, 'A2', {'FC': 0}), (2, 3, 'B1', {'FC': 10}), (3, 2, 'B2', {'FC': 10})]
    assert plumb.time_resolution == 5e-05
    assert plumb.plumbing_graph.nodes(data=True) == [(
        1, {'pressure': 0}), (2, {'pressure': 0}), (3, {'pressure': 100})]
